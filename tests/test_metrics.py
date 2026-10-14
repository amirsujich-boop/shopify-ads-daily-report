import json
from pathlib import Path

from adsreport.meta import _flatten, _pick
from adsreport.metrics import summarise

FIX = Path(__file__).parent.parent / "fixtures"


def load():
    orders = json.loads((FIX / "orders.json").read_text())["orders"]
    rows = [_flatten(x) for x in json.loads((FIX / "insights.json").read_text())["data"]]
    return orders, rows


def test_refund_and_cancellation_handling():
    orders, rows = load()
    # the CLI filters cancelled orders at fetch time; summarise() takes what it is given
    live = [o for o in orders if not o.get("cancelled_at")]
    s = summarise(live, rows)
    assert s.orders == 4
    assert s.refunds == 59.0
    assert round(s.revenue, 2) == round(89.90 + 149.00 + 0.0 + 210.50, 2)
    assert s.currency == "EUR"


def test_ad_totals_and_ratios():
    orders, rows = load()
    live = [o for o in orders if not o.get("cancelled_at")]
    s = summarise(live, rows)
    assert round(s.spend, 2) == 180.50
    assert s.impressions == 58600
    assert s.attributed_purchases == 5
    assert round(s.platform_roas, 3) == round(565.90 / 180.50, 3)
    assert round(s.roas, 3) == round(449.40 / 180.50, 3)
    assert round(s.cpa, 3) == round(180.50 / 4, 3)
    assert s.campaigns[0]["campaign"].startswith("Prospecting")  # sorted by spend desc
    assert s.campaigns[-1]["cpa"] == 0.0  # no purchases → no division by zero


def test_pick_missing_action_type():
    assert _pick([{"action_type": "lead", "value": "4"}], "purchase") == 0.0
    assert _pick(None, "purchase") == 0.0


def test_zero_day_does_not_crash():
    s = summarise([], [])
    assert s.roas == 0.0 and s.aov == 0.0 and s.cpa == 0.0 and s.ctr == 0.0
