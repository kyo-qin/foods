from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from src.models import ManifestRow
from src.storage import build_output_path


@dataclass
class ItemProcessResult:
    item_name: str
    saved_count: int
    attempted_count: int
    missing_count: int
    rows: list[ManifestRow] = field(default_factory=list)


def process_item(
    item_name: str,
    category_type: str,
    search_provider,
    output_dir: Path,
    downloader: Callable,
    normalizer: Callable[[bytes], bytes],
    writer: Callable[[Path, bytes], object],
    per_item_limit: int,
    search_candidate_limit: int,
) -> ItemProcessResult:
    candidates = search_provider.search(item_name, search_candidate_limit)
    rows: list[ManifestRow] = []
    attempted_count = 0

    for candidate in candidates:
        if len(rows) >= per_item_limit:
            break
        attempted_count += 1
        try:
            raw_bytes = downloader(candidate.source_url)
        except Exception:
            continue
        if not raw_bytes:
            continue

        try:
            normalized = normalizer(raw_bytes)
            output_path = build_output_path(output_dir, item_name, len(rows) + 1)
            write_result = writer(output_path, normalized)
        except Exception:
            continue
        if write_result is False:
            continue
        rows.append(
            ManifestRow(
                image_id=f"img_{category_type}_{item_name}_{len(rows) + 1:03d}",
                category_type=category_type,
                item_name=item_name,
                file_path=str(output_path),
                width=800,
                height=800,
                source_url=candidate.source_url,
            )
        )

    return ItemProcessResult(
        item_name=item_name,
        saved_count=len(rows),
        attempted_count=attempted_count,
        missing_count=max(per_item_limit - len(rows), 0),
        rows=rows,
    )


def run_pipeline(
    items: Iterable[str],
    category_type: str,
    search_provider,
    output_dir: Path,
    downloader: Callable,
    normalizer: Callable[[bytes], bytes],
    writer: Callable[[Path, bytes], object],
    per_item_limit: int,
    search_candidate_limit: int,
) -> list[ItemProcessResult]:
    return [
        process_item(
            item_name=item_name,
            category_type=category_type,
            search_provider=search_provider,
            output_dir=output_dir,
            downloader=downloader,
            normalizer=normalizer,
            writer=writer,
            per_item_limit=per_item_limit,
            search_candidate_limit=search_candidate_limit,
        )
        for item_name in items
    ]
