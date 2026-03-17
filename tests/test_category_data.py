from pathlib import Path

from src.categories import list_category_types


def test_all_category_files_exist_and_have_expected_item_count():
    base_dir = Path("data/categories")
    for type_key in list_category_types():
        path = base_dir / f"{type_key}.txt"
        assert path.exists()
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert 20 <= len(lines) <= 30
