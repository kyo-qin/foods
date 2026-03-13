from pathlib import Path

from src.models import CandidateImage
from src.pipeline import DishProcessResult, process_dish


class FakeSearchProvider:
    def search(self, dish_name: str, limit: int):
        return [
            CandidateImage(dish_name=dish_name, source_url="https://example.com/1.jpg"),
            CandidateImage(dish_name=dish_name, source_url="https://example.com/2.jpg"),
            CandidateImage(dish_name=dish_name, source_url="https://example.com/3.jpg"),
        ]


def test_process_dish_creates_three_manifest_rows(tmp_path: Path):
    result = process_dish(
        dish_name="鱼香肉丝",
        search_provider=FakeSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: b"fake-image-bytes",
        normalizer=lambda _raw: b"normalized-image-bytes",
        writer=lambda path, data: path.write_bytes(data),
    )
    assert len(result.rows) == 3
    assert result.rows[0].dish_name == "鱼香肉丝"
    assert result.saved_count == 3


def test_process_dish_allows_shortfall_without_raising(tmp_path: Path):
    class OneResultSearchProvider:
        def search(self, dish_name: str, limit: int):
            return [CandidateImage(dish_name=dish_name, source_url="https://example.com/1.jpg")]

    result = process_dish(
        dish_name="宫保鸡丁",
        search_provider=OneResultSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: b"fake-image-bytes",
        normalizer=lambda _raw: b"normalized-image-bytes",
        writer=lambda path, data: path.write_bytes(data),
    )
    assert isinstance(result, DishProcessResult)
    assert result.saved_count == 1
    assert result.missing_count == 2


def test_process_dish_requests_more_candidates_than_final_limit(tmp_path: Path):
    class RecordingSearchProvider:
        def __init__(self):
            self.last_limit = None

        def search(self, dish_name: str, limit: int):
            self.last_limit = limit
            return []

    provider = RecordingSearchProvider()
    result = process_dish(
        dish_name="麻婆豆腐",
        search_provider=provider,
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: None,
        normalizer=lambda _raw: b"",
        writer=lambda path, data: path.write_bytes(data),
    )
    assert result.saved_count == 0
    assert provider.last_limit == 12


def test_process_dish_skips_normalizer_failures(tmp_path: Path):
    class MixedSearchProvider:
        def search(self, dish_name: str, limit: int):
            return [
                CandidateImage(dish_name=dish_name, source_url="https://example.com/bad.jpg"),
                CandidateImage(dish_name=dish_name, source_url="https://example.com/good1.jpg"),
                CandidateImage(dish_name=dish_name, source_url="https://example.com/good2.jpg"),
                CandidateImage(dish_name=dish_name, source_url="https://example.com/good3.jpg"),
            ]

    def flaky_normalizer(raw: bytes):
        if raw == b"bad":
            raise ValueError("too small")
        return b"normalized"

    payloads = {
        "https://example.com/bad.jpg": b"bad",
        "https://example.com/good1.jpg": b"good1",
        "https://example.com/good2.jpg": b"good2",
        "https://example.com/good3.jpg": b"good3",
    }

    result = process_dish(
        dish_name="红烧肉",
        search_provider=MixedSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda url: payloads[url],
        normalizer=flaky_normalizer,
        writer=lambda path, data: path.write_bytes(data),
    )
    assert result.saved_count == 3
    assert result.attempted_count == 4


def test_process_dish_does_not_record_row_when_writer_skips_existing_file(tmp_path: Path):
    class SingleSearchProvider:
        def search(self, dish_name: str, limit: int):
            return [CandidateImage(dish_name=dish_name, source_url="https://example.com/1.jpg")]

    result = process_dish(
        dish_name="可乐鸡翅",
        search_provider=SingleSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: b"raw",
        normalizer=lambda _raw: b"normalized",
        writer=lambda path, data: False,
    )
    assert result.saved_count == 0
    assert result.rows == []
