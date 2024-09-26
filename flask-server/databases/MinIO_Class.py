import os, json
from minio import Minio
from datetime import timedelta

class MinIO_Class:
    MINIO_HOST = os.getenv("MINIO_HOST", "localhost")
    MINIO_PORT = int(os.getenv("MINIO_PORT", 9000))
    MINIO_SERVER_PORT = int(os.getenv("MINIO_SERVER_PORT", 9001))
    MINIO_USER = os.getenv("MINIO_USER", "admin12345")
    MINIO_PASS = os.getenv("MINIO_PASS", "admin12345")

    def __init__(self):
        minio_host = MinIO_Class.MINIO_HOST+":"+str(MinIO_Class.MINIO_PORT)
        self.minio_client = Minio(
            minio_host,
            access_key=MinIO_Class.MINIO_USER,
            secret_key=MinIO_Class.MINIO_PASS,
            secure=False
        )
        return
    
    def upload_dataset_object(filename, file, size, user, label):
        minio_host = MinIO_Class.MINIO_HOST+":"+str(MinIO_Class.MINIO_PORT)
        client = Minio(
            minio_host,
            access_key=MinIO_Class.MINIO_USER,
            secret_key=MinIO_Class.MINIO_PASS,
            secure=False
        )

        BUCKET_NAME = user

        # Make bucket if not exist.
        found = client.bucket_exists(BUCKET_NAME)
        if not found:
            client.make_bucket(BUCKET_NAME)
        else:
            print(f"Bucket {BUCKET_NAME} already exists")

        # Define the policy for public read access
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
                }
            ]
        }

        # Set the bucket policy
        client.set_bucket_policy(BUCKET_NAME, json.dumps(policy))
        print(f"Public read access set for bucket {BUCKET_NAME}")

        client.put_object(BUCKET_NAME, "datasets/" + label + "/" + filename, file, size)
        print(f"{"datasets/" + label + "/" + filename} is successfully uploaded to bucket {BUCKET_NAME}.")

        """
        url = client.get_presigned_url(
            "GET",
            BUCKET_NAME,
            "datasets/" + label + "/" + filename,
            expires=timedelta(hours=1)  # Expiration time for the URL
        )
        """
        # print(f"URL to download {filename}: {url}")
        # url = url.replace(MinIO_Class.MINIO_HOST+":"+str(MinIO_Class.MINIO_PORT), "localhost:"+str(MinIO_Class.MINIO_SERVER_PORT))
        url = "http://localhost:"+str(MinIO_Class.MINIO_PORT)+"/"+BUCKET_NAME+"/datasets/" + label + "/" + filename
        print(f"URL to download {filename}: {url}")

        return url
    
    def delete_dataset_object(filename, user, label):
        minio_host = MinIO_Class.MINIO_HOST+":"+str(MinIO_Class.MINIO_PORT)
        client = Minio(
            minio_host,
            access_key=MinIO_Class.MINIO_USER,
            secret_key=MinIO_Class.MINIO_PASS,
            secure=False
        )

        BUCKET_NAME = user

        client.remove_object(BUCKET_NAME, "datasets/" + label + "/" + filename)
        print(f"{"datasets/" + label + "/" + filename} is successfully deleted from bucket {BUCKET_NAME}.")

        return
    
    def delete_clustering_result_object(filename, user, label):
        minio_host = MinIO_Class.MINIO_HOST+":"+str(MinIO_Class.MINIO_PORT)
        client = Minio(
            minio_host,
            access_key=MinIO_Class.MINIO_USER,
            secret_key=MinIO_Class.MINIO_PASS,
            secure=False
        )

        BUCKET_NAME = user

        client.remove_object(BUCKET_NAME, "results/" + label + "/" + filename)
        print(f"{"results/" + label + "/" + filename} is successfully deleted from bucket {BUCKET_NAME}.")

        return