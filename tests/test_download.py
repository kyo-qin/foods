from unittest.mock import Mock

from src.download import is_image_response


def test_is_image_response_accepts_image_content_type():
    response = Mock(headers={"Content-Type": "image/jpeg"})
    assert is_image_response(response) is True


def test_is_image_response_rejects_html():
    response = Mock(headers={"Content-Type": "text/html"})
    assert is_image_response(response) is False
