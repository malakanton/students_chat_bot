import os
import boto3
from loguru import logger
from botocore.exceptions import ClientError

from config import S3_ENDPOINT, S3_KEY_ID, S3_SECRET, S3_BUCKET


class S3Client:
    __endpoint: str
    __key_id: str
    __secret: str
    __bucket: str

    def __init__(self):
        self.__endpoint = S3_ENDPOINT
        self.__bucket = S3_BUCKET
        self.__secret = S3_SECRET
        self.__key_id = S3_KEY_ID
        self.client = boto3.client(
            's3',
            endpoint_url=self.__endpoint,
            aws_access_key_id=self.__key_id,
            aws_secret_access_key=self.__secret,
        )

    def upload_file(self, file_name: str, object_name: str = None) -> bool:
        """Uploads file to a s3 default bucket
        :param file_name: str name of the file to upload
        :param object_name: str name of the file in s3 bucket,
        by default its an original file name
        """
        if object_name is None:
            object_name = os.path.basename(file_name)
        try:
            self.client.upload_file(
                file_name,
                self.__bucket,
                object_name
            )
            logger.success(f'Successfully uploaded file {file_name} to s3')
        except ClientError as e:
            logger.error(e)
            return False
        return True

    def download_file(self, object_name: str, file_name: str = None) -> bool:
        if file_name is None:
            file_name = object_name
        try:
            self.client.download_file(self.__bucket, object_name, file_name)
            logger.success(f'Successfully downloaded file {object_name} from s3')
        except ClientError as e:
            logger.error(e)
            return False
        return True

    def list_objects(self):
        return self.client.list_objects(Bucket=self.__bucket)['Contents']
