import re
import requests
import streamlit as st

def extract_book_id(url: str) -> str:
    match = re.search(r'/ebooks/(\d+)|/epub/(\d+)', url)
    return match.group(1) or match.group(2) if match else "0"

def get_book_metadata(book_id: str):
    meta_url = f"https://gutendex.com/books/{book_id}"
    try:
        response = requests.get(meta_url, timeout=5)
        response.raise_for_status()
        metadata = response.json()
        title = metadata.get("title", "Unknown Title")
        authors = metadata.get("authors", [])
        author = authors[0]["name"] if authors else "Unknown Author"
        return title, author
    except:
        return "Unknown Title", "Unknown Author"

def get_cover_url(book_id: str):
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
    try:
        if requests.head(url, timeout=3).status_code == 200:
            return url
    except:
        pass
    return "https://via.placeholder.com/120x180.png?text=No+Cover"
