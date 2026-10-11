"""Render a Summary as Markdown (works in GitHub, Notion, Slack mrkdwn-ish)."""
from __future__ import annotations

import datetime as dt

from .metrics import Summary


def _money(x: float, cur: str) -> str:
    return f"{x:,.2f} {cur}".strip()


def _pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def render(day: dt.date, s: Summary, target_roas: float | None = None) -> str:
    cur = s.currency
    lines = [f"# Daily report · {day.strftime('%a %d %b %Y')}", ""]

    verdict = ""
    if target_roas and s.spend:
        verdict = " ✅ above target" if s.roas >= target_roas else f" ⚠️ below target {target_roas:.1f}x"

    lines += [
        "## Store",
        f"- Orders: **{s.orders}**",
        f"- Revenue (net of refunds): **{_money(s.revenue, cur)}**",
        f"- AOV: {_money(s.aov, cur)}",
        f"- Discounts given: {_money(s.discounts, cur)}  ·  Refunds: {_money(s.refunds, cur)}",
        "",
        "## Meta Ads",
        f"- Spend: **{_money(s.spend, cur)}**",
        f"- ROAS: **{s.roas:.2f}x**{verdict}",
        f"- CPA (spend / all orders): {_money(s.cpa, cur)}",
        f"- Impressions: {s.impressions:,}  ·  Clicks: {s.clicks:,}  ·  CTR: {_pct(s.ctr)}  ·  CPC: {_money(s.cpc, cur)}",
        "",
    ]

    if s.campaigns:
        lines += ["## Campaigns", "", "| Campaign | Spend | Purch. | ROAS | CPA |", "|---|---:|---:|---:|---:|"]
        for c in s.campaigns:
            lines.append(
                f"| {c['campaign']} | {c['spend']:,.2f} | {c['purchases']:.0f} | {c['roas']:.2f}x | {c['cpa']:,.2f} |"
            )
        lines.append("")

    return "\n".join(lines)
