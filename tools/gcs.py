import os
from google.cloud import storage
from datetime import datetime
def upload_image_to_gcs(image_bytes: bytes, blob_name: str | None = None, bucket_name: str = os.getenv("GCS_BUCKET")) -> str:
    """
    Uploads an image represented by bytes to Google Cloud Storage.

    Args:
        image_bytes (bytes): The image data in bytes.
        bucket_name (str): The name of the GCS bucket.
        blob_name (str): The name of the blob in the bucket.

    Returns:
        str: The public URL of the uploaded image.
    """
    if not blob_name:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        blob_name = f"receipts/receipt_{timestamp}.jpeg"
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = storage.Blob(blob_name, bucket)
    blob.upload_from_string(image_bytes, content_type='image/jpeg')
    return blob.name