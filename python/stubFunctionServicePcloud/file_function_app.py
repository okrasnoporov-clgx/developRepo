import logging
import os

import azure.functions as func
from azure.storage.blob import BlobServiceClient

from file_processor import create_stat_line


app = func.FunctionApp()


@app.blob_trigger(
    arg_name="input_blob",
    path="input/{name}.txt",
    connection="AzureWebJobsStorage"
)
def process_file(input_blob: func.InputStream):
    
    filename = input_blob.name.split("/")[-1]
    content = input_blob.read().decode("utf-8")

    logging.info("Processing file: %s", filename)

    # Shared
    result = create_stat_line(filename, content)
    logging.info("Result: %s", result)

    # Azure-specific
    # ----------------------------------------
    connection_string = os.environ["AzureWebJobsStorage"]
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )

    container_client = blob_service_client.get_container_client("input")
    stat_blob = container_client.get_blob_client("stat.file")

    try:
        existing_content = (
            stat_blob
            .download_blob()
            .readall()
            .decode("utf-8")
        )
    except Exception:
        existing_content = ""

    updated_content = existing_content + result

    stat_blob.upload_blob(
        updated_content,
        overwrite=True
    )

    logging.info("stat.file updated successfully")