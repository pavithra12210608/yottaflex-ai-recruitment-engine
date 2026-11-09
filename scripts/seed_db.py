"""CLI script to seed SQLite database from existing CSV exports."""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, SessionLocal
from app.services.recruitment_service import load_entities_from_csv, seed_database_from_entities


def main():
    print("[*] Initializing Database Schema...")
    init_db()

    print("[*] Reading entities from data/*.csv...")
    entities = load_entities_from_csv()

    non_empty = {k: len(v) for k, v in entities.items() if len(v) > 0}
    if not non_empty:
        print("[FAIL] No CSV files found in data/. Please run scripts/generate_data.py first.")
        sys.exit(1)

    print(f"[*] Seeding SQLite database from {len(non_empty)} entity files...")
    db = SessionLocal()
    try:
        seed_database_from_entities(db, entities)
        print("[OK] Database successfully seeded!")
        for k, v in non_empty.items():
            print(f"   - {k:<20}: {v} rows loaded")
    finally:
        db.close()


if __name__ == "__main__":
    main()
