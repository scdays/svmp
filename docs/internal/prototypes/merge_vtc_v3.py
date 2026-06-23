# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).parent
chunks = [ROOT / ("v3-chunk-%d.html" % i) for i in range(1, 7)]


def read_chunk(path):
    raw = path.read_bytes()
    for enc in ("utf-8", "gbk", "utf-8-sig"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


html = "".join(read_chunk(p) for p in chunks)
out = ROOT / "vuln-task-center-governance-prototype-v3.html"
out.write_text(html, encoding="utf-8")
print("OK", out, len(html), "\u626b\u63cf\u6cbb\u7406" in html)
