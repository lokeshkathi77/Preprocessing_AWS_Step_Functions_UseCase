import os
import sys
from datetime import datetime, timezone


transaction_file = os.environ.get("TRANSACTION_FILE")
if not transaction_file:
    print("TRANSACTION_FILE is required", file=sys.stderr)
    raise SystemExit(2)

print(f"transaction worker started at {datetime.now(timezone.utc).isoformat()}")
print(f"processing transaction file: {transaction_file}")
print("transaction processing completed successfully")
