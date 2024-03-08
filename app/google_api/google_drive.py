import os
from typing import List
from loguru import logger
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class GoogleDriver:
    _scopes: list
    __creds: str
    local_path: str

    def __init__(
            self,
            scopes: list,
            local_path: str,
            creds_path: str
    ) -> None:
        self._scopes = scopes
        self.__creds = service_account.Credentials.from_service_account_file(
            filename=creds_path
        )
        self.service = build('drive', 'v3', credentials=self.__creds)
        self.local_path = local_path

    def _get_files_list(self) -> List[dict]:
        """Get list of all google drive files available"""
        return self.service.files().list(spaces="drive").execute()['files']

    def _get_file_id(self, filename: str) -> str:
        """Search for file id among available files"""
        files = self._get_files_list()
        for file in files:
            if file['name'] == filename:
                return file['id']

    def download_file(self, filename: str) -> str | None:
        """Download found file to the local_path directory"""
        file_id = self._get_file_id(filename)
        path = os.path.join(self.local_path, filename)
        if not file_id:
            logger.error(f'File {filename} not found on Google Drive')
            return None
        else:
            request = self.service.files().get_media(fileId=file_id)
            with open(path, 'wb') as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                logger.info(f'File {filename} downloaded successfully')
        return path
