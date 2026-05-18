#!/usr/bin/env python3
"""
Parse「数据外发字段说明.html」类文档（多为企业微信/Excel 另存为 HTML 的表格）。

用法:
  python3 tools/parse_export_fields_html.py /path/to/数据外发字段说明.html
  python3 tools/parse_export_fields_html.py /path/to/数据外发字段说明.html -o export-templates/field-catalog.json

输出:
  - field-catalog.json: 按章节/模板分组的字段列表
  - 可选 -o 目录下生成各模板草案 export-templates/draft-<section>.yaml
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


# 表头别名 → 规范列名
HEADER_ALIASES: dict[str, str] = {
    "字段名": "name",
    "参数名": "name",
    "字段": "name",
    "英文名": "name",
    "英文名称": "name",
    "属性名": "name",
    "中文名": "labelZh",
    "中文名称": "labelZh",
    "名称": "labelZh",
    "类型": "dataType",
    "数据类型": "dataType",
    "字段类型": "dataType",
    "长度": "maxLength",
    "最大长度": "maxLength",
    "必填": "required",
    "是否必填": "required",
    "必选": "required",
    "说明": "description",
    "描述": "description",
    "备注": "description",
    "取值说明": "description",
    "码表": "codeTable",
    "枚举": "codeTable",
    "来源": "source",
    "映射": "target",
    "目标字段": "target",
    "模板": "templateHint",
    "任务模板": "templateHint",
    "扫描模板": "templateHint",
    "适用场景": "templateHint",
}


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
    if v in ("是", "y", "yes", "true", "✓", "√", "必填", "必选", "1"):
        return True
    if v in ("否", "n", "no", "false", "可选", "○", "0"):
        return False
    return None


class TableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict[str, Any]] = []
        self._current_section_title = "默认"
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._cell_tag: str | None = None
        self._row_cells: list[str] = []
        self._cell_buf: list[str] = []
        self._table_rows: list[list[str]] = []
        self._pending_title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in ("h1", "h2", "h3", "h4", "strong", "b"):
            self._pending_title_parts = []
        if t == "table":
            self._in_table = True
            self._table_rows = []
        elif self._in_table and t == "tr":
            self._in_row = True
            self._row_cells = []
        elif self._in_row and t in ("td", "th"):
            self._in_cell = True
            self._cell_tag = t
            self._cell_buf = []

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in ("h1", "h2", "h3", "h4", "strong", "b") and self._pending_title_parts:
            title = "".join(self._pending_title_parts).strip()
            if title and len(title) < 120:
                self._current_section_title = title
            self._pending_title_parts = []
        if t in ("td", "th") and self._in_cell:
            self._row_cells.append("".join(self._cell_buf).strip())
            self._in_cell = False
            self._cell_tag = None
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
        elif self._pending_title_parts is not None and not self._in_table:
            if data.strip():
                self._pending_title_parts.append(data.strip())

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
            if "name" not in item and name:
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


def _guess_export_template_id(section_title: str, fields: list[dict[str, Any]]) -> str:
    for f in fields:
        hint = f.get("templateHint") or ""
        if hint:
            slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", hint.strip())[:40]
            return f"tpl-{slug}".lower().strip("-")
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", section_title)[:50]
    return f"tpl-{slug}".lower().strip("-") or "tpl-default"


def _to_export_template_yaml_block(
    export_template_id: str, section_title: str, fields: list[dict[str, Any]]
) -> str:
    lines = [
        f"# 由 parse_export_fields_html.py 从「{section_title}」自动生成，请人工校对 source / match",
        f"exportTemplateId: {export_template_id}",
        f"displayName: {section_title}",
        "match:",
        "  scanTemplateIds: []  # 绑定引擎 scanTemplateId，与 POST /tasks 一致",
        "  vulnType: null",
        "output:",
        "  format: JSON  # JSON | CSV | MIIT-2025-VULINFOLST",
        "  encoding: UTF-8",
        "  includeHeader: true",
        "trigger:",
        "  on: TASK_COMPLETED",
        "filter:",
        "  vulInfoStatList: [1, 2, 3, 5, 6, 7, 8, 9, 10]",
        "fields:",
    ]
    for f in fields:
        ext = f.get("name") or f.get("target") or "unknown"
        src = f.get("source") or ext
        req = f.get("required")
        req_comment = "  # 必填" if req is True else ""
        desc = f.get("description", "")
        desc_comment = f"  # {desc[:60]}" if desc else ""
        lines.append(f"  - target: {ext}")
        lines.append(f"    source: {src}{req_comment}{desc_comment}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="解析数据外发字段说明 HTML")
    parser.add_argument("html_path", type=Path, help="HTML 文件路径")
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=Path("export-templates"),
        help="输出目录（默认 export-templates/）",
    )
    parser.add_argument(
        "--write-drafts",
        action="store_true",
        help="为每个表格章节生成 draft-*.yaml 草案",
    )
    args = parser.parse_args()

    if not args.html_path.is_file():
        print(f"文件不存在: {args.html_path}", file=sys.stderr)
        print(
            "请将 HTML 复制到仓库，例如: export-templates/数据外发字段说明.html",
            file=sys.stderr,
        )
        return 1

    raw = args.html_path.read_text(encoding="utf-8", errors="replace")
    p = TableHTMLParser()
    p.feed(raw)

    catalog = {
        "sourceFile": str(args.html_path.name),
        "sectionCount": len(p.sections),
        "sections": p.sections,
        "canonicalSourceHints": [
            "规范域字段见设计方案 §3：vulInfoID, vulName, vulNetAddr, vulInfoStat, lvRsn, remedDesc …",
            "引擎字段映射见 §6.3.5：vulnDisposalId, orgVulId …",
        ],
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = args.out_dir / "field-catalog.json"
    catalog_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已写入 {catalog_path}（{len(p.sections)} 个表格章节，"
          f"{sum(s['fieldCount'] for s in p.sections)} 个字段）")

    if args.write_drafts:
        for sec in p.sections:
            tid = _guess_export_template_id(sec["sectionTitle"], sec["fields"])
            draft = args.out_dir / f"draft-{tid}.yaml"
            draft.write_text(
                _to_export_template_yaml_block(
                    tid, sec["sectionTitle"], sec["fields"]
                ),
                encoding="utf-8",
            )
            print(f"  草案: {draft}")

    if not p.sections:
        print(
            "警告: 未解析到表格。若 HTML 为单页应用或图片，请改为 Excel 另存为「网页(.html)」后重试。",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
