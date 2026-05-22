# 开放平台 API 治理与调用生命周期

> **定位**：说明 open-api-service **不必**为每个 REST 接口各写一套孤立实现；通过 **执行平面 + 治理平面** 统一承载业务与全链路监控管理。  
> **相关文档**：[组件职责与接口映射](./组件职责与接口映射.md) · [partner-gateway 与 open-api-service 模块清单](./partner-gateway与open-api-service-模块与接口清单.md) · [第三方接口规范](../external/开放平台API接口规范.md) · [OpenAPI](../../openapi/v1/openapi.yaml)

---

## 1. 核心结论（给架构与研发）

| 问题 | 结论 |
|------|------|
| 是否每个接口都要单独定义 IO 并手写一套实现？ | **契约上要定义**（OpenAPI）；**实现上不要 1:1 复制粘贴**，走统一调用管道 + 领域 Handler |
| `TASK_WRITE` 等 capability 是什么？ | **授权标签**（网关拦截），不是 9 个独立子系统 |
| 能否对 API 调用全生命周期监控管理？ | **可以**，作为 open-api-service 的 **治理平面**，与业务执行平面 **并存** |
| 能否只做监控、不做业务？ | **不行**；Partner 仍需任务/实例/处置，业务必须在执行平面完成 |

---

## 2. 双平面架构

```text
┌─────────────────────────────────────────────────────────────────┐
│                    open-api-service                              │
├────────────────────────────┬────────────────────────────────────┤
│  A. 执行平面（Execution）     │  B. 治理平面（Governance）          │
│  · REST 用例编排              │  · API 目录（ApiCatalog）           │
│  · 规范域模型                 │  · 调用记录（api_invocation）       │
│  · SVMP 适配                  │  · 指标 / 审计 / 配额统计           │
│  · Webhook 出站               │  · Webhook 投递生命周期             │
│  · Partner 注册 / Token       │  · API 版本 / 弃用（P2+）           │
└────────────────────────────┴────────────────────────────────────┘
         ▲                              ▲
         │ X-Partner-Id, X-Request-Id   │ 每次调用自动写入
         │                              │
   partner-gateway                 同一 requestId 贯穿
```

**调用一次 `POST /api/open/v1/tasks` 时自动发生：**

1. partner-gateway：Token、capability、限流 → 注入上下文  
2. open-api-service **治理平面**：创建 `api_invocation`（开始）  
3. open-api-service **执行平面**：校验 body → 幂等 → 调 SVMP → 写 `open_task`  
4. **治理平面**：更新 invocation（结束码、耗时、可选 SVMP span）  
5. 返回统一 `{ code, message, data, requestId }`

业务 Controller **不重复写**「记日志、记指标」代码，由 **InvocationPipeline** 统一完成。

---

## 3. 契约层 vs 实现层

### 3.1 必须定义的内容（契约层）

| 对象 | 存放位置 | 用途 |
|------|----------|------|
| 每个 operation 的 path/method | OpenAPI + `api_operation` 表 | Partner 集成、代码生成、治理统计 |
| 请求/响应 schema | OpenAPI `components/schemas` | 入参校验、文档 |
| path → capability | partner-gateway + `api_operation.required_capability` | 40301 |
| 业务错误码 | external §9 | 40001–50002 |

### 3.2 不必逐项手写的内容（实现层）

| 避免 | 推荐 |
|------|------|
| 14 个 Controller 各抄一套 try/catch + 日志 | `OpenApiController` + `InvocationPipeline` |
| 14 套独立审计表 | 一张 `api_invocation` + 可选 `api_invocation_span` |
| 每个 capability 一个微服务 | 同一服务内 `TaskHandler`、`InstanceHandler`、`ExportHandler` |

### 3.3 实现分层（推荐包结构）

```text
com.vtc.openapi
├── governance/
│   ├── ApiCatalogService          # 读 api_operation，校验 operation 是否已发布
│   ├── InvocationService          # 创建/完成 api_invocation
│   ├── InvocationContext          # partnerId, requestId, operationId, timing
│   └── metrics/PartnerMetrics     # 按 Partner/operation 聚合（P1）
├── pipeline/
│   └── InvocationPipeline         # 环绕执行：审计 → 业务 → 审计
├── handler/
│   ├── TaskHandler                # POST/GET tasks
│   ├── InstanceHandler            # search / verify / remediate ...
│   └── ExportHandler              # exports（P2）
├── adapter/
│   └── SvmpEngineAdapter          # 对内 SVMP；span 记入 invocation
├── partner/                       # 注册、Token（Agent D）
└── ui/open/                       # 薄 Controller，只调 Pipeline
```

---

## 4. API 全生命周期（治理平面）

| 阶段 | 管理内容 | 存储/模块 | 阶段 |
|------|----------|-----------|------|
| **注册** | Partner、capabilities、凭证 | `partner*` 表 | P0 |
| **发布** | API 版本、operation 上架 | `api_operation` | P0 种子数据，P2 控制台 |
| **授权** | Token、capability、限流 | partner-gateway + `partner` | P0 |
| **调用** | 每次入站 REST | `api_invocation` | P0 |
| **执行** | 业务 + SVMP | 执行平面 Handler | P0 |
| **出站** | Webhook 投递 | `webhook_delivery_log` | P1 |
| **观测** | 成功率、QPS、P99 | 指标 / 报表 API | P1 |
| **审计** | 实例状态变更 | `api_invocation` + 业务审计字段 | P1 |
| **退役** | Partner DISABLED、API sunset | `partner.status`、`api_operation.status` | P2 |

Partner 可见行为仍以 [external 规范](../external/开放平台API接口规范.md) 为准；治理平面 **不替代** 对外契约，只 **记录与管控** 调用过程。

---

## 5. 数据模型（治理平面 · P0 最小集）

### 5.1 `api_operation` — API 目录（元数据）

与 OpenAPI `operationId` 对齐，**不是**每个接口一张业务大表。

| 字段 | 类型 | 说明 |
|------|------|------|
| operation_id | VARCHAR(64) PK | 如 `createTask`，同 OpenAPI |
| api_version | VARCHAR(16) | 如 `1.0.0` |
| http_method | VARCHAR(8) | GET / POST |
| path_pattern | VARCHAR(256) | 如 `/api/open/v1/tasks` |
| required_capability | VARCHAR(64) | 如 `TASK_WRITE` |
| domain | VARCHAR(32) | TASK / INSTANCE / EXPORT / AUTH |
| status | VARCHAR(16) | PUBLISHED / DEPRECATED / DISABLED |
| published_at | TIMESTAMP | 上架时间 |

**初始化**：由 OpenAPI 生成种子 SQL 或 Liquibase，避免手工漏登记。

### 5.2 `api_invocation` — 单次调用记录（核心）

| 字段 | 类型 | 说明 |
|------|------|------|
| invocation_id | VARCHAR(64) PK | 内部 ID |
| request_id | VARCHAR(64) | 与响应 `requestId`、网关 `X-Request-Id` **一致** |
| partner_id | VARCHAR(64) | 来自 `X-Partner-Id` |
| operation_id | VARCHAR(64) | 关联 `api_operation` |
| http_method | VARCHAR(8) | |
| request_path | VARCHAR(512) | 实际路径 |
| response_code | INT | 业务 `code`（0 成功） |
| http_status | INT | 通常 200 |
| latency_ms | INT | 端到端耗时 |
| client_ip | VARCHAR(64) | 可选 |
| error_message | VARCHAR(512) | code≠0 时摘要 |
| resource_type | VARCHAR(32) | 可选：TASK / INSTANCE |
| resource_id | VARCHAR(128) | 可选：taskId / vulInfoID |
| started_at | TIMESTAMP | |
| finished_at | TIMESTAMP | |

**不默认存完整 request/response body**（合规需要时再增 `api_invocation_payload` 表，P2）。

### 5.3 `api_invocation_span` — 对内调用子链路（P1 可选）

| 字段 | 类型 | 说明 |
|------|------|------|
| span_id | VARCHAR(64) PK | |
| invocation_id | VARCHAR(64) FK | |
| span_type | VARCHAR(32) | SVMP_CREATE_TASK / SVMP_DISPOSAL / REDIS / DB |
| target | VARCHAR(256) | 如 `vul-pass POST /task/create` |
| success | BOOLEAN | |
| latency_ms | INT | |
| error_message | VARCHAR(512) | |

用于「调用全生命周期」中 **平台 → SVMP** 一段的可见性。

### 5.4 与现有业务表关系

```text
api_invocation (一次 Partner HTTP 调用)
    ├── 可能创建/更新 open_task
    ├── 可能更新 open_vuln_instance
    └── 可能触发 webhook_delivery_log（异步，另记一条出站 invocation 或专用表）
```

---

## 6. InvocationPipeline 行为约定

### 6.1 伪代码

```text
handle(request):
  ctx = buildContext(X-Partner-Id, X-Request-Id, operationId)
  invocation = invocationService.start(ctx)
  try:
    validateSchema(request)           // OpenAPI / Bean Validation
    data = handler.execute(ctx, body) // TaskHandler / InstanceHandler
    return wrapSuccess(data, ctx.requestId)
  catch BusinessException e:
    return wrapError(e.code, e.message, ctx.requestId)
  catch Exception e:
    return wrapError(50001, "engine error", ctx.requestId)
  finally:
    invocationService.finish(invocation, responseCode, latencyMs)
```

### 6.2 与 partner-gateway 分工

| 项 | partner-gateway | open-api-service 治理平面 |
|----|-----------------|---------------------------|
| 40101 / 40301 / 42901 | ✅ 产生 | 可记录「未到达业务层」的拒绝（P1：网关异步写 invocation 或 gateway_access_log） |
| 40001 / 40901 / 50001 | — | ✅ 执行平面产生，invocation 记 `response_code` |
| requestId | 生成或透传 | **原样**写入响应与 `api_invocation` |

P0 可只记录 **已进入 open-api-service** 的调用；网关拒绝的统计放 P1。

---

## 7. Handler 与 capability 的关系

| capability | Handler | 说明 |
|------------|---------|------|
| TASK_WRITE | TaskHandler.create | 一种实现覆盖 1 个 operation |
| TASK_READ | TaskHandler.get / list | 可共用 TaskHandler |
| INSTANCE_* | InstanceHandler | verify/remediate/archive 可共用「处置」内核 + 动作参数 |
| EXPORT_READ | ExportHandler | P2 |
| EVENT_SUBSCRIBE | 无入站 REST | Webhook 出站配置；不产生 Partner 入站 invocation |

**实例写接口** IO 不同，但可共用：

- 路径变量 `vulInfoID`  
- 统一 `InstanceAction` 枚举（VERIFY / REMEDIATE / ARCHIVE / VERIFY_FIX）  
- 统一前置状态校验（状态机）  

不必 6 个接口 6 份复制粘贴代码。

---

## 8. 分阶段交付（治理平面）

| 阶段 | 执行平面 | 治理平面 |
|------|----------|----------|
| **P0** | tasks CRUD + SVMP + partner 隔离 | `api_operation` 种子 + `api_invocation` + `InvocationPipeline` + requestId 贯穿 |
| **P1** | 实例 lifecycle + Webhook | `api_invocation_span`、Partner 调用报表、Webhook 投递状态 |
| **P2** | exports | 配额统计、API DEPRECATED、可选 payload 归档 |
| **P3** | — | 告警、SLA、控制台大盘 |

**P0 验收（治理）**

- [ ] 每次成功的 `POST /tasks` 在 `api_invocation` 有记录，且 `request_id` 与响应一致  
- [ ] 按 `partner_id` 可统计调用次数与失败率（SQL 或简单管理 API）  
- [ ] 无「每个 Controller 手写审计」——审计仅在 Pipeline  

---

## 9. 管理 / 查询 API（内部 · 可选 P1）

供运营或集成后台使用，**不**对 Partner 暴露。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/internal/admin/invocations` | 分页查询调用记录（filter: partnerId, operationId, code, 时间） |
| GET | `/internal/admin/invocations/{invocationId}` | 详情 + spans |
| GET | `/internal/admin/partners/{partnerId}/stats` | 成功率、QPS、Top 错误码 |
| GET | `/internal/admin/api-operations` | 已发布 API 目录 |

---

## 10. 与 multi-agent 开发的衔接

| Agent | 范围 | 与本文关系 |
|-------|------|------------|
| D | Token + Partner 注册 | 治理平面「注册」阶段 |
| E | partner-gateway | 治理平面「授权」阶段；P1 记录 401/403 |
| **F（修订）** | 业务 P0 + **InvocationPipeline** | 执行平面 + **必须**落 `api_invocation` |
| G | 联调 | 验收 requestId、invocation 表、两家 Partner 隔离 |

修订版 Prompt F 见 [multi-agent-执行Prompts.md](./multi-agent-执行Prompts.md) § Prompt F。

---

## 11. 常见误区

| 误区 | 正确理解 |
|------|----------|
| 每个 OpenAPI operation 一个 Service 类 | 按 **领域** 分 Handler，按 **operation** 登记元数据 |
| capability 等于独立部署单元 | capability 是 **权限**，不是模块边界 |
| 治理 = 另起一个「API 网关产品」 | 治理是 open-api-service **内置能力**，partner-gateway 仍只做连接层 |
| 监控接口要给 Partner 调 | 监控是 **internal admin**；Partner 仍用 external §5 |

---

## 12. 相关文档索引

| 文档 | 路径 |
|------|------|
| 组件职责总览 | [组件职责与接口映射.md](./组件职责与接口映射.md) |
| 模块与接口清单 | [partner-gateway与open-api-service-模块与接口清单.md](./partner-gateway与open-api-service-模块与接口清单.md) |
| Multi-Agent Prompts | [multi-agent-执行Prompts.md](./multi-agent-执行Prompts.md) |
| 第三方契约 | [开放平台API接口规范.md](../external/开放平台API接口规范.md) |
