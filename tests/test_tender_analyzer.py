import sys
import pathlib

# Ensure the repository root is on sys.path so the module can be imported during tests
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tender_analyzer import parse_tender_text


def test_parse_basic_fields():
    sample = """
    Tender Title: Construction of New Bridge
    Reference: TB-2025-00123
    Issuing Organization: City Public Works Department
    Closing Date: 30 September 2025
    """
    parsed = parse_tender_text(sample)
    assert parsed["title"] == "Construction of New Bridge"
    assert parsed["reference"] == "TB-2025-00123"
    assert parsed["organization"] == "City Public Works Department"
    assert "30 September 2025" in parsed["closing_date"]
