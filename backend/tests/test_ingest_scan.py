from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.services.ingest import scan_folder


def _img(p: Path) -> None:
    Image.new("RGB", (10, 10), (255, 0, 0)).save(p)


def test_scan_folder_filters_by_extension(tmp_path: Path) -> None:
    _img(tmp_path / "a.jpg")
    _img(tmp_path / "b.PNG")
    (tmp_path / "note.txt").write_text("skip me")
    sub = tmp_path / "sub"
    sub.mkdir()
    _img(sub / "c.webp")

    flat = scan_folder(tmp_path, recursive=False)
    assert {p.name for p in flat} == {"a.jpg", "b.PNG"}

    deep = scan_folder(tmp_path, recursive=True)
    assert {p.name for p in deep} == {"a.jpg", "b.PNG", "c.webp"}
