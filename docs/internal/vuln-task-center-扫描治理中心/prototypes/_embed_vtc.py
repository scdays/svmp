# -*- coding: utf-8 -*-
from pathlib import Path

proto = Path(__file__).resolve().parent
html = (proto / "vuln-task-center-governance-prototype.html").read_text(encoding="utf-8")
if '"""' in html:
    raise SystemExit("HTML contains triple double-quotes")
build = proto / "build_vtc_governance_proto.py"
text = build.read_text(encoding="utf-8")
if "___VTC_HTML_PLACEHOLDER___" not in text:
    raise SystemExit("placeholder not found")
text = text.replace("___VTC_HTML_PLACEHOLDER___", html)
build.write_text(text, encoding="utf-8")
print("embedded", len(html), "chars")
