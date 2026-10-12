from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

from .meta import MetaAdsClient
from .metrics import summarise
from .report import render
from .shopify import ShopifyClient


def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"missing environment variable {name}")
    return v


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="adsreport", description="Shopify + Meta Ads daily report")
    p.add_argument("--date", help="YYYY-MM-DD (default: yesterday)")
    p.add_argument("--tz", default="+00:00", help="store timezone offset for the order window, e.g. +01:00")
    p.add_argument("--target-roas", type=float, help="flag the day as above/below this blended ROAS")
    p.add_argument("--out", help="write Markdown here instead of stdout")
    p.add_argument("--slack", action="store_true", help="also post to SLACK_WEBHOOK_URL")
    p.add_argument("--from-fixtures", metavar="DIR", help="read orders.json / insights.json from DIR instead of the APIs")
    a = p.parse_args(argv)

    day = dt.date.fromisoformat(a.date) if a.date else dt.date.today() - dt.timedelta(days=1)

    if a.from_fixtures:
        d = Path(a.from_fixtures)
        orders = [o for o in json.loads((d / "orders.json").read_text())["orders"] if not o.get("cancelled_at")]
        from .meta import _flatten
        ad_rows = [_flatten(x) for x in json.loads((d / "insights.json").read_text())["data"]]
    else:
        shop = ShopifyClient(_env("SHOPIFY_SHOP"), _env("SHOPIFY_TOKEN"))
        meta = MetaAdsClient(_env("META_AD_ACCOUNT_ID"), _env("META_ACCESS_TOKEN"))
        orders = list(shop.orders(day, tz=a.tz))
        ad_rows = meta.insights(day)

    md = render(day, summarise(orders, ad_rows), target_roas=a.target_roas)

    if a.out:
        Path(a.out).write_text(md)
    else:
        print(md)
    if a.slack:
        from .slack import post
        post(_env("SLACK_WEBHOOK_URL"), md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
