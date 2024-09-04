import traceback
import os
import json
import base64
from openai import OpenAI
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from s3_module import list_images_in_s3, download_image_from_s3
from cnn_module import load_or_create_feature_vectors, preprocess_query
from faiss_module import load_or_create_faiss_index, search_faiss
from io import BytesIO
from PIL import Image

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
fv_pkl_path = './features/vgg16_features.pkl'
idx_path = './features/faiss_idx.index'
data_path = './data/data.json'

# Mount s3 files and Setting
file_list = list_images_in_s3()
fv = load_or_create_feature_vectors(fv_pkl_path, file_list, download_image_from_s3)
idx = load_or_create_faiss_index(idx_path, fv)
# print(file_list)

@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")

@app.post("/search/")
async def search_image(file: UploadFile = File(...)):
    query_dir = 'temp'
    query_path = os.path.join(query_dir, file.filename)
    # print('filename', file.filename)

    try:
        # 디렉토리 존재 여부 확인 후 생성
        if not os.path.exists(query_dir):
            os.makedirs(query_dir)
            print(f"Directory {query_dir} created.")

        # 파일 저장
        with open(query_path, "wb") as buffer:
            buffer.write(await file.read())
        print(f"File saved at: {query_path}")
        
        query_fv = preprocess_query(query_path)
        # print('queryfv', query_fv)

        top_k = 3
        distance, indices = search_faiss(top_k, idx, query_fv)
        # print("indices", indices)

        results = []
        for n, i in enumerate(indices[0]):
            top_n_id = file_list[i]
            # print('topn id', top_n_id)
            results.append({
                'rank': n+1,
                'file': top_n_id,
            })

        return {"results": results}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(traceback.format_exc())  # 예외 발생 위치와 스택 트레이스 출력
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

def load_data():
    with open(data_path, "r") as f:
        json_data = json.load(f)
    return json_data

class eng_id(BaseModel):
    file: str
    
@app.post("/get-description/")
async def get_description(data: eng_id):
    # 데이터 로드
    json_data = load_data()
    first_file = data.file
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

load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()
rule = '''확대된 예술 작품의 일부분을 저시력자(low-vision)인 시각장애인에게 설명해주려 한다.
    배경 지식이나 주관적인 해석을 최대한 배제하고, 작품의 소재와 형태를 위주로 묘사하라.
    묘사 시 참고해야 할 원칙은 다음과 같다.
    1. 설명의 순서 및 위치를 밝힌다. (예 : 작품의 좌상단에서부터 묘사하겠습니다.)
    2. 주요 소재를 묘사한다 (예: 6시 방향에 있는 흰색 천 같은 대상은 녹아내린 시계입니다.)
    3. 주요 소재의 형태를 자세히 묘사한다. (예 : 작품 6시 방향 내 시계의 형태)
    4. 작품의 색감을 자세히 묘사한다. (예: 작품의 전반적인 색감, 작품에서 두드러지는 색감 등)
    확대된 이미지만을 묘사하라. 간결성을 위해 모든 원칙을 사용하지 않을 수 있다. 개조식이 아닌, 미술관의 큐레이터가 설명하듯 묘사하라.'''

def generate_image_description(original_dtype, base64_image, crop_dtype, crop_base64_image):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "당신은 미술품을 객관적으로, 간결하게 묘사해주는 미술관 큐레이터입니다."},
              {"role": "user", "content": [
                  {"type": "text", "text" : "다음 작품은 확대되기 전 예술 작품의 이미지이다."},
                  {"type":"image_url", "image_url": {"url":f"data:image/{original_dtype};base64,{base64_image}"}},
                  {"type": "text", "text" : "다음은 확대된 예술 작품의 일부이다."},
                  {"type":"image_url", "image_url": {"url":f"data:image/{crop_dtype};base64,{crop_base64_image}"}},
                  {"type": "text", "text" : rule}
              ]}]
        )

        return response.choices[0].message.content
    except:
        raise HTTPException(status_code=response.status_code, detail="OpenAI API request failed")
    
@app.post("/gpt-plus-describe/")
async def describe_image(request: str = Form(...), # original path
                         crop_image: UploadFile = File(...)):
    
    # 이미지 불러오기
    print('request', request)
    original_image = download_image_from_s3(request)
    crop_image_data = await crop_image.read()

    # base64로 인코딩
    byte_original_image = image_to_bytes(original_image)
    base64_image = base64.b64encode(byte_original_image).decode('utf-8')
    crop_base64_image = base64.b64encode(crop_image_data).decode('utf-8')

    # 이미지 타입 확인
    original_dtype = dtype_is(request)
    crop_dtype = dtype_is(crop_image.filename)

    description = generate_image_description(original_dtype, base64_image, crop_dtype, crop_base64_image)
    return {"description": description}

def dtype_is(img_path):
    if img_path[-3:].lower() == 'jpg':
        dtype = 'jpeg'
    elif img_path[-3:].lower() == 'png':
        dtype = 'png'
    else:
        raise ValueError('Unsupported image format')
    return dtype

def image_to_bytes(image: Image) -> bytes:
    """PIL Image 객체를 바이트 데이터로 변환하는 함수"""
    byte_io = BytesIO()
    
    # 이미지를 원래 포맷(JPEG, PNG 등)으로 저장
    image.save(byte_io, format=image.format)
    
    # 바이트 데이터로 변환
    byte_data = byte_io.getvalue()
    return byte_data

def get_filename_from_path(s3_key):
    # 'photo/image.jpg'에서 'image.jpg'만 추출
    return os.path.basename(s3_key)

def get_image_metadata(file_list, data):
    metadata_list = []
    for file in file_list:
        matched_data = next((entry for entry in data if entry['eng_id'] == file), None)
        if matched_data:
            metadata_list.append({
                'file': file,
                'title': matched_data['meta'].get('title', 'N/A'),
                'artist': matched_data['meta'].get('artist', 'N/A')
            })
    return metadata_list

@app.get("/images-with-metadata/")
async def get_images_with_metadata():
    try:
        data = load_data()

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