import logging
from pathlib import Path

from src.config import REQUEST_RETRIES, REQUEST_TIMEOUT, SEARCH_CANDIDATE_LIMIT
from src.dishes import load_dishes
from src.download import UrlopenSession, download_bytes
from src.image_processing import normalize_image
from src.manifest import write_manifest
from src.pipeline import run_pipeline
from src.search import (
    DuckDuckGoImageSearchProvider,
    FallbackSearchProvider,
    USER_AGENT,
    WikimediaImageSearchProvider,
)
from src.storage import write_image

DATA_PATH = Path("data/dishes.txt")
OUTPUT_DIR = Path("output/images")
MANIFEST_PATH = Path("output/manifest.csv")


def _make_downloader():
    session = UrlopenSession(USER_AGENT)

    def _download(url: str):
        return download_bytes(
            url=url,
            session=session,
            timeout=REQUEST_TIMEOUT,
            retries=REQUEST_RETRIES,
        )

    return _download


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    dishes = load_dishes(str(DATA_PATH))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    provider = FallbackSearchProvider(
        [DuckDuckGoImageSearchProvider(), WikimediaImageSearchProvider()]
    )

    results = run_pipeline(
        dishes=dishes,
        search_provider=provider,
        output_dir=OUTPUT_DIR,
        downloader=_make_downloader(),
        normalizer=normalize_image,
        writer=write_image,
    )

    rows = [row for result in results for row in result.rows]
    write_manifest(MANIFEST_PATH, rows)
    logging.info("processed %s dishes and wrote %s images", len(dishes), len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
