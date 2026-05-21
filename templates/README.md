# 任务结束 · 数据外发模板

已根据 **`engine/数据外发字段说明.html`**（pdf2htmlEX 版式）解析生成字段目录与模板草案。

## 目录说明

| 子目录 | 内容 |
|--------|------|
| `yaml/` | 外发模板定义（`tpl-*.yaml`） |
| `catalogs/` | `field-catalog.json`、`phase-field-catalog.json` |
| `engine/` | 引擎正式样本 XML、数据外发字段说明 HTML |
| `reference/` | 结构参考 `report_by_*.xml` |
| `samples/` | 存活/端口推导样例 XML |
| `schemas/` | Aurora schema 与结构说明 |

## 推荐：四阶段 XML 外发包

| 阶段 | 外发文件 | 模板 |
|------|----------|------|
| 主机存活探测 | `主机存活探测结果.xml` | `yaml/tpl-svmp-phase-live.yaml` |
| 端口扫描 | `端口扫描结果.xml` | `yaml/tpl-svmp-phase-port.yaml` |
| 系统漏洞扫描 | `系统漏洞扫描结果.xml` | `yaml/tpl-svmp-phase-vuln.yaml` |
| 弱口令扫描 | `弱口令扫描结果.xml` | `yaml/tpl-svmp-phase-weakpwd.yaml` |

**整包模板**：`yaml/tpl-svmp-xml-scan-bundle.yaml`（`tar.gz` 内含上述 XML，按任务 `capabilities` 选择性生成）。

- **正式引擎样本**（绿盟 Aurora）：`engine/系统漏洞扫描结果.xml`、`engine/弱口令扫描结果.xml`
- 字段映射：`catalogs/phase-field-catalog.json`、`schemas/aurora-report.schema.json`
- 结构说明：`schemas/README.md`
- 存活/端口推导样例：`samples/`（漏洞/弱口令请以 `engine/` 正式样本为准）

```bash
python3 tools/build_export_xml_phases.py templates/catalogs/field-catalog.json -o templates
python3 tools/parse_export_fields_html.py templates/engine/数据外发字段说明.html -o templates --xml-phases
```

## Legacy：按 engineTaskType 的 txt 包（兼容）

| engineTaskType | 包内主要文件 | exportTemplateId |
|----------------|--------------|------------------|
| 1 | `task_info.txt` 等 | `yaml/tpl-svmp-task-type-1.yaml` |
| 8 | 同上 + 站点 | `yaml/tpl-svmp-task-type-8.yaml` |
| 16 | 资产发现 | `yaml/tpl-svmp-task-type-16.yaml` |
| 4 | 口令猜测 | `yaml/tpl-svmp-task-type-4.yaml` |

完整字段列表见 **`catalogs/field-catalog.json`**。新对接优先使用 **XML 四阶段包**。

## 重新解析 HTML

```bash
python3 tools/parse_export_fields_html.py templates/engine/数据外发字段说明.html -o templates --write-drafts
```

开放平台兜底模板：`yaml/tpl-open-api-default.yaml`（部侧同名 JSON 字段）。
