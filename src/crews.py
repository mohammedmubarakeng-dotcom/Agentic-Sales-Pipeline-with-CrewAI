"""Crew definitions extracted and hardened from the notebook implementation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from models import LeadScoringResult

try:
    from crewai import Agent, Crew, Task
    from crewai_tools import ScrapeWebsiteTool, SerperDevTool
    CREWAI_AVAILABLE = True
except ImportError:  # pragma: no cover - makes unit tests importable without CrewAI installed
    Agent = Crew = Task = object  # type: ignore
    ScrapeWebsiteTool = SerperDevTool = object  # type: ignore
    CREWAI_AVAILABLE = False


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT_DIR / "config"


def load_configs(config_dir: Path = CONFIG_DIR) -> Dict[str, Dict[str, Any]]:
    """Load YAML configuration files."""
    files = {
        "lead_agents": config_dir / "lead_qualification_agents.yaml",
        "lead_tasks": config_dir / "lead_qualification_tasks.yaml",
        "email_agents": config_dir / "email_engagement_agents.yaml",
        "email_tasks": config_dir / "email_engagement_tasks.yaml",
    }

    configs: Dict[str, Dict[str, Any]] = {}
    for key, filepath in files.items():
        with filepath.open("r", encoding="utf-8") as f:
            configs[key] = yaml.safe_load(f)
    return configs


def get_research_tools() -> list:
    """Return external research tools used by the lead qualification crew."""
    if not CREWAI_AVAILABLE:
        return []
    return [SerperDevTool(), ScrapeWebsiteTool()]


def build_lead_scoring_crew(config_dir: Path = CONFIG_DIR):
    """Build the lead qualification crew."""
    if not CREWAI_AVAILABLE:
        raise ImportError("CrewAI is not installed. Run `pip install -r requirements.txt`.")

    load_dotenv()
    configs = load_configs(config_dir)

    lead_agents_config = configs["lead_agents"]
    lead_tasks_config = configs["lead_tasks"]

    lead_data_agent = Agent(
        config=lead_agents_config["lead_data_agent"],
        tools=get_research_tools(),
    )

    cultural_fit_agent = Agent(
        config=lead_agents_config["cultural_fit_agent"],
        tools=get_research_tools(),
    )

    scoring_validation_agent = Agent(
        config=lead_agents_config["scoring_validation_agent"],
        tools=get_research_tools(),
    )

    lead_data_task = Task(
        config=lead_tasks_config["lead_data_collection"],
        agent=lead_data_agent,
    )

    cultural_fit_task = Task(
        config=lead_tasks_config["cultural_fit_analysis"],
        agent=cultural_fit_agent,
    )

    scoring_validation_task = Task(
        config=lead_tasks_config["lead_scoring_and_validation"],
        agent=scoring_validation_agent,
        context=[lead_data_task, cultural_fit_task],
        output_pydantic=LeadScoringResult,
    )

    return Crew(
        agents=[
            lead_data_agent,
            cultural_fit_agent,
            scoring_validation_agent,
        ],
        tasks=[
            lead_data_task,
            cultural_fit_task,
            scoring_validation_task,
        ],
        verbose=True,
    )


def build_email_writing_crew(config_dir: Path = CONFIG_DIR):
    """Build the email engagement crew."""
    if not CREWAI_AVAILABLE:
        raise ImportError("CrewAI is not installed. Run `pip install -r requirements.txt`.")

    load_dotenv()
    configs = load_configs(config_dir)

    email_agents_config = configs["email_agents"]
    email_tasks_config = configs["email_tasks"]

    email_content_specialist = Agent(
        config=email_agents_config["email_content_specialist"],
    )

    engagement_strategist = Agent(
        config=email_agents_config["engagement_strategist"],
    )

    email_drafting = Task(
        config=email_tasks_config["email_drafting"],
        agent=email_content_specialist,
    )

    engagement_optimization = Task(
        config=email_tasks_config["engagement_optimization"],
        agent=engagement_strategist,
    )

    return Crew(
        agents=[
            email_content_specialist,
            engagement_strategist,
        ],
        tasks=[
            email_drafting,
            engagement_optimization,
        ],
        verbose=True,
    )
