from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from src.config import IMAGE_SIZE, PER_DISH_LIMIT, SEARCH_CANDIDATE_LIMIT
from src.models import ManifestRow
from src.storage import build_output_path


@dataclass
class DishProcessResult:
    dish_name: str
    saved_count: int
    attempted_count: int
    missing_count: int
    rows: list[ManifestRow] = field(default_factory=list)


def process_dish(
    dish_name: str,
    search_provider,
    output_dir: Path,
    downloader: Callable,
    normalizer: Callable[[bytes], bytes],
    writer: Callable[[Path, bytes], object],
) -> DishProcessResult:
    candidates = search_provider.search(dish_name, SEARCH_CANDIDATE_LIMIT)
    rows: list[ManifestRow] = []
    attempted_count = 0

    for candidate in candidates:
        if len(rows) >= PER_DISH_LIMIT:
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
            output_path = build_output_path(output_dir, dish_name, len(rows) + 1)
            write_result = writer(output_path, normalized)
        except Exception:
            continue
        if write_result is False:
            continue
        rows.append(
            ManifestRow(
                image_id=f"img_{dish_name}_{len(rows) + 1:03d}",
                dish_name=dish_name,
                file_path=str(output_path),
                width=IMAGE_SIZE[0],
                height=IMAGE_SIZE[1],
                source_url=candidate.source_url,
            )
        )

    return DishProcessResult(
        dish_name=dish_name,
        saved_count=len(rows),
        attempted_count=attempted_count,
        missing_count=max(PER_DISH_LIMIT - len(rows), 0),
        rows=rows,
    )


def run_pipeline(
    dishes: Iterable[str],
    search_provider,
    output_dir: Path,
    downloader: Callable,
    normalizer: Callable[[bytes], bytes],
    writer: Callable[[Path, bytes], object],
) -> list[DishProcessResult]:
    return [
        process_dish(
            dish_name=dish_name,
            search_provider=search_provider,
            output_dir=output_dir,
            downloader=downloader,
            normalizer=normalizer,
            writer=writer,
        )
        for dish_name in dishes
    ]
