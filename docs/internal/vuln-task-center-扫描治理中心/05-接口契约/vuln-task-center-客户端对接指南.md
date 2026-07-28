# vuln-task-center 客户端对接指南

> **谁看**：客户端开发人员（vul-pass / 运营指标 / 部侧工单 / 开放平台）与服务端开发人员（vuln-task-center）。
> **怎么用**：**第一篇·接口契约**是双方对接的依据（路径、参数、响应、回调）；**第二篇·落地方案**告诉客户端四类业务怎么组合调用这些接口。
> **与现有文档关系**：`vuln-task-center-ab-contract.yaml` 是 vul-pass 专用的机器可读契约（子集），本指南是其超集，覆盖四类客户端并补充人读说明。`06-分析与评审/` 下的分析报告记录了缺口与演进方向。
> **日期**：2026-07-27 · **状态**：与 vuln-task-center `3.6.9` 现状对齐；标注「规划中」的能力见第 11 节。

---

## 目录

- 第一篇·接口契约
  - 1. 角色与通信总览
  - 2. 通用约定（鉴权/响应/分页/状态枚举）
  - 3. 接口清单（创建/查询/操控/报告/回调）
  - 4. 数据结构 Schema
  - 5. 四类客户端差异化约定
- 第二篇·客户端业务落地方案
  - 6. 扫描任务管理（vuln-task-center 自身业务能力）
  - 7. 运营指标任务
  - 8. 部侧专项工单
  - 9. 开放平台
  - 10. 状态机与生命周期汇总
  - 11. 现状缺口与规划（开发另起）

---

# 第一篇·接口契约

## 1. 角色与通信总览

### 1.1 角色

| 角色 | 服务 | 职责 |
|------|------|------|
| **服务端** | `vuln-task-center`（port 18087） | 扫描任务调度、扫描器分配、子任务执行、结果回传、报告生成 |
| **客户端 A** | 扫描任务管理（如 `vul-pass`） | 创建/操控扫描计划，消费扫描结果与报告 |
| **客户端 B** | 运营指标任务 | 分发指标任务（管理员）-> 确认执行（安全员）-> 消费结果 |
| **客户端 C** | 部侧专项工单 | 接收部侧工单/任务 -> 派发扫描 -> 回传部侧 |
| **客户端 D** | 开放平台（`open-api-service` / 4A） | 指定厂商发起扫描 -> 消费结果 |

### 1.2 通信方式

```
客户端                                              vuln-task-center
  │                                                       │
  │  ──① REST（创建/查询/操控/报告）──────────────────▶    │
  │                                                       │
  │  ◀──② Kafka 回调（子任务状态变更/报告完成/结果）─────  │
  │                                                       │
  │  ◀──③ REST 轮询（回调阻断时主动拉取，兜底）──────────  │
```

- **① REST**：客户端主动调用，同步返回。基础路径见各接口。
- **② Kafka 回调**：服务端主动推送，客户端订阅 topic。**这是获取任务状态/报告的主推方式**。
- **③ REST 轮询**：回调不可达时的兜底，客户端主动查询。

> **重要**：当前子任务列表「创建后异步回调」能力**缺失（规划中，见 11）**，客户端需用查询接口轮询子任务列表。

### 1.3 调度链路（理解异步行为必读）

创建任务后，vuln-task-center **并非同步下发到扫描器**，而是：

```
客户端 REST 创建
     │
     ▼
vuln-task-center 落库 scan_task + 注册到 mint 调度服务
     │
     ▼  （mint 到点回调）
POST /event/scan/task/execute  ← mint 触发，创建执行实例 scan_task_survey
     │
     ▼
按扫描器分配策略拆分子任务 scan_sub_task -> Redis 队列 -> Kafka/HTTP 下发扫描器
     │
     ▼
扫描器回传结果 -> 观察者链更新子任务状态 -> Kafka 回调客户端
```

因此：**创建接口同步返回的是「主任务ID」，子任务列表需稍后查询或等回调**。

---

## 2. 通用约定

### 2.1 鉴权

- 接口通过请求头传 `_username`（部分接口为 Query 参数）标识调用方，服务端按其部门/科室/专业匹配可用扫描器。
- 部侧工单回传走 Kafka，需 `sign` 签名（见 8.4）。
- 开放平台 `outsideScan` 当前无独立鉴权，由网关层保障（4A 接入前为内置计划）。

### 2.2 统一响应格式

所有 REST 接口返回 `Result` 包装：

```json
{
  "code": 200,           // 200 成功；非 200 失败
  "msg": "success",
  "data": { ... }        // 业务数据，类型见各接口
}
```

部分历史接口直接返回 `Map` / `JSONObject` / `PageInfo`（未包装），以各接口说明为准。

### 2.3 分页

- 请求：`PageRequest`（含 `pageNum`、`pageSize`），部分接口为 Query 参数。
- 响应：`PageInfo<T>`（含 `list`、`total`、`pageNum`、`pageSize`）。

### 2.4 状态枚举（关键，多套并存）

> 现状有 3 套任务状态字段 + 1 套报告状态，值如下。**规划中（WP2）**将引入统一枚举包装，向后兼容。

| 字段 | 所属 | 值 → 含义 |
|------|------|----------|
| `taskState` | 主任务（`scan_task`） | `0`未开始 / `1`启动 / `2`暂停 / `3`完成 |
| `state`(survey) | 执行实例（`scan_task_survey`） | `0`未开始 / `1`执行中 / `2`已完成 / `3`失败 / `4`暂停 / `5`重启 |
| `state`(subTask) | 子任务（`scan_sub_task`） | `0`未开始 / `1`执行中 / `2`已完成 / `3`失败 / `4`暂停 |
| `state`(report) | LM 报告（`scan_task_lm_report`） | `0`未开始 / `1`开始下载 / `2`下载中 / `3`已完成 / `4`上传完成 / `5`异常 |
| ES 执行态 | `VulnScanNodeExecuteAttrEnum` | `finish`/`executing`/`waiting`/`fail`/`pause` |

> **坑点**：DB 用数字字符串，ES 用英文枚举，客户端消费时注意映射。

### 2.5 任务类型 `taskType`（两套命名并存，注意）

| 取值风格 | 值 | 出处 |
|----------|----|----|
| 长名（DTO 注释，**建议客户端用此**） | `vuln_scan` / `weak_password_scan` / `base_line_scan` / `port_scan` / `asset_find_scan` | `ScanTaskDTO` 注释 |
| 短名（代码实际写入） | `vuln` / `web` / `baseline` / `pwd` / `port` / `alive` | `VulnDatabaseAttrEnum` |

服务端 `save` 时若 `flag=1`（修复核验）会把 `vuln_scan` 转 `vuln`；`saveFirstHalf/saveSecondHalf` 强制写 `vuln`。客户端传长名即可，服务端兼容。

---

## 3. 接口清单

> 路径前缀：`/v1/scan/task` = ScanTaskUi；`/v1/scan/sub/task` = ScanSubTaskUi；`/event/scan/task` = ScanTaskEvent。
> 标注：✅ 已有 · 🟡 部分（仅 LM / 入参维度待补）· 🔵 规划中（见 11）

### 3.1 任务创建（三种模式）

#### 3.1.1 创建并自动调度（`save`）✅

最常用。创建主任务并立即注册到 mint 调度，到点自动下发扫描器。

| 项 | 值 |
|----|----|
| 方法路径 | `POST /v1/scan/task/add` |
| 入参 | `ScanTaskDTO`（body） |
| 返回 | `Result` |
| 适用客户端 | 扫描任务管理、开放平台（指定厂商） |

**请求示例**（关键字段，完整字段见第 4 节）：
```json
{
  "taskName": "每日漏洞扫描",
  "taskType": "vuln_scan",
  "classifyId": "1",            // 厂商：1=LM，2=AH，3=QM，4=TRX...
  "sceneId": "xxx",             // 场景（影响扫描器分配）
  "scannerId": "xxx",           // 指定扫描器（可选；不传则按权限/负载分配）
  "inputIp": "10.0.0.1,10.0.0.2",  // 扫描目标 IP（与 selectIp/fileIp 三选一）
  "executeType": "1",           // 1=定期 2=周期
  "startTime": "2026-07-27 00:00:00",
  "endTime": "2026-07-28 00:00:00",
  "createUser": "zhangsan",
  "flag": "1",                  // 1=修复核验（可选）；运营指标用 first/second half
  "scanPort": "standard",       // LM: standard/fast/user/allports
  "scanSpeed": "0"
}
```
**服务端行为**：落库 → 设回调 `appHost=vuln-task-center, path=/event/scan/task/execute` → `mintClient.add` 注册调度。下发失败则回滚删除已建计划。

#### 3.1.2 任务下发-仅记录（`saveFirstHalf`）✅

仅创建主任务记录，**不下发调度**。用于运营指标任务「管理员分发」阶段。

| 项 | 值 |
|----|----|
| 方法路径 | `POST /v1/scan/task/add/first/half`（批量：`/batch/add/first/half`；Excel：`/batch/add/first/half/excel`） |
| 入参 | `ScanTaskDTO`（**仅需 `taskName`、`createUser`、`remarks`**） |
| 返回 | `Result` |

**服务端强制覆盖**：`taskType=vuln`、`taskState=0`、`executeType=1`、`builtInTask=0`、`flag=7`，**不调 mint**。

#### 3.1.3 任务执行-确认下发（`saveSecondHalf`）✅

对上半场记录补全参数并下发。用于运营指标任务「安全员确认执行」阶段。

| 项 | 值 |
|----|----|
| 方法路径 | `POST /v1/scan/task/add/second/half` |
| 入参 | `ScanTaskDTO`（**必带上半场返回的 `id`** + 完整扫描参数） |
| 返回 | `Result` |

**服务端行为**：强制 `flag=7` → **删除上半场旧记录** → 重新落库 → 注册 mint 下发。仅限 `vuln` 计划。

> ⚠️ 实现为「删除重建」，客户端应在下半场成功后再依赖返回的 `id`。

#### 三模式对照

| 维度 | 创建并调度(3.1.1) | 下发-仅记录(3.1.2) | 执行-确认下发(3.1.3) |
|------|------|------|------|
| 必传 | 完整 DTO | taskName, createUser, remarks | id + 完整 DTO |
| 是否下发扫描器 | ✅ 是 | ❌ 否 | ✅ 是 |
| flag | 调用方传 | 强制 7 | 强制 7 |
| 适用 | 扫描任务管理/开放平台 | 运营指标-分发 | 运营指标-执行 |

### 3.2 任务查询

| # | 接口 | 方法路径 | 入参 | 返回 | 状态 |
|---|------|---------|------|------|------|
| 3.2.1 | 主任务详情（按 taskId） | `GET /v1/scan/task/vulnScan/basicInfo/{taskId}` | taskId | `Map` | ✅ |
| 3.2.2 | 主任务详情（按 surveyId） | `GET /v1/scan/task/vulnScan/task/{surveyId}` | surveyId | `ScanTaskDTO` | ✅ |
| 3.2.3 | 主任务列表 | `GET /v1/scan/task/list` | PageRequest, ScanTaskDTO(query), _username | `PageInfo<ScanTaskDTO>` | ✅ |
| 3.2.4 | 子任务列表（分页） | `GET /v1/scan/sub/task/page` | PageRequest, ScanSubTaskDTO(query) | `PageInfo<ScanSubTaskDTO>` | ✅ |
| 3.2.5 | 子任务列表（按主任务实例） | `GET /v1/scan/task/vulnScan/surveyList/{taskId}` | taskId, PageRequest | `PageInfo<ScanTaskSurveyDTO>` | ✅ |
| 3.2.6 | 子任务详情 | `GET /v1/scan/sub/task/findById/{key}` | subTaskId | `ScanSubTaskDTO` | ✅ |
| 3.2.7 | 扫描器任务列表（按实例+节点） | `GET /v1/scan/task/vulnScan/scanNodeList/{surveyId}/{nodeId}` | surveyId, nodeId, PageRequest | `PageInfo<Map>` | 🟡 仅按 surveyId+nodeId，跨实例查询规划中 |
| 3.2.8 | 执行/等待/完成数量 | `GET /v1/queue/query/count` | taskId, surveyId | `Map<String,Integer>` | ✅ |

### 3.3 任务操控

| # | 接口 | 方法路径 | 入参 | 返回 | 状态 |
|---|------|---------|------|------|------|
| 3.3.1 | 主任务暂停 | `GET /v1/scan/task/pause/{key}` | taskId | `Result` | ✅ |
| 3.3.2 | 主任务启动 | `GET /v1/scan/task/resume/{key}` | taskId | `Result` | ✅ |
| 3.3.3 | 主任务批量暂停/启动 | `POST /v1/scan/task/batch/pause` · `/batch/resume` | `Map` / `List<ScanTaskDTO>` | `Result` | ✅ |
| 3.3.4 | 实例级暂停/启动（按 surveyId） | `GET /v1/scan/task/classify/pause/{taskId}/{surveyId}` · `classify/resume/...` | taskId, surveyId | `Result` | ✅ |
| 3.3.5 | 主任务删除 | `POST /v1/scan/task/delete` | `{ids:[...], _username}` | `Result` | ✅ |
| 3.3.6 | 子任务暂停/启动 | — | — | — | 🔵 规划中（见 11） |
| 3.3.7 | 子任务删除 | `GET /v1/scan/sub/task/delete/{key}` | subTaskId | `Result` | ✅ |
| 3.3.8 | 复扫（按历史扫描器） | `GET /v1/scan/task/vuln/rescan/{taskId}` | taskId | `Result` | ✅ |
| 3.3.9 | 复扫（指定节点） | `POST /v1/scan/task/vuln/rescan` | `Map` | `Result` | 🟡 指定节点逻辑现状被注释，规划恢复 |

> ⚠️ `ScanSubTaskUi` 的删除方法 Java 名误写为 `pause`，实为删除，**以路径 `/delete/{key}` 为准**。

### 3.4 报告

> 现状报告能力**仅绿盟 LM**，通用多厂商报告生成 🔵 规划中（见 11）。

| # | 接口 | 方法路径 | 入参 | 返回 | 状态 |
|---|------|---------|------|------|------|
| 3.4.1 | 主任务生成报告（全量） | `POST /v1/scan/task/vulnScan/domnload/report/lm/all` | `List<Map>`(surveyId/nodeId/planId), fileFormat(query) | `ResponseEntity<byte[]>` | 🟡 仅 LM |
| 3.4.2 | 子任务生成报告（单个） | `POST /v1/scan/task/vulnScan/domnload/report/lm/id` | `Map`(surveyId/nodeId/planId), fileFormat(query) | `Result` | 🟡 仅 LM |
| 3.4.3 | 报告进度查询 | `GET /v1/scan/task/vulnScan/query/domnload/report/{surveyId}` | surveyId | `Result<List<Map>>` | ✅ |
| 3.4.4 | 报告下载（失败 Excel） | `GET /v1/scan/task/vulnScan/domnload/fail/report/{surveyId}` | surveyId | `ResponseEntity<byte[]>` | ✅ |

**报告进度响应示例**：
```json
{
  "code": 200,
  "data": [
    {
      "surveyId": "123",
      "nodeId": "10",
      "planId": "lm-plan-001",
      "state": "4",          // 4=上传完成，可下载
      "progress": "100",
      "uploadPath": "/ftp/report/xxx.html",
      "errorMsg": ""
    }
  ]
}
```

### 3.5 回调通知（服务端 → 客户端，Kafka）

这是客户端获取状态/报告的**主推通道**。客户端需订阅以下 topic：

| Topic | 事件 | 触发时机 | 必备字段 |
|-------|------|---------|---------|
| `dr_vul_scan_task_status` | `SUB_TASK_STATUS_CHANGED` | 子任务状态变更 | `surveyId`, `subTaskId`, `vendor`, `status`(FINISHED/FAILED/RUNNING), `progress`, `passTaskId`, `passSubTaskId`, `scanPhase`(1排查/2验证/3修复核验) |
| `dr_vul_scan_report_status` | `REPORT_JOB_COMPLETED` | 报告生成结束 | `reportJobId`, `surveyId`, `status`(ready/failed), `passTaskId`, `downloadUrl` |
| `outsideScanResult` | 外部扫描结果 | `outsideScan` 扫描完成 | 扫描结果（开放平台专用，见 9） |

> **缺失项（规划中，WP3）**：
> - **子任务列表回调**（创建后异步推送子任务清单）——当前客户端需轮询 `3.2.4/3.2.5`。
> - **子任务报告生成结束通知**——当前需轮询 `3.4.3`。
> - 回调通道将统一为 Kafka（已确认决策），新增 topic 见 11。

---

## 4. 数据结构 Schema

### 4.1 ScanTaskDTO（创建/查询主任务，关键字段）

| 字段 | 类型 | 含义 | 创建时是否必传 |
|------|------|------|---------------|
| `id` | Long | 主键 | save 可空；second half 必传 |
| `taskName` | String | 计划名称 | 是 |
| `taskType` | String | 计划类型（见 2.5） | 是 |
| `classifyId` | String | 厂商（1=LM,2=AH,3=QM,4=TRX,7=Nessus,8=AZ,9=JTL） | 是（缺省 1） |
| `sceneId` | String | 场景 | 影响 |
| `scannerId` | String | 指定扫描器 | 否（不传则负载均衡分配） |
| `inputIp` | String | 手动输入 IP（逗号分隔） | 三选一 |
| `selectIp` | String | 选择资产 IP（逗号分隔） | 三选一 |
| `fileIp` | String | 上传文件 IP | 三选一 |
| `executeType` | String | 1=定期 2=周期 | 是（空默认 1） |
| `executeCron` | String | 周期 cron | executeType=2 时必传 |
| `startTime` / `endTime` | Date | 起止时间 | 是 |
| `createUser` | String | 责任人（按其部门匹配扫描器） | 是 |
| `flag` | String | 标识：1=修复核验,2=暴露面,5=漏洞验证,7=指标任务 | 否 |
| `builtInTask` | String | 1=内置(不在列表显示),0=否 | 否（默认 0） |
| `vmId` | String | 关联 vuln-model（指标任务） | 否 |
| `scanPort` | String | 端口策略 standard/fast/user/allports | LM 用 |
| `scanSpeed` | String | 扫描速度 -2~-...2 | LM 用 |
| `templateId` | String | 漏洞模板(0=自动匹配)/弱口令字典 | 否 |
| `appHost` / `path` | String | 回调服务名/路径 | **服务端覆盖，客户端勿传** |

> 完整 75 字段见 `ScanTaskDTO.java`，LM 专属属性（tcpScanMode/udpScan/icmpPing/scanDepth 等）从略。

### 4.2 ScanSubTaskDTO（子任务）

| 字段 | 类型 | 含义 |
|------|------|------|
| `id` | Long | 主键 |
| `taskId` | String | 主任务 ID |
| `surveyId` | String | 执行实例 ID |
| `nodeId` | String | 扫描节点 ID |
| `scannerId` | String | 扫描器 ID |
| `planId` | String | 扫描器侧任务 ID（第三方计划 ID） |
| `ips` | String | 扫描资产 IP |
| `progress` | String | 进度 |
| `state` | String | 状态（见 2.4） |
| `createTime` / `endTime` | Date | 创建/结束时间 |
| `discrption` | String | 描述（失败原因，字段拼写如此） |

### 4.3 ScanTaskSurveyDTO（执行实例）

| 字段 | 类型 | 含义 |
|------|------|------|
| `id` | Long | 实例 ID |
| `taskId` | Long | 主任务 ID |
| `state` | String | 状态（见 2.4） |
| `executeTime` / `endTime` | Date | 本次执行/结束时间 |
| `scanIpTotal` / `scanIpCount` | String | 扫描 IP 总数/已扫数 |
| `process` | String | 进度 |
| `downloadReport` | String | 报告状态：0未点击/1已点击/成功后为路径 |

---

## 5. 四类客户端差异化约定

四类客户端当前**无显式 `clientType` 字段**，靠入口、`flag`、`builtInTask`、扫描器指定方式区分（规划中 WP1 将引入 `TaskCategoryEnum` 统一）。

| 客户端 | 创建入口 | 扫描器分配策略 | 标识字段 | 结果通道 |
|--------|---------|--------------|---------|---------|
| **扫描任务管理** | `POST /v1/scan/task/add` | vtc 负载均衡（`getNodeScannerMap` 最小负载） | `flag` 按场景 | Kafka `dr_vul_scan_task_status` |
| **运营指标任务** | first half + second half | vtc 负载均衡 | `flag=7`, `vmId` | 同上 |
| **部侧专项工单** | 工单 `distribute` -> 转 ScanTask | 客户端指定扫描器/节点 | `WorkbenchVulnOrderDO.scanTaskId` 关联 | 回传部侧 Kafka |
| **开放平台** | `POST /event/scan/task/outside/scan` | 指定厂商 + vtc 负载均衡 | `builtInTask=1`, `remarks=outsideScanEvent` | Kafka `outsideScanResult` |

### 5.1 扫描器分配策略说明

- **vtc 负载均衡**（默认）：`getNodeScannerMap` 按「空闲优先 → 负载比最小 → 范围分数」选节点。客户端不传 `scannerId` 即走此策略。
- **指定扫描器/节点**：传 `scannerId`；若该 ID 在 `scanner` 表查不到，服务端 fallback 当作 `nodeId` 用（即客户端可传节点 ID 间接指定节点）。
- **指定厂商**：传 `classifyId`，在该厂商可用节点中负载均衡。
- **复扫指定节点**：现状 `vulnRescan(Map)` 的指定逻辑被注释，规划恢复（见 11）。
- **部侧 scannerHash**：现状无 hash 概念，用 nodeId fallback；规划新增（见 11）。

---

# 第二篇·客户端业务落地方案

## 6. 扫描任务管理（vuln-task-center 自身业务能力）

### 6.1 业务流程

这是最通用的扫描任务管理，vul-pass 等上游业务通过它创建扫描计划、查询结果、生成报告。

```
创建计划        查询子任务        消费结果回调        生成报告        下载报告
  │               │                  │                 │              │
  ▼               ▼                  ▼                 ▼              ▼
POST /add   GET /sub/task/page  Kafka dr_vul_scan_   POST /report   GET /report
            (轮询，缺回调)        task_status         /lm/all        progress
```

### 6.2 调用时序

```
客户端                      vuln-task-center                    mint/扫描器
  │  POST /v1/scan/task/add     │                                   │
  │  (ScanTaskDTO)              │                                   │
  │────────────────────────────▶│                                   │
  │  200 Result(主任务ID)       │  mintClient.add                   │
  │◀────────────────────────────│──────────────────────────────────▶│
  │                             │  (mint 到点回调)                  │
  │                             │  POST /event/scan/task/execute    │
  │                             │◀──────────────────────────────────│
  │                             │  拆子任务 scan_sub_task -> 下发   │
  │  GET /v1/scan/sub/task/page │                                   │
  │  (按 taskId 轮询子任务)     │                                   │
  │────────────────────────────▶│                                   │
  │  PageInfo<ScanSubTaskDTO>   │                                   │
  │◀────────────────────────────│                                   │
  │                             │                                   │
  │  ◀── Kafka dr_vul_scan_task_status (子任务状态变更) ───────────│
  │      {surveyId, subTaskId, status:FINISHED, progress:100}     │
  │                             │                                   │
  │  POST /report/lm/all        │                                   │
  │────────────────────────────▶│                                   │
  │  200 报告流                 │                                   │
  │◀────────────────────────────│                                   │
```

### 6.3 接口调用示例（最小闭环）

1. **创建**：`POST /v1/scan/task/add`，记录返回的 `taskId`。
2. **轮询子任务**（回调缺失期间）：`GET /v1/scan/sub/task/page?taskId={taskId}`，直到所有子任务 `state=2/3`。
3. **消费回调**：订阅 `dr_vul_scan_task_status`，更新本地任务状态。
4. **生成报告**：`POST /v1/scan/task/vulnScan/domnload/report/lm/all`，传 `[{surveyId, nodeId, planId}]`。
5. **查报告进度**：`GET /v1/scan/task/vulnScan/query/domnload/report/{surveyId}`，`state=4` 时 `uploadPath` 可下载。

### 6.4 生命周期状态机

```
        创建                 mint触发              扫描器回传
[taskState=0 未开始] ──▶ [taskState=1 启动] ──▶ [taskState=1 启动, survey.state=1 执行中]
                                                       │
                              ┌────────────────────────┤
                              ▼                        ▼
                    pause: taskState=2        完成: survey.state=2
                    survey.state=4            taskState=3 完成
                              │
                    resume: taskState=1
                    survey.state=5→1
```

---

## 7. 运营指标任务

### 7.1 业务流程

运营指标任务采用**两阶段**模式：管理员先「分发」（仅记录），安全员再「确认执行」（补参数并下发）。指标任务需先在 `vuln-model` 落统计信息，再用 `vmId` 关联到扫描计划。

```
管理员分发              安全员确认执行
  │                       │
  ▼                       ▼
POST /add/first/half   POST /add/second/half
(仅 taskName/createUser (带上半场 id + 完整扫描参数)
 /remarks)             强制 flag=7，删除上半场重建并下发
强制 flag=7，不下发
  │                       │
  ▼                       ▼
scan_task(state=0)      scan_task(state=0→mint下发) + vmId 关联 vuln-model
```

### 7.2 与 vuln-model 联动

- 指标任务新增前需先调 `vuln-model` 落统计信息，再用 `vmId` 记录对应关系。
- 指标任务（`flag=7`）跳过「未知资产禁止」校验（`addChectInputIp` 中 `"7".equals(flag)` 分支）。

### 7.3 调用时序

```
客户端(vuln-model)              vuln-task-center
  │  先在 vuln-model 落统计       │
  │  拿到 vmId                    │
  │                               │
  │  POST /add/first/half         │
  │  {taskName, createUser,       │
  │   remarks, vmId}              │
  │──────────────────────────────▶│  落库 flag=7, state=0，不下发
  │  200 (上半场 id)              │
  │◀──────────────────────────────│
  │                               │
  │  ... 安全员确认 ...            │
  │                               │
  │  POST /add/second/half        │
  │  {id, inputIp, classifyId,    │
  │   startTime, ...}             │
  │──────────────────────────────▶│  删旧+重建+mint下发
  │  200                          │
  │◀──────────────────────────────│
  │                               │
  │  ◀── Kafka dr_vul_scan_task_status (结果) ──
```

### 7.4 要点

- **first half 只传 3 字段**（taskName/createUser/remarks），其余服务端强制。
- **second half 必传上半场 `id`**，且仅限 `vuln` 计划。
- `vmId` 用于结果回写 vuln-model 的统计。

---

## 8. 部侧专项工单

### 8.1 业务流程

部侧工单/任务经 Kafka 下发，vuln-task-center 接收后可派发为本地扫描任务，扫描完成后再回传部侧。

> ⚠️ **现状**：部侧**入站 Kafka 消费链路（`WorkbenchConsumer`）当前全部注释未启用**。实际消费方需确认（可能在 platform-admin）。出站回传链路已启用。本节描述目标流程，标注现状。

```
部侧                           vuln-task-center                    扫描器
  │  Kafka 下发工单/任务          │                                   │
  │  (TOPICS_INTER_*_CONSUMER)   │                                   │
  │────────────────────────────▶│  ⚠️ 现状未启用                    │
  │                              │                                   │
  │  或 REST 派发                 │                                   │
  │  GET /workbench/vuln/order/  │                                   │
  │  distribute/{id}             │── 创建 ScanTaskDO ──────────────▶│
  │────────────────────────────▶│  (scanTaskId 回填工单)            │
  │                              │                                   │
  │                              │  扫描完成，结果落库               │
  │                              │◀─────────────────────────────────│
  │  Kafka 回传                  │                                   │
  │  (TOPICS_INTER_*_PRODUCER)   │                                   │
  │◀────────────────────────────│  warnTaskReport / vulnOrderReturn│
```

### 8.2 工单/任务子类型（`orderType` + `orderSubType`）

| orderType | 含义 | orderSubType | 含义 |
|-----------|------|--------------|------|
| 1 | 工单指令 | 1 | 产品漏洞验证工单请求 |
| | | 2 | 产品漏洞验证工单回传 |
| | | 3 | 系统漏洞排查处置工单请求 |
| | | 4 | 系统漏洞排查处置工单回传 |
| 2 | 任务指令 | 101 | 产品漏洞预警任务 |
| | | 102 | 产品漏洞同步任务 |
| | | 103 | 口令字典同步任务 |
| | | 104 | 产品漏洞上传任务 |
| | | 105 | 口令字典上传任务 |

### 8.3 关键接口

| 接口 | 方法路径 | 用途 | 方向 |
|------|---------|------|------|
| 工单分页 | `POST /v1/workbench/vuln/order/findWorkbenchVulnOrderByPage` | 查询工单 | 查询 |
| 工单派发扫描 | `GET /v1/workbench/vuln/order/distribute/{id}` | 工单 → ScanTask | 派发 |
| 任务派发 | `GET /v1/workbench/vuln/task/distribute/{id}` | 预警任务派发 | 派发 |
| 预警任务回传 | `POST /v1/workbench/vuln/task/warnTaskReport` | 回传部侧（orderSubType=101） | 出站 Kafka `TOPICS_INTER_TASK_PRODUCER` |
| 工单回传 | `POST /v1/workbench/vuln/order/return/vulnOrderReturn` | 回传部侧（orderSubType=3） | 出站 Kafka `TOPICS_INTER_WORKORDER_PRODUCER` |
| 工单结果 | `POST /v1/workbench/vuln/order/result/findOrderResultByPage` | 查询待上报漏洞 | 查询 |

### 8.4 签名 `sign`

部侧回传报文需带 `sign` 签名字段。`WorkbenchVulnOrderUi.insert` 强制 `type=2`(主动上报)、`orderType=1`、`ispCode=CMCC`、`orgCode=230000`、`srcTktRole=0`。签名生成可参考测试接口 `POST /v1/vuln/report/test/usePythonCreateSign`。

### 8.5 关键 DTO 字段（`WorkbenchVulnOrderDTO`）

| 字段 | 含义 |
|------|------|
| `orderId` | 指令 ID（部侧全局唯一） |
| `orderType` / `orderSubType` | 一级/二级指令类别（见 8.2） |
| `tskPriority` | 优先级 1紧急/2普通/3一般 |
| `procTime` | 处置起止时间 `YmdHis-YmdHis` |
| `vulRange` | 系统漏洞范围（base64 SQL Where） |
| `distributeStat` | 0未派发/1已派发/4已回传 |
| `scanTaskId` | 关联的扫描任务 ID（派发后回填） |
| `sign` | 签名 |

> 完整字段见 `WorkbenchVulnOrderDTO` / `WorkbenchVulnTaskDTO`。

---

## 9. 开放平台

### 9.1 业务流程

开放平台（`open-api-service` / 4A 接入前）通过 `outsideScan` 发起扫描，指定厂商，扫描结果通过 Kafka `outsideScanResult` 回吐。

```
开放平台                       vuln-task-center                    扫描器
  │  POST /event/scan/task/      │                                   │
  │  outside/scan                │                                   │
  │  {taskName, inputIp,         │  builtInTask=1(内置,不在列表显示) │
  │   taskType}                  │  createUser=admin                 │
  │────────────────────────────▶│  remarks=outsideScanEvent         │
  │  200                         │── 负载均衡下发 ──────────────────▶│
  │◀────────────────────────────│                                   │
  │                              │                                   │
  │  ◀── Kafka outsideScanResult (扫描结果) ───────────────────────│
  │      (PushDataToOutsideScanObserver 识别 remarks=outsideScanEvent 推送)
```

### 9.2 关键接口

| 接口 | 方法路径 | 入参 | 用途 |
|------|---------|------|------|
| 外部扫描 | `POST /event/scan/task/outside/scan` | `{taskName, inputIp, taskType}` | 发起扫描，内置计划，指定厂商由 `classifyId` |
| 漏洞验证 | `POST /event/scan/task/vuln/verification` | `{taskName, scannerId, inputIp, createUser, remarks}` | 漏洞验证（flag=5） |

### 9.3 要点

- `outsideScan` 强制 `builtInTask=1`（不在任务列表显示）、`createUser=admin`、`remarks=outsideScanEvent`。
- 结果**不**走 `dr_vul_scan_task_status`，而是走独立 topic `outsideScanResult`（由 `PushDataToOutsideScanObserver` 识别 `remarks` 后推送）。
- 客户端订阅 `outsideScanResult` 获取结果。
- 指定厂商：在 `outsideScan` 的 `taskType` 之外，规划中通过 `classifyId` 指定（见 11，WP5 开放平台专属入口）。

---

## 10. 状态机与生命周期汇总

### 10.1 主任务生命周期

```
                          创建并调度(3.1.1)
                          ┌──────────┐
                          ▼          │
                     [0 未开始]      │ 下发-仅记录(3.1.2)
                          │          │
                     mint触发        │
                          ▼          │
                     [1 启动] ◀──────┘ 执行-确认下发(3.1.3)
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          pause(3.3.1)  完成      delete(3.3.5)
              │           │
          [2 暂停]    [3 完成]
              │
          resume(3.3.2)
              │
          [1 启动]
```

### 10.2 子任务生命周期

```
[0 未开始] ──▶ [1 执行中] ──▶ [2 已完成]
                   │   │
                   │   └──▶ [3 失败]
                   │
                   └──▶ [4 暂停] ──▶ [1 执行中] (resume)
```

> 子任务级 pause/resume 🔵 规划中（WP4）。当前只能实例级（`classifyPause/Resume`，按 surveyId 批量）。

### 10.3 报告生命周期

```
[0 未开始] ──▶ [1 开始下载] ──▶ [2 下载中] ──▶ [3 已完成] ──▶ [4 上传完成(可下载)]
                                                  │
                                                  └──▶ [5 异常(errorMsg)]
```

---

## 11. 现状缺口与规划（开发另起）

> 以下为已确认的演进方向（详见 `06-分析与评审/vuln-task-center接口能力-合理性与完整性分析.md`）。本指南标注 🔵 的项即在此。**开发另起，遵循 auto-dev-orchestrator 流程**。

### 11.1 已确认决策

| 决策项 | 选择 |
|--------|------|
| 实施范围 | WP1+WP2+WP3 基础层（统一类型/创建模式 + 状态机 + 回调通道） |
| 回调通道 | Kafka 回调 topic |
| 状态机改造 | 包装兼容（新增统一枚举包装现有字符串，旧硬编码渐进替换） |

### 11.2 缺口与对应工作包

| 缺口 | 现状 | 规划 | WP |
|------|------|------|----|
| 4 类客户端无统一标识 | 靠 flag/builtInTask/入口区分 | `TaskCategoryEnum` + `CreateModeEnum` | WP1 |
| 状态机缺失 | 3 套字符串，仅 2 处校验 | 统一枚举 + 转换矩阵 + 前置校验 | WP2 |
| 子任务列表回调 | 缺失，客户端轮询 | Kafka 新增回调 topic | WP3 |
| 报告生成结束通知 | 缺失，客户端轮询 | Kafka 回调（已部分有 `dr_vul_scan_report_status`） | WP3 |
| 子任务级暂停/启动 | 缺失 | 子任务级 pause/resume 接口 | WP4 |
| 通用报告生成 | 仅 LM | `ReportGenerateStrategy` 多厂商 | WP4 |
| 复扫指定节点 | 逻辑被注释 | 恢复指定节点 | WP5 |
| 部侧 scannerHash | 无 | 新增 hash 字段 | WP5 |
| 开放平台专属入口 | 走 outsideScan | 专属 controller + 指定厂商 | WP5 |
| 查询扫描器任务列表（跨实例） | 仅按 surveyId | 跨 survey 维度 | WP4 |

### 11.3 客户端对接建议（过渡期）

在 WP1-WP3 落地前，客户端按本指南现状对接：

1. **子任务列表**：用 `GET /v1/scan/sub/task/page` 轮询（创建后延迟 1-2s 起查）。
2. **报告就绪**：订阅 `dr_vul_scan_report_status`；不可达时轮询 `GET .../query/domnload/report/{surveyId}`。
3. **状态映射**：消费 `dr_vul_scan_task_status` 的 `status`(FINISHED/FAILED/RUNNING) 映射到本地状态。
4. **四类客户端**：按第 5 节差异化约定选择入口和扫描器指定方式。

---

## 附录 A：Kafka topic 速查

| Topic | 方向 | 用途 | 状态 |
|-------|------|------|------|
| `dr_vul_scan_task_status` | 出站→客户端 | 子任务状态变更 | ✅ |
| `dr_vul_scan_report_status` | 出站→客户端 | 报告生成结束 | ✅ |
| `outsideScanResult` | 出站→开放平台 | 外部扫描结果 | ✅ |
| `vuln_scan_add_topic` | 出站→tools-scheduler | 下发扫描计划 | ✅ |
| `vuln_scan_result_topic` | 入站←tools-scheduler | 扫描结果回传 | ✅ |
| `ws_vuln_scan_topic` | 内部→WebSocket | 前端进度广播 | ✅ |
| `TOPICS_INTER_WORKORDER_PRODUCER` | 出站→部侧 | 工单回传 | ✅ |
| `TOPICS_INTER_TASK_PRODUCER` | 出站→部侧 | 任务回传 | ✅ |
| `TOPICS_INTER_WORKORDER_CONSUMER` | 入站←部侧 | 工单下发 | ⚠️ 注释未启用 |
| `TOPICS_INTER_TASK_CONSUMER` | 入站←部侧 | 任务下发 | ⚠️ 注释未启用 |

## 附录 B：关键代码索引

| 主题 | 路径 |
|------|------|
| 主任务 UI | [ScanTaskUi.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/ui/ScanTaskUi.java) |
| 子任务 UI | [ScanSubTaskUi.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/ui/ScanSubTaskUi.java) |
| 创建三模式 | [ScanTaskServiceImpl.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/service/impl/ScanTaskServiceImpl.java) |
| mint 回调执行 | [ScanTaskEvent.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/ui/event/ScanTaskEvent.java) |
| 扫描器分配 | [QueueAppServiceImpl.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/app/service/impl/QueueAppServiceImpl.java) |
| 部侧工单 | [WorkbenchVulnOrderUi.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/ui/WorkbenchVulnOrderUi.java) |
| 部侧常量 | [Constants.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/infrastructure/utils/constants/Constants.java) |
| Kafka 消费 | [Consumer.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/infrastructure/utils/kafka/Consumer.java) |
| ScanTaskDTO | [ScanTaskDTO.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/app/dto/ScanTaskDTO.java) |
