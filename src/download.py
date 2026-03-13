from dataclasses import dataclass
from typing import Optional
from urllib.request import Request, urlopen


def is_image_response(response) -> bool:
    content_type = response.headers.get("Content-Type", "")
    return content_type.startswith("image/")


def download_bytes(
    url: str, session, timeout: int, retries: int
) -> Optional[bytes]:
    for _ in range(retries):
        try:
            response = session.get(url, timeout=timeout)
        except Exception:
            continue
        if response.ok and is_image_response(response):
            return response.content
    return None


@dataclass
class UrlopenResponse:
    headers: dict
    content: bytes
    ok: bool = True


class UrlopenSession:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    def get(self, url: str, timeout: int) -> UrlopenResponse:
        request = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=timeout) as response:
            headers = dict(response.info())
            content = response.read()
        return UrlopenResponse(headers=headers, content=content)
