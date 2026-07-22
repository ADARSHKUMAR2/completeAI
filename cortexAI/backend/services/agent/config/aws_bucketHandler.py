# config/aws_bucketHandler.py
import os
import boto3
from dotenv import load_dotenv
from botocore.config import Config

load_dotenv()

# Force Signature Version 4 and Virtual Host Addressing
s3_config = Config(
    region_name=os.getenv("AWS_REGION", "ap-south-1"),
    signature_version="s3v4",
    s3={"addressing_style": "virtual"}
)

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION", "ap-south-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    config=s3_config
)