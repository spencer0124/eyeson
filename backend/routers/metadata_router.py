from fastapi import APIRouter, HTTPException
import os
import json
from services.s3_service import list_images_in_s3

router = APIRouter()
data_path = './data/data.json'

def load_data():
    with open(data_path, "r") as f:
        return json.load(f)

def get_filename_from_path(s3_key: str) -> str:
    return os.path.basename(s3_key)

@router.get("/images-with-metadata/")
async def get_images_with_metadata():
    try:
        data = load_data()
        file_list = list_images_in_s3()

        images_with_metadata = []
        for s3_key in file_list:
            filename = get_filename_from_path(s3_key)
            matched_data = next((entry for entry in data if entry['eng_id'] == filename), None)
            
            if matched_data:
                s3_url = f"https://seeterature.s3.amazonaws.com/{s3_key}"
                images_with_metadata.append({
                    'file': filename,
                    'title': matched_data['meta'].get('title', 'N/A'),
                    'artist': matched_data['meta'].get('artist', 'N/A'),
                    'image_url': s3_url
                })
        return {"images": images_with_metadata}
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve images and metadata")