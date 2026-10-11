"""Pull campaign-level spend and purchase conversions from the Meta Marketing API."""
from __future__ import annotations

import datetime as dt

import requests

API_VERSION = "v21.0"


class MetaAdsClient:
    def __init__(self, account_id: str, token: str, session: requests.Session | None = None):
        self.account = account_id if account_id.startswith("act_") else f"act_{account_id}"
        self.token = token
        self.s = session or requests.Session()

    def insights(self, day: dt.date) -> list[dict]:
        """Campaign rows for one day: name, spend, impressions, clicks, purchases, purchase value."""
        url = f"https://graph.facebook.com/{API_VERSION}/{self.account}/insights"
        params = {
            "access_token": self.token,
            "level": "campaign",
            "time_range": f'{{"since":"{day.isoformat()}","until":"{day.isoformat()}"}}',
            "fields": "campaign_name,spend,impressions,clicks,actions,action_values",
            "limit": 500,
        }
        rows: list[dict] = []
        while url:
            r = self.s.get(url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            rows.extend(_flatten(x) for x in data.get("data", []))
            url = data.get("paging", {}).get("next")
            params = None
        return rows


def _pick(items: list[dict] | None, action_type: str) -> float:
    for it in items or []:
        if it.get("action_type") == action_type:
            return float(it.get("value", 0))
    return 0.0


def _flatten(row: dict) -> dict:
    return {
        "campaign": row.get("campaign_name", ""),
        "spend": float(row.get("spend", 0)),
        "impressions": int(row.get("impressions", 0)),
        "clicks": int(row.get("clicks", 0)),
        "purchases": _pick(row.get("actions"), "purchase"),
        "purchase_value": _pick(row.get("action_values"), "purchase"),
    }
