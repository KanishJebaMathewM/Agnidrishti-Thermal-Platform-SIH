"""
Ensures the backend/ directory is importable as `app.*` regardless of how
pytest is invoked (repo root, as in CI, or from within backend/). Mirrors
ml/conftest.py and workers/tests/conftest.py.
"""
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
