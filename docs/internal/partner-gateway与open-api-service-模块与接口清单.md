# partner-gateway 与 open-api-service · 模块与接口清单

> **定位**：Partner 集成栈双模块的目录结构、职责边界与完整接口对照，供研发落地与联调。  
> **相关文档**：[组件职责与接口映射](./组件职责与接口映射.md) · [开放平台API治理与调用生命周期](./开放平台API治理与调用生命周期.md) · [multi-agent 执行 Prompts](./multi-agent-执行Prompts.md) · [开放平台 API 接口规范](../external/开放平台API接口规范.md) · [OpenAPI](../../openapi/v1/openapi.yaml)

**代码路径**

| 模块 | 仓库路径 | Nacos 服务名 | 包名 |
|------|----------|--------------|------|
| partner-gateway | `project_backend/svmp/partner-gateway` | `partner-gateway` | `com.vtc.openplatform.gateway` |
| open-api-service | `project_backend/svmp/open-api-service` | `open-api-service` | `com.vtc.openapi` |

**图例**：✅ 已实现 · 🔧 骨架/TODO · 📄 契约待实现 · ⛔ 禁止公网暴露

---

## 1. 总体链路

```text
Partner（HTTPS 公网）
        │
        ▼
partner-gateway ──路由──► open-api-service ──SvmpEngineAdapter──► vul-pass 等 SVMP 模块
  │ Partner Token 校验         │ Token 签发 / 业务 / Webhook
  │ capability / 限流          │ Partner 注册 / 凭证 / 管理 API
  │ 注入 X-Partner-Id          │
  │                            └── Redis partner:token:*（签发写入、网关读取）
  └── Redis 读 Token

morningglory / clover：⛔ 不参与 Partner 流量（零侵入）
```

**强制规则**

| 规则 | 负责模块 |
|------|----------|
| Token 签发 | 仅 **open-api-service** |
| Partner 上下文 | 仅信任 **partner-gateway** 注入的 `X-Partner-Id` |
| SVMP 调用 | 仅 **open-api-service**（`SvmpEngineAdapter`） |
| 40101 / 40301 / 42901 | **partner-gateway** |
| 400xx / 40901 / 500xx 业务码 | **open-api-service** |

---

## 2. partner-gateway

### 2.1 职责

| 负责 | 不负责 |
|------|--------|
| 公网 TLS、独立域名 | Token 签发 |
| 路由 `/oauth/token`、`/api/open/v1/**` | Partner 注册 / 业务 |
| Partner Token 校验（Redis / introspect） | SVMP 调用 |
| capability 拦截 G4–G5 | Webhook 出站 |
| 按 Partner 限流 G7 | |
| 注入 `X-Partner-Id`、`X-Request-Id` | |

### 2.2 目录结构

```text
partner-gateway/
├── pom.xml
├── README.md
├── src/main/java/com/vtc/openplatform/gateway/
│   ├── ApplicationStart.java
│   ├── PartnerGatewayConstants.java
│   ├── PartnerCapability.java
│   ├── PartnerCapabilityMatcher.java      # G4–G5 路径→能力
│   ├── PartnerTokenResolver.java          # Redis / Feign introspect
│   ├── PartnerRateLimiter.java            # G7
│   ├── dto/PartnerTokenContext.java
│   ├── filter/PartnerAuthFilter.java      # G1–G7 全局过滤器
│   └── infra/feign/IOpenApiIntrospectClient.java
└── src/main/resources/
    ├── bootstrap.yml
    └── application.yml
```

### 2.3 Nacos 路由（公网）

| 序号 | 路径 | 目标 | Partner 鉴权 |
|------|------|------|--------------|
| R1 | `/api/open/v1/**` | `lb://open-api-service` | ✓ |
| R2 | `/oauth/token` | `lb://open-api-service` | ✗ 白名单 |
| R3 | `/api/open/v1/oauth/token` | `lb://open-api-service` | ✗ 白名单 |
| — | `/internal/**` | **禁止** | — |

详见 `partner-gateway/README.md` Nacos 样例。

### 2.4 过滤器步骤（PartnerAuthFilter）

| 步骤 | 编号 | 动作 | 失败 code |
|------|------|------|-----------|
| 内网路径拦截 | — | `/internal/**` 拒绝 | 40101 |
| 白名单 | G1 | Token 路径跳过鉴权 | — |
| Token 校验 | G2 | Redis `partner:token:{sha256}` 或 Feign introspect | 40101 |
| 主体类型 | G3 | `subjectType == PARTNER` | 40101 |
| 能力匹配 | G4–G5 | `PartnerCapabilityMatcher` | 40301 |
| 上下文注入 | G6 | `X-Partner-Id`、`X-Request-Id`；可选剥离 Authorization | — |
| 限流 | G7 | `PartnerRateLimiter` | 42901 |

### 2.5 路径 → capability（G4–G5）

| 方法 | 路径 | capability | 阶段 |
|------|------|------------|------|
| POST | `/api/open/v1/tasks` | TASK_WRITE | P0 |
| GET | `/api/open/v1/tasks` | TASK_READ | P0 |
| GET | `/api/open/v1/tasks/{taskId}` | TASK_READ | P0 |
| POST | `/api/open/v1/instances/search` | INSTANCE_READ | P0 |
| GET | `/api/open/v1/instances/{vulInfoID}` | INSTANCE_READ | P0 |
| POST | `/api/open/v1/instances/{id}/verify` | INSTANCE_VERIFY | P1 |
| POST | `/api/open/v1/instances/verify:batch` | INSTANCE_VERIFY | P1 |
| POST | `/api/open/v1/instances/{id}/remediate` | INSTANCE_REMEDIATE | P1 |
| POST | `/api/open/v1/instances/{id}/archive` | INSTANCE_ARCHIVE | P1 |
| POST | `/api/open/v1/instances/{id}/verify-fix` | INSTANCE_VERIFY_FIX | P1 |
| POST | `/api/open/v1/instances/verify-fix:batch` | INSTANCE_VERIFY_FIX | P1 |
| GET | `/api/open/v1/exports/{exportId}` | EXPORT_READ | P2 |
| GET | `/api/open/v1/exports/{exportId}/download` | EXPORT_READ | P2 |
| GET | `/api/open/v1/tasks/{taskId}/exports` | EXPORT_READ | P2 |

### 2.6 集群内接口

本网关**不实现**业务 REST；仅 Feign 调用 open-api-service：

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/internal/token/introspect` | introspect-mode=feign 降级 |

---

## 3. open-api-service

### 3.1 职责

| 负责 | 不负责 |
|------|--------|
| Partner 注册、凭证、capabilities | 门户 IAM（clover） |
| Token 签发 / introspect / 吊销 | 网关 TLS / 限流 |
| 全部 `/api/open/v1/*` 业务（**Handler**，非每接口一套复制代码） | Partner 直连 SVMP |
| **API 调用治理**（`api_invocation`、InvocationPipeline） | 对 Partner 暴露监控 API |
| 内部管理 `/internal/admin/*` | |
| Webhook 出站 | |
| `SvmpEngineAdapter` 调 SVMP | |

> 双平面说明见 [开放平台API治理与调用生命周期](./开放平台API治理与调用生命周期.md)。

### 3.2 目录结构（DDD + 治理）

```text
open-api-service/
├── ui/
│   ├── open/OpenTaskUI.java              # 薄层 → InvocationPipeline
│   ├── auth/PartnerTokenUI.java
│   └── admin/PartnerAdminUI.java
├── pipeline/
│   └── InvocationPipeline.java           # 🆕 环绕：审计 + Handler + 统一响应
├── governance/
│   ├── InvocationService.java            # 🆕 api_invocation CRUD
│   ├── ApiCatalogService.java            # 🆕 api_operation
│   └── InvocationContext.java
├── handler/
│   └── TaskHandler.java                  # 🆕 领域用例（非每 path 一 Controller）
├── app/service/
│   ├── IOpenTaskAppService.java
│   ├── IPartnerTokenAppService.java
│   └── IPartnerAdminAppService.java
├── domain/
│   ├── partner/model/entity/
│   └── task/model/entity/OpenTaskDO.java
├── adapter/
│   └── SvmpEngineAdapter.java
├── infra/
│   ├── dao/                              # 含 api_operation, api_invocation
│   └── config/
└── common/                               # PartnerContext, OpenApiConstants
```

### 3.3 Token 与鉴权

| 方法 | 路径 | 调用方 | 实现类 | 状态 |
|------|------|--------|--------|------|
| POST | `/oauth/token` | Partner（经 gateway 白名单） | PartnerTokenUI | 🔧 |
| POST | `/api/open/v1/oauth/token` | 同上（别名） | PartnerTokenUI | 🔧 |
| POST | `/internal/token/introspect` | partner-gateway | PartnerTokenUI | 🔧 |
| POST | `/internal/partners/token` | 内网备选 | — | 📄 P0 |
| POST | `/internal/token/revoke` | 管理后台 | — | 📄 P2 |

**Token 响应**（§2.3 external）：`accessToken`、`tokenType=Bearer`、`expiresIn`、`partnerId`

**Redis 键（open-api-service 写入，partner-gateway 读取）**

| 键 | 值 |
|----|-----|
| `partner:token:{sha256(accessToken)}` | `{ subjectType, partnerId, capabilities, clientId, expiresAt }` |
| `partner:credential:{clientId}` | 凭证元数据（不含明文 secret） |

### 3.4 Partner 管理（内部）

前缀：`/internal/admin/partners` · UI：`PartnerAdminUI` · 状态：🔧 骨架

| 方法 | 路径 | 阶段 |
|------|------|------|
| POST | `/internal/admin/partners` | P0 |
| GET | `/internal/admin/partners` | P0 |
| GET | `/internal/admin/partners/{partnerId}` | P0 |
| PUT | `/internal/admin/partners/{partnerId}` | P0 |
| DELETE | `/internal/admin/partners/{partnerId}` | P1 |
| PUT | `.../capabilities` | P0 |
| PUT | `.../callback` | P1 |
| PUT | `.../rate-limit` | P1 |
| POST | `.../credentials` | P0 |
| GET | `.../credentials` | P0 |
| POST | `.../credentials/{id}/rotate` | P1 |
| DELETE | `.../credentials/{id}` | P1 |
| DELETE | `.../sessions` | P1 |

### 3.5 对外开放 REST（/api/open/v1）

Base Path：`/api/open/v1` · OpenAPI：[`openapi/v1/openapi.yaml`](../../openapi/v1/openapi.yaml)

#### 任务 · 排查

| 方法 | 路径 | operationId | UI / Service | capability | SVMP | 状态 |
|------|------|-------------|--------------|------------|------|------|
| POST | `/tasks` | createTask | OpenTaskUI | TASK_WRITE | POST `/task/create` | ✅ |
| GET | `/tasks` | listTasks | OpenTaskUI | TASK_READ | 平台库 | ✅ |
| GET | `/tasks/{taskId}` | getTask | OpenTaskUI | TASK_READ | GET `/task/progress` | ✅ |

**规则**：`(partner_id, ext_task_id)` 唯一；`extTaskId` **不下发** SVMP。

#### 实例 · 查询与生命周期

| 方法 | 路径 | capability | SVMP 适配 | 状态 |
|------|------|------------|-----------|------|
| POST | `/instances/search` | INSTANCE_READ | POST `/vuln/disposal/list` | 📄 |
| GET | `/instances/{vulInfoID}` | INSTANCE_READ | GET `/vuln/disposal/detail` | 📄 |
| POST | `/instances/{id}/verify` | INSTANCE_VERIFY | POST `/vuln/disposal/disposal` | 📄 P1 |
| POST | `/instances/verify:batch` | INSTANCE_VERIFY | 批量 disposal | 📄 P1 |
| POST | `/instances/{id}/remediate` | INSTANCE_REMEDIATE | disposal | 📄 P1 |
| POST | `/instances/{id}/archive` | INSTANCE_ARCHIVE | disposal | 📄 P1 |
| POST | `/instances/{id}/verify-fix` | INSTANCE_VERIFY_FIX | verify / 状态机 | 📄 P1 |
| POST | `/instances/verify-fix:batch` | INSTANCE_VERIFY_FIX | 同上 | 📄 P1 |
| POST | `/instances/{id}/unfixable-records` | INSTANCE_ARCHIVE | 转发 archive | 📄 P1 |

#### 数据外发

| 方法 | 路径 | capability | 状态 |
|------|------|------------|------|
| GET | `/exports/{exportId}` | EXPORT_READ | 📄 P2 |
| GET | `/exports/{exportId}/download` | EXPORT_READ | 📄 P2 |
| GET | `/tasks/{taskId}/exports` | EXPORT_READ | 📄 P2 |

### 3.6 集群内接口

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/internal/context/partner` | 降级用 Partner 上下文 | 📄 |
| POST | `/internal/events/publish` | 触发 Webhook | 📄 P1 |
| GET | `/internal/health` | HealthController | ✅ |

### 3.7 SvmpEngineAdapter → SVMP

| 开放平台动作 | SVMP 接口 | Adapter 方法 | 状态 |
|--------------|-----------|--------------|------|
| 创建任务 | POST `/task/create` | `createTask` | ✅ |
| 查询进度 | GET `/task/progress` | `getTaskProgress` | ✅ |
| 实例列表 | POST `/vuln/disposal/list` | `searchInstances` | 🔧 TODO |
| 实例详情 | GET `/vuln/disposal/detail` | `getInstanceDetail` | 🔧 TODO |
| 验证/修复/备案 | POST `/vuln/disposal/disposal` | `disposeInstance` | 🔧 TODO |
| 修复核验 | POST `/vuln/disposal/verify` | `verifyInstance` | 🔧 TODO |

Feign：`ISvmpEngineFeign` → Nacos `vul-pass`

### 3.8 Webhook 出站（open-api-service → Partner）

| eventType | capability | 阶段 |
|-----------|------------|------|
| TASK_COMPLETED / TASK_FAILED | EVENT_SUBSCRIBE | P1 |
| INSTANCE_STATUS_CHANGED / … | EVENT_SUBSCRIBE | P1 |
| EXPORT_READY | EVENT_SUBSCRIBE | P2 |

签名头：`X-Webhook-Signature`（HMAC-SHA256）

### 3.9 数据表（Liquibase · db/mysql）

| 表 | groovy 文件 | 说明 |
|----|-------------|------|
| `partner` | partner.groovy | Partner 主数据 |
| `partner_capability` | partner_capability.groovy | 能力集 |
| `partner_credential` | partner_credential.groovy | clientId / secret 哈希 |
| `partner_webhook_config` | partner_webhook_config.groovy | callbackUrl |
| `open_task` | open_task.groovy | 平台任务 ✅ |
| `partner_task_map` | partner_task_map.groovy | 幂等映射 ✅ |
| `open_vuln_instance` | open_vuln_instance.groovy | 实例映射 |
| `open_export` | open_export.groovy | 外发记录 |
| `webhook_delivery_log` | webhook_delivery_log.groovy | 回调日志 |

---

## 4. 模块间调用关系

```text
┌─────────────────┐     Redis partner:token:*      ┌──────────────────┐
│ partner-gateway │ ◄────────────────────────────► │ open-api-service │
│ PartnerAuthFilter│     Feign introspect (降级)    │ PartnerTokenUI   │
└────────┬────────┘                                └────────┬─────────┘
         │ X-Partner-Id                                   │ Feign
         ▼                                                ▼
┌─────────────────┐                              ┌──────────────────┐
│ open-api-service│                              │ vul-pass (SVMP)  │
│ OpenTaskUI 等   │ ── SvmpEngineAdapter ───────►│ /task/create 等  │
└─────────────────┘                              └──────────────────┘
```

| 调用方 | 被调用方 | 协议 | 用途 |
|--------|----------|------|------|
| Partner | partner-gateway | HTTPS | 公网入口 |
| partner-gateway | open-api-service | HTTP + LB | 路由业务 / Token |
| partner-gateway | Redis | TCP | Token 校验 |
| partner-gateway | open-api-service | Feign | introspect 降级 |
| open-api-service | Redis | TCP | Token 写入 |
| open-api-service | vul-pass | Feign | 扫描 / 处置 |
| open-api-service | clover（可选） | Feign | 名称解析，**非** Partner 鉴权 |

---

## 5. 错误码职责

| code | 含义 | 产生组件 |
|------|------|----------|
| 40101 | 鉴权失败 | partner-gateway |
| 40301 | 能力未开通 | partner-gateway |
| 42901 | 限流 | partner-gateway |
| 40001–40005 | 参数 / 状态机 | open-api-service |
| 40003 | 跨 Partner | open-api-service |
| 40901 | extTaskId 冲突 | open-api-service |
| 50001 | 引擎失败 | open-api-service |
| 50002 | Webhook 失败 | open-api-service |

凭证错误（`/oauth/token`）由 open-api-service 返回，**不经过** gateway 鉴权过滤器。

---

## 6. 分阶段交付

| 阶段 | partner-gateway | open-api-service |
|------|-----------------|------------------|
| **P0** | R1–R2、G1–G3、G6、独立域名 | Partner 表 + Token + §3.5 任务/实例读 |
| **P1** | G4–G5、G7 | 凭证轮换 + 实例写 + Webhook |
| **P2** | G8 HMAC | EXPORT + API Key |
| **P3** | G9 mTLS | IP 白名单配置 |

---

## 7. 实现快照（本清单创建时）

| 组件 | 状态 |
|------|------|
| partner-gateway 模块骨架 | ✅ 已建 |
| PartnerAuthFilter / TokenResolver / CapabilityMatcher | ✅ 骨架 |
| open-api-service DDD 包结构 | ✅ ui/app/domain/infra |
| OpenTaskUI P0 任务 API | ✅ |
| PartnerTokenUI / PartnerAdminUI | 🔧 TODO 业务逻辑 |
| Partner Liquibase 表 | ✅ groovy 已建 |
| SvmpEngineAdapter 实例/处置 | 🔧 TODO |
| morningglory / clover Partner 改造 | ⛔ 不实施 |

---

## 8. 相关文档

| 文档 | 路径 |
|------|------|
| 组件总览 | [组件职责与接口映射.md](./组件职责与接口映射.md) |
| 第三方规范 §2.3 Token | [开放平台API接口规范.md](../external/开放平台API接口规范.md) |
| OpenAPI 3.1 | [openapi/v1/openapi.yaml](../../openapi/v1/openapi.yaml) |
| partner-gateway README | [partner-gateway/README.md](../../project_backend/svmp/partner-gateway/README.md) |
| open-api-service README | [open-api-service/README.md](../../project_backend/svmp/open-api-service/README.md) |
