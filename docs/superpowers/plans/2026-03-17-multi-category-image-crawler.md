# Multi-Category Image Crawler Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the current dish-only crawler into a preset category-driven crawler selectable via `--type`, with separate category item lists, category-specific query templates, and manifest entries that record category metadata.

**Architecture:** Introduce a category configuration registry that decouples crawler behavior from hard-coded dish semantics. Keep the existing download/search/normalize/write pipeline intact, but generalize names from dish-oriented models to category item models and wire `src.main` through CLI argument parsing plus category config resolution.

**Tech Stack:** Python 3, pytest, pathlib, dataclasses, argparse

---

## File Map

- Create: `src/categories.py`
- Create: `data/categories/home_cooking.txt`
- Create: `data/categories/beverage.txt`
- Create: `data/categories/takeout_box.txt`
- Create: `data/categories/staple_food.txt`
- Create: `data/categories/dessert.txt`
- Create: `data/categories/noodle.txt`
- Create: `data/categories/milk_tea.txt`
- Create: `data/categories/coffee.txt`
- Modify: `src/main.py`
- Modify: `src/models.py`
- Modify: `src/pipeline.py`
- Modify: `src/search.py`
- Modify: `src/manifest.py`
- Modify: `README.md`
- Modify: `tests/test_main.py`
- Modify: `tests/test_pipeline.py`
- Create: `tests/test_categories.py`
- Create: `tests/test_manifest.py` or extend existing `tests/test_manifest.py`
- Create: `tests/test_category_data.py`

## Chunk 1: Category Configuration and Data Files

### Task 1: Add category registry with failing tests first

**Files:**
- Create: `src/categories.py`
- Test: `tests/test_categories.py`

- [ ] **Step 1: Write the failing tests for category lookup and listing**

```python
from pathlib import Path

import pytest

from src.categories import get_category_config, list_category_types


def test_get_category_config_returns_beverage_settings():
    config = get_category_config("beverage")
    assert config.type_key == "beverage"
    assert config.label == "酒水饮料"
    assert config.items_file == Path("data/categories/beverage.txt")
    assert "饮料" in config.query_suffix


def test_list_category_types_contains_all_presets():
    assert list_category_types() == [
        "beverage",
        "coffee",
        "dessert",
        "home_cooking",
        "milk_tea",
        "noodle",
        "staple_food",
        "takeout_box",
    ]


def test_get_category_config_rejects_unknown_type():
    with pytest.raises(ValueError) as exc_info:
        get_category_config("unknown")
    assert "unknown" in str(exc_info.value)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_categories.py -v`
Expected: FAIL because `src.categories` does not exist yet.

- [ ] **Step 3: Write the minimal category registry**

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CategoryConfig:
    type_key: str
    label: str
    items_file: Path
    query_suffix: str
    per_item_limit: int = 3
    search_candidate_limit: int = 12


CATEGORY_CONFIGS = {
    "home_cooking": CategoryConfig(...),
    "beverage": CategoryConfig(...),
    "takeout_box": CategoryConfig(...),
    "staple_food": CategoryConfig(...),
    "dessert": CategoryConfig(...),
    "noodle": CategoryConfig(...),
    "milk_tea": CategoryConfig(...),
    "coffee": CategoryConfig(...),
}


def get_category_config(type_key: str) -> CategoryConfig:
    try:
        return CATEGORY_CONFIGS[type_key]
    except KeyError as exc:
        supported = ", ".join(sorted(CATEGORY_CONFIGS))
        raise ValueError(f"unknown category type '{type_key}'. supported types: {supported}") from exc


def list_category_types() -> list[str]:
    return sorted(CATEGORY_CONFIGS)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_categories.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/categories.py tests/test_categories.py
git commit -m "feat: add category registry"
```

### Task 2: Add preset category data files and validation tests

**Files:**
- Create: `data/categories/home_cooking.txt`
- Create: `data/categories/beverage.txt`
- Create: `data/categories/takeout_box.txt`
- Create: `data/categories/staple_food.txt`
- Create: `data/categories/dessert.txt`
- Create: `data/categories/noodle.txt`
- Create: `data/categories/milk_tea.txt`
- Create: `data/categories/coffee.txt`
- Create: `tests/test_category_data.py`

- [ ] **Step 1: Write the failing data validation tests**

```python
from pathlib import Path

from src.categories import list_category_types


def test_all_category_files_exist_and_have_expected_item_count():
    base_dir = Path("data/categories")
    for type_key in list_category_types():
        path = base_dir / f"{type_key}.txt"
        assert path.exists()
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert 20 <= len(lines) <= 30
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_category_data.py -v`
Expected: FAIL because category data files do not exist yet.

- [ ] **Step 3: Add the preset item files**

Fill each file with 20-30 common mainland China terms that match the category:

- `beverage.txt`: 可乐, 雪碧, 芬达, 橙汁, 椰汁, 王老吉, 绿茶, 红茶, 苏打水, 椰子水, 矿泉水, 酸梅汤, 豆奶, 果粒橙, 乌龙茶, 茉莉花茶, 冰红茶, 冰绿茶, 乳酸菌饮料, 气泡水
- `coffee.txt`: 美式咖啡, 拿铁, 卡布奇诺, 摩卡, 冰美式, 生椰拿铁, 焦糖玛奇朵, 浓缩咖啡, 香草拿铁, 澳白, 手冲咖啡, 冷萃咖啡, 榛果拿铁, 燕麦拿铁, Dirty, 厚乳拿铁, 美式加冰, 热拿铁, 冰拿铁, 黑咖啡
- Use the same 20-30 item rule for the other six files.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_category_data.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add data/categories tests/test_category_data.py
git commit -m "feat: add preset category item lists"
```

## Chunk 2: Search and Pipeline Generalization

### Task 3: Generalize query building with TDD

**Files:**
- Modify: `src/search.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: Write the failing tests for configurable query suffixes**

```python
from src.search import build_query


def test_build_query_appends_category_suffix():
    assert build_query("可乐", "饮料 酒水 实拍 产品图") == "可乐 饮料 酒水 实拍 产品图"


def test_build_query_trims_empty_suffix():
    assert build_query("可乐", "") == "可乐"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_search.py -k build_query -v`
Expected: FAIL because `build_query` only accepts one parameter.

- [ ] **Step 3: Write the minimal implementation**

Update `src/search.py` so:

- `build_query(item_name: str, query_suffix: str) -> str`
- `DuckDuckGoImageSearchProvider.search()` receives a ready-made query string or receives `query_suffix`
- `WikimediaImageSearchProvider.search()` remains simple, but still uses item-oriented naming

Prefer the small interface change that disturbs the fewest call sites.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_search.py -k build_query -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/search.py tests/test_search.py
git commit -m "refactor: support category-specific search queries"
```

### Task 4: Rename pipeline models from dish semantics to item semantics

**Files:**
- Modify: `src/models.py`
- Modify: `src/pipeline.py`
- Modify: `tests/test_pipeline.py`
- Modify: `tests/test_models.py`

- [ ] **Step 1: Write the failing tests for item-oriented result fields**

```python
from src.pipeline import ItemProcessResult, process_item


def test_process_item_creates_three_manifest_rows(tmp_path):
    ...
    result = process_item(
        item_name="可乐",
        category_type="beverage",
        ...
    )
    assert isinstance(result, ItemProcessResult)
    assert result.rows[0].item_name == "可乐"
    assert result.rows[0].category_type == "beverage"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_pipeline.py tests/test_models.py -v`
Expected: FAIL because the code still uses `dish_name` and `DishProcessResult`.

- [ ] **Step 3: Write the minimal implementation**

Update:

- `CandidateImage.dish_name` -> `CandidateImage.item_name`
- `ManifestRow.dish_name` -> `ManifestRow.item_name`
- Add `ManifestRow.category_type`
- `DishProcessResult` -> `ItemProcessResult`
- `process_dish()` -> `process_item()`
- `run_pipeline()` accepts `items`, `category_type`, `per_item_limit`, `search_candidate_limit`

Keep behavior unchanged apart from naming and category metadata.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_pipeline.py tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models.py src/pipeline.py tests/test_pipeline.py tests/test_models.py
git commit -m "refactor: generalize pipeline from dishes to category items"
```

### Task 5: Update manifest writing for category-aware rows

**Files:**
- Modify: `src/manifest.py`
- Test: `tests/test_manifest.py`

- [ ] **Step 1: Write the failing manifest test**

```python
from pathlib import Path

from src.manifest import write_manifest
from src.models import ManifestRow


def test_write_manifest_includes_category_and_item_columns(tmp_path: Path):
    path = tmp_path / "manifest.csv"
    write_manifest(
        path,
        [
            ManifestRow(
                image_id="img_beverage_001",
                category_type="beverage",
                item_name="可乐",
                file_path="output/images/beverage/可乐/001.jpg",
                width=800,
                height=800,
                source_url="https://example.com/cola.jpg",
            )
        ],
    )
    rows = path.read_text(encoding="utf-8").splitlines()
    assert rows[0] == "image_id,category_type,item_name,file_path,width,height,source_url,status"
    assert "beverage,可乐" in rows[1]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_manifest.py -v`
Expected: FAIL because the manifest still writes `dish_name` only.

- [ ] **Step 3: Write the minimal implementation**

Update `src/manifest.py` header and row order to:

```python
[
    "image_id",
    "category_type",
    "item_name",
    "file_path",
    "width",
    "height",
    "source_url",
    "status",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_manifest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/manifest.py tests/test_manifest.py
git commit -m "feat: include category metadata in manifest"
```

## Chunk 3: CLI Wiring and User-Facing Behavior

### Task 6: Add `--type` CLI parsing in main

**Files:**
- Modify: `src/main.py`
- Modify: `tests/test_main.py`

- [ ] **Step 1: Write the failing main tests**

```python
from src.main import main


def test_main_uses_requested_category(monkeypatch, tmp_path):
    loaded_paths = []

    def fake_load_items(path):
        loaded_paths.append(path)
        return ["可乐"]

    monkeypatch.setattr("src.main.load_dishes", fake_load_items)
    monkeypatch.setattr("src.main.run_pipeline", lambda **kwargs: [])
    monkeypatch.setattr("src.main.OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("src.main.MANIFEST_PATH", tmp_path / "manifest.csv")

    assert main(["--type", "beverage"]) == 0
    assert loaded_paths == ["data/categories/beverage.txt"]


def test_main_rejects_unknown_category(monkeypatch, capsys):
    exit_code = main(["--type", "unknown"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "supported types" in captured.err
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_main.py -v`
Expected: FAIL because `main()` does not accept argv and still reads `data/dishes.txt`.

- [ ] **Step 3: Write the minimal implementation**

Update `src/main.py` to:

- parse args with `argparse`
- accept `main(argv: list[str] | None = None) -> int`
- default `--type` to `home_cooking`
- resolve config via `get_category_config()`
- load items from config file
- pass `category_type`, `per_item_limit`, `search_candidate_limit`, and `query_suffix` through the pipeline/search path
- print clear error text and return `1` for invalid category types

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/main.py tests/test_main.py
git commit -m "feat: add category selection CLI"
```

### Task 7: Ensure output paths are category-scoped

**Files:**
- Modify: `src/main.py`
- Modify: `src/storage.py` if needed
- Modify: `tests/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
def test_process_item_writes_files_under_category_directory(tmp_path):
    result = process_item(
        item_name="可乐",
        category_type="beverage",
        ...
    )
    assert "beverage/可乐/001.jpg" in result.rows[0].file_path
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_pipeline.py -k category_directory -v`
Expected: FAIL because output paths are not category-scoped yet.

- [ ] **Step 3: Write the minimal implementation**

Use `output/images/<category_type>` as the pipeline output root from `src.main.py`. Only touch `src/storage.py` if the existing helper cannot already work with a deeper root path.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_pipeline.py -k category_directory -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/main.py src/storage.py tests/test_pipeline.py
git commit -m "feat: scope output directories by category"
```

### Task 8: Refresh README usage and examples

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the documentation**

Document:

- the eight preset categories
- the `python -m src.main --type beverage` usage
- the new `data/categories/*.txt` structure
- the category-aware output path format
- the new manifest fields

- [ ] **Step 2: Manually review README for consistency**

Check that README examples match actual filenames, CLI arguments, and manifest columns.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update crawler usage for preset categories"
```

## Chunk 4: Verification

### Task 9: Run focused and full test verification

**Files:**
- No code changes expected unless failures are found

- [ ] **Step 1: Run focused tests for touched areas**

Run: `pytest tests/test_categories.py tests/test_category_data.py tests/test_search.py tests/test_pipeline.py tests/test_manifest.py tests/test_main.py -v`
Expected: PASS

- [ ] **Step 2: Run the full test suite**

Run: `pytest -v`
Expected: PASS

- [ ] **Step 3: Smoke-test the CLI on one category**

Run: `python -m src.main --type beverage`
Expected: process starts, reads `data/categories/beverage.txt`, and writes output under `output/images/beverage/`

- [ ] **Step 4: Review git diff**

Run: `git status --short`
Expected: only intended tracked changes remain

- [ ] **Step 5: Commit final verification fixes if needed**

```bash
git add .
git commit -m "test: finalize multi-category crawler verification"
```
