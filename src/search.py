import json
import re
from typing import Optional, Protocol
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from src.models import CandidateImage

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def build_query(dish_name: str) -> str:
    return f"{dish_name} 中餐 菜品图 实拍"


class SearchProvider(Protocol):
    def search(self, dish_name: str, limit: int) -> list[CandidateImage]:
        ...


class SearchProviderError(RuntimeError):
    pass


class FallbackSearchProvider:
    def __init__(self, providers):
        self.providers = providers

    def search(self, dish_name: str, limit: int) -> list[CandidateImage]:
        for provider in self.providers:
            try:
                results = provider.search(dish_name, limit)
            except Exception:
                continue
            if results:
                return results
        return []


class DuckDuckGoImageSearchProvider:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def search(self, dish_name: str, limit: int) -> list[CandidateImage]:
        query = build_query(dish_name)
        vqd = self._fetch_vqd(query)
        if not vqd:
            return []

        payload = self._fetch_results(query, vqd)
        results: list[CandidateImage] = []
        for item in payload.get("results", []):
            image_url = item.get("image")
            if not image_url:
                continue
            results.append(CandidateImage(dish_name=dish_name, source_url=image_url))
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

    def search(self, dish_name: str, limit: int) -> list[CandidateImage]:
        query = f"{dish_name} food"
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
            results.append(CandidateImage(dish_name=dish_name, source_url=image_url))
            if len(results) >= limit:
                break
        return results
