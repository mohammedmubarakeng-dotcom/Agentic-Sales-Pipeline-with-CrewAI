"""Runnable demo for the Agentic Sales Pipeline."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flow import ComplexSalesPipeline, estimate_token_cost  # noqa: E402


DEMO_LEADS = [
    {
        "name": "Sarah Chen",
        "job_title": "VP of Revenue Operations",
        "company": "Northstar Analytics",
        "email": "sarah.chen@northstar-analytics.com",
        "use_case": "Automating lead qualification and personalized outbound workflows for a growing B2B SaaS sales team.",
    },
    {
        "name": "Marcus Rivera",
        "job_title": "Head of Sales Enablement",
        "company": "CloudMetric",
        "email": "marcus@cloudmetric.io",
        "use_case": "Improving rep productivity through AI-based account research and outbound personalization.",
    },
]


def main() -> None:
    pipeline = ComplexSalesPipeline(leads=DEMO_LEADS)

    print("🚀 Agentic Sales Pipeline Demo")
    print("=" * 50)
    print("Loaded demo leads:", len(DEMO_LEADS))
    print()

    if hasattr(pipeline, "kickoff"):
        result = pipeline.kickoff()
        print("Pipeline executed through CrewAI Flow.")
        print("Result:")
        print(result)
    else:
        print(
            "CrewAI is not installed in this environment, so the demo is running in preview mode.\n"
            "Install dependencies and set API keys to execute the full agentic workflow."
        )

    example_total_tokens = 4821
    print()
    print(f"Estimated cost for {example_total_tokens} tokens: ${estimate_token_cost(example_total_tokens):.6f}")


if __name__ == "__main__":
    main()
