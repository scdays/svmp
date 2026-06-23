# Open API ↔ vul-pass ↔ vuln-task-center 落地方案

> **状态**：Wave 0 已冻结（Schema + 契约）  
> **日期**：2026-06-16  
> **功能编号**：`OPEN-VTC-W0` ~ `OPEN-VTC-W4`  
> **读者**：open-api-service / vul-pass / vuln-task-center 后端、联调、产品  
> **关联文档**：
> - [网络安全漏洞管理平台 · API 接口文档](../external/网络安全漏洞管理平台%20·%20API%20接口文档.md)
> - [漏洞实例与生命周期双轨存储-落地方案](./漏洞实例与生命周期双轨存储-落地方案.md)
> - [vuln-model扫描任务重构迁移至vul-pass-落地方案](./vuln-model扫描任务重构迁移至vul-pass-落地方案.md)
> - [vuln-task-center-扫描治理中心-PRD](./vuln-task-center-扫描治理中心-PRD.md)
> - [Open API与vul-pass内部接口映射表](./Open%20API与vul-pass内部接口映射表.md)（**P0 任务域将修订**）

---

## 一、Wave 0 交付清单（本次）

| 项 | 路径 | 状态 |
|----|------|------|
| `vul_scan_task` 编排字段 | `vul-pass/.../db/mysql/vul_scan_task.groovy` | ✅ |
| `vul_scan_task_sub` task-center 关联 | `vul-pass/.../vul_scan_task_sub.groovy` | ✅ |
| `vul_archive_inst` data_origin | `vul-pass/.../vul_archive_inst.groovy` | ✅ |
| `vul_inst_log_rela_oper` 运营轨 | `vul-pass/.../vul_inst_log_rela_oper.groovy` | ✅ |
| 业务枚举 | `vul-pass/.../enums/BizLineEnum` 等 | ✅ |
| `open_task` pass 关联 | `open-api-service/.../open_task.groovy` | ✅ |
| Internal API 契约 | 本文 §五 | ✅ |

**Wave 0 不含**：编排代码、Feign 实现、Kafka 监听、双扫下发逻辑（属 Wave 1）。

---

## 二、目标架构

```text
Partner
  → partner-gateway
  → open-api-service          （Partner 契约 /api/open/v1）
       │ Feign internal
       ▼
  vul-pass                    （VulScanTaskUi 编排内核）
       │ biz_line 分流
       ├── OPEN    → SOC_DUAL → Nessus + 绿盟 并集
       ├── METRIC  → 指标模板（vuln-model 迁移）
       └── ASSESS  → 部侧 dispatch（补齐 task-center）
       │
       ▼
  vuln-task-center            （扫描执行 + 状态/结果/报告）
       │
       ▼
  Nessus / 绿盟 RSAS / …
```

### 2.1 与旧实现的切割

| 旧路径（废弃） | 新路径 |
|----------------|--------|
| `open-api` → `POST /vul-scan-task/dispatch` + 假 `orderId` | `open-api` → `POST /internal/open/v1/tasks` |
| engHash 轮询单 sub | `scan_policy=SOC_DUAL` 固定 2 sub |
| 写 `vul_inst_log_rela`（混轨） | OPEN/METRIC 写 `vul_inst_log_rela_oper` |
| open-api Mock 引擎完成 | vul-pass 回调 `POST /internal/open/v1/tasks/{passTaskId}/notify` |

---

## 三、数据模型（Wave 0 Schema）

### 3.1 `vul_scan_task` 新增字段

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `biz_line` | VARCHAR(16) | ASSESS | OPEN / METRIC / ASSESS / PROD |
| `data_origin` | VARCHAR(16) | ASSESS | 与 inst 对齐 |
| `external_task_id` | VARCHAR(128) | — | open-api `taskId` 或 metric 外部键 |
| `scan_policy` | VARCHAR(32) | SINGLE | SOC_DUAL / SINGLE / CUSTOM |
| `tsk_scn` | VARCHAR(32) | — | 场景码 |
| `partner_id` | VARCHAR(64) | — | OPEN 专属 |
| `order_id` | — | — | **改为可空**（OPEN 无部侧指令） |

### 3.2 `vul_scan_task_sub` 新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `external_survey_id` | VARCHAR(64) | vuln-task-center `surveyId` |
| `scanner_vendor` | NESSUS / LM / … | 扫描器厂商 |
| `order_id` | — | **改为可空** |

### 3.3 `vul_archive_inst` 新增字段

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `data_origin` | VARCHAR(16) | ASSESS | 实例起源 |
| `reportable_flag` | TINYINT | 1 | 0永不报/1可遴选/2仅指令 |

### 3.4 `vul_inst_log_rela_oper`（新建）

运营轨，记录真实生命周期；部侧默认查询**不** JOIN 此表。

关键字段：`vul_info_id`、`vul_info_stat`、`transfer_time`、`tsk_id`、`order_id`（可空）、`log_ids`（可空）、`data_origin`、`ledger_status`（PENDING/FILLED/NA）、`synthesized=0`。

现网 `vul_inst_log_rela` 在 Wave 2 前仍作上报轨；Wave 1 起 OPEN 写入 oper 表。

### 3.5 `open_task` 新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `pass_task_id` | BIGINT | → `vul_scan_task.id` |
| `scan_policy` | VARCHAR(32) | 默认 SOC_DUAL |

`engine_task_id` 保留兼容；新链路以 `pass_task_id` 为准。

---

## 四、枚举约定

| 枚举 | 包路径 | 用途 |
|------|--------|------|
| `BizLineEnum` | `com.vtc.security.infra.utils.enums` | 编排入口分流 |
| `DataOriginEnum` | 同上 | inst / task / rela 起源 |
| `ScanPolicyEnum` | 同上 | SOC_DUAL 默认厂商列表 |
| `ScannerVendorEnum` | 同上 | sub.scanner_vendor |
| `LedgerStatusEnum` | 同上 | oper 轨台账状态 |

**SOC 双扫默认厂商**（`ScanPolicyEnum.SOC_DUAL`）：

```text
NESSUS + LM（绿盟）
```

---

## 五、Internal API 契约（vul-pass ↔ open-api）

> Base Path：`/internal/open/v1`（仅集群内 Feign，**不对 Partner 暴露**）  
> 鉴权：服务间 Token 或网关白名单（与现有 `/internal/admin/*` 同级）

### 5.1 `POST /internal/open/v1/tasks` — 创建 OPEN 编排任务

**调用方**：open-api-service（替代 `SvmpEngineAdapterImpl` → dispatch）

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| partnerId | string | ✓ | Partner ID |
| platformTaskId | string | ✓ | open-api 对外 `taskId` |
| extTaskId | string | ✓ | Partner 幂等键 |
| taskName | string | ✓ | 任务名称 |
| vulnType | int | ✓ | 1系统 / 2Web / 3弱口令（附录 F） |
| targets | object | ✓ | `hosts` + 可选 `auth[]` |
| scanTemplateId | int | ○ | 平台模板 |
| reportTemplateId | int | ○ | 报告模板 |
| scanPolicy | string | ○ | 默认 `SOC_DUAL` |
| srcMethod | int | ○ | 处置方式 |
| callbackUrl | string | ○ | Webhook 覆盖 |

**响应 data**：

| 字段 | 类型 | 说明 |
|------|------|------|
| passTaskId | long | `vul_scan_task.id` |
| status | string | ACCEPTED / REJECTED |
| subTasks | array | `{ subTaskId, scannerVendor, externalSurveyId }` |
| message | string | REJECTED 原因 |

**行为（Wave 1 实现）**：

1. 写 `vul_scan_task`（`biz_line=OPEN`, `data_origin=OPEN`, `scan_policy`）
2. 按策略向 vuln-task-center 创建 survey（SOC_DUAL = 2 次）
3. 写 `vul_scan_task_sub` × N

---

### 5.2 `GET /internal/open/v1/tasks/{passTaskId}` — 查询编排进度

**响应 data**：

| 字段 | 类型 | 说明 |
|------|------|------|
| passTaskId | long | — |
| status | string | PENDING / RUNNING / FINISHED / FAILED / PARTIAL_FAILED |
| progress | int | 0–100（子任务聚合） |
| subTasks | array | 各 vendor 进度 |
| finishedAt | datetime | 全部完成时间 |

**进度聚合规则**：

- `SOC_DUAL`：两子任务均 FINISHED → 父 FINISHED
- 一成功一失败 → `PARTIAL_FAILED`（可配置是否仍并集入库，默认：成功侧结果仍入库）

---

### 5.3 `POST /internal/open/v1/tasks/{passTaskId}/notify` — 编排完成通知

**调用方**：vul-pass（任务回收 + 生命周期结束后）

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| status | string | ✓ | FINISHED / FAILED / PARTIAL_FAILED |
| platformTaskId | string | ✓ | open-api taskId |
| summary | object | ○ | totalInstances / verifiedValid / falsePositive |
| errorMessage | string | ○ | 失败原因 |

**行为（Wave 1c）**：open-api 更新 `open_task` → 触发 Webhook `TASK_COMPLETED` / `TASK_FAILED` → 排队外发组装（P2）。

---

### 5.4 `GET /internal/open/v1/tasks/{passTaskId}/instances` — 实例快照（可选）

供 open-api ingest `open_vuln_instance`；Wave 1a 可与 Feign `vul-scan-task-sub-system/page` 合并。

---

## 六、vuln-task-center 对接契约（Wave 1a 冻结）

> 复用 vuln-model `ITaskClient` 路径，Wave 1 增加聚合 API。

| 步骤 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 创建上半场 | POST | `/v1/scan/task/batch/add/first/half` | 建 plan |
| 创建下半场 | POST | `/v1/scan/task/add/second/half` | 下发扫描 |
| 查状态 | GET | `/event/scan/task/survey/query/vulnScan/{surveyId}` | 轮询 |
| 拉结果 | GET | `/v1/scan/task/survey/{surveyId}/results` | **Wave 1a 新增** |
| 生成报告 | POST | `/v1/scan/task/survey/{surveyId}/report/generate` | **Wave 1a 新增** |
| 状态事件 | Kafka | topic 沿用现网 | pass 消费 |

**双扫调用**：编排层对同一 `targets` 调用 2 次下半场，`scanner_vendor` 分别为 NESSUS、LM。

---

## 七、SOC 双扫并集规则

```text
sub(Nessus) ──pull──► rawN ──┐
                              ├── mergeUnion(dedupKey) ──► handlerReport
sub(绿盟)   ──pull──► rawLM ──┘

dedupKey = assetId + vulPort + vulTransProto + vulSvc + vulId
冲突：vulLevel 取高；描述取非空；engHash 记 MULTI 或保留 sources[]
```

---

## 八、三发起方统一矩阵

| 维度 | OPEN | METRIC | ASSESS |
|------|------|--------|--------|
| 入口 | internal open API | `/ui/pass/v3/metric/*` | `dispatch` |
| scan_policy | SOC_DUAL（默认） | SINGLE | 工单 engHashes |
| task-center | ✓ | ✓（迁移后） | ✓（本次补齐） |
| rela | oper | oper | report (+oper 可选) |
| orderId | 无 | 无 | 必填 |

---

## 九、分期 Wave 对照

| Wave | 范围 | 工程 |
|------|------|------|
| **0** | Schema + 枚举 + 本文契约 | vul-pass, open-api |
| **1a** | task-center 双扫/结果/报告 API | vuln-task-center |
| **1b** | OpenTaskOrchestrator + 监听 + 并集 | vul-pass |
| **1c** | Adapter 改路 + notify + Webhook | open-api-service |
| **2** | handlerVulProcess 分流 oper/report | vul-pass |
| **3** | §5.2–5.5 实例 API | open-api |
| **4** | §5.6–5.7 外发/产物 | open-api + pass |

---

## 十、迁移与兼容

1. **历史任务**：`biz_line` / `data_origin` 默认 `ASSESS`，行为不变。
2. **order_id 可空**：仅 OPEN/METRIC 创建时为空；`dispatch` 仍校验非空。
3. **oper 表**：Wave 1 前 OPEN 可暂写现 `vul_inst_log_rela`；Wave 2 切换 appendOperRela。
4. **open-api adapter-mode=mock**：联调可继续 Mock，与 Wave 1c 并行。

---

## 十一、变更日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 0.1 | 2026-06-16 | Wave 0：Schema、枚举、Internal API 契约 |
