from fastapi import APIRouter, HTTPException, Query
import os
import json
from services.s3_service import list_images_in_s3

router = APIRouter()
data_path = './data/data_david.json' # Edit: 251121 for CHI 2026
exhibit_path = './data/exhibit_david.json' # Edit: 251121 for CHI 2026

# parameter로 path 받아 data_path와 exhibit_path 모두 다루도록 수정정
def load_data(path):
    with open(path, "r") as f:
        return json.load(f)

def get_filename_from_path(s3_key: str) -> str:
    return os.path.basename(s3_key)

@router.get("/with-images/")
async def get_images_with_metadata(uniqueid: str = Query(...)):
    try:
        # load_data 인수로 data_path 받게 수정정
        data = load_data(data_path)
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
    
@router.get("/exhibit-info/")
async def get_exhibit_with_metadata():
    try:
        exhibits = load_data(exhibit_path)
        return {"exhibits" : exhibits}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve exhibitions and metadata")