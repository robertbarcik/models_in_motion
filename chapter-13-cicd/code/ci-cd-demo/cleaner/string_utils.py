import re

def clean_string(text):
    """Remove leading/trailing spaces, convert to lowercase, remove special characters."""
    text = text.strip()
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text
