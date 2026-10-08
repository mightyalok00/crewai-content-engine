from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    claim: str = Field(min_length=1)
    source: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""

class ResearchBrief(BaseModel):
    topic: str = Field(min_length=1)
    source_url: str | None = None
    summary: str = ""
    key_claims: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)

class VerificationReport(BaseModel):
    verified_claims: list[Evidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    score: float = Field(default=0.0, ge=0.0, le=1.0)

class ContentQualityReport(BaseModel):
    factuality: float = Field(ge=0.0, le=1.0)
    source_quality: float = Field(ge=0.0, le=1.0)
    readability: float = Field(ge=0.0, le=1.0)
    seo: float = Field(ge=0.0, le=1.0)
    code_quality: float = Field(ge=0.0, le=1.0)
    overall: float = Field(ge=0.0, le=1.0)
    passed: bool
    blockers: list[str] = Field(default_factory=list)
    evaluation: "ContentEvaluationReport | None" = None

class ContentEvaluationReport(BaseModel):
    overall: float = Field(ge=0.0, le=1.0)
    passed: bool
    scores: dict[str, float] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)

class ArtifactManifest(BaseModel):
    job_id: str
    topic: str
    status: Literal["queued", "running", "completed", "failed"]
    files: dict[str, str] = Field(default_factory=dict)
