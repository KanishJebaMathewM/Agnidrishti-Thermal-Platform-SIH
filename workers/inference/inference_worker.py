"""
Online inference worker (AGNIDRISHTI_PLAN.md — online path):

  New observation (preprocessed + enriched)
       -> Build feature vector
       -> XGBoost classification
       -> Anomaly detection
       -> Store results
       -> Trigger event formation

This worker does NOT retrain the model. It loads the active model artifact
once per worker process and reuses it for every task (module-level cache).
Training is periodic and independent — see ml/training/train_classifier.py.

Model loading:
  1. Ask the model store for the active model's version/artifact paths
     (production: query `model_versions` where is_active=True; here:
     `LocalModelRegistry` scans ml/models/*_metadata.json for is_active).
  2. Load the artifact via ml/inference/classifier.py::ClassifierModel.load.
  3. Cache in memory (module-level singleton, keyed by version_tag).
  4. `reload_model(...)` forces a fresh load — call this from Contributor
     1's `POST /model/reload` endpoint.

------------------------------------------------------------------------
No hard dependency on a live database or broker. `InferenceDataStore` and
`ModelStore` are the integration seams for Contributor 1: implement them
against SQLAlchemy/PostGIS and pass instances in — the actual inference
logic (`run_inference_logic`) never changes.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Protocol

try:
    from celery import shared_task
except ImportError:  # pragma: no cover - celery not installed in this environment
    def shared_task(*_args, **_kwargs):
        def _decorator(fn):
            return fn
        return _decorator

from ml.features.feature_builder import build_feature_vector
from ml.inference.anomaly_scorer import compute_anomaly
from ml.inference.classifier import ClassifierModel

logger = logging.getLogger(__name__)

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "ml" / "models"
DEFAULT_ISOLATION_FOREST_PATH = DEFAULT_MODEL_DIR / "isolation_forest_v1.joblib"


# --------------------------------------------------------------------------
# Model loading + caching
# --------------------------------------------------------------------------

class ModelStore(Protocol):
    def get_active_model_info(self) -> dict | None:
        """Return {"version_tag", "artifact_path", "metadata_path"} or None."""
        ...


class LocalModelRegistry:
    """
    Default `ModelStore`: scans `ml/models/*_metadata.json` for an entry
    with `is_active: true`. This is what training scripts in this
    repository produce (see ml/training/train_classifier.py::save_model).
    Contributor 1 should replace this with a query against the
    `model_versions` table.
    """

    def __init__(self, model_dir: Path = DEFAULT_MODEL_DIR):
        self.model_dir = Path(model_dir)

    def get_active_model_info(self) -> dict | None:
        if not self.model_dir.exists():
            return None

        candidates = []
        for meta_path in sorted(self.model_dir.glob("*_metadata.json")):
            try:
                meta = json.loads(meta_path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if meta.get("is_active"):
                candidates.append((meta, meta_path))

        if not candidates:
            return None

        meta, meta_path = max(candidates, key=lambda pair: pair[0].get("trained_at", ""))
        artifact_path = meta.get("artifact_path") or str(
            self.model_dir / f"{meta['version_tag'].replace('.', '_')}.joblib"
        )
        return {
            "version_tag": meta["version_tag"],
            "artifact_path": artifact_path,
            "metadata_path": str(meta_path),
        }


_default_model_store = LocalModelRegistry()
_model_cache: dict[str, ClassifierModel] = {}
_iso_forest_cache: dict[str, dict] = {}


def get_active_model(store: ModelStore | None = None) -> ClassifierModel:
    """Load (once) and return the currently active classifier."""
    store = store or _default_model_store
    info = store.get_active_model_info()
    if info is None:
        raise RuntimeError(
            "No active model found. Run `python -m ml.training.train_classifier` first, "
            "or configure a ModelStore backed by the model_versions table."
        )

    tag = info["version_tag"]
    if tag not in _model_cache:
        logger.info("Loading classifier model %s from disk", tag)
        _model_cache[tag] = ClassifierModel.load(info["artifact_path"], info["metadata_path"])
    return _model_cache[tag]


def reload_model(store: ModelStore | None = None) -> ClassifierModel:
    """Force a reload from disk, bypassing the cache. Wire to POST /model/reload."""
    store = store or _default_model_store
    info = store.get_active_model_info()
    if info is None:
        raise RuntimeError("No active model found to reload.")
    tag = info["version_tag"]
    _model_cache[tag] = ClassifierModel.load(info["artifact_path"], info["metadata_path"])
    return _model_cache[tag]


def load_isolation_forest_models(path: Path = DEFAULT_ISOLATION_FOREST_PATH) -> dict:
    """Load (once) the per-class Isolation Forest models, if trained."""
    key = str(path)
    if key in _iso_forest_cache:
        return _iso_forest_cache[key]

    if not Path(path).exists():
        _iso_forest_cache[key] = {}
        return {}

    import joblib
    models = joblib.load(path)
    _iso_forest_cache[key] = models
    return models


# --------------------------------------------------------------------------
# Data access seam
# --------------------------------------------------------------------------

class InferenceDataStore(Protocol):
    def get_observation(self, observation_id: str) -> dict | None: ...
    def get_source_baseline(self, source_id: str | None) -> dict | None: ...
    def get_context(self, latitude: float, longitude: float) -> dict: ...
    def save_inference_result(self, observation_id: str, result: dict) -> None: ...


class InMemoryInferenceStore:
    """
    Default in-process store for tests, demo/replay mode, and local
    development without a database. Not for production use.
    """

    def __init__(self):
        self._observations: dict[str, dict] = {}
        self._baselines: dict[str, dict] = {}
        self._results: dict[str, dict] = {}

    def add_observation(self, observation: dict, baseline: dict | None = None) -> None:
        self._observations[observation["id"]] = observation
        if baseline is not None and observation.get("source_id"):
            self._baselines[observation["source_id"]] = baseline

    def get_observation(self, observation_id: str) -> dict | None:
        return self._observations.get(observation_id)

    def get_source_baseline(self, source_id: str | None) -> dict | None:
        if not source_id:
            return None
        return self._baselines.get(source_id)

    def get_context(self, latitude: float, longitude: float) -> dict:
        # A real implementation resolves this via PostGIS (state/district/
        # nearest facility/land-use/forest lookups). In-memory mode has no
        # geographic reference layers, so it returns an empty context —
        # tests supply context explicitly via add_observation's caller.
        return {}

    def save_inference_result(self, observation_id: str, result: dict) -> None:
        self._results[observation_id] = result

    def get_inference_result(self, observation_id: str) -> dict | None:
        return self._results.get(observation_id)


_default_inference_store = InMemoryInferenceStore()


# --------------------------------------------------------------------------
# Core inference logic (pure — the part that must stay reproducible)
# --------------------------------------------------------------------------

def run_inference_logic(
    observation: dict,
    baseline: dict | None,
    context: dict,
    classifier: ClassifierModel,
    isolation_forest_models: dict | None = None,
) -> dict:
    """
    Run classification + anomaly detection for a single observation.

    Returns a dict combining the classifier and anomaly-scorer outputs,
    suitable for persisting on the observation record.
    """
    feature_vector = build_feature_vector(observation, baseline, context)
    classification = classifier.predict(feature_vector)

    iso_model = None
    if isolation_forest_models:
        iso_model = isolation_forest_models.get(classification["predicted_class"])
    anomaly = compute_anomaly(feature_vector, baseline, iso_model)

    return {
        "observation_id": str(observation.get("id", "")),
        **classification,
        **anomaly,
    }


# --------------------------------------------------------------------------
# Celery task
# --------------------------------------------------------------------------

@shared_task(name="workers.inference.run_inference")
def run_inference(
    observation_id: str,
    store: InferenceDataStore | None = None,
    model_store: ModelStore | None = None,
) -> dict | None:
    """
    Steps:
    1. Load observation + context from the store.
    2. Load source baseline (or None if new source).
    3. Build feature vector + run classification.
    4. Run anomaly scorer.
    5. Store results on the observation record.
    6. Trigger event formation for this observation.
    """
    store = store or _default_inference_store
    observation = store.get_observation(observation_id)
    if observation is None:
        logger.warning("run_inference: observation %s not found", observation_id)
        return None

    baseline = store.get_source_baseline(observation.get("source_id"))
    context = store.get_context(observation["latitude"], observation["longitude"])

    classifier = get_active_model(model_store)
    isolation_forest_models = load_isolation_forest_models()

    result = run_inference_logic(observation, baseline, context, classifier, isolation_forest_models)
    store.save_inference_result(observation_id, result)

    _trigger_event_formation(observation_id)
    return result


def _trigger_event_formation(observation_id: str) -> None:
    """
    Trigger workers.events.process_event for this observation. Uses
    `.delay(...)` when running under a real Celery worker; falls back to a
    direct call when no broker/app is configured (tests, demo mode, or
    celery not installed) so the online path still completes end-to-end.
    """
    from workers.events.event_worker import process_event

    try:
        process_event.delay(observation_id)
    except Exception:
        process_event(observation_id)
