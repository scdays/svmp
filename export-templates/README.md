# 任务结束 · 数据外发模板

将 **`数据外发字段说明.html`** 放入本目录后执行解析：

```bash
python3 tools/parse_export_fields_html.py export-templates/数据外发字段说明.html -o export-templates --write-drafts
```

生成物：

| 文件 | 说明 |
|------|------|
| `field-catalog.json` | 从 HTML 表格提取的字段目录（按章节） |
| `draft-tpl-*.yaml` | 各章节对应的 Export Template 草案（需校对 `match.scanTemplateIds` 与 `source`） |

手工维护的参考模板：

- `tpl-open-api-default.yaml` — JSON 扁平列表
- `tpl-miit-2025-vulInfoLst.yaml` — 部侧嵌套结构

设计说明见主文档 **§十二**。
