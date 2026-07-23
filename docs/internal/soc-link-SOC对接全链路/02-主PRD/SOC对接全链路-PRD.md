# SOC 对接全链路 PRD · vul-pass × vuln-task-center × open-api-service

> **状态**：草稿 v1.0（评审 + 一键落地用）
> **日期**：2026-06-17
> **功能编号**：`SOC-LINK-W0` ~ `SOC-LINK-W4`
> **读者**：vul-pass / vuln-task-center / open-api-service / asset-newleak-manage 后端、前端、产品、联调
> **交付目标**：本文档 + 任务拆分矩阵 + 执行 Prompt 三件套，支撑 Multi-Agent 并行开发

## 关联文档

| 文档 | 路径 |
|------|------|
| API 接口文档（对外契约） | `svmp/docs/external/网络安全漏洞管理平台 · API 接口文档.md` |
| 双轨存储落地方案 | `svmp/docs/internal/漏洞实例与生命周期双轨存储-落地方案.md` |
| vuln-task-center PRD | `svmp/docs/internal/vuln-task-center-扫描治理中心-PRD.md` |
| vuln-model 迁移方案 | `svmp/docs/internal/vuln-model扫描任务重构迁移至vul-pass-落地方案.md` |
| open-api-vtc-pass 落地方案（Wave 0） | `svmp/docs/internal/open-api-vtc-pass-落地方案.md` |
| 前端原型（vul-pass 任务编排） | `svmp/docs/internal/prototypes/open-api-vtc-pass-prototype-v1.html` |
| 前端原型（task-center 治理） | `svmp/docs/internal/prototypes/vuln-task-center-governance-prototype-v3.html` |

---

## 一、背景与目标

### 1.1 三发起方统一问题

当前平台存在三个任务/漏洞实例的发起方，链路割裂：

| 发起方 | 现状 | 目标 |
|--------|------|------|
| **OPEN**（外部 Partner / SOC 接入） | open-api-service Mock 引擎或假 `orderId` 调 dispatch | 经 vul-pass 编排 → vuln-task-center 双扫 → 并集入库 |
| **METRIC**（vuln-model 指标排查） | model 自带扫描 + Excel 导出 → pass 导入 | 重构到 vul-pass，`data_origin=METRIC`，写 oper 轨 |
| **ASSESS**（部侧考核） | vul-pass `dispatch` 考核链，**未对接 vuln-task-center** | 补齐 task-center 下发，保持上报轨不变 |

**核心矛盾**：vul-pass 考核线（ASSESS）成熟且严谨，但未与 vuln-task-center 真正对接；OPEN 和 METRIC 链路需要复用 ASSESS 的生命周期能力，但走独立编排入口。

### 1.2 SOC 双扫特殊要求

> **SOC 接入方要求**：每一次创建任务，都要分别把扫描目标下发到 **Nessus** 和 **绿盟扫描器**，两份任务结果取**并集**记录并反馈。

当前 vuln-task-center 已支持 Nessus 和绿盟下发，但 vul-pass 层缺乏「同目标多扫描器并集」编排能力。

### 1.3 目标架构

```text
Partner (SOC)                        部侧考核 UI              vuln-model 指标
    │ POST /api/open/v1/tasks/vul        │ dispatch                │ (Wave 4 同步)
    ▼                                    ▼                         ▼
open-api-service ──Feign──?  vul-pass（VulScanTaskUi 编排内核）
                               │ biz_line 分流
                               ├── OPEN    → scan_policy=SOC_DUAL → Nessus + 绿盟 并集 → oper 轨
                               ├── METRIC  → scan_policy=SINGLE   → 单扫描器          → oper 轨
                               └── ASSESS  → scan_policy=SINGLE   → 单/多扫描器      → report 轨 (+oper 可选)
                               │
                               ▼
                         vuln-task-center（扫描治理中心）
                               ├── ScannerAdapter-LM（绿盟）
                               ├── ScannerAdapter-AH（安恒）
                               ├── Nessus 适配（现有）
                               ├── survey → sub_task 执行
                               ├── 对账 / 状态回调 / 结果拉取
                               └── 报告生成 / 原始报告回收
                               │
                               ▼
                         Nessus / 绿盟 RSAS / 安恒明鉴 / ...
```

### 1.4 设计原则

1. **不新增微服务**：能力沉淀 vul-pass，open-api-service 保持薄网关。
2. **复用 ASSESS 生命周期**：transition 跃迁规则只驱动 `vul_archive_inst`，不因双轨分裂。
3. **渐进迁移**：保留 Excel 导入过渡，不强求一步到位。
4. **SOC_DUAL 可配置**：双扫厂商列表由 `ScanPolicyEnum` 定义，可扩展。
5. **对账先行**：task-center 的 ScannerAdapter + 对账能力是上层稳定的基础。

---

## 二、用户故事

### 2.1 SOC 接入方（Partner）

| ID | 作为… | 我希望… | 以便… | Wave |
|----|-------|---------|-------|------|
| US-O01 | SOC 接入方 | 调用 `POST /tasks/vul` 创建排查任务，平台自动双扫 | 一次请求覆盖多扫描器 | W1 |
| US-O02 | SOC 接入方 | 通过 Webhook 收到 `TASK_COMPLETED` 后拉取漏洞实例并集 | 获取去重后的完整漏洞清单 | W1 |
| US-O03 | SOC 接入方 | 对漏洞实例发起验证/处置/修复核验 | 走完漏洞全生命周期 | W3 |
| US-O04 | SOC 接入方 | 下载规范化 Export（XML/JSON）和原始报告 Artifact | 交付审计 | W4 |
| US-O05 | SOC 接入方 | 查询任务进度时看到双扫各子任务状态 | 知道哪侧还在跑 | W1 |
| US-O06 | SOC 接入方 | 对已修复实例发起修复核验，平台按最近扫描器全量复扫并判定 6/7 | 闭环修复效果确认 | W3 |

### 2.2 平台运营

| ID | 作为… | 我希望… | 以便… | Wave |
|----|-------|---------|-------|------|
| US-P01 | 安全运营 | 在 vul-pass 任务工作台看到 OPEN 编排任务及其双扫子任务 | 监控 SOC 双扫进度 | W1 |
| US-P02 | 安全运营 | 在任务工作台查看并集后的漏洞、存活主机、端口信息 | 一站式排查 | W1 |
| US-P03 | 安全运营 | METRIC 排查任务也在 vul-pass 内完成（不再导出 Excel） | 减少手工环节 | W4 |
| US-P04 | 安全运营 | ASSESS 考核任务也走 task-center 下发 | 统一执行面 | W2 |

### 2.3 平台管理员

| ID | 作为… | 我希望… | 以便… | Wave |
|----|-------|---------|-------|------|
| US-A01 | 平台管理员 | 配置 Partner 的 `scanPolicy`（SOC_DUAL / SINGLE） | 按接入方差异化 | W0 |
| US-A02 | 平台管理员 | 在 task-center 治理页看到对账差异 | 发现绕行/遗留任务 | W2 |

---

## 三、功能范围

### 3.1 Wave 矩阵

| Wave | 范围 | 工程 | 依赖 |
|------|------|------|------|
| **W0** | Schema + 枚举 + Internal API 契约（已冻结） | vul-pass, open-api | — |
| **W1** | task-center 双扫/结果/报告 API + vul-pass OpenTaskOrchestrator + 并集 + open-api Adapter 改路 | vuln-task-center, vul-pass, open-api | W0 |
| **W2** | ASSESS 补齐 task-center 下发 + task-center ScannerAdapter-LM + 对账 | vul-pass, vuln-task-center | W1 |
| **W3** | 实例生命周期 API（verify/remediate/verify-fix）+ handlerVulProcess 分流 oper/report | open-api, vul-pass | W1 |
| **W4** | Export/Artifact 外发 + METRIC 迁移 | open-api, vul-pass | W3 |

### 3.2 不做边界

- **不重写** vul-pass `transition` 状态机核心逻辑
- **不替换** tools-scheduler / SOAR 引擎本身
- **不一次性** 迁移全部 9 家厂商扫描器
- **不做** 扫描器固件升级、VPN 组网等设备运维
- **W1~W3 不做** 常态化遴选/合成（属双轨方案 Wave 3，独立推进）

---

## 四、数据模型

### 4.1 vul-pass 新增/扩展

#### 4.1.1 `vul_scan_task` 新增字段（W0 已冻结）

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `biz_line` | VARCHAR(16) | ASSESS | OPEN / METRIC / ASSESS / PROD |
| `data_origin` | VARCHAR(16) | ASSESS | 与 inst 对齐 |
| `external_task_id` | VARCHAR(128) | — | open-api `taskId` 或 metric 外部键 |
| `scan_policy` | VARCHAR(32) | SINGLE | SOC_DUAL / SINGLE / CUSTOM |
| `tsk_scn` | VARCHAR(32) | — | 场景码 |
| `partner_id` | VARCHAR(64) | — | OPEN 专属 |
| `order_id` | — | — | **改为可空**（OPEN 无部侧指令） |

#### 4.1.2 `vul_scan_task_sub` 新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `external_survey_id` | VARCHAR(64) | vuln-task-center `surveyId` |
| `scanner_vendor` | VARCHAR(16) | NESSUS / LM / AH |
| `order_id` | — | **改为可空** |

#### 4.1.3 `vul_archive_inst` 新增字段

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `data_origin` | VARCHAR(16) | ASSESS | METRIC / OPEN / PROD / ASSESS / IMPORT |
| `reportable_flag` | TINYINT | 1 | 0永不报 / 1可遴选 / 2仅指令 |

#### 4.1.4 `vul_inst_log_rela_oper`（新建，运营轨）

| 字段 | 约束 | 说明 |
|------|------|------|
| `id` | PK | — |
| `vul_info_id` | NOT NULL | → inst.id |
| `vul_info_stat` | NOT NULL | 该次变更后状态 |
| `transfer_time` | NOT NULL | 识别时间戳 |
| `tsk_id` | NOT NULL | 产生变更的任务/子任务 |
| `order_id` | **可空** | 生产/开放可无部侧指令 |
| `log_ids` | **可空** | 台账可后补；`ledger_status=PENDING` |
| `data_origin` | NOT NULL | 与 inst 一致 |
| `ledger_status` | NOT NULL | PENDING / FILLED / NA |
| `synthesized` | TINYINT | 0=真实 / 1=合成 |
| `eng_hash`, `src_method`, `source` | — | 同现表 |

### 4.2 open-api-service 新增/扩展

#### 4.2.1 `open_task` 新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `pass_task_id` | BIGINT | → `vul_scan_task.id` |
| `scan_policy` | VARCHAR(32) | 默认 SOC_DUAL |

#### 4.2.2 新增 `open_export`（W4）

| 字段 | 说明 |
|------|------|
| `export_id` | 外发记录 ID |
| `task_id` | open-api taskId |
| `pass_task_id` | 关联 pass 任务 |
| `format` | xml / json |
| `export_stage` | TASK_COMPLETED / VERIFY_SCAN / VERIFY_FIX_SCAN |
| `data_type` | MIXED / SYSTEM_VULNERABILITY / ... |
| `status` | PENDING / READY / EXPIRED / FAILED |
| `record_count` | 记录条数 |
| `file_path` | 存储路径 |

#### 4.2.3 新增 `open_artifact`（W4）

| 字段 | 说明 |
|------|------|
| `artifact_id` | 产物 ID |
| `task_id` | open-api taskId |
| `export_id` | 关联外发 |
| `export_stage` | 阶段 |
| `artifact_source` | SCANNER_RAW / PLATFORM_REPORT |
| `report_type_code` | 平台报告类型码 |
| `sub_task_id` | 子任务 ID（多扫描器区分） |
| `file_name`, `file_format`, `content_type` | 文件元信息 |
| `byte_size`, `checksum` | 校验 |
| `status` | PENDING / READY / EXPIRED / FAILED |

### 4.3 vuln-task-center 新增

（沿用 vuln-task-center PRD §4.4：`scan_node` 扩展、`scanner_api_capability`、`reconcile_task_diff`、`scanner_template`）

---

## 五、vuln-task-center 对接改造（W1a）

### 5.1 新增 REST API

#### 5.1.1 `GET /v1/scan/task/survey/{surveyId}/results` — 拉取扫描结果

**用途**：vul-pass 在子任务完成后主动拉取存活探测、端口列表、系统漏洞等数据。

**响应 data**：

| 字段 | 类型 | 说明 |
|------|------|------|
| surveyId | string | survey ID |
| status | string | FINISHED / FAILED |
| targets | array | 扫描目标列表 |
| liveProbeResults | array | 存活探测结果 |
| portScanResults | array | 端口扫描结果 |
| vulnerabilities | array | 漏洞列表（按 vulID 聚合） |
| weakPasswords | array | 弱口令（type=3） |
| baselineResults | array | 基线结果 |

#### 5.1.2 `POST /v1/scan/task/survey/{surveyId}/report/generate` — 生成原始报告

**用途**：vul-pass 主动发起报告生成请求，异步等待完成。

**请求体**：

| 字段 | 必填 | 说明 |
|------|:----:|------|
| reportTemplateCode | ○ | 报告模板码（沿用 task-center PRD US-P02） |
| format | ○ | xml / pdf / xlsx |

**响应 data**：

| 字段 | 说明 |
|------|------|
| reportJobId | 报告任务 ID |
| status | queued / generating |

#### 5.1.3 `GET /v1/scan/report/jobs/{reportJobId}` — 查询报告状态

| 字段 | 说明 |
|------|------|
| reportJobId | — |
| status | pending / queued / generating / ready / failed |
| progress | 0–100 |
| downloadUrl | ready 时返回 |

#### 5.1.4 `GET /v1/scan/report/jobs/{reportJobId}/download` — 下载原始报告

返回二进制文件流。

### 5.2 状态回调契约（Kafka）

vuln-task-center 在子任务状态变更时发送 Kafka 消息，vul-pass 消费：

```json
{
  "event": "SUB_TASK_STATUS_CHANGED",
  "surveyId": "SV-LM-002",
  "subTaskId": "ST-001",
  "vendor": "LM",
  "status": "FINISHED",
  "progress": 100,
  "finishedAt": "2026-06-17T10:00:00Z",
  "passTaskId": 10086001,
  "passSubTaskId": 200001
}
```

报告生成完成回调：

```json
{
  "event": "REPORT_JOB_COMPLETED",
  "reportJobId": "RJ-001",
  "surveyId": "SV-LM-002",
  "status": "ready",
  "downloadUrl": "/v1/scan/report/jobs/RJ-001/download",
  "passTaskId": 10086001
}
```

### 5.3 现有接口复用

| 步骤 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 创建上半场 | POST | `/v1/scan/task/batch/add/first/half` | 建 plan |
| 创建下半场 | POST | `/v1/scan/task/add/second/half` | 下发扫描 |
| 查状态 | GET | `/event/scan/task/survey/query/vulnScan/{surveyId}` | 轮询 |

---

## 六、vul-pass 编排改造（W1b）

### 6.1 OpenTaskOrchestrator（新增）

**职责**：处理 `biz_line=OPEN` 的任务编排，替代直接调 `dispatch`。

**核心流程**：

```text
POST /internal/open/v1/tasks
  → 写 vul_scan_task (biz_line=OPEN, scan_policy=SOC_DUAL)
  → 按 scan_policy 拆分子任务
     ├── SOC_DUAL: 2 个 sub (NESSUS + LM)
     └── SINGLE: 1 个 sub
  → 逐个调 task-center first/half + second/half
  → 写 vul_scan_task_sub (external_survey_id, scanner_vendor)
  → 返回 passTaskId + subTasks[]
```

### 6.2 SOC 双扫并集规则

```text
sub(Nessus) ──pull results──? rawN ──┐
                                      ├── mergeUnion(dedupKey) ──? handlerReport
sub(绿盟)   ──pull results──? rawLM ──┘

dedupKey = assetId + vulPort + vulTransProto + vulSvc + vulId
冲突解决：
  - vulLevel: 取高
  - vulName / vulDesc: 取非空
  - engHash: 记 MULTI 或保留 sources[]
  - transferTime: 取最早
```

**并集触发条件**：SOC_DUAL 下所有 sub 均 FINISHED（或一成功一失败，默认成功侧仍入库）。

### 6.3 结果回收与生命周期

复用 ASSESS 成熟链路，但按 `biz_line` 分流：

```text
task-center 回调 FINISHED
  → vul-pass 拉取 results（双扫分别拉取）
  → mergeUnion（仅 SOC_DUAL）
  → handlerReport（标准化）
  → handlerVulProcess（生命周期）
     ├── ASSESS: inst + rela_report + 台账 + 回传 order
     ├── OPEN:   inst + rela_oper only（data_origin=OPEN）
     └── METRIC: inst + rela_oper only（data_origin=METRIC）
  → 触发报告生成（调 task-center report/generate）
  → 异步等待报告完成回调
  → 提取原始报告存储
  → 通知 open-api (POST /internal/open/v1/tasks/{passTaskId}/notify)
```

### 6.4 handlerVulProcess 分流改造（W2）

**现状**：`handlerVulProcess` 内 `writeVulInstLedger` 统一写 `vul_inst_log_rela`。

**改造**：拆分为 `appendOperRela` / `appendReportRela`，按 `biz_line` 分流：

| biz_line | oper 轨 | report 轨 | 台账 | 回传 order |
|----------|---------|-----------|------|-----------|
| ASSESS | 可选（建议写） | **写**（synthesized=0） | 同步 | 是 |
| OPEN | **写** | 不写 | 跳过 | 否 |
| METRIC | **写** | 不写 | 跳过 | 否 |

### 6.5 新增 Internal API

#### `POST /internal/open/v1/tasks` — 创建 OPEN 编排任务

**调用方**：open-api-service

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| partnerId | string | ? | Partner ID |
| platformTaskId | string | ? | open-api 对外 taskId |
| extTaskId | string | ? | Partner 幂等键 |
| taskName | string | ? | 任务名称 |
| vulnType | int | ? | 1系统 / 2Web / 3弱口令 |
| targets | object | ? | `hosts` + 可选 `auth[]` |
| scanTemplateId | int | ○ | 平台模板 |
| reportTemplateId | int | ○ | 报告模板 |
| scanPolicy | string | ○ | 默认 SOC_DUAL |
| srcMethod | int | ○ | 处置方式 |
| callbackUrl | string | ○ | Webhook 覆盖 |

**响应 data**：

| 字段 | 类型 | 说明 |
|------|------|------|
| passTaskId | long | `vul_scan_task.id` |
| status | string | ACCEPTED / REJECTED |
| subTasks | array | `{ subTaskId, scannerVendor, externalSurveyId }` |

#### `GET /internal/open/v1/tasks/{passTaskId}` — 查询编排进度

**响应 data**：

| 字段 | 类型 | 说明 |
|------|------|------|
| passTaskId | long | — |
| status | string | PENDING / RUNNING / FINISHED / FAILED / PARTIAL_FAILED |
| progress | int | 0–100（子任务聚合） |
| subTasks | array | 各 vendor 进度 |
| finishedAt | datetime | 全部完成时间 |

#### `POST /internal/open/v1/tasks/{passTaskId}/notify` — 编排完成通知

**调用方**：vul-pass（任务回收 + 生命周期结束后）

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| status | string | ? | FINISHED / FAILED / PARTIAL_FAILED |
| platformTaskId | string | ? | open-api taskId |
| summary | object | ○ | totalInstances / verifiedValid / falsePositive |
| errorMessage | string | ○ | 失败原因 |

---

## 七、open-api-service 改造（W1c）

### 7.1 Adapter 改路

**现状**：`SvmpEngineAdapterImpl` → `POST /vul-scan-task/dispatch` + 假 `orderId`。

**改造**：调用 vul-pass `POST /internal/open/v1/tasks`，记录 `pass_task_id`。

### 7.2 进度查询聚合

`GET /tasks/{taskId}` 增强为调用 vul-pass `GET /internal/open/v1/tasks/{passTaskId}`，聚合双扫进度。

### 7.3 Webhook 触发

收到 vul-pass `notify` 后：
1. 更新 `open_task` 状态
2. 触发 Webhook `TASK_COMPLETED` / `TASK_FAILED`
3. 排队外发组装（W4）

---

## 八、实例生命周期 API（W3）

### 8.1 漏洞实例状态机

```text
排查（创建任务）→ vulInfoStat = 1（初始发现）
验证（verify）
    → VALID → 2（已验证有效）
    → FALSE_POSITIVE → 3（已验证误报，终态）
处置（remediate）
    → 已修复 → 5
    → 修复失败/备案 → 9
修复核验（verify-fix）
    → 平台异步复扫 → 6（核验已修复）/ 7（核验未修复）/ 10（核验失败）
```

**前置状态约束**：

| 动作 | 前置 vulInfoStat | 终态 |
|------|------------------|------|
| verify | 0, 1 | 2 或 3 |
| remediate | 2, 7 | 5 或 9 |
| verify-fix | 5 | 6, 7, 10 |

### 8.2 open-api 实例写接口

open-api 接收 Partner 请求 → Feign 调 vul-pass internal API → vul-pass Domain 层执行 transition + appendOperRela/appendReportRela。

| 对外接口 | vul-pass internal |
|----------|-------------------|
| `POST /instances/{vulInfoID}/verify` | `POST /internal/open/v1/instances/{vulInfoID}/verify` |
| `POST /instances/remediate:batch` | `POST /internal/open/v1/instances/remediate:batch` |
| `POST /instances/{vulInfoID}/verify-fix` | `POST /internal/open/v1/instances/{vulInfoID}/verify-fix` |

**verify-fix 复扫扫描器选择**：默认使用该实例最近一次排查/扫描所用扫描器（记录在 `vul_scan_task_sub.scanner_vendor`）。

### 8.3 幂等

- 创建任务：`extTaskId`（必填）+ `Idempotency-Key`（可选）
- 实例写：`Idempotency-Key: {动作}:{vulInfoID}:{clientRequestId}`，24h 缓存


### 8.4 修复核验（verify-fix）编排链路

> 对应开放平台 API **§5.5 漏洞实例 · 修复核验**。由 **Partner 主动发起**；平台异步复扫后判定终态并外发。

#### 8.4.1 业务语义

| 项 | 说明 |
|----|------|
| 触发方 | Partner 调用 `POST /instances/{vulInfoID}/verify-fix` 或批量接口 |
| 前置状态 | `vulInfoStat = 5`（已修复） |
| 受理响应 | 同步返回 `verifyFixStatus=PENDING/RUNNING`、`verifyFixJobId`；**受理期间状态保持 5** |
| 终态 | 6 核验修复 / 7 核验未修复 / 10 核验失败 |
| 与 verify 区分 | verify 确认漏洞真假（前置 0/1）；verify-fix 确认**修复是否生效**（前置 5） |

#### 8.4.2 端到端时序

```text
Partner
  | POST /api/open/v1/instances/{vulInfoID}/verify-fix  (Idempotency-Key)
  v
open-api-service
  | 能力码 INSTANCE_VERIFY_FIX + 幂等 24h
  | Feign -> vul-pass internal verify-fix
  v
vul-pass OpenInstanceAppService
  1. 校验 vulInfoStat=5
  2. 按 vulInfoID 加载 vul_archive_inst（系统漏洞实例档案）
  3. 从实例/系统漏洞库提取影响资产 IP（assetIp）、端口、协议 -> 扫描 targets[]
  4. 查询该实例最近一次扫描 sub：vul_scan_task_sub ORDER BY finish_time DESC
     -> 读取 scanner_vendor（NESSUS / LM / AH ...）
  5. 创建修复核验扫描任务（biz_line=OPEN, tsk_scn=VERIFY_FIX, scan_policy=SINGLE）
  6. 调用 vuln-task-center 下发 **单厂商全量扫描**（不复用 SOC_DUAL 双扫）
  7. 写 verify_fix_job 关联（verifyFixJobId 关联 passTaskId/subId 与 vulInfoID）
  8. 同步返回受理结果给 open-api -> Partner
  v
vuln-task-center
  | 全量主机/系统漏洞扫描（**不支持指定产品漏洞 ID 下发**）
  v
扫描完成 -> Kafka dr_vul_scan_task_status
  v
vul-pass VerifyFixRecycleHandler
  1. handlerReport 解析全量结果
  2. **仅关注** verify-fix 请求中的目标 vulInfoID（及对应 vulId/dedupKey）
  3. 判定：
     - 结果中**未再检出**该漏洞 -> transition -> vulInfoStat=6（核验修复）
     - **仍检出** -> vulInfoStat=7（核验未修复）
     - 引擎失败/超时 -> vulInfoStat=10（核验失败）
  4. appendOperRela + writeVulInstLedger
  5. notify open-api
  v
open-api
  | EXPORT_READY（exportStage=VERIFY_FIX_SCAN）
  | Webhook INSTANCE_VERIFY_FIX_COMPLETED
  v
Partner 轮询外发或接收 Webhook
```

#### 8.4.3 扫描下发约束

| 约束 | 说明 |
|------|------|
| 扫描器选择 | 默认使用该漏洞实例**最近一次排查/扫描**使用的扫描器（`vul_scan_task_sub.scanner_vendor`） |
| 扫描范围 | 对实例影响资产 IP 做**全量扫描**；task-center **不支持**按产品漏洞 ID 定点下发 |
| 结果过滤 | 回收结果为全量；状态判定**仅匹配**本次 verify-fix 的 `vulInfoID`（及 vulId） |
| SOC_DUAL | 修复核验为**单 survey 复扫**，不触发双扫并集合并 |
| procMethod | 建议 `1060`（修复核验自适应扫描）；阶段 `PHASE_VERIFICATION` / `scan_phase=3` |

#### 8.4.4 数据落库

| 表/字段 | 用途 |
|---------|------|
| `vul_scan_task.tsk_scn` | `VERIFY_FIX` 区分排查/验证/修复核验任务 |
| `vul_scan_task.scan_policy` | 固定 `SINGLE` |
| `vul_scan_task_sub.scanner_vendor` | 复扫厂商 |
| `vul_scan_task_sub.scan_phase` | `3` = 修复核验阶段 |
| `open_verify_fix_job`（建议新增） | verifyFixJobId、partnerId、vulInfoID、passTaskId、status |
| `vul_inst_log_rela_oper` | 核验动作写运营轨 |

#### 8.4.5 外发与回调

| 事件 | 时机 | exportStage |
|------|------|-------------|
| `INSTANCE_VERIFY_FIX_COMPLETED` | 复扫完成且状态已更新 | - |
| `EXPORT_READY` | 外发组装完成 | `VERIFY_FIX_SCAN` |

外发须含 `targets[]`、`liveProbeResults[]`、`portScanResults[]`、`vulnerabilities[]`（§5.6.3）。

#### 8.4.6 验收要点（W3）

- [ ] Partner 对 stat=5 实例发起 verify-fix，同步收到 `verifyFixStatus=RUNNING`
- [ ] vul-pass 从系统漏洞库正确解析影响资产 IP
- [ ] 复扫使用最近一次 `scanner_vendor`，且为单 survey 全量扫描
- [ ] 全量结果回收后，仅目标 vulInfoID 参与 6/7/10 判定
- [ ] 完成后收到 `INSTANCE_VERIFY_FIX_COMPLETED` + `EXPORT_READY(VERIFY_FIX_SCAN)`

---

## 九、扫描结果外发与报告产物（W4）

### 9.1 Export（规范化 TaskExport）

**触发时机**：任务结束、验证扫描完成、修复核验扫描完成。

**输出结构**：

```text
TaskExport
├── export（元数据）
├── task（任务信息）
├── summary（汇总统计）
├── targets[]（扫描目标）
├── liveProbeResults[]（存活探测）
├── portScanResults[]（端口扫描）
├── vulnerabilities[]（按 vulID 聚合）
│   └── instances[]（系统漏洞实例明细）
├── weakPasswords[]
├── baselineResults[]
└── appendices[]
```

**SOC_DUAL 聚合**：双扫结果合并后统一输出，`vulnerabilities[].instances[].evidence` 可保留多源证据。

### 9.2 Artifact（报告产物）

| artifactSource | 说明 | 典型格式 |
|----------------|------|----------|
| SCANNER_RAW | 扫描器原始报告 | xml, xlsx, zip |
| PLATFORM_REPORT | 平台渲染报告 | xlsx, pdf, html |

**SOC_DUAL 多产物**：每个子任务各一份原始报告，可按策略合并为 ZIP。

### 9.3 Webhook 事件

| eventType | 触发 |
|-----------|------|
| TASK_COMPLETED | 任务正常结束 |
| TASK_FAILED | 任务失败 |
| INSTANCE_VERIFY_FIX_COMPLETED | 修复核验完成 |
| EXPORT_READY | 规范化外发可下载 |
| ARTIFACT_READY | 报告产物可下载 |

---

## 十、前端改造（asset-newleak-manage）

### 10.1 新增页面

| 页面 | 说明 | Wave |
|------|------|------|
| OPEN 编排任务列表 | 展示 `biz_line=OPEN` 任务 | W1 |
| 任务实例工作台 | Tab：概览/子任务(双扫)/结果并集/漏洞生命周期/报告产物/回调 | W1 |
| 漏洞实例详情 | 验证/处置/核验操作入口 | W3 |
| 外发记录列表 | Export 下载 | W4 |
| 报告产物列表 | Artifact 下载 | W4 |

### 10.2 任务实例工作台 Tab 设计

参考 `open-api-vtc-pass-prototype-v1.html`：

1. **概览**：时间线展示任务全流程
2. **子任务（双扫）**：左右对比 Nessus / 绿盟进度与漏洞数
3. **结果并集**：可视化并集过程，展示 dedupKey 与冲突解决
4. **漏洞生命周期**：实例列表 + 状态跃迁历史
5. **报告产物**：原始报告 + 平台报告下载
6. **Partner 回调**：Webhook 投递日志

---

## 十一、分期交付详述

### 11.1 W1（约 4 周）— 双扫编排核心

**范围**：
- vuln-task-center: 新增 results/report API + Kafka 回调
- vul-pass: OpenTaskOrchestrator + SOC_DUAL 并集 + Internal API
- open-api: Adapter 改路 + notify 接收 + Webhook TASK_COMPLETED

**验收**：
- [ ] SOC Partner 创建任务 → 双扫下发 → 并集入库 → Webhook 回调
- [ ] vul-pass 任务工作台可见双扫子任务进度
- [ ] 一侧失败另一侧成功，成功侧结果仍入库
- [ ] vuln-task-center results API 返回存活/端口/漏洞完整数据
- [ ] 报告生成请求可发起，完成后可下载

### 11.2 W2（约 3 周）— ASSESS 补齐 + task-center 治理

**范围**：
- vul-pass: ASSESS `dispatch` 链路补齐 task-center 下发
- vuln-task-center: ScannerAdapter-LM + 对账（LM active_list）
- handlerVulProcess 分流改造（oper/report）

**验收**：
- [ ] 考核任务经 task-center 下发，sub_task 落库
- [ ] 绿盟节点对账返回 MATCHED/ORPHAN/MISSING/DRIFT
- [ ] OPEN 写 oper 轨，ASSESS 写 report 轨
- [ ] 部侧查询 JOIN rela_report 不受影响

### 11.3 W3（约 3 周）— 实例生命周期

**范围**：
- vul-pass: internal verify/remediate/verify-fix API + transition
- open-api: 对外 §5.3-5.5 接口 + 幂等
- 前端: 漏洞实例详情 + 操作表单

**验收**：
- [ ] Partner 验证 → 状态 2/3
- [ ] Partner 处置 → 状态 5/9
- [ ] Partner 修复核验 → 异步复扫 → 6/7/10
- [ ] verify-fix 使用最近一次扫描器
- [ ] 幂等键生效
- [ ] verify-fix：从 vul_archive_inst 解析资产 IP，按最近 scanner_vendor 单 survey 全量下发
- [ ] verify-fix：回收全量结果后仅匹配目标 vulInfoID -> 6/7/10
- [ ] verify-fix：EXPORT_READY exportStage=VERIFY_FIX_SCAN + INSTANCE_VERIFY_FIX_COMPLETED

### 11.4 W4（约 3 周）— 外发 + METRIC 迁移

**范围**：
- open-api: Export/Artifact 接口 + Webhook EXPORT_READY/ARTIFACT_READY
- vul-pass: Export 组装 + 原始报告存储
- METRIC: vuln-model 迁移（Big Bang）

**验收**：
- [ ] 任务完成后可下载 XML/JSON Export
- [ ] 可下载扫描器原始报告
- [ ] METRIC 任务在 vul-pass 内完成，写 oper 轨
- [ ] 历史漏洞全量迁移至 inst + rela_oper

---

## 十二、风险与对策

| 风险 | 对策 |
|------|------|
| ASSESS 考核链路改造影响部侧上报 | W2 仅补齐 task-center 下发，report 轨逻辑不变；充分回归 |
| SOC 双扫并集去重规则不准 | dedupKey 配置化；联调阶段对比人工核验 |
| vuln-task-center 报告生成不稳定 | 异步重试 + 超时降级；W1 先支持 LM |
| handlerVulProcess 分流改造遗漏分支 | Code Review 清单 + 单元测试覆盖 biz_line 全分支 |
| open-api Mock 与真实链路切换 | W1c adapter-mode 可配置，支持并行联调 |
| METRIC Big Bang 迁移数据不一致 | 2 轮 dry-run + 指标对账（附录 D） |
| verify-fix 复扫扫描器选择错误 | 记录 `scanner_vendor` 于 sub 表，复扫时查询 |
| verify-fix 全量复扫误伤/耗时 | 单 IP 全量模板 + 结果仅过滤目标 vulInfoID 做状态判定 |

---

## 十三、附录

### 附录 A：漏洞实例状态码 vulInfoStat

| 码 | 含义 | 阶段 |
|----|------|------|
| 0 | 潜伏预警 | — |
| 1 | 初始发现 | 排查 |
| 2 | 已验证有效 | 验证 |
| 3 | 已验证误报（终态） | 验证 |
| 5 | 已修复 | 处置 |
| 6 | 核验已修复 | 核验 |
| 7 | 核验未修复 | 核验 |
| 9 | 修复失败/备案 | 处置 |
| 10 | 核验失败 | 核验 |

### 附录 B：任务类型 type

| 码 | 说明 |
|----|------|
| 1 | 漏洞扫描 |
| 2 | WEB 应用扫描 |
| 3 | 口令猜测 |

### 附录 C：业务枚举

| 枚举 | 值 | 用途 |
|------|----|------|
| BizLineEnum | OPEN / METRIC / ASSESS / PROD | 编排入口分流 |
| DataOriginEnum | METRIC / OPEN / PROD / ASSESS / IMPORT | inst/task/rela 起源 |
| ScanPolicyEnum | SOC_DUAL / SINGLE / CUSTOM | 扫描策略 |
| ScannerVendorEnum | NESSUS / LM / AH / QM / TRX | sub.scanner_vendor |
| LedgerStatusEnum | PENDING / FILLED / NA | oper 轨台账状态 |

### 附录 D：SOC_DUAL 默认厂商

```text
NESSUS + LM（绿盟）
```

可扩展为 `ScanPolicyEnum.CUSTOM` 按需配置。

---

## 十四、变更日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-06-17 | 初稿：三发起方统一、SOC 双扫、W1~W4 分期 |
