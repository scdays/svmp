#!/usr/bin/env python3
"""
从 field-catalog.json 生成四阶段 XML 外发定义（主机存活 / 端口 / 系统漏洞 / 弱口令）。

《数据外发字段说明》原文以 tar.gz + 多份 txt 描述；引擎侧更易消费的形态为四份 XML。
本工具不解析真实引擎 XML 样本，而是依据 HTML 已解析字段做分 phase 映射并产出模板与样例。

用法:
  python3 tools/build_export_xml_phases.py export-templates/field-catalog.json -o export-templates
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

PHASES: dict[str, dict[str, Any]] = {
    "live": {
        "fileName": "主机存活探测结果.xml",
        "rootElement": "LiveProbeResult",
        "displayName": "主机存活探测",
        "capability": "liveCheck",
        "legacyTxt": ["task_info.txt", "asset_info.txt"],
    },
    "port": {
        "fileName": "端口扫描结果.xml",
        "rootElement": "PortScanResult",
        "displayName": "端口扫描",
        "capability": "portScan",
        "legacyTxt": ["task_info.txt", "asset_info.txt"],
    },
    "vuln": {
        "fileName": "系统漏洞扫描结果.xml",
        "rootElement": "SystemVulnScanResult",
        "displayName": "系统漏洞扫描",
        "capability": "vulnScan",
        "legacyTxt": ["vul_info.txt", "asset_vuls.txt"],
    },
    "weakpwd": {
        "fileName": "弱口令扫描结果.xml",
        "rootElement": "WeakPasswordScanResult",
        "displayName": "弱口令扫描",
        "capability": "weakPasswordScan",
        "legacyTxt": ["asset_pwds.txt", "task_info.txt", "asset_info.txt"],
    },
}

TASK_META_FIELDS = {
    "id",
    "taskUuid",
    "taskType",
    "taskCount",
    "scanTimes",
    "execType",
    "hostCount",
    "product",
    "baseInfo",
    "device",
    "ipType",
    "source",
    "summary",
    "scanInfo",
    "taskStatus",
    "taskSource",
}

LIVE_FIELDS = {
    "liveCheck",
    "tcp",
    "icmp",
    "live",
    "ports",
    "liveArp",
    "spingDelay",
    "existNum",
    "notExistNum",
    "isHostPortExtendExistWeb",
}

PORT_FIELDS = {
    "portScan",
    "udp",
    "speed",
    "scanScope",
    "scanStyle",
    "port",
    "software",
    "geo_id",
    "geo",
    "mac",
    "type",
    "ip",
    "osName",
}

VULN_FIELDS = {
    "sysScan",
    "debug",
    "oracle",
    "scanpri",
    "alertMsg",
    "encoding",
    "name",
    "cve",
    "cnvd",
    "cvss",
    "vulLocalId",
    "others",
    "times",
    "vulnId",
    "vendor",
    "urls",
    "vUrl",
    "workflow",
    "vulTarget",
    "status",
    "riskValue",
    "riskLevel",
    "syncTime",
}

WEAKPWD_FIELDS = {
    "pswdGuess",
    "count",
    "thread",
    "timeout",
    "interval",
    "asset_pwds",
    "accountCount",
    "userName",
    "password",
    "isSystem",
    "weakAccountInfo",
    "other_info",
}

TARGET_COMMON = {"assetKey", "assetName", "target", "os", "status"}

PHASE_TARGET_COMMON: dict[str, set[str]] = {
    "live": TARGET_COMMON,
    "port": TARGET_COMMON,
    "weakpwd": TARGET_COMMON,
    "vuln": {"assetKey", "assetName", "target"},
}


def _collect_all_fields(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}
    for sec in catalog.get("sections", []):
        section = sec.get("sectionTitle", "")
        for f in sec.get("fields", []):
            name = f.get("name")
            if not name or name in by_name:
                continue
            entry = dict(f)
            entry["fromSection"] = section
            if sec.get("taskType") is not None:
                entry["engineTaskType"] = sec["taskType"]
            by_name[name] = entry
    return by_name


def _primary_phase(name: str) -> str | None:
    if name in LIVE_FIELDS:
        return "live"
    if name in PORT_FIELDS:
        return "port"
    if name in VULN_FIELDS:
        return "vuln"
    if name in WEAKPWD_FIELDS:
        return "weakpwd"
    return None


def _phases_for_field(name: str) -> set[str]:
    phases: set[str] = set()
    primary = _primary_phase(name)
    if primary:
        phases.add(primary)
    for phase_id, names in PHASE_TARGET_COMMON.items():
        if name in names:
            phases.add(phase_id)
    return phases


def build_phase_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    all_fields = _collect_all_fields(catalog)
    phases_out: dict[str, Any] = {}
    unassigned: list[str] = []

    for phase_id, meta in PHASES.items():
        fields: list[dict[str, Any]] = []
        for name, field in sorted(all_fields.items()):
            if phase_id not in _phases_for_field(name) and name not in TASK_META_FIELDS:
                continue
            fields.append(
                {
                    "name": name,
                    "source": name,
                    "description": field.get("description", ""),
                    "fromSection": field.get("fromSection", ""),
                    **({"scope": "taskMeta"} if name in TASK_META_FIELDS else {}),
                }
            )
        phases_out[phase_id] = {
            **meta,
            "phaseId": phase_id,
            "fieldCount": len(fields),
            "fields": fields,
        }

    for name in sorted(all_fields):
        if not _phases_for_field(name) and name not in TASK_META_FIELDS:
            unassigned.append(name)

    return {
        "version": "1.0",
        "description": "SVMP 任务结束外发：四阶段 XML（由 field-catalog 映射，替代多 txt 拼装）",
        "packageFormat": "SVMP-TAR-GZ-XML",
        "packageFiles": [m["fileName"] for m in PHASES.values()],
        "deprecatedLegacyFiles": [
            "task_info.txt",
            "asset_info.txt",
            "asset_vuls.txt",
            "vul_info.txt",
            "asset_pwds.txt",
        ],
        "phases": phases_out,
        "unassignedFieldNames": unassigned,
    }


def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            _indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def _sample_live() -> ET.Element:
    root = ET.Element("LiveProbeResult", version="1.0")
    meta = ET.SubElement(root, "TaskMeta")
    for tag, text in (
        ("id", "10001"),
        ("taskUuid", "uuid-task-001"),
        ("taskType", "1"),
        ("hostCount", "10"),
        ("existNum", "8"),
        ("notExistNum", "2"),
    ):
        ET.SubElement(meta, tag).text = text
    cfg = ET.SubElement(root, "LiveCheckConfig")
    for tag, text in (("tcp", "1"), ("icmp", "1"), ("live", "1"), ("ports", "22,80,443")):
        ET.SubElement(cfg, tag).text = text
    hosts = ET.SubElement(root, "Hosts")
    host = ET.SubElement(hosts, "Host")
    for tag, text in (
        ("assetKey", "10.0.0.1"),
        ("assetName", "示例主机"),
        ("alive", "true"),
        ("os", "Linux"),
    ):
        ET.SubElement(host, tag).text = text
    return root


def _sample_port() -> ET.Element:
    root = ET.Element("PortScanResult", version="1.0")
    meta = ET.SubElement(root, "TaskMeta")
    ET.SubElement(meta, "taskUuid").text = "uuid-task-001"
    cfg = ET.SubElement(root, "PortScanConfig")
    for tag, text in (
        ("udp", "0"),
        ("speed", "3"),
        ("scanScope", "standard"),
        ("scanStyle", "CONNECT"),
    ):
        ET.SubElement(cfg, tag).text = text
    targets = ET.SubElement(root, "Targets")
    target = ET.SubElement(targets, "Target")
    ET.SubElement(target, "assetKey").text = "10.0.0.1"
    ports = ET.SubElement(target, "Ports")
    port = ET.SubElement(ports, "Port")
    ET.SubElement(port, "number").text = "443"
    ET.SubElement(port, "protocol").text = "tcp"
    ET.SubElement(port, "service").text = "https"
    return root


def _sample_vuln() -> ET.Element:
    root = ET.Element("SystemVulnScanResult", version="1.0")
    meta = ET.SubElement(root, "TaskMeta")
    ET.SubElement(meta, "taskUuid").text = "uuid-task-001"
    vulns = ET.SubElement(root, "Vulnerabilities")
    vuln = ET.SubElement(vulns, "Vulnerability")
    for tag, text in (
        ("vulLocalId", "VUL-2024-0001"),
        ("name", "OpenSSL 心脏出血"),
        ("cve", "CVE-2014-0160"),
        ("cnvd", ""),
        ("cvss", "5.0"),
        ("others", "…"),
    ):
        ET.SubElement(vuln, tag).text = text
    rels = ET.SubElement(root, "AssetVulnerabilities")
    rel = ET.SubElement(rels, "AssetVulnerability")
    for tag, text in (
        ("assetKey", "10.0.0.1"),
        ("vulLocalId", "VUL-2024-0001"),
        ("times", "1"),
        ("riskLevel", "high"),
    ):
        ET.SubElement(rel, tag).text = text
    return root


def _sample_weakpwd() -> ET.Element:
    root = ET.Element("WeakPasswordScanResult", version="1.0")
    meta = ET.SubElement(root, "TaskMeta")
    ET.SubElement(meta, "taskUuid").text = "uuid-task-001"
    targets = ET.SubElement(root, "Targets")
    target = ET.SubElement(targets, "Target")
    ET.SubElement(target, "assetKey").text = "10.0.0.1"
    ET.SubElement(target, "accountCount").text = "1"
    accounts = ET.SubElement(target, "WeakAccounts")
    account = ET.SubElement(accounts, "Account")
    for tag, text in (("userName", "admin"), ("password", "***"), ("isSystem", "true")):
        ET.SubElement(account, tag).text = text
    return root


SAMPLE_BUILDERS = {
    "live": _sample_live,
    "port": _sample_port,
    "vuln": _sample_vuln,
    "weakpwd": _sample_weakpwd,
}


def write_samples(out_dir: Path) -> None:
    samples_dir = out_dir / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    for phase_id, meta in PHASES.items():
        root = SAMPLE_BUILDERS[phase_id]()
        _indent_xml(root)
        tree = ET.ElementTree(root)
        path = samples_dir / meta["fileName"]
        tree.write(path, encoding="utf-8", xml_declaration=True)
        print(f"  样例: {path}")


def write_bundle_template(out_dir: Path, phase_catalog: dict[str, Any]) -> Path:
    path = out_dir / "tpl-svmp-xml-scan-bundle.yaml"
    lines = [
        "# 四阶段 XML 外发包（推荐）；legacy txt 见 deprecatedLegacyFiles",
        "exportTemplateId: tpl-svmp-xml-scan-bundle",
        "displayName: SVMP 扫描结果（四阶段 XML）",
        "match:",
        "  exportPackageProfile: svmp-xml-phases",
        "  # 按任务能力命中子文件（未启用的阶段可不产出对应 XML）",
        "  capabilities:",
        "    liveCheck: optional",
        "    portScan: optional",
        "    vulnScan: optional",
        "    weakPasswordScan: optional",
        "  engineTaskTypes: [1, 4, 5, 8, 16]  # TASK_SYS_SCAN / PWD / SYS_PWD / WEB / ASSET_FIND",
        "output:",
        "  format: SVMP-TAR-GZ-XML",
        "  encoding: UTF-8",
        "  fileNamePattern: 'svmp-export-{taskId}-{occurredAt}.tar.gz'",
        "  packageFiles:",
    ]
    for fn in phase_catalog["packageFiles"]:
        lines.append(f"    - {fn}")
    lines.extend(
        [
            "  deprecatedLegacyFiles:",
        ]
    )
    for fn in phase_catalog["deprecatedLegacyFiles"]:
        lines.append(f"    - {fn}")
    lines.extend(
        [
            "trigger:",
            "  on: TASK_COMPLETED",
            "filter:",
            "  vulInfoStatList: [1, 2, 3, 5, 6, 7, 8, 9, 10]",
            "phases:",
        ]
    )
    for phase_id, phase in phase_catalog["phases"].items():
        lines.append(f"  {phase_id}:")
        lines.append(f"    file: {phase['fileName']}")
        lines.append(f"    rootElement: {phase['rootElement']}")
        lines.append(f"    capability: {phase['capability']}")
        lines.append("    fields:")
        for f in phase["fields"][:20]:
            desc = f.get("description") or ""
            comment = f"  # {desc}" if desc else ""
            lines.append(f"      - target: {f['name']}")
            lines.append(f"        source: {f['source']}{comment}")
        if len(phase["fields"]) > 20:
            lines.append(f"      # …共 {len(phase['fields'])} 字段，见 phase-field-catalog.json")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_phase_templates(out_dir: Path, phase_catalog: dict[str, Any]) -> list[Path]:
    written: list[Path] = []
    for phase_id, phase in phase_catalog["phases"].items():
        tid = f"tpl-svmp-phase-{phase_id}"
        path = out_dir / f"{tid}.yaml"
        lines = [
            f"# 单阶段：{phase['displayName']} → {phase['fileName']}",
            f"exportTemplateId: {tid}",
            f"displayName: {phase['displayName']}",
            "match:",
            f"  capability: {phase['capability']}",
            "output:",
            "  format: SVMP-XML",
            "  encoding: UTF-8",
            f"  fileName: {phase['fileName']}",
            f"  rootElement: {phase['rootElement']}",
            "trigger:",
            "  on: TASK_COMPLETED",
            "fields:",
        ]
        for f in phase["fields"]:
            desc = f.get("description") or ""
            comment = f"  # {desc}" if desc else ""
            lines.append(f"  - target: {f['name']}")
            lines.append(f"    source: {f['source']}{comment}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="生成四阶段 XML 外发目录与模板")
    parser.add_argument(
        "catalog_path",
        type=Path,
        nargs="?",
        default=Path("export-templates/field-catalog.json"),
    )
    parser.add_argument("-o", "--out-dir", type=Path, default=Path("export-templates"))
    parser.add_argument("--no-samples", action="store_true")
    args = parser.parse_args()

    if not args.catalog_path.is_file():
        print(f"缺少 field-catalog: {args.catalog_path}", file=sys.stderr)
        print("请先运行: python3 tools/parse_export_fields_html.py ...", file=sys.stderr)
        return 1

    catalog = json.loads(args.catalog_path.read_text(encoding="utf-8"))
    phase_catalog = build_phase_catalog(catalog)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    phase_path = args.out_dir / "phase-field-catalog.json"
    phase_path.write_text(
        json.dumps(phase_catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已写入 {phase_path}")

    if not args.no_samples:
        write_samples(args.out_dir)

    bundle = write_bundle_template(args.out_dir, phase_catalog)
    print(f"  模板: {bundle}")

    for p in write_phase_templates(args.out_dir, phase_catalog):
        print(f"  模板: {p}")

    if phase_catalog["unassignedFieldNames"]:
        print(
            f"提示: {len(phase_catalog['unassignedFieldNames'])} 个字段未归入四阶段 "
            f"（处置单/预警等仍用独立模板）"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
