import boto3
from io import BytesIO
from PIL import Image
from fastapi import HTTPException

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

def download_image_from_s3(s3_key):
    try:
        # 1. S3에서 객체 가져오기 시도
        print(f"Attempting to download image with key: {s3_key}")
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        print(f"Successfully retrieved object from S3: {s3_key}")

        # 2. 이미지 데이터 읽기
        img_data = response['Body'].read()
        print(f"Image data read from S3, size: {len(img_data)} bytes")

        # 3. 이미지 데이터로부터 이미지 객체 생성 시도
        try:
            image = Image.open(BytesIO(img_data))
            print(f"Image successfully opened: {s3_key}")
            return image
        except Exception as image_open_error:
            print(f"Error opening image: {str(image_open_error)}")
            raise HTTPException(status_code=500, detail=f"Failed to open image from S3: {str(image_open_error)}")

    except s3_client.exceptions.NoSuchKey as no_key_error:
        print(f"No such key: {s3_key} in bucket: {bucket_name}")
        raise HTTPException(status_code=404, detail=f"No such key: {s3_key} in S3 bucket")
    
    except Exception as e:
        print(f"Error downloading image from S3: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while downloading image from S3: {str(e)}")