from pathlib import Path

from src.storage import build_output_path, ensure_output_dirs


def test_build_output_path_uses_dish_directory(tmp_path: Path):
    path = build_output_path(tmp_path, "鱼香肉丝", 1)
    assert path == tmp_path / "鱼香肉丝" / "001.jpg"


def test_ensure_output_dirs_creates_directory(tmp_path: Path):
    dish_dir = ensure_output_dirs(tmp_path, "鱼香肉丝")
    assert dish_dir.exists()
    assert dish_dir.is_dir()
