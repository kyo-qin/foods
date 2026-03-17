import json
import logging
import re
from typing import Optional, Protocol
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from src.models import CandidateImage

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def build_query(item_name: str, query_suffix: str) -> str:
    return f"{item_name} {query_suffix}".strip()


class SearchProvider(Protocol):
    def search(self, item_name: str, limit: int) -> list[CandidateImage]:
        ...


class QuerySearchProvider(Protocol):
    def search(self, query: str, item_name: str, limit: int) -> list[CandidateImage]:
        ...


class SearchProviderError(RuntimeError):
    pass


class FallbackSearchProvider:
    def __init__(self, providers):
        self.providers = providers

    def search(self, item_name: str, limit: int) -> list[CandidateImage]:
        for provider in self.providers:
            try:
                results = provider.search(item_name, limit)
            except Exception:
                continue
            if results:
                return results
        return []


class DuckDuckGoImageSearchProvider:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def search(self, query: str, item_name: str, limit: int) -> list[CandidateImage]:
        vqd = self._fetch_vqd(query)
        if not vqd:
            return []

        payload = self._fetch_results(query, vqd)
        results: list[CandidateImage] = []
        for item in payload.get("results", []):
            image_url = item.get("image")
            if not image_url:
                continue
            results.append(CandidateImage(item_name=item_name, source_url=image_url))
            if len(results) >= limit:
                break
        return results

    def _fetch_vqd(self, query: str) -> Optional[str]:
        try:
            url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=self.timeout) as response:
                html = response.read().decode("utf-8", errors="ignore")
        except Exception as exc:
            raise SearchProviderError(str(exc)) from exc
        match = re.search(r'vqd="([^"]+)"', html) or re.search(r"vqd=([0-9-]+)&", html)
        return match.group(1) if match else None

    def _fetch_results(self, query: str, vqd: str) -> dict:
        try:
            url = (
                "https://duckduckgo.com/i.js?"
                f"q={quote_plus(query)}&o=json&p=1&l=wt-wt&f=,,,&vqd={quote_plus(vqd)}"
            )
            request = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Referer": "https://duckduckgo.com/",
                    "Accept": "application/json",
                },
            )
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise SearchProviderError(str(exc)) from exc


class WikimediaImageSearchProvider:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def search(self, query: str, item_name: str, limit: int) -> list[CandidateImage]:
        url = (
            "https://commons.wikimedia.org/w/api.php?action=query&format=json"
            f"&generator=search&gsrnamespace=6&gsrsearch={quote_plus(query)}"
            f"&gsrlimit={limit}&prop=imageinfo&iiprop=url"
        )
        request = Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise SearchProviderError(str(exc)) from exc

        pages = payload.get("query", {}).get("pages", {})
        results: list[CandidateImage] = []
        for page in pages.values():
            imageinfo = page.get("imageinfo", [])
            if not imageinfo:
                continue
            image_url = imageinfo[0].get("url")
            if not image_url:
                continue
            results.append(CandidateImage(item_name=item_name, source_url=image_url))
            if len(results) >= limit:
                break
        return results


class PixabayImageSearchProvider:
    def __init__(self, api_key: str, timeout: int = 15):
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str, item_name: str, limit: int) -> list[CandidateImage]:
        params = urlencode(
            {
                "key": self.api_key,
                "q": query,
                "image_type": "photo",
                "lang": "zh",
                "per_page": limit,
            }
        )
        request = Request(
            f"https://pixabay.com/api/?{params}",
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise SearchProviderError(str(exc)) from exc
        return self._parse_payload(payload, item_name, limit)

    def _parse_payload(self, payload: dict, item_name: str, limit: int) -> list[CandidateImage]:
        results: list[CandidateImage] = []
        for item in payload.get("hits", []):
            image_url = item.get("largeImageURL") or item.get("webformatURL")
            if not image_url:
                continue
            results.append(CandidateImage(item_name=item_name, source_url=image_url))
            if len(results) >= limit:
                break
        return results


class PexelsImageSearchProvider:
    def __init__(self, api_key: str, timeout: int = 15):
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str, item_name: str, limit: int) -> list[CandidateImage]:
        params = urlencode({"query": query, "per_page": limit})
        request = Request(
            f"https://api.pexels.com/v1/search?{params}",
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "Authorization": self.api_key,
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise SearchProviderError(str(exc)) from exc
        return self._parse_payload(payload, item_name, limit)

    def _parse_payload(self, payload: dict, item_name: str, limit: int) -> list[CandidateImage]:
        results: list[CandidateImage] = []
        for item in payload.get("photos", []):
            src = item.get("src", {})
            image_url = src.get("large") or src.get("original")
            if not image_url:
                continue
            results.append(CandidateImage(item_name=item_name, source_url=image_url))
            if len(results) >= limit:
                break
        return results


class EngineFallbackSearchProvider:
    def __init__(self, providers):
        self.providers = providers

    def search(self, query: str, item_name: str, limit: int) -> list[CandidateImage]:
        for provider in self.providers:
            try:
                results = provider.search(query, item_name, limit)
            except Exception:
                continue
            if results:
                return results
        return []


class MultiQuerySearchProvider:
    def __init__(self, provider: QuerySearchProvider, query_suffixes: tuple[str, ...], logger=None):
        self.provider = provider
        self.query_suffixes = query_suffixes
        self.logger = logger or logging.getLogger(__name__)

    def search(self, item_name: str, limit: int) -> list[CandidateImage]:
        results: list[CandidateImage] = []
        seen_urls: set[str] = set()

        for suffix in self.query_suffixes:
            if len(results) >= limit:
                break

            query = build_query(item_name, suffix)
            candidates = self.provider.search(query, item_name, limit)
            self.logger.info('item=%s query="%s" candidates=%s', item_name, query, len(candidates))

            for candidate in candidates:
                if candidate.source_url in seen_urls:
                    continue
                seen_urls.add(candidate.source_url)
                results.append(candidate)
                if len(results) >= limit:
                    break

        self.logger.info("item=%s unique_candidates=%s", item_name, len(results))
        return results
