#!/usr/bin/env python3
"""
解析 export-templates 下正式的「系统漏洞扫描结果.xml」「弱口令扫描结果.xml」
（绿盟 Aurora 报告格式），生成 schema 与平台字段映射。

用法:
  python3 tools/parse_export_xml_samples.py -o export-templates/xml-schemas
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

OFFICIAL_FILES: dict[str, str] = {
    "vuln": "系统漏洞扫描结果.xml",
    "weakpwd": "弱口令扫描结果.xml",
}

# Aurora 元素 → 《数据外发字段说明》/ 平台规范域 source（§3）
AURORA_TO_PLATFORM: dict[str, dict[str, str]] = {
    "vuln": {
        "aurora/report/task/id": "id",
        "aurora/report/task/name": "baseInfo",
        "aurora/report/task/task_type": "taskType",
        "aurora/report/task/time_start_scan": "scanTimes",
        "aurora/report/task/time_end_scan": "syncTime",
        "aurora/report/scanned_ip_count": "hostCount",
        "aurora/report/targets/target/ip": "assetKey",
        "aurora/report/targets/target/host_score": "riskValue",
        "aurora/report/targets/target/vul_score": "riskValue",
        "aurora/report/targets/target/vuln_scanned/vuln/port": "port",
        "aurora/report/targets/target/vuln_scanned/vuln/vul_id": "vulLocalId",
        "aurora/report/targets/target/vuln_scanned/vuln/protocol": "protocol",
        "aurora/report/targets/target/vuln_scanned/vuln/service": "service",
        "aurora/report/targets/target/vuln_scanned/vuln/mess_string": "others",
        "aurora/report/targets/target/vuln_scanned/vuln/vul_confirmed": "status",
        "aurora/report/targets/target/vuln_detail/vuln/vul_id": "vulLocalId",
        "aurora/report/targets/target/vuln_detail/vuln/plugin_id": "vulLocalId",
        "aurora/report/targets/target/vuln_detail/vuln/name": "name",
        "aurora/report/targets/target/vuln_detail/vuln/cve_id": "cve",
        "aurora/report/targets/target/vuln_detail/vuln/cnnvd": "cnvd",
        "aurora/report/targets/target/vuln_detail/vuln/cncve": "cnvd",
        "aurora/report/targets/target/vuln_detail/vuln/risk_points": "cvss",
        "aurora/report/targets/target/vuln_detail/vuln/threat_category": "others",
        "aurora/report/targets/target/vuln_detail/vuln/description": "others",
        "aurora/report/targets/target/vuln_detail/vuln/solution": "others",
        "aurora/report/targets/target/vuln_detail/vuln/date_found": "syncTime",
    },
    "weakpwd": {
        "aurora/report/task/id": "id",
        "aurora/report/task/task_type": "taskType",
        "aurora/report/targets/target/ip": "assetKey",
        "aurora/report/targets/target/password_results/password_result/type": "service",
        "aurora/report/targets/target/password_results/password_result/username": "userName",
        "aurora/report/targets/target/password_results/password_result/password": "password",
        "aurora/report/targets/target/vuln_scanned/vuln/port": "port",
        "aurora/report/targets/target/vuln_scanned/vuln/vul_id": "vulLocalId",
        "aurora/report/targets/target/vuln_scanned/vuln/mess_string": "weakAccountInfo",
        "aurora/report/targets/target/vuln_detail/vuln/name": "name",
    },
}


def _path_key(elem: ET.Element) -> str:
    parts: list[str] = []
    cur: ET.Element | None = elem
    while cur is not None and cur.tag != "aurora":
        parts.append(cur.tag)
        cur = cur.getparent() if hasattr(cur, "getparent") else None  # type: ignore[attr-defined]
    parts.reverse()
    if parts and parts[0] != "aurora":
        return "aurora/" + "/".join(parts)
    return "aurora/" + "/".join(parts) if parts else "aurora"


def _iter_paths(path: Path, max_elements: int = 200_000) -> tuple[set[str], dict[str, int], dict[str, Any]]:
    """流式遍历，收集元素路径与 task_type 等摘要。"""
    paths: set[str] = set()
    tag_counts: dict[str, int] = defaultdict(int)
    summary: dict[str, Any] = {}
    n = 0
    stack: list[str] = ["aurora"]

    for event, elem in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            stack.append(elem.tag)
            tag_counts[elem.tag] += 1
            if len(stack) <= 8:
                paths.add("/".join(stack))
            if elem.tag == "task_type" and elem.text and "task_type" not in summary:
                summary["task_type"] = elem.text.strip()
            if elem.tag == "task" and event == "start":
                pass
            n += 1
        else:
            if elem.tag == "target" and "target_count" not in summary:
                summary["target_count"] = summary.get("target_count", 0) + 1
            stack.pop()
            elem.clear()
        if n >= max_elements:
            summary["truncated"] = True
            summary["elements_scanned"] = n
            break
    else:
        summary["elements_scanned"] = n
    return paths, dict(tag_counts), summary


def _build_schema(
    phase: str,
    sample_path: Path,
    paths: set[str],
    tag_counts: dict[str, int],
    summary: dict[str, Any],
) -> dict[str, Any]:
    mapping = AURORA_TO_PLATFORM.get(phase, {})
    fields = []
    for aurora_path, source in sorted(mapping.items()):
        fields.append(
            {
                "auroraPath": aurora_path,
                "source": source,
                "xmlPath": aurora_path.replace("aurora/", "", 1),
            }
        )
    return {
        "phase": phase,
        "officialSample": sample_path.name,
        "format": "aurora",
        "rootElement": "aurora",
        "encoding": "utf-8",
        "summary": summary,
        "uniqueTags": sorted(tag_counts.keys()),
        "pathPrefixes": sorted(paths)[:80],
        "fieldMappings": fields,
    }


def parse_official_samples(export_dir: Path) -> dict[str, Any]:
    schemas: dict[str, Any] = {}
    for phase, filename in OFFICIAL_FILES.items():
        sample = export_dir / filename
        if not sample.is_file():
            raise FileNotFoundError(f"缺少正式样本: {sample}")
        paths, tag_counts, summary = _iter_paths(sample)
        schemas[phase] = _build_schema(phase, sample, paths, tag_counts, summary)
    return {
        "format": "aurora",
        "vendor": "绿盟科技",
        "description": "正式引擎外发 XML（系统漏洞 / 弱口令扫描结果）",
        "officialSamples": {
            phase: OFFICIAL_FILES[phase] for phase in OFFICIAL_FILES
        },
        "phases": schemas,
    }


def apply_to_phase_catalog(export_dir: Path, aurora_doc: dict[str, Any]) -> None:
    """用 Aurora 正式结构覆盖 phase-field-catalog 中 vuln / weakpwd 阶段。"""
    phase_path = export_dir / "phase-field-catalog.json"
    if not phase_path.is_file():
        print(f"跳过 phase-field-catalog（不存在）: {phase_path}", file=sys.stderr)
        return

    catalog = json.loads(phase_path.read_text(encoding="utf-8"))
    for phase_id, schema in aurora_doc["phases"].items():
        if phase_id not in catalog.get("phases", {}):
            continue
        phase = catalog["phases"][phase_id]
        phase["format"] = "aurora"
        phase["rootElement"] = "aurora"
        phase["officialSample"] = schema["officialSample"]
        phase["fieldMappings"] = schema["fieldMappings"]
        phase["fields"] = [
            {
                "name": m["source"],
                "source": m["source"],
                "auroraPath": m["auroraPath"],
                "xmlPath": m["xmlPath"],
            }
            for m in schema["fieldMappings"]
        ]
        phase["fieldCount"] = len(phase["fields"])
    phase_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已更新 {phase_path}（vuln / weakpwd → aurora）")


def main() -> int:
    parser = argparse.ArgumentParser(description="解析正式 Aurora XML 样本")
    parser.add_argument(
        "-d",
        "--export-dir",
        type=Path,
        default=Path("export-templates"),
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=Path("export-templates/xml-schemas"),
    )
    parser.add_argument("--update-phase-catalog", action="store_true", default=True)
    args = parser.parse_args()

    try:
        doc = parse_official_samples(args.export_dir)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "aurora-report.schema.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入 {out}")
    for phase, s in doc["phases"].items():
        print(
            f"  [{phase}] {s['officialSample']} task_type={s['summary'].get('task_type')} "
            f"targets≈{s['summary'].get('target_count')} tags={len(s['uniqueTags'])}"
        )

    if args.update_phase_catalog:
        apply_to_phase_catalog(args.export_dir, doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
