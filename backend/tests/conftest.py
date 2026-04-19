from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATA_DIR", str(ROOT / "tests" / "_tmp"))
os.environ.setdefault("DB_URL", f"sqlite:///{ROOT / 'tests' / '_tmp' / 'test.db'}")
os.environ.setdefault("FAISS_INDEX_PATH", str(ROOT / "tests" / "_tmp" / "faiss.index"))
(ROOT / "tests" / "_tmp").mkdir(parents=True, exist_ok=True)
