from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# JSON 파일 경로
data_path = './data/data.json'

# Load data (image metadata)
def load_data():
    with open(data_path, "r") as f:
        json_data = json.load(f)
    return json_data

# 결과 항목을 정의하는 모델
class eng_id(BaseModel):
    rank: int
    file: str

# 전체 요청 본문을 정의하는 모델
class Engid_list(BaseModel):
    results: List[eng_id]

@app.post("/get-description/")
async def get_description(data: Engid_list):
    # 데이터 로드
    json_data = load_data()

    first = data.results[0].model_dump()
    first_file = first['file']

    matched = next((entry for entry in json_data if entry['eng_id'] == first_file), None)
    
    if matched:
        return {
            'eng_id': matched.get('eng_id', 'N/A'),
            'description': matched.get('description', 'N/A'),
            'explanation': matched.get('explanation', 'N/A'),
            'comment': matched.get('comment', 'N/A'),
            'meta': matched.get('meta', 'N/A')
        }
    else:
        raise HTTPException(status_code=404, detail="Matching entry not found")