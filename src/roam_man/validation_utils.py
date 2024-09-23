import re
from datetime import datetime


def is_valid_date(date_string: str) -> bool:
    # Define the regex pattern for "DD-MM-YYYY" date format
    pattern = r"^\d{2}-\d{2}-\d{4}$"

    # First, check if the string matches the pattern
    if re.match(pattern, date_string):
        try:
            # Try to parse the date to ensure it's valid
            datetime.strptime(date_string, "%d-%m-%Y")
            return True
        except ValueError:
            return False
    return False
