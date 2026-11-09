"""CLI script to run data validation engine and print detailed report."""
import sys
from pathlib import Path
from tabulate import tabulate

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.recruitment_service import load_entities_from_csv
from app.validators.validation_engine import ValidationEngine


def main():
    print("[*] Loading dataset from CSV exports...")
    entities = load_entities_from_csv()

    if not any(len(v) > 0 for v in entities.values()):
        print("[FAIL] Dataset not found in data/. Please run scripts/generate_data.py first.")
        sys.exit(1)

    print("[*] Running Comprehensive Validation Engine...")
    validator = ValidationEngine(entities)
    report = validator.run_all_validations()

    print("\n" + "=" * 70)
    print("                   RECRUITMENT DATA VALIDATION REPORT")
    print("=" * 70)
    print(f"Overall Status   : {report['status']}")
    print(f"Total Checks     : {report['total_checks']}")
    print(f"Passed Checks    : {report['passed_checks']}")
    print(f"Failed Checks    : {report['failed_checks']}")
    print(f"Warnings         : {report['warning_checks']}")
    print(f"Execution Time   : {report['timestamp']}")
    print("=" * 70 + "\n")

    table_data = []
    for f in report["findings"]:
        table_data.append([
            f["severity"],
            f["check_name"],
            f["entity"],
            f["record_id"] or "-",
            f["message"][:75] + ("..." if len(f["message"]) > 75 else ""),
        ])

    headers = ["Severity", "Check Name", "Entity", "Record ID", "Message"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("\n")


if __name__ == "__main__":
    main()
