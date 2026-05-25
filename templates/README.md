# 任务结束 · 数据外发模板（当前版本）

开放平台与 SVMP 任务结束外发以 **四阶段 XML**（及同构 JSON）为主；字段目录与扫描结果样本供 `tools/` 解析使用。

## 目录说明

| 子目录 | 内容 |
|--------|------|
| `yaml/` | 当前启用的外发模板（四阶段 + 整包 + 开放平台兜底 + 部侧报送） |
| `catalogs/` | `field-catalog.json`、`phase-field-catalog.json` |
| `engine/` | 扫描结果样本 XML、数据外发字段说明 HTML |
| `schemas/` | 扫描结果 XML schema |
| `xml/` | §5.1.1 扫描任务配置（`scanTask` 示例） |

## 扫描任务配置（xml/ · `POST /tasks/file`）

| 文件 | 说明 |
|------|------|
| `scan-task-vuln-example.xml` | 模式 A：type=1，引用平台模板 1001/2001 |
| `scan-task-vuln-inline-example.xml` | 模式 B：`<server>` 内联扫描阶段 + 登陆检查 `<targets>` + `<report>` |
| `scan-task-web-example.xml` | 模式 A：type=2，引用平台模板 1001/2001 |
| `scan-task-pwdguess-example.xml` | 模式 B：type=3，`<server>` 内联 pwdGuess + `<report>` |
| `scan-task-inline-templates-reference.xml` | `<server>` 内联扫描阶段 + `<report>` 全量结构 |

**`<server>`**：`taskName` / `priority` / **`targets`**（扫描地址，`,` 或 `;` 分隔）及内联扫描阶段（模式 B）。  
**根级 `<targets>`**：登陆检查信息，**始终存在**；无登陆检查时写 `<targets/>`。  
**模式 A**：`scanTemplateId` + `reportTemplateId`（引用平台附录 H）。  
**模式 B**：扫描阶段内联于 `<server>` + 根级 `<report>`（自定义，不使用平台内置模板）。  
部侧扩展参数见接口规范 **附录 I**（XML 元素 `<miitExt>`）。

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
