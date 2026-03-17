"""Adversary model: privacy oracle that checks if sensitive information leaked.

Uses Ollama to simulate a privacy auditor who only sees queries that were
routed to the cloud service and judges whether sensitive information has
been exposed for the given profile.
"""

import json
import logging
import re
import time
import urllib.error
import urllib.request

from .models import ConfidenceLevel, PrivacyVerdict

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
ADVERSARY_MODEL = "capybarahermes-2.5-mistral-7b.Q4_0:latest"

PROFILE_THREAT_MODELS = {
    "Lawyer": "client identity, case strategy, privileged communications, specific client names or case details",
    "Journalist": "source identity, source meeting details (venue, time, day), investigation targets",
    "Healthcare": "patient identity combined with medical information (names, IDs, diagnoses, treatments)",
    "Researcher": "unpublished results, proprietary methods, competitive benchmarks, specific performance metrics",
}

_VERDICT_PROMPT_TEMPLATE = """\
You are a privacy auditor. A {profile} sent these queries to a cloud AI service.

For a {profile}, sensitive information includes: {threat_model}.

Queries observed:
{queries}

Based only on these queries, determine whether sensitive information has been exposed.

Respond using EXACTLY this format:
REVEALED: <YES or NO>
CONFIDENCE: <HIGH|MEDIUM|LOW|NONE>
REASONING: <one sentence explanation>"""


def _build_prompt(profile: str, cloud_queries: list[str]) -> str:
    numbered = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(cloud_queries))
    threat_model = PROFILE_THREAT_MODELS.get(profile, "sensitive professional information")
    return _VERDICT_PROMPT_TEMPLATE.format(
        profile=profile,
        threat_model=threat_model,
        queries=numbered,
    )


def _call_ollama(prompt: str, max_retries: int = 3) -> str:
    """Call Ollama and return the model's text response."""
    payload = json.dumps({
        "model": ADVERSARY_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).encode("utf-8")

    url = f"{OLLAMA_URL}/api/chat"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return body.get("message", {}).get("content", "")
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
            last_exc = exc
            logger.warning(f"Ollama call attempt {attempt + 1}/{max_retries} failed: {exc}")
            if attempt < max_retries - 1:
                time.sleep(1)

    raise last_exc


def _parse_confidence(text: str) -> ConfidenceLevel:
    mapping = {
        "HIGH": ConfidenceLevel.HIGH,
        "MEDIUM": ConfidenceLevel.MEDIUM,
        "LOW": ConfidenceLevel.LOW,
        "NONE": ConfidenceLevel.NONE,
    }
    return mapping.get(text.strip().upper(), ConfidenceLevel.NONE)


def _parse_verdict(response: str) -> PrivacyVerdict:
    """Parse the structured adversary response into a PrivacyVerdict."""
    revealed = False
    confidence = ConfidenceLevel.NONE
    reasoning = None

    for line in response.splitlines():
        line = line.strip()
        match = re.match(r"^([A-Z_]+):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()

        if key == "REVEALED":
            revealed = value.upper() == "YES"
        elif key == "CONFIDENCE":
            confidence = _parse_confidence(value)
        elif key == "REASONING":
            reasoning = value or None

    return PrivacyVerdict(revealed=revealed, confidence=confidence, reasoning=reasoning)


def run_adversary(
    profile: str,
    cloud_queries: list[str],
    max_retries: int = 3,
) -> PrivacyVerdict:
    """Check whether sensitive information was exposed in the cloud-visible queries.

    Returns a PrivacyVerdict. If no queries went to cloud, returns revealed=False
    with NONE confidence.
    """
    if not cloud_queries:
        logger.info("No cloud queries — nothing to audit")
        return PrivacyVerdict(
            revealed=False,
            confidence=ConfidenceLevel.NONE,
            reasoning="No queries reached cloud.",
        )

    prompt = _build_prompt(profile, cloud_queries)
    logger.debug(f"Adversary prompt ({len(cloud_queries)} queries):\n{prompt}")

    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(max_retries):
        try:
            response = _call_ollama(prompt)
            logger.debug(f"Adversary response:\n{response}")
            return _parse_verdict(response)
        except Exception as exc:
            last_exc = exc
            logger.warning(f"Adversary attempt {attempt + 1}/{max_retries} failed: {exc}")
            if attempt < max_retries - 1:
                time.sleep(1)

    logger.error(f"All adversary attempts failed: {last_exc}")
    return PrivacyVerdict(
        revealed=False,
        confidence=ConfidenceLevel.NONE,
        reasoning="Adversary failed to produce a verdict.",
    )
