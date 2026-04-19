from __future__ import annotations

from pathlib import Path

from app.ml.hot_pipeline import sha256_file


def test_sha256_is_deterministic(tmp_path: Path) -> None:
    f = tmp_path / "x.bin"
    f.write_bytes(b"photos-ai")
    a = sha256_file(f)
    b = sha256_file(f)
    assert a == b
    assert len(a) == 64


def test_sha256_changes_with_content(tmp_path: Path) -> None:
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"aaa")
    b.write_bytes(b"bbb")
    assert sha256_file(a) != sha256_file(b)
