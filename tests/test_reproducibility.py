"""Tests for bitwise deterministic reproducibility across runs."""
import pytest
from app.config import DEFAULT_SEED
from scripts.check_reproducibility import verify_reproducibility


def test_deterministic_reproducibility():
    """Verify that independent generation runs produce identical bitwise checksums."""
    is_reproducible = verify_reproducibility(seed=DEFAULT_SEED, use_baseline=False)
    assert is_reproducible is True
