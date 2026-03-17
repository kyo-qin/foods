import importlib

import src.config
from src.config import IMAGE_SIZE


def test_default_image_size_is_square():
    assert IMAGE_SIZE == (800, 800)


def test_api_keys_default_to_empty(monkeypatch):
    monkeypatch.delenv("PIXABAY_API_KEY", raising=False)
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    importlib.reload(src.config)
    assert src.config.PIXABAY_API_KEY == ""
    assert src.config.PEXELS_API_KEY == ""
