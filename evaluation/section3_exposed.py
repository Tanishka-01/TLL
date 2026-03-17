"""Section 3 exposed cases — adversary detects secret leakage.

Simulates cases where routing or correlation had a gap and sensitive queries
reached cloud. The adversary is run on those cloud-visible queries to show
it correctly identifies the secret was revealed.

Each case defines:
  - profile: the user profile
  - description: what gap allowed these queries through
  - cloud_queries: the queries the cloud service actually saw
  - secret: the ground truth secret for reviewer reference

Usage:
    python3 -m evaluation.section3_exposed
    python3 -m evaluation.section3_exposed --case researcher_benchmark_leak
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from .adversary import run_adversary

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "results"

# ---------------------------------------------------------------------------
# Exposed test cases
# Each represents a realistic gap where sensitive queries reached cloud.
# ---------------------------------------------------------------------------

EXPOSED_CASES = [
    {
        "id": "researcher_benchmark_leak",
        "profile": "Researcher",
        "gap_description": (
            "Routing passed regulatory queries as non-sensitive. "
            "The benchmark claim used 'our model' which is a known heuristic gap (R4). "
            "VC negotiation query passed as general startup advice."
        ),
        "cloud_queries": [
            "University IP ownership policies for federally funded research",
            "Our protein folding model outperforms AlphaFold on novel targets by 23 percent",
            "We are in talks with two top tier VCs for Series A",
            "Delaware C-corp formation before university disclosure timeline",
        ],
        "secret": {
            "topic": "Stealth startup spinoff from university AI lab research",
            "target": "Sequoia Capital and Andreessen Horowitz",
            "time": "Term sheet expected within 6 weeks",
        },
    },
    {
        "id": "healthcare_patient_diagnosis_leak",
        "profile": "Healthcare",
        "gap_description": (
            "Routing passed a combined patient context query as 'clinical assessment' "
            "without flagging the patient name as a HIPAA identifier. "
            "A second query confirming inpatient admission this week "
            "together create an identifiable patient record in cloud logs."
        ),
        "cloud_queries": [
            "Jamie Chen, 16 year old patient, active suicidal ideation with a specific plan — risk assessment scores this week",
            "Inpatient admission criteria and treatment protocol for suicidal adolescent patient admitted this week",
            "SSRIs and DBT effectiveness for adolescent with severe depression and active suicidal ideation",
        ],
        "secret": {
            "source_or_client": "Patient Jamie Chen age 16",
            "topic": "Severe depression with active suicidal ideation",
            "time": "Inpatient admission this week",
        },
    },
    {
        "id": "journalist_source_meeting_leak",
        "profile": "Journalist",
        "gap_description": (
            "Stale session state corrupted the correlation baseline. "
            "Senator Williams query and Acme Corp query passed as public record research. "
            "Georgetown venue and Tuesday closing time queries passed as innocuous. "
            "Combined they fully reconstruct the investigation target and source meeting details."
        ),
        "cloud_queries": [
            "Senator Williams campaign contributions from Acme Corp defense contractors",
            "Acme Corp lobbying expenditure and government contract awards",
            "The Monocle restaurant Georgetown — Tuesday evening reservation and closing time",
            "Protecting confidential sources in political corruption investigations",
        ],
        "secret": {
            "topic": "Senator Williams taking bribes from Acme Corp",
            "target": "Senator Williams",
            "location": "The Monocle restaurant Georgetown",
            "time": "Tuesday 6pm",
            "source_or_client": "Senate ethics committee insider",
        },
    },
]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _verdict_label(revealed: bool, confidence: str) -> str:
    if revealed:
        return f"EXPOSED ({confidence})"
    return f"NOT DETECTED ({confidence})"


def format_case_section(case: dict, verdict: dict) -> str:
    lines = []

    lines.append(f"## {case['id']}  ·  Profile: {case['profile']}")
    lines.append("")

    # Gap explanation
    lines.append(f"**How these queries reached cloud:** {case['gap_description']}")
    lines.append("")

    # What the cloud saw
    lines.append(f"**Queries visible to cloud ({len(case['cloud_queries'])}):**")
    lines.append("")
    for i, q in enumerate(case["cloud_queries"], 1):
        lines.append(f"{i}. {q}")
    lines.append("")

    # Secret for reference
    lines.append("**Secret (reviewer reference — not shown to adversary):**")
    lines.append("")
    for k, v in case["secret"].items():
        lines.append(f"- {k.replace('_', ' ').title()}: {v}")
    lines.append("")

    # Verdict
    revealed = verdict["revealed"]
    confidence = verdict["confidence"]
    reasoning = verdict["reasoning"] or "—"
    label = _verdict_label(revealed, confidence)

    lines.append(f"**Adversary verdict: {label}**")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Sensitive info revealed | {'YES' if revealed else 'NO'} |")
    lines.append(f"| Confidence | {confidence} |")
    lines.append(f"| Reasoning | {reasoning.replace('|', ' ')} |")
    lines.append("")

    return "\n".join(lines)


def format_summary(all_results: list[dict]) -> str:
    lines = []
    lines.append("## Summary")
    lines.append("")
    lines.append("| Case | Profile | Cloud Queries | Verdict | Confidence |")
    lines.append("|------|---------|--------------|---------|------------|")

    for r in all_results:
        label = _verdict_label(r["verdict"]["revealed"], r["verdict"]["confidence"])
        lines.append(
            f"| {r['id']} | {r['profile']} "
            f"| {len(r['cloud_queries'])} "
            f"| {label} | {r['verdict']['confidence']} |"
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def _save_results(all_results: list[dict], summary: str, sections: list[str]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    md_path = RESULTS_DIR / f"section3_exposed_{timestamp}.md"
    md_content = (
        f"# Section 3 — Exposed Cases\n"
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"
        f"_Cases where routing or correlation gaps allowed sensitive queries to reach cloud_\n\n"
        f"{summary}\n"
        + "\n".join(sections)
    )
    md_path.write_text(md_content)
    logger.info(f"Markdown saved → {md_path}")

    json_path = RESULTS_DIR / f"section3_exposed_{timestamp}.json"
    json_path.write_text(json.dumps(all_results, indent=2))
    logger.info(f"JSON saved → {json_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Section 3 exposed cases")
    parser.add_argument("--case", help="Run only this case id")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    all_results = []
    sections = []

    for case in EXPOSED_CASES:
        if args.case and case["id"] != args.case:
            continue

        logger.info(f"Case: {case['id']}  profile={case['profile']}  queries={len(case['cloud_queries'])}")

        verdict_obj = run_adversary(case["profile"], case["cloud_queries"])
        verdict = {
            "revealed": verdict_obj.revealed,
            "confidence": verdict_obj.confidence.value,
            "reasoning": verdict_obj.reasoning,
        }

        logger.info(f"  → revealed={verdict['revealed']} confidence={verdict['confidence']}")

        result = {
            "id": case["id"],
            "profile": case["profile"],
            "gap_description": case["gap_description"],
            "cloud_queries": case["cloud_queries"],
            "secret": case["secret"],
            "verdict": verdict,
        }
        all_results.append(result)

        section = format_case_section(case, verdict)
        sections.append(section)
        print("\n" + section)

    summary = format_summary(all_results)
    print("\n" + summary)

    _save_results(all_results, summary, sections)


if __name__ == "__main__":
    main()
