"""
Ensures the repository root is importable as `workers.*` regardless of how
pytest is invoked. Mirrors ml/conftest.py.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
