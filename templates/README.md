# 任务结束 · 数据外发模板（当前版本）

开放平台与 SVMP 任务结束外发以 **四阶段 XML**（及同构 JSON）为主；字段目录与引擎样本供 `tools/` 解析使用。

## 目录说明

| 子目录 | 内容 |
|--------|------|
| `yaml/` | 当前启用的外发模板（四阶段 + 整包 + 开放平台兜底 + 部侧报送） |
| `catalogs/` | `field-catalog.json`、`phase-field-catalog.json` |
| `engine/` | 引擎正式 Aurora 样本 XML、`数据外发字段说明.html` |
| `schemas/` | `aurora-report.schema.json` 与结构说明 |
| `xml/` | §5.1.1 扫描任务配置（`ScanTask` 示例）及引擎厂商参考 `config.xml` |

## 扫描任务配置（xml/ · §5.1.1 `file`）

| 文件 | 说明 |
|------|------|
| `scan-task-vuln-example.xml` | 模式 A：type=1，引用平台模板 1001/2001 |
| `scan-task-vuln-inline-example.xml` | 模式 B：富文本 target + 内联 scanTemplate/reportTemplate |
| `scan-task-web-example.xml` | 模式 A：type=2，引用平台模板 1002/2001 |
| `scan-task-pwdguess-example.xml` | 模式 B：type=3，内联模板 |
| `scan-task-inline-templates-reference.xml` | 内联 scanTemplate/reportTemplate 全量结构 |
| `config.xml` | 引擎厂商原始配置（非开放平台格式） |

**模式 A**：`scanTemplateId` + `reportTemplateId`（引用平台附录 H）。  
**模式 B**：`<scanTemplate>` + `<reportTemplate>`（自定义，不使用平台内置模板）。

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
