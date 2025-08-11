from pathlib import Path
import re


def read_txt(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def read_epub(p: Path) -> str:
    from ebooklib import epub
    from bs4 import BeautifulSoup
    book = epub.read_epub(str(p))
    parts = []
    for item in book.get_items():
        if item.get_type() == 9:  # DOCUMENT
            soup = BeautifulSoup(item.get_content(), "html.parser")
            parts.append(soup.get_text(" ", strip=True))
    return "\n\n".join(parts)


def read_pdf(p: Path) -> str:
    try:
        import fitz
        pages = []
        with fitz.open(str(p)) as doc:
            for page in doc:
                pages.append(page.get_text("text"))
        return "\n\n".join(pages)
    except Exception:
        from pypdf import PdfReader
        reader = PdfReader(str(p))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)


def extract_text(path: str) -> str:
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".txt":
        txt = read_txt(p)
    elif ext == ".epub":
        txt = read_epub(p)
    elif ext == ".pdf":
        txt = read_pdf(p)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    txt = re.sub(r"\r\n?", "\n", txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return txt.strip()
