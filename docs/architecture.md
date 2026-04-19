# Architecture Overview

## Summary

This project implements an **agentic sales pipeline** that combines:
- multi-agent lead qualification
- structured scoring outputs
- personalized email drafting
- Flow-based routing logic
- cost-awareness for LLM usage

It is designed as a portfolio-quality foundation that can be adapted for:
- outbound prospecting
- inbound lead triage
- RevOps enrichment workflows
- AI-assisted sales development pipelines

---

## Core design principles

### 1. Specialized agents over monolithic prompts
Instead of asking one large prompt to do everything, the system divides work among focused agents:
- **Lead Data Agent** gathers factual context
- **Cultural Fit Agent** interprets strategic alignment
- **Scoring Validation Agent** converts findings into a structured score
- **Email Content Specialist** drafts outreach
- **Engagement Strategist** improves clarity and conversion

This separation improves maintainability, evaluation, and future extensibility.

### 2. Structured outputs for reliability
The lead qualification crew returns a `LeadScoringResult` Pydantic object with:
- `personal_info`
- `company_info`
- `lead_score`

This makes it easier to:
- validate responses
- store outputs in databases
- send clean payloads to CRMs or APIs
- build downstream routing logic

### 3. Configuration-driven behavior
Agent definitions and task prompts are stored in YAML files under `config/`.
This makes it easy to update:
- roles
- goals
- backstories
- task instructions
- expected outputs

without rewriting application logic.

### 4. Flow orchestration
The pipeline is implemented using CrewAI Flow patterns.

The simple pipeline follows this sequence:

```text
fetch_leads -> score_leads -> store_leads_score -> filter_leads -> write_email -> send_email
```

The complex pipeline adds conditional routing:

```text
fetch_leads -> score_leads -> filter_leads -> route_by_volume
                                 ├─ high   -> store_in_salesforce
                                 ├─ medium -> send_to_sales_team
                                 └─ low    -> write_email -> send_email
```

### 5. Research tools
The lead qualification crew uses:
- `SerperDevTool`
- `ScrapeWebsiteTool`

These allow the agents to:
- search the web
- inspect websites
- enrich company context
- support more informed scoring decisions

### 6. Cost awareness
The demo includes token usage cost estimation utilities. In client projects, this can be expanded to:
- per-agent cost attribution
- per-run cost dashboards
- budget thresholds
- optimization reporting

---

## Components

## `src/models.py`
Contains the structured schemas for lead research and scoring.

Key models:
- `LeadPersonalInfo`
- `CompanyInfo`
- `LeadScore`
- `LeadScoringResult`
- `LeadInput`

## `src/crews.py`
Responsible for:
- loading YAML configuration
- building lead qualification crew
- building email engagement crew
- attaching research tools where needed

## `src/flow.py`
Contains:
- helper functions for filtering and routing
- cost estimation utilities
- `SimpleSalesPipeline`
- `ComplexSalesPipeline`

## `examples/demo.py`
Provides a runnable demo with example leads.

## `tests/test_pipeline.py`
Validates routing, normalization, filtering, and cost estimation behavior.

---

## Data flow

### Input
The pipeline accepts lead records such as:

```python
{
    "name": "Sarah Chen",
    "job_title": "VP of Revenue Operations",
    "company": "Northstar Analytics",
    "email": "sarah.chen@northstar-analytics.com",
    "use_case": "Automating lead qualification and personalized outbound workflows."
}
```

### Internal transformation
The lead is normalized into:

```python
{
    "lead_data": {
        "name": "...",
        "job_title": "...",
        "company": "...",
        "email": "...",
        "use_case": "..."
    }
}
```

This format is then passed into CrewAI crews.

### Output
Lead scoring returns structured data that can be saved, routed, or sent downstream for further action.

Possible downstream actions:
- store in CRM
- queue for SDR review
- trigger personalized nurture email
- push to webhook / automation platform

---

## Extension ideas for client work

This portfolio version is intentionally modular so it can be extended into premium client engagements.

Examples:
- HubSpot / Salesforce sync
- Apollo / Clay / Clearbit enrichment
- Gmail / Outlook delivery
- Slack notifications
- lead deduplication
- account-level scoring
- prompt evaluation harness
- reporting dashboards
- human-in-the-loop approval step
- multilingual outbound personalization

---

## Premium implementation roadmap

### Phase 1 — Discovery
- define ICP and qualification logic
- map source systems
- identify routing rules
- define outreach constraints

### Phase 2 — Prototype
- implement agents and tasks
- configure scoring output
- build initial flow
- run against sample data

### Phase 3 — Productionization
- connect CRM / email tools
- add logging and observability
- harden prompts
- define fallback logic
- add deployment workflow

### Phase 4 — Optimization
- A/B test messaging
- compare scoring against actual outcomes
- refine thresholds
- measure ROI and cost per workflow run

---

## Recommended client positioning

This architecture is especially attractive to:
- SaaS founders
- outbound agencies
- RevOps teams
- fractional GTM consultants
- technical sales operators

It demonstrates both:
1. **business relevance**, and
2. **technical implementation maturity**
