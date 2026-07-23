# partner-gateway / partner-admin / open-api-service / vul-pass 平台业务解耦改造方案（v3）

> 版本：v3.0  日期：2026-06-23
> 上一版：v2.0（2026-06-22，主张“不物理合并，partner-gateway 独立，open-api-service 暂留平台管理面 + mock”）
> 本版变更：正式引入 **partner-admin**，形成四服务目标架构：`partner-gateway` 入站网关执行面、`partner-admin` 平台治理管理面、`open-api-service` 纯 mock 业务服务、`vul-pass` 真实漏洞业务服务。
> 适用范围：`project_backend/svmp/partner-gateway`、`project_backend/svmp/open-api-service`、后续 `partner-admin`、`project_backend/svmp/vul-pass`、`project_frontend/asset/asset-openplatform-manage`、`project_frontend/asset/asset-manage-master`

---

## 0. 本版结论

本方案采纳新的四服务拆分：

```text
partner-gateway
  入站网关执行面
  - Partner API 唯一入口
  - Token 校验
  - 能力码拦截
  - 限流执行
  - 调用记录采集
  - 请求追踪
  - 路由到 mock 或 vul-pass

partner-admin
  平台治理管理面 + 查询面 + 异步治理 Worker
  - Partner 管理
  - 凭证管理
  - 能力码/接口目录/开发指南
  - 流控配置
  - Webhook 配置、投递执行、投递记录查询
  - 调用记录查询
  - 运营案件壳
  - Token 签发（短期）

open-api-service
  纯 mock 业务服务
  - 保留当前已上线完整 mock 能力
  - 风险排查 mock
  - 修复核验 mock
  - 接入测试 mock
  - 处置测试 mock
  - Export / Webhook / OperationCase mock 事件产生
  - 不再沉淀新的真实业务编排

vul-pass
  真实漏洞业务服务
  - 真实任务
  - 真实漏洞实例
  - 真实验证 / 处置 / 修复核验
  - 真实扫描编排
  - 真实业务 payload
```

核心判断：

1. **不物理合并 partner-gateway 与 open-api-service**：两者栈差异明显，partner-gateway 为 WebFlux/Spring Boot 2.6.3，open-api-service 为 Servlet MVC/Spring Boot 2.2.10 + esmp-support，硬合代价高。
2. **新增 partner-admin 承接平台管理面**：避免把管理 CRUD 塞进 partner-gateway，也避免 open-api-service 继续承担平台管理面。
3. **open-api-service 保留当前完整 mock**：当前 mock 能力已上线，可作为后续 vul-pass 接入的回滚基线。
4. **路由到 mock 或 vul-pass 由 partner-gateway 决策**：partner-gateway 是所有 Partner API 的唯一入口，负责入站治理和 route target 选择。
5. **Webhook 不由 partner-gateway 投递**：Webhook 是出站异步投递，归 partner-admin 的 dispatcher/worker 执行。

---

## 1. 背景与现状

### 1.1 v1 / v2 演进

| 版本 | 主张 | 后续修正 |
|---|---|---|
| v1 | 物理合并 partner-gateway + open-api-service 为 open-gateway | 重新摸底发现 WebFlux/Servlet 栈冲突明显，不宜硬合 |
| v2 | 不物理合并；partner-gateway 独立；open-api-service 暂留平台管理面 + mock | 用户决定新增 partner-admin，进一步拆出平台管理面 |
| v3 | 四服务架构：partner-gateway + partner-admin + open-api-service mock + vul-pass | 本版定稿 |

### 1.2 当前代码状态摘要

#### partner-gateway

- 路径：`project_backend/svmp/partner-gateway`
- 技术栈：Spring Boot 2.6.3 / Spring Cloud 2021.0.1 / WebFlux / Redis / Nacos
- 当前职责：Partner 鉴权、能力码拦截、路由转发、CORS、限流（默认关）
- 当前路由：`/api/open/v1/**`、`/oauth/token`、`/api/open/v1/oauth/token`、`/open-api-service/**` 均转发到 `lb://open-api-service`
- 核心类：`PartnerAuthFilter`、`PartnerTokenResolver`、`PartnerJwtSupport`、`PartnerCapability`、`PartnerCapabilityMatcher`、`PartnerRateLimiter`
- 主要问题：能力码硬编码、JWT 密钥硬编码、无调用记录采集、无 route-mode(mock/vul-pass) 配置

#### open-api-service

- 路径：`project_backend/svmp/open-api-service`
- 技术栈：Spring Boot 2.2.10 / Hoxton.SR4 / esmp-support / Servlet MVC / MyBatis-Plus / Kafka / Redis / MySQL
- 当前职责过重：Partner 契约实现、平台管理面、Token 签发/校验、调用记录、Webhook、运营案件、mock、task-center/vul-pass 适配
- 当前 mock：已完整上线，覆盖风险排查、修复核验、接入测试、处置测试、Export、Webhook、运营案件等联调闭环
- 当前模式：具备 `adapter-mode: mock / task-center / vul-pass` 三模式；早期 fixture-based mock（`adapter-mode: mock`）已弃用，**当下 mock 由 task-center 引擎实现**，即测试环境 `adapter-mode=task-center` 即为 mock 验收环境

#### 前端

- `asset-openplatform-manage`：qiankun 子应用，端口 13021，负责开放平台页面
- `asset-manage-master`：qiankun 主应用，端口 13001，注册 `openPlatform` 子应用
- 当前双通道：
  - Admin 通道 `/open-api-service` → 平台管理面
  - Partner 通道 `/api/open/v1` + `/oauth/token` → partner-gateway

---

## 2. 四服务职责边界

### 2.1 partner-gateway：入站网关执行面

partner-gateway 只做运行时入站治理，不做管理 CRUD，不做 Webhook 出站投递，不做漏洞业务。

职责：

| 职责 | 说明 |
|---|---|
| Partner API 唯一入口 | `/api/open/v1/**`、`/oauth/token` |
| Token 校验 | 校验 Bearer Token，读取 token context |
| 能力码拦截 | 根据 operation/capability 规则拦截，未授权返回 40301 |
| 限流执行 | QPS、日配额、能力级限额等在入口执行 |
| 幂等基础校验 | 识别 `Idempotency-Key`，可做基础去重/透传 |
| 请求追踪 | 生成/透传 `X-Request-Id` |
| Partner 上下文注入 | 注入 `X-Partner-Id` 等内部 Header |
| 调用记录采集 | 采集 invocation start/finish，写事件或异步落库 |
| 路由选择 | 根据 `route-mode`/路由注册表转发到 mock 或 vul-pass |
| CORS | 外部 Partner API 的跨域统一处理 |

不做：

- Partner 管理 CRUD；
- 凭证管理；
- 接口目录维护；
- Webhook 出站投递；
- Webhook 投递日志查询；
- 运营案件工作台；
- 漏洞任务/实例/修复核验业务。

### 2.2 partner-admin：平台治理管理面

partner-admin 承接 open-api-service 当前的通用平台管理能力，并承担 Webhook dispatcher / case shell / 查询面。

首批迁入能力：

| 能力 | 说明 |
|---|---|
| Partner 管理 | Partner CRUD、状态启停、类型维护 |
| 凭证管理 | clientId/clientSecret 生成、禁用、轮换 |
| Token 签发（短期） | `/oauth/token` 可由 partner-gateway 转发到 partner-admin；远期可迁认证服务 |
| 能力码配置 | capability registry、Partner 能力授权 |
| 接口目录 | `api_operation`、operationId/path/method/capability |
| 开发指南 | developer docs、文档链接、接入说明 |
| 流控配置 | Partner QPS、日配额、能力级限额配置；执行仍在 gateway |
| 调用记录查询 | 查询 `api_invocation`，采集由 gateway 负责 |
| Webhook 配置 | webhookUrl、secret、启停、签名配置 |
| Webhook 投递执行 | dispatcher/worker 消费业务事件，签名、投递、重试 |
| Webhook 投递记录查询 | 查询 `webhook_delivery_log` |
| 运营案件壳 | case_id、partner_id、case_type、timeline、关联 invocation/webhook |
| 运营案件工作台聚合 | 读取案件壳，按 case_type 调用 mock/vul-pass 业务 handler 获取 payload |

不做：

- 入站 Partner API 网关拦截；
- 漏洞真实任务、实例、修复核验编排；
- mock 业务状态机。

### 2.3 open-api-service：纯 mock 业务服务

open-api-service 保留当前已上线完整 mock 能力，作为联调/E2E/回归基线。

保留能力：

| 能力 | 说明 |
|---|---|
| 接入测试 mock | Partner 契约输入输出、任务创建、token 链路配合 |
| 风险排查 mock | `open-task`、mock 报告导入、任务工作台 payload |
| 处置测试 mock | verify/remediate/verify-fix/batch 状态机 |
| 修复核验 mock | verify-fix job、复扫 XML、allFixed/allUnfixed/compare |
| Export mock | mock 外发元数据与下载 |
| Webhook 事件产生 | 产生 `TASK_COMPLETED`、`EXPORT_READY`、`INSTANCE_VERIFY_FIX_COMPLETED` 等事件，投递由 partner-admin 执行 |
| OperationCase 业务 payload | 产生/提供 mock 案件业务详情，案件壳由 partner-admin 维护 |

逐步剥离：

- Partner 管理；
- 凭证管理；
- 接口目录；
- 开发指南；
- 流控配置；
- Webhook 投递执行与记录查询；
- 运营案件壳；
- 调用记录查询；
- Token 签发。

### 2.4 vul-pass：真实漏洞业务服务

vul-pass 承接真实业务能力。

职责：

- 真实任务创建与扫描编排；
- 真实漏洞实例查询；
- 真实验证、处置、修复核验；
- 真实 export 生成；
- 真实业务事件产生；
- 真实案件业务 payload；
- 与 vuln-task-center、扫描器、file-sharing-center 等对接。

---

## 3. 路由决策：由 partner-gateway 发出

### 3.1 结论

路由到 mock 或 vul-pass 的决策必须在 partner-gateway：

```text
Partner / 前端联调
  ↓
partner-gateway
  1. Token 校验
  2. 能力码拦截
  3. 限流
  4. 生成 requestId
  5. 采集 invocation start
  6. 根据 route-mode / route registry 选择后端
       mock     → open-api-service
       vul-pass → vul-pass
  7. 转发请求
  8. 采集 invocation finish
```

不建议继续保留：

```text
Partner → partner-gateway → open-api-service → mock 或 vul-pass
```

因为这会让 open-api-service 继续成为二级网关，违背“open-api-service 纯 mock 化”的目标。

### 3.2 route-mode 配置建议

短期配置：

```yaml
partner:
  gateway:
    route-mode: mock # mock | vul-pass
    routes:
      mock-target: lb://open-api-service
      vul-pass-target: lb://vul-pass
```

语义：

| route-mode | `/api/open/v1/**` 目标 | 用途 |
|---|---|---|
| `mock` | open-api-service | 当前联调/E2E/回归基线 |
| `vul-pass` | vul-pass | 后续真实漏洞业务链路 |

中期演进为 route registry：

```yaml
partner:
  gateway:
    route-registry:
      - business: vuln
        mode: mock
        prefix: /api/open/v1
        target: lb://open-api-service
      - business: vuln
        mode: vul-pass
        prefix: /api/open/v1
        target: lb://vul-pass
```

---

## 4. 调用记录 / 流控 / Webhook / 运营案件归属

### 4.1 调用记录

| 动作 | 服务 |
|---|---|
| 采集 invocation start/finish | partner-gateway |
| 写入 `api_invocation` | 短期可由 gateway 异步写 DB 或调用 partner-admin 内部接口；中期推荐发事件由 partner-admin 消费落库 |
| 查询调用记录 | partner-admin |
| 前端展示 | asset-openplatform-manage 流量治理页面 |

推荐链路：

```text
partner-gateway
  ↓ InvocationRecordedEvent
partner-admin consumer
  ↓
api_invocation
  ↓
/internal/admin/invocations 查询
```

短期可以先保持 open-api-service 查询接口不动，待 partner-admin 创建后迁移查询面。

### 4.2 流控

流控拆成配置与执行：

| 能力 | 服务 |
|---|---|
| 流控配置 CRUD | partner-admin |
| QPS/日配额/能力限额执行 | partner-gateway |
| 限流命中记录 | partner-gateway 采集 |
| 流控统计查询 | partner-admin |

流控必须发生在请求进入业务服务前，因此执行面不能放在 partner-admin 或 open-api-service。

### 4.3 Webhook

Webhook 是出站异步投递，不属于 partner-gateway。

| 能力 | 服务 |
|---|---|
| Webhook 配置管理 | partner-admin |
| Webhook Secret 轮换 | partner-admin |
| Webhook 业务事件产生 | open-api-service mock 或 vul-pass |
| Webhook 投递执行 | partner-admin dispatcher/worker |
| HMAC-SHA256 签名 | partner-admin dispatcher/worker |
| 重试 / 退避 | partner-admin dispatcher/worker |
| `webhook_delivery_log` 落库 | partner-admin |
| Webhook 投递记录查询 | partner-admin |

推荐链路：

```text
open-api-service mock 或 vul-pass
  ↓ OpenPlatformWebhookEvent
partner-admin webhook-dispatcher
  ↓ 读取 partner_webhook_config
  ↓ HMAC-SHA256 签名
  ↓ HTTP 投递 Partner webhookUrl
  ↓ 写 webhook_delivery_log
asset-openplatform-manage 查询展示
```

### 4.4 运营案件壳

| 内容 | 服务 |
|---|---|
| case_id / partner_id / case_type / primary_resource / status | partner-admin |
| timeline / invocation 关联 / webhook 关联 | partner-admin |
| 业务 payload | open-api-service mock 或 vul-pass |
| 工作台聚合 | partner-admin |

工作台查询链路：

```text
前端
  ↓
partner-admin /internal/admin/operation-cases/{caseId}/workspace
  ↓
读取案件壳 + timeline + invocation + webhook
  ↓
根据 case_type / route-mode 调用业务 handler
    route-mode=mock     → open-api-service
    route-mode=vul-pass → vul-pass
  ↓
聚合返回 workspace
```

---

## 5. 能力迁移清单

### 5.1 从 open-api-service 迁往 partner-admin

| 能力 | 当前 open-api-service 典型接口 | 目标 |
|---|---|---|
| Partner 管理 | `/internal/admin/partners` | partner-admin |
| 凭证管理 | `/internal/admin/partners/{id}/credentials` | partner-admin |
| Webhook Secret 轮换 | `/internal/admin/partners/{id}/webhook-secret/rotate` | partner-admin |
| 接口目录 | `/internal/admin/api-operations` | partner-admin |
| 开发指南 | `/internal/admin/developer-docs` | partner-admin |
| 调用记录查询 | `/internal/admin/invocations` | partner-admin |
| Webhook 投递记录查询 | `/internal/admin/webhook-deliveries` | partner-admin |
| Export 下载治理入口 | `/internal/admin/exports/{id}/download` | partner-admin 或后续 artifact/export 服务 |
| 流控策略/统计 | quota/stats 相关接口 | partner-admin 配置/查询，gateway 执行 |
| 运营案件壳 | `/internal/admin/operation-cases` | partner-admin |
| Token 签发 | `/oauth/token` | 短期 partner-admin，远期认证服务 |
| Token introspect | `/internal/token/introspect` | 尽量废弃；gateway 以 Redis 校验为主 |

### 5.2 保留在 open-api-service mock

| 能力 | 当前接口/页面 |
|---|---|
| 接入测试 | `MockE2eConsole` / `e2eRunner` / Partner 契约 mock |
| 风险排查 | `/internal/admin/mock-tasks`、`/internal/admin/open-tasks` mock 工作台 payload |
| 处置测试 | `/api/open/v1/instances/*/verify|remediate|verify-fix` mock |
| 修复核验 | `/internal/admin/mock-verify-fix`、verify-fix mock job |
| mock 报告导入 | NSFocus XML 预览/导入 |
| mock Export | mock 外发元数据和下载 |
| mock 业务事件 | TASK_COMPLETED / EXPORT_READY / INSTANCE_VERIFY_FIX_COMPLETED 事件产生 |
| mock 业务案件 payload | TASK_SCAN / INSTANCE_VERIFY / VERIFY_FIX / INSTANCE_BATCH 详情 |

### 5.3 后续迁往 vul-pass

| 能力 | 目标 |
|---|---|
| 真实任务 | vul-pass |
| 真实漏洞实例 | vul-pass |
| 真实验证/处置/修复核验 | vul-pass |
| 真实 export | vul-pass 或 export/artifact 服务 |
| 真实业务事件 | vul-pass 产生，partner-admin 投递 |
| 真实运营案件业务 payload | vul-pass |

---

## 6. 分阶段实施计划

### Phase 0：v3 架构定稿与验收基线确认

目标：确认当前 open-api-service mock 已作为上线基线。

任务：

1. 确认测试环境 `open-api.engine.adapter-mode=mock` 或使用 mock profile；
2. 补一份 mock 链路验收记录；
3. 明确 route-mode 后续由 partner-gateway 控制；
4. 明确 partner-admin 拆分边界。

验收：

- open-api-service mock 已上线；
- 前端四个入口可跑通：接入测试、风险排查、修复核验、处置测试；
- 流量治理、Webhook 记录、运营案件、Export 等治理面能查到 mock 产生的数据。

### Phase 1：partner-gateway route-mode 与入站治理补齐

目标：让 partner-gateway 成为 mock/vul-pass 的路由决策点。

任务：

1. 新增 `partner.gateway.route-mode=mock|vul-pass`；
2. 新增 mock target / vul-pass target 配置；
3. 保持 `/oauth/token` 短期转发到 open-api-service，后续切 partner-admin；
4. JWT 密钥配置化；
5. 调用记录采集设计（先事件模型，不一定立即落库）；
6. 保持真实 Token 链路优先，必要时仅本地支持 auth-bypass。

验收：

- route-mode=mock 时，Partner API 转发 open-api-service；
- route-mode=vul-pass 配置存在但可暂不启用；
- mock 链路不绕过 partner-gateway；
- 生产环境不存在 auth-bypass。

### Phase 2：创建 partner-admin 空壳并迁平台管理面第一批能力

目标：创建 partner-admin，先迁通用管理面，不碰 mock 业务。

首批迁移：

1. Partner 管理；
2. 凭证管理；
3. 能力码配置；
4. 接口目录；
5. 开发指南；
6. 流控配置；
7. Token 签发（短期）；
8. 调用记录查询。

原则：

- 不迁 mock 风险排查；
- 不迁 mock 修复核验；
- 不迁 mock 报告导入；
- 不迁 mock 工作台 payload。

验收：

- 前端 Partner 管理、接口目录、开发指南、流控策略页面指向 partner-admin 后可用；
- `/oauth/token` 可由 partner-gateway 转发 partner-admin；
- partner-gateway Token 校验仍可从 Redis 读取 token context。

### Phase 3：Webhook dispatcher 与运营案件壳迁 partner-admin

目标：把出站治理能力与 case shell 从 open-api-service 剥离。

任务：

1. 迁 Webhook 配置管理；
2. 迁 Webhook Secret 轮换；
3. 新建 partner-admin webhook-dispatcher；
4. mock/vul-pass 统一发布 `OpenPlatformWebhookEvent`；
5. partner-admin 消费事件，投递并写 `webhook_delivery_log`；
6. 迁运营案件壳；
7. 工作台聚合由 partner-admin 调 mock/vul-pass handler。

验收：

- mock 业务事件由 partner-admin 投递 Webhook；
- 推送记录页面查 partner-admin；
- 运营案件列表/工作台查 partner-admin；
- 业务 payload 仍来自 open-api-service mock。

### Phase 4：vul-pass 对接

目标：在 mock 稳定基线上接真实业务。

任务：

1. 对齐 Partner 契约与 vul-pass 内部接口；
2. partner-gateway route-mode=vul-pass 灰度；
3. vul-pass 实现真实任务/实例/处置/修复核验；
4. vul-pass 产生业务事件，partner-admin 负责投递；
5. partner-admin 工作台按 route-mode 聚合 vul-pass payload。

验收：

- route-mode=vul-pass 下 Partner API 全流程通过；
- route-mode=mock 可随时切回；
- mock 与 vul-pass 对外契约形状一致。

### Phase 5：open-api-service 纯 mock 化收口

目标：open-api-service 不再承载平台管理面和真实业务，只保留 mock。

任务：

1. 删除/下线已迁走的 admin 接口；
2. 移除真实 vul-pass/task-center adapter 或保留为测试分支；
3. 保留 mock 实现（当下由 task-center 引擎承载的 mock 能力）；早期 fixture-based mock 已弃用，不再保留；
4. 保留 mock 业务 handler；
5. 梳理数据库表归属，平台表迁 partner-admin，真实业务表迁 vul-pass，mock 表可独立库/独立 schema。

验收：

- open-api-service 只服务 route-mode=mock；
- partner-admin 可独立承担平台治理管理面；
- vul-pass 可独立承担真实业务。

---

## 7. 前端调整计划

### 7.1 短期保持路径兼容

为降低风险，前端短期路径保持：

| 前端通道 | 当前 baseURL | 后续代理目标 |
|---|---|---|
| Partner 通道 | `/api/open/v1`、`/oauth/token` | partner-gateway |
| Admin 通道 | `/open-api-service` | 先指 open-api-service，逐步切 partner-admin |

迁移时建议使用网关/nginx 兼容旧路径：

```text
/open-api-service/internal/admin/partners        → partner-admin
/open-api-service/internal/admin/api-operations  → partner-admin
/open-api-service/internal/admin/mock-tasks      → open-api-service mock
/open-api-service/internal/admin/mock-verify-fix → open-api-service mock
```

这样前端可以分批改，不需要一次性大改所有 API 文件。

### 7.2 中期新增运行时配置

新增：

```js
VUE_APP_PARTNER_ADMIN_BASE_URL=/partner-admin
VUE_APP_OPEN_MOCK_ADMIN_BASE_URL=/open-api-service
```

前端 API 分组：

| API 文件 | 目标 |
|---|---|
| `partner.js` | partner-admin |
| `catalog.js` | partner-admin |
| `invocation.js` | partner-admin（invocation/webhook 查询） |
| `quota.js` | partner-admin |
| `operationCase.js` | partner-admin 壳 + workspace 聚合 |
| `mockTask.js` | open-api-service mock |
| `mockVerifyFix.js` | open-api-service mock |
| `openPartnerApi.js` | partner-gateway（Partner 通道） |
| `verifyFix.js` | 阶段性：mock 时 open-api-service；real 时 partner-admin 聚合/vul-pass handler |

### 7.3 枚举注册表化

后续由 partner-admin 提供：

- capabilities；
- operation catalog；
- webhook event types；
- case types；
- response codes；
- scanner types。

前端 `src/constants/openPlatformDisplay/enums.js` 从硬编码逐步改为启动时加载 + 本地兜底。

---

## 8. 数据归属建议

### 8.1 partner-admin 平台治理库

建议归 partner-admin：

- `partner`
- `partner_credential`
- `partner_capability`
- `partner_webhook_config`
- `api_operation`
- `api_invocation`
- `webhook_delivery_log`
- `open_operation_case`
- `open_operation_case_event`
- `open_operation_case_target`
- quota / rate limit 相关表
- developer docs 相关表

### 8.2 open-api-service mock 库

建议只保留 mock 需要的表（当下 mock 由 task-center 引擎实现，不再依赖早期 fixture bundle）：

- mock task；
- mock task sub；
- mock vuln instance；
- mock verify fix job；
- mock export。

可继续沿用现库过渡，但最终建议独立 schema，避免 mock 与真实数据混用。

### 8.3 vul-pass 真实业务库

建议归 vul-pass：

- 真实任务；
- 真实任务子任务；
- 真实扫描结果；
- 真实漏洞实例；
- 真实漏洞实例日志；
- 真实修复核验作业；
- 真实 export/artifact 业务数据。

---

## 9. 风险与回滚

| 风险 | 缓解 | 回滚 |
|---|---|---|
| partner-admin 拆分导致前端大面积改动 | 先用网关/nginx 做旧路径兼容，再逐步改前端 baseURL | 路由回 open-api-service |
| route-mode=vul-pass 不稳定 | mock 保持可用，route-mode 可切回 mock | 切回 mock |
| 调用记录上移 partner-gateway 后性能受影响 | 异步事件/Kafka/Redis Stream，不阻塞请求 | 临时回 open-api-service 写 invocation |
| Webhook dispatcher 迁移造成重复投递 | 事件幂等 key + delivery 唯一约束 | 暂停新 dispatcher，回 open-api-service 投递 |
| Token 签发迁 partner-admin 影响登录 | 先保持 `/oauth/token` 旧路径兼容，灰度切 partner-admin | 回 open-api-service 签发 |
| 数据表迁移风险 | 双写 + 对账 + 分批切读 | 回退读旧表 |

---

## 10. 验收标准

### Phase 0 / 1 验收

- 当前 open-api-service mock 能力已上线；
- route-mode=mock 时，Partner API 经 partner-gateway 进入 open-api-service mock；
- 接入测试、风险排查、修复核验、处置测试均可跑通；
- 治理页面能查到调用记录、Webhook 投递、运营案件、Export。

### Phase 2 验收

- Partner 管理、凭证管理、接口目录、开发指南、流控配置、调用记录查询迁 partner-admin；
- `/oauth/token` 可由 partner-admin 签发并写入 Redis token context；
- partner-gateway 可正常校验 partner-admin 签发的 token。

### Phase 3 验收

- Webhook 投递由 partner-admin dispatcher 执行；
- open-api-service mock / vul-pass 只产生业务事件；
- 运营案件壳由 partner-admin 维护，业务 payload 由 mock/vul-pass 提供。

### Phase 4 验收

- route-mode=vul-pass 下真实漏洞业务全流程通过；
- route-mode=mock 可作为回滚基线；
- mock 与 vul-pass 对外契约保持一致。

### Phase 5 验收

- open-api-service 只保留 mock 业务；
- partner-admin 独立承担平台治理管理面；
- vul-pass 独立承担真实漏洞业务；
- 新接入非漏洞业务时，平台层不需要新增硬编码业务枚举。

---

## 11. 下一步建议

立即进入 **Phase 0 / Phase 1**：

1. 补充当前 mock 上线验收记录；
2. 在 partner-gateway 设计并实现 `route-mode=mock|vul-pass`；
3. 确认所有 Partner API 不绕过 partner-gateway；
4. 梳理 partner-admin 首批接口清单与建项方案；
5. 输出 P1 施工清单：涉及 partner-gateway 配置、open-api-service mock 配置、前端代理配置、验收脚本。

建议不要直接进入 vul-pass 对接。mock 是后续真实链路的回滚基线，必须先固化为验收基线。
