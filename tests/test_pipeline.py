from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flow import coerce_score, estimate_token_cost, filter_qualified_leads, normalize_leads, route_by_volume


def test_coerce_score_from_dict():
    payload = {"lead_score": {"score": 88}}
    assert coerce_score(payload) == 88


def test_filter_qualified_leads_threshold():
    scores = [
        {"lead_score": {"score": 55}},
        {"lead_score": {"score": 71}},
        {"lead_score": {"score": 99}},
    ]
    filtered = filter_qualified_leads(scores, threshold=70)
    assert len(filtered) == 2


def test_route_by_volume_low():
    assert route_by_volume([1, 2, 3]) == "low"


def test_route_by_volume_medium():
    assert route_by_volume([1, 2, 3, 4, 5, 6]) == "medium"


def test_route_by_volume_high():
    assert route_by_volume(list(range(11))) == "high"


def test_estimate_token_cost():
    cost = estimate_token_cost(total_tokens=1_000_000, input_cost_per_million=0.15)
    assert cost == 0.15


def test_normalize_leads():
    leads = [
        {
            "name": "Alice Johnson",
            "job_title": "VP Sales",
            "company": "Acme",
            "email": "alice@acme.com",
            "use_case": "Need AI lead scoring.",
        }
    ]
    normalized = normalize_leads(leads)
    assert normalized[0]["lead_data"]["company"] == "Acme"
