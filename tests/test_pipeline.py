from pathlib import Path

from src.models import CandidateImage
from src.pipeline import ItemProcessResult, process_item


class FakeSearchProvider:
    def search(self, item_name: str, limit: int):
        return [
            CandidateImage(item_name=item_name, source_url="https://example.com/1.jpg"),
            CandidateImage(item_name=item_name, source_url="https://example.com/2.jpg"),
            CandidateImage(item_name=item_name, source_url="https://example.com/3.jpg"),
        ]


def test_process_item_creates_three_manifest_rows(tmp_path: Path):
    result = process_item(
        item_name="鱼香肉丝",
        category_type="home_cooking",
        search_provider=FakeSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: b"fake-image-bytes",
        normalizer=lambda _raw: b"normalized-image-bytes",
        writer=lambda path, data: path.write_bytes(data),
        per_item_limit=3,
        search_candidate_limit=12,
    )
    assert len(result.rows) == 3
    assert result.rows[0].item_name == "鱼香肉丝"
    assert result.rows[0].category_type == "home_cooking"
    assert result.saved_count == 3


def test_process_item_allows_shortfall_without_raising(tmp_path: Path):
    class OneResultSearchProvider:
        def search(self, item_name: str, limit: int):
            return [CandidateImage(item_name=item_name, source_url="https://example.com/1.jpg")]

    result = process_item(
        item_name="宫保鸡丁",
        category_type="home_cooking",
        search_provider=OneResultSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: b"fake-image-bytes",
        normalizer=lambda _raw: b"normalized-image-bytes",
        writer=lambda path, data: path.write_bytes(data),
        per_item_limit=3,
        search_candidate_limit=12,
    )
    assert isinstance(result, ItemProcessResult)
    assert result.saved_count == 1
    assert result.missing_count == 2


def test_process_item_requests_more_candidates_than_final_limit(tmp_path: Path):
    class RecordingSearchProvider:
        def __init__(self):
            self.last_limit = None

        def search(self, item_name: str, limit: int):
            self.last_limit = limit
            return []

    provider = RecordingSearchProvider()
    result = process_item(
        item_name="麻婆豆腐",
        category_type="home_cooking",
        search_provider=provider,
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: None,
        normalizer=lambda _raw: b"",
        writer=lambda path, data: path.write_bytes(data),
        per_item_limit=3,
        search_candidate_limit=12,
    )
    assert result.saved_count == 0
    assert provider.last_limit == 12


def test_process_item_skips_normalizer_failures(tmp_path: Path):
    class MixedSearchProvider:
        def search(self, item_name: str, limit: int):
            return [
                CandidateImage(item_name=item_name, source_url="https://example.com/bad.jpg"),
                CandidateImage(item_name=item_name, source_url="https://example.com/good1.jpg"),
                CandidateImage(item_name=item_name, source_url="https://example.com/good2.jpg"),
                CandidateImage(item_name=item_name, source_url="https://example.com/good3.jpg"),
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

    result = process_item(
        item_name="红烧肉",
        category_type="home_cooking",
        search_provider=MixedSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda url: payloads[url],
        normalizer=flaky_normalizer,
        writer=lambda path, data: path.write_bytes(data),
        per_item_limit=3,
        search_candidate_limit=12,
    )
    assert result.saved_count == 3
    assert result.attempted_count == 4


def test_process_item_does_not_record_row_when_writer_skips_existing_file(tmp_path: Path):
    class SingleSearchProvider:
        def search(self, item_name: str, limit: int):
            return [CandidateImage(item_name=item_name, source_url="https://example.com/1.jpg")]

    result = process_item(
        item_name="可乐鸡翅",
        category_type="home_cooking",
        search_provider=SingleSearchProvider(),
        output_dir=tmp_path,
        downloader=lambda *_args, **_kwargs: b"raw",
        normalizer=lambda _raw: b"normalized",
        writer=lambda path, data: False,
        per_item_limit=3,
        search_candidate_limit=12,
    )
    assert result.saved_count == 0
    assert result.rows == []


def test_process_item_writes_files_under_category_directory(tmp_path: Path):
    result = process_item(
        item_name="可乐",
        category_type="beverage",
        search_provider=FakeSearchProvider(),
        output_dir=tmp_path / "beverage",
        downloader=lambda *_args, **_kwargs: b"fake-image-bytes",
        normalizer=lambda _raw: b"normalized-image-bytes",
        writer=lambda path, data: path.write_bytes(data),
        per_item_limit=3,
        search_candidate_limit=12,
    )
    assert "beverage/可乐/001.jpg" in result.rows[0].file_path
