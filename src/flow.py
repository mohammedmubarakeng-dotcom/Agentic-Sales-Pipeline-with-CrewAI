"""Flow implementations for the Agentic Sales Pipeline.

Includes:
- SimpleSalesPipeline
- ComplexSalesPipeline with conditional routing
- utility helpers for scoring, routing, and cost estimation
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence

from dotenv import load_dotenv

from crews import build_email_writing_crew, build_lead_scoring_crew
from models import LeadInput

try:
    from crewai import Flow
    from crewai.flow.flow import and_, listen, router, start
    CREWAI_AVAILABLE = True
except ImportError:  # pragma: no cover - allows import during tests without CrewAI
    CREWAI_AVAILABLE = False

    class Flow:  # type: ignore
        def __init__(self, *args, **kwargs):
            self.state = {}

    def start():
        def decorator(func):
            return func
        return decorator

    def listen(*_args, **_kwargs):
        def decorator(func):
            return func
        return decorator

    def router(*_args, **_kwargs):
        def decorator(func):
            return func
        return decorator

    def and_(*args):  # noqa: ANN001
        return args


DEFAULT_THRESHOLD = int(os.getenv("DEFAULT_LEAD_SCORE_THRESHOLD", "70"))


@dataclass
class CostEstimate:
    total_tokens: int
    input_cost_per_million: float
    output_cost_per_million: float = 0.0

    @property
    def estimated_total_cost(self) -> float:
        return (self.total_tokens / 1_000_000) * (
            self.input_cost_per_million + self.output_cost_per_million
        )


def estimate_token_cost(
    total_tokens: int,
    input_cost_per_million: float = 0.150,
    output_cost_per_million: float = 0.0,
) -> float:
    """Estimate token cost using per-million-token pricing."""
    estimate = CostEstimate(
        total_tokens=total_tokens,
        input_cost_per_million=input_cost_per_million,
        output_cost_per_million=output_cost_per_million,
    )
    return round(estimate.estimated_total_cost, 6)


def coerce_score(item: Any) -> int:
    """Extract a score from multiple possible result shapes."""
    if isinstance(item, dict):
        lead_score = item.get("lead_score")
        if isinstance(lead_score, dict):
            return int(lead_score.get("score", 0))
        if hasattr(lead_score, "score"):
            return int(lead_score.score)
        if "score" in item:
            return int(item["score"])
    if hasattr(item, "lead_score") and hasattr(item.lead_score, "score"):
        return int(item.lead_score.score)
    return 0


def filter_qualified_leads(scores: Sequence[Any], threshold: int = DEFAULT_THRESHOLD) -> List[Any]:
    """Keep leads whose score exceeds the threshold."""
    return [score for score in scores if coerce_score(score) > threshold]


def route_by_volume(scores: Sequence[Any]) -> str:
    """Route a batch of leads based on batch size."""
    if len(scores) > 10:
        return "high"
    if len(scores) > 5:
        return "medium"
    return "low"


def normalize_leads(leads: Iterable[dict]) -> List[dict]:
    """Normalize raw lead dictionaries into CrewAI-compatible payloads."""
    return [LeadInput(**lead).to_crew_payload() for lead in leads]


class SimpleSalesPipeline(Flow):
    """Simple Flow implementation: fetch -> score -> filter -> write -> send."""

    def __init__(self, leads: list[dict] | None = None):
        super().__init__()
        self._input_leads = leads or []
        self.lead_scoring_crew = build_lead_scoring_crew() if CREWAI_AVAILABLE else None
        self.email_writing_crew = build_email_writing_crew() if CREWAI_AVAILABLE else None

    @start()
    def fetch_leads(self):
        """Pull leads from a source. In production, replace this with DB / CRM retrieval."""
        if self._input_leads:
            return normalize_leads(self._input_leads)

        demo_leads = [
            {
                "name": "João Moura",
                "job_title": "Director of Engineering",
                "company": "Clearbit",
                "email": "joao@clearbit.com",
                "use_case": "Using AI agents to improve data enrichment.",
            }
        ]
        return normalize_leads(demo_leads)

    @listen(fetch_leads)
    def score_leads(self, leads):
        """Run lead scoring crew against each lead."""
        if not self.lead_scoring_crew:
            raise RuntimeError("CrewAI is unavailable. Install dependencies to execute the Flow.")
        scores = self.lead_scoring_crew.kickoff_for_each(leads)
        self.state["score_crews_results"] = scores
        return scores

    @listen(score_leads)
    def store_leads_score(self, scores):
        """Persist scores. Placeholder for database or CRM integration."""
        self.state["stored_scores"] = scores
        return scores

    @listen(score_leads)
    def filter_leads(self, scores):
        """Filter qualified leads by threshold."""
        return filter_qualified_leads(scores)

    @listen(filter_leads)
    def write_email(self, leads):
        """Write emails for filtered leads."""
        if not self.email_writing_crew:
            raise RuntimeError("CrewAI is unavailable. Install dependencies to execute the Flow.")

        scored_leads = []
        for lead in leads:
            if hasattr(lead, "to_dict"):
                scored_leads.append(lead.to_dict())
            elif isinstance(lead, dict):
                scored_leads.append(lead)
            else:
                scored_leads.append({"lead_score": {"score": coerce_score(lead)}})

        emails = self.email_writing_crew.kickoff_for_each(scored_leads)
        self.state["emails"] = emails
        return emails

    @listen(write_email)
    def send_email(self, emails):
        """Placeholder for email sending integration."""
        self.state["sent_emails"] = emails
        return emails


class ComplexSalesPipeline(Flow):
    """Complex Flow implementation with conditional routing."""

    def __init__(self, leads: list[dict] | None = None):
        super().__init__()
        self._input_leads = leads or []
        self.lead_scoring_crew = build_lead_scoring_crew() if CREWAI_AVAILABLE else None
        self.email_writing_crew = build_email_writing_crew() if CREWAI_AVAILABLE else None

    @start()
    def fetch_leads(self):
        if self._input_leads:
            return normalize_leads(self._input_leads)

        demo_leads = [
            {
                "name": "João Moura",
                "job_title": "Director of Engineering",
                "company": "Clearbit",
                "email": "joao@clearbit.com",
                "use_case": "Using AI agents to improve data enrichment.",
            }
        ]
        return normalize_leads(demo_leads)

    @listen(fetch_leads)
    def score_leads(self, leads):
        if not self.lead_scoring_crew:
            raise RuntimeError("CrewAI is unavailable. Install dependencies to execute the Flow.")
        scores = self.lead_scoring_crew.kickoff_for_each(leads)
        self.state["score_crews_results"] = scores
        return scores

    @listen(score_leads)
    def store_leads_score(self, scores):
        self.state["stored_scores"] = scores
        return scores

    @listen(score_leads)
    def filter_leads(self, scores):
        return filter_qualified_leads(scores)

    @listen(and_(filter_leads, store_leads_score))
    def log_leads(self, leads):
        self.state["logged_leads"] = leads
        return leads

    @router(filter_leads, paths=["high", "medium", "low"])
    def count_leads(self, scores):
        bucket = route_by_volume(scores)
        self.state["routing_bucket"] = bucket
        return bucket

    @listen("high")
    def store_in_salesforce(self, leads):
        self.state["salesforce_batch"] = leads
        return leads

    @listen("medium")
    def send_to_sales_team(self, leads):
        self.state["sales_team_batch"] = leads
        return leads

    @listen("low")
    def write_email(self, leads):
        if not self.email_writing_crew:
            raise RuntimeError("CrewAI is unavailable. Install dependencies to execute the Flow.")

        scored_leads = []
        for lead in leads:
            if hasattr(lead, "to_dict"):
                scored_leads.append(lead.to_dict())
            elif isinstance(lead, dict):
                scored_leads.append(lead)
            else:
                scored_leads.append({"lead_score": {"score": coerce_score(lead)}})

        emails = self.email_writing_crew.kickoff_for_each(scored_leads)
        self.state["emails"] = emails
        return emails

    @listen(write_email)
    def send_email(self, emails):
        self.state["sent_emails"] = emails
        return emails
