# Chinese Dish Image Crawler Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local CLI project that collects 50-100 common Chinese restaurant dish names, searches public web images for each dish, downloads candidates, converts accepted images to 800x800 output files, stores them by dish name, and exports a CSV manifest with image IDs and dish names.

**Architecture:** Use a small Python package with a single CLI entry point that coordinates dish loading, image search, download, validation, image normalization, output writing, and CSV export. Keep the search provider behind a simple interface so the first implementation can use one public image-search strategy while leaving room to add site-specific providers later.

**Tech Stack:** Python 3.11+, `requests`, `Pillow`, `pytest`, standard library `csv`, `pathlib`, `logging`, `dataclasses`

---

## File Structure

- `README.md`
  Purpose: project setup, dependency install, run instructions, output layout.
- `requirements.txt`
  Purpose: runtime dependencies.
- `requirements-dev.txt`
  Purpose: test dependencies.
- `data/dishes.txt`
  Purpose: built-in list of 50-100 common Chinese restaurant dish names.
- `src/__init__.py`
  Purpose: package marker.
- `src/main.py`
  Purpose: CLI entry point and top-level orchestration.
- `src/config.py`
  Purpose: central constants such as output paths, image size, retries, per-dish limits.
- `src/models.py`
  Purpose: dataclasses for candidate images, processed images, and manifest rows.
- `src/dishes.py`
  Purpose: load and validate dish names from `data/dishes.txt`.
- `src/search.py`
  Purpose: image search provider interface and query builder.
- `src/download.py`
  Purpose: download candidate images with retries and response validation.
- `src/image_processing.py`
  Purpose: decode, validate, crop, resize, and encode 800x800 JPEG output.
- `src/storage.py`
  Purpose: create output directories, assign file names, write images, and manage incremental skips.
- `src/manifest.py`
  Purpose: generate and append CSV rows.
- `src/pipeline.py`
  Purpose: per-dish pipeline coordination and result summary.
- `tests/test_dishes.py`
  Purpose: dish list loading and validation tests.
- `tests/test_image_processing.py`
  Purpose: image filtering and 800x800 conversion tests.
- `tests/test_manifest.py`
  Purpose: CSV row serialization tests.
- `tests/test_storage.py`
  Purpose: output naming and directory-writing tests.
- `tests/test_pipeline.py`
  Purpose: end-to-end pipeline tests with mocked search and download components.

## Chunk 1: Project Skeleton And Dependencies

### Task 1: Create the Python project scaffold

**Files:**
- Create: `README.md`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `src/__init__.py`
- Create: `src/main.py`
- Create: `src/config.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Write the failing smoke test**

```python
from src.config import IMAGE_SIZE


def test_default_image_size_is_square():
    assert IMAGE_SIZE == (800, 800)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing constant.

- [ ] **Step 3: Write minimal implementation**

```python
# src/config.py
IMAGE_SIZE = (800, 800)
PER_DISH_LIMIT = 3
```

```python
# src/main.py
def main() -> int:
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add dependency manifests**

`requirements.txt`
```text
requests
Pillow
```

`requirements-dev.txt`
```text
-r requirements.txt
pytest
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_config_smoke.py -v`
Expected: PASS

## Chunk 2: Built-In Dish List

### Task 2: Add the built-in 50-100 dish list and loader

**Files:**
- Create: `data/dishes.txt`
- Create: `src/dishes.py`
- Create: `tests/test_dishes.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.dishes import load_dishes


def test_load_dishes_returns_at_least_50_unique_names():
    dishes = load_dishes("data/dishes.txt")
    assert len(dishes) >= 50
    assert len(dishes) == len(set(dishes))


def test_load_dishes_strips_blank_lines():
    dishes = load_dishes("tests/fixtures/dishes_sample.txt")
    assert dishes == ["鱼香肉丝", "宫保鸡丁"]
```

- [ ] **Step 2: Add fixture file for blank-line handling**

Create `tests/fixtures/dishes_sample.txt`:
```text

鱼香肉丝

宫保鸡丁
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_dishes.py -v`
Expected: FAIL because loader does not exist.

- [ ] **Step 4: Write minimal implementation**

```python
from pathlib import Path


def load_dishes(path: str) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    dishes: list[str] = []
    seen: set[str] = set()
    for raw in lines:
        name = raw.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        dishes.append(name)
    return dishes
```

- [ ] **Step 5: Populate `data/dishes.txt` with 50-100 common dishes**

Use a curated plain-text list such as:
```text
鱼香肉丝
宫保鸡丁
麻婆豆腐
回锅肉
水煮鱼
...
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_dishes.py -v`
Expected: PASS

## Chunk 3: Data Models And CSV Manifest

### Task 3: Define data models for pipeline state

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.models import CandidateImage, ManifestRow


def test_manifest_row_defaults_to_ok_status():
    row = ManifestRow(
        image_id="img_000001",
        dish_name="鱼香肉丝",
        file_path="output/images/鱼香肉丝/001.jpg",
        width=800,
        height=800,
        source_url="https://example.com/1.jpg",
    )
    assert row.status == "ok"


def test_candidate_image_tracks_source_url():
    item = CandidateImage(dish_name="鱼香肉丝", source_url="https://example.com/1.jpg")
    assert item.source_url.endswith(".jpg")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`
Expected: FAIL because models do not exist.

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass


@dataclass(slots=True)
class CandidateImage:
    dish_name: str
    source_url: str


@dataclass(slots=True)
class ManifestRow:
    image_id: str
    dish_name: str
    file_path: str
    width: int
    height: int
    source_url: str
    status: str = "ok"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`
Expected: PASS

### Task 4: Implement manifest CSV writer

**Files:**
- Create: `src/manifest.py`
- Create: `tests/test_manifest.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from src.manifest import write_manifest
from src.models import ManifestRow


def test_write_manifest_creates_csv_with_header(tmp_path: Path):
    target = tmp_path / "manifest.csv"
    rows = [
        ManifestRow(
            image_id="img_000001",
            dish_name="鱼香肉丝",
            file_path="output/images/鱼香肉丝/001.jpg",
            width=800,
            height=800,
            source_url="https://example.com/1.jpg",
        )
    ]

    write_manifest(target, rows)

    content = target.read_text(encoding="utf-8")
    assert "image_id,dish_name,file_path,width,height,source_url,status" in content
    assert "img_000001,鱼香肉丝" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_manifest.py -v`
Expected: FAIL because writer does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
import csv


def write_manifest(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["image_id", "dish_name", "file_path", "width", "height", "source_url", "status"])
        for row in rows:
            writer.writerow([row.image_id, row.dish_name, row.file_path, row.width, row.height, row.source_url, row.status])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_manifest.py -v`
Expected: PASS

## Chunk 4: Search Query And Candidate Fetching

### Task 5: Build the search query layer

**Files:**
- Create: `src/search.py`
- Create: `tests/test_search.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.search import build_query


def test_build_query_adds_chinese_food_keywords():
    query = build_query("鱼香肉丝")
    assert "鱼香肉丝" in query
    assert "中餐" in query
    assert "实拍" in query
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_search.py -v`
Expected: FAIL because query builder does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def build_query(dish_name: str) -> str:
    return f"{dish_name} 中餐 菜品图 实拍"
```

- [ ] **Step 4: Add provider protocol skeleton**

```python
from typing import Protocol

from src.models import CandidateImage


class SearchProvider(Protocol):
    def search(self, dish_name: str, limit: int) -> list[CandidateImage]:
        ...
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_search.py -v`
Expected: PASS

### Task 6: Implement image downloader with retries and content checks

**Files:**
- Create: `src/download.py`
- Create: `tests/test_download.py`

- [ ] **Step 1: Write the failing tests**

```python
from unittest.mock import Mock

from src.download import is_image_response


def test_is_image_response_accepts_image_content_type():
    response = Mock(headers={"Content-Type": "image/jpeg"})
    assert is_image_response(response) is True


def test_is_image_response_rejects_html():
    response = Mock(headers={"Content-Type": "text/html"})
    assert is_image_response(response) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_download.py -v`
Expected: FAIL because helper does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def is_image_response(response) -> bool:
    content_type = response.headers.get("Content-Type", "")
    return content_type.startswith("image/")
```

- [ ] **Step 4: Extend implementation with download function**

```python
import requests


def download_bytes(url: str, session: requests.Session, timeout: int, retries: int) -> bytes | None:
    for _ in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            if response.ok and is_image_response(response):
                return response.content
        except requests.RequestException:
            continue
    return None
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_download.py -v`
Expected: PASS

## Chunk 5: Image Validation, Resize, And Storage

### Task 7: Implement image normalization to 800x800 JPEG

**Files:**
- Create: `src/image_processing.py`
- Create: `tests/test_image_processing.py`

- [ ] **Step 1: Write the failing tests**

```python
from io import BytesIO

from PIL import Image

from src.image_processing import normalize_image


def make_image_bytes(size=(1200, 900), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_normalize_image_returns_800_square():
    result = normalize_image(make_image_bytes())
    image = Image.open(BytesIO(result))
    assert image.size == (800, 800)
    assert image.format == "JPEG"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_image_processing.py -v`
Expected: FAIL because processor does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
from io import BytesIO

from PIL import Image


def normalize_image(raw_bytes: bytes) -> bytes:
    with Image.open(BytesIO(raw_bytes)) as image:
        image = image.convert("RGB")
        width, height = image.size
        crop_size = min(width, height)
        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        image = image.crop((left, top, left + crop_size, top + crop_size))
        image = image.resize((800, 800))
        output = BytesIO()
        image.save(output, format="JPEG", quality=90)
        return output.getvalue()
```

- [ ] **Step 4: Add a minimum-size validation test**

```python
import pytest

from src.image_processing import normalize_image, ImageTooSmallError


def test_normalize_image_rejects_small_images():
    with pytest.raises(ImageTooSmallError):
        normalize_image(make_image_bytes(size=(200, 200)))
```

- [ ] **Step 5: Extend implementation to reject tiny images**

```python
class ImageTooSmallError(ValueError):
    pass
```

Reject images where the shorter side is below a configured threshold such as `400`.

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_image_processing.py -v`
Expected: PASS

### Task 8: Implement output storage and stable naming

**Files:**
- Create: `src/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

from src.storage import build_output_path, ensure_output_dirs


def test_build_output_path_uses_dish_directory(tmp_path: Path):
    path = build_output_path(tmp_path, "鱼香肉丝", 1)
    assert path == tmp_path / "鱼香肉丝" / "001.jpg"


def test_ensure_output_dirs_creates_directory(tmp_path: Path):
    dish_dir = ensure_output_dirs(tmp_path, "鱼香肉丝")
    assert dish_dir.exists()
    assert dish_dir.is_dir()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_storage.py -v`
Expected: FAIL because storage helpers do not exist.

- [ ] **Step 3: Write minimal implementation**

```python
from pathlib import Path


def ensure_output_dirs(base_dir: Path, dish_name: str) -> Path:
    dish_dir = base_dir / dish_name
    dish_dir.mkdir(parents=True, exist_ok=True)
    return dish_dir


def build_output_path(base_dir: Path, dish_name: str, index: int) -> Path:
    return ensure_output_dirs(base_dir, dish_name) / f"{index:03d}.jpg"
```

- [ ] **Step 4: Add image write helper and overwrite policy**

Write a helper that skips writing when the target file already exists unless `overwrite=True`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_storage.py -v`
Expected: PASS

## Chunk 6: Pipeline Orchestration

### Task 9: Implement per-dish processing pipeline with mocks

**Files:**
- Create: `src/pipeline.py`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from src.models import CandidateImage
from src.pipeline import process_dish


class FakeSearchProvider:
    def search(self, dish_name: str, limit: int):
        return [
            CandidateImage(dish_name=dish_name, source_url="https://example.com/1.jpg"),
            CandidateImage(dish_name=dish_name, source_url="https://example.com/2.jpg"),
            CandidateImage(dish_name=dish_name, source_url="https://example.com/3.jpg"),
        ]


def test_process_dish_creates_three_manifest_rows(tmp_path: Path):
    rows = process_dish(
        dish_name="鱼香肉丝",
        search_provider=FakeSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: b"fake-image-bytes",
        normalizer=lambda _raw: b"normalized-image-bytes",
        writer=lambda path, data: path.write_bytes(data),
    )
    assert len(rows) == 3
    assert rows[0].dish_name == "鱼香肉丝"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL because pipeline does not exist.

- [ ] **Step 3: Write minimal implementation**

Implement `process_dish(...)` so it:
- requests candidates from the search provider
- loops through candidates until 3 images are accepted
- downloads bytes
- normalizes the image
- writes `001.jpg`, `002.jpg`, `003.jpg`
- returns manifest rows for accepted files

- [ ] **Step 4: Extend test coverage for shortfall handling**

Add a test that returns only one valid image and assert the pipeline returns one row without raising.

- [ ] **Step 5: Add summary result object**

Create a small result structure that records:
- `dish_name`
- `saved_count`
- `attempted_count`
- `missing_count`

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS

### Task 10: Wire the full CLI entry point

**Files:**
- Modify: `src/main.py`
- Modify: `src/config.py`
- Modify: `src/pipeline.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write the failing CLI test**

```python
from src.main import main


def test_main_returns_zero_for_success(monkeypatch, tmp_path):
    monkeypatch.setattr("src.main.load_dishes", lambda _path: ["鱼香肉丝"])
    monkeypatch.setattr("src.main.run_pipeline", lambda **_kwargs: [])
    assert main() == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_main.py -v`
Expected: FAIL because orchestration is incomplete.

- [ ] **Step 3: Implement CLI orchestration**

`main()` should:
- load dishes from `data/dishes.txt`
- prepare output directories
- construct provider/session objects
- run the pipeline
- write `output/manifest.csv`
- return `0` on success

- [ ] **Step 4: Add logging configuration**

Log:
- dish start
- accepted image count
- per-dish shortfall
- final totals

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_main.py -v`
Expected: PASS

## Chunk 7: End-To-End Verification And Documentation

### Task 11: Document setup and usage

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write README sections**

Document:
- Python version
- install commands
- run command
- output structure
- notes about public-image quality and copyright review

- [ ] **Step 2: Add an example command**

```bash
python -m src.main
```

- [ ] **Step 3: Add example output tree**

```text
output/
├── images/
│   └── 鱼香肉丝/
│       ├── 001.jpg
│       ├── 002.jpg
│       └── 003.jpg
└── manifest.csv
```

### Task 12: Run full verification

**Files:**
- Modify: none

- [ ] **Step 1: Run the full unit test suite**

Run: `pytest -v`
Expected: all tests PASS

- [ ] **Step 2: Run one local smoke execution**

Run: `python -m src.main`
Expected:
- creates `output/images/`
- creates `output/manifest.csv`
- logs per-dish progress

- [ ] **Step 3: Inspect generated outputs**

Check:
- every generated image opens successfully
- every generated image is 800x800
- manifest row count matches saved image count

- [ ] **Step 4: Record known limitations**

Document any of:
- dishes with fewer than 3 valid images
- unstable search results
- provider-specific throttling or blocking

