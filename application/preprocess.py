#!/usr/bin/env python3
"""Validate and clean transaction CSV files before ECS processing."""

import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED_COLUMNS = ("transaction_id", "amount", "currency")


def clean_transaction(row):
    transaction_id = (row.get("transaction_id") or "").strip()
    amount_text = (row.get("amount") or "").strip()
    currency = (row.get("currency") or "").strip().upper()

    if not transaction_id:
        raise ValueError("transaction_id is missing")
    if not currency:
        raise ValueError("currency is missing")

    try:
        amount = Decimal(amount_text)
    except InvalidOperation as exc:
        raise ValueError("amount is not numeric") from exc

    if amount <= 0:
        raise ValueError("amount must be greater than zero")

    return {
        "transaction_id": transaction_id,
        "amount": format(amount, "f"),
        "currency": currency,
    }


def preprocess(input_path, output_path, rejected_path):
    seen = set()
    valid_count = 0
    rejected_count = 0

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(rejected_path).parent.mkdir(parents=True, exist_ok=True)

    with (
        Path(input_path).open("r", encoding="utf-8-sig", newline="") as source,
        Path(output_path).open("w", encoding="utf-8", newline="") as output,
        Path(rejected_path).open("w", encoding="utf-8", newline="") as rejected,
    ):
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not set(REQUIRED_COLUMNS).issubset(reader.fieldnames):
            raise ValueError(
                f"CSV must contain columns: {', '.join(REQUIRED_COLUMNS)}"
            )

        valid_writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS)
        rejected_writer = csv.DictWriter(
            rejected,
            fieldnames=(*REQUIRED_COLUMNS, "error"),
        )
        valid_writer.writeheader()
        rejected_writer.writeheader()

        for row in reader:
            try:
                cleaned = clean_transaction(row)
                if cleaned["transaction_id"] in seen:
                    raise ValueError("duplicate transaction_id")
                seen.add(cleaned["transaction_id"])
                valid_writer.writerow(cleaned)
                valid_count += 1
            except (TypeError, ValueError) as exc:
                rejected_writer.writerow(
                    {
                        column: row.get(column, "")
                        for column in REQUIRED_COLUMNS
                    }
                    | {"error": str(exc)}
                )
                rejected_count += 1

    return valid_count, rejected_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rejected", required=True)
    args = parser.parse_args()

    try:
        valid, rejected = preprocess(
            args.input,
            args.output,
            args.rejected,
        )
    except (OSError, ValueError) as exc:
        print(f"Preprocessing failed: {exc}", file=sys.stderr)
        return 1

    print(f"Preprocessing complete: valid={valid}, rejected={rejected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
