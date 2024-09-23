import pytest
import random

from faker import Faker
from roam_man import validation_utils as vu


# Define a pytest fixture for setting up the Faker instance
@pytest.fixture(scope="function")
def faker_instance():
    fake = Faker()
    yield fake


# Generate random valid dates in DD-MM-YYYY format
def generate_random_valid_date(fake):
    return fake.date_of_birth(minimum_age=1, maximum_age=100).strftime("%d-%m-%Y")


# Generate random invalid dates or date strings
def generate_random_invalid_date(fake):
    invalid_dates = [
        "32-12-2023",  # Invalid day
        "25-13-2023",  # Invalid month
        "99-99-9999",  # Completely invalid date
        "2023-12-25",  # Invalid format
        "00-00-0000",  # Nonexistent date
        "31-02-2023",  # Invalid February date
        "31-04-2023",  # Invalid April date
        fake.date_of_birth(minimum_age=1, maximum_age=100).strftime(
            "%Y-%m-%d"
        ),  # Wrong format (YYYY-MM-DD)
    ]
    return random.choice(invalid_dates)


# Test valid dates using the faker_instance fixture
def test_random_valid_dates(faker_instance):
    for _ in range(5):
        valid_date = generate_random_valid_date(faker_instance)
        assert vu.is_valid_date(valid_date), f"Valid date failed: {valid_date}"


# Test invalid dates using the faker_instance fixture
def test_random_invalid_dates(faker_instance):
    for _ in range(5):
        invalid_date = generate_random_invalid_date(faker_instance)
        assert not vu.is_valid_date(
            invalid_date
        ), f"Invalid date passed: {invalid_date}"
