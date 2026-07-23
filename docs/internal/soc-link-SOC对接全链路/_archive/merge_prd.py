# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).parent


def read_chunk(path):
    raw = path.read_bytes()
    for enc in ("utf-8", "gbk", "utf-8-sig"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


parts = [
    read_chunk(ROOT / "prd-part-before-43.md"),
    read_chunk(ROOT / "_ah_section_43.md"),
    read_chunk(ROOT / "prd-part-after-43.md"),
]
html = "".join(parts)
out = ROOT / "vuln-task-center-\u626b\u63cf\u6cbb\u7406\u4e2d\u5fc3-PRD.md"
out.write_text(html, encoding="utf-8")
marker = "\u5b89\u6052\u660e\u9274"
print("OK", out, len(html), marker in html)
