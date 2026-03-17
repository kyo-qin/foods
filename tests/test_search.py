from src.models import CandidateImage
from src.search import (
    FallbackSearchProvider,
    MultiQuerySearchProvider,
    PexelsImageSearchProvider,
    PixabayImageSearchProvider,
    SearchProviderError,
    build_query,
)


def test_build_query_appends_category_suffix():
    assert build_query("可乐", "饮料 酒水 实拍 产品图") == "可乐 饮料 酒水 实拍 产品图"


def test_build_query_trims_empty_suffix():
    assert build_query("可乐", "") == "可乐"


def test_fallback_search_provider_uses_second_provider_when_first_fails():
    class FailingProvider:
        def search(self, item_name: str, limit: int):
            raise SearchProviderError("primary failed")

    class WorkingProvider:
        def search(self, item_name: str, limit: int):
            return [CandidateImage(item_name=item_name, source_url="https://example.com/1.jpg")]

    provider = FallbackSearchProvider([FailingProvider(), WorkingProvider()])
    results = provider.search("鱼香肉丝", 3)
    assert len(results) == 1
    assert results[0].item_name == "鱼香肉丝"


def test_fallback_search_provider_returns_empty_when_all_providers_fail():
    class FailingProvider:
        def search(self, item_name: str, limit: int):
            raise SearchProviderError("provider failed")

    provider = FallbackSearchProvider([FailingProvider()])
    assert provider.search("鱼香肉丝", 3) == []


def test_multi_query_search_provider_falls_back_when_first_query_has_no_results():
    class FakeProvider:
        def __init__(self):
            self.queries = []

        def search(self, query: str, item_name: str, limit: int):
            self.queries.append(query)
            if query == "可乐 饮料 酒水 实拍 产品图":
                return []
            return [CandidateImage(item_name=item_name, source_url="https://example.com/cola.jpg")]

    inner_provider = FakeProvider()
    provider = MultiQuerySearchProvider(
        provider=inner_provider,
        query_suffixes=("饮料 酒水 实拍 产品图", "饮料 实拍"),
    )

    results = provider.search("可乐", 12)
    assert len(results) == 1
    assert inner_provider.queries == [
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

    inner_provider = FakeProvider()
    provider = MultiQuerySearchProvider(
        provider=inner_provider,
        query_suffixes=("饮料 实拍", "饮料", ""),
    )

    results = provider.search("可乐", 2)
    assert len(results) == 2
    assert inner_provider.calls == 1


def test_pixabay_provider_extracts_image_urls():
    provider = PixabayImageSearchProvider(api_key="key")
    payload = {
        "hits": [
            {"largeImageURL": "https://example.com/a.jpg"},
            {"webformatURL": "https://example.com/b.jpg"},
        ]
    }
    results = provider._parse_payload(payload, "可乐", 2)
    assert [row.source_url for row in results] == [
        "https://example.com/a.jpg",
        "https://example.com/b.jpg",
    ]


def test_pexels_provider_extracts_image_urls():
    provider = PexelsImageSearchProvider(api_key="key")
    payload = {
        "photos": [
            {"src": {"large": "https://example.com/a.jpg"}},
            {"src": {"original": "https://example.com/b.jpg"}},
        ]
    }
    results = provider._parse_payload(payload, "可乐", 2)
    assert [row.source_url for row in results] == [
        "https://example.com/a.jpg",
        "https://example.com/b.jpg",
    ]
