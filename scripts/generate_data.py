"""CLI script to generate synthetic recruitment data and seed SQLite database."""
import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DEFAULT_SEED, BASELINE_TARGETS, TEST_TARGETS
from app.database import init_db, SessionLocal
from app.services.recruitment_service import generate_and_save_data


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic recruitment data.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"Random seed (default: {DEFAULT_SEED})")
    parser.add_argument("--quick", action="store_true", help="Generate small fast dataset for testing")
    parser.add_argument("--requisitions", type=int, default=None, help="Requisitions count override")
    parser.add_argument("--candidates", type=int, default=None, help="Candidates count override")
    parser.add_argument("--applications", type=int, default=None, help="Applications count override")
    parser.add_argument("--interviews", type=int, default=None, help="Interviews count override")
    parser.add_argument("--offers", type=int, default=None, help="Offers count override")

    args = parser.parse_args()

    targets = TEST_TARGETS if args.quick else BASELINE_TARGETS.copy()
    if args.requisitions:
        targets["num_requisitions"] = args.requisitions
    if args.candidates:
        targets["num_candidates"] = args.candidates
    if args.applications:
        targets["num_applications"] = args.applications
    if args.interviews:
        targets["num_interviews"] = args.interviews
    if args.offers:
        targets["num_offers"] = args.offers

    print("[*] Initializing Database and Tables...")
    init_db()

    print(f"[*] Generating Synthetic Data (Seed: {args.seed})...")
    print(f"    Target Requisitions : {targets['num_requisitions']}")
    print(f"    Target Candidates   : {targets['num_candidates']}")
    print(f"    Target Applications : {targets['num_applications']}")
    print(f"    Target Interviews   : {targets['num_interviews']}")
    print(f"    Target Offers       : {targets['num_offers']}")

    db = SessionLocal()
    try:
        row_counts, anomalies_count = generate_and_save_data(
            seed=args.seed,
            num_requisitions=targets["num_requisitions"],
            num_candidates=targets["num_candidates"],
            num_applications=targets["num_applications"],
            num_interviews=targets["num_interviews"],
            num_offers=targets["num_offers"],
            db=db,
        )
    finally:
        db.close()

    print("\n[OK] Generation Complete! Entity Counts:")
    for entity, count in row_counts.items():
        print(f"   - {entity:<20}: {count} records")

    print(f"\n[!] Intentional Ground Truth Anomalies Injected: {anomalies_count}")
    print("    CSV & JSON Exports saved to 'data/' directory.")
    print("    SQLite database seeded at 'data/recruitment.db'.\n")


if __name__ == "__main__":
    main()
