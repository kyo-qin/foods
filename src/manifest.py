import csv
from pathlib import Path
from typing import Iterable

from src.models import ManifestRow


def write_manifest(path: Path, rows: Iterable[ManifestRow]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["image_id", "dish_name", "file_path", "width", "height", "source_url", "status"]
        )
        for row in rows:
            writer.writerow(
                [
                    row.image_id,
                    row.dish_name,
                    row.file_path,
                    row.width,
                    row.height,
                    row.source_url,
                    row.status,
                ]
            )
