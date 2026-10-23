from __future__ import annotations

import requests


def post(webhook_url: str, markdown: str) -> None:
    """Send the report to a Slack incoming webhook. Slack's mrkdwn is close enough to Markdown for this."""
    text = markdown.replace("**", "*").replace("# ", "").replace("## ", "*").replace("|---|---:|---:|---:|---:|\n", "")
    r = requests.post(webhook_url, json={"text": text}, timeout=15)
    r.raise_for_status()
