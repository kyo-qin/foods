from pathlib import Path


def ensure_output_dirs(base_dir: Path, dish_name: str) -> Path:
    dish_dir = base_dir / dish_name
    dish_dir.mkdir(parents=True, exist_ok=True)
    return dish_dir


def build_output_path(base_dir: Path, dish_name: str, index: int) -> Path:
    return ensure_output_dirs(base_dir, dish_name) / f"{index:03d}.jpg"


def write_image(path: Path, data: bytes, overwrite: bool = False) -> bool:
    if path.exists() and not overwrite:
        return False
    path.write_bytes(data)
    return True
