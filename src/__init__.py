"""
Top-level shim package to expose `backend/src` as `src` for tests.

This allows test imports like `import src.services...` to work without setting
PYTHONPATH in all environments. This is a small compatibility shim for test runs.
"""

import os

# Append the backend/src directory (located at repository root) to this
# package's search path so imports like `import src.services...` resolve to
# the code under backend/src. Compute repo root as the parent of this file's
# parent directory.
repo_root = os.path.dirname(os.path.dirname(__file__))
backend_src = os.path.normpath(os.path.join(repo_root, "backend", "src"))
if os.path.isdir(backend_src):
    __path__.append(backend_src)
