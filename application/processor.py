import csv
import io
import json
import logging
import os
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

import boto3


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def process_transactions(content):
    reader = csv.DictReader(io.StringIO(content))

    required_columns = {"transaction_id", "amount", "currency"}

    if not reader.fieldnames:
        raise ValueError("The transaction file has no header")

    missing_columns = required_columns.difference(reader.fieldnames)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    valid_transactions = []
    rejected_transactions = []

    for line_number, row in enumerate(reader, start=2):
        transaction_id = (row.get("transaction_id") or "").strip()
        amount_text = (row.get("amount") or "").strip()
        currency = (row.get("currency") or "").strip()

        if not transaction_id:
            rejected_transactions.append(
                {
                    "lineNumber": line_number,
                    "reason": "Transaction ID is missing",
                }
            )
            continue

        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            rejected_transactions.append(
                {
                    "lineNumber": line_number,
                    "transactionId": transaction_id,
                    "reason": "Amount is not numeric",
                }
            )
            continue

        if amount <= 0:
            rejected_transactions.append(
                {
                    "lineNumber": line_number,
                    "transactionId": transaction_id,
                    "reason": "Amount must be greater than zero",
                }
            )
            continue

        if not currency:
            rejected_transactions.append(
                {
                    "lineNumber": line_number,
                    "transactionId": transaction_id,
                    "reason": "Currency is missing",
                }
            )
            continue

        valid_transactions.append(
            {
                "transactionId": transaction_id,
                "amount": str(amount),
                "currency": currency,
            }
        )

    return {
        "inputRecords": len(valid_transactions) + len(rejected_transactions),
        "validRecords": len(valid_transactions),
        "rejectedRecords": len(rejected_transactions),
        "validTransactions": valid_transactions,
        "rejections": rejected_transactions,
    }


def run_local():
    input_file = os.getenv(
        "LOCAL_INPUT_FILE",
        "sample-data/transactions.csv",
    )

    output_file = os.getenv(
        "LOCAL_OUTPUT_FILE",
        "transaction-summary.json",
    )

    logger.info("Running in local mode")
    logger.info("Reading input file: %s", input_file)

    content = Path(input_file).read_text(encoding="utf-8")
    result = process_transactions(content)

    result["inputLocation"] = input_file
    result["outputLocation"] = output_file

    Path(output_file).write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    logger.info(
        "Processing completed: input=%s valid=%s rejected=%s",
        result["inputRecords"],
        result["validRecords"],
        result["rejectedRecords"],
    )

    logger.info("Output written to: %s", output_file)


def run_s3():
    input_bucket = os.environ["INPUT_BUCKET"]
    input_key = os.environ["INPUT_KEY"]
    output_bucket = os.environ["OUTPUT_BUCKET"]

    transaction_date = os.getenv("TRANSACTION_DATE", "unknown")
    execution_id = os.getenv("EXECUTION_ID", "manual")

    s3 = boto3.client("s3")

    logger.info("Running in S3 mode")
    logger.info("Reading s3://%s/%s", input_bucket, input_key)

    response = s3.get_object(
        Bucket=input_bucket,
        Key=input_key,
    )

    content = response["Body"].read().decode("utf-8")
    result = process_transactions(content)

    output_key = (
        f"processed/{transaction_date}/"
        f"{execution_id}/transaction-summary.json"
    )

    result["inputLocation"] = f"s3://{input_bucket}/{input_key}"
    result["outputLocation"] = f"s3://{output_bucket}/{output_key}"

    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=json.dumps(result, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    logger.info(
        "Processing completed: input=%s valid=%s rejected=%s",
        result["inputRecords"],
        result["validRecords"],
        result["rejectedRecords"],
    )

    logger.info(
        "Output written to s3://%s/%s",
        output_bucket,
        output_key,
    )


def main():
    run_mode = os.getenv("RUN_MODE", "local").lower()

    if run_mode == "local":
        run_local()
    elif run_mode == "s3":
        run_s3()
    else:
        raise ValueError(
            f"Unsupported RUN_MODE: {run_mode}. Use local or s3."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Transaction processing failed")
        sys.exit(1)
