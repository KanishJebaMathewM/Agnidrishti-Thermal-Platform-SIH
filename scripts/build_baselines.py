"""
CLI wrapper for the historical baseline builder (Contributor 3 / ML domain).

Usage:
  python scripts/build_baselines.py --input observations.json --output ml/models/baselines.json
  python scripts/build_baselines.py --demo    # synthetic data, no DB required

Integration point for Contributor 1: replace `_load_observations_by_source`
with a query joining `observations` to `thermal_sources`, and replace the
JSON output with an upsert into the `source_baselines` table. The
computation itself (ml/training/build_baselines.py) does not change.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.training.build_baselines import build_all_baselines  # noqa: E402


def _load_observations_by_source_from_json(path: Path) -> dict:
    data = json.loads(path.read_text())
    by_source: dict[str, list[dict]] = {}
    for obs in data:
        source_id = obs.get("source_id")
        if not source_id:
            continue
        by_source.setdefault(source_id, []).append(obs)
    return by_source


def _load_demo_observations_by_source() -> dict:
    from ml.datasets.synthetic import generate_synthetic_dataset

    records = generate_synthetic_dataset(n_per_class=50)
    by_source: dict[str, list[dict]] = {}
    for record in records:
        source_id = record["observation"].get("source_id")
        if not source_id:
            continue
        by_source.setdefault(source_id, []).append(record["observation"])
    return by_source


def main():
    parser = argparse.ArgumentParser(description="Build historical source baselines.")
    parser.add_argument("--input", type=Path, help="JSON file: list of observation dicts with source_id")
    parser.add_argument("--output", type=Path, default=ROOT / "ml" / "models" / "baselines.json")
    parser.add_argument("--demo", action="store_true", help="Use synthetic demo data instead of --input")
    args = parser.parse_args()

    if args.demo or not args.input:
        by_source = _load_demo_observations_by_source()
        print(f"Using synthetic demo data ({len(by_source)} sources) - pass --input for real observations.")
    else:
        by_source = _load_observations_by_source_from_json(args.input)

    baselines = build_all_baselines(by_source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(baselines, indent=2))
    print(f"Wrote {len(baselines)} source baselines to {args.output}")


if __name__ == "__main__":
    main()
