"""Section 3: Adversary results — privacy oracle verdict on cloud-visible queries.

Loads Section 2 JSON, extracts the queries that actually reached cloud after
both routing and correlation, runs the adversary privacy oracle on them, and
reports whether sensitive information was exposed.

Usage:
    python3 -m evaluation.section3_adversary --section2 evaluation/results/section2_correlation_TIMESTAMP.json
    python3 -m evaluation.section3_adversary --section2 evaluation/results/section2_correlation_TIMESTAMP.json --scenario lawyer_whistleblower_client
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Adversary module lives in the evaluation package
from .adversary import run_adversary

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "results"
SCENARIOS_DIR = Path(__file__).parent / "scenarios"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_scenario_meta() -> dict:
    meta = {}
    for path in SCENARIOS_DIR.glob("*.json"):
        with open(path) as f:
            d = json.load(f)
        meta[d["id"]] = {
            "description": d.get("description", ""),
            "secret": d.get("secret", {}),
        }
    return meta


def _verdict_icon(revealed: bool, confidence: str) -> str:
    if not revealed:
        return "SAFE"
    if confidence == "HIGH":
        return "EXPOSED (HIGH)"
    if confidence == "MEDIUM":
        return "EXPOSED (MEDIUM)"
    return "EXPOSED (LOW)"


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_scenario_section(scenario_id: str, profile: str, description: str,
                             secret: dict, total_queries: int,
                             cloud_queries: list[str], verdict: dict) -> str:
    lines = []

    lines.append(f"## {scenario_id}  ·  Profile: {profile}")
    lines.append(f"_{description}_")
    lines.append("")

    # What the cloud saw
    lines.append(f"**Queries visible to cloud after routing + correlation: {len(cloud_queries)}/{total_queries}**")
    lines.append("")
    if cloud_queries:
        for i, q in enumerate(cloud_queries, 1):
            lines.append(f"{i}. {q}")
    else:
        lines.append("_No queries reached cloud._")
    lines.append("")

    # Secret (for reviewer reference)
    secret_fields = {k: v for k, v in secret.items() if v}
    if secret_fields:
        lines.append("**Secret the adversary is trying to reconstruct:**")
        lines.append("")
        for k, v in secret_fields.items():
            lines.append(f"- {k.replace('_', ' ').title()}: {v}")
        lines.append("")

    # Verdict
    revealed = verdict["revealed"]
    confidence = verdict["confidence"]
    reasoning = verdict["reasoning"] or "—"
    icon = _verdict_icon(revealed, confidence)

    lines.append(f"**Adversary verdict: {icon}**")
    lines.append("")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Sensitive info revealed | {'YES' if revealed else 'NO'} |")
    lines.append(f"| Confidence | {confidence} |")
    lines.append(f"| Reasoning | {reasoning} |")
    lines.append("")

    return "\n".join(lines)


def format_summary_table(all_results: list[dict]) -> str:
    lines = []
    lines.append("## Summary")
    lines.append("")
    lines.append("| Scenario | Profile | Queries to Cloud | Adversary Verdict | Confidence |")
    lines.append("|----------|---------|-----------------|-------------------|------------|")

    for r in all_results:
        icon = _verdict_icon(r["verdict"]["revealed"], r["verdict"]["confidence"])
        lines.append(
            f"| {r['scenario_id']} | {r['profile']} "
            f"| {r['final_cloud']}/{r['total_queries']} "
            f"| {icon} | {r['verdict']['confidence']} |"
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def _save_results(all_results: list[dict], summary: str, sections: list[str]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    md_path = RESULTS_DIR / f"section3_adversary_{timestamp}.md"
    md_content = (
        f"# Section 3 — Adversary Results\n"
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"
        f"_Privacy oracle verdict on queries visible to cloud after routing + correlation_\n\n"
        f"{summary}\n"
        + "\n".join(sections)
    )
    md_path.write_text(md_content)
    logger.info(f"Markdown saved → {md_path}")

    json_path = RESULTS_DIR / f"section3_adversary_{timestamp}.json"
    json_path.write_text(json.dumps(all_results, indent=2))
    logger.info(f"JSON saved → {json_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Section 3: adversary evaluation")
    parser.add_argument("--section2", required=True, help="Path to Section 2 JSON results file")
    parser.add_argument("--scenario", help="Run only this scenario id")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    section2_path = Path(args.section2)
    if not section2_path.exists():
        print(f"Error: {section2_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(section2_path) as f:
        section2_data = json.load(f)

    scenario_meta = _load_scenario_meta()

    all_results = []
    sections = []

    for entry in section2_data:
        sid = entry["scenario_id"]
        if args.scenario and sid != args.scenario:
            continue

        profile = entry["profile"]
        total_queries = entry["total_queries"]
        meta = scenario_meta.get(sid, {})
        description = meta.get("description", "")
        secret = meta.get("secret", {})

        # Extract only the queries that passed correlation (reached cloud)
        cloud_queries = [
            r["query"] for r in entry["correlation_checks"]
            if r["decision"] == "PASS"
        ]
        final_cloud = len(cloud_queries)

        logger.info(f"Scenario: {sid}  profile={profile}  cloud_queries={final_cloud}")

        verdict_obj = run_adversary(profile, cloud_queries)
        verdict = {
            "revealed": verdict_obj.revealed,
            "confidence": verdict_obj.confidence.value,
            "reasoning": verdict_obj.reasoning,
        }

        logger.info(
            f"  Verdict: revealed={verdict['revealed']} "
            f"confidence={verdict['confidence']}"
        )

        result = {
            "scenario_id": sid,
            "profile": profile,
            "total_queries": total_queries,
            "final_cloud": final_cloud,
            "cloud_queries": cloud_queries,
            "verdict": verdict,
        }
        all_results.append(result)

        section = format_scenario_section(
            sid, profile, description, secret,
            total_queries, cloud_queries, verdict,
        )
        sections.append(section)
        print("\n" + section)

    summary = format_summary_table(all_results)
    print("\n" + summary)

    _save_results(all_results, summary, sections)


if __name__ == "__main__":
    main()
