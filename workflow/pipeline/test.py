from urllib.request import urlretrieve
from werkzeug.utils import secure_filename
from minio import Minio
import os

def upload_file(path):
    source_file = path
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if source_file == "":
        return "file not found"
    if source_file:
        destination_file = secure_filename(source_file)
        size = os.stat(path).st_size
        msg = upload_object(destination_file, source_file, size)
        return msg
    
def upload_object(destination_file, source_file, size):
    # with open(source_file) as f: data = f.read()
    bucket_name = BUCKET_NAME
    # class Dataset:
    #     def __init__(self, data=None):
    #         # Initialize the data attribute with the provided data or an empty list by default
    #         self.data = data if data is not None else []
    # dataset = Dataset(data=data)
    client = Minio(MINIO_ENDPOINT, MINIO_USER, MINIO_PASS, secure=False)
    # Make bucket if not exist.
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")
    # client.put_object(bucket_name, destination_file, source_file, size)
    client.fput_object(bucket_name, destination_file, source_file, size)
    return f"{destination_file} is successfully uploaded to bucket {bucket_name}."

url = "https://raw.githubusercontent.com/razaulmustafa852/youtubegoes5g/main/Models/Stall-Windows%20-%20Stall-3s.csv"
filename = "init_dataset.csv"

# download file
path, headers = urlretrieve(url, filename)
# minio credentials
MINIO_USER = "minioadmin"
MINIO_PASS = "minioadmin"
BUCKET_NAME = "flask-minio"
MINIO_ENDPOINT = "minio-svc.minio:9000"
msg = upload_file(path)