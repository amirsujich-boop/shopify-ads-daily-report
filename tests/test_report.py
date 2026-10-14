import datetime as dt
import json
from pathlib import Path

from adsreport.cli import main
from adsreport.meta import _flatten
from adsreport.metrics import summarise
from adsreport.report import render

FIX = Path(__file__).parent.parent / "fixtures"


def test_render_contains_key_numbers():
    orders = [o for o in json.loads((FIX / "orders.json").read_text())["orders"] if not o["cancelled_at"]]
    rows = [_flatten(x) for x in json.loads((FIX / "insights.json").read_text())["data"]]
    md = render(dt.date(2025, 10, 14), summarise(orders, rows), target_roas=3.0)
    assert "Orders: **4**" in md
    assert "Spend: **180.50 EUR**" in md
    assert "Blended ROAS: **2.49x** ⚠️ below target 3.0x" in md
    assert "| Prospecting · Broad · Video | 120.40 | 3 | 2.72x | 40.13 |" in md
    assert "Meta reports more purchase value" in md  # 565.90 vs 449.40 → warning shown


def test_cli_from_fixtures(tmp_path, capsys):
    out = tmp_path / "r.md"
    assert main(["--from-fixtures", str(FIX), "--date", "2025-10-14", "--out", str(out)]) == 0
    text = out.read_text()
    assert text.startswith("# Daily report · Tue 14 Oct 2025")
    assert "Orders: **4**" in text
