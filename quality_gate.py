from __future__ import annotations

import re

from evaluation.runner import evaluate_package
from models import ContentQualityReport, VerificationReport


def evaluate_quality(
    content: str,
    verification: VerificationReport | None = None,
    *,
    minimum_score: float = 0.80,
) -> ContentQualityReport:
    text = content.strip()
    words = re.findall(r"\b\w+\b", text)
    headings = len(re.findall(r"^#{1,3}\s+", text, flags=re.MULTILINE))
    code_blocks = len(re.findall(r"```", text)) // 2
    has_title = bool(re.search(r"^#\s+\S+", text, flags=re.MULTILINE))
    word_count = len(words)

    factuality = verification.score if verification else 0.70
    source_quality = (
        sum(item.confidence for item in verification.verified_claims)
        / len(verification.verified_claims)
        if verification and verification.verified_claims
        else 0.65
    )
    readability = min(1.0, 0.55 + min(word_count, 2500) / 5000 + min(headings, 8) * 0.03)
    seo = min(1.0, 0.55 + (0.12 if has_title else 0) + min(headings, 8) * 0.04)
    code_quality = 0.90 if code_blocks == 0 else min(1.0, 0.65 + min(code_blocks, 6) * 0.05)

    blockers = []
    if word_count < 250:
        blockers.append("content_too_short")
    if not has_title:
        blockers.append("missing_h1")
    if verification and verification.unsupported_claims:
        blockers.append("unsupported_claims_present")

    legacy_overall = (
        0.30 * factuality
        + 0.20 * source_quality
        + 0.20 * readability
        + 0.15 * seo
        + 0.15 * code_quality
    )

    evaluation = evaluate_package(text, verification, minimum_score=minimum_score)
    overall = round(0.70 * legacy_overall + 0.30 * evaluation.overall, 3)
    blockers.extend(note for note in evaluation.notes if note not in blockers)

    return ContentQualityReport(
        factuality=round(factuality, 3),
        source_quality=round(source_quality, 3),
        readability=round(readability, 3),
        seo=round(seo, 3),
        code_quality=round(code_quality, 3),
        overall=overall,
        passed=overall >= minimum_score and not blockers,
        blockers=blockers,
        evaluation=evaluation,
    )
