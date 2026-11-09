"""Tests for deterministic generation output consistency."""
import pytest
from app.config import DEFAULT_SEED, TEST_TARGETS
from app.generators.synthetic_data_generator import SyntheticDataGenerator


def test_generation_exact_match():
    gen1 = SyntheticDataGenerator(seed=DEFAULT_SEED)
    e1, gt1 = gen1.generate(**TEST_TARGETS)

    gen2 = SyntheticDataGenerator(seed=DEFAULT_SEED)
    e2, gt2 = gen2.generate(**TEST_TARGETS)

    # Check keys
    assert set(e1.keys()) == set(e2.keys())

    for entity_name in e1.keys():
        list1 = e1[entity_name]
        list2 = e2[entity_name]
        assert len(list1) == len(list2), f"Length mismatch for {entity_name}"
        assert list1 == list2, f"Content mismatch for {entity_name}"

    assert len(gt1) == len(gt2)
    assert gt1 == gt2


def test_different_seeds_produce_different_data():
    gen1 = SyntheticDataGenerator(seed=1001)
    e1, _ = gen1.generate(**TEST_TARGETS)

    gen2 = SyntheticDataGenerator(seed=2002)
    e2, _ = gen2.generate(**TEST_TARGETS)

    # Candidates should differ
    names_1 = [c["full_name"] for c in e1["candidates"]]
    names_2 = [c["full_name"] for c in e2["candidates"]]
    assert names_1 != names_2
