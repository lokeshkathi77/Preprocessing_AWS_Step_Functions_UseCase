#!/usr/bin/env python3
"""Normalize transaction CSV values and write the result back to S3."""

import argparse
import csv
import json
import os
import tempfile
from urllib.parse import urlparse

import boto3


DEFAULT_FIELD_VALUES = {
    "transaction_id": "UNKNOWN",
    "customer_id": "UNKNOWN",
    "amount": "0",
    "currency": "UNKNOWN",
    "transaction_date": "UNKNOWN",
}


def parse_s3_uri(uri):
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.lstrip("/"):
        raise ValueError("The transaction file must be an s3://bucket/key URI")
    return parsed.netloc, parsed.path.lstrip("/")


def load_defaults():
    configured = os.environ.get("TRANSACTION_DEFAULTS_JSON")
    if not configured:
        return DEFAULT_FIELD_VALUES.copy()

    values = DEFAULT_FIELD_VALUES.copy()
    values.update(json.loads(configured))
    return {str(key): str(value) for key, value in values.items()}


def normalize_file(input_uri, output_uri, defaults):
    input_bucket, input_key = parse_s3_uri(input_uri)
    output_bucket, output_key = parse_s3_uri(output_uri)
    s3 = boto3.client("s3")

    with tempfile.NamedTemporaryFile(mode="w+", newline="", encoding="utf-8") as file:
        response = s3.get_object(Bucket=input_bucket, Key=input_key)
        rows = csv.DictReader(
            response["Body"].read().decode("utf-8").splitlines()
        )
        if not rows.fieldnames:
            raise ValueError("The transaction file must contain a header")

        writer = csv.DictWriter(file, fieldnames=rows.fieldnames)
        writer.writeheader()
        row_count = 0

        for row in rows:
            for field, default in defaults.items():
                if field in row and not str(row[field] or "").strip():
                    row[field] = default
            writer.writerow(row)
            row_count += 1

        file.flush()
        file.seek(0)
        s3.upload_fileobj(file, output_bucket, output_key)

    return row_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    row_count = normalize_file(args.input, args.output, load_defaults())
    print(f"normalized_records={row_count}")
    print(f"normalized_file={args.output}")


if __name__ == "__main__":
    main()
