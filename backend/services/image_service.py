from io import BytesIO
from PIL import Image

def dtype_is(img_path: str) -> str:
    if img_path[-3:].lower() == 'jpg':
        return 'jpeg'
    elif img_path[-3:].lower() == 'png':
        return 'png'
    else:
        raise ValueError('Unsupported image format')

def image_to_bytes(image: Image) -> bytes:
    byte_io = BytesIO()
    image.save(byte_io, format=image.format)
    return byte_io.getvalue()