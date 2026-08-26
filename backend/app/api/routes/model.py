import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from workers.inference.inference_worker import LocalModelRegistry, reload_model

router = APIRouter()

_registry = LocalModelRegistry()


@router.get("/current")
async def current_model():
    info = _registry.get_active_model_info()
    if info is None:
        return {"version_tag": None, "is_active": False, "status": "no_active_model"}

    metadata: dict = {}
    try:
        metadata = json.loads(Path(info["metadata_path"]).read_text())
    except (OSError, json.JSONDecodeError):
        pass

    return {
        "version_tag": info["version_tag"],
        "is_active": True,
        "status": "ready",
        "artifact_path": info["artifact_path"],
        "feature_set_version": metadata.get("feature_set_version"),
        "training_data_version": metadata.get("training_data_version"),
        "trained_at": metadata.get("trained_at"),
        "metrics": metadata.get("metrics"),
    }


@router.post("/reload")
async def reload_active_model():
    try:
        model = reload_model(_registry)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "reloaded", "version_tag": model.metadata.get("version_tag")}
