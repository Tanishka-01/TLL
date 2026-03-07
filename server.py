#!/usr/bin/env python3
"""TLL HTTP Server - Privacy-aware routing as a service.

Exposes TLL routing via HTTP so any app can send a query and get
a routing decision back.

Usage:
    python3 server.py --host 0.0.0.0 --port 8080

Request:
    POST /route
    Content-Type: application/json
    {"query": "My client is suing Google", "profile": "Lawyer", "session": "optional"}

Response:
    {"route": "LOCAL", "reason": "...", "sensitivity": "...", "correlation_override": false}
"""

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from tll import (
    validate_profile,
    call_ollama,
    extract_routing_decision,
    extract_reason,
    extract_sensitivity,
    log_routing_decision,
    CLOUD_SERVICES,
    DEFAULT_MODEL,
    DEFAULT_OLLAMA_URL,
    ROUTING_LOG_PATH,
)
from correlation import (
    load_history,
    update_history,
    check_correlation,
    summarize_query,
)

MODEL = DEFAULT_MODEL
OLLAMA_URL = DEFAULT_OLLAMA_URL


class TLLHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/route":
            self._send(404, {"error": "Not found. Use POST /route"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            self._send(400, {"error": "Invalid JSON"})
            return

        query = data.get("query", "").strip()
        profile_raw = data.get("profile", "").strip()
        session = data.get("session", "default").strip() or "default"

        if not query:
            self._send(400, {"error": "Missing field: query"})
            return
        if not profile_raw:
            self._send(400, {"error": "Missing field: profile"})
            return

        try:
            profile = validate_profile(profile_raw)
        except ValueError as e:
            self._send(400, {"error": str(e)})
            return

        try:
            result = call_ollama(query, profile, MODEL, OLLAMA_URL)
        except (ConnectionError, RuntimeError) as e:
            self._send(503, {"error": str(e)})
            return

        initial_decision = extract_routing_decision(result["response"])
        final_decision = initial_decision
        correlation_result = None
        correlation_override = False

        if initial_decision in CLOUD_SERVICES:
            try:
                history = load_history(session)
                correlation_result = check_correlation(
                    profile, initial_decision, history, query,
                    model=MODEL, ollama_url=OLLAMA_URL,
                )
                if correlation_result["risk"] == "HIGH" or correlation_result["recommendation"] == "LOCAL":
                    final_decision = "local"
                    correlation_override = True
            except (ConnectionError, RuntimeError):
                pass

        if final_decision in CLOUD_SERVICES:
            try:
                update_history(session, final_decision, summarize_query(query))
            except OSError:
                pass

        result["initial_decision"] = initial_decision
        result["final_decision"] = final_decision
        result["correlation_override"] = correlation_override
        result["correlation_result"] = correlation_result
        result["session_id"] = session

        log_routing_decision(result, ROUTING_LOG_PATH)

        self._send(200, {
            "route": final_decision.upper(),
            "reason": extract_reason(result["response"]),
            "sensitivity": extract_sensitivity(result["response"]),
            "correlation_override": correlation_override,
            "session": session,
        })

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(200, {
                "service": "TLL - Tight-Lipped Layer",
                "usage": "POST /route with {query, profile, session(optional)}",
                "profiles": ["Lawyer", "Journalist", "Healthcare", "Researcher"],
            })

    def _send(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[{self.client_address[0]}] {fmt % args}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="TLL HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL, help=f"Ollama URL (default: {DEFAULT_OLLAMA_URL})")
    args = parser.parse_args()

    global MODEL, OLLAMA_URL
    MODEL = args.model
    OLLAMA_URL = args.url

    server = HTTPServer((args.host, args.port), TLLHandler)
    print(f"TLL server running on http://{args.host}:{args.port}")
    print(f"Model: {MODEL}  Ollama: {OLLAMA_URL}")
    print("Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        sys.exit(0)


if __name__ == "__main__":
    main()
