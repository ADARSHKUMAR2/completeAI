# test_upload.py
import os
from config.aws_bucketHandler import s3

try:
    print("Uploading test object to AWS S3...")
    s3.put_object(
        Bucket=os.getenv("AWS_BUCKET_NAME"),
        Body=b"test image buffer",
        Key="test_check.png",
        ContentType="image/png"
    )
    print("✅ S3 PutObject Succeeded! Credentials and Region are 100% valid.")
except Exception as e:
    print("❌ S3 Upload Failed:", e)