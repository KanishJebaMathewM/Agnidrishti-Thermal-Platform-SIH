"""
Ensures the repository root is importable as `ml.*` / `workers.*` regardless
of how pytest is invoked (repo root, from within ml/, or with -p rootdir
overrides). Belt-and-suspenders alongside the ml/__init__.py package
markers, which normally make pytest do this automatically.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
