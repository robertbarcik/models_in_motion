def bin_age(age):
    """
    Bin a customer's age into a lifecycle category.

    Returns:
        "young"  for ages 0-30
        "middle" for ages 31-50
        "senior" for ages 51+

    Raises ValueError for negative ages.
    """
    if age < 0:
        raise ValueError(f"Age cannot be negative, got {age}")
    if age <= 30:
        return "young"
    elif age <= 50:
        return "middle"
    else:
        return "senior"


def compute_spend_ratio(monthly_spend, age):
    """
    Compute annual spending relative to customer age.
    This feature captures spending intensity relative to lifecycle stage.

    Returns 0.0 when age is zero to avoid division errors.
    """
    if age == 0:
        return 0.0
    return round((monthly_spend * 12) / age, 2)