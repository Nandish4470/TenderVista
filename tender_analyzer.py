"""
Simple Tender Analyzer

This script extracts text from a PDF file and attempts to parse common tender fields:
- Tender Title
- Tender Reference / ID
- Issuing Organization
- Closing Date

It uses PyMuPDF (fitz) to extract embedded text. If a page has no extractable text, it falls back to OCR using pytesseract.

Usage:
    python tender_analyzer.py /path/to/tender.pdf

This is a small, self-contained utility created as a reference-based implementation.
"""

from __future__ import annotations
import re
import sys
import json
import argparse
from typing import Dict, Optional, Any

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import pytesseract
except Exception:
    pytesseract = None

try:
    from dateutil import parser as dateparser
except Exception:
    dateparser = None


def extract_text_from_pdf(path: str, force_ocr: bool = False, dpi: int = 200) -> str:
    """Extract text from PDF using PyMuPDF and fallback OCR with pytesseract for pages with no text or if force_ocr."""
    if not fitz:
        raise RuntimeError("PyMuPDF (fitz) is required. Install with 'pip install pymupdf'.")

    doc = fitz.open(path)
    pages_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = ""
        if not force_ocr:
            try:
                text = page.get_text("text") or ""
            except Exception:
                text = ""

        if text and text.strip() and not force_ocr:
            pages_text.append(text)
            continue

        # Fallback to OCR
        if pytesseract and Image:
            pix = page.get_pixmap(dpi=dpi)
            mode = "RGB" if pix.n < 4 else "RGBA"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            pages_text.append(ocr_text)
        else:
            pages_text.append("")
    return "\n".join(pages_text)


# Heuristic parsing functions

RE_TITLE = re.compile(r"(?im)^\s*(?:Tender(?:\s+Title)?|Title|Project)[:\-\s]{0,5}(.+)$")
RE_REF = re.compile(r"(?im)(?:Reference|Ref|Tender\s+No\.?|Tender\s+ID)[:\-\s]{0,5}([A-Z0-9\-_/]+)")
RE_ORG = re.compile(r"(?im)^(?:Issued\s+By|Issuing\s+Organization|Organization|Procurement\s+Entity|Issued\s+To)[:\-\s]{0,5}(.+)$")
RE_DATE = re.compile(r"(?im)(?:Closing\s+Date|Deadline|Bid\s+Submission\s+Deadline|Submission\s+Deadline)[:\-\s]{0,5}(.+)$")


def first_match(pattern: re.Pattern, text: str) -> Optional[str]:
    m = pattern.search(text)
    if not m:
        return None
    return m.group(1).strip()


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    if not dateparser:
        # dateutil not available; return raw
        return date_str
    try:
        dt = dateparser.parse(date_str, fuzzy=True)
        return dt.isoformat()
    except Exception:
        return date_str


def parse_tender_text(text: str) -> Dict[str, Optional[str]]:
    """Parse heuristic fields from extracted text."""
    lines = text.splitlines()
    full = "\n".join([l.strip() for l in lines if l.strip()])

    title = first_match(RE_TITLE, full)
    ref = first_match(RE_REF, full)
    org = first_match(RE_ORG, full)
    date = first_match(RE_DATE, full)

    # Secondary heuristics
    if not title:
        # Try first non-empty line with capitalization
        for l in lines:
            s = l.strip()
            if not s:
                continue
            if len(s) > 10 and s[0].isupper():
                title = s
                break

    normalized_date = normalize_date(date)

    return {"title": title, "reference": ref, "organization": org, "closing_date": normalized_date}


def analyze_file(path: str, force_ocr: bool = False, dpi: int = 200) -> Dict[str, Any]:
    text = extract_text_from_pdf(path, force_ocr=force_ocr, dpi=dpi)
    parsed = parse_tender_text(text)
    return {
        "path": path,
        "parsed": parsed,
        "text_snippet": text[:200]
    }


def main():
    parser = argparse.ArgumentParser(description="Tender Analyzer CLI")
    parser.add_argument("path", help="Path to PDF file to analyze")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--ocr", action="store_true", help="Force OCR for all pages")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for OCR rendering")

    args = parser.parse_args()

    try:
        result = analyze_file(args.path, force_ocr=args.ocr, dpi=args.dpi)
        if args.json:
            print(json.dumps(result))
        else:
            print(f"Analyzed: {args.path}")
            for k, v in result["parsed"].items():
                print(f"{k}: {v}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
