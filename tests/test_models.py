from pydantic import ValidationError
from models import ContentQualityReport, Evidence

def test_evidence_validates_confidence():
    assert Evidence(claim="x", source="docs", confidence=0.8).confidence == 0.8

def test_quality_report_rejects_invalid_score():
    try:
        ContentQualityReport(factuality=2, source_quality=0, readability=0, seo=0, code_quality=0, overall=0, passed=False)
    except ValidationError:
        return
    raise AssertionError("Expected Pydantic validation error")