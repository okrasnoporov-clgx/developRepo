import os
import sys
import boto3 #AWS SDK for Python


file_name = sys.argv[1]

bucket_name = os.environ["S3_BUCKET_NAME"]
folder = os.environ["S3_FOLDER"]

session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    aws_session_token=os.environ["AWS_SESSION_TOKEN"],
)

s3 = session.client("s3")

object_key = f"{folder}/{os.path.basename(file_name)}"

s3.upload_file(
    file_name,
    bucket_name,
    object_key
)

print(f"Uploaded: s3://{bucket_name}/{object_key}")

