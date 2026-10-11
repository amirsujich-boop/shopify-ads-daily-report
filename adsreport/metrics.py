"""Pure functions: raw orders + ad rows → the numbers that go in the report."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Summary:
    orders: int = 0
    revenue: float = 0.0          # net of refunds and discounts
    refunds: float = 0.0
    discounts: float = 0.0
    currency: str = ""
    spend: float = 0.0
    impressions: int = 0
    clicks: int = 0
    attributed_purchases: float = 0.0
    attributed_value: float = 0.0
    campaigns: list[dict] = field(default_factory=list)

    # ---- derived -------------------------------------------------------
    @property
    def aov(self) -> float:
        return self.revenue / self.orders if self.orders else 0.0

    @property
    def roas(self) -> float:
        """Blended: all store revenue / all ad spend. The honest number."""
        return self.revenue / self.spend if self.spend else 0.0

    @property
    def cpa(self) -> float:
        return self.spend / self.orders if self.orders else 0.0

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions else 0.0

    @property
    def cpc(self) -> float:
        return self.spend / self.clicks if self.clicks else 0.0


def summarise(orders: list[dict], ad_rows: list[dict]) -> Summary:
    s = Summary()
    for o in orders:
        s.orders += 1
        refunded = sum(
            float(t.get("amount", 0))
            for r in o.get("refunds", [])
            for t in r.get("transactions", [])
            if t.get("kind") == "refund" and t.get("status") == "success"
        )
        s.refunds += refunded
        s.discounts += float(o.get("total_discounts", 0))
        s.revenue += float(o.get("total_price", 0)) - refunded
        s.currency = s.currency or o.get("currency", "")

    for row in ad_rows:
        s.spend += row["spend"]
        s.impressions += row["impressions"]
        s.clicks += row["clicks"]
        s.attributed_purchases += row["purchases"]
        s.attributed_value += row["purchase_value"]
        s.campaigns.append(
            {
                **row,
                "roas": row["purchase_value"] / row["spend"] if row["spend"] else 0.0,
                "cpa": row["spend"] / row["purchases"] if row["purchases"] else 0.0,
            }
        )
    s.campaigns.sort(key=lambda c: c["spend"], reverse=True)
    return s
