import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.configs.environment import EnvKey


class S3Client:
    def __init__(self, environment: dict):
        self._environment = environment
        self._client = None
        self._connect()

    def _connect(self):
        self._client = boto3.client(
            "s3",
            aws_access_key_id=self._environment[EnvKey.WIKI_S3_ACCESS_KEY],
            aws_secret_access_key=self._environment[EnvKey.WIKI_S3_SECRET_KEY],
            endpoint_url=self._environment[EnvKey.WIKI_S3_URL],
            region_name=self._environment[EnvKey.WIKI_S3_REGION],
        )

    async def upload_file(self, file: bytes, file_name: str, file_type: str):
        try:
            self._client.put_object(
                Bucket=self._environment[EnvKey.WIKI_S3_BUCKET_NAME],
                Key=file_name,
                Body=file,
                ContentType=file_type,
            )
            file_url = (
                f"{self._environment[EnvKey.WIKI_S3_URL]}/"
                f"{self._environment[EnvKey.WIKI_S3_BUCKET_NAME]}/"
                f"{file_name}"
            )
            return file_url
        except ClientError as e:
            raise e

    async def file_exists(self, file_name: str) -> bool:
        try:
            await self._client.head_object(
                Bucket=self._environment[EnvKey.WIKI_S3_BUCKET_NAME],
                Key=file_name,
            )
            return True
        except self._client.exceptions.ClientError:
            return False
        except NoCredentialsError as e:
            raise e

    async def get_file_download_uri(self, file_name: str):
        try:
            file = self._client.get_object(
                Bucket=self._environment[EnvKey.WIKI_S3_BUCKET_NAME],
                Key=file_name,
            )
            file_content = file["Body"].read()
            return file_content

        except ClientError as e:
            raise e

    async def delete_file(self, file_name: str) -> bool:
        try:
            self._client.head_object(
                Bucket=self._environment[EnvKey.WIKI_S3_BUCKET_NAME],
                Key=file_name,
            )
            self._client.delete_object(
                Bucket=self._environment[EnvKey.WIKI_S3_BUCKET_NAME],
                Key=file_name,
            )
            return True

        except ClientError as e:
            raise e
