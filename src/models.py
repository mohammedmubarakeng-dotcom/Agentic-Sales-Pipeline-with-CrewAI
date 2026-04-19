"""Pydantic models for the Agentic Sales Pipeline."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class LeadPersonalInfo(BaseModel):
    """Personal information about the lead."""

    name: str = Field(..., description="The full name of the lead.")
    job_title: str = Field(..., description="The job title of the lead.")
    role_relevance: int = Field(
        ...,
        ge=0,
        le=10,
        description="A score representing how relevant the lead's role is to the decision-making process (0-10).",
    )
    professional_background: Optional[str] = Field(
        default=None,
        description="A brief description of the lead's professional background.",
    )


class CompanyInfo(BaseModel):
    """Company information associated with the lead."""

    company_name: str = Field(..., description="The name of the company the lead works for.")
    industry: str = Field(..., description="The industry in which the company operates.")
    company_size: int = Field(..., description="The size of the company in employee count.")
    revenue: Optional[float] = Field(
        default=None,
        description="The annual revenue of the company, if available.",
    )
    market_presence: int = Field(
        ...,
        ge=0,
        le=10,
        description="A score representing the company's market presence (0-10).",
    )


class LeadScore(BaseModel):
    """Lead score and validation information."""

    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="The final score assigned to the lead (0-100).",
    )
    scoring_criteria: List[str] = Field(
        ...,
        description="The criteria used to determine the lead's score.",
    )
    validation_notes: Optional[str] = Field(
        default=None,
        description="Any notes regarding the validation of the lead score.",
    )


class LeadScoringResult(BaseModel):
    """Final structured output for lead qualification."""

    personal_info: LeadPersonalInfo = Field(
        ...,
        description="Personal information about the lead.",
    )
    company_info: CompanyInfo = Field(
        ...,
        description="Information about the lead's company.",
    )
    lead_score: LeadScore = Field(
        ...,
        description="The calculated score and related information for the lead.",
    )


class LeadInput(BaseModel):
    """Input payload for a lead entering the pipeline."""

    name: str = Field(..., description="Full name of the lead.")
    job_title: str = Field(..., description="Job title of the lead.")
    company: str = Field(..., description="Company name.")
    email: str = Field(..., description="Email address for outreach.")
    use_case: str = Field(..., description="Primary problem or use case to address.")

    def to_crew_payload(self) -> dict:
        """Convert the lead into the payload structure expected by CrewAI tasks."""
        return {
            "lead_data": {
                "name": self.name,
                "job_title": self.job_title,
                "company": self.company,
                "email": self.email,
                "use_case": self.use_case,
            }
        }
