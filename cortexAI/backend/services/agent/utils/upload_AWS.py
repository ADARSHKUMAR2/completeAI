import os
from config.aws_bucketHandler import s3
from dotenv import load_dotenv  

load_dotenv()

def upload_to_s3(filename, buffer, content_type):  
    s3.put_object(
        Bucket=os.getenv("AWS_BUCKET_NAME"),
        Body=buffer,
        Key=filename,
        ContentType=content_type
    )
    return filename