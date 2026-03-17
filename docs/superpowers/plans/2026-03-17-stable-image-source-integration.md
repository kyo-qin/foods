# Stable Image Source Integration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate optional official image APIs so the crawler prefers `Pixabay` and `Pexels` when API keys are configured, then falls back to the current search sources.

**Architecture:** Add two new query providers that match the existing single-query provider interface. Gate them behind environment variables and compose the provider chain in `src.main` so the search coordinator can remain unchanged.

**Tech Stack:** Python 3, pytest, urllib, json, environment variables

---

## File Map

- Modify: `src/config.py`
- Modify: `src/search.py`
- Modify: `src/main.py`
- Modify: `README.md`
- Modify: `tests/test_search.py`
- Modify: `tests/test_main.py`
- Modify: `tests/test_config_smoke.py`

## Chunk 1: Config and Provider Parsers

### Task 1: Add API key config with tests

**Files:**
- Modify: `src/config.py`
- Modify: `tests/test_config_smoke.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Add `PIXABAY_API_KEY` and `PEXELS_API_KEY` config values**
- [ ] **Step 4: Run tests to verify they pass**

### Task 2: Add Pixabay and Pexels providers with TDD

**Files:**
- Modify: `src/search.py`
- Modify: `tests/test_search.py`

- [ ] **Step 1: Write failing parser/provider tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement minimal providers**
- [ ] **Step 4: Run tests to verify they pass**

## Chunk 2: Main Wiring

### Task 3: Build provider chain conditionally from configured keys

**Files:**
- Modify: `src/main.py`
- Modify: `tests/test_main.py`

- [ ] **Step 1: Write failing main tests for provider ordering**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement conditional provider chain**
- [ ] **Step 4: Run tests to verify they pass**

## Chunk 3: Verification

### Task 4: Docs and end-to-end verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Document API key setup**
- [ ] **Step 2: Run focused tests**
- [ ] **Step 3: Run full test suite**
- [ ] **Step 4: Smoke-test CLI with current environment**
