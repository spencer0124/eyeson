import boto3
from io import BytesIO
from PIL import Image
from fastapi import HTTPException

# AWS S3 설정
s3_client = boto3.client('s3')
bucket_name = 'seeterature'

def list_images_in_s3(prefix=''):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = [content['Key'] for content in response.get('Contents', []) if content['Key'].lower().endswith(('jpg', 'jpeg', 'png'))]
        return files
    except Exception as e:
        print(f"Error listing images in S3: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list images in S3")

def download_image_from_s3(s3_key):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        img_data = response['Body'].read()
        image = Image.open(BytesIO(img_data))
        return image
    except Exception as e:
        print(f"Error downloading image from S3: {str(e)}")
        raise HTTPException(status_code=404, detail="Image not found in S3")