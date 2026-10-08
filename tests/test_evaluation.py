from models import Evidence, VerificationReport
from evaluation.runner import evaluate_package

def _verification(score=0.95, unsupported=None):
    return VerificationReport(
        verified_claims=[Evidence(claim="CrewAI uses agents", source="official documentation", confidence=score)],
        unsupported_claims=unsupported or [],
        score=score,
    )

def _article():
    return "# Technical Guide\n\n## Overview\n\nUseful context.\n\n## Architecture\n\nMore detail.\n\n## Example\n\nImplementation guidance.\n\n## Conclusion\n\nActionable takeaway."

def test_evaluation_passes_high_quality_package():
    report = evaluate_package(_article(), _verification())
    assert report.passed is True
    assert report.overall >= 0.80
    assert report.scores["evidence_coverage"] >= 0.90

def test_evaluation_blocks_missing_verification():
    report = evaluate_package(_article(), None)
    assert report.passed is False
    assert "verification_report_missing" in report.notes

def test_evaluation_penalizes_unsupported_claims():
    report = evaluate_package(_article(), _verification(unsupported=["claim"]))
    assert report.passed is False
    assert "unsupported_claims_present" in report.notes

def test_code_blocks_require_language_and_content():
    article = _article() + "\n\n```python\nprint('ok')\n```"
    report = evaluate_package(article, _verification())
    assert report.scores["code_quality"] == 1.0
