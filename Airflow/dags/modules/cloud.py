import os
import json
import logging
from dotenv import load_dotenv

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.hooks.sqs import SqsHook

load_dotenv()
AWS_CONN_ID = os.getenv("AWS_CONN_ID")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
queueUrl = os.getenv("QUEUE_URL")

logging.basicConfig(level=logging.INFO)


def upload_to_s3(filename: str, data_to_upload: json):
    try:
        conn = S3Hook(aws_conn_id=AWS_CONN_ID)
        s3_client = conn.get_conn()
        response = s3_client.put_object(
                            Body=data_to_upload,
                            Bucket=AWS_BUCKET_NAME,
                            Key=filename,
                            ContentType="application/json")
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logging.info(f"uploaded successfully. filename: {filename}")
        else:
            error_message = f"Upload failed. Filename: {filename}, HTTPStatusCode: {response['ResponseMetadata']['HTTPStatusCode']}"
            raise Exception(error_message)
    
    except Exception as e:
        logging.error(f"upload failed. filename: {filename}, error: {e}")

def download_from_s3(filename: str) -> json:
    try:
        conn = S3Hook(aws_conn_id=AWS_CONN_ID)
        s3_client = conn.get_conn()
        response = s3_client.get_object(
                            Bucket=AWS_BUCKET_NAME,
                            Key=filename)
        object_content = response['Body'].read()                                
        return json.loads(object_content)
    except Exception as e:
        logging.error(f"download failed. error: {e}")

def get_sqs_message_num(**kwargs):
    conn = SqsHook(aws_conn_id=AWS_CONN_ID, region_name="ap-southeast-2")
    sqs_hook_client = conn.get_conn()
    response = sqs_hook_client.get_queue_attributes(
                QueueUrl=queueUrl,
                AttributeNames=['ApproximateNumberOfMessages']
                )
    approximate_number_of_messages = int(response['Attributes']['ApproximateNumberOfMessages'])
    return approximate_number_of_messages