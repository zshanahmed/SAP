"""
This file contains the code for uploading resources to azure and returning the resource url
"""

import os
import time
from azure.storage.blob import BlobServiceClient


def upload_file_to_azure(upload_file_name, called_by_test_function=False):
    """
    @param called_by_test_function: Set this to true when calling from unit test function
    @param upload_file_name: the file to upload must be present inside /tmp/
    @return: returns the url of the resource on the cloud
    """
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a unique name for the container
    container_name = "sepibacontainer"

    # File to upload
    local_file_name = upload_file_name
    # if a file of the same name is already on azure, the upload will fail
    # adding timestamp to filename to overcome the duplicate issue
    curr_timestamp = str(time.time()).split('.')[0]
    file_name_on_cloud = curr_timestamp + local_file_name
    upload_file_path = os.path.join('/tmp', local_file_name)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name_on_cloud)

    # Upload the created file
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data)

    # delete the file from server once uploaded to azure
    os.remove(upload_file_path)

    # if the test function calls the function, delete the blob on cloud. We don't want to have unwanted resources on cloud
    if called_by_test_function:
        blob_client.delete_blob()

    return "https://sepibafiles.blob.core.windows.net/sepibacontainer/" + upload_file_name
