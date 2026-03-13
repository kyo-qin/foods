from io import BytesIO

from PIL import Image

from src.config import IMAGE_SIZE, MIN_SOURCE_EDGE


class ImageTooSmallError(ValueError):
    pass


def normalize_image(raw_bytes: bytes) -> bytes:
    with Image.open(BytesIO(raw_bytes)) as image:
        image = image.convert("RGB")
        width, height = image.size
        if min(width, height) < MIN_SOURCE_EDGE:
            raise ImageTooSmallError("image is too small to normalize")

        crop_size = min(width, height)
        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        image = image.crop((left, top, left + crop_size, top + crop_size))
        image = image.resize(IMAGE_SIZE)

        output = BytesIO()
        image.save(output, format="JPEG", quality=90)
        return output.getvalue()
