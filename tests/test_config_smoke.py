from src.config import IMAGE_SIZE


def test_default_image_size_is_square():
    assert IMAGE_SIZE == (800, 800)
