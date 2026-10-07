import pytest
from feature_engineering import bin_age, compute_spend_ratio


def test_bin_age_typical_values():
    """Each representative age maps to the correct category."""
    assert bin_age(25) == "young"
    assert bin_age(40) == "middle"
    assert bin_age(65) == "senior"


def test_bin_age_boundaries():
    """Values at the exact boundaries fall into the expected bins."""
    assert bin_age(30) == "young"    # upper boundary of "young"
    assert bin_age(31) == "middle"   # lower boundary of "middle"
    assert bin_age(50) == "middle"   # upper boundary of "middle"
    assert bin_age(51) == "senior"   # lower boundary of "senior"


def test_bin_age_negative_raises_error():
    """Negative age should raise a ValueError, not silently return a bin."""
    with pytest.raises(ValueError):
        bin_age(-5)


def test_spend_ratio_normal():
    """Standard case: customer aged 30 spending 100/month -> (100 * 12) / 30 = 40.0"""
    assert compute_spend_ratio(100, 30) == 40.0


def test_spend_ratio_zero_age():
    """Edge case: age zero should return 0.0 instead of raising ZeroDivisionError."""
    assert compute_spend_ratio(100, 0) == 0.0
