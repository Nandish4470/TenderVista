# Tender Analyzer Utility

This small utility extracts text from tender PDF documents and attempts to parse common fields such as title, reference ID, issuing organization, and closing date.

Files added:
- `tender_analyzer.py` - main script
- `requirements.txt` - Python dependencies
- `tests/test_tender_analyzer.py` - unit tests for the parser

## Quick start

1. Create a virtual environment and install dependencies:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. Install system dependencies for Tesseract OCR (required for OCR fallback):

    - Debian/Ubuntu: `sudo apt-get install tesseract-ocr`
    - macOS (Homebrew): `brew install tesseract`

3. Run the analyzer on a PDF:

    ```bash
    python tender_analyzer.py path/to/tender.pdf
    ```

4. Run tests:

    ```bash
    pip install pytest
    pytest -q
    ```

## Assumptions and edge cases

- The parser is heuristic and may not correctly identify fields in all tender formats.
- OCR fallback requires `tesseract` to be installed and accessible in `PATH`.
- Large PDFs will be processed page-by-page; for very large files increase memory/dpi handling or pre-split.

## Next steps (optional)

- Add more robust date parsing and normalization.
- Use ML-based layout parsing for more accurate field extraction (e.g., LayoutLM or Google Document AI).
- Integrate into the existing TenderVista backend service.
