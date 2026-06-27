#!/usr/bin/env python3

import argparse
from pathlib import Path

import boto3


def parse_s3_uri(uri):
    if not uri.startswith("s3://"):
        raise ValueError("S3 URI must start with s3://")

    stripped = uri[5:]
    bucket, _, prefix = stripped.partition("/")
    return bucket, prefix


def main():
    parser = argparse.ArgumentParser(
        description="Upload remote access diagnostics bundle to S3"
    )
    parser.add_argument("--file", required=True, help="Path to diagnostics bundle")
    parser.add_argument(
        "--bucket",
        required=True,
        help="S3 destination, for example s3://bucket/path/",
    )
    args = parser.parse_args()

    source_file = Path(args.file)

    if not source_file.exists():
        raise FileNotFoundError(source_file)

    bucket, prefix = parse_s3_uri(args.bucket)
    key = f"{prefix.rstrip('/')}/{source_file.name}"

    s3 = boto3.client("s3")
    s3.upload_file(str(source_file), bucket, key)

    print(f"Uploaded {source_file} to s3://{bucket}/{key}")


if __name__ == "__main__":
    main()
