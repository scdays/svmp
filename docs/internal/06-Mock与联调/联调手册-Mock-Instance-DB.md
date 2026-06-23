# Mock 实例 MySQL 落库联调手册（OP-MOCK-P1-DB）

## 前置

- `spring.profiles.active=mock`
- `open-api.engine.adapter-mode=mock`
- `open-api.engine.mock.auto-ingest-instances-on-finish=true`（默认）
- MySQL 已执行 Liquibase（`open_vuln_instance` / `open_task` 扩展字段）

## 用例 1：scanTemplateId=1001 + type=1 落库约 500 条

1. `POST /api/open/v1/tasks/vul`：`scanTemplateId=1001`、`type=1`、`reportTemplateId=2001`
2. 等待 `task-finish-delay-seconds`（默认 5s）后 `GET /tasks/{taskId}` → `FINISHED`
3. 查库：`SELECT COUNT(*) FROM open_vuln_instance WHERE task_id=?` → 约 500
4. `POST /instances/search`：`taskId` 分页 → 条数与 fixture `scan-1001-vul` 一致

## 用例 2：处置持久化

1. 取一条 `vulInfoId`（格式 `{taskId}-VI-...`）
2. `PUT /instances/{vulInfoId}/verify` → `VALID`
3. `GET /instances/{vulInfoId}` → `vulInfoStat=2`
4. 查库 `vul_info_stat=2`

## 用例 3：重启后任务进度与实例

1. 重启 `open-api-service`
2. `GET /tasks/{taskId}` → 仍为 `FINISHED`（非 `mock engine task not found`）
3. `POST /instances/search` → 数据仍在

## 用例 4：模板 1002 / 1003 / type=3

| scanTemplateId | type | 预期 bundle | 典型条数 |
|----------------|------|-------------|----------|
| 1001 | 3 | scan-1001-pwd | 8 |
| 1002 | 1 | scan-1002-live | 1 |
| 1003 | 1 | scan-1003-port | 5 |

## 用例 5：auto-ingest=false

1. 配置 `open-api.engine.mock.auto-ingest-instances-on-finish=false`
2. 新建任务并 FINISHED
3. 库表无新行；`POST /instances/search` 仍可读 fixture

## 用例 6：幂等 ingest

1. 同一 `taskId` 多次 `GET /tasks/{taskId}`（已 FINISHED）
2. `open_vuln_instance` 行数不增长、`vul_info_id` UK 无冲突

## 验收脚本

```powershell
$env:JAVA_HOME="C:\Program Files\Java\jdk1.8.0_202"
powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile
```

## 相关文档

- PRD：`svmp/docs/internal/open-api-mock-instance-db-PRD.md`
- Mock 总方案：`svmp/docs/internal/引擎对接与Mock模式方案.md`
