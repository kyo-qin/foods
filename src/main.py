import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from src.categories import get_category_config
from src.config import PEXELS_API_KEY, PIXABAY_API_KEY, REQUEST_RETRIES, REQUEST_TIMEOUT
from src.dishes import load_dishes
from src.download import UrlopenSession, download_bytes
from src.image_processing import normalize_image
from src.manifest import write_manifest
from src.pipeline import run_pipeline
from src.search import (
    DuckDuckGoImageSearchProvider,
    EngineFallbackSearchProvider,
    FallbackSearchProvider,
    MultiQuerySearchProvider,
    PexelsImageSearchProvider,
    PixabayImageSearchProvider,
    USER_AGENT,
    WikimediaImageSearchProvider,
)
from src.storage import write_image

OUTPUT_DIR = Path("output/images")
MANIFEST_PATH = Path("output/manifest.csv")


def build_engine_providers():
    engine_providers = []
    if PIXABAY_API_KEY:
        engine_providers.append(PixabayImageSearchProvider(api_key=PIXABAY_API_KEY))
    if PEXELS_API_KEY:
        engine_providers.append(PexelsImageSearchProvider(api_key=PEXELS_API_KEY))
    engine_providers.extend(
        [
            DuckDuckGoImageSearchProvider(),
            WikimediaImageSearchProvider(),
        ]
    )
    return engine_providers


def build_probe_providers():
    return [
        ("duckduckgo", DuckDuckGoImageSearchProvider()),
        ("wikimedia", WikimediaImageSearchProvider()),
    ]


def ensure_search_providers_reachable(providers):
    errors = []
    for name, provider in providers:
        try:
            provider.search("可乐", "可乐", 1)
            return None
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    details = "\n".join(errors)
    raise RuntimeError(
        "search providers are unreachable; network access may be blocked in the current environment\n"
        f"{details}"
    )


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


def parse_args(argv: Optional[list[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", default="home_cooking", dest="category_type")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    try:
        category_config = get_category_config(args.category_type)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        ensure_search_providers_reachable(build_probe_providers())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    items = load_dishes(str(category_config.items_file))
    category_output_dir = OUTPUT_DIR / category_config.type_key
    category_output_dir.mkdir(parents=True, exist_ok=True)
    engine_provider = EngineFallbackSearchProvider(build_engine_providers())
    provider = MultiQuerySearchProvider(
        provider=engine_provider,
        query_suffixes=category_config.query_suffixes,
    )

    results = run_pipeline(
        items=items,
        category_type=category_config.type_key,
        search_provider=provider,
        output_dir=category_output_dir,
        downloader=_make_downloader(),
        normalizer=normalize_image,
        writer=write_image,
        per_item_limit=category_config.per_item_limit,
        search_candidate_limit=category_config.search_candidate_limit,
    )

    rows = [row for result in results for row in result.rows]
    write_manifest(MANIFEST_PATH, rows)
    logging.info(
        "processed %s items for %s and wrote %s images",
        len(items),
        category_config.type_key,
        len(rows),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
