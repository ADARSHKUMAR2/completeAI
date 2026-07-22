import os
from config.aws_bucketHandler import s3
from dotenv import load_dotenv  

load_dotenv()

def get_from_s3(filename, expires_in=600):  # 👈 Remove 'async'
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": os.getenv("AWS_BUCKET_NAME"),
            "Key": filename,
        },
        ExpiresIn=expires_in
    )
    return url