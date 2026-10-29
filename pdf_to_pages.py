"""
Convert a PDF into fixed-size text pages sized for a 2.13" e-ink display
(250x122 landscape, default 8x8 pixel font).

Run this on your PC, not the Pico.
Requires: pip install pypdf

Usage:
    python pdf_to_pages.py fahrenheit451.pdf pages/
"""

import sys
import os
import textwrap
from pypdf import PdfReader

CHARS_PER_LINE = 28   # ~250px wide / 8px font, minus a small margin
LINES_PER_PAGE = 13   # one row reserved at the bottom for the page number


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = []
    for page in reader.pages:
        full_text.append(page.extract_text() or "")
    return "\n".join(full_text)


# The Pico's built-in font only covers plain ASCII. PDFs often use "smart"
# typographic characters that fall outside that set and render as broken
# glyphs on the display, so swap them for plain ASCII equivalents here.
CHAR_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'",   # curly single quotes
    "\u201c": '"', "\u201d": '"',   # curly double quotes
    "\u2013": "-", "\u2014": "-",   # en dash, em dash
    "\u2026": "...",                # ellipsis
    "\u00a0": " ",                  # non-breaking space
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",  # ligatures
    "\ufb03": "ffi", "\ufb04": "ffl",                # ligatures
}


def normalize_text(text):
    for bad, good in CHAR_REPLACEMENTS.items():
        text = text.replace(bad, good)
    # Anything else non-ASCII gets dropped rather than corrupted on screen
    return text.encode("ascii", errors="ignore").decode("ascii")


def paginate(text):
    wrapped_lines = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(paragraph, CHARS_PER_LINE))

    pages = []
    for i in range(0, len(wrapped_lines), LINES_PER_PAGE):
        pages.append(wrapped_lines[i:i + LINES_PER_PAGE])
    return pages


def write_pages(pages, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for i, page_lines in enumerate(pages):
        path = os.path.join(out_dir, "page_{:04d}.txt".format(i))
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(page_lines))
    return len(pages)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf_to_pages.py <input.pdf> <output_dir>")
        sys.exit(1)

    pdf_path, out_dir = sys.argv[1], sys.argv[2]
    text = extract_text(pdf_path)
    text = normalize_text(text)
    pages = paginate(text)
    count = write_pages(pages, out_dir)
    print("Wrote {} pages to {}/".format(count, out_dir))