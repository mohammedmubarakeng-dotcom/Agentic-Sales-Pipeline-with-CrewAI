# API Documentation

This repository is primarily organized as a Python package + runnable demo.

## Modules

### `src/models.py`

#### `LeadPersonalInfo`
Structured information about the lead.

Fields:
- `name: str`
- `job_title: str`
- `role_relevance: int`
- `professional_background: Optional[str]`

#### `CompanyInfo`
Structured company information.

Fields:
- `company_name: str`
- `industry: str`
- `company_size: int`
- `revenue: Optional[float]`
- `market_presence: int`

#### `LeadScore`
Validated lead scoring metadata.

Fields:
- `score: int`
- `scoring_criteria: List[str]`
- `validation_notes: Optional[str]`

#### `LeadScoringResult`
Top-level output schema.

Fields:
- `personal_info: LeadPersonalInfo`
- `company_info: CompanyInfo`
- `lead_score: LeadScore`

#### `LeadInput`
Input model for inbound leads.

Methods:
- `to_crew_payload() -> dict`

Example:
```python
from models import LeadInput

lead = LeadInput(
    name="Sarah Chen",
    job_title="VP Revenue Operations",
    company="Northstar Analytics",
    email="sarah@example.com",
    use_case="Automating lead qualification."
)

payload = lead.to_crew_payload()
```

---

### `src/crews.py`

#### `load_configs(config_dir=CONFIG_DIR) -> dict`
Loads all YAML configuration files.

#### `get_research_tools() -> list`
Returns web research tools for CrewAI agents.

#### `build_lead_scoring_crew(config_dir=CONFIG_DIR)`
Builds the 3-agent lead qualification crew.

#### `build_email_writing_crew(config_dir=CONFIG_DIR)`
Builds the 2-agent email engagement crew.

Example:
```python
from crews import build_lead_scoring_crew

crew = build_lead_scoring_crew()
result = crew.kickoff(inputs={
    "lead_data": {
        "name": "Sarah Chen",
        "job_title": "VP Revenue Operations",
        "company": "Northstar Analytics",
        "email": "sarah@example.com",
        "use_case": "Automating lead qualification."
    }
})
```

---

### `src/flow.py`

#### Utility functions

##### `estimate_token_cost(total_tokens, input_cost_per_million=0.150, output_cost_per_million=0.0) -> float`
Estimates token cost for a workflow run.

##### `coerce_score(item) -> int`
Extracts a score from multiple result shapes.

##### `filter_qualified_leads(scores, threshold=70) -> list`
Returns only scores above the configured threshold.

##### `route_by_volume(scores) -> str`
Returns:
- `"high"` if lead count > 10
- `"medium"` if lead count > 5
- `"low"` otherwise

##### `normalize_leads(leads) -> list`
Converts raw lead dicts into CrewAI-compatible payloads.

---

## Flow classes

### `SimpleSalesPipeline`
Implements:

```text
fetch_leads -> score_leads -> store_leads_score -> filter_leads -> write_email -> send_email
```

### `ComplexSalesPipeline`
Implements:

```text
fetch_leads -> score_leads -> store_leads_score -> filter_leads -> count_leads
                                                  ├─ high   -> store_in_salesforce
                                                  ├─ medium -> send_to_sales_team
                                                  └─ low    -> write_email -> send_email
```

---

## Example usage

```python
from flow import ComplexSalesPipeline

leads = [
    {
        "name": "Sarah Chen",
        "job_title": "VP Revenue Operations",
        "company": "Northstar Analytics",
        "email": "sarah@example.com",
        "use_case": "Automating lead qualification and outbound research."
    }
]

pipeline = ComplexSalesPipeline(leads=leads)
result = pipeline.kickoff()
```

---

## Notes for production use

In a client deployment, the following integrations are common:
- CRM ingestion from Salesforce / HubSpot
- outbound email via Gmail, Outlook, SendGrid, or Instantly
- webhook triggers
- Slack / Teams notifications
- observability, retries, and approval workflows

This repo is intentionally structured so those additions can be layered on cleanly.
