# utils/getFrom_AWS.py
import os
from config.aws_bucketHandler import s3

def get_from_s3(filename: str, expires_in: int = 3600): # 👈 Reduced from 86400 to 3600
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": os.getenv("AWS_BUCKET_NAME"),
            "Key": filename,
        },
        ExpiresIn=expires_in
    )
    return url