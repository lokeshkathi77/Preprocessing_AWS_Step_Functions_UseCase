import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "application"))

from processor import process_transactions


def test_valid_and_rejected_transactions():
    content = """transaction_id,amount,currency
TXN001,250.00,INR
TXN002,-25.00,INR
TXN003,100.00,INR
"""

    result = process_transactions(content)

    assert result["inputRecords"] == 3
    assert result["validRecords"] == 2
    assert result["rejectedRecords"] == 1


def test_missing_header_column():
    content = """transaction_id,amount
TXN001,250.00
"""

    try:
        process_transactions(content)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "Missing required columns" in str(error)


def test_non_numeric_amount_is_rejected():
    content = """transaction_id,amount,currency
TXN001,ABC,INR
"""

    result = process_transactions(content)

    assert result["validRecords"] == 0
    assert result["rejectedRecords"] == 1
    assert result["rejections"][0]["reason"] == "Amount is not numeric"
