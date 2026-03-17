"""Pydantic models for the adversary simulation framework."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class PrivacyVerdict(BaseModel):
    """Adversary verdict: did sensitive information leak in the cloud-visible queries?"""
    revealed: bool
    confidence: ConfidenceLevel
    reasoning: Optional[str] = None
