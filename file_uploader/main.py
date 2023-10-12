#!/usr/bin/env python
from file_uploader.cli import parse_input
from file_uploader.uploader import Uploader


def main():
    args = parse_input()

    uploader = Uploader(args.url, args.s3_bucket, args.s3_key_prefix)
    uploader.upload()


if __name__ == '__main__':
    main()
