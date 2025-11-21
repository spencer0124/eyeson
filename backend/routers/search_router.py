from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import traceback
from typing import List, Dict
from services.s3_service import list_images_in_s3, download_image_from_s3
from services.cnn_service import load_or_create_feature_vectors, preprocess_query
from services.faiss_service import load_or_create_faiss_index, search_faiss

router = APIRouter()

# Global variables for feature vectors and index
fv_pkl_path = './features/david_vgg16_features.pkl'
idx_path = './features/david_faiss_idx.index'

# Initialize feature vectors and index
file_list = list_images_in_s3()
fv = load_or_create_feature_vectors(fv_pkl_path, file_list, download_image_from_s3)
idx = load_or_create_faiss_index(idx_path, fv)

@router.post("/")
async def search_image(file: UploadFile = File(...)):
    query_dir = 'temp'
    query_path = os.path.join(query_dir, file.filename)

    try:
        if not os.path.exists(query_dir):
            os.makedirs(query_dir)

        with open(query_path, "wb") as buffer:
            buffer.write(await file.read())
        
        query_fv = preprocess_query(query_path)
        top_k = 3
        distance, indices = search_faiss(top_k, idx, query_fv)

        results = []
        for n, i in enumerate(indices[0]):
            top_n_id = file_list[i]
            results.append({
                'rank': n+1,
                'file': top_n_id,
            })
        return {"results": results}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")