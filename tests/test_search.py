from urllib.error import URLError

from src.models import CandidateImage
from src.search import (
    FallbackSearchProvider,
    SearchProviderError,
    build_query,
)


def test_build_query_adds_chinese_food_keywords():
    query = build_query("鱼香肉丝")
    assert "鱼香肉丝" in query
    assert "中餐" in query
    assert "实拍" in query


def test_fallback_search_provider_uses_second_provider_when_first_fails():
    class FailingProvider:
        def search(self, dish_name: str, limit: int):
            raise SearchProviderError("primary failed")

    class WorkingProvider:
        def search(self, dish_name: str, limit: int):
            return [CandidateImage(dish_name=dish_name, source_url="https://example.com/1.jpg")]

    provider = FallbackSearchProvider([FailingProvider(), WorkingProvider()])
    results = provider.search("鱼香肉丝", 3)
    assert len(results) == 1
    assert results[0].dish_name == "鱼香肉丝"


def test_fallback_search_provider_returns_empty_when_all_providers_fail():
    class FailingProvider:
        def search(self, dish_name: str, limit: int):
            raise SearchProviderError("provider failed")

    provider = FallbackSearchProvider([FailingProvider()])
    assert provider.search("鱼香肉丝", 3) == []
