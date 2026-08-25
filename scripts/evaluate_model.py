"""
CLI wrapper for model evaluation (Contributor 3 / ML domain).

Usage:
  python scripts/evaluate_model.py --model-path ml/models/xgb_v1_0.joblib

See ml/evaluation/evaluate.py for the evaluation logic itself.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.evaluation.evaluate import main  # noqa: E402

if __name__ == "__main__":
    main()
