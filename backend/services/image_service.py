from io import BytesIO
from PIL import Image
import json

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

def load_data(path):
    with open(path, "r") as f:
        return json.load(f)

def load_id_from_title(title: str):
    data_path = '../data/data.json'
    json_data = load_data(data_path)

    for item in json_data:
        if item['meta']['title'] == title:
            return item['eng_id']
    raise ValueError(f"Title '{title}' not found in JSON data.")