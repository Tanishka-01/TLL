"""Routing strategies for adversary simulation.

Three methods:
- always_cloud: all queries go to cloud
- threshold_router: keyword-based local/cloud split
- tll_router: full TLL pipeline via tll.py
"""

import logging
import re
import subprocess
from pathlib import Path

from .models import RoutingResult

logger = logging.getLogger(__name__)

# Path to tll.py and correlation.py (one level up from evaluation/)
TLL_DIR = Path(__file__).parent.parent
TLL_SCRIPT = TLL_DIR / "tll.py"
CORRELATION_SCRIPT = TLL_DIR / "correlation.py"

# Keywords that trigger LOCAL routing in the threshold strategy
THRESHOLD_KEYWORDS = [
    "source",
    "patient",
    "client",
    "confidential",
    "leaked",
    "secret",
    "my client",
    "my patient",
    "my source",
]

CLOUD_SERVICES = {"claude", "openai", "gemini"}


def always_cloud(queries: list[str]) -> RoutingResult:
    """Route all queries to cloud."""
    return RoutingResult(
        method="always_cloud",
        queries_to_cloud=list(queries),
        queries_to_local=[],
    )


def threshold_router(queries: list[str], profile: str) -> RoutingResult:
    """Keyword-based routing: sensitive keywords → LOCAL, otherwise → CLOUD."""
    cloud: list[str] = []
    local: list[str] = []

    for query in queries:
        q_lower = query.lower()
        if any(kw in q_lower for kw in THRESHOLD_KEYWORDS):
            local.append(query)
        else:
            cloud.append(query)

    return RoutingResult(
        method="threshold",
        queries_to_cloud=cloud,
        queries_to_local=local,
    )


def tll_router(queries: list[str], profile: str, session_id: str) -> RoutingResult:
    """Full TLL routing via tll.py directly.

    Clears the session first, then runs each query through TLL and
    parses the FINAL ROUTING decision from stdout.
    """
    # Clear session history before starting
    clear_result = subprocess.run(
        ["python3", str(CORRELATION_SCRIPT), "--session", session_id, "--action", "clear"],
        cwd=str(TLL_DIR),
        capture_output=True,
        text=True,
    )
    logger.debug(f"Session clear: {clear_result.stdout.strip()}")

    cloud: list[str] = []
    local: list[str] = []
    scores_cloud: dict[str, float] = {}
    scores_local: dict[str, float] = {}

    for query in queries:
        try:
            result = subprocess.run(
                [
                    "python3", str(TLL_SCRIPT),
                    "--profile", profile,
                    "--query", query,
                    "--session", session_id,
                ],
                cwd=str(TLL_DIR),
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"TLL timeout for query: {query!r} — defaulting to LOCAL")
            local.append(query)
            continue

        output = result.stdout
        logger.debug(f"TLL output for {query!r}:\n{output}")

        decision = _parse_final_routing(output)
        score = _parse_sensitivity_score(output)
        logger.info(f"  [{decision.upper()}] sensitivity={score} {query!r}")

        if decision in CLOUD_SERVICES:
            cloud.append(query)
            if score is not None:
                scores_cloud[query] = score
        else:
            local.append(query)
            if score is not None:
                scores_local[query] = score

    return RoutingResult(
        method="tll",
        queries_to_cloud=cloud,
        queries_to_local=local,
        sensitivity_scores_cloud=scores_cloud,
        sensitivity_scores_local=scores_local,
    )


def _parse_final_routing(output: str) -> str:
    """Extract the routing decision from tll.py stdout.

    Matches 'Route: LOCAL/CLOUD/...' (current tll.py output format).
    Returns a lowercase service name: 'local', 'claude', 'openai', 'gemini'.
    Defaults to 'local' if not found.
    """
    for line in output.splitlines():
        if line.startswith("Route:"):
            decision = line.split("Route:", 1)[1].strip().lower()
            decision = decision.split()[0] if decision else "local"
            return decision
    return "local"


def _parse_sensitivity_score(output: str) -> float | None:
    """Extract the sensitivity score from TLL stdout.

    Looks for 'Sensitivity: [score]' anywhere in the output.
    Returns a float in [0.0, 1.0] or None if not found.
    """
    match = re.search(r"Sensitivity:\s*([\d.]+)", output)
    if match:
        try:
            score = float(match.group(1))
            return max(0.0, min(1.0, score))
        except ValueError:
            return None
    return None
