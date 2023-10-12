import argparse


def parse_input():
    parser = argparse.ArgumentParser(
        description='CLI uploader utility'
    )
    parser.add_argument('url', type=str, help='URL to the zip archive')
    parser.add_argument('s3_bucket', type=str, help='S3 bucket name')
    parser.add_argument('s3_key_prefix', default="", help='S3 key prefix for uploaded files')

    args = parser.parse_args()
    s3_key_prefix = args.s3_key_prefix or ""
    return args
