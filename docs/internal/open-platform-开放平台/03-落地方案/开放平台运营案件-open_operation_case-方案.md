# 开放平台运营案件（open_operation_case）方案 · 方案三

> **状态**：设计稿 v1.0 · 2026-06-18  
> **读者**：open-api-service 后端、asset-openplatform-manage 前端、产品/运营  
> **原型**：`svmp/docs/internal/prototypes/open-platform-admin-prototype.html`（运营案件章节）

---

## 1. 背景与目标

### 1.1 问题

| 现象 | 根因 |
|------|------|
| API 调用记录全有，但验证/处置/修复核验无法像 OPEN 编排任务一样运营 | 缺少**业务平面一等公民句柄** |
| `api_invocation` 是治理记录，不是可跟踪的「案件」 | 异步完成与受理调用脱钩；批量 1:N |
| `open_task` 有工作台，`verify-fix` 仅有 mock 菜单 | 未统一运营壳层 |
| `open_vuln_instance` 是状态快照，不是操作单 | 无法列表检索「某次验证工单」 |

### 1.2 目标

1. **统一句柄**：所有 Partner 写操作（及内部异步延续）归属 `case_id`
2. **统一工作台**：一种 UI 壳 + 按 `case_type` 渲染业务面板（对齐 `OpenTaskWorkspace`）
3. **统一关联**：`api_invocation` / `webhook_delivery_log` / `open_vuln_instance_log` 均挂 `case_id`
4. **渐进迁移**：`open_task`、`open_verify_fix_job` 保留，通过 **投影/视图** 纳入案件体系，避免大爆炸重写

---

## 2. 概念模型

```
Partner 请求
    → 创建 open_operation_case（ACCEPTED）
    → 写 api_invocation（resource_type=CASE, resource_id=caseId）
    → 执行业务（同步 DONE / 异步 RUNNING）
    → 子流程更新 case + 写 case_event
    → 完成 → Webhook（payload 带 caseId）
```

### 2.1 case_type 枚举

| case_type | 说明 | 主资源 | 来源 API |
|-----------|------|--------|----------|
| `TASK_SCAN` | 扫描/排查/验证编排 | `task_id` | POST `/tasks/vul`、文件创建 |
| `INSTANCE_VERIFY` | 单实例验证（真假） | `vul_info_id` | POST `.../verify` |
| `INSTANCE_REMEDIATE` | 单实例处置 | `vul_info_id` | POST `.../remediate` |
| `VERIFY_FIX` | 修复核验复扫 | `job_id` | POST `.../verify-fix` |
| `INSTANCE_BATCH` | 批量写操作（可选） | `batch_id` | POST `.../batch` |

> **TASK_SCAN** 与现有 `open_task` 1:1：`open_task.case_id` 回填或 `open_operation_case.ref_task_id` 互指。

### 2.2 状态机

```
ACCEPTED → RUNNING → FINISHED
              ↘ FAILED
              ↘ PARTIAL_FAILED（批量/多目标）
```

| 状态 | 含义 |
|------|------|
| ACCEPTED | 已受理，尚未执行业务副作用 |
| RUNNING | 异步进行中（verify-fix、task-center 子任务） |
| FINISHED | 终态成功 |
| FAILED | 终态失败 |
| PARTIAL_FAILED | 批量部分失败 |

---

## 3. 数据模型

### 3.1 open_operation_case（主表）

| 字段 | 类型 | 说明 |
|------|------|------|
| case_id | VARCHAR(32) PK | `CASE-{uuid12}` |
| partner_id | VARCHAR(64) | Partner |
| case_type | VARCHAR(32) | 见上表 |
| status | VARCHAR(16) | 状态机 |
| title | VARCHAR(256) | 运营列表展示标题（可自动生成） |
| primary_resource_type | VARCHAR(32) | TASK / INSTANCE / VERIFY_FIX_JOB |
| primary_resource_id | VARCHAR(128) | taskId / vulInfoId / jobId |
| batch_id | VARCHAR(128) | 批量幂等批次 |
| invocation_id | VARCHAR(64) | 受理 API 调用 |
| idempotency_key | VARCHAR(128) | 幂等键 |
| request_summary_json | TEXT | 请求摘要（脱敏） |
| result_summary_json | TEXT | 结果摘要 |
| error_message | VARCHAR(512) | 失败原因 |
| started_at / finished_at | DATETIME | |
| created_at / updated_at | DATETIME | |

索引：`partner_id + case_type + status`、`primary_resource_id`、`batch_id`、`invocation_id`

### 3.2 open_operation_case_target（多目标，可选）

批量 verify-fix / batch verify / batch remediate 时一行一个目标：

| 字段 | 说明 |
|------|------|
| case_id | 所属案件 |
| target_key | vul_info_id |
| target_status | PENDING/DONE/FAILED |
| prev_stat / result_stat | 状态跃迁 |
| payload_json | 单项请求/结果 |

> 单实例操作可不用 target 表，直接写主表 + `open_vuln_instance_log.case_id`。

### 3.3 open_operation_case_event（时间线）

| 字段 | 说明 |
|------|------|
| case_id | |
| event_type | ACCEPTED / DISPATCHED / SUB_FINISHED / STATE_CHANGED / WEBHOOK_SENT / … |
| event_payload_json | |
| created_at | |

### 3.4 关联表扩展

| 表 | 新增字段 | 用途 |
|----|----------|------|
| api_invocation | case_id | 反向查案件 |
| webhook_delivery_log | case_id | 工作台 Webhook Tab |
| open_vuln_instance_log | case_id | 跃迁与案件绑定 |
| open_task | case_id | TASK_SCAN 互指 |
| open_verify_fix_job | case_id | VERIFY_FIX 互指 |

---

## 4. 与现有实体映射

| 现有 | 方案三处理 |
|------|------------|
| open_task | `case_type=TASK_SCAN`，case 工作台复用现有 `OpenTaskWorkspace` 数据，**壳层统一** |
| open_task_sub | 作为 case_event + 子资源，不单独建 case |
| open_verify_fix_job | `case_type=VERIFY_FIX`，job 字段迁入案件载荷面板 |
| open_vuln_instance | primary_resource 指向 vulInfoId；实例详情页链到最近 N 条 case |
| api_invocation | 受理时写 case_id；历史数据可按 resource_id 回填 |
| open_vuln_instance_log | 写 log 时带 case_id |

---

## 5. Admin API（internal）

### 5.1 列表

```
GET /internal/admin/operation-cases
  ?partnerId=&caseType=&status=&primaryResourceId=&page=&size=
```

### 5.2 工作台（统一）

```
GET /internal/admin/operation-cases/{caseId}/workspace
```

响应结构（统一壳）：

```json
{
  "case": { "caseId", "caseType", "status", "partnerId", "title", ... },
  "summary": { "statCards": [...] },
  "timeline": [ { "at", "eventType", "text", "level" } ],
  "invocations": [ ... ],
  "webhooks": [ ... ],
  "stateLogs": [ ... ],
  "payload": { }
}
```

`payload` 按 `caseType` 多态：

| caseType | payload 内容 |
|----------|----------------|
| TASK_SCAN | 等同 `OpenTaskWorkspaceDto` |
| INSTANCE_VERIFY / INSTANCE_REMEDIATE | 实例快照 + 本次请求/响应 + 跃迁 |
| VERIFY_FIX | job + items + VTC 字段 + 复扫结果 |

### 5.3 操作（按类型扩展）

| caseType | 运营动作 |
|----------|----------|
| TASK_SCAN | 重试下发、查看 survey 结果（已有） |
| VERIFY_FIX | 重试 VTC 下发、导入复扫 XML、手动完成 |
| INSTANCE_* | 仅观测（或运营强制改状态，二期） |

---

## 6. 写入链路改造

### 6.1 InvocationPipeline（统一入口）

```text
start(ctx)
  → case = caseService.openAccepted(operationId, ctx)
  → ctx.setCaseId(case.getCaseId())
handler.execute()
  → caseService.onSyncSuccess(caseId, result)  // 同步
finish(ctx, response)
  → invocation.case_id = ctx.caseId
```

### 6.2 异步

| 场景 | 行为 |
|------|------|
| verify-fix accept | case RUNNING；job.case_id = caseId |
| VTC/Kafka 完成 | caseService.onAsyncProgress / onFinished |
| task-center 编排 | TASK_SCAN case 在 createTask 时创建，子任务事件写 case_event |

### 6.3 跃迁日志

`OpenVulnInstanceAudit` 增加 `caseId`；`open_vuln_instance_log.case_id` 必填（新写入）。

---

## 7. 前端（asset-openplatform-manage）

### 7.1 菜单

```
运营中心
  ├── 运营案件（列表）          ← 新
  ├── OPEN 编排任务（可合并为 case 筛选 TASK_SCAN）
  └── 修复核验（可合并为 case 筛选 VERIFY_FIX）
```

### 7.2 路由

| 路由 | 页面 |
|------|------|
| `/operation-cases` | 列表 + 筛选 |
| `/operation-cases/:caseId` | 统一工作台 |
| `/operation-cases/:caseId?tab=timeline` | 深链 Tab |

### 7.3 组件

```
OperationCaseLayout.vue      # 壳：头、状态、Tab
OperationCaseList.vue
TaskScanCasePanel.vue        # 嵌入原 TaskWorkspace
InstanceOpCasePanel.vue      # verify / remediate
VerifyFixCasePanel.vue       # 修复核验
CaseTimeline.vue
CaseInvocationList.vue
```

---

## 8. 实施分期

| 阶段 | 范围 | 工期（估） |
|------|------|------------|
| **W1** | 表结构 + case 创建/列表/详情壳 + invocation.case_id 回填 | 1 周 |
| **W2** | VERIFY_FIX、INSTANCE_VERIFY/REMEDIATE 接入 + workspace payload | 1 周 |
| **W3** | TASK_SCAN 与 open_task 双写/投影 + 前端统一工作台 | 1 周 |
| **W4** | 历史回填、batch 案件、运营操作（重试） | 1 周 |

---

## 9. 风险与决策

| 项 | 决策 |
|----|------|
| open_task 是否废弃 | **不废弃**；TASK_SCAN case 为运营视图，task 为执行实体 |
| 批量 API | 一个 batch 一个 case + case_target 多行 |
| 与 vul-pass 关系 | open-api 侧案件；vul-pass 仍用 vul_scan_task，通过 taskId 关联 |
| 权限 | internal admin only |

---

## 10. 验收标准

1. Partner 发起 verify/remediate/verify-fix/创建任务后，运营案件列表** 30 秒内**可查到 `case_id`
2. 工作台可看到：时间线、API 调用、Webhook、跃迁日志、业务载荷
3. 修复核验案件展示 VTC surveyId、进度、逐项 6/7/10，体验不低于 OPEN 编排工作台
4. 从 `api_invocation` 详情可一键跳转 `case_id` 工作台
