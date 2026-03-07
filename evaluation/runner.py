"""Adversary simulation runner.

Usage:
    python -m evaluation.runner                               # all scenarios, all methods
    python -m evaluation.runner --scenario journalist_source_meeting
    python -m evaluation.runner --method tll
    python -m evaluation.runner --verbose
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from .adversary import run_adversary
from .models import EvaluationResult, Scenario
from .routers import always_cloud, threshold_router, tll_router
from .scorer import score_reconstruction

logger = logging.getLogger(__name__)

SCENARIOS_DIR = Path(__file__).parent / "scenarios"
RESULTS_DIR = Path(__file__).parent / "results"
METHODS = ["always_cloud", "threshold", "tll"]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_scenarios(scenario_filter: str | None = None) -> list[Scenario]:
    """Load all scenario JSON files, optionally filtered by scenario id."""
    scenarios: list[Scenario] = []

    for path in sorted(SCENARIOS_DIR.glob("*.json")):
        if scenario_filter and path.stem != scenario_filter:
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            scenarios.append(Scenario(**data))
        except Exception as exc:
            logger.error(f"Failed to load scenario {path.name}: {exc}")

    return scenarios


# ---------------------------------------------------------------------------
# Running a single scenario × method
# ---------------------------------------------------------------------------

def run_scenario(scenario: Scenario, method: str) -> EvaluationResult:
    """Run one scenario through one routing method and score the adversary."""
    session_id = f"eval_{scenario.id}_{method}"
    total_queries = len(scenario.queries)

    logger.info(f"  [{method}] routing {total_queries} queries (session={session_id})")

    if method == "always_cloud":
        routing = always_cloud(scenario.queries)
    elif method == "threshold":
        routing = threshold_router(scenario.queries, scenario.profile)
    elif method == "tll":
        routing = tll_router(scenario.queries, scenario.profile, session_id)
    else:
        raise ValueError(f"Unknown routing method: {method!r}")

    cloud_count = len(routing.queries_to_cloud)
    local_count = len(routing.queries_to_local)
    logger.info(f"  [{method}] cloud={cloud_count} local={local_count}")

    adversary_guess = run_adversary(scenario.profile, routing.queries_to_cloud)
    score = score_reconstruction(scenario.secret, adversary_guess)

    logger.info(f"  [{method}] reconstruction score = {score:.3f}")

    # Compute average sensitivity scores when available (tll only)
    avg_sen_local: float | None = None
    avg_sen_cloud: float | None = None
    if routing.sensitivity_scores_local:
        vals = list(routing.sensitivity_scores_local.values())
        avg_sen_local = sum(vals) / len(vals)
    if routing.sensitivity_scores_cloud:
        vals = list(routing.sensitivity_scores_cloud.values())
        avg_sen_cloud = sum(vals) / len(vals)

    if avg_sen_local is not None or avg_sen_cloud is not None:
        logger.info(
            f"  [{method}] avg sensitivity — local={avg_sen_local:.2f if avg_sen_local is not None else '-'} "
            f"cloud={avg_sen_cloud:.2f if avg_sen_cloud is not None else '-'}"
        )

    return EvaluationResult(
        scenario_id=scenario.id,
        profile=scenario.profile,
        method=method,
        queries_sent_to_cloud=cloud_count,
        queries_kept_local=local_count,
        adversary_guess=adversary_guess,
        reconstruction_score=score,
        avg_sensitivity_local=avg_sen_local,
        avg_sensitivity_cloud=avg_sen_cloud,
    )


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _fmt_sen(val: float | None) -> str:
    """Format a sensitivity average for table display."""
    return f"{val:.2f}" if val is not None else "-"


def _format_results_table(results: list[EvaluationResult]) -> str:
    """Generate a markdown table of per-scenario results plus a summary."""
    lines: list[str] = []

    # Per-scenario table
    lines.append("| Scenario | Method | Cloud | Score | Avg Sen (LOCAL) | Avg Sen (CLOUD) |")
    lines.append("|----------|--------|-------|-------|-----------------|-----------------|")

    for r in results:
        total = r.queries_sent_to_cloud + r.queries_kept_local
        lines.append(
            f"| {r.scenario_id} | {r.method} | {r.queries_sent_to_cloud}/{total} | "
            f"{r.reconstruction_score:.2f} | {_fmt_sen(r.avg_sensitivity_local)} | "
            f"{_fmt_sen(r.avg_sensitivity_cloud)} |"
        )

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Method | Cloud | Score | Avg Sensitivity (LOCAL) | Avg Sensitivity (CLOUD) |")
    lines.append("|--------|-------|-------|-------------------------|-------------------------|")

    for method in METHODS:
        method_results = [r for r in results if r.method == method]
        if not method_results:
            continue
        avg_score = sum(r.reconstruction_score for r in method_results) / len(method_results)
        avg_cloud = sum(r.queries_sent_to_cloud for r in method_results) / len(method_results)

        local_sens = [r.avg_sensitivity_local for r in method_results if r.avg_sensitivity_local is not None]
        cloud_sens = [r.avg_sensitivity_cloud for r in method_results if r.avg_sensitivity_cloud is not None]
        avg_sen_local = sum(local_sens) / len(local_sens) if local_sens else None
        avg_sen_cloud = sum(cloud_sens) / len(cloud_sens) if cloud_sens else None

        lines.append(
            f"| {method} | {avg_cloud:.1f} | {avg_score:.2f} | "
            f"{_fmt_sen(avg_sen_local)} | {_fmt_sen(avg_sen_cloud)} |"
        )

    return "\n".join(lines)


def _format_detail_section(results: list[EvaluationResult]) -> str:
    """Generate a detailed markdown section with adversary guesses per scenario."""
    lines: list[str] = []

    lines.append("")
    lines.append("## Detailed Adversary Reconstructions")
    lines.append("")

    for r in results:
        lines.append(f"### {r.scenario_id} — {r.method}")
        lines.append(f"- Cloud queries: {r.queries_sent_to_cloud}")
        lines.append(f"- Score: {r.reconstruction_score:.3f}")
        if r.avg_sensitivity_local is not None or r.avg_sensitivity_cloud is not None:
            lines.append(f"- Avg sensitivity LOCAL: {_fmt_sen(r.avg_sensitivity_local)}")
            lines.append(f"- Avg sensitivity CLOUD: {_fmt_sen(r.avg_sensitivity_cloud)}")
        g = r.adversary_guess
        lines.append(f"- **Topic**: {g.topic or 'Cannot determine'} ({g.topic_confidence.value})")
        lines.append(f"- **Target**: {g.target or 'Cannot determine'} ({g.target_confidence.value})")
        lines.append(f"- **Location**: {g.location or 'Cannot determine'} ({g.location_confidence.value})")
        lines.append(f"- **Time**: {g.time or 'Cannot determine'} ({g.time_confidence.value})")
        lines.append(
            f"- **Source/Client**: {g.source_or_client or 'Cannot determine'} ({g.source_or_client_confidence.value})"
        )
        if g.reasoning:
            lines.append(f"- **Reasoning**: {g.reasoning}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def _save_results(results: list[EvaluationResult], table: str, detail: str) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = RESULTS_DIR / f"results_{timestamp}.json"
    json_path.write_text(
        json.dumps([r.model_dump() for r in results], indent=2, default=str)
    )
    logger.info(f"JSON results saved → {json_path}")

    md_path = RESULTS_DIR / f"results_{timestamp}.md"
    md_content = (
        f"# TLL Adversary Simulation Results\n"
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
        f"{table}\n"
        f"{detail}\n"
    )
    md_path.write_text(md_content)
    logger.info(f"Markdown report saved → {md_path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TLL adversary simulation — measures privacy protection across routing methods"
    )
    parser.add_argument(
        "--scenario",
        help="Run only this scenario (e.g. journalist_source_meeting)",
    )
    parser.add_argument(
        "--method",
        choices=METHODS,
        help="Run only this routing method (always_cloud, threshold, tll)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    scenarios = load_scenarios(args.scenario)
    if not scenarios:
        msg = (
            f"No scenarios found matching {args.scenario!r}."
            if args.scenario
            else "No scenario files found in evaluation/scenarios/."
        )
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    methods = [args.method] if args.method else METHODS
    results: list[EvaluationResult] = []

    for scenario in scenarios:
        logger.info(f"Scenario: {scenario.id}  profile={scenario.profile}")
        for method in methods:
            result = run_scenario(scenario, method)
            results.append(result)

    table = _format_results_table(results)
    detail = _format_detail_section(results)

    print("\n" + table)
    _save_results(results, table, detail)


if __name__ == "__main__":
    main()
