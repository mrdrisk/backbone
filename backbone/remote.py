import os
import boto3
from dotenv import load_dotenv

load_dotenv()


def get_b2_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["B2_ENDPOINT_URL"],
        aws_access_key_id=os.environ["B2_KEY_ID"],
        aws_secret_access_key=os.environ["B2_APPLICATION_KEY"],
    )


def upload_file(local_path, bucket_name=None):
    bucket_name = bucket_name or os.environ["B2_BUCKET_NAME"]
    client = get_b2_client()
    key_name = os.path.basename(local_path)

    client.upload_file(local_path, bucket_name, key_name)
    return f"s3://{bucket_name}/{key_name}"


def download_file(remote_key, local_path, bucket_name=None):
    bucket_name = bucket_name or os.environ["B2_BUCKET_NAME"]
    client = get_b2_client()

    client.download_file(bucket_name, remote_key, local_path)
    return local_path
