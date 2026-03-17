"""Section 2: Correlation results — what the correlation layer adds on top of routing.

Loads Section 1 JSON, takes only the cloud-bound queries per scenario, runs them
through the correlation layer in session order (maintaining per-service history),
and records what gets blocked vs passed at each step.

Usage:
    python3 -m evaluation.section2_correlation --section1 evaluation/results/section1_routing_TIMESTAMP.json
    python3 -m evaluation.section2_correlation --section1 evaluation/results/section1_routing_TIMESTAMP.json --scenario journalist_source_meeting
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Correlation module lives in the TLL root (one level up from evaluation/)
TLL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TLL_DIR))

from correlation import check_correlation, summarize_query  # noqa: E402

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "results"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _short(query: str, max_len: int = 70) -> str:
    """Truncate a query for display."""
    return query if len(query) <= max_len else query[:max_len - 1] + "…"


def _history_display(history_items: list[str]) -> str:
    """Format history list for the table cell — each item numbered."""
    if not history_items:
        return "—"
    return "; ".join(f"({i+1}) {q}" for i, q in enumerate(history_items))


def _engine_label(result: dict, had_history: bool) -> str:
    if not had_history:
        return "— (no history)"
    if result["duration_ms"] == 0:
        return "Heuristic (0 ms)"
    return f"LLM ({result['duration_ms']} ms)"


def _decision_label(result: dict) -> str:
    if result["recommendation"] == "LOCAL" or result["risk"] == "HIGH":
        return "BLOCKED"
    return "PASS"


def _extract_reasoning(result: dict, had_history: bool) -> str:
    """Extract meaningful reasoning text from the correlation response."""
    if not had_history:
        return "No prior history for this service — correlation check skipped."
    resp = result.get("response", "")
    if resp.startswith("[Heuristic]"):
        return resp[len("[Heuristic]"):].strip()
    # LLM response format:
    #   [brief analysis paragraph]
    #   Correlation Risk: HIGH/LOW/NONE
    #   Recommendation: SAFE for X / ROUTE TO LOCAL
    # Extract the analysis paragraph (everything before "Correlation Risk:")
    lines = [l.strip() for l in resp.splitlines() if l.strip()]
    analysis_lines = []
    for line in lines:
        if line.upper().startswith("CORRELATION RISK:") or line.upper().startswith("RECOMMENDATION:"):
            break
        analysis_lines.append(line)
    analysis = " ".join(analysis_lines).strip()
    if analysis:
        return analysis
    # Fallback: return the full response stripped
    return resp.strip()[:200]


# ---------------------------------------------------------------------------
# Core: run correlation checks for one scenario
# ---------------------------------------------------------------------------

def run_scenario_correlation(scenario_id: str, profile: str, rows: list[dict]) -> list[dict]:
    """Run correlation checks on the cloud-bound queries from Section 1.

    Maintains per-service history. Blocked queries are not added to history.
    Returns a list of result dicts, one per cloud-bound query.
    """
    # Per-service session history (mirrors what correlation.py tracks on disk)
    history: dict[str, list[str]] = {"claude": [], "openai": [], "gemini": []}
    results = []

    for row in rows:
        if row["decision"] != "CLOUD":
            continue  # Already handled in Section 1

        query = row["query"]
        service = row["service"].lower()
        service_history = history[service]

        had_history = len(service_history) > 0
        history_snapshot = list(service_history)  # copy before check

        corr = check_correlation(
            profile=profile,
            service=service,
            history=history,
            query=query,
        )

        decision = _decision_label(corr)
        engine = _engine_label(corr, had_history)

        results.append({
            "query": query,
            "service": service.upper(),
            "history_at_check": history_snapshot,
            "engine": engine,
            "decision": decision,
            "risk": corr["risk"],
            "recommendation": corr["recommendation"],
            "reasoning": _extract_reasoning(corr, had_history),
            "duration_ms": corr["duration_ms"],
        })

        logger.info(
            f"  [{decision}] ({corr['risk']}) {query!r} "
            f"history={len(history_snapshot)} rec={corr['recommendation']}"
        )

        # Only add to history if not blocked
        if decision == "PASS":
            history[service].append(summarize_query(query))

    return results


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_scenario_section(scenario_id: str, profile: str, description: str,
                             total_queries: int, corr_results: list[dict]) -> str:
    lines = []

    passed = sum(1 for r in corr_results if r["decision"] == "PASS")
    blocked = sum(1 for r in corr_results if r["decision"] == "BLOCKED")
    cloud_in = len(corr_results)

    lines.append(f"## {scenario_id}  ·  Profile: {profile}")
    lines.append(f"_{description}_")
    lines.append("")
    lines.append(
        f"Routing passed **{cloud_in}/{total_queries}** queries to cloud. "
        f"Correlation additionally blocked **{blocked}**. "
        f"**{passed}/{total_queries} queries reach cloud after both layers.**"
    )
    lines.append("")

    if not corr_results:
        lines.append("_No queries reached this stage._")
        lines.append("")
        return "\n".join(lines)

    lines.append("| # | Query | Service | History Visible at Check | Engine | Risk | Decision |")
    lines.append("|---|-------|---------|--------------------------|--------|------|----------|")

    for i, r in enumerate(corr_results, 1):
        hist = _history_display(r["history_at_check"]).replace("|", "\\|")
        query_display = _short(r["query"]).replace("|", "\\|")
        decision_display = f"**{r['decision']}**" if r["decision"] == "BLOCKED" else r["decision"]
        rec_note = " (rec: LOCAL)" if r["recommendation"] == "LOCAL" and r["risk"] != "HIGH" else ""
        lines.append(
            f"| {i} | {query_display} | {r['service']} | {hist} "
            f"| {r['engine']} | {r['risk']}{rec_note} | {decision_display} |"
        )

    lines.append("")

    # Detailed analysis for all LLM-checked queries
    llm_results = [r for r in corr_results if "LLM" in r["engine"]]
    if llm_results:
        lines.append("**Correlation analysis detail:**")
        lines.append("")
        for r in llm_results:
            status = "BLOCKED" if r["decision"] == "BLOCKED" else "passed"
            lines.append(f"**{r['query']}** — {status}")
            lines.append(f"> {r['reasoning']}")
            lines.append("")

    return "\n".join(lines)


def format_summary_table(all_results: list[dict]) -> str:
    lines = []
    lines.append("## Summary")
    lines.append("")
    lines.append("| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |")
    lines.append("|----------|---------|--------------|------------------------|-------------|")

    for entry in all_results:
        total = entry["total_queries"]
        cloud_in = entry["cloud_in"]
        blocked = entry["blocked"]
        final = cloud_in - blocked
        lines.append(
            f"| {entry['scenario_id']} | {entry['profile']} "
            f"| {cloud_in}/{total} | {blocked} | {final}/{total} |"
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def _save_results(all_results: list[dict], summary: str, sections: list[str]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    md_path = RESULTS_DIR / f"section2_correlation_{timestamp}.md"
    md_content = (
        f"# Section 2 — Correlation Results\n"
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"
        f"_Correlation layer applied to cloud-bound queries from Section 1, in session order_\n\n"
        f"{summary}\n"
        + "\n".join(sections)
    )
    md_path.write_text(md_content)
    logger.info(f"Markdown saved → {md_path}")

    json_path = RESULTS_DIR / f"section2_correlation_{timestamp}.json"
    json_path.write_text(json.dumps(all_results, indent=2))
    logger.info(f"JSON saved → {json_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Section 2: correlation evaluation")
    parser.add_argument(
        "--section1", required=True,
        help="Path to Section 1 JSON results file",
    )
    parser.add_argument(
        "--scenario",
        help="Run only this scenario id",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    section1_path = Path(args.section1)
    if not section1_path.exists():
        print(f"Error: {section1_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(section1_path) as f:
        section1_data = json.load(f)

    # Load scenario descriptions from JSON files
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_meta = {}
    for path in scenarios_dir.glob("*.json"):
        with open(path) as f:
            d = json.load(f)
        scenario_meta[d["id"]] = d.get("description", "")

    all_results = []
    sections = []

    for entry in section1_data:
        sid = entry["scenario"]
        if args.scenario and sid != args.scenario:
            continue

        profile = entry["profile"]
        rows = entry["rows"]
        description = scenario_meta.get(sid, "")
        total_queries = len(rows)
        cloud_in = sum(1 for r in rows if r["decision"] == "CLOUD")

        logger.info(f"Scenario: {sid}  profile={profile}  cloud_in={cloud_in}")

        corr_results = run_scenario_correlation(sid, profile, rows)

        blocked = sum(1 for r in corr_results if r["decision"] == "BLOCKED")
        final_cloud = cloud_in - blocked

        all_results.append({
            "scenario_id": sid,
            "profile": profile,
            "total_queries": total_queries,
            "cloud_in": cloud_in,
            "blocked": blocked,
            "final_cloud": final_cloud,
            "correlation_checks": corr_results,
        })

        section = format_scenario_section(sid, profile, description, total_queries, corr_results)
        sections.append(section)
        print("\n" + section)

    summary = format_summary_table(all_results)
    print("\n" + summary)

    _save_results(all_results, summary, sections)


if __name__ == "__main__":
    main()
