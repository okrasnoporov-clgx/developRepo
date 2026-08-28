import os
import sys
import boto3


file_name = sys.argv[1]

bucket_name = os.environ["S3_BUCKET_NAME"]
folder = os.environ["S3_FOLDER"]

s3 = boto3.client("s3")

object_key = f"{folder}/{os.path.basename(file_name)}"

s3.upload_file(
    file_name,
    bucket_name,
    object_key
)

print(f"Uploaded: s3://{bucket_name}/{object_key}")

