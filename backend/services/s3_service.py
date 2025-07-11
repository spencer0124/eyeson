import boto3
from io import BytesIO
from PIL import Image
from fastapi import HTTPException
import json

# AWS S3 설정
s3_client = boto3.client('s3')
bucket_name = 'seeterature'
prefix = 'photo/'

def list_images_in_s3():
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = [content['Key'] for content in response.get('Contents', []) if content['Key'].lower().endswith(('jpg', 'jpeg', 'png'))]
        return files
    except Exception as e:
        print(f"Error listing images in S3: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list images in S3")

def load_data(path):
    with open(path, "r") as f:
        return json.load(f)

def load_id_from_title(title: str):
    data_path = './data/data_david.json'
    json_data = load_data(data_path)
    tmp_title = title[6:]
    print('tmp',tmp_title)

    for item in json_data:
        if item['eng_id'] == tmp_title:
            return item['eng_id']
    raise ValueError(f"EngId '{tmp_title}' not found in JSON data.")

def download_image_from_s3_gpt(s3_key):
    print('s3', s3_key)
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        print('resp', response)
        img_data = response['Body'].read()
        image = Image.open(BytesIO(img_data))
        return image
    except Exception as e:
        print(f"Error downloading image from S3: {str(e)}")
        raise HTTPException(status_code=404, detail="Image not found in S3")
    
def download_image_from_s3(title):
    print('title',title)
    eng_id = load_id_from_title(title)
    s3_key = 'photo/'+eng_id
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        img_data = response['Body'].read()
        image = Image.open(BytesIO(img_data))
        return image
    except Exception as e:
        print(f"Error downloading image from S3: {str(e)}")
        raise HTTPException(status_code=404, detail="Image not found in S3")