# -*- coding: utf-8 -*-
"""Generate vuln-task-center governance prototype with correct UTF-8."""
from pathlib import Path

OUT = Path(__file__).with_name("vuln-task-center-governance-prototype.html")
HTML = """___VTC_HTML_PLACEHOLDER___"""
OUT.write_text(HTML, encoding="utf-8")
print("written:", OUT, "bytes:", OUT.stat().st_size)
