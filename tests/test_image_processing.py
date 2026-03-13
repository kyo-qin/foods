from io import BytesIO

import pytest
from PIL import Image

from src.image_processing import ImageTooSmallError, normalize_image


def make_image_bytes(size=(1200, 900), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_normalize_image_returns_800_square():
    result = normalize_image(make_image_bytes())
    image = Image.open(BytesIO(result))
    assert image.size == (800, 800)
    assert image.format == "JPEG"


def test_normalize_image_rejects_small_images():
    with pytest.raises(ImageTooSmallError):
        normalize_image(make_image_bytes(size=(200, 200)))
