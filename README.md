# shopify-ads-daily-report

One command that answers the question every store owner asks at 8 a.m.: **"did yesterday's ads pay for themselves?"**

It pulls yesterday's paid orders from Shopify and campaign spend from Meta Ads, computes the numbers that matter, and writes a short Markdown report. Optionally posts it to Slack. Runs for free on GitHub Actions.

```
# Daily report · Tue 14 Oct 2025

## Store
- Orders: **4**
- Revenue (net of refunds): **449.40 EUR**
- AOV: 112.35 EUR

## Meta Ads
- Spend: **180.50 EUR**
- Blended ROAS: **2.49x** ⚠️ below target 3.0x  ·  MER: 40.16%
- Platform ROAS (Meta attributed): 3.14x on 5 purchases
- CPA (spend / all orders): 45.13 EUR

| Campaign | Spend | Purch. | ROAS | CPA |
|---|---:|---:|---:|---:|
| Prospecting · Broad · Video | 120.40 | 3 | 2.72x | 40.13 |
| Retargeting · 30d visitors | 38.10 | 2 | 6.25x | 19.05 |
| Catalog · DPA | 22.00 | 0 | 0.00x | 0.00 |

> Meta reports more purchase value than the store took in. Expect this on days with view-through
> attribution or a 7-day click window catching up on earlier orders. Trust the blended number.
```

## Why blended ROAS

Meta's own ROAS counts a purchase if the buyer saw or clicked an ad in the last 7 days (or 1 day for views). On a normal day that overstates by 20–60 %. The report shows both:

- **Blended ROAS** = all store revenue ÷ all ad spend. Cannot be gamed by attribution windows. This is the one to make decisions on.
- **Platform ROAS** = what Ads Manager shows. Useful per campaign, for relative comparison only.

Revenue is net of refunds and excludes cancelled orders, so a bad day looks bad.

## Install

```bash
pip install git+https://github.com/amirsujich-boop/shopify-ads-daily-report
cp .env.example .env   # fill in tokens, then: export $(cat .env | xargs)
adsreport --tz "+01:00" --target-roas 3
```

Try it without any credentials:

```bash
adsreport --from-fixtures fixtures --date 2025-10-14 --target-roas 3
```

### Credentials

| Variable | Where to get it |
|---|---|
| `SHOPIFY_SHOP` | the `xxx` in `xxx.myshopify.com` |
| `SHOPIFY_TOKEN` | Shopify admin → Settings → Apps → Develop apps → create one with `read_orders` → Admin API access token |
| `META_AD_ACCOUNT_ID` | Ads Manager URL, `act=1234567890` |
| `META_ACCESS_TOKEN` | Business Settings → System users → generate token with `ads_read` (does not expire) |
| `SLACK_WEBHOOK_URL` | optional, Slack app → Incoming webhooks |

## Run it every morning on GitHub Actions

1. Fork this repo (private forks are fine).
2. Settings → Secrets and variables → Actions → add the five variables above as secrets.
3. Variables tab → add `ENABLE_DAILY_REPORT` = `true` (the scheduled job stays off without it, so a fresh fork does not fail every morning).
4. Done. `.github/workflows/daily.yml` runs at 06:15 UTC, posts to Slack and keeps each report as a build artifact. Adjust `--tz` and `--target-roas` in that file.

## CLI

```
adsreport [--date YYYY-MM-DD] [--tz +01:00] [--target-roas 3] [--out file.md] [--slack] [--from-fixtures DIR]
```

## Extending

- Google Ads / TikTok: add a client that returns rows shaped like `meta._flatten()` (`campaign, spend, impressions, clicks, purchases, purchase_value`) and concatenate them before `summarise()`. Blended ROAS then becomes truly blended.
- Weekly roll-up: call `summarise()` with seven days of orders and rows; the maths does not care.
- Different output: `report.render()` returns a string; swap it for an HTML or Google Sheets writer.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

MIT.
