"""CLI script to verify strict reproducibility across independent generation runs."""
import os
import sys
import shutil
import tempfile
from pathlib import Path
from tabulate import tabulate

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DEFAULT_SEED, TEST_TARGETS, BASELINE_TARGETS
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.services.recruitment_service import compute_dataset_hashes


def verify_reproducibility(seed: int = DEFAULT_SEED, use_baseline: bool = False):
    targets = BASELINE_TARGETS if use_baseline else TEST_TARGETS
    print(f"[*] Verifying Reproducibility with Seed: {seed}")
    print(f"    Configuration: {'Full Baseline' if use_baseline else 'Fast Test Scale'}")

    temp_dir_1 = tempfile.mkdtemp(prefix="yottaflex_run1_")
    temp_dir_2 = tempfile.mkdtemp(prefix="yottaflex_run2_")

    try:
        # Run 1
        print("    Generating Run 1...")
        gen1 = SyntheticDataGenerator(seed=seed)
        ent1, gt1 = gen1.generate(**targets)
        gen1.export_to_csv(ent1, gt1, temp_dir_1)
        hashes_1 = compute_dataset_hashes(temp_dir_1)

        # Run 2
        print("    Generating Run 2...")
        gen2 = SyntheticDataGenerator(seed=seed)
        ent2, gt2 = gen2.generate(**targets)
        gen2.export_to_csv(ent2, gt2, temp_dir_2)
        hashes_2 = compute_dataset_hashes(temp_dir_2)

        # Compare
        all_files = sorted(set(hashes_1.keys()) | set(hashes_2.keys()))
        table_data = []
        all_match = True

        for fname in all_files:
            h1 = hashes_1.get(fname, "N/A")
            h2 = hashes_2.get(fname, "N/A")
            match = (h1 == h2) and (h1 != "MISSING")
            if not match:
                all_match = False
            table_data.append([
                fname,
                h1[:12] + "...",
                h2[:12] + "...",
                "MATCH" if match else "MISMATCH",
            ])

        print("\n" + "=" * 65)
        print("              REPRODUCIBILITY COMPARISON MATRIX")
        print("=" * 65)
        headers = ["File Name", "Run 1 SHA-256", "Run 2 SHA-256", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print("=" * 65)

        if all_match:
            print("\n[OK] SUCCESS: All files produced 100% bitwise identical hashes!")
            print(f"    Reproducibility verified under seed {seed}.\n")
            return True
        else:
            print("\n[FAIL] Checksums did not match between runs.\n")
            return False

    finally:
        shutil.rmtree(temp_dir_1, ignore_errors=True)
        shutil.rmtree(temp_dir_2, ignore_errors=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test deterministic reproducibility.")
    parser.add_argument("--baseline", action="store_true", help="Run on full baseline scale instead of fast test scale")
    args = parser.parse_args()

    success = verify_reproducibility(use_baseline=args.baseline)
    sys.exit(0 if success else 1)
