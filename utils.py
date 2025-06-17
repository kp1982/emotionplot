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
