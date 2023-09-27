from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import os
from dotenv import load_dotenv
import json

load_dotenv()
AWS_CONN_ID = os.getenv("AWS_CONN_ID")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

def upload_to_s3(filename, data_to_upload):
    conn = S3Hook(aws_conn_id=AWS_CONN_ID)
    s3_client = conn.get_conn()
    response = s3_client.put_object(
                        Body=data_to_upload,
                        Bucket=AWS_BUCKET_NAME,
                        Key=filename,
                        ContentType="application/json")
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f"uploaded successfully. filename: {filename}")
    else:
        print(f"upload failed. filename: {filename}")

def download_from_s3(filename):
    conn = S3Hook(aws_conn_id=AWS_CONN_ID)
    s3_client = conn.get_conn()
    response = s3_client.get_object(
                        Bucket=AWS_BUCKET_NAME,
                        Key=filename)
    object_content = response['Body'].read()                                
    return json.loads(object_content)
