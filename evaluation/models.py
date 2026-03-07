"""Pydantic models for the adversary simulation framework."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Secret(BaseModel):
    topic: Optional[str] = None
    target: Optional[str] = None
    location: Optional[str] = None
    time: Optional[str] = None
    source_or_client: Optional[str] = None


class Scenario(BaseModel):
    id: str
    profile: str
    description: str
    secret: Secret
    queries: list[str]


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class AdversaryGuess(BaseModel):
    topic: Optional[str] = None
    topic_confidence: ConfidenceLevel = ConfidenceLevel.NONE
    target: Optional[str] = None
    target_confidence: ConfidenceLevel = ConfidenceLevel.NONE
    location: Optional[str] = None
    location_confidence: ConfidenceLevel = ConfidenceLevel.NONE
    time: Optional[str] = None
    time_confidence: ConfidenceLevel = ConfidenceLevel.NONE
    source_or_client: Optional[str] = None
    source_or_client_confidence: ConfidenceLevel = ConfidenceLevel.NONE
    reasoning: Optional[str] = None


class RoutingResult(BaseModel):
    method: str
    queries_to_cloud: list[str]
    queries_to_local: list[str]
    # Sensitivity score (0.0–1.0) per query, populated by tll_router only
    sensitivity_scores_cloud: dict[str, float] = Field(default_factory=dict)
    sensitivity_scores_local: dict[str, float] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    scenario_id: str
    profile: str
    method: str
    queries_sent_to_cloud: int
    queries_kept_local: int
    adversary_guess: AdversaryGuess
    reconstruction_score: float
    avg_sensitivity_local: Optional[float] = None
    avg_sensitivity_cloud: Optional[float] = None
