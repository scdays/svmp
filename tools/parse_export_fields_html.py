#!/usr/bin/env python3
"""
解析《数据外发字段说明.html》。

支持两种版式：
1. **table**：Excel 另存为 HTML 的 <table>
2. **pdf-html**（默认）：pdf2htmlEX 导出的绝对定位 <motion>/<div> + JSON 示例

用法:
  python3 tools/parse_export_fields_html.py templates/engine/数据外发字段说明.html
  python3 tools/parse_export_fields_html.py ... --write-drafts
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

HEADER_ALIASES: dict[str, str] = {
    "字段名": "name",
    "参数名": "name",
    "字段": "name",
    "英文名": "name",
    "中文名": "labelZh",
    "类型": "dataType",
    "必填": "required",
    "是否必填": "required",
    "说明": "description",
    "描述": "description",
    "备注": "description",
}

def _normalize_section_title(title: str) -> str:
    t = re.sub(r"\s+", "", title)
    t = re.sub(r"[—\-–·()（）]", "", t)
    return t


SECTION_TASK_TYPE: dict[str, dict[str, Any]] = {
    "主机扫描": {"taskType": 1, "taskTypeMacro": "TASK_SYS_SCAN", "exportPackage": "tar.gz"},
    "网站扫描任务": {"taskType": 8, "taskTypeMacro": "TASK_WEB_SCAN"},
    "资产发现任务": {"taskType": 16, "taskTypeMacro": "TASK_ASSET_FIND"},
    "口令猜测任务": {"taskType": 4, "taskTypeMacro": "TASK_PWD_SCAN"},
    "数据外发处置单系统漏洞": {"profile": "disposal-workflow"},
    "数据外发预警": {"profile": "early-warning"},
}


def _section_meta(title: str) -> dict[str, Any]:
    key = _normalize_section_title(title)
    for pattern, meta in SECTION_TASK_TYPE.items():
        if _normalize_section_title(pattern) == key:
            return meta
    return {}

EXPORT_FILES_HINT = [
    "task_info.txt",
    "asset_info.txt",
    "asset_vuls.txt",
    "vul_info.txt",
]


def _norm_header(text: str) -> str:
    t = re.sub(r"\s+", "", text.strip())
    for key, canonical in HEADER_ALIASES.items():
        if key in t or t == key:
            return canonical
    return t.lower() or "col"


def _parse_required(val: str) -> bool | None:
    v = val.strip().lower()
    if not v or v in ("—", "-", "无", "n/a"):
        return None
    if v in ("是", "y", "yes", "true", "✓", "必填", "必选", "1"):
        return True
    if v in ("否", "n", "no", "false", "可选", "○", "0"):
        return False
    return None


def _strip_html(chunk: str) -> str:
    chunk = re.sub(r"<span class=\"_[^\"]*\"></span>", "", chunk)
    chunk = re.sub(r"<[^>]+>", " ", chunk)
    chunk = re.sub(r"\s+", " ", chunk)
    return chunk.strip()


def _extract_task_macros(html: str) -> dict[str, int]:
    macros: dict[str, int] = {}
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\s+", " ", text)
    for m in re.finditer(r"(TASK_[A-Z_0-9]+)\s*=\s*(\d+)", text):
        macros[m.group(1)] = int(m.group(2))
    return macros


def _extract_fields_from_chunk(html_chunk: str) -> list[dict[str, Any]]:
    """从 JSON 示例行提取 "key": 与 # 注释（兼容 pdf2htmlEX 断行）。"""
    plain = re.sub(r"<[^>]+>", " ", html_chunk)
    plain = re.sub(r"\s+", " ", plain)
    fields: list[dict[str, Any]] = []
    seen: set[str] = set()

    for m in re.finditer(r'"([a-zA-Z][a-zA-Z0-9_]*)"\s*:', plain):
        key = m.group(1)
        if key in seen or key in ("ctm",):
            continue
        seen.add(key)
        tail = plain[m.end() : m.end() + 200]
        desc = ""
        cm = re.search(r"#\s*([^#\"]{2,80})", tail)
        if cm:
            desc = cm.group(1).strip()
        fields.append({"name": key, "description": desc, "jsonKey": key})
    return fields


def _extract_export_files(html_chunk: str) -> list[str]:
    text = _strip_html(html_chunk)
    found = []
    for name in EXPORT_FILES_HINT:
        if name in text and name not in found:
            found.append(name)
    return found


def parse_pdf_html(html: str) -> dict[str, Any]:
    h2_pat = re.compile(
        r'class="t m0 x3 h2 y[0-9a-f]+ ff1 fs0[^"]*"[^>]*>(.*?)</div>',
        re.S,
    )
    matches = list(h2_pat.finditer(html))
    sections: list[dict[str, Any]] = []
    macros = _extract_task_macros(html)

    for i, m in enumerate(matches):
        title = _strip_html(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(html)
        chunk = html[start:end]

        if title == "接口宏定义":
            sections.append(
                {
                    "sectionTitle": title,
                    "taskTypeMacros": macros,
                    "fields": [],
                }
            )
            continue

        fields = _extract_fields_from_chunk(chunk)
        export_files = _extract_export_files(chunk)
        meta = _section_meta(title)
        entry: dict[str, Any] = {
            "sectionTitle": title,
            "fieldCount": len(fields),
            "fields": fields,
            **meta,
        }
        if export_files:
            entry["exportFiles"] = export_files
        if fields or export_files or meta:
            sections.append(entry)

    return {
        "format": "pdf-html",
        "sectionCount": len(sections),
        "taskTypeMacros": macros,
        "sections": sections,
    }


class TableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict[str, Any]] = []
        self._current_section_title = "默认"
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._row_cells: list[str] = []
        self._cell_buf: list[str] = []
        self._table_rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t == "table":
            self._in_table = True
            self._table_rows = []
        elif self._in_table and t == "tr":
            self._in_row = True
            self._row_cells = []
        elif self._in_row and t in ("td", "th"):
            self._in_cell = True
            self._cell_buf = []

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in ("td", "th") and self._in_cell:
            self._row_cells.append("".join(self._cell_buf).strip())
            self._in_cell = False
        elif t == "tr" and self._in_row:
            if any(c.strip() for c in self._row_cells):
                self._table_rows.append(self._row_cells)
            self._in_row = False
        elif t == "table" and self._in_table:
            self._flush_table()
            self._in_table = False

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_buf.append(data)

    def _flush_table(self) -> None:
        if len(self._table_rows) < 2:
            return
        header = [_norm_header(c) for c in self._table_rows[0]]
        fields: list[dict[str, Any]] = []
        for row in self._table_rows[1:]:
            if len(row) < len(header):
                row = row + [""] * (len(header) - len(row))
            item: dict[str, Any] = {}
            for i, col in enumerate(header):
                val = row[i].strip() if i < len(row) else ""
                if not val:
                    continue
                if col == "required":
                    item["required"] = _parse_required(val)
                else:
                    item[col] = val
            name = item.get("name") or item.get("target") or item.get("labelZh")
            if not name:
                continue
            if "name" not in item:
                item["name"] = name
            fields.append(item)
        if fields:
            self.sections.append(
                {
                    "sectionTitle": self._current_section_title,
                    "fieldCount": len(fields),
                    "fields": fields,
                }
            )


def _slug(title: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", title.strip())[:50]
    return slug.lower().strip("-") or "default"


def _template_id_for_section(sec: dict[str, Any]) -> str:
    if sec.get("taskType") is not None:
        return f"tpl-svmp-task-type-{sec['taskType']}"
    if sec.get("profile") == "early-warning":
        return "tpl-svmp-early-warning"
    if sec.get("profile") == "disposal-workflow":
        return "tpl-svmp-disposal-workflow"
    return f"tpl-{_slug(sec['sectionTitle'])}"


def _to_yaml(sec: dict[str, Any], fields: list[dict[str, Any]]) -> str:
    tid = _template_id_for_section(sec)
    title = sec["sectionTitle"]
    lines = [
        f"# 由《数据外发字段说明》章节「{title}」生成，请校对 source 映射",
        f"exportTemplateId: {tid}",
        f"displayName: {title}",
        "match:",
    ]
    if sec.get("taskType") is not None:
        lines.append(f"  engineTaskType: {sec['taskType']}  # {sec.get('taskTypeMacro', '')}")
        lines.append("  scanTemplateIds: []  # 可选：再细绑 scanTemplateId")
    elif sec.get("profile"):
        lines.append(f"  exportProfile: {sec['profile']}")
    else:
        lines.append("  scanTemplateIds: []")
    if sec.get("exportFiles"):
        lines.append("output:")
        lines.append("  format: SVMP-TAR-GZ")
        lines.append("  packageFiles:")
        for f in sec["exportFiles"]:
            lines.append(f"    - {f}")
    else:
        lines.append("output:")
        lines.append("  format: JSON")
    lines.extend(
        [
            "  encoding: UTF-8",
            "trigger:",
            "  on: TASK_COMPLETED",
            "filter:",
            "  vulInfoStatList: [1, 2, 3, 5, 6, 7, 8, 9, 10]",
            "fields:",
        ]
    )
    for f in fields:
        key = f.get("name", "unknown")
        desc = f.get("description", "")
        comment = f"  # {desc}" if desc else ""
        lines.append(f"  - target: {key}")
        lines.append(f"    source: {key}{comment}")
    return "\n".join(lines) + "\n"


def parse_html_file(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if "<table" in raw.lower():
        p = TableHTMLParser()
        p.feed(raw)
        if p.sections:
            return {
                "format": "table",
                "sourceFile": path.name,
                "sectionCount": len(p.sections),
                "sections": p.sections,
            }
    catalog = parse_pdf_html(raw)
    catalog["sourceFile"] = path.name
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description="解析数据外发字段说明 HTML")
    parser.add_argument("html_path", type=Path)
    parser.add_argument("-o", "--out-dir", type=Path, default=Path("templates"))
    parser.add_argument("--write-drafts", action="store_true")
    parser.add_argument(
        "--xml-phases",
        action="store_true",
        help="解析后生成四阶段 XML 外发目录（phase-field-catalog、样例 XML、tpl-svmp-xml-scan-bundle）",
    )
    args = parser.parse_args()

    if not args.html_path.is_file():
        print(f"文件不存在: {args.html_path}", file=sys.stderr)
        return 1

    from template_layout import ensure_dirs

    catalog = parse_html_file(args.html_path)
    layout = ensure_dirs(args.out_dir)
    catalog_path = layout["catalogs"] / "field-catalog.json"
    catalog_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total_fields = sum(s.get("fieldCount", len(s.get("fields", []))) for s in catalog["sections"])
    print(
        f"已写入 {catalog_path}（格式={catalog.get('format')}, "
        f"{catalog['sectionCount']} 章节, {total_fields} 字段）"
    )

    if args.write_drafts:
        for sec in catalog["sections"]:
            fields = sec.get("fields", [])
            if not fields and not sec.get("exportFiles"):
                continue
            tid = _template_id_for_section(sec)
            draft = layout["yaml"] / f"{tid}.yaml"
            draft.write_text(_to_yaml(sec, fields), encoding="utf-8")
            print(f"  模板: {draft} ({len(fields)} 字段)")

    if args.xml_phases:
        import subprocess

        tools_dir = Path(__file__).resolve().parent
        aurora = tools_dir / "parse_export_xml_samples.py"
        if aurora.is_file():
            subprocess.call([sys.executable, str(aurora), "-d", str(layout["engine"])])
        script = tools_dir / "build_export_xml_phases.py"
        rc = subprocess.call(
            [sys.executable, str(script), str(catalog_path), "-o", str(layout["root"])],
        )
        if rc != 0:
            return rc

    if catalog["sectionCount"] == 0 or total_fields == 0:
        print("警告: 未解析到有效字段。", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
