## Description

Create CLI utility that as an argument receives URL to the ZIP archive and upload archives files to the
S3 with concurrency.

## Installation

To install the utility, follow these steps:

2. Install [Poetry](https://python-poetry.org/docs/#installation) for managing dependencies and virtual environment:

   `pip install poetry`


## Clone the repository:

`git clone https://github.com/starenesha/s3_zip_uploader.git
cd s3_zip_uploader`

## Install the dependencies:

   `poetry install`

## Add aws credentials .env

Add credentials

    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=

## Usage
The utility supports the following commands:

Upload a file:

   `s3_zip_uploader https://example.com/file.zip test-bucket ""`

## Additional options:

<file URL> - The URL of the file you want to upload.
<S3 bucket name> - The name of the S3 bucket where you want to upload the file.
<S3 key prefix> (optional) - The S3 key prefix where the file will be uploaded (if specified).
