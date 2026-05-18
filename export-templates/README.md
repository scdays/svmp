# 任务结束 · 数据外发模板

已根据 **`数据外发字段说明.html`**（pdf2htmlEX 版式）解析生成字段目录与模板草案。

## 解析结果摘要

| engineTaskType | 宏 | 外发包 | 模板 ID |
|----------------|-----|--------|---------|
| 1 | TASK_SYS_SCAN | tar.gz：`task_info.txt`、`asset_info.txt`、`asset_vuls.txt`、`vul_info.txt` | `tpl-svmp-task-type-1.yaml` |
| 8 | TASK_WEB_SCAN | 同上 + 站点 `site_info/*.txt` | `tpl-svmp-task-type-8.yaml`（继承 type-1） |
| 16 | TASK_ASSET_FIND | `task_info.txt`、`asset_info.txt` | `tpl-svmp-task-type-16.yaml`（继承 type-1） |
| 4 | TASK_PWD_SCAN | 口令猜测专用字段 | `tpl-svmp-task-type-4.yaml` |
| — | 处置单外发 | `vul_info.txt` 等 | `tpl-svmp-disposal-workflow.yaml` |
| — | 预警外发 | `intell_info.txt`、`warning_info.txt` | `tpl-svmp-early-warning.yaml` |

完整字段列表见 **`field-catalog.json`**（含中文注释说明）。

## 重新解析

```bash
python3 tools/parse_export_fields_html.py export-templates/数据外发字段说明.html -o export-templates --write-drafts
```

## 平台侧用法（设计方案 §十二）

1. 任务 `TASK_COMPLETED` 时读取任务的 `engineTaskType` / `scanTemplateId`
2. 匹配 `export-templates/tpl-*.yaml`
3. 渲染为 tar.gz 或 JSON/CSV，触发 `EXPORT_READY` Webhook

开放平台兜底模板：`tpl-open-api-default.yaml`（部侧同名 JSON 字段）。
