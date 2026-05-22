# 网络安全漏洞管理平台 · 开放平台 API 接口规范

| 项 | 内容 |
|----|------|
| API 版本 | **1.1.0** |
| 协议 | HTTPS · REST JSON |
| Base Path | `/api/open/v1` |
| OpenAPI | [`openapi/v1/openapi.yaml`](../../openapi/v1/openapi.yaml)（OpenAPI 3.1，可导入 Swagger UI / Postman / 代码生成） |
| 适用对象 | 已完成 Partner 注册的第三方系统（SIEM、ITSM、资产平台、安全运营系统等） |

## 目录

- [1. 概述](#1-概述)
- [2. 接入准备](#2-接入准备)
- [3. 鉴权与安全](#3-鉴权与安全)
- [4. 通用约定](#4-通用约定)
- [5. REST API](#5-rest-api)
- [6. 事件回调（Webhook）](#6-事件回调webhook)
- [7. 扫描结果数据外发（xml / json）](#7-扫描结果数据外发xml--json)
- [8. 能力码（Capability）](#8-能力码capability)
- [9. 业务错误码](#9-业务错误码)
- [10. 典型集成流程](#10-典型集成流程)
- [附录 A · 漏洞实例状态](#附录-a--漏洞实例状态-vulinfostat)
- [附录 B · 相关资源](#附录-b--相关资源)

---

## 1. 概述

### 1.1 能力范围

第三方通过**开放平台 API** 可完成：

| 能力 | 说明 |
|------|------|
| 扫描/排查 | 创建任务、查询进度与结果摘要 |
| 漏洞实例 | 查询、验证、处置（含修复与修复失败/备案）、修复核验 |
| 扫描结果数据外发 | 任务结束、验证扫描、修复核验扫描完成后下载结构化结果（支持 XML / JSON 两种输出物） |
| 事件通知 | 平台向 Partner 回调 URL 推送任务/实例/外发就绪事件 |

扫描与漏洞检测由平台内部对接执行引擎完成；Partner **不直接调用**引擎接口。

### 1.2 集成架构

```text
┌─────────────────────┐         HTTPS REST          ┌──────────────────────────┐
│  第三方系统 Partner  │ ◀────────────────────────▶ │  漏洞管理平台 · 开放平台   │
│  (您的系统)          │         Webhook POST         │  /api/open/v1            │
└─────────────────────┘ ◀────────────────────────── └──────────────────────────┘
```

### 1.3 漏洞实例生命周期（写接口）

```text
排查（POST /tasks）
    → 实例默认 vulInfoStat = 1（初始发现）
验证（POST /instances/{vulInfoID}/verify）
    → 2 已验证有效  |  3 已验证误报（终态，不可再处置）
处置
    → POST .../remediate  → vulInfoStat = 5（已修复）或 9（修复失败/备案，同一接口）
修复核验（POST .../verify-fix）
    → 平台触发核验扫描；完成后 → 6 / 7 / 10
```

---

## 2. 接入准备

### 2.1 开通材料

接入前由平台运营分配：

| 配置项 | 说明 |
|--------|------|
| `partnerId` | 接入方唯一标识 |
| 鉴权凭证 | Bearer Token，或 `X-Api-Key` + HMAC 密钥 |
| `capabilities` | 已开通的能力码列表（见 §8） |
| 回调地址 | 默认 `callbackUrl`（可在创建任务时覆盖） |
| IP 白名单 / mTLS | 按安全要求可选 |

### 2.2 环境地址

| 环境 | Base URL 示例 |
|------|----------------|
| 测试 | `https://{测试域名}/api/open/v1` |
| 生产 | `https://{生产域名}/api/open/v1` |

实际域名以平台运营提供为准。

---

## 3. 鉴权与安全

### 3.1 方式一：Bearer Token（推荐）

```http
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### 3.2 方式二：API Key + 签名

| 请求头 | 说明 |
|--------|------|
| `X-Api-Key` | 平台分配的 Key |
| `X-Signature` | 对规范串做 **HMAC-SHA256** 的十六进制摘要 |
| `X-Timestamp` | Unix 时间戳（秒），有效期建议 ≤ 5 分钟 |

签名原文（示例，以运营文档为准）：

```text
{HTTP_METHOD}\n{PATH}\n{TIMESTAMP}\n{SHA256_HEX(BODY)}
```

### 3.3 Webhook 验签（Partner 侧实现）

平台向您的 `callbackUrl` 投递事件时携带：

| 请求头 | 说明 |
|--------|------|
| `X-Webhook-Signature` | 事件 body 的 HMAC-SHA256 |
| `X-Webhook-Timestamp` | Unix 秒，5 分钟内有效 |

收到后请先验签再处理业务；建议响应 HTTP `200` 及 `{"received":true}`。

---

## 4. 通用约定

### 4.1 响应包装

除文件下载外，接口在 **HTTP 200** 时仍使用业务码 `code` 区分成败：

```json
{
  "code": 0,
  "message": "ok",
  "requestId": "req-20260518-001",
  "data": { }
}
```

| 字段 | 说明 |
|------|------|
| `code` | `0` 成功；非 0 见 §9 |
| `message` | 描述信息 |
| `data` | 成功时业务数据；失败多为 `null` |
| `requestId` | 排障追踪 ID，建议日志留存 |

### 4.2 幂等

| 场景 | 约定 |
|------|------|
| 创建任务 | **必填** `extTaskId`（Partner 侧唯一）；重复提交返回 `40901` 或 `200` 且返回已有 `taskId` |
| 查询任务进度 | 仅使用平台返回的 **`taskId`**，不需传 `extTaskId` |
| 实例写操作 | 建议请求头 `Idempotency-Key: {vulInfoID}-{动作}` |

### 4.3 分页与时间

| 项 | 约定 |
|----|------|
| 分页 | `page` 从 1 起；`size` 最大 1000 |
| 时间 | ISO 8601 UTC，如 `2026-05-18T08:00:00Z` |
| 实例 `transferTime` | 部侧常见为 **Unix 秒字符串** |

### 4.4 字段命名

漏洞实例字段与部侧表34 **同名**，例如：`vulInfoID`、`vulInfoStat`、`vulName`、`vulNetAddr`、`remedDesc`、`srcMethod` 等。第三方对接报送系统时可减少字段转换。

---
## 5. REST API

> 路径均相对于 Base Path `/api/open/v1`。  
> 下文「—」表示该项无参数。

### 5.0 接口一览

| 阶段 | 方法 | 路径 | 能力码 |
|------|------|------|--------|
| 排查 | POST | `/tasks` | `TASK_WRITE` |
| 排查 | GET | `/tasks` | `TASK_READ` |
| 排查 | GET | `/tasks/{taskId}` | `TASK_READ` |
| 查询 | POST | `/instances/search` | `INSTANCE_READ` |
| 查询 | GET | `/instances/{vulInfoID}` | `INSTANCE_READ` |
| 验证 | POST | `/instances/{vulInfoID}/verify` | `INSTANCE_VERIFY` |
| 验证 | POST | `/instances/verify:batch` | `INSTANCE_VERIFY` |
| 处置 | POST | `/instances/{vulInfoID}/remediate` | `INSTANCE_REMEDIATE` |
| 处置 | POST | `/instances/remediate:batch` | `INSTANCE_REMEDIATE` |
| 修复核验 | POST | `/instances/{vulInfoID}/verify-fix` | `INSTANCE_VERIFY_FIX` |
| 修复核验 | POST | `/instances/verify-fix:batch` | `INSTANCE_VERIFY_FIX` |
| 外发 | GET | `/exports/{exportId}` | `EXPORT_READ` |
| 外发 | GET | `/exports/{exportId}/download` | `EXPORT_READ` |
| 外发 | GET | `/tasks/{taskId}/exports` | `EXPORT_READ` |

**写接口生命周期**：排查 → 验证 → 处置（`remediate`，含已修复与修复失败）→ 修复核验。

### 5.0.1 文档体例

各接口按下列块描述：**路径参数** · **查询参数** · **请求头** · **请求体** · **响应 data** · **状态约束** · **示例**。

**字段列**：`参数` · `类型` · `必填`（✓ 必填 / ○ 可选 / 条件 条件必填）· `说明`

**通用请求头**（写接口建议携带）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| Authorization | string | ✓ | `Bearer <accessToken>`，或 `X-Api-Key` + `X-Signature` |
| Content-Type | string | ✓ | `application/json` |
| Idempotency-Key | string | ○ | 写操作幂等；创建任务可与 `extTaskId` 二选一；实例处置建议 `vulInfoID+动作` |

**重要约定**：

| 项 | 约定 |
|----|------|
| 任务键 | **仅创建任务**使用 `extTaskId`；查进度、拉实例仅使用平台返回的 **`taskId`** |
| 实例写操作 | 均以路径 **`vulInfoID`** 定位，**不使用** `extTaskId` / `taskId` |
| 实例搜索 | `taskId` / `extTaskId` 在 **请求体** 中传递；勿传冲突值 |

---

### 5.1 任务 · 排查/扫描

#### 5.1.1 `POST /tasks` — 创建扫描任务

| 项 | 值 |
|----|-----|
| 能力 | `TASK_WRITE` |
| 说明 | 排查入口；新发现实例默认 `vulInfoStat = 1` |

**路径参数**：— · **查询参数**：—

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| extTaskId | string | ✓ | Partner 幂等键 |
| taskName | string | ✓ | 任务名称 |
| targets | string[] | ✓ | 扫描目标列表（IPv4 / IPv6 / URL；平台按条目自动识别类型） |
| vulnType | int | ✓ | **1**=系统漏洞，**2**=Web 漏洞 |
| callbackUrl | string | ○ | 覆盖 Partner 默认回调 URL |
| scanTemplateId | int | ○ | 扫描模板 ID；支持 **漏洞扫描**、**存活探测**、**端口扫描** 及组合（由模板定义） |
| srcMethod | int | ○ | 资产扫描/处置方式，码表见《接口规范(2025)》**A.10**；若传入则**覆盖** `scanTemplateId` 默认处置方式 |
| exportTemplateId | string | ○ | 扫描结果外发模板（如 `tpl-svmp-xml-scan-bundle`） |
| priority | enum | ○ | `LOW` / `MEDIUM` / `HIGH` |
| options.portScope | string | ○ | 端口范围，如 `1-65535` |
| options.isLiveProbe | bool | ○ | 是否存活探测 |
| options.pswdGuessEnabled | bool | ○ | 是否弱口令检测 |

> **IPv6 提示**：`targets` 含 IPv6 时，写法多样（全写、压缩、`[]` 包裹等）。Partner 入参与平台响应/外发回显的字符串形式**可能不一致**。建议统一采用 **RFC 5952 规范格式**（全小写、最长零压缩，如 `2001:db8::1`），并在联调阶段比对「请求 targets ↔ 任务详情 ↔ 外发 targets[]」是否一致。

**响应 data**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| extTaskId | string | ✓ | 回显 |
| taskId | string | ✓ | 平台任务 ID（后续均用此字段） |
| status | enum | ✓ | `ACCEPTED` / `QUEUED` / `REJECTED` |
| createdAt | datetime | ✓ | 创建时间 |
| message | string | ○ | `REJECTED` 时原因 |

**状态约束**：相同 `extTaskId` 重复提交 → **40901** 或 **200** 且返回已有 `taskId`。

**请求示例**

```http
POST /api/open/v1/tasks HTTP/1.1
Authorization: Bearer <accessToken>
Content-Type: application/json
Idempotency-Key: idem-ext-2026-0001

{
  "extTaskId": "EXT-TASK-2026-0001",
  "taskName": "2026Q2-核心业务系统排查",
  "targets": ["10.10.1.1", "10.10.1.2", "2001:db8::1"],
  "vulnType": 1,
  "callbackUrl": "https://partner.example.com/hooks/vuln",
  "scanTemplateId": 10086,
  "srcMethod": 1021,
  "exportTemplateId": "tpl-svmp-xml-scan-bundle",
  "priority": "HIGH",
  "options": {
    "portScope": "1-65535",
    "isLiveProbe": true,
    "pswdGuessEnabled": false
  }
}
```

**响应示例（成功）**

```json
{
  "code": 0,
  "message": "ok",
  "requestId": "req-20260517-t001",
  "data": {
    "extTaskId": "EXT-TASK-2026-0001",
    "taskId": "TASK-7f3a2b1c",
    "status": "ACCEPTED",
    "createdAt": "2026-05-17T08:00:00Z"
  }
}
```

---

#### 5.1.2 `GET /tasks/{taskId}` — 查询任务进度

| 项 | 值 |
|----|-----|
| 能力 | `TASK_READ` |
| 说明 | **仅需**路径 `taskId`，**无需** `extTaskId` |

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| taskId | string | ✓ | 创建任务响应中的平台任务 ID |

**响应 data**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| extTaskId | string | ○ | 回显（来自映射表，非请求入参） |
| taskId | string | ✓ | 平台任务 ID |
| status | enum | ✓ | `PENDING` / `RUNNING` / `FINISHED` / `FAILED` |
| progress | int | ○ | 0–100 |
| startedAt | datetime | ○ | 开始时间 |
| finishedAt | datetime | ○ | 结束时间 |
| errorMessage | string | ○ | 失败原因 |

**请求示例**

```http
GET /api/open/v1/tasks/TASK-7f3a2b1c HTTP/1.1
Authorization: Bearer <accessToken>
```

**响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "requestId": "req-20260517-t010",
  "data": {
    "extTaskId": "EXT-TASK-2026-0001",
    "taskId": "TASK-7f3a2b1c",
    "status": "RUNNING",
    "progress": 65,
    "startedAt": "2026-05-17T08:00:05Z",
    "finishedAt": null,
    "errorMessage": null
  }
}
```

---

#### 5.1.3 `GET /tasks` — 分页查询任务列表

| 项 | 值 |
|----|-----|
| 能力 | `TASK_READ` |

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| extTaskId | string | ○ | 按 Partner 键过滤（平台库，不调引擎） |
| status | enum | ○ | `PENDING` / `RUNNING` / `FINISHED` / `FAILED` |
| createdFrom | datetime | ○ | 创建时间起（含） |
| createdTo | datetime | ○ | 创建时间止（含） |
| page | int | ✓ | 从 1 开始 |
| size | int | ✓ | ≤1000 |

**响应 data**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| page | int | ✓ | 当前页 |
| size | int | ✓ | 每页条数 |
| total | int | ✓ | 总记录数 |
| items | array | ✓ | 任务摘要列表 |

**items[] 元素**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| taskId | string | ✓ | **后续查进度、拉实例均用此字段** |
| extTaskId | string | ○ | Partner 幂等键 |
| taskName | string | ✓ | 任务名称 |
| status | enum | ✓ | 任务状态 |
| progress | int | ○ | 0–100 |
| startedAt / finishedAt | datetime | ○ | 起止时间 |
| errorMessage | string | ○ | 失败原因 |
| createdAt | datetime | ✓ | 创建时间 |

---

### 5.2 漏洞实例 · 查询

#### 5.2.1 `POST /instances/search` — 分页搜索

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_READ` |
| 说明 | 建议至少传 `taskId` 或 `extTaskId` 之一 |

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| exportProfile | string | ○ | `MIIT-2025`：部侧扩展字段档 |

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| taskId | string | ○ | 平台任务 ID |
| extTaskId | string | ○ | 平台解析为 taskId；**勿与 taskId 传冲突值** |
| vulInfoStatList | int[] | ○ | 状态过滤；空表示不过滤 |
| vulLevelList | int[] | ○ | 危害等级过滤 |
| page | int | ✓ | 从 1 开始 |
| size | int | ✓ | ≤1000 |

**响应 data.items[]**（列表标准字段）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| vulInfoID | string | ✓ | 系统漏洞实例 ID |
| vulID | string | ○ | 产品漏洞编号 |
| vulInfoStat | int | ✓ | 状态（A.8） |
| lvRsn | int | ○ | 未修复原因（A.23） |
| vulName | string | ✓ | 漏洞名称 |
| vulLevel | int | ○ | 危害等级 |
| orgVulId | string | ○ | 原始编号（如 CVE） |
| vulNetAddr | string | ○ | 网络地址 |
| vulPort | int | ○ | 端口 |
| vulSvc | string | ○ | 服务 |
| isAccess | int | ○ | **0** 内网 / **1** 互联网 |
| transferTime | string | ✓ | 状态变更时间（常为 Unix 秒字符串） |
| vulnDisposalId | string | ○ | 引擎处置 ID |
| extVulnRef | string | ○ | Partner 扩展引用 |

**请求示例**

```json
{
  "taskId": "TASK-7f3a2b1c",
  "vulInfoStatList": [1, 2],
  "vulLevelList": [3, 4],
  "page": 1,
  "size": 50
}
```

---

#### 5.2.2 `GET /instances/{vulInfoID}` — 实例详情

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_READ` |

**路径参数**：`vulInfoID`（✓）

**响应 data**：在列表标准字段基础上增加：

| 参数 | 说明 |
|------|------|
| remedDesc / fixLnk / defDev / remedTime / srcMethod | 修复台账 |
| vulInstCpe、assetID、assetName 等 | 表34 扩展 |
| archiveReason、provincialFields | 备案补充 |
| extVulnRef | Partner 扩展 |

---

### 5.3 漏洞实例 · 验证

> **与修复核验区分**：本节确认漏洞**真假**（前置 `vulInfoStat ∈ {0,1}`）；`verify-fix` 确认**修复是否生效**（前置 `vulInfoStat = 5`）。

#### 5.3.1 `POST /instances/{vulInfoID}/verify` — 单条验证

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_VERIFY` |

**路径参数**：`vulInfoID`（✓）

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| vulnType | int | ○ | 1/2；默认取自实例 |
| verifyResult | enum | ✓ | `VALID`→**2**；`FALSE_POSITIVE`→**3** |
| srcMethod | int | 条件 | **`VALID` 时必填**（如 1021、1026） |
| transferTime | string | ○ | 缺省服务端生成 |
| operator | string | ✓ | 操作人（审计） |
| remark | string | ○ | 备注 |

**响应 data**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| vulInfoID | string | ✓ | 实例 ID |
| vulInfoStat | int | ✓ | 变更后状态 |
| lvRsn | int | ○ | 验证阶段通常为空 |
| transferTime | string | ✓ | 变更时间 |
| srcMethod | int | ○ | 回显处置方式 |

**状态约束**：前置 `vulInfoStat ∈ {0,1}`；**3（误报）后禁止**修复/备案。

**扫描外发**：若验证阶段触发复扫 / POC 扫描，完成后平台生成 `EXPORT_READY`（`exportStage=VERIFY_SCAN`）。外发结构按 §5.8.6 聚合；相关实例位于 `vulnerabilities[].instances[]`。

**请求示例（验证有效）**

```json
{
  "verifyResult": "VALID",
  "srcMethod": 1021,
  "operator": "sec-analyst@corp.com",
  "transferTime": "1747476000",
  "remark": "POC 复核通过"
}
```

---

#### 5.3.2 `POST /instances/verify:batch` — 批量验证

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_VERIFY` |
| 说明 | 部分成功；**不使用** `extTaskId` |

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| operator | string | ✓ | 操作人 |
| items | array | ✓ | 待验证列表 |

**items[] 元素**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| vulInfoID | string | ✓ | 实例 ID |
| vulnType | int | ○ | 默认取自实例 |
| verifyResult | enum | ✓ | `VALID` / `FALSE_POSITIVE` |
| srcMethod | int | 条件 | `VALID` 时必填 |
| transferTime | string | ○ | 本条时间 |
| remark | string | ○ | 备注 |

**响应 data**：

| 参数 | 说明 |
|------|------|
| success | 成功项数组，元素结构同单条「响应 data」 |
| failed | 失败项：`vulInfoID`、`code`、`message` |

---

### 5.4 处置阶段说明

验证有效（`vulInfoStat = 2`）或核验未修复（`vulInfoStat = 7`）后，调用 **§5.5** `POST .../remediate` 提交处置结果：

| 结果 | `vulInfoStat` | 说明 |
|------|---------------|------|
| 已修复 | **5** | `srcMethod` 为可修复类（A.10，如 1050–1052） |
| 修复失败 / 备案 | **9** | `srcMethod` 为不可修复类；须传 `lvRsn`（A.23）、`archiveReason` |

**状态约束**：

| 类型 | 规则 |
|------|------|
| 前置 | `vulInfoStat ∈ {2, 7}`，且 `≠ 3` |
| 终态 | 单次调用推进至 **5** 或 **9**；已终态不可重复处置（**40005**） |

> 原独立 `POST .../archive` 已合并入 `remediate`；`archive` 路径不再提供。

---

### 5.5 处置 · 修复（含修复失败/备案）

#### 5.5.1 `POST /instances/{vulInfoID}/remediate` — 单条处置

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_REMEDIATE` |

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| srcMethod | int | ✓ | 漏洞管理处置方式，码表 **A.10**（如 1050 补丁、1051 防护、1052 关停；不可修复类 → 终态 9） |
| remedDesc | string | 条件 | 已修复（→5）时必填 |
| fixLnk | string | 条件 | `srcMethod=1050` 时必填 |
| defDev | string | 条件 | `srcMethod=1051` 或 `1052` 时必填 |
| remedTime | string | 条件 | 已修复时必填，如 `3日` |
| lvRsn | int | 条件 | 修复失败（→9）时必填，码表 **A.23**（101–109 / 999） |
| archiveReason | string | 条件 | 修复失败（→9）时必填 |
| approvedBy | string | ○ | 修复失败审批人 |
| recordAt | string | ○ | 备案时间 |
| provincialFields | object | ○ | 省侧扩展 JSON |
| srcTktRole | int | ○ | 派单角色，码表 **A.9**（表56 `srcTktRole`） |
| dstTktRole | int | ○ | 处置角色，码表 **A.9**（表56 `dstTktRole`） |
| assignerDept | string | ○ | 派单人部门（表56 拆分 `srcTktPrsn`，**勿**直接传 `srcTktPrsn`） |
| assignerEmail | string | ○ | 派单人邮箱 |
| assignerPhone | string | ○ | 派单人电话 |
| handlerDept | string | ○ | 处置人部门（表56 拆分 `dstTktPrsn`，**勿**直接传 `dstTktPrsn`） |
| handlerEmail | string | ○ | 处置人邮箱 |
| handlerPhone | string | ○ | 处置人电话 |
| transferTime | string | ○ | 缺省服务端生成 |
| remark | string | ○ | 备注 |

**响应 data**：`vulInfoID`、`vulInfoStat`（**5** 或 **9**）、`lvRsn`、`transferTime`、`remedDesc` 或 `archiveReason`、`srcMethod`。

**请求示例（已修复）**

```json
{
  "srcMethod": 1050,
  "remedDesc": "升级 OpenSSH 至 9.6p1 并重启 sshd",
  "fixLnk": "https://www.openssh.com/releasenotes.html",
  "remedTime": "3日",
  "srcTktRole": 1,
  "dstTktRole": 2,
  "assignerDept": "安全运营中心",
  "assignerEmail": "soc-dispatch@corp.com",
  "assignerPhone": "010-12345678",
  "handlerDept": "基础架构部",
  "handlerEmail": "ops@corp.com",
  "handlerPhone": "010-87654321",
  "transferTime": "1747480000"
}
```

**请求示例（修复失败/备案）**

```json
{
  "srcMethod": 1099,
  "lvRsn": 101,
  "archiveReason": "业务连续性限制，经评估接受风险",
  "approvedBy": "risk-committee@corp.com",
  "srcTktRole": 1,
  "dstTktRole": 3,
  "assignerDept": "安全运营中心",
  "assignerEmail": "soc-dispatch@corp.com",
  "assignerPhone": "010-12345678",
  "handlerDept": "业务系统部",
  "handlerEmail": "app-owner@corp.com",
  "handlerPhone": "010-11112222",
  "transferTime": "1747481000"
}
```

---

#### 5.5.2 `POST /instances/remediate:batch` — 批量处置

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_REMEDIATE` |
| 说明 | 部分成功；**不使用** `extTaskId` |

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| items | array | ✓ | 待处置列表 |

**items[] 元素**：字段同 §5.5.1，且每条 **必填** `vulInfoID`（路径参数改为 body 字段）。

**响应 data**：

| 参数 | 说明 |
|------|------|
| success | 成功项数组，元素结构同单条「响应 data」 |
| failed | 失败项：`vulInfoID`、`code`、`message` |

---

### 5.7 漏洞实例 · 修复核验

#### 5.7.1 `POST /instances/{vulInfoID}/verify-fix` — 单条

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_VERIFY_FIX` |
| 说明 | 前置 **`vulInfoStat = 5`**；平台触发修复核验扫描，完成后推进状态并可选外发 |

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| transferTime | string | ○ | 缺省服务端生成 |
| remark | string | ○ | 备注 |

**平台行为**：受理后异步执行核验扫描；`vulInfoStat` 暂保持 **5**，完成后通过 Webhook `INSTANCE_VERIFY_FIX_COMPLETED` 通知终态 **6 / 7 / 10**，并可产生 `EXPORT_READY`（`exportStage=VERIFY_FIX_SCAN`）。

**响应 data（受理）**：`vulInfoID`、`vulInfoStat`（5）、`verifyFixStatus`（`PENDING` / `RUNNING`）、`verifyFixJobId`、`message`。

**请求示例**

```json
{
  "transferTime": "1747488000",
  "remark": "安排复扫 POC"
}
```

---

#### 5.7.2 `POST /instances/verify-fix:batch` — 批量

| 项 | 值 |
|----|-----|
| 能力 | `INSTANCE_VERIFY_FIX` |

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| items | array | ✓ | 待核验列表 |

**items[] 元素**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| vulInfoID | string | ✓ | 实例 ID |
| transferTime | string | ○ | 本条时间 |
| remark | string | ○ | 备注 |

**响应 data**：`success` / `failed`，结构同 §5.5.2 批量处置。

---

### 5.8 扫描结果 · 数据外发

任务扫描结束、验证阶段扫描完成、修复核验阶段扫描完成且外发组装完成后，平台推送 **`EXPORT_READY`**（§6），或通过下列接口拉取。

#### 5.8.1 输出物格式

扫描结果外发输出物由开放平台按当前接口领域模型重新组装，支持 **`xml`** 与 **`json`** 两种 `format`；根结构为 `<TaskExport>` / `taskExport`，不作为引擎原始 XML 透传。

| `format` | 下载 `Content-Type` | 输出物 | 说明 |
|----------|---------------------|--------|------|
| `xml` | `application/xml` | 单个 XML 文档 | 根元素为 `<TaskExport>`，字段名与 JSON key 保持一致 |
| `json` | `application/json` | 单个 JSON 文档 | 顶层对象为 `taskExport`，字段与 XML 同构 |

**序列化约定**：

| 项 | 约定 |
|----|------|
| 字段来源 | 以本开放接口的任务、实例、处置、备案、修复核验字段为准；引擎原始字段仅进入 `evidence` / `appendices` 等扩展节点 |
| 数组 | JSON 使用数组；XML 使用复数容器 + 单数元素，如 `targets.target[]` 对应 `<targets><target>...</target></targets>` |
| 空值 | JSON 可省略或为 `null`；XML 可省略空元素 |
| 时间 | 与 §4.3 一致，平台字段使用 ISO 8601 UTC；需要保留引擎原始时间时放入 `evidence.engineTime` |
| 弱口令 | 不输出明文密码；统一输出 `passwordMasked` 或空值 |

#### 5.8.2 外发触发场景

| `exportStage` | 触发时机 | `dataType` | 输出约定 |
|---------------|----------|------------|----------|
| `TASK_COMPLETED` | 普通扫描 / 排查任务结束 | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` | 按任务启用能力输出 `liveProbeResults[]`、`portScanResults[]`、`vulnerabilities[]` 等 |
| `VERIFY_SCAN` | 漏洞验证阶段触发复扫 / POC 扫描完成 | `SYSTEM_VULNERABILITY` | 按 §5.8.6 产品漏洞聚合；实例在 `instances[]` |
| `VERIFY_FIX_SCAN` | 修复核验阶段触发复扫完成 | `SYSTEM_VULNERABILITY` | 同上 |

`VERIFY_SCAN` / `VERIFY_FIX_SCAN` 产生的外发与任务结束外发使用同一下载接口和同一 `xml` / `json` 序列化规则；区别仅在 `export.exportStage`、`export.dataType`。阶段扫描外发按 §5.8.6 产品漏洞聚合结构输出，实例明细位于 `vulnerabilities[].instances[]`，以 `vulInfoID` 标识。

#### 5.8.3 输出物逻辑结构

```text
TaskExport / taskExport
├── export                 # 外发记录元数据
├── task                   # 当前开放接口任务信息
├── summary                # 汇总统计
├── targets / target[]          # 扫描目标 / 资产维度
├── liveProbeResults / liveProbeResult[]  # 主机存活探测结果
├── portScanResults / portScanResult[]    # 端口扫描结果
├── vulnerabilities / vulnerability[]   # 按产品漏洞 vulID 聚合
│   ├── vulID, orgVulId, vulLevel, vulName, vulDesc
│   └── instances / instance[]            # 系统漏洞实例明细
│       ├── vulInfoID, targetId, vulInfoStat, vulPort, evidence …
├── weakPasswords / weakPassword[]
├── baselineResults / baselineResult[]
└── appendices / appendix[]      # 跨目标或无法归属到单目标的附录
```

各任务能力在规范化输出中的落点：

| 任务能力 | 规范化落点 | 说明 |
|----------|------------|------|
| 主机存活探测 | `targets[]` + `liveProbeResults[]` | `targets[]` 保存目标主数据，`liveProbeResults[]` 保存探测方式、存活状态、时延等结果 |
| 端口扫描 | `targets[]` + `portScanResults[]` | 端口、协议、状态、服务、Banner 等作为正式端口扫描结果输出 |
| 漏洞扫描 | `targets[]` + `vulnerabilities[]` | 按 **产品漏洞 `vulID`** 聚合；实例明细在 `instances[]` |
| 验证 / 修复核验扫描 | `vulnerabilities[]` | `exportStage` 区分 `VERIFY_SCAN` / `VERIFY_FIX_SCAN`；实例在 `instances[]` |

其他引擎结果参考结构的落点：

| 参考结构 | 规范化落点 | 说明 |
|----------|------------|------|
| Web 漏洞结果 | `targets[].site` + `vulnerabilities[].evidence.url` | Web 站点作为目标，URL、参数、请求信息进入证据 |
| 系统综合结果 | `vulnerabilities[]` + `baselineResults[]` + `weakPasswords[]` + `appendices[]` | 漏洞、配置基线、弱口令、主机附录拆到独立集合 |
| 口令猜测结果 | `weakPasswords[]` + `vulnerabilities[]` | 弱口令作为独立集合，同时可关联漏洞实例 `vulInfoID` |

#### 5.8.4 输出参数（`export` / `task` / `summary`）

| JSON 路径 | XML 路径 | 类型 | 必填 | 说明 |
|-----------|----------|------|:---:|------|
| `taskExport.export.exportId` | `/TaskExport/export/exportId` | string | ✓ | 外发记录 ID |
| `taskExport.export.format` | `/TaskExport/export/format` | enum | ✓ | `xml` / `json` |
| `taskExport.export.exportTemplateId` | `/TaskExport/export/exportTemplateId` | string | ○ | 外发模板 ID |
| `taskExport.export.exportStage` | `/TaskExport/export/exportStage` | enum | ✓ | `TASK_COMPLETED` / `VERIFY_SCAN` / `VERIFY_FIX_SCAN` |
| `taskExport.export.dataType` | `/TaskExport/export/dataType` | enum | ✓ | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` |
| `taskExport.export.generatedAt` | `/TaskExport/export/generatedAt` | datetime | ✓ | 生成时间 |
| `taskExport.export.expiresAt` | `/TaskExport/export/expiresAt` | datetime | ○ | 下载过期时间 |
| `taskExport.export.recordCount` | `/TaskExport/export/recordCount` | int | ✓ | 漏洞**实例**总条数（`instances[]` 合计），用于评估包大小 |
| `taskExport.task.taskId` | `/TaskExport/task/taskId` | string | ✓ | 平台任务 ID |
| `taskExport.task.extTaskId` | `/TaskExport/task/extTaskId` | string | ○ | Partner 幂等键 |
| `taskExport.task.taskName` | `/TaskExport/task/taskName` | string | ✓ | 任务名称 |
| `taskExport.task.targetType` | `/TaskExport/task/targetType` | enum | ✓ | `IPV4` / `IPV6` / `URL` |
| `taskExport.task.vulnType` | `/TaskExport/task/vulnType` | int | ✓ | **1**=系统漏洞，**2**=Web 漏洞 |
| `taskExport.task.scanTemplateId` | `/TaskExport/task/scanTemplateId` | int | ○ | 扫描模板 ID |
| `taskExport.task.status` | `/TaskExport/task/status` | enum | ✓ | `FINISHED` / `FAILED` 等任务状态 |
| `taskExport.task.startedAt` | `/TaskExport/task/startedAt` | datetime | ○ | 任务开始时间 |
| `taskExport.task.finishedAt` | `/TaskExport/task/finishedAt` | datetime | ○ | 任务结束时间 |
| `taskExport.summary.totalTargets` | `/TaskExport/summary/totalTargets` | int | ○ | 目标总数 |
| `taskExport.summary.aliveTargets` | `/TaskExport/summary/aliveTargets` | int | ○ | 存活目标数 |
| `taskExport.summary.openPorts` | `/TaskExport/summary/openPorts` | int | ○ | 开放端口数 |
| `taskExport.summary.totalInstances` | `/TaskExport/summary/totalInstances` | int | ○ | 漏洞实例总数 |
| `taskExport.summary.verifiedValid` | `/TaskExport/summary/verifiedValid` | int | ○ | 已验证有效数 |
| `taskExport.summary.falsePositive` | `/TaskExport/summary/falsePositive` | int | ○ | 误报数 |
| `taskExport.summary.remediated` | `/TaskExport/summary/remediated` | int | ○ | 已修复数 |
| `taskExport.summary.archived` | `/TaskExport/summary/archived` | int | ○ | 已备案 / 修复失败数 |
| `taskExport.summary.weakPasswordCount` | `/TaskExport/summary/weakPasswordCount` | int | ○ | 弱口令条数 |
| `taskExport.summary.baselineIssueCount` | `/TaskExport/summary/baselineIssueCount` | int | ○ | 配置基线问题条数 |

#### 5.8.5 输出参数（`targets[]` / `liveProbeResults[]` / `portScanResults[]`）

| JSON 路径 | XML 路径 | 类型 | 必填 | 说明 |
|-----------|----------|------|:---:|------|
| `taskExport.targets[].targetId` | `/TaskExport/targets/target/targetId` | string | ✓ | 平台目标 ID；无资产 ID 时可由任务 ID + 目标地址生成 |
| `taskExport.targets[].target` | `/TaskExport/targets/target/target` | string | ✓ | 原始扫描目标，IP / URL 均可 |
| `taskExport.targets[].targetType` | `/TaskExport/targets/target/targetType` | enum | ✓ | `IPV4` / `IPV6` / `URL` |
| `taskExport.targets[].assetID` | `/TaskExport/targets/target/assetID` | string | ○ | 平台资产 ID |
| `taskExport.targets[].assetName` | `/TaskExport/targets/target/assetName` | string | ○ | 资产名称 |
| `taskExport.targets[].site` | `/TaskExport/targets/target/site` | string | ○ | Web 站点 URL |
| `taskExport.targets[].os` | `/TaskExport/targets/target/os` | string | ○ | 操作系统 |
| `taskExport.targets[].riskValue` | `/TaskExport/targets/target/riskValue` | decimal | ○ | 目标风险值 |
| `taskExport.targets[].riskLevel` | `/TaskExport/targets/target/riskLevel` | int | ○ | 目标风险等级 |
| `taskExport.liveProbeResults[].liveProbeId` | `/TaskExport/liveProbeResults/liveProbeResult/liveProbeId` | string | ✓ | 存活探测结果 ID |
| `taskExport.liveProbeResults[].targetId` | `/TaskExport/liveProbeResults/liveProbeResult/targetId` | string | ✓ | 关联 `targets[].targetId` |
| `taskExport.liveProbeResults[].address` | `/TaskExport/liveProbeResults/liveProbeResult/address` | string | ✓ | 探测地址，通常为 IP / 域名 |
| `taskExport.liveProbeResults[].alive` | `/TaskExport/liveProbeResults/liveProbeResult/alive` | bool | ✓ | 是否存活 |
| `taskExport.liveProbeResults[].probeMethod` | `/TaskExport/liveProbeResults/liveProbeResult/probeMethod` | enum/string | ○ | 探测方式，如 `ICMP` / `TCP` / `ARP` |
| `taskExport.liveProbeResults[].latencyMs` | `/TaskExport/liveProbeResults/liveProbeResult/latencyMs` | int | ○ | 响应耗时，单位毫秒 |
| `taskExport.liveProbeResults[].mac` | `/TaskExport/liveProbeResults/liveProbeResult/mac` | string | ○ | MAC 地址 |
| `taskExport.liveProbeResults[].osGuess` | `/TaskExport/liveProbeResults/liveProbeResult/osGuess` | string | ○ | 操作系统识别 / 猜测结果 |
| `taskExport.liveProbeResults[].detectedAt` | `/TaskExport/liveProbeResults/liveProbeResult/detectedAt` | datetime | ○ | 探测时间 |
| `taskExport.portScanResults[].portScanId` | `/TaskExport/portScanResults/portScanResult/portScanId` | string | ✓ | 端口扫描结果 ID |
| `taskExport.portScanResults[].targetId` | `/TaskExport/portScanResults/portScanResult/targetId` | string | ✓ | 关联 `targets[].targetId` |
| `taskExport.portScanResults[].address` | `/TaskExport/portScanResults/portScanResult/address` | string | ✓ | 扫描地址，通常为 IP / 域名 |
| `taskExport.portScanResults[].port` | `/TaskExport/portScanResults/portScanResult/port` | int | ✓ | 端口号 |
| `taskExport.portScanResults[].protocol` | `/TaskExport/portScanResults/portScanResult/protocol` | enum/string | ✓ | `TCP` / `UDP` 等 |
| `taskExport.portScanResults[].state` | `/TaskExport/portScanResults/portScanResult/state` | enum/string | ✓ | `open` / `closed` / `filtered` 等 |
| `taskExport.portScanResults[].service` | `/TaskExport/portScanResults/portScanResult/service` | string | ○ | 服务名称，如 `ssh` / `http` |
| `taskExport.portScanResults[].banner` | `/TaskExport/portScanResults/portScanResult/banner` | string | ○ | Banner 信息 |
| `taskExport.portScanResults[].version` | `/TaskExport/portScanResults/portScanResult/version` | string | ○ | 服务版本 |
| `taskExport.portScanResults[].detectedAt` | `/TaskExport/portScanResults/portScanResult/detectedAt` | datetime | ○ | 探测时间 |

#### 5.8.6 输出参数（`vulnerabilities[]` · 产品漏洞聚合）

外发时 **`vulnerabilities[]` 按产品漏洞 `vulID` 聚合**，同一产品漏洞的多条实例归入 `instances[]`，以减少重复字段、缩小包体。

**产品层（`vulnerabilities[]` 元素）**：

| JSON 路径 | XML 路径 | 类型 | 必填 | 说明 |
|-----------|----------|------|:---:|------|
| `taskExport.vulnerabilities[].vulID` | `/TaskExport/vulnerabilities/vulnerability/vulID` | string | ✓ | 产品漏洞编号（聚合键，外发包内唯一） |
| `taskExport.vulnerabilities[].orgVulId` | `/TaskExport/vulnerabilities/vulnerability/orgVulId` | string | ○ | 原始编号，如 CVE |
| `taskExport.vulnerabilities[].vulLevel` | `/TaskExport/vulnerabilities/vulnerability/vulLevel` | int | ○ | 危害等级 |
| `taskExport.vulnerabilities[].vulName` | `/TaskExport/vulnerabilities/vulnerability/vulName` | string | ✓ | 漏洞名称 |
| `taskExport.vulnerabilities[].vulDesc` | `/TaskExport/vulnerabilities/vulnerability/vulDesc` | string | ○ | 漏洞描述 |

**实例层（`vulnerabilities[].instances[]`）**：

| JSON 路径 | XML 路径 | 类型 | 必填 | 说明 |
|-----------|----------|------|:---:|------|
| `…instances[].vulInfoID` | `…/instances/instance/vulInfoID` | string | ✓ | 系统漏洞实例 ID |
| `…instances[].targetId` | `…/instances/instance/targetId` | string | ✓ | 关联 `targets[].targetId` |
| `…instances[].vulInfoStat` | `…/instances/instance/vulInfoStat` | int | ✓ | 实例状态，见附录 A |
| `…instances[].lvRsn` | `…/instances/instance/lvRsn` | int | ○ | 未修复原因 |
| `…instances[].vulNetAddr` | `…/instances/instance/vulNetAddr` | string | ○ | 网络地址 |
| `…instances[].vulPort` | `…/instances/instance/vulPort` | int | ○ | 端口 |
| `…instances[].vulSvc` | `…/instances/instance/vulSvc` | string | ○ | 服务 |
| `…instances[].isAccess` | `…/instances/instance/isAccess` | int | ○ | **0** 内网 / **1** 互联网 |
| `…instances[].transferTime` | `…/instances/instance/transferTime` | string | ✓ | 状态变更时间 |
| `…instances[].srcMethod` | `…/instances/instance/srcMethod` | int | ○ | 验证 / 处置方式 |
| `…instances[].extVulnRef` | `…/instances/instance/extVulnRef` | string | ○ | Partner 扩展引用 |
| `…instances[].evidence.url` | `…/evidence/url` | string | ○ | Web 命中 URL |
| `…instances[].evidence.protocol` | `…/evidence/protocol` | string | ○ | 协议 |
| `…instances[].evidence.message` | `…/evidence/message` | string | ○ | 命中证据 |
| `…instances[].remediation.*` | `…/remediation/*` | — | ○ | 修复 / 备案字段，结构同原扁平 `remediation` |

#### 5.8.7 输出参数（弱口令、配置基线与附录）

| JSON 路径 | XML 路径 | 类型 | 必填 | 说明 |
|-----------|----------|------|:---:|------|
| `taskExport.weakPasswords[].weakPasswordId` | `/TaskExport/weakPasswords/weakPassword/weakPasswordId` | string | ✓ | 弱口令记录 ID |
| `taskExport.weakPasswords[].targetId` | `/TaskExport/weakPasswords/weakPassword/targetId` | string | ✓ | 关联目标 ID |
| `taskExport.weakPasswords[].vulInfoID` | `/TaskExport/weakPasswords/weakPassword/vulInfoID` | string | ○ | 关联漏洞实例 ID |
| `taskExport.weakPasswords[].service` | `/TaskExport/weakPasswords/weakPassword/service` | string | ✓ | 服务类型，如 `ssh` / `mysql` |
| `taskExport.weakPasswords[].port` | `/TaskExport/weakPasswords/weakPassword/port` | int | ○ | 登录端口 |
| `taskExport.weakPasswords[].protocol` | `/TaskExport/weakPasswords/weakPassword/protocol` | string | ○ | 协议 |
| `taskExport.weakPasswords[].username` | `/TaskExport/weakPasswords/weakPassword/username` | string | ✓ | 用户名 |
| `taskExport.weakPasswords[].passwordMasked` | `/TaskExport/weakPasswords/weakPassword/passwordMasked` | string | ○ | 脱敏后的口令，不输出明文 |
| `taskExport.baselineResults[].baselineResultId` | `/TaskExport/baselineResults/baselineResult/baselineResultId` | string | ✓ | 配置基线结果 ID |
| `taskExport.baselineResults[].targetId` | `/TaskExport/baselineResults/baselineResult/targetId` | string | ✓ | 关联目标 ID |
| `taskExport.baselineResults[].templateName` | `/TaskExport/baselineResults/baselineResult/templateName` | string | ○ | 配置模板名称 |
| `taskExport.baselineResults[].checkName` | `/TaskExport/baselineResults/baselineResult/checkName` | string | ✓ | 检查项名称 |
| `taskExport.baselineResults[].groupName` | `/TaskExport/baselineResults/baselineResult/groupName` | string | ○ | 检查项分组 |
| `taskExport.baselineResults[].riskValue` | `/TaskExport/baselineResults/baselineResult/riskValue` | decimal | ○ | 风险值 |
| `taskExport.baselineResults[].result` | `/TaskExport/baselineResults/baselineResult/result` | enum/string | ✓ | `PASS` / `FAIL` / `UNKNOWN`，或保留引擎原始值 |
| `taskExport.baselineResults[].solution` | `/TaskExport/baselineResults/baselineResult/solution` | string | ○ | 修复建议 |
| `taskExport.appendices[].appendixId` | `/TaskExport/appendices/appendix/appendixId` | string | ✓ | 附录 ID |
| `taskExport.appendices[].targetId` | `/TaskExport/appendices/appendix/targetId` | string | ○ | 关联目标 ID |
| `taskExport.appendices[].name` | `/TaskExport/appendices/appendix/name` | string | ✓ | 附录名称，如端口信息、端口 Banner、安装软件信息 |
| `taskExport.appendices[].columns[]` | `/TaskExport/appendices/appendix/columns/column` | string[] | ✓ | 表头 |
| `taskExport.appendices[].rows[][]` | `/TaskExport/appendices/appendix/rows/row/value` | string[][] | ✓ | 表格行值，按 `columns` 顺序排列 |

#### 5.8.8 `GET /exports/{exportId}` — 外发元数据

| 项 | 值 |
|----|-----|
| 能力 | `EXPORT_READ` |

**路径参数**：`exportId`（✓）

**响应 data**：

| 参数 | 类型 | 说明 |
|------|------|------|
| exportId | string | 外发记录 ID |
| taskId | string | 平台任务 ID |
| extTaskId | string | Partner 任务键 |
| exportTemplateId | string | 外发模板 |
| format | string | `xml` / `json` |
| exportStage | enum | `TASK_COMPLETED` / `VERIFY_SCAN` / `VERIFY_FIX_SCAN` |
| dataType | enum | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` |
| status | enum | `PENDING` / `READY` / `EXPIRED` / `FAILED` |
| recordCount | int | 记录条数 |
| expiresAt | datetime | 下载过期时间 |
| createdAt | datetime | 生成时间 |
| downloadUrl | string | 可选预签名 URL |

#### 5.8.9 `GET /exports/{exportId}/download` — 下载文件

| 项 | 值 |
|----|-----|
| 能力 | `EXPORT_READ` |

返回文件流；`format=xml` 时返回单个规范化 XML 文档，`format=json` 时返回同构 JSON 文档。弱口令相关字段不输出明文密码，Partner 存储与展示需符合本单位数据安全要求。

#### 5.8.10 `GET /tasks/{taskId}/exports` — 任务外发历史

| 项 | 值 |
|----|-----|
| 能力 | `EXPORT_READ` |

**查询参数**：`page`、`size`（✓）

**响应 data**：分页包装 + `items[]`（元素结构同外发元数据）。

---
## 6. 事件回调（Webhook）

平台向 Partner 注册的 URL 发起 **`POST`**，`Content-Type: application/json`。

### 6.1 公共请求体

| 字段 | 类型 | 说明 |
|------|------|------|
| eventId | string | 事件唯一 ID（幂等处理） |
| eventType | string | 见下表 |
| occurredAt | datetime | 事件发生时间 |
| partnerId | string | 接入方 ID |
| payload | object | 随事件类型变化 |

### 6.2 事件类型与 payload

| eventType | 说明 |
|-----------|------|
| `TASK_COMPLETED` | 任务正常结束 |
| `TASK_FAILED` | 任务失败 |
| `INSTANCE_VERIFY_FIX_COMPLETED` | 修复核验完成（→6/7/10） |
| `EXPORT_READY` | 外发包可下载 |

**`TASK_COMPLETED` / `TASK_FAILED` · payload**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| taskId | string | ✓ | 平台任务 ID |
| extTaskId | string | ○ | Partner 任务键 |
| status | enum | ✓ | `FINISHED` / `FAILED` |
| summary.totalInstances | int | ○ | 实例总数 |
| summary.verifiedValid | int | ○ | 验证有效数 |
| summary.falsePositive | int | ○ | 误报数 |

**`INSTANCE_VERIFY_FIX_COMPLETED` · payload**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| vulInfoID | string | ✓ | 实例 ID |
| vulInfoStat | int | ✓ | 当前状态（6/7/10） |
| previousVulInfoStat | int | ○ | 变更前状态（通常为 5） |

**`EXPORT_READY` · payload**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| exportId | string | ✓ | 外发记录 ID |
| taskId | string | ✓ | 平台任务 ID |
| extTaskId | string | ○ | Partner 任务键 |
| exportTemplateId | string | ○ | 外发模板 |
| format | string | ✓ | 外发格式 |
| exportStage | string | ✓ | `TASK_COMPLETED` / `VERIFY_SCAN` / `VERIFY_FIX_SCAN` |
| dataType | string | ✓ | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` |
| recordCount | int | ○ | 条数 |
| downloadUrl | string | ○ | 预签名下载 URL |

### 6.3 示例：任务完成

```json
{
  "eventId": "evt-20260518-0001",
  "eventType": "TASK_COMPLETED",
  "occurredAt": "2026-05-18T14:00:00Z",
  "partnerId": "partner-demo-01",
  "payload": {
    "extTaskId": "EXT-TASK-2026-0001",
    "taskId": "TASK-7f3a2b1c",
    "status": "FINISHED",
    "summary": {
      "totalInstances": 25,
      "verifiedValid": 18,
      "falsePositive": 5
    }
  }
}
```

### 6.4 示例：修复核验完成

```json
{
  "eventId": "evt-20260517-0003",
  "eventType": "INSTANCE_VERIFY_FIX_COMPLETED",
  "occurredAt": "2026-05-17T15:00:00Z",
  "partnerId": "partner-demo-01",
  "payload": {
    "vulInfoID": "VI-20260517-0002",
    "vulInfoStat": 6,
    "previousVulInfoStat": 5
  }
}
```

### 6.5 示例：外发就绪

```json
{
  "eventId": "evt-20260518-0002",
  "eventType": "EXPORT_READY",
  "occurredAt": "2026-05-18T14:05:00Z",
  "partnerId": "partner-demo-01",
  "payload": {
    "exportId": "EXP-20260518-7f3a",
    "taskId": "TASK-7f3a2b1c",
    "extTaskId": "EXT-TASK-2026-0001",
    "exportTemplateId": "tpl-svmp-xml-scan-bundle",
    "format": "xml",
    "exportStage": "TASK_COMPLETED",
    "dataType": "MIXED",
    "recordCount": 128,
    "downloadUrl": "https://vuln-platform.example.com/download/EXP-20260518-7f3a?sig=..."
  }
}
```

非 2xx 响应将触发平台重试（策略以运营配置为准）。

---

## 7. 扫描结果数据外发（xml / json）

### 7.1 输出结构

对外输出为单个规范化文档，不透传引擎原始 XML。`xml` 与 `json` 仅为序列化格式差异，逻辑结构完全一致。

| 格式 | 根结构 | 示例文件名 |
|------|--------|------------|
| `xml` | `<TaskExport>` | `export-{taskId}-{exportId}.xml` |
| `json` | `{ "taskExport": { ... } }` | `export-{taskId}-{exportId}.json` |

### 7.2 结构示例（完整）

以下示例展示任务结束外发的**完整顶层结构**：`export`、`task`、`summary`、`targets`、`liveProbeResults`、`portScanResults`、聚合后的 `vulnerabilities[]`（含 `instances[]`）。验证/修复核验阶段外发仅 `export` + `vulnerabilities[]` 等子集，序列化规则相同。

**JSON 示例**：

```json
{
  "taskExport": {
    "export": {
      "exportId": "EXP-20260518-7f3a",
      "format": "json",
      "exportTemplateId": "tpl-svmp-xml-scan-bundle",
      "exportStage": "TASK_COMPLETED",
      "dataType": "MIXED",
      "generatedAt": "2026-05-18T14:05:00Z",
      "expiresAt": "2026-05-25T14:05:00Z",
      "recordCount": 3
    },
    "task": {
      "taskId": "TASK-7f3a2b1c",
      "extTaskId": "EXT-TASK-2026-0001",
      "taskName": "2026Q2-核心业务系统排查",
      "vulnType": 1,
      "scanTemplateId": 10086,
      "status": "FINISHED",
      "startedAt": "2026-05-18T08:00:00Z",
      "finishedAt": "2026-05-18T14:00:00Z"
    },
    "summary": {
      "totalTargets": 2,
      "aliveTargets": 2,
      "openPorts": 4,
      "totalInstances": 3,
      "verifiedValid": 0,
      "falsePositive": 0,
      "remediated": 0,
      "archived": 0,
      "weakPasswordCount": 0,
      "baselineIssueCount": 0
    },
    "targets": [
      {
        "targetId": "TGT-001",
        "target": "10.10.1.1",
        "targetType": "IPV4",
        "assetID": "AST-1001",
        "assetName": "core-host-01",
        "os": "Linux"
      },
      {
        "targetId": "TGT-002",
        "target": "2001:db8::1",
        "targetType": "IPV6",
        "assetName": "core-host-v6"
      }
    ],
    "liveProbeResults": [
      {
        "liveProbeId": "LIVE-001",
        "targetId": "TGT-001",
        "address": "10.10.1.1",
        "alive": true,
        "probeMethod": "ICMP",
        "latencyMs": 12,
        "detectedAt": "2026-05-18T08:05:00Z"
      },
      {
        "liveProbeId": "LIVE-002",
        "targetId": "TGT-002",
        "address": "2001:db8::1",
        "alive": true,
        "probeMethod": "ICMP",
        "latencyMs": 8,
        "detectedAt": "2026-05-18T08:05:02Z"
      }
    ],
    "portScanResults": [
      {
        "portScanId": "PORT-001",
        "targetId": "TGT-001",
        "address": "10.10.1.1",
        "port": 22,
        "protocol": "TCP",
        "state": "open",
        "service": "ssh",
        "banner": "OpenSSH/4.3",
        "detectedAt": "2026-05-18T08:10:00Z"
      },
      {
        "portScanId": "PORT-002",
        "targetId": "TGT-001",
        "address": "10.10.1.1",
        "port": 443,
        "protocol": "TCP",
        "state": "open",
        "service": "https",
        "detectedAt": "2026-05-18T08:10:01Z"
      }
    ],
    "vulnerabilities": [
      {
        "vulID": "VUL-OPENSSH-BYPASS",
        "orgVulId": "CVE-2006-5051",
        "vulLevel": 3,
        "vulName": "OpenSSH 安全限制绕过漏洞",
        "vulDesc": "OpenSSH 4.x 存在安全限制绕过，可能导致未授权访问。",
        "instances": [
          {
            "vulInfoID": "VI-20260518-0001",
            "targetId": "TGT-001",
            "vulInfoStat": 1,
            "vulNetAddr": "10.10.1.1",
            "vulPort": 22,
            "vulSvc": "ssh",
            "isAccess": 0,
            "transferTime": "1747476000",
            "evidence": {
              "protocol": "TCP",
              "message": "OpenSSH/4.3"
            }
          },
          {
            "vulInfoID": "VI-20260518-0002",
            "targetId": "TGT-002",
            "vulInfoStat": 1,
            "vulNetAddr": "2001:db8::1",
            "vulPort": 22,
            "vulSvc": "ssh",
            "transferTime": "1747476100",
            "evidence": {
              "protocol": "TCP",
              "message": "OpenSSH/4.3"
            }
          }
        ]
      },
      {
        "vulID": "VUL-SSL-WEAK",
        "orgVulId": "CVE-2014-3566",
        "vulLevel": 2,
        "vulName": "SSLv3 POODLE 漏洞",
        "vulDesc": "服务支持 SSLv3，存在 POODLE 攻击风险。",
        "instances": [
          {
            "vulInfoID": "VI-20260518-0003",
            "targetId": "TGT-001",
            "vulInfoStat": 1,
            "vulNetAddr": "10.10.1.1",
            "vulPort": 443,
            "vulSvc": "https",
            "transferTime": "1747476200",
            "evidence": {
              "protocol": "TCP",
              "message": "SSLv3 supported"
            }
          }
        ]
      }
    ]
  }
}
```

**XML 示例**（与 JSON 同构；`instances` 为 `instance` 元素列表）：

```xml
<TaskExport>
  <export>
    <exportId>EXP-20260518-7f3a</exportId>
    <format>xml</format>
    <exportTemplateId>tpl-svmp-xml-scan-bundle</exportTemplateId>
    <exportStage>TASK_COMPLETED</exportStage>
    <dataType>MIXED</dataType>
    <generatedAt>2026-05-18T14:05:00Z</generatedAt>
    <expiresAt>2026-05-25T14:05:00Z</expiresAt>
    <recordCount>3</recordCount>
  </export>
  <task>
    <taskId>TASK-7f3a2b1c</taskId>
    <extTaskId>EXT-TASK-2026-0001</extTaskId>
    <taskName>2026Q2-核心业务系统排查</taskName>
    <vulnType>1</vulnType>
    <scanTemplateId>10086</scanTemplateId>
    <status>FINISHED</status>
    <startedAt>2026-05-18T08:00:00Z</startedAt>
    <finishedAt>2026-05-18T14:00:00Z</finishedAt>
  </task>
  <summary>
    <totalTargets>2</totalTargets>
    <aliveTargets>2</aliveTargets>
    <openPorts>4</openPorts>
    <totalInstances>3</totalInstances>
    <verifiedValid>0</verifiedValid>
    <falsePositive>0</falsePositive>
    <remediated>0</remediated>
    <archived>0</archived>
  </summary>
  <targets>
    <target>
      <targetId>TGT-001</targetId>
      <target>10.10.1.1</target>
      <targetType>IPV4</targetType>
      <assetName>core-host-01</assetName>
    </target>
    <target>
      <targetId>TGT-002</targetId>
      <target>2001:db8::1</target>
      <targetType>IPV6</targetType>
      <assetName>core-host-v6</assetName>
    </target>
  </targets>
  <liveProbeResults>
    <liveProbeResult>
      <liveProbeId>LIVE-001</liveProbeId>
      <targetId>TGT-001</targetId>
      <address>10.10.1.1</address>
      <alive>true</alive>
      <probeMethod>ICMP</probeMethod>
      <latencyMs>12</latencyMs>
    </liveProbeResult>
  </liveProbeResults>
  <portScanResults>
    <portScanResult>
      <portScanId>PORT-001</portScanId>
      <targetId>TGT-001</targetId>
      <address>10.10.1.1</address>
      <port>22</port>
      <protocol>TCP</protocol>
      <state>open</state>
      <service>ssh</service>
      <banner>OpenSSH/4.3</banner>
    </portScanResult>
  </portScanResults>
  <vulnerabilities>
    <vulnerability>
      <vulID>VUL-OPENSSH-BYPASS</vulID>
      <orgVulId>CVE-2006-5051</orgVulId>
      <vulLevel>3</vulLevel>
      <vulName>OpenSSH 安全限制绕过漏洞</vulName>
      <vulDesc>OpenSSH 4.x 存在安全限制绕过，可能导致未授权访问。</vulDesc>
      <instances>
        <instance>
          <vulInfoID>VI-20260518-0001</vulInfoID>
          <targetId>TGT-001</targetId>
          <vulInfoStat>1</vulInfoStat>
          <vulPort>22</vulPort>
          <vulSvc>ssh</vulSvc>
          <transferTime>1747476000</transferTime>
          <evidence>
            <protocol>TCP</protocol>
            <message>OpenSSH/4.3</message>
          </evidence>
        </instance>
        <instance>
          <vulInfoID>VI-20260518-0002</vulInfoID>
          <targetId>TGT-002</targetId>
          <vulInfoStat>1</vulInfoStat>
          <vulPort>22</vulPort>
          <transferTime>1747476100</transferTime>
        </instance>
      </instances>
    </vulnerability>
    <vulnerability>
      <vulID>VUL-SSL-WEAK</vulID>
      <orgVulId>CVE-2014-3566</orgVulId>
      <vulLevel>2</vulLevel>
      <vulName>SSLv3 POODLE 漏洞</vulName>
      <vulDesc>服务支持 SSLv3，存在 POODLE 攻击风险。</vulDesc>
      <instances>
        <instance>
          <vulInfoID>VI-20260518-0003</vulInfoID>
          <targetId>TGT-001</targetId>
          <vulInfoStat>1</vulInfoStat>
          <vulPort>443</vulPort>
          <vulSvc>https</vulSvc>
          <transferTime>1747476200</transferTime>
        </instance>
      </instances>
    </vulnerability>
  </vulnerabilities>
</TaskExport>
```

字段说明以 §5.8.4–§5.8.7 为准。

**修复核验扫描外发**（`exportStage=VERIFY_FIX_SCAN`，`dataType=SYSTEM_VULNERABILITY`）：

```json
{
  "taskExport": {
    "export": {
      "exportId": "EXP-VERIFY-FIX-20260518-001",
      "format": "json",
      "exportStage": "VERIFY_FIX_SCAN",
      "dataType": "SYSTEM_VULNERABILITY",
      "generatedAt": "2026-05-18T15:05:00Z",
      "recordCount": 1
    },
    "vulnerabilities": [
      {
        "vulID": "VUL-OPENSSH-BYPASS",
        "orgVulId": "CVE-2006-5051",
        "vulLevel": 3,
        "vulName": "OpenSSH 安全限制绕过漏洞",
        "vulDesc": "OpenSSH 4.x 存在安全限制绕过。",
        "instances": [
          {
            "vulInfoID": "VI-20260518-0001",
            "targetId": "TGT-001",
            "vulInfoStat": 6,
            "vulNetAddr": "10.10.1.1",
            "vulPort": 22,
            "transferTime": "1747488000"
          }
        ]
      }
    ]
  }
}
```

### 7.3 获取方式

1. 订阅 `EXPORT_READY` → 使用 `downloadUrl` 或 `GET /exports/{exportId}/download`
2. 或轮询 `GET /tasks/{taskId}/exports` 直至出现 `status=READY`

---

## 8. 能力码（Capability）

| 能力码 | 说明 |
|--------|------|
| `TASK_WRITE` | 创建任务 |
| `TASK_READ` | 查询任务 |
| `INSTANCE_READ` | 查询实例 |
| `INSTANCE_VERIFY` | 验证 |
| `INSTANCE_REMEDIATE` | 处置（含已修复与修复失败） |
| `INSTANCE_VERIFY_FIX` | 修复核验 |
| `EXPORT_READ` | 查询/下载外发包 |
| `EVENT_SUBSCRIBE` | 接收 Webhook（须在平台登记回调 URL） |

未开通的能力调用将返回 **`40301`**。

---

## 9. 业务错误码

| code | 含义 | 处理建议 |
|------|------|----------|
| 0 | 成功 | — |
| 40001 | 参数校验失败 | 检查请求体 |
| 40002 | 状态机不允许 | 核对当前 `vulInfoStat` |
| 40003 | 资源不存在 | 检查 ID |
| 40004 | 枚举/码表非法 | 对照附录状态表 |
| 40005 | 修复与备案互斥 | 勿重复处置 |
| 40101 | 鉴权失败 | 检查 Token/签名 |
| 40301 | 能力未开通 | 联系运营开通 |
| 40901 | 幂等冲突 | 使用已返回的 `taskId` |
| 42901 | 限流 | 退避重试 |
| 50001 | 引擎调用失败 | 稍后重试或联系平台 |
| 50002 | 回调投递失败 | 平台异步重试；检查 Partner 接收端 |

---

## 10. 典型集成流程

```text
1. POST /tasks（extTaskId 幂等）→ 保存 taskId
2. 轮询 GET /tasks/{taskId} 或等待 Webhook TASK_COMPLETED
3. 收到 EXPORT_READY → GET /exports/{exportId}/download → 按 `format` 解析 XML 或 JSON
4. POST /instances/search?taskId=... → 入库漏洞实例
5. 业务侧处置后：
   - POST .../verify（有效/误报）
   - POST .../remediate（含修复失败 →9）
   - POST .../verify-fix
6. 若 verify / verify-fix 触发扫描，继续接收 EXPORT_READY，按 `exportStage` 识别验证扫描或修复核验扫描外发
7. 可选：订阅 `INSTANCE_VERIFY_FIX_COMPLETED` / `EXPORT_READY` 等事件驱动 ITSM 工单
```

---

## 附录 A · 漏洞实例状态 `vulInfoStat`

| 值 | 说明 | 阶段 |
|----|------|------|
| 0 | 潜在预警 | 预警 |
| 1 | 初始发现 | 识别 |
| 2 | 已验证有效 | 识别 |
| 3 | 已验证误报 | 终态 |
| 5 | 已修复 | 修复 |
| 6 | 核验修复 | 修复 |
| 7 | 核验未修复 | 识别 |
| 8 | 验证失败 | 识别 |
| 9 | 修复失败（备案） | 识别 |
| 10 | 核验失败 | 识别 |

---

## 附录 B · 相关资源

| 资源 | 路径 |
|------|------|
| OpenAPI 3.1 | [`openapi/v1/openapi.yaml`](../../openapi/v1/openapi.yaml) |

**本地预览**（Redocly CLI 2.x）：`npx @redocly/cli build-docs openapi/v1/openapi.yaml -o openapi/v1/api-docs.html`，用浏览器打开生成的 HTML。需要 **Node.js ≥ 20.19**。亦可使用 https://editor.swagger.io 导入该 YAML。

文档问题请联系平台集成对接人（`partnerId` 对应运营渠道）。
