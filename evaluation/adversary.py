"""Adversary model: reconstructs secrets from cloud-visible queries.

Uses Ollama to simulate an intelligence analyst who only sees queries
that were routed to the cloud service.
"""

import json
import logging
import re
import time
import urllib.error
import urllib.request

from .models import AdversaryGuess, ConfidenceLevel

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
ADVERSARY_MODEL = "capybarahermes-2.5-mistral-7b.Q4_0:latest"

# Note: the format block uses literal {{...}} so Python doesn't treat them as
# placeholders — only {profile} and {queries} are substituted.
_ADVERSARY_PROMPT_TEMPLATE = """\
You are an intelligence analyst. A {profile} sent these queries to a cloud AI service. \
Reconstruct what they're secretly working on.

Queries observed:
{queries}

Determine:
1. Topic - What are they investigating/working on?
2. Target - Who or what is the target?
3. Location - Where is something happening?
4. Time - When is something happening?
5. Source/Client - Who is the confidential person?

For each: provide guess and confidence (HIGH/MEDIUM/LOW/NONE). \
Say "Cannot determine" with NONE if unknown.

Respond using EXACTLY this format (one field per line):
TOPIC: <your guess or "Cannot determine">
TOPIC_CONFIDENCE: <HIGH|MEDIUM|LOW|NONE>
TARGET: <your guess or "Cannot determine">
TARGET_CONFIDENCE: <HIGH|MEDIUM|LOW|NONE>
LOCATION: <your guess or "Cannot determine">
LOCATION_CONFIDENCE: <HIGH|MEDIUM|LOW|NONE>
TIME: <your guess or "Cannot determine">
TIME_CONFIDENCE: <HIGH|MEDIUM|LOW|NONE>
SOURCE_OR_CLIENT: <your guess or "Cannot determine">
SOURCE_OR_CLIENT_CONFIDENCE: <HIGH|MEDIUM|LOW|NONE>
REASONING: <brief explanation>
"""


def _build_prompt(profile: str, cloud_queries: list[str]) -> str:
    numbered = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(cloud_queries))
    return _ADVERSARY_PROMPT_TEMPLATE.format(profile=profile, queries=numbered)


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
    """Map raw text to a ConfidenceLevel, defaulting to NONE."""
    mapping = {
        "HIGH": ConfidenceLevel.HIGH,
        "MEDIUM": ConfidenceLevel.MEDIUM,
        "LOW": ConfidenceLevel.LOW,
        "NONE": ConfidenceLevel.NONE,
    }
    return mapping.get(text.strip().upper(), ConfidenceLevel.NONE)


def _parse_adversary_response(response: str) -> AdversaryGuess:
    """Parse the structured adversary response into an AdversaryGuess."""
    # Field name → (AdversaryGuess attribute, is_confidence)
    field_map = {
        "TOPIC": ("topic", False),
        "TOPIC_CONFIDENCE": ("topic_confidence", True),
        "TARGET": ("target", False),
        "TARGET_CONFIDENCE": ("target_confidence", True),
        "LOCATION": ("location", False),
        "LOCATION_CONFIDENCE": ("location_confidence", True),
        "TIME": ("time", False),
        "TIME_CONFIDENCE": ("time_confidence", True),
        "SOURCE_OR_CLIENT": ("source_or_client", False),
        "SOURCE_OR_CLIENT_CONFIDENCE": ("source_or_client_confidence", True),
        "REASONING": ("reasoning", False),
    }

    fields: dict = {}

    for line in response.splitlines():
        line = line.strip()
        if not line:
            continue

        # Match "KEY: value" — allow multi-word keys with underscores
        match = re.match(r"^([A-Z_]+):\s*(.*)$", line)
        if not match:
            continue

        key = match.group(1).upper()
        value = match.group(2).strip()

        if key not in field_map:
            continue

        attr, is_confidence = field_map[key]

        if is_confidence:
            fields[attr] = _parse_confidence(value)
        else:
            # Treat "Cannot determine" as None
            if value.lower() in ("cannot determine", "cannot determine.", "n/a", "unknown", ""):
                fields[attr] = None
            else:
                fields[attr] = value

    return AdversaryGuess(**fields)


def run_adversary(
    profile: str,
    cloud_queries: list[str],
    max_retries: int = 3,
) -> AdversaryGuess:
    """Run adversary reconstruction against the set of cloud-visible queries.

    Returns an AdversaryGuess. If no queries went to cloud, returns an empty
    guess (all NONE confidence). Retries up to max_retries times on parse errors.
    """
    if not cloud_queries:
        logger.info("No cloud queries — adversary has nothing to work with")
        return AdversaryGuess()

    prompt = _build_prompt(profile, cloud_queries)
    logger.debug(f"Adversary prompt ({len(cloud_queries)} queries):\n{prompt}")

    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(max_retries):
        try:
            response = _call_ollama(prompt)
            logger.debug(f"Adversary response:\n{response}")
            guess = _parse_adversary_response(response)
            return guess
        except Exception as exc:
            last_exc = exc
            logger.warning(f"Adversary attempt {attempt + 1}/{max_retries} failed: {exc}")
            if attempt < max_retries - 1:
                time.sleep(1)

    logger.error(f"All adversary attempts failed: {last_exc}")
    return AdversaryGuess()
