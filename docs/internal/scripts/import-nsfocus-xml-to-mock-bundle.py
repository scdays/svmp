#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert NSFocus Aurora XML to open-api-service mock fixture.

Parsing rules align with vul-pass NsfocusXmlParserV4.java:
  data/report/targets/target
    -> vuln_scanned/vuln      (port binding + dedup fingerprint)
    -> vuln_detail/vuln      (name, cve, risk_points, ...)
    -> password_results/password_result  (weak-password scan)

Reference: project_backend/svmp/vul-pass/.../NsfocusXmlParserV4.java

Example:
  python import-nsfocus-xml-to-mock-bundle.py \\
    --xml ../../standards/mock-data/report_by_vul.xml \\
    --bundle-id nsfocus-vul-template \\
    --out ../../../project_backend/svmp/open-api-service/src/main/resources/mock/engine/bundles/nsfocus-vul-template
"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# AbstractVulResultParser.REGEX_PORT
PORT_PATTERN = re.compile(
    r"^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|"
    r"[1-5][0-9]{4}|[1-9][0-9]{0,3}|0)$"
)

# vuln-model LmItemAppConvert: low=4, moderate=7, high=10 -> VulLevelEnum 2/3/4
LOW_RISK = 4.0
MODERATE_RISK = 7.0
HIGH_RISK = 10.0


def child_text(parent: Optional[ET.Element], tag: str) -> str:
    """Direct child text, same as NsfocusXmlParserV4.getChildText."""
    if parent is None:
        return ""
    for child in parent:
        if child.tag == tag:
            return (child.text or "").strip()
    return ""


def direct_children(parent: Optional[ET.Element], tag: str) -> List[ET.Element]:
    if parent is None:
        return []
    return [c for c in parent if c.tag == tag]


def parse_scan_time(raw: str) -> str:
    if not raw:
        return "1716192000"
    raw = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return str(int(datetime.strptime(raw, fmt).timestamp()))
        except ValueError:
            continue
    return "1716192000"


def risk_to_vul_level(risk: float) -> int:
    """Map NSFocus risk_points to VulLevelEnum: 4=high, 3=medium, 2=low."""
    if risk >= MODERATE_RISK:
        return 4
    if risk >= LOW_RISK:
        return 3
    return 2


def parse_port(port_str: str) -> int:
    try:
        return max(0, int(port_str or "0"))
    except ValueError:
        return 0


def fingerprint(port: str, vul_id: str, protocol: str, service: str) -> str:
    return ":".join([port, vul_id, protocol, service])


def load_vuln_details(target: ET.Element) -> Dict[str, dict]:
    details: Dict[str, dict] = {}
    detail_root = target.find("vuln_detail")
    if detail_root is None:
        return details
    for vuln in direct_children(detail_root, "vuln"):
        vul_id = child_text(vuln, "vul_id")
        if not vul_id:
            continue
        risk_raw = child_text(vuln, "risk_points")
        try:
            risk = float(risk_raw) if risk_raw else 0.0
        except ValueError:
            risk = 0.0
        cve = child_text(vuln, "cve_id")
        cnnvd = child_text(vuln, "cnnvd")
        details[vul_id] = {
            "name": child_text(vuln, "name"),
            "plugin_id": child_text(vuln, "plugin_id"),
            "cve_id": cve,
            "cnnvd": cnnvd,
            "threat_category": child_text(vuln, "threat_category"),
            "risk_points": risk,
            "solution": child_text(vuln, "solution"),
            "description": child_text(vuln, "description"),
            "org_vul_id": cve or cnnvd or "",
        }
    return details


def load_vuln_scanned(target: ET.Element) -> List[dict]:
    """NsfocusXmlParserV4.parseVulScanned: validate port + dedup fingerprint."""
    scanned: List[dict] = []
    cache: Set[str] = set()
    root = target.find("vuln_scanned")
    if root is None:
        return scanned
    for vuln in direct_children(root, "vuln"):
        port_str = child_text(vuln, "port")
        vul_id = child_text(vuln, "vul_id")
        protocol = child_text(vuln, "protocol")
        service = child_text(vuln, "service")
        mess = child_text(vuln, "mess_string")
        if not PORT_PATTERN.match(port_str):
            continue
        key = fingerprint(port_str, vul_id, protocol, service)
        if key in cache:
            continue
        cache.add(key)
        scanned.append(
            {
                "port": port_str,
                "vul_id": vul_id,
                "protocol": protocol,
                "service": service,
                "mess_string": mess,
            }
        )
    return scanned


def load_password_results(target: ET.Element) -> List[dict]:
    results: List[dict] = []
    root = target.find("password_results")
    if root is None:
        return results
    for item in direct_children(root, "password_result"):
        pwd_type = child_text(item, "type")
        if not pwd_type:
            continue
        results.append(
            {
                "type": pwd_type,
                "username": child_text(item, "username"),
                "password": child_text(item, "password"),
            }
        )
    return results


def is_weak_password_scan(task_type: str, target: ET.Element) -> bool:
    if task_type == "4":
        return True
    return bool(load_password_results(target))


def make_instance(
    seq: int,
    scan_kind: str,
    task_id: str,
    ip: str,
    transfer_time: str,
    scanned: dict,
    detail: dict,
    pwd: Optional[dict] = None,
) -> dict:
    vul_id = scanned["vul_id"]
    port = parse_port(scanned["port"])
    protocol = scanned["protocol"]
    service = scanned["service"]
    mess = scanned["mess_string"]

    name = detail.get("name") or mess or ("NSFocus-" + vul_id)
    risk = detail.get("risk_points", 5.0 if scan_kind == "pwd" else 0.0)
    org_vul_id = detail.get("org_vul_id") or ("NSFOCUS-" + vul_id)

    vul_info_id = "VI-%s-%s-%s-%d-%d" % (scan_kind, task_id, vul_id, port, seq)
    inst = {
        "id": seq,
        "vulInfoID": vul_info_id,
        "vulInfoId": vul_info_id,
        "vulID": "VUL-" + vul_id,
        "vulId": "VUL-" + vul_id,
        "vulInfoStat": 1,
        "vulName": name[:200],
        "vulLevel": risk_to_vul_level(risk),
        "orgVulId": org_vul_id[:64],
        "vulNetAddr": ip,
        "vulPort": port,
        "vulSvc": service or protocol,
        "isAccess": 0,
        "transferTime": transfer_time,
        "vulnDisposalId": vul_info_id,
        "extVulnRef": mess[:500] if mess else None,
    }
    if pwd:
        inst["username"] = pwd.get("username")
        inst["password"] = pwd.get("password")
        inst["pwdType"] = pwd.get("type")
    return inst


def parse_appendix_rows(info_elem: ET.Element) -> Tuple[List[str], List[List[str]]]:
    names: List[str] = []
    name_root = info_elem.find("record_result_name")
    if name_root is not None:
        for name_elem in direct_children(name_root, "name"):
            names.append((name_elem.text or "").strip())
    rows: List[List[str]] = []
    for rr in info_elem.findall("record_results"):
        for result in direct_children(rr, "result"):
            values = []
            for val in direct_children(result, "value"):
                values.append((val.text or "").strip())
            if values:
                rows.append(values)
    return names, rows


def is_port_appendix(info_name: str) -> bool:
    return "port" in info_name.lower() or "\u7aef\u53e3" in info_name


def parse_live_instances(
    target: ET.Element, task_id: str, transfer_time: str, limit: int, seq_start: int
) -> Tuple[List[dict], int]:
    ip = child_text(target, "ip") or "0.0.0.0"
    seq = seq_start
    instances: List[dict] = []
    if limit > 0 and len(instances) >= limit:
        return instances, seq
    seq += 1
    vul_info_id = "VI-live-%s-%s-%d" % (task_id, ip.replace(".", "-"), seq)
    instances.append(
        {
            "id": seq,
            "vulInfoID": vul_info_id,
            "vulInfoId": vul_info_id,
            "vulID": "LIVE-" + task_id,
            "vulId": "LIVE-" + task_id,
            "vulInfoStat": 1,
            "vulName": "Host alive: " + ip,
            "vulLevel": 1,
            "orgVulId": "LIVE-PROBE",
            "vulNetAddr": ip,
            "vulPort": 0,
            "vulSvc": "ICMP",
            "isAccess": 0,
            "transferTime": transfer_time,
            "vulnDisposalId": vul_info_id,
            "extVulnRef": "liveProbe=true",
        }
    )
    return instances, seq


def parse_port_instances(
    target: ET.Element, task_id: str, transfer_time: str, limit: int, seq_start: int
) -> Tuple[List[dict], int]:
    ip = child_text(target, "ip") or "0.0.0.0"
    seq = seq_start
    instances: List[dict] = []
    cache: Set[str] = set()
    appendix = target.find("appendix_info")
    if appendix is None:
        return instances, seq
    for info in direct_children(appendix, "info"):
        info_name = child_text(info, "info_name")
        if not is_port_appendix(info_name):
            continue
        names, rows = parse_appendix_rows(info)
        idx_port = next((i for i, n in enumerate(names) if "\u7aef\u53e3" in n or n.lower() == "port"), 0)
        idx_proto = next((i for i, n in enumerate(names) if "\u534f\u8bae" in n or n.lower() == "protocol"), 1)
        idx_svc = next((i for i, n in enumerate(names) if "\u670d\u52a1" in n or n.lower() == "service"), 2)
        idx_state = next((i for i, n in enumerate(names) if "\u72b6\u6001" in n or n.lower() == "state"), 3)
        for row in rows:
            if len(row) <= idx_port:
                continue
            port_str = row[idx_port]
            if not PORT_PATTERN.match(port_str):
                continue
            state = row[idx_state].lower() if len(row) > idx_state else "open"
            if state and state not in ("open", "opened"):
                continue
            proto = row[idx_proto] if len(row) > idx_proto else "tcp"
            service = row[idx_svc] if len(row) > idx_svc else proto
            key = ":".join([port_str, proto, service])
            if key in cache:
                continue
            cache.add(key)
            if limit > 0 and len(instances) >= limit:
                break
            seq += 1
            vul_info_id = "VI-port-%s-%s-%d" % (task_id, port_str, seq)
            instances.append(
                {
                    "id": seq,
                    "vulInfoID": vul_info_id,
                    "vulInfoId": vul_info_id,
                    "vulID": "PORT-" + port_str,
                    "vulId": "PORT-" + port_str,
                    "vulInfoStat": 1,
                    "vulName": ("Open port: %s/%s %s" % (port_str, proto, service))[:200],
                    "vulLevel": 1,
                    "orgVulId": "PORT-SCAN",
                    "vulNetAddr": ip,
                    "vulPort": parse_port(port_str),
                    "vulSvc": service or proto,
                    "vulTransProto": proto.upper() if proto else None,
                    "isAccess": 0,
                    "transferTime": transfer_time,
                    "vulnDisposalId": vul_info_id,
                    "extVulnRef": state,
                }
            )
    return instances, seq


def parse_target_instances(
    target: ET.Element,
    task_id: str,
    task_type: str,
    transfer_time: str,
    limit: int,
    seq_start: int,
    profile: str,
) -> Tuple[List[dict], int]:
    if profile == "live":
        return parse_live_instances(target, task_id, transfer_time, limit, seq_start)
    if profile == "port":
        return parse_port_instances(target, task_id, transfer_time, limit, seq_start)
    ip = child_text(target, "ip") or "0.0.0.0"
    details = load_vuln_details(target)
    scanned_list = load_vuln_scanned(target)
    instances: List[dict] = []
    seq = seq_start
    weak = profile == "pwd" or is_weak_password_scan(task_type, target)
    scan_kind = "pwd" if weak else "vul"

    if weak:
        # VulScanTaskSubDomainServiceImpl.buildVulResultPwd: type.upper() -> scanned.service.upper()
        scanned_by_service = {}
        for s in scanned_list:
            if s.get("service"):
                scanned_by_service[s["service"].upper()] = s
            if s.get("protocol"):
                scanned_by_service.setdefault(s["protocol"].upper(), s)

        def find_scanned_for_password(pwd_type: str) -> Optional[dict]:
            key = pwd_type.upper()
            scanned = scanned_by_service.get(key)
            if scanned is not None:
                return scanned
            lower = pwd_type.lower()
            for candidate in scanned_list:
                mess = candidate.get("mess_string") or ""
                if lower in mess.lower():
                    return candidate
            return None

        for pwd in load_password_results(target):
            scanned = find_scanned_for_password(pwd["type"])
            if scanned is None:
                continue
            detail = details.get(scanned["vul_id"], {})
            if limit > 0 and len(instances) >= limit:
                break
            seq += 1
            instances.append(
                make_instance(seq, scan_kind, task_id, ip, transfer_time, scanned, detail, pwd)
            )
        # Fallback: password_results empty but vuln_scanned present (template edge case)
        if not instances:
            for scanned in scanned_list:
                detail = details.get(scanned["vul_id"], {})
                if not detail and not scanned.get("mess_string"):
                    continue
                if limit > 0 and len(instances) >= limit:
                    break
                seq += 1
                instances.append(
                    make_instance(seq, scan_kind, task_id, ip, transfer_time, scanned, detail)
                )
    else:
        # buildVulResult: prefer vul_detail; allow mess-only scanned rows
        for scanned in scanned_list:
            detail = details.get(scanned["vul_id"])
            if detail is None and not scanned.get("mess_string"):
                continue
            if limit > 0 and len(instances) >= limit:
                break
            seq += 1
            instances.append(
                make_instance(seq, scan_kind, task_id, ip, transfer_time, scanned, detail)
            )

    return instances, seq


def parse_xml_instances(xml_path: Path, limit: int, profile: str) -> Tuple[dict, List[dict]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    NSFOCUS_VENDOR = "\u7eff\u76df\u79d1\u6280"
    vendor = child_text(root.find(".//report"), "vendor")
    if vendor and vendor != NSFOCUS_VENDOR:
        raise SystemExit("Unsupported vendor (expect NSFocus): %s" % vendor)

    task_elem = root.find(".//report/task")
    task_id = child_text(task_elem, "id") or "mock"
    task_name = child_text(task_elem, "name") or xml_path.stem
    task_type = child_text(task_elem, "task_type")
    transfer_time = parse_scan_time(child_text(task_elem, "time_end_scan"))
    effective_profile = profile
    if effective_profile == "auto":
        effective_profile = "pwd" if task_type == "4" else "vul"
    scan_kind = effective_profile if effective_profile in ("live", "port") else (
        "pwd" if task_type == "4" or effective_profile == "pwd" else "vul"
    )
    if effective_profile == "pwd":
        task_type = "4"

    instances: List[dict] = []
    seq = 0
    for target in root.findall(".//report/targets/target"):
        batch, seq = parse_target_instances(
            target, task_id, task_type, transfer_time, limit, seq, effective_profile
        )
        instances.extend(batch)
        if limit > 0 and len(instances) >= limit:
            instances = instances[:limit]
            break

    meta = {
        "taskId": task_id,
        "taskName": task_name,
        "taskType": task_type,
        "scanKind": scan_kind,
        "sourceXml": xml_path.name,
        "transferTime": transfer_time,
        "parserRef": "NsfocusXmlParserV4",
        "profile": effective_profile,
    }
    return meta, instances


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import NSFocus Aurora XML to open-api mock bundle (NsfocusXmlParserV4 aligned)"
    )
    parser.add_argument("--xml", required=True, help="Path to aurora report XML")
    parser.add_argument("--bundle-id", required=True, help="Bundle id")
    parser.add_argument("--out", required=True, help="Output bundle directory")
    parser.add_argument("--limit", type=int, default=0, help="Max instances (0=all)")
    parser.add_argument("--match-task-name", default="", help="manifest match.taskNameContains")
    parser.add_argument("--match-ext-prefix", default="", help="manifest match.extTaskIdPrefix")
    parser.add_argument("--profile", default="auto",
                        choices=["auto", "vul", "pwd", "live", "port"],
                        help="Parse profile (auto=from task_type)")
    parser.add_argument("--scan-template-id", type=int, default=0, help="match.scanTemplateId")
    parser.add_argument("--report-template-ids", default="2001,2002",
                        help="match.reportTemplateIds comma list")
    parser.add_argument("--vuln-types", default="",
                        help="match.vulnTypes comma list, e.g. 1,2 or 3")
    args = parser.parse_args()

    xml_path = Path(args.xml)
    if not xml_path.is_file():
        raise SystemExit("XML not found: %s" % xml_path)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = args.profile
    meta, instances = parse_xml_instances(xml_path, args.limit, profile)
    task_name_contains = args.match_task_name or None
    if task_name_contains and len(task_name_contains) > 40:
        task_name_contains = task_name_contains[:40]

    report_ids = [int(x.strip()) for x in args.report_template_ids.split(",") if x.strip()]
    vuln_types = [int(x.strip()) for x in args.vuln_types.split(",") if x.strip()]
    match_doc = {
        "extTaskIdPrefix": args.match_ext_prefix or None,
        "taskNameContains": task_name_contains,
    }
    if args.scan_template_id > 0:
        match_doc["scanTemplateId"] = args.scan_template_id
    if report_ids:
        match_doc["reportTemplateIds"] = report_ids
    if vuln_types:
        match_doc["vulnTypes"] = vuln_types

    instances_doc = {
        "bundleId": args.bundle_id,
        "description": (
            "NSFocus %s scan (NsfocusXmlParserV4), task=%s, source=%s, count=%d, profile=%s"
            % (meta["scanKind"], meta["taskId"], meta["sourceXml"], len(instances), profile)
        ),
        "match": match_doc,
        "instances": instances,
    }
    manifest = {
        "bundleId": args.bundle_id,
        "description": instances_doc["description"],
        "match": match_doc,
        "instanceCount": len(instances),
        "sourceXml": meta["sourceXml"],
        "taskId": meta["taskId"],
        "taskName": meta["taskName"],
        "scanKind": meta["scanKind"],
        "profile": meta["profile"],
        "parserRef": meta["parserRef"],
        "importedAt": datetime.now().strftime("%Y-%m-%d"),
    }

    (out_dir / "instances.json").write_text(
        json.dumps(instances_doc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    raw_copy = out_dir / "source.xml"
    if not raw_copy.exists():
        raw_copy.write_bytes(xml_path.read_bytes())

    print("Wrote bundle '%s' with %d instances -> %s" % (args.bundle_id, len(instances), out_dir))


if __name__ == "__main__":
    main()
