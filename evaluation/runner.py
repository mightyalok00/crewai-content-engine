from __future__ import annotations

import json
from pathlib import Path

from models import ContentEvaluationReport, VerificationReport
from .scorers import score_package

def evaluate_package(content: str, verification: VerificationReport | None = None, *, minimum_score: float = 0.80) -> ContentEvaluationReport:
    scores = score_package(content, verification)
    weighted = {"evidence_coverage": 0.30, "verification": 0.30, "structure": 0.20, "code_quality": 0.20}
    overall = sum(score.value * weighted[score.name] for score in scores)
    notes = [note for score in scores for note in score.notes]
    return ContentEvaluationReport(overall=round(overall, 3), passed=overall >= minimum_score and not any(note in notes for note in ("unsupported_claims_present", "verification_report_missing")), scores={score.name: score.value for score in scores}, notes=notes)

def evaluate_file(content_path: str | Path, verification_path: str | Path | None = None, output_path: str | Path | None = None, *, minimum_score: float = 0.80) -> ContentEvaluationReport:
    content = Path(content_path).read_text(encoding="utf-8")
    verification = None
    if verification_path:
        verification = VerificationReport.model_validate_json(Path(verification_path).read_text(encoding="utf-8"))
    report = evaluate_package(content, verification, minimum_score=minimum_score)
    if output_path:
        Path(output_path).write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
    return report
