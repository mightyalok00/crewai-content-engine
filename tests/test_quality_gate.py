from models import Evidence, VerificationReport
from quality_gate import evaluate_quality

def test_quality_gate_passes_well_formed_article():
    content = "# A Useful Guide\n\n" + ("This is useful technical context. " * 100)
    report = evaluate_quality(content, VerificationReport(verified_claims=[Evidence(claim="example", source="official documentation", confidence=0.95)], score=0.95))
    assert report.overall >= 0.80
    assert report.passed is True

def test_quality_gate_blocks_missing_title():
    report = evaluate_quality("short")
    assert report.passed is False
    assert "content_too_short" in report.blockers
    assert "missing_h1" in report.blockers