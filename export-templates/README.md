# 任务结束 · 数据外发模板

已根据 **`数据外发字段说明.html`**（pdf2htmlEX 版式）解析生成字段目录与模板草案。

## 推荐：四阶段 XML 外发包

不再以多份 **txt**（`task_info.txt`、`asset_info.txt`、`asset_vuls.txt`、`vul_info.txt`）为主消费形态，改为按扫描阶段产出 **XML**：

| 阶段 | 外发文件 | 模板 |
|------|----------|------|
| 主机存活探测 | `主机存活探测结果.xml` | `tpl-svmp-phase-live.yaml` |
| 端口扫描 | `端口扫描结果.xml` | `tpl-svmp-phase-port.yaml` |
| 系统漏洞扫描 | `系统漏洞扫描结果.xml` | `tpl-svmp-phase-vuln.yaml` |
| 弱口令扫描 | `弱口令扫描结果.xml` | `tpl-svmp-phase-weakpwd.yaml` |

**整包模板**：`tpl-svmp-xml-scan-bundle.yaml`（`tar.gz` 内含上述 XML，按任务 `capabilities` 选择性生成）。

- **正式引擎样本**（绿盟 Aurora）：`系统漏洞扫描结果.xml`、`弱口令扫描结果.xml`（与本目录同级）
- 字段映射：`phase-field-catalog.json`、`xml-schemas/aurora-report.schema.json`
- 结构说明：`xml-schemas/README.md`
- 存活/端口推导样例：`samples/`（漏洞/弱口令请以正式样本为准）

```bash
# 自 field-catalog 生成 XML 阶段目录与模板
python3 tools/build_export_xml_phases.py export-templates/field-catalog.json -o export-templates

# 自 HTML 解析并一并生成 XML 阶段产物
python3 tools/parse_export_fields_html.py export-templates/数据外发字段说明.html -o export-templates --xml-phases
```

## Legacy：按 engineTaskType 的 txt 包（兼容）

| engineTaskType | 宏 | 包内主要文件 | exportTemplateId |
|----------------|-----|--------------|------------------|
| 1 | TASK_SYS_SCAN | `task_info.txt`、`asset_info.txt`、`asset_vuls.txt`、`vul_info.txt` | `tpl-svmp-task-type-1.yaml` |
| 8 | TASK_WEB_SCAN | 同上 + 站点 `site_info/*.txt` | `tpl-svmp-task-type-8.yaml` |
| 16 | TASK_ASSET_FIND | `task_info.txt`、`asset_info.txt` | `tpl-svmp-task-type-16.yaml` |
| 4 | TASK_PWD_SCAN | 口令猜测专用字段 | `tpl-svmp-task-type-4.yaml` |
| — | 处置单外发 | `vul_info.txt` 等 | `tpl-svmp-disposal-workflow.yaml` |
| — | 预警外发 | `intell_info.txt`、`warning_info.txt` | `tpl-svmp-early-warning.yaml` |

完整字段列表见 **`field-catalog.json`**。新对接优先使用 **XML 四阶段包**；txt 模板保留用于存量 Partner。

## 重新解析 HTML

```bash
python3 tools/parse_export_fields_html.py export-templates/数据外发字段说明.html -o export-templates --write-drafts
```

## 平台侧用法（设计方案 §十二）

1. 任务 `TASK_COMPLETED` 时读取任务的扫描能力（`liveCheck` / `portScan` / 漏洞 / 弱口令）或 `exportTemplateId`
2. 默认匹配 `tpl-svmp-xml-scan-bundle`；兼容场景可指定 legacy `tpl-svmp-task-type-*`
3. 渲染为 `tar.gz` 或 JSON/CSV，触发 `EXPORT_READY` Webhook

开放平台兜底模板：`tpl-open-api-default.yaml`（部侧同名 JSON 字段）。
