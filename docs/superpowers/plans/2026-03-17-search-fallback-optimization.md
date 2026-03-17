# Search Fallback Optimization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve crawler success rate by replacing the single fixed query suffix per category with ordered fallback query templates, deduplicating candidates across queries, and logging query-level hit counts.

**Architecture:** Keep the existing provider implementations responsible for single-query execution. Move fallback orchestration into a small search-layer coordinator driven by category config. Update category config to hold multiple query suffixes per type and let the main entrypoint inject those templates into the search layer.

**Tech Stack:** Python 3, pytest, dataclasses, logging

---

## File Map

- Modify: `src/categories.py`
- Modify: `src/search.py`
- Modify: `src/main.py`
- Modify: `tests/test_categories.py`
- Modify: `tests/test_search.py`
- Optionally modify: `README.md`

## Chunk 1: Category Query Template Expansion

### Task 1: Replace single query suffix with ordered suffix templates

**Files:**
- Modify: `src/categories.py`
- Modify: `tests/test_categories.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.categories import get_category_config


def test_beverage_category_has_fallback_query_suffixes():
    config = get_category_config("beverage")
    assert config.query_suffixes == (
        "饮料 酒水 实拍 产品图",
        "饮料 实拍",
        "饮料",
        "",
    )


def test_home_cooking_category_keeps_more_conservative_fallbacks():
    config = get_category_config("home_cooking")
    assert config.query_suffixes[-1] == "中餐 实拍"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_categories.py -v`
Expected: FAIL because config still exposes `query_suffix`.

- [ ] **Step 3: Write the minimal implementation**

Update `CategoryConfig` to use:

```python
query_suffixes: tuple[str, ...]
```

Fill all 8 preset types with ordered fallback suffixes, with wider fallbacks for:

- `beverage`
- `milk_tea`
- `coffee`

and more conservative fallbacks for the other five types.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_categories.py -v`
Expected: PASS

## Chunk 2: Search Fallback Coordinator

### Task 2: Add multi-query candidate aggregation with TDD

**Files:**
- Modify: `src/search.py`
- Modify: `tests/test_search.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.models import CandidateImage
from src.search import MultiQuerySearchProvider


def test_multi_query_search_provider_falls_back_when_first_query_has_no_results():
    class FakeProvider:
        def __init__(self):
            self.queries = []

        def search(self, query: str, item_name: str, limit: int):
            self.queries.append(query)
            if query == "可乐 饮料 酒水 实拍 产品图":
                return []
            return [CandidateImage(item_name=item_name, source_url="https://example.com/cola.jpg")]

    provider = MultiQuerySearchProvider(
        provider=FakeProvider(),
        query_suffixes=("饮料 酒水 实拍 产品图", "饮料 实拍"),
    )

    results = provider.search("可乐", 12)
    assert len(results) == 1
    assert provider.provider.queries == [
        "可乐 饮料 酒水 实拍 产品图",
        "可乐 饮料 实拍",
    ]


def test_multi_query_search_provider_deduplicates_urls_across_queries():
    class FakeProvider:
        def search(self, query: str, item_name: str, limit: int):
            return [
                CandidateImage(item_name=item_name, source_url="https://example.com/shared.jpg"),
                CandidateImage(item_name=item_name, source_url=f"https://example.com/{query}.jpg"),
            ]

    provider = MultiQuerySearchProvider(
        provider=FakeProvider(),
        query_suffixes=("饮料 实拍", "饮料"),
    )

    results = provider.search("可乐", 12)
    assert len(results) == 3


def test_multi_query_search_provider_stops_after_reaching_limit():
    class FakeProvider:
        def __init__(self):
            self.calls = 0

        def search(self, query: str, item_name: str, limit: int):
            self.calls += 1
            return [
                CandidateImage(item_name=item_name, source_url="https://example.com/1.jpg"),
                CandidateImage(item_name=item_name, source_url="https://example.com/2.jpg"),
            ]

    provider = MultiQuerySearchProvider(
        provider=FakeProvider(),
        query_suffixes=("饮料 实拍", "饮料", ""),
    )

    results = provider.search("可乐", 2)
    assert len(results) == 2
    assert provider.provider.calls == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_search.py -v`
Expected: FAIL because `MultiQuerySearchProvider` does not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Refactor the provider interface so single-query providers can execute an explicit query string for a given item, then add:

```python
class MultiQuerySearchProvider:
    def __init__(self, provider, query_suffixes, logger=None):
        ...

    def search(self, item_name: str, limit: int) -> list[CandidateImage]:
        ...
```

Behavior:

- Build each query with `build_query(item_name, suffix)`
- Call the wrapped provider once per query
- Deduplicate by `source_url`
- Stop when unique result count reaches `limit`
- Log item/query/result counts per round

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_search.py -v`
Expected: PASS

## Chunk 3: Entry Point Wiring

### Task 3: Inject fallback query templates into main

**Files:**
- Modify: `src/main.py`
- Modify: `tests/test_main.py`

- [ ] **Step 1: Write the failing test**

```python
def test_main_builds_search_provider_with_category_query_fallbacks(monkeypatch, tmp_path):
    captured_provider = {}

    def fake_run_pipeline(**kwargs):
        captured_provider["provider"] = kwargs["search_provider"]
        return []

    monkeypatch.setattr("src.main.load_dishes", lambda _path: ["可乐"])
    monkeypatch.setattr("src.main.run_pipeline", fake_run_pipeline)
    ...

    assert main(["--type", "beverage"]) == 0
    assert captured_provider["provider"].query_suffixes[0] == "饮料 酒水 实拍 产品图"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_main.py -v`
Expected: FAIL because `main` still injects a single suffix.

- [ ] **Step 3: Write the minimal implementation**

Update `src.main.py` to construct:

- a single-query fallback provider stack for actual engines
- a `MultiQuerySearchProvider` wrapper configured with `category_config.query_suffixes`

Keep the rest of the pipeline unchanged.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_main.py -v`
Expected: PASS

## Chunk 4: Verification

### Task 4: Verify tests and smoke test beverage crawling

**Files:**
- No code changes expected unless failures are found

- [ ] **Step 1: Run focused tests**

Run: `pytest tests/test_categories.py tests/test_search.py tests/test_main.py -v`
Expected: PASS

- [ ] **Step 2: Run the full test suite**

Run: `pytest -v`
Expected: PASS

- [ ] **Step 3: Smoke-test beverage crawl**

Run: `python3 -m src.main --type beverage`
Expected: command completes; logs show per-query hit counts; success rate should be measurably better than the prior zero-image run

- [ ] **Step 4: Review worktree state**

Run: `git status --short`
Expected: only intended changes are present
