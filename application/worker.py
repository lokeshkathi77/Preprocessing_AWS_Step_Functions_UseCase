import csv
import os
import sys
from datetime import datetime, timezone
from io import TextIOWrapper
from urllib.parse import urlparse

import boto3


def parse_s3_uri(uri):
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.lstrip("/"):
        raise ValueError("TRANSACTION_FILE must be an s3://bucket/key URI")
    return parsed.netloc, parsed.path.lstrip("/")


def process_transaction_file(uri):
    bucket, key = parse_s3_uri(uri)
    response = boto3.client("s3").get_object(Bucket=bucket, Key=key)
    stream = TextIOWrapper(response["Body"], encoding="utf-8", newline="")
    reader = csv.DictReader(stream)
    rows = list(reader)
    amount_column = os.environ.get("TRANSACTION_AMOUNT_COLUMN", "amount")
    amounts = [float(row[amount_column]) for row in rows if row.get(amount_column)]
    return len(rows), sum(amounts)


transaction_file = os.environ.get("TRANSACTION_FILE")
if not transaction_file:
    print("TRANSACTION_FILE is required", file=sys.stderr)
    raise SystemExit(2)

try:
    record_count, total_amount = process_transaction_file(transaction_file)
except (ValueError, KeyError, TypeError) as error:
    print(f"transaction processing failed: {error}", file=sys.stderr)
    raise SystemExit(3) from error

print(f"transaction worker started at {datetime.now(timezone.utc).isoformat()}")
print(f"processed transaction file: {transaction_file}")
print(f"record_count={record_count}")
print(f"total_amount={total_amount:.2f}")
print("transaction processing completed successfully")
