import re
import requests
import streamlit as st

def extract_book_id(url: str) -> str:
    match = re.search(r'/ebooks/(\d+)|/epub/(\d+)', url)

  
    if match:
        return match.group(1) or match.group(2)
    return "0"  # fallback


def text_to_latex(text, linebreak_type="\\"):
    """
    Convert plain text into LaTeX format, preserving line breaks.

    :param text: Input poem or text (copy-pasted).
    :param linebreak_type: Choose from ["\\", "\\newline", "\\linebreak", "\\par"].
    :return: LaTeX-formatted text.
    """
    special_chars = {
        "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "$": r"\$", "{": r"\{", "}": r"\}",
        "^": r"\^{}", "~": r"\textasciitilde{}", "\\": r"\textbackslash{}"
    }
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)

    # Preserve line breaks using selected method
    text = text.replace("\n", f" {linebreak_type}\n")
    return text



def latex_to_paragraph_dataframe(latex_text):
    """
    Parses LaTeX-formatted text, groups lines into paragraphs based on single \newline breaks,
    and stores each paragraph in a DataFrame row.
    :param latex_text: LaTeX-formatted string.
    :return: Pandas DataFrame with paragraphs as rows.
    """
    # Remove LaTeX document structure
    latex_text = re.sub(r"\\documentclass{.*?}|\\begin{document}|\\end{document}", "", latex_text, flags=re.DOTALL)
    # Split text by isolated \newline (i.e., it appears on a line by itself)
    raw_paragraphs = re.split(r"\s*\n\s*\\newline\s*\n\s*", latex_text.strip())
    # Merge paragraph lines (inside each paragraph) into a single text block
    paragraphs = [" ".join(re.split(r"\s*\\newline\s*", para)).strip() for para in raw_paragraphs]
    # Remove remaining LaTeX commands and extra spaces
    paragraphs = [re.sub(r"\\[a-zA-Z]+", "", para).strip() for para in paragraphs if para.strip()]
    # Convert to DataFrame
    df = pd.DataFrame({"Paragraph": paragraphs})
    return df

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

