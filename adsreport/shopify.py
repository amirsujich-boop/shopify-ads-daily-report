"""Pull orders from the Shopify Admin REST API for one day."""
from __future__ import annotations

import datetime as dt
from typing import Iterator

import requests

API_VERSION = "2024-10"


class ShopifyClient:
    def __init__(self, shop: str, token: str, session: requests.Session | None = None):
        # shop is the myshopify subdomain, e.g. "my-store" or "my-store.myshopify.com"
        self.shop = shop.replace(".myshopify.com", "")
        self.base = f"https://{self.shop}.myshopify.com/admin/api/{API_VERSION}"
        self.s = session or requests.Session()
        self.s.headers.update({"X-Shopify-Access-Token": token, "Accept": "application/json"})

    def orders(self, day: dt.date, tz: str = "+00:00") -> Iterator[dict]:
        """Yield paid orders created on `day`. Follows `Link` pagination."""
        start = f"{day.isoformat()}T00:00:00{tz}"
        end = f"{(day + dt.timedelta(days=1)).isoformat()}T00:00:00{tz}"
        url = f"{self.base}/orders.json"
        params = {
            "status": "any",
            "financial_status": "paid",
            "created_at_min": start,
            "created_at_max": end,
            "limit": 250,
            "fields": "id,created_at,total_price,subtotal_price,total_discounts,currency,line_items,refunds,cancelled_at",
        }
        while url:
            r = self.s.get(url, params=params, timeout=30)
            r.raise_for_status()
            for o in r.json().get("orders", []):
                if o.get("cancelled_at"):
                    continue
                yield o
            url = _next_link(r.headers.get("Link", ""))
            params = None  # page_info links already carry the query


def _next_link(header: str) -> str | None:
    for part in header.split(","):
        if 'rel="next"' in part:
            return part.split(";")[0].strip().strip("<>")
    return None
