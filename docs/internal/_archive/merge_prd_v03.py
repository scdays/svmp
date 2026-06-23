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


before = read_chunk(ROOT / "prd-part-before-43.md")
v03 = read_chunk(ROOT / "prd-part-v03-ia-report.md")
ah = read_chunk(ROOT / "_ah_section_43.md")
after = read_chunk(ROOT / "prd-part-after-43.md")

marker = "### 3.1"
head, tail = before.split(marker, 1)
html = head + v03 + "\n" + marker + tail + ah + after

old_row = "| \u5b50\u4efb\u52a1\u64cd\u63a7 API\uff08LM/AH\uff09 | | \u2705 | | | |"
new_row = old_row + "\n| \u626b\u63cf\u62a5\u544a\u751f\u6210\u4e0e\u4e0b\u8f7d\uff08ReportAdapter\uff09 | | \u2705 | \u589e\u5f3a | | |"
html = html.replace(old_row, new_row)

html = html.replace(
    "3. **\u4efb\u52a1\u5168\u751f\u547d\u5468\u671f**\uff1a\u7b5b\u9009\u53ef\u7528\u626b\u63cf\u5668\u3001\u53c2\u6570\u8be6\u60c5\u3001\u5b50\u4efb\u52a1\u76d1\u63a7\u3001\u5f02\u5e38\u6062\u590d",
    "3. **\u4efb\u52a1\u5168\u751f\u547d\u5468\u671f**\uff1a\u7b5b\u9009\u53ef\u7528\u626b\u63cf\u5668\u3001\u53c2\u6570\u8be6\u60c5\u3001\u5b50\u4efb\u52a1\u76d1\u63a7\u3001\u5f02\u5e38\u6062\u590d\n"
    "4. **\u7ed3\u679c\u4e0e\u62a5\u544a\u4ea4\u4ed8**\uff1a\u6309\u62a5\u544a\u6a21\u677f\u751f\u6210\u3001\u8fdb\u5ea6\u8ddf\u8e2a\u3001\u4e0b\u8f7d/\u6295\u9012\uff08LM/AH\uff09",
)

html = html.replace(
    "| \u6a21\u677f/\u80fd\u529b\u672a\u6807\u51c6\u5316 | LM \u57fa\u7ebf/\u5f31\u53e3\u4ee4\u8f83\u5168\uff0cAH \u7b56\u7565/\u5b57\u5178\u672a\u7eb3\u5165\u80fd\u529b\u6ce8\u518c\u8868 |",
    "| \u6a21\u677f/\u80fd\u529b\u672a\u6807\u51c6\u5316 | LM \u57fa\u7ebf/\u5f31\u53e3\u4ee4\u8f83\u5168\uff0cAH \u7b56\u7565/\u5b57\u5178\u672a\u7eb3\u5165\u80fd\u529b\u6ce8\u518c\u8868 |\n"
    "| \u62a5\u544a\u80fd\u529b\u5206\u6563 | LM \u62a5\u544a\u4e0b\u8f7d\u903b\u8f91\u7740\u6563\u5728 ScanTaskAppServiceImpl / Kafka\uff0c\u65e0\u7edf\u4e00\u6a21\u677f\u4e0e\u72b6\u6001 |",
)

html = html.replace(
    "| 0.2 \u8349\u7a3f | 2026-06-14 | \u2014 | \u65b0\u589e\u5b89\u6052\u660e\u9274 DAS-RAS V5.0 Capability Profile\u3001\u5bf9\u8d26/\u64cd\u63a7/P1 \u4ea4\u4ed8\u8303\u56f4 |",
    "| 0.2 \u8349\u7a3f | 2026-06-14 | \u2014 | \u65b0\u589e\u5b89\u6052\u660e\u9274 DAS-RAS V5.0 Capability Profile\u3001\u5bf9\u8d26/\u64cd\u63a7/P1 \u4ea4\u4ed8\u8303\u56f4 |\n"
    "| 0.3 \u8349\u7a3f | 2026-06-14 | \u2014 | \u4ea7\u54c1\u57df\u6a21\u578b 3.0\u3001\u7ed3\u679c\u4e0e\u62a5\u544a\u57df US-P*\u3001\u539f\u578b v3 \u4ea4\u4ed8\u89c4\u683c |",
)

html += "\n\n---\n\n> \u539f\u578b v3 \u4ea4\u4ed8\u89c4\u683c\u89c1\uff1a`vuln-task-center-prototype-v3-spec.md`\n"

out = ROOT / "vuln-task-center-\u626b\u63cf\u6cbb\u7406\u4e2d\u5fc3-PRD.md"
out.write_text(html, encoding="utf-8")
print("OK", out, len(html), "\u62a5\u544a" in html)
