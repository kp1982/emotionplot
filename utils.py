import re

def extract_book_id(url: str) -> str:
    """
    Tries to extract a valid Gutenberg book ID from various URL formats.
    """
    # Match numbers at end of /ebooks/### or /epub/### path
    match = re.search(r'/ebooks/(\d+)|/epub/(\d+)', url)
    if match:
        return match.group(1) or match.group(2)
    return "0"  # fallback
