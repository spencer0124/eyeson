from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import json
import base64
from typing import Dict, Any, List
from services.s3_service import download_image_from_s3
from services.image_service import image_to_bytes, dtype_is
from services.openai_service import generate_image_description

router = APIRouter()
data_path = './data/data.json'

class EngId(BaseModel):
    file: str

def load_data() -> List[Dict[str, Any]]:
    with open(data_path, "r") as f:
        return json.load(f)

@router.post("/getOrigin/")
async def get_description(data: EngId):
    json_data = load_data()
    first_file = data.file
    if first_file[-4].isdigit():
        first_file = first_file[:-5] + '1' + first_file[-4:]
    s3_url = f"https://seeterature.s3.amazonaws.com/photo/{first_file}"

    try:
        matched = next(entry for entry in json_data if entry['eng_id'] == first_file)
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"No matching entry found for eng_id: {first_file}")

    return {
        'eng_id': matched.get('eng_id', 'N/A'),
        'description': matched.get('description', 'N/A'),
        'explanation': matched.get('explanation', 'N/A'),
        'comment': matched.get('comment', 'N/A'),
        'meta': matched.get('meta', 'N/A'),
        'image_url': s3_url
    }

@router.post("/gptPlus/")
async def describe_image(request: str = Form(...), crop_image: UploadFile = File(...)):
    try:
        original_image = download_image_from_s3(request)
        crop_image_data = await crop_image.read()

        byte_original_image = image_to_bytes(original_image)
        base64_image = base64.b64encode(byte_original_image).decode('utf-8')
        crop_base64_image = base64.b64encode(crop_image_data).decode('utf-8')

        original_dtype = dtype_is(request)
        crop_dtype = dtype_is(crop_image.filename)

        description = generate_image_description(original_dtype, base64_image, crop_dtype, crop_base64_image)
        return {"description": description}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))