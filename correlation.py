#!/usr/bin/env python3
"""Correlation Analyzer - Detects dangerous query combinations across sessions.

Tracks what each cloud service has seen and determines if routing a new query
there would create a dangerous correlation of information.
"""

import json
import os
import time
import urllib.request
import urllib.error

SESSIONS_DIR = "./logs/sessions"
DEFAULT_MODEL = "capybarahermes-2.5-mistral-7b.Q4_0:latest"
DEFAULT_OLLAMA_URL = "http://localhost:11434"

CORRELATION_SYSTEM_PROMPT = """You are a correlation analyzer. Given a new query, user profile, and what a cloud service has already seen, determine if routing this query there would create a dangerous combination.

Individual queries can look safe alone but reveal secrets when combined. Your job is to detect when a new query would COMPLETE A PICTURE.

DANGEROUS COMBINATIONS:
- Journalist: TOPIC + SPECIFIC LOCATION reveals where story is happening
- Journalist: SOURCE MENTION + TIME + PLACE reveals meeting details
- Lawyer: CLIENT HINTS + CASE DETAILS reveals privileged info
- Healthcare: CONDITION + DEMOGRAPHICS can identify patient
- Researcher: RESEARCH AREA + SPECIFIC NUMBERS reveals unpublished results

RESPOND WITH:
[Brief analysis]
Correlation Risk: [NONE / LOW / HIGH]
Recommendation: [SAFE for {service} / ROUTE TO LOCAL]

EXAMPLES:

Profile: Journalist
Claude has seen: ["senator financial disclosures", "Georgetown restaurants"]
New query: "What time does The Monocle close Tuesday?"

Claude has topic + general area. Adding specific venue + day completes source meeting picture.
Correlation Risk: HIGH
Recommendation: ROUTE TO LOCAL

Profile: Healthcare
Claude has seen: ["diabetes treatment protocols"]
New query: "Metformin side effects?"

General medical info + more general medical info. No patient identifiers.
Correlation Risk: NONE
Recommendation: SAFE for Claude"""


def _get_session_path(session_id):
    """Get the file path for a session's history."""
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")


def load_history(session_id):
    """Load session history from disk.

    Returns:
        dict with keys "claude", "openai", "gemini", each containing a list of query summaries
    """
    path = _get_session_path(session_id)

    if not os.path.exists(path):
        return {"claude": [], "openai": [], "gemini": []}

    try:
        with open(path, "r") as f:
            data = json.load(f)
            # Ensure all keys exist
            for key in ["claude", "openai", "gemini"]:
                if key not in data:
                    data[key] = []
            return data
    except (json.JSONDecodeError, OSError):
        return {"claude": [], "openai": [], "gemini": []}


def save_history(session_id, history):
    """Save session history to disk."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    path = _get_session_path(session_id)

    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def update_history(session_id, service, query_summary):
    """Add a query summary to a service's history.

    Args:
        session_id: The session identifier
        service: One of "claude", "openai", "gemini"
        query_summary: Brief summary of what the query was about
    """
    service = service.lower()
    if service not in ["claude", "openai", "gemini"]:
        raise ValueError(f"Invalid service: {service}")

    history = load_history(session_id)
    history[service].append(query_summary)
    save_history(session_id, history)


def clear_history(session_id):
    """Clear all history for a session."""
    path = _get_session_path(session_id)

    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def _heuristic_correlation_check(profile, service_history, query):
    """Fast keyword-based correlation check that catches obvious dangerous combos.

    Returns ("HIGH", reason_string) if a dangerous pattern is detected,
    or (None, None) if no heuristic match (fall through to LLM).
    """
    query_lower = query.lower()
    history_text = " ".join(service_history).lower()

    # Location-related keywords
    LOCATION_WORDS = [
        "restaurant", "cafe", "bar", "tavern", "hotel", "lobby", "park",
        "street", "avenue", "blvd", "plaza", "square", "station",
        "airport", "metro", "corner of", "near", "behind", "across from",
        "georgetown", "capitol", "pentagon", "downtown", "district",
    ]
    # Time-related keywords
    TIME_WORDS = [
        "monday", "tuesday", "wednesday", "thursday", "friday",
        "saturday", "sunday", "am", "pm", "noon", "midnight",
        "morning", "evening", "tonight", "tomorrow", "today",
        "what time", "close", "open", "hours",
    ]
    # Person-related keywords
    PERSON_WORDS = [
        "senator", "congressman", "representative", "official",
        "source", "contact", "informant", "whistleblower",
        "client", "patient", "mrn", "dob", "ssn",
    ]
    # Specific-venue keywords (names, proper nouns in queries)
    VENUE_WORDS = [
        "monocle", "blue duck", "fiola", "martin's", "old ebbitt",
        "café milano", "le diplomate",
    ]

    def _has_any(text, keywords):
        return any(kw in text for kw in keywords)

    profile_lower = profile.lower()

    if profile_lower == "journalist":
        # DANGEROUS: location/area in history + specific venue or time in new query (or vice versa)
        hist_has_location = _has_any(history_text, LOCATION_WORDS)
        hist_has_time = _has_any(history_text, TIME_WORDS)
        hist_has_person = _has_any(history_text, PERSON_WORDS)
        hist_has_venue = _has_any(history_text, VENUE_WORDS)

        query_has_location = _has_any(query_lower, LOCATION_WORDS)
        query_has_time = _has_any(query_lower, TIME_WORDS)
        query_has_person = _has_any(query_lower, PERSON_WORDS)
        query_has_venue = _has_any(query_lower, VENUE_WORDS)

        # Location + specific venue/time = source meeting picture
        if (hist_has_location or hist_has_venue) and (query_has_time or query_has_venue):
            return ("HIGH", "Location area in history + specific venue/time in query completes source meeting picture")
        if (query_has_location or query_has_venue) and (hist_has_time or hist_has_venue):
            return ("HIGH", "Time/venue in history + location in query completes source meeting picture")
        # Person + location/time = source identity exposure
        if hist_has_person and (query_has_location or query_has_time):
            return ("HIGH", "Person reference in history + location/time in query could expose source")
        if query_has_person and (hist_has_location or hist_has_time):
            return ("HIGH", "Location/time in history + person reference in query could expose source")

    elif profile_lower == "healthcare":
        # DANGEROUS: patient identifier + medical condition across queries
        hist_has_person = _has_any(history_text, PERSON_WORDS + ["patient", "name", "record"])
        query_has_person = _has_any(query_lower, PERSON_WORDS + ["patient", "name", "record"])
        MEDICAL_WORDS = ["diagnosis", "treatment", "symptom", "condition", "medication",
                         "prescription", "dosage", "prognosis", "surgery", "lab result"]
        hist_has_medical = _has_any(history_text, MEDICAL_WORDS)
        query_has_medical = _has_any(query_lower, MEDICAL_WORDS)

        if hist_has_person and query_has_medical:
            return ("HIGH", "Patient identifier in history + medical info in query violates HIPAA")
        if query_has_person and hist_has_medical:
            return ("HIGH", "Medical info in history + patient identifier in query violates HIPAA")

    elif profile_lower == "lawyer":
        # DANGEROUS: client info + case strategy across queries
        hist_has_person = _has_any(history_text, PERSON_WORDS + ["client", "plaintiff", "defendant"])
        query_has_person = _has_any(query_lower, PERSON_WORDS + ["client", "plaintiff", "defendant"])
        STRATEGY_WORDS = ["strategy", "settlement", "negotiate", "damages", "liability",
                          "evidence", "deposition", "filing", "motion", "discovery"]
        hist_has_strategy = _has_any(history_text, STRATEGY_WORDS)
        query_has_strategy = _has_any(query_lower, STRATEGY_WORDS)

        if hist_has_person and query_has_strategy:
            return ("HIGH", "Client info in history + case strategy in query exposes privileged info")
        if query_has_person and hist_has_strategy:
            return ("HIGH", "Case strategy in history + client info in query exposes privileged info")

    elif profile_lower == "researcher":
        # DANGEROUS: proprietary method + specific results across queries
        RESEARCH_WORDS = ["proprietary", "unpublished", "our model", "our method", "our approach",
                          "our results", "benchmark", "accuracy", "beats", "outperforms"]
        NUMBERS_WORDS = ["percent", "%", "score", "accuracy", "f1", "bleu", "mmlu"]

        hist_has_research = _has_any(history_text, RESEARCH_WORDS)
        query_has_research = _has_any(query_lower, RESEARCH_WORDS)
        hist_has_numbers = _has_any(history_text, NUMBERS_WORDS)
        query_has_numbers = _has_any(query_lower, NUMBERS_WORDS)

        if hist_has_research and query_has_numbers:
            return ("HIGH", "Proprietary research in history + specific metrics in query reveals unpublished results")
        if query_has_research and hist_has_numbers:
            return ("HIGH", "Metrics in history + proprietary research in query reveals unpublished results")

    return (None, None)


def check_correlation(profile, service, history, query, model=DEFAULT_MODEL, ollama_url=DEFAULT_OLLAMA_URL):
    """Check if routing a query to a service creates dangerous correlations.

    Uses a fast heuristic check first, then falls back to LLM analysis.

    Args:
        profile: User profile (Lawyer, Journalist, Healthcare, Researcher)
        service: Target cloud service (claude, openai, gemini)
        history: Session history dict from load_history()
        query: The new query to check
        model: Ollama model to use
        ollama_url: Ollama API base URL

    Returns:
        dict with keys:
            - risk: "NONE", "LOW", or "HIGH"
            - recommendation: "SAFE" or "LOCAL"
            - response: Full LLM response
            - duration_ms: Time taken
    """
    service = service.lower()
    service_history = history.get(service, [])

    # If no history for this service, no correlation possible
    if not service_history:
        return {
            "risk": "NONE",
            "recommendation": "SAFE",
            "response": "No prior queries to this service - no correlation possible.",
            "duration_ms": 0,
        }

    # --- Heuristic pre-check: catches obvious dangerous patterns instantly ---
    heuristic_risk, heuristic_reason = _heuristic_correlation_check(profile, service_history, query)
    if heuristic_risk == "HIGH":
        return {
            "risk": "HIGH",
            "recommendation": "LOCAL",
            "response": f"[Heuristic] {heuristic_reason}",
            "duration_ms": 0,
        }

    # --- LLM-based check for subtler correlations ---
    # Build the correlation check prompt
    service_display = service.capitalize()
    user_prompt = f"""Profile: {profile}
{service_display} has seen: {json.dumps(service_history)}
New query: "{query}"

Analyze whether routing this query to {service_display} would create a dangerous combination with what it has already seen."""

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": CORRELATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }).encode("utf-8")

    url = f"{ollama_url.rstrip('/')}/api/chat"

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.time()

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Could not reach Ollama at {ollama_url}. Is it running?\n  {e}"
        )
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"Ollama returned HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}"
        )

    elapsed_ms = int((time.time() - start) * 1000)
    content = body.get("message", {}).get("content", "No response from model")

    # Parse risk level from response
    risk = "NONE"
    recommendation = "SAFE"

    content_upper = content.upper()
    if "CORRELATION RISK: HIGH" in content_upper or "RISK: HIGH" in content_upper:
        risk = "HIGH"
        recommendation = "LOCAL"
    elif "CORRELATION RISK: LOW" in content_upper or "RISK: LOW" in content_upper:
        risk = "LOW"
        recommendation = "SAFE"
    elif "CORRELATION RISK: NONE" in content_upper or "RISK: NONE" in content_upper:
        risk = "NONE"
        recommendation = "SAFE"

    # Also check for explicit routing recommendation
    if "ROUTE TO LOCAL" in content_upper:
        recommendation = "LOCAL"
    elif f"SAFE FOR {service.upper()}" in content_upper:
        recommendation = "SAFE"

    return {
        "risk": risk,
        "recommendation": recommendation,
        "response": content,
        "duration_ms": elapsed_ms,
    }


def summarize_query(query):
    """Create a brief summary of a query for history storage.

    For simplicity, we just use the first 100 chars. In production,
    you might want to use an LLM to create semantic summaries.
    """
    # Simple approach: truncate and clean
    summary = query.strip()
    if len(summary) > 100:
        summary = summary[:97] + "..."
    return summary


def format_history(history):
    """Format history for display."""
    lines = []
    for service in ["claude", "openai", "gemini"]:
        queries = history.get(service, [])
        lines.append(f"{service.upper()}: {len(queries)} queries")
        for i, q in enumerate(queries, 1):
            lines.append(f"  {i}. {q}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Simple test
    import argparse

    parser = argparse.ArgumentParser(description="Correlation analyzer test")
    parser.add_argument("--session", "-s", required=True, help="Session ID")
    parser.add_argument("--action", "-a", choices=["show", "clear", "check", "add"], required=True)
    parser.add_argument("--service", help="Service name (for add/check)")
    parser.add_argument("--query", "-q", help="Query (for check/add)")
    parser.add_argument("--profile", "-p", help="Profile (for check)")

    args = parser.parse_args()

    if args.action == "show":
        history = load_history(args.session)
        print(format_history(history))

    elif args.action == "clear":
        if clear_history(args.session):
            print(f"Cleared history for session: {args.session}")
        else:
            print(f"No history found for session: {args.session}")

    elif args.action == "add":
        if not args.service or not args.query:
            print("Error: --service and --query required for add")
        else:
            update_history(args.session, args.service, summarize_query(args.query))
            print(f"Added query to {args.service} history")

    elif args.action == "check":
        if not args.service or not args.query or not args.profile:
            print("Error: --service, --query, and --profile required for check")
        else:
            history = load_history(args.session)
            result = check_correlation(args.profile, args.service, history, args.query)
            print(f"Risk: {result['risk']}")
            print(f"Recommendation: {result['recommendation']}")
            print(f"Duration: {result['duration_ms']}ms")
            print("---")
            print(result['response'])
