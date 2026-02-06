import os
from typing import Optional

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from dotenv import load_dotenv
load_dotenv()


def create_s3_client(
    *,
    endpoint_url: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    region_name: str = 'us-east-1',
) -> BaseClient:
    """Create a universal S3 client for AWS S3 and MinIO.
    Args:
        endpoint_url (Optional[str]):
            Custom S3 endpoint URL (required for MinIO).
        access_key (Optional[str]):
            Access key ID (explicit for MinIO, optional for AWS).
        secret_key (Optional[str]):
            Secret access key (explicit for MinIO, optional for AWS).
        region_name (str): AWS region name (kept for compatibility)."""
    resolved_access_key = access_key or os.getenv('AWS_ACCESS_KEY_ID')
    resolved_secret_key = secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')

    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=resolved_access_key,
        aws_secret_access_key=resolved_secret_key,
        region_name=region_name,
    )


def ensure_bucket_exists(
    s3_client: BaseClient,
    *,
    bucket: str,
) -> dict[str, str]:
    """Ensure that the bucket exists, create it if missing.
    Args:
        s3_client (BaseClient): Boto3 S3 client instance.
        bucket (str): Bucket name to check/create."""
    try:
        s3_client.head_bucket(Bucket=bucket)
        return {'bucket': bucket, 'status': 'exists'}
    except ClientError as exc:
        error_code = str(exc.response.get('Error', {}).get('Code', ''))

        if error_code in {'404', 'NoSuchBucket', 'NotFound'}:
            try:
                s3_client.create_bucket(Bucket=bucket)
            except ClientError as create_exc:
                raise RuntimeError(
                    f'Failed to create bucket: {create_exc}'
                ) from create_exc
            return {'bucket': bucket, 'status': 'created'}

        raise RuntimeError(f'Failed to check bucket: {exc}') from exc


def upload_file(
    s3_client: BaseClient,
    *,
    file_path: str,
    bucket: str,
    object_name: Optional[str] = None,
) -> dict[str, str]:
    """Upload a local file to S3-compatible storage.
    Args:
        s3_client (BaseClient): Boto3 S3 client instance.
        file_path (str): Path to a local file to upload.
        bucket (str): Target bucket name.
        object_name (Optional[str]): Target object key in the bucket."""
    key_name = object_name or os.path.basename(file_path)

    try:
        s3_client.upload_file(file_path, bucket, key_name)
    except ClientError as exc:
        raise RuntimeError(f'Failed to upload file: {exc}') from exc

    return {'bucket': bucket, 'key': key_name}


def generate_presigned_get_url(
    s3_client: BaseClient,
    *,
    bucket: str,
    object_name: str,
    expiration_seconds: int = 3600,
) -> str:
    """Generate a presigned URL for downloading an object.
    Args:
        s3_client (BaseClient): Boto3 S3 client instance.
        bucket (str): Bucket name.
        object_name (str): Object key in the bucket.
        expiration_seconds (int): URL expiration time in seconds."""
    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': object_name},
            ExpiresIn=expiration_seconds,
        )
    except ClientError as exc:
        raise RuntimeError(f'Failed to generate presigned URL: {exc}') from exc

    return presigned_url


def build_env_client_params() -> dict[str, Optional[str]]:
    """Build S3 client parameters from environment variables.
    Args:
        None: No arguments."""
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    region_name = os.getenv('S3_REGION', 'us-east-1')

    return {
        'endpoint_url': endpoint_url,
        'access_key': access_key,
        'secret_key': secret_key,
        'region_name': region_name,
    }


def create_example_file(file_name: str = 'example.txt') -> str:
    """Create example file in script directory.
    Args:
        file_name (str): Name of the file to create."""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('This is an example file')

    return file_path


if __name__ == '__main__':
    created_file_path = create_example_file()

    client_params = build_env_client_params()
    s3 = create_s3_client(**client_params)

    bucket_name = 'my-bucket'
    bucket_result = ensure_bucket_exists(
        s3_client=s3,
        bucket=bucket_name,
    )
    print(bucket_result)

    upload_result = upload_file(
        s3_client=s3,
        file_path=created_file_path,
        bucket=bucket_name,
        object_name=os.path.basename(created_file_path),
    )

    # download_url = generate_presigned_get_url(
    #     s3_client=s3,
    #     bucket=upload_result['bucket'],
    #     object_name=upload_result['key'],
    #     expiration_seconds=3600,
    # )

    # print(download_url)
