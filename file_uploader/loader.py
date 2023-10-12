import os
import sys
import logging
import tempfile
import zipfile
import requests
import concurrent.futures
import boto3
from botocore.exceptions import ClientError
from typing import List


class Uploader:
    def __init__(self, url: str, s3_bucket: str, s3_key_prefix: str = ""):
        """
        Initialize the Uploader class.
        Args:
            url (str): The URL of the zip archive.
            s3_bucket (str): The name of the S3 bucket.
            s3_key_prefix (str, optional): The prefix to be added to S3 keys.
            Defaults to "".
        """
        self.url = url
        self.s3_bucket = s3_bucket
        self.s3_key_prefix = s3_key_prefix
        self.logger = self._setup_logger()
        self.s3_client = boto3.client('s3')
        self.zip_file_paths: List[str] = []

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger for the Uploader class.
        Returns:
            logging.Logger: The configured logger object.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def _validate(self):
        """
        Validate the S3 bucket and URL.
        Raises:
            Exception: If the S3 bucket or URL is invalid.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
        except ClientError as e:
            self.logger.error('S3 bucket failed with: {}'.format(e))
            raise Exception('S3 bucket does not exist: {}'.format(e))

        try:
            response = requests.head(self.url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.error('Invalid URL {} with error: {}'.format(self.url, e))
            raise Exception('Invalid URL {} with error: {}'.format(self.url, e))

    def download_zip(self, temp_zip_file: str) -> bool:
        """
        Download the zip archive from the specified URL and save it to a temporary file.
        Args:
            temp_zip_file (str): The path to the temporary file to save the zip archive.
        Returns:
            bool: True if the download is successful, False otherwise.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()

            with open(temp_zip_file, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.HTTPError as e:
            self.logger.error(e)
            return False

        self.logger.info('Archive downloaded successfully.')
        return True

    def get_zip_archive(self, temp_zip_file: str) -> str:
        """
        Extract the zip archive to a temporary directory.
        Args:
            temp_zip_file (str): The path to the temporary zip archive to extract.
        Returns:
            str: The path to the temporary directory containing the extracted files.
        """
        self.logger.info('Extracting zip archive: {}'.format(temp_zip_file))
        temp_dir = tempfile.mkdtemp()

        with zipfile.ZipFile(temp_zip_file, 'r') as zip_file:
            zip_file.extractall(temp_dir)

        self.logger.info('Archive extracted successfully.')
        return temp_dir

    def get_all_file_paths(self, directory: str) -> List[str]:
        """
        List all file paths in the specified directory and its subdirectories.
        Args:
            directory (str): The directory to list.
        Returns:
            List[str]: A list of all file paths in the directory tree.
        """
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
        return file_paths

    def upload_files_to_s3(self, local_file_path: str, s3_key: str):
        """
        Upload a file to the specified S3 key.
        Args:
            local_file_path (str): The local file path to upload.
            s3_key (str): The S3 key to upload the file to.
        """
        try:
            self.s3_client.upload_file(Filename=local_file_path, Bucket=self.s3_bucket, Key=s3_key)
        except (IsADirectoryError, FileNotFoundError) as e:
            self.logger.error('Failed to upload file to S3 bucket: {}'.format(e))
            raise Exception('Failed to upload file to S3 bucket: {}'.format(e))

        self.logger.info('{} uploaded successfully to S3 bucket: {}'.format(s3_key, self.s3_bucket))

    def upload(self):
        """
        Download, extract, and upload the files to the specified S3 bucket.
        """
        try:
            temp_files_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            if self.download_zip(temp_files_zip.name):
                temp_dir = self.get_zip_archive(temp_files_zip.name)
                paths = self.get_all_file_paths(temp_dir)

                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    for file in paths:
                        s3_file = os.path.join(self.s3_key_prefix, os.path.relpath(file, temp_dir))
                        executor.submit(self.upload_files_to_s3, file, s3_file)

                    # Wait for all tasks to complete.
                    executor.shutdown(wait=True)

                # Delete the local zip file and extracted files
                os.remove(temp_files_zip.name)
                self.logger.info('Zip files have been deleted')
        except Exception as e:
            self.logger.error(e)
            raise e
