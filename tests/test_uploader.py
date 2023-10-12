import os
import pytest
from moto import mock_s3
from file_uploader.loader import Uploader
import boto3
from unittest.mock import patch

import tempfile
import requests

@pytest.fixture
def mock_s3_service():
    with mock_s3():
        yield boto3.client('s3', region_name='us-east-1')

@pytest.fixture
def mock_requests_get(mocker):
    response = requests.Response()
    response.status_code = 200
    response._content = b'some content'
    mocker.patch('requests.get', return_value=response)

def test_validate_valid_s3_bucket_and_url():
    url = "http://example.com/file.zip"
    s3_bucket = "test-bucket"
    uploader = Uploader(url, s3_bucket)
    with patch.object(uploader.s3_client, 'head_bucket') as mock_head_bucket, \
         patch('requests.head') as mock_requests_head:
        mock_head_bucket.return_value = True
        mock_requests_head.return_value.status_code = 200

        uploader._validate()

        mock_head_bucket.assert_called_once_with(Bucket=s3_bucket)
        mock_requests_head.assert_called_once_with(url)

def test_validate_invalid_s3_bucket():
    url = "http://example.com/file.zip"
    s3_bucket = "test-bucket"
    uploader = Uploader(url, s3_bucket)
    with patch.object(uploader.s3_client, 'head_bucket') as mock_head_bucket, \
         patch('requests.head') as mock_requests_head:
        mock_head_bucket.side_effect = Exception("Invalid S3 Bucket")

        with pytest.raises(Exception, match="Invalid S3 Bucket"):
            uploader._validate()

        mock_head_bucket.assert_called_once_with(Bucket=s3_bucket)
        mock_requests_head.assert_not_called()

def test_validate_invalid_url():
    url = "http://example.com/file.zip"
    s3_bucket = "test-bucket"
    uploader = Uploader(url, s3_bucket)
    with patch.object(uploader.s3_client, 'head_bucket') as mock_head_bucket, \
         patch('requests.head') as mock_requests_head:
        mock_head_bucket.return_value = True
        mock_requests_head.side_effect = requests.exceptions.HTTPError("Invalid URL")

        with pytest.raises(Exception, match="Invalid URL http://example.com/file.zip with error: Invalid URL"):
            uploader._validate()

        mock_head_bucket.assert_called_once_with(Bucket=s3_bucket)
        mock_requests_head.assert_called_once_with(url)

def test_upload(mock_s3_service, mock_requests_get):
    with tempfile.NamedTemporaryFile(suffix='.zip') as temp_zip_file:
        uploader = Uploader("http://example.com/file.zip", "test-bucket")
        assert uploader.download_zip(temp_zip_file.name)
        