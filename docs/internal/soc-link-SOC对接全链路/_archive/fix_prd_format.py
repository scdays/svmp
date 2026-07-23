# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(__file__).parent
p = ROOT / "vuln-task-center-\u626b\u63cf\u6cbb\u7406\u4e2d\u5fc3-PRD.md"
text = p.read_text(encoding="utf-8")
text = text.replace("| ? |", "| \u2705 |")
text = re.sub(r"\n{3,}", "\n\n", text)
lines = text.split("\n")
out = []
for i, line in enumerate(lines):
    if line.strip() == "" and out and i + 1 < len(lines):
        prev, nxt = out[-1], lines[i + 1]
        if prev.lstrip().startswith("|") and nxt.lstrip().startswith("|"):
            continue
    out.append(line)
text = "\n".join(out)
p.write_text(text, encoding="utf-8")
print("fixed", len(text))
