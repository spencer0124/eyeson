from fastapi import Request, APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import json
import base64
import time
from typing import Dict, Any, List
from services.s3_service import download_image_from_s3_gpt
from services.image_service import image_to_bytes, dtype_is
from services.openai_service import *

router = APIRouter()
data_path = './data/data_david.json' # Edit: 251121 for CHI 2026

class EngId(BaseModel):
    file: str

def load_data() -> List[Dict[str, Any]]:
    with open(data_path, "r") as f:
        return json.load(f)

@router.post("/get-origin/")
async def get_description(data: EngId):
    json_data = load_data()
    first_file = data.file
    if first_file[-4].isdigit():
        first_file = first_file[:-5] + '1' + first_file[-4:]
    s3_url = f"https://seeterature.s3.amazonaws.com/photo/david/{first_file}" # Edit: 251121 for CHI 2026

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

@router.post("/gpt-artwork/")
async def describe_image_with_artwork(promptmode: Request, request: str = Form(...), crop_image: UploadFile = File(...)):
    try:        
        original_image_data = download_image_from_s3_gpt(request)
        crop_image_data = await crop_image.read()

        byte_original_image = image_to_bytes(original_image_data)
        base64_image = base64.b64encode(byte_original_image).decode('utf-8')
        crop_base64_image = base64.b64encode(crop_image_data).decode('utf-8')

        original_dtype = dtype_is(request)
        crop_dtype = dtype_is(crop_image.filename)

        prompt_mode = promptmode.query_params.get("promptmode", "promptmode1")
        description = generate_image_description(prompt_mode, original_dtype, base64_image, crop_dtype, crop_base64_image)
        return {"description": description}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/gpt-nonartwork/")
async def describe_image_without_artwork(request: Request, original_image: UploadFile = File(...), crop_image: UploadFile = File(...)):
    try:
        original_image_data = await original_image.read()
        crop_image_data = await crop_image.read()

        original_base64_image = base64.b64encode(original_image_data).decode('utf-8')
        crop_base64_image = base64.b64encode(crop_image_data).decode('utf-8')

        original_dtype = dtype_is(original_image.filename)
        crop_dtype = dtype_is(crop_image.filename)

        print('original',original_dtype,'crop',crop_dtype)
        
        prompt_mode = request.query_params.get("promptmode", "promptmode1")
        description = generate_image_description(prompt_mode, original_dtype, original_base64_image, crop_dtype, crop_base64_image)
        return {"description": description}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/gpt-nonartwork-prompt/")
async def describe_image_with_user_prompt(request: Request, original_image: UploadFile = File(...), crop_image: UploadFile = File(...), user_prompt: str = Form(...)):
    try:
        print('user prompt on post', user_prompt)
        original_image_data = await original_image.read()
        crop_image_data = await crop_image.read()

        original_base64_image = base64.b64encode(original_image_data).decode('utf-8')
        crop_base64_image = base64.b64encode(crop_image_data).decode('utf-8')

        original_dtype = dtype_is(original_image.filename)
        crop_dtype = dtype_is(crop_image.filename)
        
        prompt_mode = request.query_params.get("promptmode", "promptmode1")
        description = answer_user_prompt(prompt_mode, original_dtype, original_base64_image, crop_dtype, crop_base64_image, user_prompt)
        return {"description": description}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))