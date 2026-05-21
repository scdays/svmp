# 四阶段 XML 外发结构说明

引擎任务结束后，外发包推荐为 **`tar.gz`**，内含下列 XML（按任务启用的扫描能力选择性产出）。

## 正式样本（绿盟 Aurora）

**`templates/engine/`** 下为引擎正式外发文件（请勿与 `samples/` 下推导占位混淆）：

| 文件 | task_type | 根元素 | 说明 |
|------|-----------|--------|------|
| `engine/系统漏洞扫描结果.xml` | `1` | `<aurora>` | `vuln_scanned` + `vuln_detail`（CVE/CNNVD 等） |
| `engine/弱口令扫描结果.xml` | `4` | `<aurora>` | `password_results` + 弱口令类 `vuln_detail` |

结构概要：

```text
aurora
├── ret_code / ret_msg
└── data
    ├── page, page_size, page_total, target_total
    └── report
        ├── vendor, product, version, sysvul_version, vultpl_version
        ├── task (id, name, task_type, time_start_scan, time_end_scan, …)
        ├── scanned_ip_count, failed_hosts
        └── targets/target (ip, host_score, vul_score, …)
            ├── vuln_scanned/vuln     # 目标上扫描到的漏洞实例
            ├── vuln_detail/vuln      # 漏洞库详情（name, cve_id, cnnvd, risk_points, …）
            ├── password_results/password_result   # 弱口令专扫
            └── appendix_info/info    # 端口 Banner、远程端口信息等
```

解析产物：

- **`aurora-report.schema.json`**：`python3 tools/parse_export_xml_samples.py`
- **平台字段映射**：`catalogs/phase-field-catalog.json` 中 `vuln` / `weakpwd` 阶段的 `auroraPath` → `source`

## 存活 / 端口（推导结构，待引擎样本）

| 文件 | 根元素 | 状态 |
|------|--------|------|
| `主机存活探测结果.xml` | `LiveProbeResult` | 由 HTML 字段推导；`build_export_xml_phases.py` 可生成占位 |
| `端口扫描结果.xml` | `PortScanResult` | 由 HTML 字段推导；`build_export_xml_phases.py` 可生成占位 |

## 生成命令

```bash
python3 tools/parse_export_xml_samples.py
python3 tools/build_export_xml_phases.py templates/catalogs/field-catalog.json -o templates
```
