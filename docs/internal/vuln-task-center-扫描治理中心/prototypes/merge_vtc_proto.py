# -*- coding: utf-8 -*-
from pathlib import Path

d = Path(__file__).parent
chunks = [d / "vtc-chunk-{0}.html".format(i) for i in range(1, 5)]


def read_chunk(path):
    raw = path.read_bytes()
    for enc in ("utf-8", "gbk", "utf-8-sig"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


html = "".join(read_chunk(p) for p in chunks)
out = d / "vuln-task-center-governance-prototype.html"
out.write_text(html, encoding="utf-8")
marker = "\u626b\u63cf\u6cbb\u7406"
print("OK", str(out), len(html), marker in html)
