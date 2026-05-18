# 四阶段 XML 外发结构说明

引擎任务结束后，外发包推荐为 **`tar.gz`**，内含下列 XML（按任务启用的扫描能力选择性产出）：

| 文件 | 根元素 | 能力键 | 替代 legacy txt |
|------|--------|--------|-----------------|
| `主机存活探测结果.xml` | `LiveProbeResult` | `liveCheck` | `task_info.txt`（摘要）+ `asset_info.txt`（存活列） |
| `端口扫描结果.xml` | `PortScanResult` | `portScan` | `asset_info.txt`（端口/服务） |
| `系统漏洞扫描结果.xml` | `SystemVulnScanResult` | `vulnScan` | `vul_info.txt` + `asset_vuls.txt` |
| `弱口令扫描结果.xml` | `WeakPasswordScanResult` | `weakPasswordScan` | `asset_pwds.txt` |

## 公共约定

- 编码 **UTF-8**，根节点带 `version="1.0"` 属性。
- 各文件均含 **`TaskMeta`**（任务 ID、`taskUuid`、`taskType`、`hostCount` 等），与 HTML 中 `task_info.txt` 字段对齐。
- 明细列表使用复数容器：`Hosts` / `Targets` / `Vulnerabilities` / `WeakAccounts`。
- 弱口令密码字段对外发时应经平台脱敏（样例中为 `***`）。

## 样例与字段目录

- 样例 XML：`export-templates/samples/`
- 分 phase 字段映射：`export-templates/phase-field-catalog.json`
- 组装模板：`tpl-svmp-xml-scan-bundle.yaml`、单阶段 `tpl-svmp-phase-*.yaml`

生成命令：

```bash
python3 tools/build_export_xml_phases.py export-templates/field-catalog.json -o export-templates
# 或与 HTML 解析一并执行：
python3 tools/parse_export_fields_html.py export-templates/数据外发字段说明.html -o export-templates --xml-phases
```
