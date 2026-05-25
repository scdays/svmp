# 网络安全漏洞管理平台 · 开放平台 API 接口规范

| 项        | 内容                                                         |
| --------- | ------------------------------------------------------------ |
| API 版本  | **1.0.3**                                                    |
| 协议      | HTTPS · REST JSON                                            |
| Base Path | `/api/open/v1`                                               |
| OpenAPI   | [`openapi/v1/openapi.yaml`](../../openapi/v1/openapi.yaml)（OpenAPI 3.1，可导入 Swagger UI / Postman / 代码生成） |
| 适用对象  | 已完成 Partner 注册的第三方系统（SIEM、ITSM、资产平台、安全运营系统等） |

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
- [附录 A · 漏洞实例状态 `vulInfoStat`](#附录-a--漏洞实例状态-vulinfostat)
- [附录 B · 相关资源](#附录-b--相关资源)
- [附录 C · 平台用户角色](#附录-c--平台用户角色-srctktrole--dsttktrole)
- [附录 D · 漏洞管理处置方式](#附录-d--漏洞管理处置方式-srcmethod)
- [附录 E · 未修复原因](#附录-e--未修复原因-lvrsn)
- [附录 F · 任务类型](#附录-f--任务类型-type)
- [附录 G · 扫描任务配置文件 `file`](#附录-g--扫描任务配置文件-file)
- [附录 H · 扫描模板与报告模板](#附录-h--扫描模板与报告模板)
- [附录 I · 部侧排查扩展参数](#附录-i--部侧排查扩展参数)
- [附录 J · 接入 FAQ](#附录-j--接入-faq)
- [修订记录](#修订记录)

---

## 1. 概述

### 1.1 能力范围

第三方通过**开放平台 API** 可完成：

| 能力             | 说明                                                         |
| ---------------- | ------------------------------------------------------------ |
| 扫描/排查        | 创建任务、查询进度与结果摘要                                 |
| 漏洞实例         | 查询、验证、处置（含修复与修复失败/备案）、修复核验          |
| 扫描结果数据外发 | 任务结束、验证扫描、修复核验扫描完成后下载结构化结果（支持 XML / JSON 两种输出物） |
| 事件通知         | 平台向 Partner 回调 URL 推送任务/实例/外发就绪事件           |

扫描与漏洞检测由平台内部扫描执行层完成；Partner **不直接调用**扫描器或底层扫描接口。

### 1.2 集成架构

```text
┌─────────────────────┐         HTTPS REST          ┌──────────────────────────┐
│  第三方系统 Partner  │ ◀────────────────────────▶ │  漏洞管理平台 · 开放平台   │
│  Partner 系统          │         Webhook POST         │  /api/open/v1            │
└─────────────────────┘ ◀────────────────────────── └──────────────────────────┘
```

### 1.3 漏洞实例生命周期（写接口）

本节说明**会改变业务状态**的写操作数量与顺序；完整路径清单见 [§5.0](#50-接口总览)。

#### 1.3.1 状态流转（业务语义）

```text
排查（创建任务，见 §1.3.2）
    → 实例默认 vulInfoStat = 1（初始发现）
验证（POST .../verify）
    → 2 已验证有效  |  3 已验证误报（终态，不可再处置）
处置（POST .../remediate）
    → 5 已修复  |  9 修复失败/备案（同一接口，由请求体区分）
修复核验（POST .../verify-fix）
    → 平台异步核验扫描；完成后 → 6 / 7 / 10（Webhook 见 §6）
```

#### 1.3.2 写接口数量对照

| 分类 | 业务步骤 | HTTP 方法 · 路径 | 数量 | 说明 |
|------|----------|------------------|:----:|------|
| **任务写** | 创建排查任务 | `POST /tasks/file` **或** `POST /tasks/vul` | **2 路径，二选一** | 不属于实例写接口；产生 `taskId` 与实例 |
| **实例写** | ① 验证 | `POST /instances/{vulInfoID}/verify` | 1 | 同步受理 |
| | | `POST /instances/verify:batch` | 1 | 批量，与单条语义相同 |
| | ② 处置 | `POST /instances/{vulInfoID}/remediate` | 1 | 含修复成功与修复失败/备案 |
| | | `POST /instances/remediate:batch` | 1 | 批量 |
| | ③ 修复核验 | `POST /instances/{vulInfoID}/verify-fix` | 1 | 异步；终态靠 Webhook 或轮询 |
| | | `POST /instances/verify-fix:batch` | 1 | 批量 |

**计数口径**：

- **实例生命周期写操作** = **3 类业务动作**（验证 → 处置 → 修复核验），对应 **6 个 HTTP 路径**（每类含单条 + 批量）。
- **含排查任务创建**时，再加 **2 个创建路径（二选一）**，共 **8 个写路径**。
- **读接口**（`GET /tasks/{taskId}`、`POST /instances/search` 等）不改变状态，不计入上表。

---

## 2. 接入准备

### 2.1 开通材料

接入前由平台运营分配：

| 配置项           | 说明                                                                                          |
| ---------------- | --------------------------------------------------------------------------------------------- |
| `partnerId`      | 接入方唯一标识                                                                                |
| 鉴权凭证         | `clientId` + `clientSecret`（或运营预发 Token）；换取 `accessToken` 见 [§3.1.1](#311-获取-access-token) |
| `capabilities`   | 已开通的能力码列表（见 §8）                                                                   |
| 回调地址         | 默认 `callbackUrl`（可在创建任务时覆盖）                                                      |
| IP 白名单 / mTLS | 按安全要求可选                                                                                |

### 2.2 环境地址

| 环境 | 业务 API Base URL                | 认证服务 Base URL（示例）                                      |
| ---- | -------------------------------- | -------------------------------------------------------------- |
| 测试 | `https://{测试域名}/api/open/v1` | `https://{测试认证域名}`（运营提供，**通常不同于**业务域名） |
| 生产 | `https://{生产域名}/api/open/v1` | `https://{生产认证域名}`                                       |

实际域名以平台运营开通材料为准。**获取 Token 不在 `/api/open/v1` 路径下。**

---

## 3. 鉴权与安全

### 3.1 Bearer Token（调用业务 API）

**v1.0.3 唯一支持的 REST 鉴权方式。** 业务接口（`/api/open/v1/*`）请求头：

```http
Authorization: Bearer <accessToken>
Content-Type: application/json
```

`accessToken` 须先通过 [§3.1.1](#311-获取-access-token) 换取；有效期与刷新策略以运营开通说明为准。

### 3.1.1 获取 access Token

Token 由**平台认证/登录服务**签发（OAuth 2.0 Client Credentials），**不属于**开放平台业务 Base Path `/api/open/v1`。

| 项 | 说明 |
|----|------|
| 调用方 | Partner 服务端（勿在前端暴露 `clientSecret`） |
| 凭证来源 | 运营开通时分配的 `clientId`、`clientSecret`（与 `partnerId` 绑定） |
| 端点（二选一，以开通材料为准） | 标准：`POST {authBaseUrl}/oauth/token`；简化：`POST {authBaseUrl}/api/partners/token` |
| `{authBaseUrl}` | 认证服务根地址，见 [§2.2](#22-环境地址) 开通材料 |

**标准 OAuth 2.0 Client Credentials 请求**

```http
POST /oauth/token HTTP/1.1
Host: {authBaseUrl}
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id={clientId}&client_secret={clientSecret}
```

**标准响应**

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**简化 JSON 端点请求**（部分环境提供）

```http
POST /api/partners/token HTTP/1.1
Host: {authBaseUrl}
Content-Type: application/json

{
  "grantType": "client_credentials",
  "clientId": "cli_abc123",
  "clientSecret": "***"
}
```

**简化响应**

```json
{
  "accessToken": "eyJ...",
  "tokenType": "Bearer",
  "expiresIn": 86400,
  "partnerId": "partner-demo-01"
}
```

| 项 | 约定 |
|----|------|
| 使用方式 | 将 `access_token` / `accessToken` 填入业务请求 `Authorization: Bearer ...` |
| 过期 | `expires_in` / `expiresIn` 秒；到期前重新调用 Token 端点换取新 Token |
| 失败 | HTTP 401 + 业务码或 OAuth `error` 字段；勿用过期 Token 重试业务写接口 |

> OpenAPI 文件（`openapi/v1/openapi.yaml`）仅描述 `/api/open/v1` 业务契约；Token 端点见本节及运营开通手册。

### 3.2 方式二：API Key + 签名（暂未开放）

`X-Api-Key` + `X-Signature`（HMAC-SHA256）鉴权**不在 v1.0.3 范围内**；调用 REST API 须使用 §3.1 Bearer Token。该方式计划于后续版本提供。

### 3.3 Webhook 验签（与 REST 无关）

**Partner 调用开放平台 REST API 时不需要 Webhook 验签，平台也不会因每次 REST 调用而回调 Partner。**

Webhook 验签仅当**平台向 Partner 登记的 `callbackUrl` 推送异步事件**（§6）时，由 Partner 在**接收端**校验 `X-Webhook-Signature` 等请求头。详细步骤见 [§6.0 Partner 接收端验签](#60-partner-接收端验签)。

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

| 字段        | 说明                            |
| ----------- | ------------------------------- |
| `code`      | `0` 成功；非 0 见 §9            |
| `message`   | 描述信息                        |
| `data`      | 成功时业务数据；失败多为 `null` |
| `requestId` | 排障追踪 ID，建议日志留存       |

### 4.2 幂等

#### 创建任务

| 场景     | 约定                                                                                         |
| -------- | -------------------------------------------------------------------------------------------- |
| 业务键   | 请求体 **必填** `extTaskId`（Partner 侧唯一，用于业务幂等）                                  |
| 请求头   | **可选** `Idempotency-Key`（HTTP 传输层幂等，防重复 POST）                                   |
| 去重规则 | 实现幂等时 **二者提供其一即可**，无需同时依赖；**若同时提供，平台优先按 `extTaskId` 判重** |
| 重复提交 | 相同 `extTaskId` 或相同 `(partnerId, Idempotency-Key)` → **40901** 或 **200** 且返回已有 `taskId` |

> **说明**：§5.1.1 示例同时携带 `extTaskId` 与 `Idempotency-Key` 为**合法写法**——前者为必填业务键，后者为可选增强；并非「只能填其中一个字段」。

#### 实例写操作（verify / remediate / verify-fix）

同一实例在生命周期内会**多次**合法写操作（验证 → 处置 → 修复核验；或核验未修复后再次处置）。幂等键标识的是**某一次具体写请求**，用于吸收网络重试，**不应**在 Partner 侧对「实例 + 动作」固定写死为永久唯一值。

| 项                   | 约定                                                         |
| -------------------- | ------------------------------------------------------------ |
| 推荐格式             | `Idempotency-Key: {动作}:{vulInfoID}:{clientRequestId}`      |
| `{动作}`             | `verify` / `remediate` / `verify-fix`                        |
| `{clientRequestId}`  | Partner 为**本次**调用生成的 UUID 或单调递增序号；每次新意图须使用新 ID |
| 平台去重             | 按 `(partnerId, Idempotency-Key)` 缓存首次响应，默认保留 **24 小时**（租户可配置） |
| 相同 Key + 相同 body | 视为重试，返回首次 `code` 与 `data`                          |
| 相同 Key + 不同 body | **40901**                                                    |
| Key 过期后           | 按新业务请求处理；若状态机不允许则 **40002** / **40005**     |

**设计说明**：平台**不**以时间窗口代替状态机——幂等解决「重复提交同一请求」；「能否再次处置/核验」由 `vulInfoStat` 与 **40005** 等业务码约束。时间窗口仅控制幂等记录占用时长，避免 Partner 重试 ID 无限堆积。

**示例**

```http
# 首次验证 VI-001（clientRequestId=req-001）
Idempotency-Key: verify:VI-20260517-0001:req-001

# 网络超时后重试（同一 req-001）→ 返回首次结果
Idempotency-Key: verify:VI-20260517-0001:req-001

# 核验未修复后再次处置（新意图，须新 ID）
Idempotency-Key: remediate:VI-20260517-0001:req-002
```

#### 批量实例写

批量接口的 `Idempotency-Key` 作用在**整批请求**上，而非每条 `items[]`。

| 项                | 约定                                                         |
| ----------------- | ------------------------------------------------------------ |
| 推荐格式          | `{动作}:batch:{clientBatchId}`，如 `remediate:batch:550e8400-e29b-41d4-a716-446655440000` |
| `{clientBatchId}` | Partner 为本批次生成的 UUID；批次重试时使用**同一** batchId 与 Key |
| 平台行为          | 相同批次 Key 重放时返回**首次** `success` / `failed` 拆分结果 |
| body 一致性       | 重放时 `items[]` 条数、顺序及每条字段须与首次一致；否则 **40901** |
| 与单条互斥        | 单条路径接口与 `:batch` 接口**不可**共用同一 `Idempotency-Key` |

```http
POST /api/open/v1/instances/remediate:batch HTTP/1.1
Idempotency-Key: remediate:batch:batch-20260518-001

{ "items": [ { "vulInfoID": "VI-...", ... }, ... ] }
```

### 4.3 分页与时间

| 项                  | 约定                                    |
| ------------------- | --------------------------------------- |
| 分页                | `page` 从 1 起；`size` 最大 1000        |
| 时间                | ISO 8601 UTC，如 `2026-05-18T08:00:00Z` |
| 实例 `transferTime` | 部侧常见为 **Unix 秒字符串**            |

### 4.4 字段命名

漏洞实例字段与部侧表34 **同名**，例如：`vulInfoID`、`vulInfoStat`、`vulName`、`vulNetAddr`、`remedDesc`、`srcMethod` 等。第三方对接报送系统时可减少字段转换。

---
## 5. REST API

> 路径均相对于 Base Path `/api/open/v1`。  
> 下文「—」表示该项无参数。

### 5.0 接口一览

| 阶段     | 方法 | 路径                                | 能力码                |
| -------- | ---- | ----------------------------------- | --------------------- |
| 排查     | POST | `/tasks/file`                       | `TASK_WRITE`          |
| 排查     | POST | `/tasks/vul`                        | `TASK_WRITE`          |
| 排查     | GET  | `/tasks`                            | `TASK_READ`           |
| 排查     | GET  | `/tasks/{taskId}`                   | `TASK_READ`           |
| 查询     | POST | `/instances/search`                 | `INSTANCE_READ`       |
| 查询     | GET  | `/instances/{vulInfoID}`            | `INSTANCE_READ`       |
| 验证     | POST | `/instances/{vulInfoID}/verify`     | `INSTANCE_VERIFY`     |
| 验证     | POST | `/instances/verify:batch`           | `INSTANCE_VERIFY`     |
| 处置     | POST | `/instances/{vulInfoID}/remediate`  | `INSTANCE_REMEDIATE`  |
| 处置     | POST | `/instances/remediate:batch`        | `INSTANCE_REMEDIATE`  |
| 修复核验 | POST | `/instances/{vulInfoID}/verify-fix` | `INSTANCE_VERIFY_FIX` |
| 修复核验 | POST | `/instances/verify-fix:batch`       | `INSTANCE_VERIFY_FIX` |
| 外发     | GET  | `/exports/{exportId}`               | `EXPORT_READ`         |
| 外发     | GET  | `/exports/{exportId}/download`      | `EXPORT_READ`         |
| 外发     | GET  | `/tasks/{taskId}/exports`           | `EXPORT_READ`         |

**写接口生命周期**：排查 → 验证 → 处置（`remediate`，含已修复与修复失败）→ 修复核验。

### 5.0.1 文档体例

各接口按下列块描述：**路径参数** · **查询参数** · **请求头** · **请求体** · **响应 data** · **状态约束** · **示例**。

#### 表格列名约定

全文表格按场景使用固定列名，避免混用：

| 场景 | 表头 | 适用章节 |
|------|------|----------|
| 接口元信息 | `项` · `值` | 各接口开头的「能力 / 说明」块 |
| 约定与约束 | `项` · `约定` | §4.2 幂等、§5 重要约定等 |
| REST 参数字段 | `参数` · `类型` · `必填` · `说明` | §5 请求体/响应体/查询参数（**标准体例**） |
| 简化结构 | `字段` · `类型` · `说明` | §4.1 响应包装、§6.1 Webhook 公共体等 |
| 外发 XML/JSON 映射 | `JSON 路径` · `XML 路径` · `类型` · `必填` · `说明` | §7 扫描结果外发 |

**必填列取值**：`✓` 必填 · `○` 可选 · `条件` 条件必填。

**通用请求头**（写接口建议携带）：

| 参数            | 类型   | 必填 | 说明                                                                               |
| --------------- | ------ | :--: | ---------------------------------------------------------------------------------- |
| Authorization   | string |  ✓   | `Bearer <accessToken>`（见 §3.1、§3.1.1）                                          |
| Content-Type    | string |  ✓   | `application/json`                                                                 |
| Idempotency-Key | string |  ○   | 写操作幂等，见 §4.2；创建任务可选，与 `extTaskId` 去重规则见 §4.2                  |

**重要约定**：

| 项         | 约定                                                         |
| ---------- | ------------------------------------------------------------ |
| 任务键     | **仅创建任务**使用 `extTaskId`；查进度、拉实例仅使用平台返回的 **`taskId`** |
| 实例写操作 | 均以路径 **`vulInfoID`** 定位，**不使用** `extTaskId` / `taskId` |
| 实例搜索   | `taskId` / `extTaskId` 在 **请求体** 中传递；勿传冲突值      |

---

### 5.1 任务 · 排查/扫描

#### 5.1.1 `POST /tasks/file` — 创建扫描任务（XML 配置）

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 能力 | `TASK_WRITE`                                                 |
| 说明 | 基于 **`file` XML 配置** 创建扫描任务；`type` **1 / 2 / 3** 均可。任务名称、扫描目标与扫描策略写在 XML `<server>` 内；登陆检查信息写在根级 `<targets>`（始终存在，可为空）；并 **二选一**：引用平台模板 ID，或内联扫描阶段 + `<report>`，见 [附录 G](#附录-g--扫描任务配置文件-file) / [附录 H](#附录-h--扫描模板与报告模板) |

**路径参数**：— · **查询参数**：—

**请求体**：

| 参数      | 类型   | 必填 | 说明                                                         |
| --------- | ------ | :--: | ------------------------------------------------------------ |
| extTaskId | string |  ✓   | Partner 幂等键                                               |
| type      | int    |  ✓   | 任务类型，见 [附录 F](#附录-f--任务类型-type)（**1** / **2** / **3**） |
| file      | string |  ✓   | 任务配置 XML（UTF-8）；根元素 `<scanTask>`，须含 `<server>` 与根级 `<targets>`，见 [附录 G](#附录-g--扫描任务配置文件-file) |

**响应 data**：

| 参数      | 类型     | 必填 | 说明                               |
| --------- | -------- | :--: | ---------------------------------- |
| extTaskId | string   |  ✓   | 回显                               |
| taskId    | string   |  ✓   | 平台任务 ID（后续均用此字段）      |
| status    | enum     |  ✓   | `ACCEPTED` / `QUEUED` / `REJECTED` |
| createdAt | datetime |  ✓   | 创建时间                           |
| message   | string   |  ○   | `REJECTED` 时原因                  |

**状态约束**：相同 `extTaskId` 重复提交 → **40901** 或 **200** 且返回已有 `taskId`；`type` 非法 → **40004**；`file` 不符合 [附录 G](#附录-g--扫描任务配置文件-file) → **40001**。

**请求示例（WEB 应用扫描）**

```http
POST /api/open/v1/tasks/file HTTP/1.1
Authorization: Bearer <accessToken>
Content-Type: application/json
Idempotency-Key: idem-ext-2026-web-0001

{
  "extTaskId": "EXT-TASK-2026-WEB-0001",
  "type": 2,
  "file": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><scanTask>...</scanTask>"
}
```

> **幂等说明**：本示例同时包含必填 `extTaskId` 与可选 `Idempotency-Key`，均为合法写法；平台优先按 `extTaskId` 判重（见 §4.2）。

**响应示例（成功）**

```json
{
  "code": 0,
  "message": "ok",
  "requestId": "req-20260518-w001",
  "data": {
    "extTaskId": "EXT-TASK-2026-WEB-0001",
    "taskId": "TASK-a1b2c3d4",
    "status": "ACCEPTED",
    "createdAt": "2026-05-18T08:00:00Z"
  }
}
```

---

#### 5.1.2 `POST /tasks/vul` — 创建扫描任务（JSON）

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 能力 | `TASK_WRITE`                                                 |
| 说明 | `type` **1 / 2 / 3** 均可；传入结构化目标与平台模板 ID（`scanTemplateId`、`reportTemplateId`），见 [附录 H](#附录-h--扫描模板与报告模板)。JSON 请求不支持内联模板，XML 配置见 §5.1.1 |

**路径参数**：— · **查询参数**：—

**请求体**：

| 参数              | 类型     | 必填 | 说明                                                         |
| ----------------- | -------- | :--: | ------------------------------------------------------------ |
| extTaskId         | string   |  ✓   | Partner 幂等键                                               |
| taskName          | string   |  ✓   | 任务名称                                                     |
| type              | int      |  ✓   | 任务类型，见 [附录 F](#附录-f--任务类型-type)（**1** / **2** / **3**） |
| targets           | object   |  ✓   | 扫描目标；含 `hosts`（地址列表）与 `auth`（登陆凭据），见下表 |
| scanTemplateId    | int      |  ○   | 平台扫描模板 ID（[附录 H.1](#h1-扫描模板-scantemplateid)）；缺省 **`0`** 按 `type` 自动匹配 |
| reportTemplateId  | int      |  ○   | 平台报告模板 ID（[附录 H.2](#h2-报告模板-reporttemplateid)）；**缺省 `0`** 按 `type` 自动匹配 |
| callbackUrl       | string   |  ○   | 覆盖 Partner 默认回调 URL                                    |
| priority          | enum     |  ○   | `LOW` / `MEDIUM` / `HIGH`                                    |
| srcMethod         | int      |  ○   | 技术处置方式，见 [附录 D](#附录-d--漏洞管理处置方式-srcmethod)、[附录 I](#附录-i--部侧排查扩展参数) |
| vulIDs            | string[] |  ○   | 产品漏洞 ID 列表（部侧 `vulID`）；**预留**，后续开放查询接口 |
| secResourceHashes | string[] |  ○   | 安全资源设备 hash 列表（扫描器）；**预留**，后续开放查询接口 |

**`targets` 对象**

| 参数  | 类型   | 必填 | 说明                                                         |
| ----- | ------ | :--: | ------------------------------------------------------------ |
| hosts | string |  ✓   | 扫描目标 ip / domain / url；多个以 **`,` 或 `;`** 分隔（同 XML `<server><targets>`） |
| auth  | array  |  ○   | 登陆检查凭据；无登陆检查时省略或 `[]`。元素字段见下表        |

**`targets.auth[]` 元素**

| 参数      | 类型   | 必填 | 说明                                                         |
| --------- | ------ | :--: | ------------------------------------------------------------ |
| ip        | string |  ✓   | 目标 IP（IPv4/IPv6）                                         |
| protocol  | string |  ○   | 登陆协议：`SSH` / `SMB` / `Telnet` / `RDP` 等                |
| port      | int    |  ○   | 登陆端口 **0–65535**                                         |
| username  | string |  ○   | 登陆用户名                                                   |
| password  | string |  ○   | 登陆密码（明文；传输须 HTTPS，平台侧加密存储）               |
| jumpHosts | array  |  ○   | 跳转机列表，元素含 `ip` / `protocol` / `port` / `username` / `password` |

> **IPv6 提示**：`hosts` 含 IPv6 时，写法多样（全写、压缩、`[]` 包裹等）。Partner 入参与平台响应/外发回显的字符串形式**可能不一致**。建议统一采用 **RFC 5952 规范格式**（全小写、最长零压缩，如 `2001:db8::1`），并在联调阶段比对「请求 `targets.hosts` ↔ 任务详情 ↔ 外发 `targets[]`」是否一致。

**响应 data**：

| 参数      | 类型     | 必填 | 说明                               |
| --------- | -------- | :--: | ---------------------------------- |
| extTaskId | string   |  ✓   | 回显                               |
| taskId    | string   |  ✓   | 平台任务 ID（后续均用此字段）      |
| status    | enum     |  ✓   | `ACCEPTED` / `QUEUED` / `REJECTED` |
| createdAt | datetime |  ✓   | 创建时间                           |
| message   | string   |  ○   | `REJECTED` 时原因                  |

**状态约束**：相同 `extTaskId` 重复提交 → **40901** 或 **200** 且返回已有 `taskId`。`scanTemplateId` / `reportTemplateId` 匹配规则见 [附录 H](#附录-h--扫描模板与报告模板)。

**请求示例**

```http
POST /api/open/v1/tasks/vul HTTP/1.1
Authorization: Bearer <accessToken>
Content-Type: application/json
Idempotency-Key: idem-ext-2026-0001

{
  "extTaskId": "EXT-TASK-2026-0001",
  "taskName": "2026Q2-核心业务系统排查",
  "type": 1,
  "targets": {
    "hosts": "10.10.1.2",
    "auth": [
      {
        "ip": "10.65.195.204",
        "protocol": "SSH",
        "port": 22,
        "username": "root",
        "password": "Gp+CdzxD",
        "jumpHosts": [
          {
            "ip": "10.65.195.204",
            "protocol": "SSH",
            "port": 22,
            "username": "root",
            "password": "Gp+CdzxD"
          }
        ]
      }
    ]
  },
  "scanTemplateId": 1001,
  "reportTemplateId": 2001,
  "srcMethod": 1021,
  "vulIDs": ["MVM-2019-1696145560773468160"],
  "secResourceHashes": ["8f3a2b1c9d4e5f60718293a4b5c6d7e8"],
  "callbackUrl": "https://partner.example.com/hooks/vuln",
  "priority": "HIGH"
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

#### 5.1.3 `GET /tasks/{taskId}` — 查询任务进度

| 项   | 值                                          |
| ---- | ------------------------------------------- |
| 能力 | `TASK_READ`                                 |
| 说明 | **仅需**路径 `taskId`，**无需** `extTaskId` |

**路径参数**：

| 参数   | 类型   | 必填 | 说明                        |
| ------ | ------ | :--: | --------------------------- |
| taskId | string |  ✓   | 创建任务响应中的平台任务 ID |

**响应 data**：

| 参数         | 类型     | 必填 | 说明                                          |
| ------------ | -------- | :--: | --------------------------------------------- |
| extTaskId    | string   |  ○   | 回显（来自映射表，非请求入参）                |
| taskId       | string   |  ✓   | 平台任务 ID                                   |
| status       | enum     |  ✓   | `PENDING` / `RUNNING` / `FINISHED` / `FAILED` |
| progress     | int      |  ○   | 0–100                                         |
| startedAt    | datetime |  ○   | 开始时间                                      |
| finishedAt   | datetime |  ○   | 结束时间                                      |
| errorMessage | string   |  ○   | 失败原因                                      |

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

#### 5.1.4 `GET /tasks` — 分页查询任务列表

| 项   | 值          |
| ---- | ----------- |
| 能力 | `TASK_READ` |

**查询参数**：

| 参数        | 类型     | 必填 | 说明                                          |
| ----------- | -------- | :--: | --------------------------------------------- |
| extTaskId   | string   |  ○   | 按 Partner 键过滤（平台库，不调引擎）         |
| status      | enum     |  ○   | `PENDING` / `RUNNING` / `FINISHED` / `FAILED` |
| createdFrom | datetime |  ○   | 创建时间起（含）                              |
| createdTo   | datetime |  ○   | 创建时间止（含）                              |
| page        | int      |  ✓   | 从 1 开始                                     |
| size        | int      |  ✓   | ≤1000                                         |

**响应 data**：

| 参数  | 类型  | 必填 | 说明         |
| ----- | ----- | :--: | ------------ |
| page  | int   |  ✓   | 当前页       |
| size  | int   |  ✓   | 每页条数     |
| total | int   |  ✓   | 总记录数     |
| items | array |  ✓   | 任务摘要列表 |

**items[] 元素**：

| 参数                   | 类型     | 必填 | 说明                             |
| ---------------------- | -------- | :--: | -------------------------------- |
| taskId                 | string   |  ✓   | **后续查进度、拉实例均用此字段** |
| extTaskId              | string   |  ○   | Partner 幂等键                   |
| taskName               | string   |  ✓   | 任务名称                         |
| status                 | enum     |  ✓   | 任务状态                         |
| progress               | int      |  ○   | 0–100                            |
| startedAt / finishedAt | datetime |  ○   | 起止时间                         |
| errorMessage           | string   |  ○   | 失败原因                         |
| createdAt              | datetime |  ✓   | 创建时间                         |

---

### 5.2 漏洞实例 · 查询

#### 5.2.1 `POST /instances/search` — 分页搜索

| 项   | 值                                      |
| ---- | --------------------------------------- |
| 能力 | `INSTANCE_READ`                         |
| 说明 | 建议至少传 `taskId` 或 `extTaskId` 之一 |

**查询参数**：

| 参数          | 类型   | 必填 | 说明                        |
| ------------- | ------ | :--: | --------------------------- |
| exportProfile | string |  ○   | `MIIT-2025`：部侧扩展字段档 |

**请求体**：

| 参数            | 类型   | 必填 | 说明                                        |
| --------------- | ------ | :--: | ------------------------------------------- |
| taskId          | string |  ○   | 平台任务 ID                                 |
| extTaskId       | string |  ○   | 平台解析为 taskId；**勿与 taskId 传冲突值** |
| vulInfoStatList | int[]  |  ○   | 状态过滤；空表示不过滤                      |
| vulLevelList    | int[]  |  ○   | 危害等级过滤                                |
| page            | int    |  ✓   | 从 1 开始                                   |
| size            | int    |  ✓   | ≤1000                                       |

**响应 data.items[]**（列表标准字段）：

| 参数           | 类型   | 必填 | 说明                                               |
| -------------- | ------ | :--: | -------------------------------------------------- |
| vulInfoID      | string |  ✓   | 系统漏洞实例 ID                                    |
| vulID          | string |  ○   | 产品漏洞编号                                       |
| vulInfoStat    | int    |  ✓   | 状态（A.8）                                        |
| lvRsn          | int    |  ○   | 未修复原因，见 [附录 E](#附录-e--未修复原因-lvrsn) |
| vulName        | string |  ✓   | 漏洞名称                                           |
| vulLevel       | int    |  ○   | 危害等级                                           |
| orgVulId       | string |  ○   | 原始编号（如 CVE）                                 |
| vulNetAddr     | string |  ○   | 网络地址                                           |
| vulPort        | int    |  ○   | 端口                                               |
| vulSvc         | string |  ○   | 服务                                               |
| isAccess       | int    |  ○   | **0** 内网 / **1** 互联网                          |
| transferTime   | string |  ✓   | 状态变更时间（常为 Unix 秒字符串）                 |
| vulnDisposalId | string |  ○   | 引擎处置 ID                                        |
| extVulnRef     | string |  ○   | Partner 扩展引用                                   |

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

| 项   | 值              |
| ---- | --------------- |
| 能力 | `INSTANCE_READ` |

**路径参数**：`vulInfoID`（✓）

**响应 data**：在列表标准字段基础上增加：

| 参数                                                | 说明         |
| --------------------------------------------------- | ------------ |
| remedDesc / fixLnk / defDev / remedTime / srcMethod | 修复台账     |
| vulInstCpe、assetID、assetName 等                   | 表34 扩展    |
| archiveReason、provincialFields                     | 备案补充     |
| extVulnRef                                          | Partner 扩展 |

---

### 5.3 漏洞实例 · 验证

> **与修复核验区分**：本节确认漏洞**真假**（前置 `vulInfoStat ∈ {0,1}`）；`verify-fix` 确认**修复是否生效**（前置 `vulInfoStat = 5`）。

#### 5.3.1 `POST /instances/{vulInfoID}/verify` — 单条验证

| 项   | 值                |
| ---- | ----------------- |
| 能力 | `INSTANCE_VERIFY` |

**路径参数**：`vulInfoID`（✓）

**请求体**：

| 参数         | 类型   | 必填 | 说明                                                         |
| ------------ | ------ | :--: | ------------------------------------------------------------ |
| vulnType     | int    |  ○   | 1/2；默认取自实例                                            |
| verifyResult | enum   |  ✓   | `VALID`→**2**；`FALSE_POSITIVE`→**3**                        |
| srcMethod    | int    | 条件 | **`VALID` 时必填**，见 [附录 D](#附录-d--漏洞管理处置方式-srcmethod)（如 **1021**、**1026**） |
| transferTime | string |  ○   | 缺省服务端生成                                               |
| operator     | string |  ✓   | 操作人（审计）                                               |
| remark       | string |  ○   | 备注                                                         |

**响应 data**：

| 参数         | 类型   | 必填 | 说明             |
| ------------ | ------ | :--: | ---------------- |
| vulInfoID    | string |  ✓   | 实例 ID          |
| vulInfoStat  | int    |  ✓   | 变更后状态       |
| lvRsn        | int    |  ○   | 验证阶段通常为空 |
| transferTime | string |  ✓   | 变更时间         |
| srcMethod    | int    |  ○   | 回显处置方式     |

**状态约束**：前置 `vulInfoStat ∈ {0,1}`；**3（误报）后禁止**修复/备案。

**扫描外发**：若验证阶段触发复扫 / POC 扫描，完成后平台生成 `EXPORT_READY`（`exportStage=VERIFY_SCAN`）。外发结构按 §5.6.6 聚合；须含 `targets[]`、`liveProbeResults[]`、`vulnerabilities[]`。

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

| 项   | 值                               |
| ---- | -------------------------------- |
| 能力 | `INSTANCE_VERIFY`                |
| 说明 | 部分成功；**不使用** `extTaskId` |

**请求体**：

| 参数     | 类型   | 必填 | 说明       |
| -------- | ------ | :--: | ---------- |
| operator | string |  ✓   | 操作人     |
| items    | array  |  ✓   | 待验证列表 |

**items[] 元素**：

| 参数         | 类型   | 必填 | 说明                       |
| ------------ | ------ | :--: | -------------------------- |
| vulInfoID    | string |  ✓   | 实例 ID                    |
| vulnType     | int    |  ○   | 默认取自实例               |
| verifyResult | enum   |  ✓   | `VALID` / `FALSE_POSITIVE` |
| srcMethod    | int    | 条件 | `VALID` 时必填             |
| transferTime | string |  ○   | 本条时间                   |
| remark       | string |  ○   | 备注                       |

**响应 data**：

| 参数    | 说明                                    |
| ------- | --------------------------------------- |
| success | 成功项数组，元素结构同单条「响应 data」 |
| failed  | 失败项：`vulInfoID`、`code`、`message`  |

---

### 5.4 处置 · 修复

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 能力     | `INSTANCE_REMEDIATE`                                         |
| 前置状态 | `vulInfoStat ∈ {2, 7}`（否则 **40002**）；误报（**3**）不可处置 |
| 接口     | `POST /instances/{vulInfoID}/remediate`、`POST /instances/remediate:batch` |

验证有效或核验未修复后，回写**已修复**或**修复失败（备案）**。由请求体字段组合决定终态：

| 处置结果        | 终态 `vulInfoStat` | 条件必填                                                     |
| --------------- | ------------------ | ------------------------------------------------------------ |
| 已修复          | **5**              | `srcMethod` 为 **1050–1053**（[附录 D](#附录-d--漏洞管理处置方式-srcmethod)）；`remedDesc`、`remedTime`；**1050** 另需 `fixLnk`；**1051/1052** 另需 `defDev` |
| 修复失败 / 备案 | **9**              | `lvRsn`（[附录 E](#附录-e--未修复原因-lvrsn)）、`archiveReason` |

**工单字段（必填）**：对应部侧表56「系统漏洞修复类型日志」。`srcTktRole`、`dstTktRole` 见 [附录 C](#附录-c--平台用户角色-srctktrole--dsttktrole)；`assignerDept`、`handlerDept` **必填**；派单人 `assignerEmail` / `assignerPhone`、处置人 `handlerEmail` / `handlerPhone` **至少填一项**（部侧 `srcTktPrsn`/`dstTktPrsn` 为「部门,邮箱,电话」合并串，开放平台**不提供**该合并字段）。

同一实例仅可成功处置一次；重复调用返回 **40005**。

#### 5.4.1 `POST /instances/{vulInfoID}/remediate` — 单条处置

**请求体**：

| 参数             | 类型   | 必填 | 说明                                                         |
| ---------------- | ------ | :--: | ------------------------------------------------------------ |
| srcMethod        | int    |  ✓   | 处置方式，见 [附录 D](#附录-d--漏洞管理处置方式-srcmethod)   |
| remedDesc        | string | 条件 | →**5** 时必填：修复方案说明                                  |
| fixLnk           | string | 条件 | `srcMethod=1050` 时必填：补丁链接                            |
| defDev           | string | 条件 | `srcMethod=1051` 或 `1052` 时必填：防护/阻断设备             |
| remedTime        | string | 条件 | →**5** 时必填，格式 `数值+单位`（如 `3日`、`2周`）           |
| lvRsn            | int    | 条件 | →**9** 时必填，见 [附录 E](#附录-e--未修复原因-lvrsn)        |
| archiveReason    | string | 条件 | →**9** 时必填：企业内部备案说明                              |
| approvedBy       | string |  ○   | 备案审批人                                                   |
| recordAt         | string |  ○   | 备案时间                                                     |
| provincialFields | object |  ○   | 省侧扩展 JSON                                                |
| srcTktRole       | int    |  ✓   | 派单角色，见 [附录 C](#附录-c--平台用户角色-srctktrole--dsttktrole) |
| dstTktRole       | int    |  ✓   | 处置角色，见 [附录 C](#附录-c--平台用户角色-srctktrole--dsttktrole) |
| assignerDept     | string |  ✓   | 派单人部门                                                   |
| assignerEmail    | string | 条件 | 派单人邮箱；与 `assignerPhone` **至少填一项**                |
| assignerPhone    | string | 条件 | 派单人电话；与 `assignerEmail` **至少填一项**                |
| handlerDept      | string |  ✓   | 处置人部门                                                   |
| handlerEmail     | string | 条件 | 处置人邮箱；与 `handlerPhone` **至少填一项**                 |
| handlerPhone     | string | 条件 | 处置人电话；与 `handlerEmail` **至少填一项**                 |
| transferTime     | string |  ○   | 状态变更时间（Unix 秒字符串）；缺省由服务端生成              |
| remark           | string |  ○   | 备注                                                         |

**响应 data**：`vulInfoID`、`vulInfoStat`（**5** 或 **9**）、`lvRsn`、`transferTime`、`remedDesc` 或 `archiveReason`、`srcMethod`。

**幂等**：`Idempotency-Key: remediate:{vulInfoID}:{clientRequestId}`，见 §4.2。

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
  "srcMethod": 999,
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

#### 5.4.2 `POST /instances/remediate:batch` — 批量处置

| 项   | 值                               |
| ---- | -------------------------------- |
| 能力 | `INSTANCE_REMEDIATE`             |
| 说明 | 部分成功；**不使用** `extTaskId` |

**请求体**：

| 参数  | 类型  | 必填 | 说明       |
| ----- | ----- | :--: | ---------- |
| items | array |  ✓   | 待处置列表 |

**items[] 元素**：

| 参数             | 类型   | 必填 | 说明                                                         |
| ---------------- | ------ | :--: | ------------------------------------------------------------ |
| vulInfoID        | string |  ✓   | 实例 ID                                                      |
| srcMethod        | int    |  ✓   | 处置方式，见 [附录 D](#附录-d--漏洞管理处置方式-srcmethod)   |
| remedDesc        | string | 条件 | →**5** 时必填：修复方案说明                                  |
| fixLnk           | string | 条件 | `srcMethod=1050` 时必填：补丁链接                            |
| defDev           | string | 条件 | `srcMethod=1051` 或 `1052` 时必填：防护/阻断设备             |
| remedTime        | string | 条件 | →**5** 时必填，格式 `数值+单位`（如 `3日`、`2周`）           |
| lvRsn            | int    | 条件 | →**9** 时必填，见 [附录 E](#附录-e--未修复原因-lvrsn)        |
| archiveReason    | string | 条件 | →**9** 时必填：企业内部备案说明                              |
| approvedBy       | string |  ○   | 备案审批人                                                   |
| recordAt         | string |  ○   | 备案时间                                                     |
| provincialFields | object |  ○   | 省侧扩展 JSON                                                |
| srcTktRole       | int    |  ✓   | 派单角色，见 [附录 C](#附录-c--平台用户角色-srctktrole--dsttktrole) |
| dstTktRole       | int    |  ✓   | 处置角色，见 [附录 C](#附录-c--平台用户角色-srctktrole--dsttktrole) |
| assignerDept     | string |  ✓   | 派单人部门                                                   |
| assignerEmail    | string | 条件 | 派单人邮箱；与 `assignerPhone` **至少填一项**                |
| assignerPhone    | string | 条件 | 派单人电话；与 `assignerEmail` **至少填一项**                |
| handlerDept      | string |  ✓   | 处置人部门                                                   |
| handlerEmail     | string | 条件 | 处置人邮箱；与 `handlerPhone` **至少填一项**                 |
| handlerPhone     | string | 条件 | 处置人电话；与 `handlerEmail` **至少填一项**                 |
| transferTime     | string |  ○   | 本条状态变更时间（Unix 秒字符串）；缺省由服务端生成          |
| remark           | string |  ○   | 备注                                                         |

**响应 data**：

| 参数    | 类型  | 必填 | 说明                                       |
| ------- | ----- | :--: | ------------------------------------------ |
| success | array |  ✓   | 成功项列表，元素结构同 §5.4.1「响应 data」 |
| failed  | array |  ✓   | 失败项列表                                 |

**failed[] 元素**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| vulInfoID | string |  ✓   | 实例 ID    |
| code      | int    |  ✓   | 业务错误码 |
| message   | string |  ✓   | 错误描述   |

**幂等**：请求头 `Idempotency-Key` 见 §4.2 批量约定，如 `remediate:batch:{clientBatchId}`。

---

### 5.5 漏洞实例 · 修复核验

#### 5.5.1 `POST /instances/{vulInfoID}/verify-fix` — 单条

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 能力 | `INSTANCE_VERIFY_FIX`                                        |
| 说明 | 前置 **`vulInfoStat = 5`**；平台触发修复核验扫描，完成后推进状态并可选外发 |

**请求体**：

| 参数         | 类型   | 必填 | 说明           |
| ------------ | ------ | :--: | -------------- |
| transferTime | string |  ○   | 缺省服务端生成 |
| remark       | string |  ○   | 备注           |

**平台行为**：受理后异步执行核验扫描；`vulInfoStat` 暂保持 **5**，完成后通过 Webhook `INSTANCE_VERIFY_FIX_COMPLETED` 通知终态 **6 / 7 / 10**，并可产生 `EXPORT_READY`（`exportStage=VERIFY_FIX_SCAN`）。外发须含 `targets[]`、`liveProbeResults[]`、`portScanResults[]`、`vulnerabilities[]`（§5.6.3）。

**响应 data（受理）**：

| 参数            | 类型   | 必填 | 说明                  |
| --------------- | ------ | :--: | --------------------- |
| vulInfoID       | string |  ✓   | 实例 ID               |
| vulInfoStat     | int    |  ✓   | 受理时通常为 **5**    |
| verifyFixStatus | enum   |  ✓   | `PENDING` / `RUNNING` |
| verifyFixJobId  | string |  ○   | 核验任务 ID           |
| message         | string |  ○   | 受理说明              |

**幂等**：`Idempotency-Key: verify-fix:{vulInfoID}:{clientRequestId}`，见 §4.2。

**请求示例**

```json
{
  "transferTime": "1747488000",
  "remark": "安排复扫 POC"
}
```

---

#### 5.5.2 `POST /instances/verify-fix:batch` — 批量

| 项   | 值                               |
| ---- | -------------------------------- |
| 能力 | `INSTANCE_VERIFY_FIX`            |
| 说明 | 部分成功；**不使用** `extTaskId` |

**请求体**：

| 参数  | 类型  | 必填 | 说明       |
| ----- | ----- | :--: | ---------- |
| items | array |  ✓   | 待核验列表 |

**items[] 元素**：

| 参数         | 类型   | 必填 | 说明                                                |
| ------------ | ------ | :--: | --------------------------------------------------- |
| vulInfoID    | string |  ✓   | 实例 ID                                             |
| transferTime | string |  ○   | 本条状态变更时间（Unix 秒字符串）；缺省由服务端生成 |
| remark       | string |  ○   | 备注                                                |

**响应 data**：

| 参数    | 类型  | 必填 | 说明                                     |
| ------- | ----- | :--: | ---------------------------------------- |
| success | array |  ✓   | 成功项列表，元素见下表「success[] 元素」 |
| failed  | array |  ✓   | 失败项列表，元素见下表「failed[] 元素」  |

**success[] 元素**（与 §5.5.1「响应 data」一致）：

| 参数            | 类型   | 必填 | 说明                                              |
| --------------- | ------ | :--: | ------------------------------------------------- |
| vulInfoID       | string |  ✓   | 实例 ID                                           |
| vulInfoStat     | int    |  ✓   | 受理时通常为 **5**；异步完成后由 Webhook 通知终态 |
| verifyFixStatus | enum   |  ○   | `PENDING` / `RUNNING`                             |
| verifyFixJobId  | string |  ○   | 核验任务 ID                                       |
| transferTime    | string |  ○   | 变更时间                                          |
| message         | string |  ○   | 受理说明                                          |

**failed[] 元素**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| vulInfoID | string |  ✓   | 实例 ID    |
| code      | int    |  ✓   | 业务错误码 |
| message   | string |  ✓   | 错误描述   |

**幂等**：请求头 `Idempotency-Key` 见 §4.2 批量约定，如 `verify-fix:batch:{clientBatchId}`。

---

### 5.6 扫描结果 · 数据外发

任务扫描结束、验证阶段扫描完成、修复核验阶段扫描完成且外发组装完成后，平台推送 **`EXPORT_READY`**（§6），或通过下列接口拉取。

#### 5.6.1 输出物格式

扫描结果外发输出物由开放平台按当前接口领域模型重新组装，支持 **`xml`** 与 **`json`** 两种 `format`；根结构为 `<TaskExport>` / `taskExport`，不作为引擎原始 XML 透传。

| `format` | 下载 `Content-Type` | 输出物         | 说明                                                |
| -------- | ------------------- | -------------- | --------------------------------------------------- |
| `xml`    | `application/xml`   | 单个 XML 文档  | 根元素为 `<TaskExport>`，字段名与 JSON key 保持一致 |
| `json`   | `application/json`  | 单个 JSON 文档 | 顶层对象为 `taskExport`，字段与 XML 同构            |

**序列化约定**：

| 项       | 约定                                                         |
| -------- | ------------------------------------------------------------ |
| 字段来源 | 以本开放接口的任务、实例、处置、备案、修复核验字段为准；引擎原始字段仅进入 `evidence` / `appendices` 等扩展节点 |
| 数组     | JSON 使用数组；XML 使用复数容器 + 单数元素，如 `targets.target[]` 对应 `<targets><target>...</target></targets>` |
| 空值     | JSON 可省略或为 `null`；XML 可省略空元素                     |
| 时间     | 与 §4.3 一致，平台字段使用 ISO 8601 UTC；需要保留引擎原始时间时放入 `evidence.engineTime` |
| 弱口令   | 不输出明文密码；统一输出 `passwordMasked` 或空值             |

#### 5.6.2 外发触发场景

| `exportStage`     | 触发时机                            | `dataType`                                                   | 输出约定                                                     |
| ----------------- | ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `TASK_COMPLETED`  | 普通扫描 / 排查任务结束             | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` | 按任务启用能力输出；漏洞扫描见 §5.6.3「漏洞扫描」行          |
| `VERIFY_SCAN`     | 漏洞验证阶段触发复扫 / POC 扫描完成 | `SYSTEM_VULNERABILITY`                                       | `targets[]` + `liveProbeResults[]` + `vulnerabilities[]`（§5.6.6 聚合） |
| `VERIFY_FIX_SCAN` | 修复核验阶段触发复扫完成            | `SYSTEM_VULNERABILITY`                                       | `targets[]` + `liveProbeResults[]` + `portScanResults[]` + `vulnerabilities[]`（§5.6.6 聚合） |

`VERIFY_SCAN` / `VERIFY_FIX_SCAN` 与任务结束外发使用同一下载接口和同一 `xml` / `json` 序列化规则；区别在 `export.exportStage`。阶段扫描外发**须**包含目标与存活探测结果，漏洞实例按 §5.6.6 聚合于 `vulnerabilities[].instances[]`。

#### 5.6.3 输出物逻辑结构

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

| 任务能力     | 规范化落点                                                   | 说明                                                         |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 主机存活探测 | `targets[]` + `liveProbeResults[]`                           | `targets[]` 保存目标主数据，`liveProbeResults[]` 保存探测方式、存活状态、时延等结果 |
| 端口扫描     | `targets[]` + `portScanResults[]`                            | 端口、协议、状态、服务、Banner 等作为正式端口扫描结果输出    |
| 漏洞扫描     | `targets[]` + `liveProbeResults[]` + `portScanResults[]` + `vulnerabilities[]` | 目标、存活、端口与漏洞结果同包输出；漏洞按 **产品漏洞 `vulID`** 聚合，实例在 `instances[]` |
| 修复核验     | `targets[]` + `liveProbeResults[]` + `portScanResults[]` + `vulnerabilities[]` | `exportStage=VERIFY_FIX_SCAN`                                |

其他引擎结果参考结构的落点：

| 参考结构     | 规范化落点                                                   | 说明                                               |
| ------------ | ------------------------------------------------------------ | -------------------------------------------------- |
| Web 漏洞结果 | `targets[].site` + `vulnerabilities[].evidence.url`          | Web 站点作为目标，URL、参数、请求信息进入证据      |
| 系统综合结果 | `vulnerabilities[]` + `baselineResults[]` + `weakPasswords[]` + `appendices[]` | 漏洞、配置基线、弱口令、主机附录拆到独立集合       |
| 口令猜测结果 | `weakPasswords[]` + `vulnerabilities[]`                      | 弱口令作为独立集合，同时可关联漏洞实例 `vulInfoID` |

#### 5.6.4 输出参数（`export` / `task` / `summary`）

| JSON 路径                               | XML 路径                                 | 类型     | 必填 | 说明                                                         |
| --------------------------------------- | ---------------------------------------- | -------- | :--: | ------------------------------------------------------------ |
| `taskExport.export.exportId`            | `/TaskExport/export/exportId`            | string   |  ✓   | 外发记录 ID                                                  |
| `taskExport.export.format`              | `/TaskExport/export/format`              | enum     |  ✓   | `xml` / `json`                                               |
| `taskExport.export.reportTemplateId`    | `/TaskExport/export/reportTemplateId`    | int      |  ○   | 报告/外发模板 ID；与创建任务 `reportTemplateId` 一致，见 [附录 H.2](#h2-报告模板-reporttemplateid) |
| `taskExport.export.exportStage`         | `/TaskExport/export/exportStage`         | enum     |  ✓   | `TASK_COMPLETED` / `VERIFY_SCAN` / `VERIFY_FIX_SCAN`         |
| `taskExport.export.dataType`            | `/TaskExport/export/dataType`            | enum     |  ✓   | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` |
| `taskExport.export.generatedAt`         | `/TaskExport/export/generatedAt`         | datetime |  ✓   | 生成时间                                                     |
| `taskExport.export.expiresAt`           | `/TaskExport/export/expiresAt`           | datetime |  ○   | 下载过期时间                                                 |
| `taskExport.export.recordCount`         | `/TaskExport/export/recordCount`         | int      |  ✓   | 漏洞**实例**总条数（`instances[]` 合计），用于评估包大小     |
| `taskExport.task.taskId`                | `/TaskExport/task/taskId`                | string   |  ✓   | 平台任务 ID                                                  |
| `taskExport.task.extTaskId`             | `/TaskExport/task/extTaskId`             | string   |  ○   | Partner 幂等键                                               |
| `taskExport.task.taskName`              | `/TaskExport/task/taskName`              | string   |  ✓   | 任务名称                                                     |
| `taskExport.task.targetType`            | `/TaskExport/task/targetType`            | enum     |  ✓   | `IPV4` / `IPV6` / `URL`                                      |
| `taskExport.task.type`                  | `/TaskExport/task/type`                  | int      |  ✓   | 任务类型，见 [附录 F](#附录-f--任务类型-type)                |
| `taskExport.task.scanTemplateId`        | `/TaskExport/task/scanTemplateId`        | int      |  ○   | 扫描模板 ID                                                  |
| `taskExport.task.reportTemplateId`      | `/TaskExport/task/reportTemplateId`      | int      |  ○   | 报告/外发模板 ID                                             |
| `taskExport.task.status`                | `/TaskExport/task/status`                | enum     |  ✓   | `FINISHED` / `FAILED` 等任务状态                             |
| `taskExport.task.startedAt`             | `/TaskExport/task/startedAt`             | datetime |  ○   | 任务开始时间                                                 |
| `taskExport.task.finishedAt`            | `/TaskExport/task/finishedAt`            | datetime |  ○   | 任务结束时间                                                 |
| `taskExport.summary.totalTargets`       | `/TaskExport/summary/totalTargets`       | int      |  ○   | 目标总数                                                     |
| `taskExport.summary.aliveTargets`       | `/TaskExport/summary/aliveTargets`       | int      |  ○   | 存活目标数                                                   |
| `taskExport.summary.openPorts`          | `/TaskExport/summary/openPorts`          | int      |  ○   | 开放端口数                                                   |
| `taskExport.summary.totalInstances`     | `/TaskExport/summary/totalInstances`     | int      |  ○   | 漏洞实例总数                                                 |
| `taskExport.summary.verifiedValid`      | `/TaskExport/summary/verifiedValid`      | int      |  ○   | 已验证有效数                                                 |
| `taskExport.summary.falsePositive`      | `/TaskExport/summary/falsePositive`      | int      |  ○   | 误报数                                                       |
| `taskExport.summary.remediated`         | `/TaskExport/summary/remediated`         | int      |  ○   | 已修复数                                                     |
| `taskExport.summary.archived`           | `/TaskExport/summary/archived`           | int      |  ○   | 已备案 / 修复失败数                                          |
| `taskExport.summary.weakPasswordCount`  | `/TaskExport/summary/weakPasswordCount`  | int      |  ○   | 弱口令条数                                                   |
| `taskExport.summary.baselineIssueCount` | `/TaskExport/summary/baselineIssueCount` | int      |  ○   | 配置基线问题条数                                             |

#### 5.6.5 输出参数（`targets[]` / `liveProbeResults[]` / `portScanResults[]`）

| JSON 路径                                   | XML 路径                                                   | 类型        | 必填 | 说明                                                |
| ------------------------------------------- | ---------------------------------------------------------- | ----------- | :--: | --------------------------------------------------- |
| `taskExport.targets[].targetId`             | `/TaskExport/targets/target/targetId`                      | string      |  ✓   | 平台目标 ID；无资产 ID 时可由任务 ID + 目标地址生成 |
| `taskExport.targets[].target`               | `/TaskExport/targets/target/target`                        | string      |  ✓   | 原始扫描目标，IP / URL 均可                         |
| `taskExport.targets[].targetType`           | `/TaskExport/targets/target/targetType`                    | enum        |  ✓   | `IPV4` / `IPV6` / `URL`                             |
| `taskExport.targets[].assetID`              | `/TaskExport/targets/target/assetID`                       | string      |  ○   | 平台资产 ID                                         |
| `taskExport.targets[].assetName`            | `/TaskExport/targets/target/assetName`                     | string      |  ○   | 资产名称                                            |
| `taskExport.targets[].site`                 | `/TaskExport/targets/target/site`                          | string      |  ○   | Web 站点 URL                                        |
| `taskExport.targets[].os`                   | `/TaskExport/targets/target/os`                            | string      |  ○   | 操作系统                                            |
| `taskExport.targets[].riskValue`            | `/TaskExport/targets/target/riskValue`                     | decimal     |  ○   | 目标风险值                                          |
| `taskExport.targets[].riskLevel`            | `/TaskExport/targets/target/riskLevel`                     | int         |  ○   | 目标风险等级                                        |
| `taskExport.liveProbeResults[].liveProbeId` | `/TaskExport/liveProbeResults/liveProbeResult/liveProbeId` | string      |  ✓   | 存活探测结果 ID                                     |
| `taskExport.liveProbeResults[].targetId`    | `/TaskExport/liveProbeResults/liveProbeResult/targetId`    | string      |  ✓   | 关联 `targets[].targetId`                           |
| `taskExport.liveProbeResults[].address`     | `/TaskExport/liveProbeResults/liveProbeResult/address`     | string      |  ✓   | 探测地址，通常为 IP / 域名                          |
| `taskExport.liveProbeResults[].alive`       | `/TaskExport/liveProbeResults/liveProbeResult/alive`       | bool        |  ✓   | 是否存活                                            |
| `taskExport.liveProbeResults[].probeMethod` | `/TaskExport/liveProbeResults/liveProbeResult/probeMethod` | enum/string |  ○   | 探测方式，如 `ICMP` / `TCP` / `ARP`                 |
| `taskExport.liveProbeResults[].latencyMs`   | `/TaskExport/liveProbeResults/liveProbeResult/latencyMs`   | int         |  ○   | 响应耗时，单位毫秒                                  |
| `taskExport.liveProbeResults[].mac`         | `/TaskExport/liveProbeResults/liveProbeResult/mac`         | string      |  ○   | MAC 地址                                            |
| `taskExport.liveProbeResults[].osGuess`     | `/TaskExport/liveProbeResults/liveProbeResult/osGuess`     | string      |  ○   | 操作系统识别 / 猜测结果                             |
| `taskExport.liveProbeResults[].detectedAt`  | `/TaskExport/liveProbeResults/liveProbeResult/detectedAt`  | datetime    |  ○   | 探测时间                                            |
| `taskExport.portScanResults[].portScanId`   | `/TaskExport/portScanResults/portScanResult/portScanId`    | string      |  ✓   | 端口扫描结果 ID                                     |
| `taskExport.portScanResults[].targetId`     | `/TaskExport/portScanResults/portScanResult/targetId`      | string      |  ✓   | 关联 `targets[].targetId`                           |
| `taskExport.portScanResults[].address`      | `/TaskExport/portScanResults/portScanResult/address`       | string      |  ✓   | 扫描地址，通常为 IP / 域名                          |
| `taskExport.portScanResults[].port`         | `/TaskExport/portScanResults/portScanResult/port`          | int         |  ✓   | 端口号                                              |
| `taskExport.portScanResults[].protocol`     | `/TaskExport/portScanResults/portScanResult/protocol`      | enum/string |  ✓   | `TCP` / `UDP` 等                                    |
| `taskExport.portScanResults[].state`        | `/TaskExport/portScanResults/portScanResult/state`         | enum/string |  ✓   | `open` / `closed` / `filtered` 等                   |
| `taskExport.portScanResults[].service`      | `/TaskExport/portScanResults/portScanResult/service`       | string      |  ○   | 服务名称，如 `ssh` / `http`                         |
| `taskExport.portScanResults[].banner`       | `/TaskExport/portScanResults/portScanResult/banner`        | string      |  ○   | Banner 信息                                         |
| `taskExport.portScanResults[].version`      | `/TaskExport/portScanResults/portScanResult/version`       | string      |  ○   | 服务版本                                            |
| `taskExport.portScanResults[].detectedAt`   | `/TaskExport/portScanResults/portScanResult/detectedAt`    | datetime    |  ○   | 探测时间                                            |

#### 5.6.6 输出参数（`vulnerabilities[]` · 产品漏洞聚合）

外发时 **`vulnerabilities[]` 按产品漏洞 `vulID` 聚合**，同一产品漏洞的多条实例归入 `instances[]`，以减少重复字段、缩小包体。

**产品层（`vulnerabilities[]` 元素）**：

| JSON 路径                               | XML 路径                                             | 类型   | 必填 | 说明                                 |
| --------------------------------------- | ---------------------------------------------------- | ------ | :--: | ------------------------------------ |
| `taskExport.vulnerabilities[].vulID`    | `/TaskExport/vulnerabilities/vulnerability/vulID`    | string |  ✓   | 产品漏洞编号（聚合键，外发包内唯一） |
| `taskExport.vulnerabilities[].orgVulId` | `/TaskExport/vulnerabilities/vulnerability/orgVulId` | string |  ○   | 原始编号，如 CVE                     |
| `taskExport.vulnerabilities[].vulLevel` | `/TaskExport/vulnerabilities/vulnerability/vulLevel` | int    |  ○   | 危害等级                             |
| `taskExport.vulnerabilities[].vulName`  | `/TaskExport/vulnerabilities/vulnerability/vulName`  | string |  ✓   | 漏洞名称                             |
| `taskExport.vulnerabilities[].vulDesc`  | `/TaskExport/vulnerabilities/vulnerability/vulDesc`  | string |  ○   | 漏洞描述                             |

**实例层（`vulnerabilities[].instances[]`）**：

| JSON 路径                        | XML 路径                            | 类型   | 必填 | 说明                                        |
| -------------------------------- | ----------------------------------- | ------ | :--: | ------------------------------------------- |
| `…instances[].vulInfoID`         | `…/instances/instance/vulInfoID`    | string |  ✓   | 系统漏洞实例 ID                             |
| `…instances[].targetId`          | `…/instances/instance/targetId`     | string |  ✓   | 关联 `targets[].targetId`                   |
| `…instances[].vulInfoStat`       | `…/instances/instance/vulInfoStat`  | int    |  ✓   | 实例状态，见附录 A                          |
| `…instances[].lvRsn`             | `…/instances/instance/lvRsn`        | int    |  ○   | 未修复原因                                  |
| `…instances[].vulNetAddr`        | `…/instances/instance/vulNetAddr`   | string |  ○   | 网络地址                                    |
| `…instances[].vulPort`           | `…/instances/instance/vulPort`      | int    |  ○   | 端口                                        |
| `…instances[].vulSvc`            | `…/instances/instance/vulSvc`       | string |  ○   | 服务                                        |
| `…instances[].isAccess`          | `…/instances/instance/isAccess`     | int    |  ○   | **0** 内网 / **1** 互联网                   |
| `…instances[].transferTime`      | `…/instances/instance/transferTime` | string |  ✓   | 状态变更时间                                |
| `…instances[].srcMethod`         | `…/instances/instance/srcMethod`    | int    |  ○   | 验证 / 处置方式                             |
| `…instances[].extVulnRef`        | `…/instances/instance/extVulnRef`   | string |  ○   | Partner 扩展引用                            |
| `…instances[].evidence.url`      | `…/evidence/url`                    | string |  ○   | Web 命中 URL                                |
| `…instances[].evidence.protocol` | `…/evidence/protocol`               | string |  ○   | 协议                                        |
| `…instances[].evidence.message`  | `…/evidence/message`                | string |  ○   | 命中证据                                    |
| `…instances[].remediation.*`     | `…/remediation/*`                   | —      |  ○   | 修复 / 备案字段，结构同原扁平 `remediation` |

#### 5.6.7 输出参数（弱口令、配置基线与附录）

| JSON 路径                                       | XML 路径                                                     | 类型        | 必填 | 说明                                            |
| ----------------------------------------------- | ------------------------------------------------------------ | ----------- | :--: | ----------------------------------------------- |
| `taskExport.weakPasswords[].weakPasswordId`     | `/TaskExport/weakPasswords/weakPassword/weakPasswordId`      | string      |  ✓   | 弱口令记录 ID                                   |
| `taskExport.weakPasswords[].targetId`           | `/TaskExport/weakPasswords/weakPassword/targetId`            | string      |  ✓   | 关联目标 ID                                     |
| `taskExport.weakPasswords[].vulInfoID`          | `/TaskExport/weakPasswords/weakPassword/vulInfoID`           | string      |  ○   | 关联漏洞实例 ID                                 |
| `taskExport.weakPasswords[].service`            | `/TaskExport/weakPasswords/weakPassword/service`             | string      |  ✓   | 服务类型，如 `ssh` / `mysql`                    |
| `taskExport.weakPasswords[].port`               | `/TaskExport/weakPasswords/weakPassword/port`                | int         |  ○   | 登录端口                                        |
| `taskExport.weakPasswords[].protocol`           | `/TaskExport/weakPasswords/weakPassword/protocol`            | string      |  ○   | 协议                                            |
| `taskExport.weakPasswords[].username`           | `/TaskExport/weakPasswords/weakPassword/username`            | string      |  ✓   | 用户名                                          |
| `taskExport.weakPasswords[].passwordMasked`     | `/TaskExport/weakPasswords/weakPassword/passwordMasked`      | string      |  ○   | 脱敏后的口令，不输出明文                        |
| `taskExport.baselineResults[].baselineResultId` | `/TaskExport/baselineResults/baselineResult/baselineResultId` | string      |  ✓   | 配置基线结果 ID                                 |
| `taskExport.baselineResults[].targetId`         | `/TaskExport/baselineResults/baselineResult/targetId`        | string      |  ✓   | 关联目标 ID                                     |
| `taskExport.baselineResults[].templateName`     | `/TaskExport/baselineResults/baselineResult/templateName`    | string      |  ○   | 配置模板名称                                    |
| `taskExport.baselineResults[].checkName`        | `/TaskExport/baselineResults/baselineResult/checkName`       | string      |  ✓   | 检查项名称                                      |
| `taskExport.baselineResults[].groupName`        | `/TaskExport/baselineResults/baselineResult/groupName`       | string      |  ○   | 检查项分组                                      |
| `taskExport.baselineResults[].riskValue`        | `/TaskExport/baselineResults/baselineResult/riskValue`       | decimal     |  ○   | 风险值                                          |
| `taskExport.baselineResults[].result`           | `/TaskExport/baselineResults/baselineResult/result`          | enum/string |  ✓   | `PASS` / `FAIL` / `UNKNOWN`，或保留引擎原始值   |
| `taskExport.baselineResults[].solution`         | `/TaskExport/baselineResults/baselineResult/solution`        | string      |  ○   | 修复建议                                        |
| `taskExport.appendices[].appendixId`            | `/TaskExport/appendices/appendix/appendixId`                 | string      |  ✓   | 附录 ID                                         |
| `taskExport.appendices[].targetId`              | `/TaskExport/appendices/appendix/targetId`                   | string      |  ○   | 关联目标 ID                                     |
| `taskExport.appendices[].name`                  | `/TaskExport/appendices/appendix/name`                       | string      |  ✓   | 附录名称，如端口信息、端口 Banner、安装软件信息 |
| `taskExport.appendices[].columns[]`             | `/TaskExport/appendices/appendix/columns/column`             | string[]    |  ✓   | 表头                                            |
| `taskExport.appendices[].rows[][]`              | `/TaskExport/appendices/appendix/rows/row/value`             | string[][]  |  ✓   | 表格行值，按 `columns` 顺序排列                 |

#### 5.6.8 `GET /exports/{exportId}` — 外发元数据

| 项   | 值            |
| ---- | ------------- |
| 能力 | `EXPORT_READ` |

**路径参数**：`exportId`（✓）

**响应 data**：

| 参数             | 类型     | 说明                                                         |
| ---------------- | -------- | ------------------------------------------------------------ |
| exportId         | string   | 外发记录 ID                                                  |
| taskId           | string   | 平台任务 ID                                                  |
| extTaskId        | string   | Partner 任务键                                               |
| reportTemplateId | int      | 报告/外发模板 ID                                             |
| format           | string   | `xml` / `json`                                               |
| exportStage      | enum     | `TASK_COMPLETED` / `VERIFY_SCAN` / `VERIFY_FIX_SCAN`         |
| dataType         | enum     | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` |
| status           | enum     | `PENDING` / `READY` / `EXPIRED` / `FAILED`                   |
| recordCount      | int      | 记录条数                                                     |
| expiresAt        | datetime | 下载过期时间                                                 |
| createdAt        | datetime | 生成时间                                                     |
| downloadUrl      | string   | 可选预签名 URL                                               |

#### 5.6.9 `GET /exports/{exportId}/download` — 下载文件

| 项   | 值            |
| ---- | ------------- |
| 能力 | `EXPORT_READ` |

返回文件流；`format=xml` 时返回单个规范化 XML 文档，`format=json` 时返回同构 JSON 文档。弱口令相关字段不输出明文密码，Partner 存储与展示需符合本单位数据安全要求。

#### 5.6.10 `GET /tasks/{taskId}/exports` — 任务外发历史

| 项   | 值            |
| ---- | ------------- |
| 能力 | `EXPORT_READ` |

**查询参数**：`page`、`size`（✓）

**响应 data**：分页包装 + `items[]`（元素结构同外发元数据）。

---
## 6. 事件回调（Webhook）

平台在**特定异步事件**发生时，向 Partner 注册的 `callbackUrl` 发起 **`POST`**（`Content-Type: application/json`）。

| 项 | 约定 |
|----|------|
| 触发时机 | 任务完成/失败、修复核验完成、外发就绪等（见 §6.2） |
| 与 REST 关系 | Partner **主动调用**业务 API **不会**触发 Webhook；Webhook 为平台**单向推送** |
| 替代方式 | 也可轮询 `GET /tasks/{taskId}`、`GET /exports/{exportId}` 等，见 §10 |

### 6.0 Partner 接收端验签

平台投递事件时携带下列请求头，Partner **收到回调后**应先验签再处理：

| 字段 | 类型 | 说明 |
|------|------|------|
| `X-Webhook-Signature` | string | 事件 body 的 HMAC-SHA256（密钥为运营分配的 Webhook Secret） |
| `X-Webhook-Timestamp` | string | Unix 秒时间戳；与服务器时间差 **5 分钟内**有效 |

| 项 | 约定 |
|----|------|
| 响应 | 建议 HTTP `200`，body `{"received":true}` |
| 失败重试 | 非 2xx 时平台按运营策略重试（见 §6 末尾） |
| 幂等 | 以 `eventId` 去重，避免重复处理同一事件 |

### 6.1 公共请求体

| 字段       | 类型     | 说明                    |
| ---------- | -------- | ----------------------- |
| eventId    | string   | 事件唯一 ID（幂等处理） |
| eventType  | string   | 见下表                  |
| occurredAt | datetime | 事件发生时间            |
| partnerId  | string   | 接入方 ID               |
| payload    | object   | 随事件类型变化          |

### 6.2 事件类型与 payload

| eventType                       | 说明                    |
| ------------------------------- | ----------------------- |
| `TASK_COMPLETED`                | 任务正常结束            |
| `TASK_FAILED`                   | 任务失败                |
| `INSTANCE_VERIFY_FIX_COMPLETED` | 修复核验完成（→6/7/10） |
| `EXPORT_READY`                  | 外发包可下载            |

**`TASK_COMPLETED` / `TASK_FAILED` · payload**：

| 参数                   | 类型   | 必填 | 说明                  |
| ---------------------- | ------ | :--: | --------------------- |
| taskId                 | string |  ✓   | 平台任务 ID           |
| extTaskId              | string |  ○   | Partner 任务键        |
| status                 | enum   |  ✓   | `FINISHED` / `FAILED` |
| summary.totalInstances | int    |  ○   | 实例总数              |
| summary.verifiedValid  | int    |  ○   | 验证有效数            |
| summary.falsePositive  | int    |  ○   | 误报数                |

**`INSTANCE_VERIFY_FIX_COMPLETED` · payload**：

| 参数                | 类型   | 必填 | 说明                   |
| ------------------- | ------ | :--: | ---------------------- |
| vulInfoID           | string |  ✓   | 实例 ID                |
| vulInfoStat         | int    |  ✓   | 当前状态（6/7/10）     |
| previousVulInfoStat | int    |  ○   | 变更前状态（通常为 5） |

**`EXPORT_READY` · payload**：

| 参数             | 类型   | 必填 | 说明                                                         |
| ---------------- | ------ | :--: | ------------------------------------------------------------ |
| exportId         | string |  ✓   | 外发记录 ID                                                  |
| taskId           | string |  ✓   | 平台任务 ID                                                  |
| extTaskId        | string |  ○   | Partner 任务键                                               |
| reportTemplateId | int    |  ○   | 报告/外发模板 ID                                             |
| format           | string |  ✓   | 外发格式                                                     |
| exportStage      | string |  ✓   | `TASK_COMPLETED` / `VERIFY_SCAN` / `VERIFY_FIX_SCAN`         |
| dataType         | string |  ✓   | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` |
| recordCount      | int    |  ○   | 条数                                                         |
| downloadUrl      | string |  ○   | 预签名下载 URL                                               |

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
    "reportTemplateId": 2001,
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

| 格式   | 根结构                      | 示例文件名                        |
| ------ | --------------------------- | --------------------------------- |
| `xml`  | `<TaskExport>`              | `export-{taskId}-{exportId}.xml`  |
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
      "reportTemplateId": 2001,
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
      "type": 1,
      "scanTemplateId": 1001,
      "reportTemplateId": 2001,
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
    <reportTemplateId>2001</reportTemplateId>
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
    <type>1</type>
    <scanTemplateId>1001</scanTemplateId>
    <reportTemplateId>2001</reportTemplateId>
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

字段说明以 §5.6.4–§5.6.7 为准。

**修复核验外发**（`exportStage=VERIFY_FIX_SCAN`，`dataType=SYSTEM_VULNERABILITY`；须含 `targets[]`、`liveProbeResults[]`、`portScanResults[]`、`vulnerabilities[]`）：

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
    "targets": [
      {
        "targetId": "TGT-001",
        "target": "10.10.1.1",
        "targetType": "IPV4",
        "assetName": "core-host-01"
      }
    ],
    "liveProbeResults": [
      {
        "liveProbeId": "LIVE-VF-001",
        "targetId": "TGT-001",
        "address": "10.10.1.1",
        "alive": true,
        "probeMethod": "ICMP",
        "latencyMs": 10
      }
    ],
    "portScanResults": [
      {
        "portScanId": "PORT-VF-001",
        "targetId": "TGT-001",
        "address": "10.10.1.1",
        "port": 22,
        "protocol": "TCP",
        "state": "open",
        "service": "ssh",
        "banner": "OpenSSH/9.6"
      }
    ],
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

| 能力码                | 说明                                 |
| --------------------- | ------------------------------------ |
| `TASK_WRITE`          | 创建任务                             |
| `TASK_READ`           | 查询任务                             |
| `INSTANCE_READ`       | 查询实例                             |
| `INSTANCE_VERIFY`     | 验证                                 |
| `INSTANCE_REMEDIATE`  | 处置（含已修复与修复失败）           |
| `INSTANCE_VERIFY_FIX` | 修复核验                             |
| `EXPORT_READ`         | 查询/下载外发包                      |
| `EVENT_SUBSCRIBE`     | 接收 Webhook（须在平台登记回调 URL） |

未开通的能力调用将返回 **`40301`**。

---

## 9. 业务错误码

| code  | 含义           | 处理建议                                                     |
| ----- | -------------- | ------------------------------------------------------------ |
| 0     | 成功           | —                                                            |
| 40001 | 参数校验失败   | 检查请求体                                                   |
| 40002 | 状态机不允许   | 核对当前 `vulInfoStat`                                       |
| 40003 | 资源不存在     | 检查 ID                                                      |
| 40004 | 枚举/码表非法  | 对照附录状态表                                               |
| 40005 | 修复与备案互斥 | 勿重复处置                                                   |
| 40101 | 鉴权失败       | 检查 Token/签名                                              |
| 40301 | 能力未开通     | 联系运营开通                                                 |
| 40901 | 幂等冲突       | 创建任务使用已返回的 `taskId`；实例写使用首次响应或更换 `clientRequestId` |
| 42901 | 限流           | 退避重试                                                     |
| 50001 | 引擎调用失败   | 稍后重试或联系平台                                           |
| 50002 | 回调投递失败   | 平台异步重试；检查 Partner 接收端                            |

---

## 10. 典型集成流程

```text
1. POST /tasks/file 或 POST /tasks/vul（§5.1.1 XML / §5.1.2 JSON；`extTaskId` 幂等）→ 保存 taskId
2. 轮询 GET /tasks/{taskId} 或等待 Webhook TASK_COMPLETED
3. 收到 EXPORT_READY → GET /exports/{exportId}/download → 按 `format` 解析 XML 或 JSON
4. POST /instances/search?taskId=... → 入库漏洞实例
5. 业务侧处置后：
   - POST .../verify（有效/误报）
   - POST .../remediate（含修复失败 →9）
   - POST .../verify-fix
6. 若 verify / verify-fix 触发扫描，继续接收 EXPORT_READY，按 `exportStage` 识别验证扫描或修复核验外发
7. 可选：订阅 `INSTANCE_VERIFY_FIX_COMPLETED` / `EXPORT_READY` 等事件驱动 ITSM 工单
```

---

## 附录 A · 漏洞实例状态 `vulInfoStat`

摘自《基础电信企业网络安全漏洞管理平台接口规范(2025年版)》**A.8 系统漏洞状态码表**。

| 值   | 说明       | 阶段 |
| ---- | ---------- | ---- |
| 0    | 潜在预警   | 预警 |
| 1    | 初始发现   | 识别 |
| 2    | 已验证有效 | 识别 |
| 3    | 已验证误报 | 修复 |
| 5    | 已修复     | 修复 |
| 6    | 核验修复   | 修复 |
| 7    | 核验未修复 | 识别 |
| 8    | 验证失败   | 识别 |
| 9    | 修复失败   | 识别 |
| 10   | 核验失败   | 识别 |

---

## 附录 B · 相关资源

| 资源                          | 路径                                                         |
| ----------------------------- | ------------------------------------------------------------ |
| OpenAPI 3.1                   | [`openapi/v1/openapi.yaml`](../../openapi/v1/openapi.yaml)   |
| 扫描任务配置示例（漏洞扫描）  | [`templates/xml/scan-task-vuln-example.xml`](../../templates/xml/scan-task-vuln-example.xml) |
| 扫描任务（模式 B · 内联模板） | [`templates/xml/scan-task-vuln-inline-example.xml`](../../templates/xml/scan-task-vuln-inline-example.xml) |
| 内联 scanTemplate/report 参考 | [`templates/xml/scan-task-inline-templates-reference.xml`](../../templates/xml/scan-task-inline-templates-reference.xml) |
| 扫描任务配置示例（WEB）       | [`templates/xml/scan-task-web-example.xml`](../../templates/xml/scan-task-web-example.xml) |
| 扫描任务配置示例（口令猜测）  | [`templates/xml/scan-task-pwdguess-example.xml`](../../templates/xml/scan-task-pwdguess-example.xml) |
| 部侧接口规范原文              | [`docs/standards/基础电信企业网络安全漏洞管理平台接口规范(2025年版).docx`](../standards/基础电信企业网络安全漏洞管理平台接口规范(2025年版).docx) |

**本地预览**（Redocly CLI 2.x）：`npx @redocly/cli build-docs openapi/v1/openapi.yaml -o openapi/v1/api-docs.html`，用浏览器打开生成的 HTML。需要 **Node.js ≥ 20.19**。亦可使用 https://editor.swagger.io 导入该 YAML。

文档问题请联系平台集成对接人（`partnerId` 对应运营渠道）。

---

## 附录 C · 平台用户角色 `srcTktRole` / `dstTktRole`

摘自部侧规范 **A.9 平台用户角色表**，用于 §5.4 处置工单字段及部侧表56 日志。

| 角色代码 | 说明                    |
| -------- | ----------------------- |
| 0        | 超级管理员              |
| 1        | 安全审计管理员          |
| 2        | 操作员                  |
| 3        | 审核员                  |
| 4        | 技术员                  |
| 5        | 检查员                  |
| 6        | 系统配置管理员          |
| 7        | 授权（用户）管理员      |
| 8        | 外部系统-资产责任人     |
| 9        | 外部系统-业务系统责任人 |
| 10       | 外部-其他               |

---

## 附录 D · 漏洞管理处置方式 `srcMethod`

摘自部侧规范 **A.10 漏洞管理处置方式码表**。开放平台在创建扫描任务（§5.1.1 / §5.1.2，见 [附录 I](#附录-i--部侧排查扩展参数)）、验证（§5.3）、处置（§5.4）等接口中以 `srcMethod` 传递**处置代码**列取值。

| 处置代码 | 技术处置方式             | 漏洞管理类型             | 台账类别 |
| -------- | ------------------------ | ------------------------ | -------- |
| 1080     | 关联分析                 | 产品漏洞预警             | 108      |
| 1020     | 指纹插件（远程版本扫描） | 系统漏洞排查             | 102      |
| 1021     | POC 插件                 | 系统漏洞排查             | 102      |
| 1022     | 漏洞扫描（混合）         | 系统漏洞排查             | 102      |
| 1023     | （人工）线下导入         | 系统漏洞排查             | 102      |
| 1024     | （人工）本地发现         | 系统漏洞排查             | 102      |
| 1026     | 交叉扫描验证             | 系统漏洞排查             | 102      |
| 1027     | 登录扫描                 | 系统漏洞排查             | 102      |
| 1028     | 连通性检测               | 系统漏洞排查             | 102      |
| 1030     | 字典组合暴破             | 弱口令扫描               | 103      |
| 1031     | 规则猜测暴破             | 弱口令扫描               | 103      |
| 1032     | 配置文件分析             | 弱口令扫描               | 103      |
| 1040     | EXP 漏洞利用             | 系统漏洞利用             | 104      |
| 1050     | 补丁修复                 | 系统漏洞修复             | 105      |
| 1051     | 等效防护修复             | 系统漏洞修复             | 105      |
| 1052     | 连通性阻断（离线使用）   | 系统漏洞修复             | 105      |
| 1053     | 资产下线                 | 系统漏洞修复             | 105      |
| 1060     | 修复核验自适应扫描       | 漏洞安全验证             | 106      |
| 1061     | 攻击模拟漏洞扫描         | 漏洞安全验证             | 106      |
| 1070     | 本地动态核验             | 产品漏洞验证（分类定级） | 107      |
| 1071     | 静态代码审计             | 产品漏洞验证（分类定级） | 107      |
| 1090     | 社工                     | 网络渗透测试             | 109      |
| 1091     | 钓鱼                     | 网络渗透测试             | 109      |
| 1092     | 实例型漏洞利用           | 网络渗透测试             | 109      |
| 1093     | 弱口令提权               | 网络渗透测试             | 109      |
| 1094     | 线下导入                 | 网络渗透测试             | 109      |
| 1100     | 模糊测试                 | 产品漏洞挖掘             | 110      |
| 1101     | 源码逻辑审计             | 产品漏洞挖掘             | 110      |
| 1102     | 符号执行                 | 产品漏洞挖掘             | 110      |
| 1103     | 污点分析                 | 产品漏洞挖掘             | 110      |
| 1110     | 崩溃路径复现             | POC 开发验证             | 111      |
| 1111     | 代码插桩                 | POC 开发验证             | 111      |
| 1112     | 可利用条件约束           | POC 开发验证             | 111      |
| 1113     | CoreDump 分析            | POC 开发验证             | 111      |
| 1114     | 补丁比对                 | POC 开发验证             | 111      |
| 1010     | 登录管理                 | 漏管平台维护             | 101      |
| 1000     | 时钟同步                 | 漏管平台系统日志         | 100      |
| 990      | 方式不限                 | 通用                     | 99       |
| 999      | 其他方式                 | —                        | —        |
| 2990     | 保留扩展                 | 其他类型                 | 299      |

**§5.4 处置常用代码**：已修复 → **1050–1053**；验证有效 → **1021**、**1026** 等排查/验证类；修复失败/备案 → 结合 `lvRsn` 使用 **999** 或其他符合业务场景的代码。

---

## 附录 E · 未修复原因 `lvRsn`

摘自部侧规范 **A.23 未修复原因**。§5.4 处置进入终态 **9（修复失败）** 时必填。

| 编码 | 原因说明       |
| ---- | -------------- |
| 101  | 无修复方案     |
| 102  | 修复方案无效   |
| 103  | 修复成本过高   |
| 104  | 优先级未达基线 |
| 105  | 白名单         |
| 107  | 非对外暴露资产 |
| 108  | VPT 无危害     |
| 109  | 接受风险       |
| 999  | 其他           |

---

## 附录 F · 任务类型 `type`

创建任务（§5.1.1 / §5.1.2）共用任务类型码表；**两种创建方式均支持 type 1 / 2 / 3**。

| 类型码 | 说明         | §5.1.1（`POST /tasks/file`） | §5.1.2（`POST /tasks/vul`） |
| ------ | ------------ | ---------------------------- | --------------------------- |
| **1**  | 漏洞扫描     | ✓                            | ✓                           |
| **2**  | WEB 应用扫描 | ✓                            | ✓                           |
| **3**  | 口令猜测     | ✓                            | ✓                           |

非法 `type` 返回 **40004**。`scanTemplateId` 无效或与 `type` 不匹配 → **40004**。

---

## 附录 G · 扫描任务配置文件 `file`

§5.1.1 请求体 `file` 字段承载 **UTF-8 XML 正文**（非 Base64）。Partner 将 XML 作为 JSON 字符串转义后提交。

与 §5.1.2 的差异：

| 项            | §5.1.1（`POST /tasks/file`）                                 | §5.1.2（`POST /tasks/vul`）                      |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| 扫描目标      | XML `<server><targets>` 文本（ip/domain/url，逗号或分号分隔） | JSON `targets.hosts` 字符串（格式同上）          |
| 登陆检查      | 根级 `<targets>` 容器（始终存在，可为空 `<targets/>`）       | JSON `targets.auth[]`（无登陆检查时省略或 `[]`） |
| 扫描/报告策略 | **引用平台模板 ID**，或 **内联扫描阶段于 `<server>` + `<report>`**（自定义，不用平台内置） | **仅** `scanTemplateId` / `reportTemplateId`     |

### G.1 结构约定

| 项             | 约定                                                         |
| -------------- | ------------------------------------------------------------ |
| 根元素         | **`<scanTask>`**                                             |
| 任务类型       | JSON **`type`**（1/2/3）；不在 XML 重复                      |
| 任务与扫描     | **`<server>`** 必填，含 `taskName`、`priority`、可选 `callbackUrl`、**`targets`**（扫描目标文本）及内联扫描阶段（模式 B） |
| 扫描目标       | **`/scanTask/server/targets`**：一个或多个 ip / domain / url，**逗号 `,` 或分号 `;` 分隔** |
| 登陆检查       | 根级 **`<targets>`** **始终存在**；未启用或信息为空时为 **空标签** `<targets/>` |
| 模板（二选一） | **A** · `scanTemplateId` + `reportTemplateId`（均 **>0**） · **B** · 扫描阶段内联于 `<server>` + 根级 `<report>`（**不得**与 A 同时出现） |
| 部侧扩展       | 可选 `<miitExt>`，见 [附录 I](#附录-i--部侧排查扩展参数)     |

### G.2 元素与字段

**`<server>` · 任务信息、扫描目标与扫描策略**

| 路径                           | 类型   | 必填 | 说明                                                         |
| ------------------------------ | ------ | :--: | ------------------------------------------------------------ |
| `/scanTask/server/taskName`    | string |  ✓   | 任务名称                                                     |
| `/scanTask/server/priority`    | enum   |  ○   | `LOW` / `MEDIUM` / `HIGH`；缺省 `MEDIUM`                     |
| `/scanTask/server/callbackUrl` | string |  ○   | 覆盖 Partner 默认 Webhook URL                                |
| `/scanTask/server/targets`     | string |  ✓   | 扫描目标：ip / domain / url；多个以 **`,` 或 `;`** 分隔      |
| `/scanTask/server/liveProbe` … |        | 条件 | 模式 **B**；内联扫描阶段，见 [H.1](#h1-扫描模板-scantemplateid) |
| `/scanTask/server/portScan` …  |        | 条件 | 模式 **B**                                                   |
| `/scanTask/server/vulnScan` …  |        | 条件 | 模式 **B**                                                   |
| `/scanTask/server/pwdGuess` …  |        | 条件 | 模式 **B**；type **3**                                       |

**根级 `<targets>` · 登陆检查（始终存在）**

| 项     | 约定                                                         |
| ------ | ------------------------------------------------------------ |
| 存在性 | **必须**出现 `<targets>` 标签；无登陆检查时写 **`<targets/>`** |
| 内容   | 每条 `<target>` 为富文本登陆信息（见下表）；与 `<server><targets>` 扫描地址列表 **独立** |

**富文本 `<target>` 子元素**（登陆检查；JSON §5.1.2 对应 `targets.auth[]`）

| 路径                                      | 类型   | 必填 | 说明                                           |
| ----------------------------------------- | ------ | :--: | ---------------------------------------------- |
| `…/ip`                                    | string |  ✓*  | 目标 IP（IPv4/IPv6）；*富文本时与 `url` 二选一 |
| `…/url`                                   | string |  ✓*  | Web URL（`type=2`）                            |
| `…/protocol`                              | string |  ○   | `SSH` / `SMB` / `Telnet` / `RDP` 等            |
| `…/port`                                  | int    |  ○   | 端口 **0–65535**                               |
| `…/username`                              | string |  ○   | 用户名                                         |
| `…/password`                              | string |  ○   | 密码（CDATA）                                  |
| `…/jumpHosts`                             | 容器   |  ○   | 可为空；子元素 `jumpHost`                      |
| `…/jumpHosts/jumpHost/ip`                 | string |  ✓   | 跳转机 IP                                      |
| `…/jumpHosts/jumpHost/protocol`           | string |  ✓   | `SSH` / `Telnet`                               |
| `…/jumpHosts/jumpHost/port`               | int    |  ✓   | 端口                                           |
| `…/jumpHosts/jumpHost/username`           | string |  ○   | 用户名                                         |
| `…/jumpHosts/jumpHost/password`           | string |  ○   | 密码                                           |
| `…/templates`                             | 容器   |  ○   | 可为空；配置核查模板参数                       |
| `…/templates/template/@uuid`              | string |  ✓   | 模板 UUID                                      |
| `…/templates/template/param/@name`        | string |  ✓   | 参数名                                         |
| `…/templates/template/param/@description` | string |  ○   | 展示名                                         |
| `…/templates/template/param/@typeField`   | string |  ○   | `text` / `password`                            |
| `…/templates/template/param`              | string |  ✓   | 参数值（CDATA）                                |

**根 `<scanTask>` · 模板引用、报告与部侧扩展**

| 路径                                          | 类型   | 必填 | 说明                                                         |
| --------------------------------------------- | ------ | :--: | ------------------------------------------------------------ |
| `/scanTask/scanTemplateId`                    | int    | 条件 | 模式 **A**；平台扫描模板 ID                                  |
| `/scanTask/reportTemplateId`                  | int    | 条件 | 模式 **A**；平台报告模板 ID                                  |
| `/scanTask/report`                            | 容器   | 条件 | 模式 **B**；内联 [H.2](#h2-报告模板-reporttemplateid)        |
| `/scanTask/miitExt`                           | 容器   |  ○   | 部侧排查扩展，见 [附录 I](#附录-i--部侧排查扩展参数)         |
| `…/miitExt/srcMethod`                         | int    |  ○   | 技术处置方式，见 [附录 D](#附录-d--漏洞管理处置方式-srcmethod) |
| `…/miitExt/vulIDs/vulId`                      | string |  ○   | 产品漏洞 ID，可重复                                          |
| `…/miitExt/secResourceHashes/secResourceHash` | string |  ○   | 安全资源设备 hash，可重复                                    |

**内联 `<server>` 扫描阶段**（字段定义见 H.1，作为 `<server>` 直接子元素）

| 路径                                                         | 类型 | 说明                                    |
| ------------------------------------------------------------ | ---- | --------------------------------------- |
| `…/liveProbe/@enabled`                                       | bool | 存活探测                                |
| `…/liveProbe/icmp` · `tcp` · `tcpPorts`                      |      | ICMP/TCP；`tcpPorts` 缺省 **`1-65535`** |
| `…/portScan/@enabled`                                        | bool | 端口扫描                                |
| `…/portScan/strategy`                                        | enum | `standard` / `fast` / `user` / `all`    |
| `…/portScan/userPorts` · `tcpMode` · `udpEnabled`            |      | 端口策略细节                            |
| `…/vulnScan/@enabled` · `depth` · `expVerify`                |      | 漏洞/Web 扫描                           |
| `…/pwdGuess/@enabled` · `threadNum` · `timeoutSec` · `services/service` |      | 口令猜测（type **3**）                  |

**内联 `<report>`**

| 路径            | 类型 | 必填 | 说明                                                         |
| --------------- | ---- | :--: | ------------------------------------------------------------ |
| `…/format`      | enum |  ✓   | `json` / `xml`                                               |
| `…/dataProfile` | enum |  ✓   | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` 等 |

### G.3 校验规则

| 规则        | 说明                                                         |
| ----------- | ------------------------------------------------------------ |
| 模板模式    | **A**（双 ID >0）与 **B**（`<server>` 内联扫描阶段 + `<report>`）**互斥**；混用 → **40001** |
| 模式 B      | 不得出现 `scanTemplateId` / `reportTemplateId`，或二者均为 **0**；不得出现仅空的 `<report/>` 而无 `format` |
| 模式 A      | 不得出现 `<server>` 内联扫描阶段子元素（`liveProbe` 等）或 `<report>` |
| `<targets>` | 根级 `<targets>` **必须存在**；无登陆检查时须为 `<targets/>` |
| 扫描目标    | `<server><targets>` 非空；`type=2` 须含 URL；`type=3` 须含 IP 且 `<server>` 内启用 `pwdGuess` |

### G.4 示例

**模式 B · 富文本目标 + 内联 H.1/H.2（`type=1`）** — 见 [`scan-task-vuln-inline-example.xml`](../../templates/xml/scan-task-vuln-inline-example.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<scanTask>
  <server>
    <taskName><![CDATA[2026Q2-核心业务排查]]></taskName>
    <priority>HIGH</priority>
    <callbackUrl><![CDATA[https://partner.example.com/hooks/vuln]]></callbackUrl>
    <targets><![CDATA[10.65.195.204]]></targets>
    <liveProbe enabled="true"><icmp>true</icmp><tcp>true</tcp></liveProbe>
    <portScan enabled="true"><strategy>standard</strategy><tcpMode>SYN</tcpMode></portScan>
    <vulnScan enabled="true"><depth>3</depth><expVerify>false</expVerify></vulnScan>
  </server>
  <targets>
    <target>
      <ip><![CDATA[10.65.195.204]]></ip>
      <protocol><![CDATA[SSH]]></protocol>
      <port><![CDATA[22]]></port>
      <username><![CDATA[root]]></username>
      <password><![CDATA[Gp+CdzxD]]></password>
      <jumpHosts>
        <jumpHost>
          <ip><![CDATA[10.65.195.204]]></ip>
          <protocol><![CDATA[SSH]]></protocol>
          <port><![CDATA[22]]></port>
          <username><![CDATA[root]]></username>
          <password><![CDATA[Gp+CdzxD]]></password>
        </jumpHost>
      </jumpHosts>
      <templates/>
    </target>
  </targets>
  <miitExt>
    <srcMethod>1021</srcMethod>
    <vulIDs>
      <vulId><![CDATA[MVM-2019-1696145560773468160]]></vulId>
    </vulIDs>
    <secResourceHashes>
      <secResourceHash><![CDATA[8f3a2b1c9d4e5f60718293a4b5c6d7e8]]></secResourceHash>
    </secResourceHashes>
  </miitExt>
  <report>
    <format>json</format>
    <dataProfile>MIXED</dataProfile>
  </report>
</scanTask>
```

**模式 A · 引用平台模板** — 见 [`scan-task-vuln-example.xml`](../../templates/xml/scan-task-vuln-example.xml)

---

## 附录 H · 扫描模板与报告模板

H.1 / H.2 定义扫描策略与报告/外发的数据结构。平台可预置模板（通过 ID 引用）；§5.1.1 亦可在 `file` 内联填写。

| 用法         | §5.1.1（`POST /tasks/file`）                            | §5.1.2（`POST /tasks/vul`）           |
| ------------ | ------------------------------------------------------- | ------------------------------------- |
| 引用平台模板 | `scanTemplateId` + `reportTemplateId`（>0）             | `scanTemplateId` + `reportTemplateId` |
| 自定义内容   | 扫描阶段内联于 `<server>` + 根级 `<report>`（结构见下） | **不支持**                            |

### H.1 扫描模板 `scanTemplateId` / `<server>` 内联扫描阶段

定义存活探测、端口扫描、漏洞扫描 / 口令猜测各阶段。内联时作为 `<server>` 的直接子元素。

| 字段 / XML 路径                                        | 类型 | 说明                                                  |
| ------------------------------------------------------ | ---- | ----------------------------------------------------- |
| liveProbe.enabled                                      | bool | 存活探测开关（`/scanTask/server/liveProbe/@enabled`） |
| liveProbe.icmp · tcp · tcpPorts                        |      | `tcpPorts` 缺省 **`1-65535`**                         |
| portScan.enabled                                       | bool | 端口扫描开关                                          |
| portScan.strategy                                      | enum | `standard` / `fast` / `user` / `all`                  |
| portScan.userPorts · tcpMode · udpEnabled              |      | 端口策略                                              |
| vulnScan.enabled · depth · expVerify                   |      | 漏洞/Web 扫描                                         |
| pwdGuess.enabled · threadNum · timeoutSec · services[] |      | 口令猜测（type **3**）                                |

**匹配规则**

| scanTemplateId | 行为                                                     |
| -------------- | -------------------------------------------------------- |
| **0**（缺省）  | 按 `type` 选用平台默认模板（见下表）                     |
| **>0**         | 按 ID 加载；`applicableTypes` 须包含当前 `type`          |
| 校验失败       | 模板不存在，或 `type` 不在 `applicableTypes` → **40004** |

**平台预置模板**

| scanTemplateId | templateName | applicableTypes | 摘要                    |
| -------------- | ------------ | --------------- | ----------------------- |
| **1001**       | 漏洞扫描     | [1,2,3]         | 端口探测 + 标准漏洞排查 |
| **1002**       | 存活探测     | [1,2,3]         | 资产存活探测            |
| **1003**       | 端口扫描     | [1,2,3]         | 端口探测                |

缺省 `scanTemplateId=0` 时：`type=1/2/3` 均默认选用 **1001**。

### H.2 报告模板 `reportTemplateId` / `<report>`

定义任务结束外发数据包的序列化格式与字段剖面（§5.6 / §7）。内联时根元素为 `<report>`。

| 字段 / XML 路径 | 类型 | 说明                                                         |
| --------------- | ---- | ------------------------------------------------------------ |
| format          | enum | `json` / `xml`                                               |
| dataProfile     | enum | `MIXED` / `SYSTEM_VULNERABILITY` / `LIVE_PROBE` / `PORT_SCAN` 等 |

**匹配规则**

| reportTemplateId | 行为                       |
| ---------------- | -------------------------- |
| **0**（缺省）    | 按 `type` 选用默认报告模板 |
| **>0**           | 按 ID 加载                 |

**平台预置示例**

| reportTemplateId | templateName       | format | dataProfile |
| ---------------- | ------------------ | ------ | ----------- |
| **2001**         | 开放平台 JSON 整包 | json   | MIXED       |
| **2002**         | 开放平台 XML 整包  | xml    | MIXED       |

外发回显：`taskExport.export.reportTemplateId`、`taskExport.export.format` 与创建任务一致（内联自定义时 `reportTemplateId` 回显 **0**，`format` / `dataProfile` 取自内联定义）。

---

## 附录 I · 部侧排查扩展参数

摘自部侧规范排查/扫描工单相关字段，用于 §5.1.1 / §5.1.2 创建任务时向平台声明**技术处置方式**、**待扫产品漏洞范围**及**扫描资源设备**。与 [附录 D](#附录-d--漏洞管理处置方式-srcmethod) 处置码表对齐。

| 参数              | JSON（§5.1.2）        | XML（§5.1.1 · `<miitExt>`）                   | 类型     | 必填 | 说明                                                         |
| ----------------- | --------------------- | --------------------------------------------- | -------- | :--: | ------------------------------------------------------------ |
| srcMethod         | `srcMethod`           | `miitExt/srcMethod`                           | int      |  ○   | **技术处置方式**（处置代码），见附录 D；排查类典型 **1020–1026**（如 **1021**=POC 插件、**1022**=漏洞扫描混合） |
| vulIDs            | `vulIDs[]`            | `miitExt/vulIDs/vulId[]`                      | string[] |  ○   | 产品漏洞 ID 列表；**预留**                                   |
| secResourceHashes | `secResourceHashes[]` | `miitExt/secResourceHashes/secResourceHash[]` | string[] |  ○   | 安全资源设备 hash；**预留**                                  |

**使用说明**

| 项                  | 约定                                                         |
| ------------------- | ------------------------------------------------------------ |
| 缺省                | 三项均可省略；平台按 `type` 与模板 ID 使用默认处置方式及平台分配的安全资源 |
| `srcMethod`         | 须与任务 `type` 及扫描模板策略一致；非法码 → **40004**       |
| `vulIDs`            | 非空时平台仅针对列表内产品漏洞编排扫描/结果归集；ID 不存在时可返回 **40001**（待查询接口开放后行为以运营配置为准） |
| `secResourceHashes` | 非空时平台调度指定 hash 对应扫描器；hash 无效或未授权 → **40001** / **40301**（待设备查询接口开放后行为以运营配置为准） |
| 部侧映射            | 平台内部映射部侧工单 `procMethod` / 安全资源调度；Partner **无需**传递部侧 `orderID` 等 L2 字段 |

**排查类 `srcMethod` 速查**（附录 D 节选）

| 代码 | 技术处置方式             |
| ---- | ------------------------ |
| 1020 | 指纹插件（远程版本扫描） |
| 1021 | POC 插件                 |
| 1022 | 漏洞扫描（混合）         |
| 1023 | （人工）线下导入         |
| 1024 | 网络分析                 |
| 1025 | 登录扫描                 |
| 1026 | 连通性检测（ping 扫描）  |

---

## 附录 J · 接入 FAQ

本节汇总 Partner 接入过程中的常见疑问与官方答复，与正文各章节交叉引用。接入方反馈的新问题经评审后纳入本附录并在 [修订记录](#修订记录) 中说明。

| # | 疑问摘要 | 答复要点 | 详见 |
|---|----------|----------|------|
| J-1 | §1.3 写接口到底有几个操作？ | 实例生命周期 **3 类业务动作**（验证、处置、修复核验）→ **6 个 HTTP 路径**（每类单条 + 批量）；含排查任务创建时再加 **2 个创建路径（二选一）**，共 **8 个写路径** | [§1.3.2](#132-写接口数量对照) |
| J-2 | `Bearer Token` 应调哪个接口换取？ | Token **不在** `/api/open/v1`；向运营提供的 `{authBaseUrl}` 调用 `POST /oauth/token`（标准 OAuth）或 `POST /api/partners/token`（简化 JSON），再用返回的 Token 调用业务 API | [§2.2](#22-环境地址)、[§3.1.1](#311-获取-access-token) |
| J-3 | 调用 REST 是否每次都要做 Webhook 验签？ | **否**。Webhook 验签仅用于 Partner **接收**平台异步事件回调时校验 `X-Webhook-Signature`；Partner **主动调用** REST 只需 `Authorization: Bearer` | [§3.3](#33-webhook-验签与-rest-无关)、[§6.0](#60-partner-接收端验签) |
| J-4 | 幂等「二选一」与示例同时带 `extTaskId`、`Idempotency-Key` 是否矛盾？ | **不矛盾**。创建任务时 `extTaskId` **必填**（业务幂等键），`Idempotency-Key` **可选**（HTTP 层增强）；同时携带合法，平台 **优先按 `extTaskId` 判重** | [§4.2](#42-幂等)、[§5.1.1](#511-创建任务filexml) |
| J-5 | 各节表格列名不一致，如何阅读？ | 全文按场景固定表头：接口元信息 `项·值`、约定 `项·约定`、REST 参数 `参数·类型·必填·说明`、简化结构 `字段·类型·说明`、外发映射 `JSON 路径·XML 路径·…` | [§5.0.1](#501-文档体例) |

### J-1 · 写接口数量与 §1.3 的关系

**疑问**：§1.3 标题为「漏洞实例生命周期（写接口）」，但创建排查任务也算写操作，总数应如何理解？

**答复**：

1. **实例写接口**（改变 `vulInfoStat` 的 REST 写操作）固定为 **3 类 × 2 路径 = 6 个**：
   - 验证：`POST /instances/{vulInfoID}/verify`、`POST /instances/verify:batch`
   - 处置：`POST /instances/{vulInfoID}/remediate`、`POST /instances/remediate:batch`
   - 修复核验：`POST /instances/{vulInfoID}/verify-fix`、`POST /instances/verify-fix:batch`
2. **任务创建**（产生 `taskId` 与初始实例，不属于上述实例状态机写接口）为 **2 个路径二选一**：
   - `POST /tasks/file`（XML 配置文件）
   - `POST /tasks/vul`（JSON 排查参数）
3. **合计**：若口径为「所有会改变平台数据的 Partner 写路径」，则为 **8 个**；若仅统计实例生命周期写接口，则为 **6 个**。
4. **读接口**（如 `GET /tasks/{taskId}`、`POST /instances/search`）不改变业务状态，不计入写接口数量。

### J-2 · Bearer Token 获取端点

**疑问**：文档多处要求 `Authorization: Bearer <accessToken>`，但未在 `/api/open/v1` 下看到 Token 接口，应如何换取？

**答复**：

| 步骤 | 动作 |
|------|------|
| 1 | 向平台运营索取 `clientId`、`clientSecret` 及 **认证服务 Base URL**（`authBaseUrl`，通常与业务 API 域名不同） |
| 2 | 服务端调用 Token 端点（开通材料指定其一）：<br>• 标准：`POST {authBaseUrl}/oauth/token`（`grant_type=client_credentials`）<br>• 简化：`POST {authBaseUrl}/api/partners/token`（JSON body） |
| 3 | 解析响应中的 `access_token` / `accessToken`，填入业务请求头 `Authorization: Bearer ...` |
| 4 | 调用开放平台业务 API：`https://{业务域名}/api/open/v1/...` |

> OpenAPI 文件（`openapi/v1/openapi.yaml`）** intentionally** 仅描述业务契约 `/api/open/v1`；Token 端点不在 OpenAPI 范围内，以本节及运营开通手册为准。

### J-3 · Webhook 验签适用范围

**疑问**：§3 鉴权章节出现 Webhook 验签，是否意味着每次 REST 请求都要计算 HMAC？

**答复**：

| 场景 | 是否需要 Webhook 验签 |
|------|----------------------|
| Partner → 平台 REST 调用 | **否**；使用 Bearer Token（§3.1） |
| 平台 → Partner 异步事件 POST 到 `callbackUrl` | **是**；Partner 在接收端校验 `X-Webhook-Signature`、`X-Webhook-Timestamp`（§6.0） |

Partner 主动调用 REST **不会**触发平台向 Partner 回调；Webhook 为平台在任务完成、实例状态变更、外发就绪等事件上的**单向推送**。

### J-4 · 创建任务幂等：`extTaskId` 与 `Idempotency-Key`

**疑问**：§4.2 写「创建任务幂等二选一」，但 §5.1.1 示例同时携带两个字段，是否违规？

**答复**：

| 字段 | 必填 | 作用 | 判重优先级 |
|------|:---:|------|-----------|
| `extTaskId` | ✓ | Partner 侧任务唯一业务 ID；平台与 SVMP 映射 | **高**（优先） |
| `Idempotency-Key` | ○ | HTTP 传输层防重复 POST（如网络重试） | 低；与 `extTaskId` 同时存在时仍合法 |

「二选一」指平台支持 **两种独立的去重机制**，并非「请求体只能出现其中一个字段」。实例写接口的幂等则主要通过 `Idempotency-Key` 实现（§4.2）。

### J-5 · 表格列名体例

**疑问**：有的表格用「参数|类型|必填|说明」，有的用「字段|类型|说明」，是否字段定义不一致？

**答复**：列名差异表示**表格用途**不同，字段语义一致。接入开发时以 [§5.0.1](#501-文档体例) 对照表为准；REST 请求/响应字段描述优先采用 `参数·类型·必填·说明` 四列体例，Webhook 公共体等简化块采用 `字段·类型·说明` 三列体例。

---

## 修订记录

| 版本      | 日期       | 说明                                                                                                                                                                                                                                                                                                                                 |
| --------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1.0.3** | 2026-05-19 | **§1.3** 重写实例生命周期写接口对照表（3 类 6 路径；含任务创建共 8 路径）；**§2.1/§2.2** 补充 `clientId`/`clientSecret` 与认证服务 Base URL；**§3.1.1** 新增 OAuth / 简化 JSON Token 换取说明与示例；**§3.3** 明确 Webhook 验签与 REST 无关并指向 §6.0；**§4.2** 澄清创建任务幂等（`extTaskId` 必填、`Idempotency-Key` 可选及优先判重规则）；**§5.0.1** 统一表格列名体例；**§5.1.1** 示例后补充幂等说明；**§6** 补充 Webhook 触发说明，**§6.0** 迁入 Partner 接收端验签步骤；**附录 J** 新增接入 FAQ（J-1～J-5） |
| **1.0.2** | 2026-05-23 | §5.1.2 `targets` 改为对象：`hosts`（扫描地址）+ `auth[]`（登陆凭据）                                                                                                                                                                                                                                                               |
| **1.0.1** | 2026-05-19 | §5.1.1 / §5.1.2 创建任务路径拆分：`POST /tasks/file`（XML）、`POST /tasks/vul`（JSON）； |
| **1.0.0** | 2026-05-17 | 首版发布：开放平台 REST API、Webhook、扫描结果外发（XML/JSON）、能力码与业务错误码 |