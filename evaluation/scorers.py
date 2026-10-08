from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from models import Evidence, VerificationReport


@dataclass(frozen=True)
class Score:
    name: str
    value: float
    notes: tuple[str, ...] = ()


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 3)))


def score_evidence(evidence: Iterable[Evidence]) -> Score:
    items = list(evidence)
    if not items:
        return Score("evidence_coverage", 0.0, ("no_evidence_records",))
    source_bonus = sum(bool(item.source.strip()) for item in items) / len(items)
    confidence = sum(item.confidence for item in items) / len(items)
    return Score("evidence_coverage", _clamp(0.7 * confidence + 0.3 * source_bonus))


def score_structure(content: str) -> Score:
    headings = re.findall(r"^#{1,3}\s+.+$", content, flags=re.MULTILINE)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    checks = [
        (bool(re.search(r"^#\s+\S+", content, re.MULTILINE)), "missing_h1"),
        (len(headings) >= 3, "few_headings"),
        (len(paragraphs) >= 5, "few_sections"),
    ]
    value = sum(ok for ok, _ in checks) / len(checks)
    return Score("structure", _clamp(value), tuple(note for ok, note in checks if not ok))


def score_code_blocks(content: str) -> Score:
    fence = chr(96) * 3
    blocks = re.findall(re.escape(fence) + r"([\w+-]*)\n(.*?)" + re.escape(fence), content, flags=re.DOTALL)
    if not blocks:
        return Score("code_quality", 1.0)
    language_coverage = sum(bool(lang.strip()) for lang, _ in blocks) / len(blocks)
    non_empty = sum(bool(body.strip()) for _, body in blocks) / len(blocks)
    return Score("code_quality", _clamp(0.6 * language_coverage + 0.4 * non_empty))


def score_verification(verification: VerificationReport | None) -> Score:
    if verification is None:
        return Score("verification", 0.0, ("verification_report_missing",))
    notes = []
    if verification.unsupported_claims:
        notes.append("unsupported_claims_present")
    if verification.warnings:
        notes.append("verification_warnings_present")
    penalty = min(0.4, 0.1 * len(verification.unsupported_claims) + 0.03 * len(verification.warnings))
    return Score("verification", _clamp(verification.score - penalty), tuple(notes))


def score_package(content: str, verification: VerificationReport | None = None) -> list[Score]:
    evidence = verification.verified_claims if verification else []
    return [
        score_evidence(evidence),
        score_verification(verification),
        score_structure(content),
        score_code_blocks(content),
    ]
