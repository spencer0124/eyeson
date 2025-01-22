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
    data_path = './data/data.json'
    json_data = load_data(data_path)

    for item in json_data.get("meta", []):  # 'meta' 리스트 탐색
        if item.get("title") == title:
            return json_data.get("eng_id")  # 해당 제목의 eng_id 반환
    raise ValueError(f"Title '{title}' not found in JSON data.")