"""Section 1: Routing results — per-query sensitivity scorer decisions.

Runs every scenario query through TLL with --no-correlation so only the
sensitivity scorer's judgment is captured, with no session context.

Usage:
    python3 -m evaluation.section1_routing
    python3 -m evaluation.section1_routing --scenario journalist_source_meeting
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

SCENARIOS_DIR = Path(__file__).parent / "scenarios"
RESULTS_DIR = Path(__file__).parent / "results"
TLL_DIR = Path(__file__).parent.parent
TLL_SCRIPT = TLL_DIR / "tll.py"

CLOUD_SERVICES = {"claude", "openai", "gemini"}


def load_scenarios(scenario_filter=None):
    scenarios = []
    for path in sorted(SCENARIOS_DIR.glob("*.json")):
        if scenario_filter and path.stem != scenario_filter:
            continue
        with open(path) as f:
            scenarios.append(json.load(f))
    return scenarios


def route_query(profile, query):
    """Run a single query through TLL with no-correlation. Returns (decision, reason, sensitivity)."""
    try:
        result = subprocess.run(
            ["python3", str(TLL_SCRIPT),
             "--profile", profile,
             "--query", query,
             "--no-correlation"],
            cwd=str(TLL_DIR),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return "local", "timeout", ""

    decision = "local"
    reason = ""
    sensitivity = ""

    for line in result.stdout.splitlines():
        if line.startswith("Route:"):
            decision = line.split("Route:", 1)[1].strip().lower().split()[0]
        elif line.startswith("Reason:"):
            reason = line.split("Reason:", 1)[1].strip()
        elif line.startswith("Sensitivity:"):
            sensitivity = line.split("Sensitivity:", 1)[1].strip()

    return decision, reason, sensitivity


def run_scenario(scenario):
    profile = scenario["profile"]
    queries = scenario["queries"]
    rows = []

    for i, query in enumerate(queries, 1):
        logger.info(f"  [{i}/{len(queries)}] {query!r}")
        decision, reason, sensitivity = route_query(profile, query)
        dest = "CLOUD" if decision in CLOUD_SERVICES else "LOCAL"
        rows.append({
            "query": query,
            "decision": dest,
            "service": decision.upper() if decision in CLOUD_SERVICES else None,
            "reason": reason,
            "sensitivity": sensitivity,
        })
        logger.info(f"    → {dest}{' (' + decision.upper() + ')' if dest == 'CLOUD' else ''}")

    return rows


def format_scenario_section(scenario, rows):
    lines = []
    profile = scenario["profile"]
    sid = scenario["id"]

    cloud_count = sum(1 for r in rows if r["decision"] == "CLOUD")
    local_count = sum(1 for r in rows if r["decision"] == "LOCAL")

    lines.append(f"## {sid}  ·  Profile: {profile}")
    lines.append(f"_{scenario['description']}_")
    lines.append("")
    lines.append(f"**{local_count}/{len(rows)} queries kept LOCAL — {cloud_count}/{len(rows)} sent to cloud**")
    lines.append("")
    lines.append("| # | Query | Decision | Reason |")
    lines.append("|---|-------|----------|--------|")

    for i, r in enumerate(rows, 1):
        dest = r["decision"]
        if dest == "CLOUD":
            dest = f"CLOUD ({r['service']})"
        reason = r["reason"].replace("|", "\\|") if r["reason"] else "—"
        query = r["query"].replace("|", "\\|")
        lines.append(f"| {i} | {query} | {dest} | {reason} |")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Section 1: routing-only evaluation")
    parser.add_argument("--scenario", help="Run only this scenario id")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    scenarios = load_scenarios(args.scenario)
    if not scenarios:
        print("Error: no scenarios found.", file=sys.stderr)
        sys.exit(1)

    all_sections = []
    all_rows = []

    for scenario in scenarios:
        logger.info(f"Scenario: {scenario['id']}  profile={scenario['profile']}")
        rows = run_scenario(scenario)
        all_sections.append(format_scenario_section(scenario, rows))
        all_rows.append({"scenario": scenario["id"], "profile": scenario["profile"], "rows": rows})

    # Summary table
    summary_lines = ["## Summary", "",
                     "| Scenario | Profile | LOCAL | CLOUD |",
                     "|----------|---------|-------|-------|"]
    for entry in all_rows:
        rows = entry["rows"]
        local = sum(1 for r in rows if r["decision"] == "LOCAL")
        cloud = sum(1 for r in rows if r["decision"] == "CLOUD")
        summary_lines.append(f"| {entry['scenario']} | {entry['profile']} | {local}/{len(rows)} | {cloud}/{len(rows)} |")

    summary = "\n".join(summary_lines)

    # Print to stdout
    print("\n" + summary + "\n")
    for section in all_sections:
        print(section)

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    md_path = RESULTS_DIR / f"section1_routing_{timestamp}.md"
    md_content = (
        f"# Section 1 — Routing Results\n"
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"
        f"_No correlation — sensitivity scorer decisions only_\n\n"
        f"{summary}\n\n"
        + "\n".join(all_sections)
    )
    md_path.write_text(md_content)

    json_path = RESULTS_DIR / f"section1_routing_{timestamp}.json"
    json_path.write_text(json.dumps(all_rows, indent=2))

    logger.info(f"Saved → {md_path}")
    logger.info(f"Saved → {json_path}")


if __name__ == "__main__":
    main()
