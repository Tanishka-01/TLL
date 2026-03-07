#!/usr/bin/env python3
"""Tight-Lipped Layer (TLL) - Privacy-aware routing simulator.

Routes queries to the appropriate AI service based on privacy sensitivity
and user profile. Uses a local Ollama model for routing decisions.

Usage:
    python3 tll.py --profile Lawyer --query "My client is suing Google"
    python3 tll.py --profile Healthcare --query "Patient John Smith, MRN-4521..."
    python3 tll.py --profile Journalist --query "Meeting my source at 6pm"
    python3 tll.py --profile Researcher --query "Our new model beats GPT-4 by 12%"
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

from correlation import (
    load_history,
    update_history,
    check_correlation,
    summarize_query,
    format_history,
    clear_history,
)

TLL_SYSTEM_PROMPT = """You are the Tight-Lipped Layer, a privacy-aware routing advisor.

Given a user's query and their profile, decide which AI service should handle it and explain why.

CORE PRINCIPLE: Privacy sensitivity is RELATIVE, not absolute. The same information carries different risk depending on who is asking. A journalist asking "meeting at 6pm" is protecting a source. A healthcare worker asking the same is just planning dinner. Think: If an adversary saw this query, could they harm THIS specific user given their profile?

CRITICAL RULE: If the query contains ANY sensitive information for this profile, you MUST route to LOCAL. No cloud service — no matter how strong its privacy policy — is acceptable for sensitive data. Cloud services can be subpoenaed, breached, or logged. LOCAL is the ONLY option that guarantees zero data exposure. Only route to a cloud service (Claude, OpenAI, Gemini) when the query is clearly non-sensitive for this profile.

AVAILABLE SERVICES:

LOCAL - Your device, perfect privacy, good capability. ALWAYS use this when information is sensitive for this profile. This is the default for anything containing protected data.

CLAUDE - Anthropic's service, strong privacy, excellent capability. ONLY for non-sensitive queries. Block if query is adversarial to Anthropic.

OPENAI - OpenAI/Microsoft service, good privacy, excellent capability. ONLY for non-sensitive queries. Block if query is adversarial to OpenAI or Microsoft.

GEMINI - Google/Alphabet service, moderate privacy, good capability. ONLY for non-sensitive queries. Block if query is adversarial to Google or Alphabet.

PROFILE THREAT MODELS:

Each profile has different things they protect. The same information can be critical for one profile and meaningless for another.

Lawyer - Protects client identity, case strategy, privileged communications. If ANY client name, case detail, or legal strategy is mentioned → sensitive → LOCAL. General legal research (e.g., "what is an NDA") is not sensitive.

Journalist - Protects source identity, source meetings, investigation targets. If ANY source, meeting detail, or investigation target is mentioned → sensitive → LOCAL. General research (e.g., "how does FOIA work") is not sensitive.

Healthcare - Protects patient identity combined with medical info (HIPAA). If ANY patient name, ID, or identifiable medical record appears → sensitive → LOCAL. This is a legal requirement, not a preference. General medical questions (e.g., "treatment for diabetes") are not sensitive.

Researcher - Protects proprietary methods, unpublished results, competitive benchmarks. If ANY unpublished data, proprietary method, or competitive benchmark appears → sensitive → LOCAL. Public knowledge (e.g., "how do transformers work") is not sensitive.

CONFLICT DETECTION:

If the query is adversarial to a company, block that company's service. Adversarial means: lawsuits against them, investigating them, competing with them, criticizing them.

Google/Alphabet → Block Gemini
Anthropic → Block Claude
OpenAI/Microsoft → Block OpenAI

YOUR RESPONSE:

Think through the query naturally. Explain what information is present, whether it's sensitive for THIS profile and why, note any service conflicts, then give your routing decision. Be conversational, like a privacy advisor explaining to a colleague. End with a clear "Route to [SERVICE]" statement. Remember: if sensitive, ALWAYS route to LOCAL.

End your response with:
Reason: [one sentence explaining the routing decision]
Sensitivity: [one sentence describing how sensitive this query is for this profile and why]"""

VALID_PROFILES = ["Lawyer", "Journalist", "Healthcare", "Researcher"]
CLOUD_SERVICES = ["claude", "openai", "gemini"]

DEFAULT_MODEL = "capybarahermes-2.5-mistral-7b.Q4_0:latest"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
ROUTING_LOG_PATH = "./logs/routing.log"


def extract_routing_decision(response):
    """Extract the routing decision from TLL response.

    Looks for patterns like "Route to LOCAL", "recommended_route: claude", etc.
    Returns lowercase service name or None if not found.
    """
    VALID_SERVICES = {"local", "claude", "openai", "gemini"}
    # Map common aliases the model produces
    SERVICE_ALIASES = {
        "edge": "local",
        "device": "local",
        "on-device": "local",
        "ollama": "local",
        "anthropic": "claude",
        "gpt": "openai",
        "gpt-4": "openai",
        "chatgpt": "openai",
        "google": "gemini",
        "bard": "gemini",
    }

    response_lower = response.lower()

    # Try multiple patterns in priority order
    patterns = [
        r"route\s+to\s+(\w[\w-]*)",            # "Route to LOCAL"
        r"recommended_route:\s*(\w[\w-]*)",     # "recommended_route: local"
        r"final\s+route:\s*(\w[\w-]*)",         # "final route: claude"
        r"routing\s+decision:\s*(\w[\w-]*)",    # "routing decision: local"
        r"recommend\s+routing\s+to\s+(\w[\w-]*)",  # "recommend routing to..."
        r"should\s+be\s+routed?\s+to\s+(\w[\w-]*)",  # "should be routed to..."
        r"route:\s*(\w[\w-]*)",                 # "route: local"
    ]

    for pattern in patterns:
        match = re.search(pattern, response_lower)
        if match:
            service = match.group(1).strip("-").lower()
            if service in VALID_SERVICES:
                return service
            if service in SERVICE_ALIASES:
                return SERVICE_ALIASES[service]

    # Fallback: check last 150 chars for a valid service name
    last_150 = response_lower[-150:] if len(response_lower) > 150 else response_lower
    for service in ["local", "claude", "openai", "gemini"]:
        if service in last_150:
            return service

    # If nothing matched, default to local (safe fallback)
    return "local"


def extract_sensitivity(response: str) -> str:
    """Extract the natural language sensitivity description from a TLL response."""
    match = re.search(r"Sensitivity:\s*(.+)", response)
    if match:
        return match.group(1).strip()
    return ""


def extract_reason(response: str) -> str:
    """Extract the one-line reason from a TLL response."""
    match = re.search(r"Reason:\s*(.+)", response)
    if match:
        return match.group(1).strip()
    return ""


DEFAULT_SESSION = "default"


def validate_profile(profile):
    """Case-insensitive profile validation. Returns the canonical form."""
    for valid in VALID_PROFILES:
        if valid.lower() == profile.lower():
            return valid
    raise ValueError(
        f"Invalid profile '{profile}'. Must be one of: {', '.join(VALID_PROFILES)}"
    )


def call_ollama(query, profile, model, ollama_url):
    """Send the TLL prompt to Ollama via the /api/chat HTTP endpoint."""
    user_prompt = f"Profile: {profile}\nQuery: {query}"

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": TLL_SYSTEM_PROMPT},
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

    return {
        "response": content,
        "profile": profile,
        "query": query,
        "model": model,
        "duration_ms": elapsed_ms,
    }


def log_routing_decision(result, log_path=ROUTING_LOG_PATH):
    """Append a JSONL entry to the routing log."""
    from datetime import datetime

    entry = {
        "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        "profile": result["profile"],
        "query": result["query"],
        "model": result["model"],
        "duration_ms": result["duration_ms"],
        "response": result["response"],
        "session_id": result.get("session_id"),
        "initial_decision": result.get("initial_decision"),
        "final_decision": result.get("final_decision"),
        "correlation_override": result.get("correlation_override", False),
        "correlation_risk": result.get("correlation_result", {}).get("risk") if result.get("correlation_result") else None,
        "correlation_duration_ms": result.get("correlation_result", {}).get("duration_ms") if result.get("correlation_result") else None,
    }

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as e:
        print(f"Warning: could not write routing log: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Tight-Lipped Layer (TLL) - Privacy-aware routing simulator"
    )
    parser.add_argument(
        "--profile", "-p",
        required=True,
        help=f"User profile ({', '.join(VALID_PROFILES)})",
    )
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="The user query to route",
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_OLLAMA_URL,
        help=f"Ollama API base URL (default: {DEFAULT_OLLAMA_URL})",
    )
    parser.add_argument(
        "--log",
        default=ROUTING_LOG_PATH,
        help=f"Routing log file path (default: {ROUTING_LOG_PATH})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print metadata to stderr",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print only the model response (no header/footer)",
    )
    parser.add_argument(
        "--session", "-s",
        default=DEFAULT_SESSION,
        help=f"Session ID for correlation tracking (default: {DEFAULT_SESSION})",
    )
    parser.add_argument(
        "--no-correlation",
        action="store_true",
        help="Skip correlation checking",
    )

    args = parser.parse_args()

    # Validate profile
    try:
        profile = validate_profile(args.profile)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Call Ollama for TLL routing decision
    try:
        result = call_ollama(args.query, profile, args.model, args.url)
    except (ConnectionError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract initial routing decision
    initial_decision = extract_routing_decision(result["response"])
    final_decision = initial_decision
    correlation_result = None
    correlation_override = False

    # Correlation check if routed to cloud service
    if not args.no_correlation and initial_decision in CLOUD_SERVICES:
        try:
            history = load_history(args.session)
            correlation_result = check_correlation(
                profile,
                initial_decision,
                history,
                args.query,
                model=args.model,
                ollama_url=args.url,
            )

            # Override to LOCAL if HIGH risk or if LLM explicitly recommends LOCAL
            if correlation_result["risk"] == "HIGH" or correlation_result["recommendation"] == "LOCAL":
                final_decision = "local"
                correlation_override = True

        except (ConnectionError, RuntimeError) as e:
            print(f"Warning: Correlation check failed: {e}", file=sys.stderr)
            # Continue with original decision if correlation check fails

    # Update session history if final decision is a cloud service
    if final_decision in CLOUD_SERVICES:
        try:
            update_history(args.session, final_decision, summarize_query(args.query))
        except OSError as e:
            print(f"Warning: Could not update session history: {e}", file=sys.stderr)

    # Add correlation info to result
    result["initial_decision"] = initial_decision
    result["final_decision"] = final_decision
    result["correlation_override"] = correlation_override
    result["correlation_result"] = correlation_result
    result["session_id"] = args.session

    # Log the decision
    log_routing_decision(result, args.log)

    reason = extract_reason(result["response"])
    sensitivity = extract_sensitivity(result["response"])

    # Output
    if args.raw:
        print(result["response"])
        if correlation_override:
            print(f"\n[CORRELATION OVERRIDE: {initial_decision.upper()} -> LOCAL]")
    else:
        print(f"Profile: {result['profile']}")
        print(f"Query: {result['query']}")
        print(f"Route: {final_decision.upper() if final_decision else 'UNKNOWN'}")
        if reason:
            print(f"Reason: {reason}")
        if sensitivity:
            print(f"Sensitivity: {sensitivity}")
        if correlation_override:
            print(f"[Correlation override: {initial_decision.upper()} -> LOCAL]")

    if args.verbose:
        print(
            json.dumps(
                {k: v for k, v in result.items() if k != "response"},
                indent=2,
            ),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
