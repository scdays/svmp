# 任务结束 · 数据外发模板（当前版本）

开放平台与 SVMP 任务结束外发以 **四阶段 XML**（及同构 JSON）为主；字段目录与引擎样本供 `tools/` 解析使用。

## 目录说明

| 子目录 | 内容 |
|--------|------|
| `yaml/` | 当前启用的外发模板（四阶段 + 整包 + 开放平台兜底 + 部侧报送） |
| `catalogs/` | `field-catalog.json`、`phase-field-catalog.json` |
| `engine/` | 引擎正式 Aurora 样本 XML、`数据外发字段说明.html` |
| `schemas/` | `aurora-report.schema.json` 与结构说明 |

## 模板清单（yaml/）

| exportTemplateId | 说明 |
|------------------|------|
| `tpl-svmp-xml-scan-bundle` | 默认整包：四阶段 XML（`match.exportPackageProfile: svmp-xml-phases`） |
| `tpl-svmp-phase-live` / `-port` / `-vuln` / `-weakpwd` | 单阶段外发 |
| `tpl-open-api-default` | Partner 未命中专用模板时的 JSON 兜底 |
| `tpl-miit-2025-vulInfoLst` | 部侧 `vulInfoLst` 报送结构 |

## 生成与维护

```bash
python3 tools/parse_export_fields_html.py templates/engine/数据外发字段说明.html -o templates --xml-phases
python3 tools/build_export_xml_phases.py templates/catalogs/field-catalog.json -o templates
python3 tools/parse_export_xml_samples.py -d templates/engine
```

存活/端口推导样例可由 `build_export_xml_phases.py` 写入 `samples/`（运行期生成，不入库）。
