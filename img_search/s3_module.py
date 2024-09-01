import boto3

s3_client = boto3.client('s3')
bucket_name = 'seeterature'

try:
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    print(response)
except Exception as e:
    print(f"Error: {str(e)}")