import os
import pickle
import faiss
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import json
from cnn_module import create_fv, preprocess_query
from faiss_module import make_faiss_idx, search_faiss
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
img_folder_path = './data/'
fv_pkl_path = './features/vgg16_features.pkl'
idx_path = './features/faiss_idx.index'
data_path = './data/data.json'

# Load or create feature vectors
if os.path.isfile(fv_pkl_path):
    with open(fv_pkl_path, 'rb') as file:
        fv = pickle.load(file)
else:
    fv = create_fv(img_folder_path, fv_pkl_path)

# Load or create FAISS index
if os.path.isfile(idx_path):
    idx = faiss.read_index(idx_path)
else:
    idx = make_faiss_idx(fv, idx_path)

filetype = ['jpg','JPG','png','PNG']
file_list = sorted([i for i in os.listdir(img_folder_path) if (i[-3:] in filetype)])
print(file_list)

@app.get("/")
async def read_root():
    # Redirect to /static/index.html
    return RedirectResponse(url="/static/index.html")

# Search API
@app.post("/search/")
async def search_image(file: UploadFile = File(...)):
    query_path = f'./temp/{file.filename}'
    print('filename', file.filename)

    try:
        # Save the uploaded image to the temp folder
        with open(query_path, "wb") as buffer:
            buffer.write(await file.read())

        # Preprocess query image to get feature vector
        query_fv = preprocess_query(query_path)
        print('queryfv', query_fv)

        # Perform FAISS search
        top_k = 3
        distance, indices = search_faiss(top_k, idx, query_fv)
        print("indices", indices)

        # Retrieve top results
        results = []
        for n, i in enumerate(indices[0]):
            top_n_id = file_list[i]
            print('topn id', top_n_id)
            results.append({
                'rank': n+1,
                'file': top_n_id,
                })

        # Return results
        return {"results": results}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
    
############# api 구분 ############

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