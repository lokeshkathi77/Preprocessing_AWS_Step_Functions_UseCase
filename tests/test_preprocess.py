import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "application"))

from preprocess import preprocess


def test_preprocess_writes_cleaned_and_rejected_rows(tmp_path):
    input_path = tmp_path / "transactions.csv"
    output_path = tmp_path / "processed" / "cleaned.csv"
    rejected_path = tmp_path / "errors" / "rejected.csv"

    input_path.write_text(
        "transaction_id,amount,currency\n"
        "TXN001,250.00,INR\n"
        "TXN002,-25.00,INR\n"
        "TXN001,100.00,INR\n",
        encoding="utf-8",
    )

    valid, rejected = preprocess(input_path, output_path, rejected_path)

    assert (valid, rejected) == (1, 2)
    with output_path.open(newline="", encoding="utf-8") as file:
        assert list(csv.DictReader(file))[0]["transaction_id"] == "TXN001"
    with rejected_path.open(newline="", encoding="utf-8") as file:
        errors = list(csv.DictReader(file))
    assert errors[0]["error"] == "amount must be greater than zero"
    assert errors[1]["error"] == "duplicate transaction_id"
