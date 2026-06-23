# 网关归位与平台/业务解耦改造方案（v2 · 基于迭代后现状重写）

> 版本：v2.0  日期：2026-06-22
> 上一版：v1.0（2026-06-19，主张"物理合并为一个 open-gateway"）
> 本版变更：基于近期前后端迭代重新摸底，**放弃物理合并**，改为"职责归位 + 接口对齐 + 分期推进"，服从"先保证 mock 完整，再 vul-pass 对接"的诉求
> 适用范围：partner-gateway、open-api-service、vul-pass、vuln-task-center、asset-openplatform-manage、asset-manage-master

---

## 0. 为什么重写（v1 → v2 的关键转变）

v1 主张把 partner-gateway + open-api-service 物理合并为一个 `open-gateway`。近期迭代后重新摸底，发现四个改变假设的事实：

| 事实 | 对 v1 的影响 |
|---|---|
| partner-gateway 是独立 WebFlux 网关（Spring Boot **2.6.3** + Spring Cloud 2021.0.1），**不继承 esmp-support**，正是为避开 Servlet 冲突才独立建项 | 物理合并要解决 reactive/servlet 栈冲突，代价高 |
| open-api-service 是 Servlet MVC（Spring Boot **2.2.10** + Hoxton.SR4），继承 `esmp-support:3.0.2-SNAPSHOT` | 两栈代际差大，硬合等于重写其中一个 |
| partner-gateway 已是纯转发网关（4 条路由全部 `lb://open-api-service`），职责干净 | 真正的污染在 open-api-service，不在网关 |
| open-api-service 的 **mock 已完整**（`adapter-mode: mock` 全契约覆盖），缺的是 partner-gateway 层 mock + 当前默认 mode 是 task-center | v1"先保证 mock 完整"的前提已部分成立，只需补齐 |

**v2 结论：不物理合并。** 保持 partner-gateway 独立网关，把散在 open-api-service 的网关职责归位，open-api-service 退化为"业务服务 + mock 桩 + 通往 vul-pass 的适配层"。这样既不碰栈冲突，又能达成解耦目标。

---

## 1. 现状摸底（迭代后真实状态）

### 1.1 partner-gateway（端口 35770，WebFlux）

- **栈**：Spring Boot 2.6.3 / Spring Cloud 2021.0.1 / WebFlux / Nacos / Redis(db=2)
- **职责**：Partner 鉴权 + 能力码拦截 + 路由转发 + 限流(默认关) + CORS
- **路由**：4 条全部转发到 `lb://open-api-service`（`/api/open/v1/**`、`/oauth/token`、`/api/open/v1/oauth/token`、`/open-api-service/**`）
- **核心类**：`PartnerAuthFilter`(G1–G6, order=-100)、`PartnerTokenResolver`(redis/feign 双模式)、`PartnerJwtSupport`(JWT 校验,密钥硬编码)、`PartnerCapability`(9 项枚举)、`PartnerCapabilityMatcher`(17 条硬编码 AntPathMatcher 规则)、`PartnerRateLimiter`
- **关键缺陷**：
  - **无 mock 机制**（无 adapter-mode，无降级）
  - **无调用记录**（`api_invocation` 在 open-api-service 侧记）
  - **JWT 密钥硬编码** `SECURITY_KEY`（与 spore JWTUtils 一致，但散在两处）
  - **能力码权威定义在此**（9 项枚举 + 17 条规则），与 open-api-service 的 `partner_capability` 表无单一数据源
  - 无 GlobalExceptionHandler（错误由 Filter 内 `OpenApiErrorWriter` 直接写 HTTP 200 + code）

### 1.2 open-api-service（端口 35780，Servlet MVC）

- **栈**：Spring Boot 2.2.10 / Hoxton.SR4 / esmp-support 3.0.2-SNAPSHOT / MyBatis-Plus / Kafka / Nacos / Redis(db=2) / MySQL(`open_api`)
- **职责**（过载）：Partner 契约实现 + 管理面 + Token 签发/校验 + 调用记录 + 三模式引擎适配 + 漏洞业务全套
- **Controller**：17 个 / 76 接口
  - `/api/open/v1/**`（Partner 契约，17 接口）：OpenTaskUI / OpenInstanceUI / OpenExportUI
  - `/oauth/token` + `/internal/token/introspect`（PartnerTokenUI）
  - `/internal/admin/**`（管理面，54 接口）：PartnerAdminUI / InvocationAdminUI / OpenTaskAdminUI / OpenVulnInstanceAdminUI / OperationCaseAdminUI / VerifyFixAdminUI / ApiCatalogAdminUI / **MockTaskAdminUI** / **MockVerifyFixAdminUI** / WebhookTestAdminUI
  - `/internal/svmp/v1/verify-fix/jobs/{id}/completed`（SvmpVerifyFixNotifyUI）
- **FeignClient**：4 个 → vul-pass(2)、vuln-task-center(1)、file-sharing-center(1)
- **三模式适配**（`@ConditionalOnProperty(open-api.engine.adapter-mode)`）：
  - `vul-pass`（代码默认 matchIfMissing=true）
  - `mock`（`application-mock.yml`，**已完整实现**）
  - `task-center`（`application-task-center.yml`，**当前 application.yml 默认**）
- **表**：11 张平台表 + 13 张漏洞业务表，同库 `open_api`，Liquibase Groovy 管理（18 文件），无自定义 Mapper XML
- **mock 完整性**：✅ 全契约覆盖（SvmpEngineAdapterMockImpl + VulnInstanceGatewayMockImpl + MockTaskAdminUI + MockVerifyFixAdminUI + fixture 机制），含 auto/manual 两模式、webhook 外发、案件通知

### 1.3 前端 asset-openplatform-manage（端口 13021，qiankun 子应用 `openPlatform`）

- 双通道：Admin 通道 `/open-api-service`(→平台网关:7000) + Partner 通道 `/api/open/v1`(→partner-gateway:35770)
- 22 路由，20 页面；mock 入口：`MockE2eConsole`(接入测试) / `MockManualIngest`(半人工导入) / `VerifyFixWorkspace`(核验)
- 枚举高度集中：`src/constants/openPlatformDisplay/enums.js`（CAPABILITIES/WEBHOOK_EVENT_TYPES/OPERATION_CASE_TYPES/API_OPERATIONS 等全硬编码）
- `OpenSocOrchestration.vue` 仍存在但**已无路由挂载**（遗留代码）

### 1.4 前端 asset-manage-master（端口 13001，qiankun 主应用）

- 注册 `openPlatform` 子应用：`container=#subapp-viewport2`，`activeRule=/openPlatform`，entry 由 `window.conf` 下发
- 隐藏路由 `open-platform-hidden-routes.js`（9 条详情/工作台路由，`RouteView` 占位，不依赖 DB menu）
- proxy：`/open-api-service`→7000、`/api/open/v1`+`/oauth/token`→35770、`/openPlatform`→13021

### 1.5 三个关键判断

1. **mock 完整性**：open-api-service mock ✅ 完整；缺的是 **partner-gateway 无 mock** + **当前默认 mode=task-center 不是 mock**。测试期联调需切回 mock。
2. **网关职责倒挂**：Token 签发/校验、调用记录、能力码权威都错位在 open-api-service；partner-gateway 反而只做转发。
3. **能力码无单一数据源**：枚举在 partner-gateway，授权在 open-api-service 表，拦截规则在 partner-gateway 硬编码，三处手工同步。

---

## 2. 设计原则（v2 调整）

1. **不物理合并**：partner-gateway 保持独立 WebFlux 网关；避免 reactive/servlet 栈冲突。
2. **职责归位**：把散在 open-api-service 的网关职责（Token 签发/校验、调用记录、能力码权威）逐步上移到 partner-gateway 或独立认证服务；open-api-service 退化为业务服务。
3. **mock 优先**：先确保 mock 端到端可用（partner-gateway 层 mock + 默认 mode 切回 mock），再推 vul-pass 真实对接。
4. **注册表驱动**：能力码、Webhook 事件、案件类型由业务注册，平台不硬编码枚举。
5. **业务下沉**：漏洞业务表/编排/契约实现下沉 vul-pass（远期，vul-pass 就绪后）。
6. **判据不变**：一个字段/表/事件类型，换个非漏洞业务就用不上，就不该在平台层。

---

## 3. 目标架构（v2）

```
┌─────────────────────────────────────────────────────────────────┐
│  partner-gateway  (独立 WebFlux 网关, 35770)                      │
│  公司级公共底座 · 零业务语义                                       │
│  ─ 入站治理: TLS / 限流 / Token校验 / 能力码拦截 / X-Partner-Id注入 │
│  ─ 路由:     /api/open/v1/**  → open-api-service(业务/mock)       │
│             /oauth/token      → 认证服务(签发)                    │
│  ─ 调用记录: api_invocation (从 open-api-service 上移)            │
│  ─ 能力码权威: PartnerCapability 注册表 (从硬编码改配置/接口加载)   │
│  ─ mock旁路:  gateway.mock.enabled 时跳过Token/能力码强校验        │
└──────────┬────────────────────────────────────┬─────────────────┘
           │ adapter-mode=mock                  │ adapter-mode=vul-pass
           ▼                                    ▼
┌────────────────────────────────────────┐   ┌──────────────────────────────┐
│ open-api-service (业务服务 + mock桩)     │   │ vul-pass (+vuln-business)     │
│ ─ Partner契约实现(mock分支已完整)        │   │ ─ 漏洞业务真实实现              │
│ ─ 管理面 /internal/admin/**             │   │ ─ open_task/open_vuln_instance │
│ ─ 三模式适配: mock / vul-pass / task    │   │   /open_verify_fix_job/open_export│
│ ─ 漏洞业务表(暂留,远期下沉)              │   │ ─ autoVerify/UNION/INTERSECT   │
│ ─ 注册项: 向网关注册能力码/事件/案件类型  │   │   /scan_phase/双轨/transition  │
└────────────────────────────────────────┘   └──────────────────────────────┘

认证服务(远期): OAuth Token 签发/刷新/吊销 (从 open-api-service 上移)
vuln-task-center(18087): 扫描治理, 由 vul-pass 调用
file-sharing-center: 外发文件
```

### 3.1 职责归位对照

| 职责 | 当前位置 | 目标位置 | 阶段 |
|---|---|---|---|
| Token 签发（`/oauth/token`） | open-api-service `PartnerTokenUI` | 认证服务（远期）/ 暂留 open-api-service | P3 |
| Token 校验（introspect） | open-api-service + partner-gateway 双写 | partner-gateway redis 模式为主 | P2 |
| Token Redis 存储 | open-api-service `PartnerTokenRedisStore` | 暂留（partner-gateway 读） | P2 |
| 调用记录 `api_invocation` | open-api-service `InvocationPipeline` | partner-gateway（上移） | P3 |
| 能力码权威定义 | partner-gateway 枚举(硬编码) + open-api-service 表 | **单一数据源：open-api-service 表 + partner-gateway 启动加载** | P2 |
| 能力码拦截规则 | partner-gateway 17 条 AntPathMatcher(硬编码) | 注册表/配置驱动 | P2 |
| JWT 密钥 | partner-gateway 硬编码 | Nacos 配置共享 | P1 |
| 限流 | partner-gateway(默认关) | partner-gateway(按需开) | P3 |
| 漏洞业务表/编排 | open-api-service | vul-pass | P4 |
| Partner 契约实现 | open-api-service(mock 完整 / vul-pass 待接) | open-api-service 适配层 → vul-pass | P4 |

---

## 4. 分期实施（服从"先 mock 完整，再 vul-pass 对接"）

### Phase 1 —— mock 端到端可用（最高优先级，1 周）

**目标**：让 mock 模式从 partner-gateway 入口到 open-api-service 全链路跑通，作为联调与前端测试的稳定基线。

| 任务 | 文件/位置 | 说明 |
|---|---|---|
| 1.1 默认 mode 切回 mock | `open-api-service/src/main/resources/application.yml` | `open-api.engine.adapter-mode: mock`（当前是 task-center）；或测试环境用 `application-mock.yml` profile |
| 1.2 partner-gateway 增加 mock 旁路 | `partner-gateway` 新增 `partner.gateway.mock.enabled` 配置 + `PartnerAuthFilter` 分支 | `mock.enabled=true` 时：Token 校验降级（放行或固定 context）、能力码拦截放行、仍注入 `X-Partner-Id`（从 query/header 兜底）。**仅测试环境启用**，生产强制关 |
| 1.3 JWT 密钥配置化 | `PartnerJwtSupport.SECURITY_KEY` → Nacos `partner.gateway.jwt.secret` | 与 open-api-service 签发密钥共享同一配置项，消除硬编码 |
| 1.4 mock fixture 扩充 | `open-api-service/src/main/resources/mock/engine/bundles/` | 当前仅 6 个 NSFocus 模板，补齐 verify/remediate/verify-fix 各状态机分支的 fixture |
| 1.5 前端默认联调 mock | `asset-manage-master/public/conf/index.js` + `.env.development.local` | Admin Key 保持 `dev-internal-admin-key-change-in-prod`；确认前端双通道代理指向 35770/7000 |
| 1.6 验收 | MockE2eConsole + MockManualIngest + VerifyFixWorkspace | 跑通 `runBootstrapE2e` + `runFullManualE2e` + 实例 FSM 全链路 |

**验收标准**：
- `adapter-mode=mock` + `gateway.mock.enabled=true` 下，前端 MockE2eConsole 一键全流程通过（Partner 注册→Token→建任务→导入→实例 verify/remediate/verify-fix→webhook→export）；
- partner-gateway 在 mock 旁路下不依赖 vul-pass/vuln-task-center 任何真实服务；
- mock 不暴露 `scan_phase`/`verify_merge_strategy` 等内部字段（契约形状 only）。

**回滚**：`adapter-mode` 改回 task-center，`gateway.mock.enabled=false`。

---

### Phase 2 —— 能力码单一数据源 + 注册表雏形（2 周）

**目标**：解决能力码三处手工同步问题，并为注册表机制打底。

| 任务 | 说明 |
|---|---|
| 2.1 能力码权威归一 | open-api-service `partner_capability` 表为单一数据源；partner-gateway 启动时通过 Feign/接口拉取能力码清单与拦截规则，替换 `PartnerCapability` 枚举与 17 条硬编码 AntPathMatcher |
| 2.2 能力码查询接口 | open-api-service 新增 `GET /internal/registry/capabilities`（内网鉴权），返回 `{code, path, method}[]`；partner-gateway 启动加载 + 定时刷新 |
| 2.3 前端能力码注册表下发 | 新增 `GET /internal/admin/registry/capabilities`（Admin 通道）；前端 `enums.js` 的 `CAPABILITIES` 改为启动时拉取填充 `REGISTRY`，本地保留兜底枚举 |
| 2.4 前端 E2E_CAPABILITIES 去硬编码 | `openPartnerApi.js` 的 `E2E_CAPABILITIES` 改从注册表读取 |
| 2.5 scannerTypeLabel 去硬编码 | `verifyFix.js` 的 `scannerTypeLabel`(1=绿盟/7=Nessus) 改注册表或配置 |

**验收标准**：
- open-api-service 表新增一个能力码，partner-gateway 无需改代码即可拦截；
- 前端新建 Partner 时能力码选项从后端下发，与网关拦截规则一致。

**回滚**：partner-gateway 回退硬编码枚举；前端回退本地枚举。

---

### Phase 3 —— 网关职责归位（2-3 周，可与 P2 并行）

**目标**：把错位在 open-api-service 的网关职责上移，open-api-service 开始瘦身。

| 任务 | 说明 |
|---|---|
| 3.1 调用记录上移 | `api_invocation` 写入逻辑从 open-api-service `InvocationPipeline` 上移到 partner-gateway（WebFlux filter 侧记录）；open-api-service 保留查询读。需注意 reactive 环境下异步写 DB/异步发 Kafka |
| 3.2 Token 校验收敛 redis 模式 | partner-gateway `introspect-mode` 固定 redis，移除 feign 降级依赖（消除网关→业务反向依赖）；open-api-service `/internal/token/introspect` 降级为内部诊断用 |
| 3.3 Token 签发评估 | `/oauth/token` 是否上移认证服务，视公司认证服务现状定；暂留 open-api-service 但隔离为独立模块，便于后续迁移 |
| 3.4 限流启用评估 | partner-gateway `rate-limit.enabled` 按 Partner 维度开启，配额数据从 open-api-service `partner_quota` 表加载 |
| 3.5 CORS 单点化 | 确认 CORS 仅在 partner-gateway 一处配置，open-api-service 移除重复 CORS |

**验收标准**：
- partner-gateway 独立承担鉴权 + 调用记录 + 限流，open-api-service 故障时网关仍能记录调用并拒绝未授权请求；
- 网关→open-api-service 无鉴权反向依赖（redis 模式）。

**回滚**：调用记录回 open-api-service；introspect 回 feign 模式。

---

### Phase 4 —— vul-pass 真实对接（3-4 周，依赖 vul-pass 就绪）

**目标**：在 mock 稳定基础上，切到 vul-pass 真实链路，逐步替换 mock 分支。

| 任务 | 说明 |
|---|---|
| 4.1 vul-pass 契约对齐 | 确认 vul-pass `/vul-scan-task/dispatch`、`/vul-scan-task/page2`、`/vul-scan-task-sub-system/page`、`PUT /vul-scan-task-sub-system` 与 `IVulPassScanTaskFeign`/`IVulPassInstanceFeign` 方法签名一致；对齐实例域两硬约束（vulInfoID≠id、写前先查 page 换 id） |
| 4.2 SvmpEngineAdapterImpl 补全 | vul-pass 模式下 `SvmpEngineAdapterImpl` 的实例方法（searchInstances/getInstanceDetail/disposeInstance/verifyInstance）从 UnsupportedOperationException 补全，走 `IVulPassInstanceFeign` |
| 4.3 灰度切流 | `adapter-mode` 从 mock 灰度切到 vul-pass；同一输入 mock vs vul-pass 输出对比回归 |
| 4.4 mock 保留为联调桩 | mock 分支不删除，作为 Partner 联调/E2E 测试的常驻桩（`adapter-mode=mock` 仍可切回） |
| 4.5 前端无感切换 | 前端不动，后端切 mode |

**验收标准**：
- `adapter-mode=vul-pass` 下，前端 MockE2eConsole 全流程通过（真实 vul-pass 链路）；
- mock 与 vul-pass 同输入输出一致（契约形状）；
- mock 桩仍可随时切回用于联调。

**回滚**：`adapter-mode` 切回 mock。

---

### Phase 5 —— 业务下沉 vul-pass（远期，vul-pass 稳定后）

**目标**：漏洞业务表/编排/案件彻底下沉 vul-pass，open-api-service 回到"网关后端的通用业务服务"定位。

| 任务 | 说明 |
|---|---|
| 5.1 业务表迁移 | `open_task`/`open_task_sub`/`open_task_scan_result`/`open_vuln_instance`/`open_vuln_instance_log`/`open_verify_fix_job`/`open_verify_fix_job_item`/`open_operation_case*` 迁 vul-pass；open-api-service 留平台表（partner/api_invocation/api_operation/webhook_delivery_log/open_export*） |
| 5.2 业务 Admin 迁移 | `/internal/admin/open-tasks`、`/open-vuln-instances`、`/verify-fix`、`/operation-cases` 迁 vul-pass；open-api-service 留 `/internal/admin/partners`、`/invocations`、`/webhook-deliveries`、`/quotas` |
| 5.3 契约实现迁移 | `/api/open/v1/tasks/vul`、`/instances/*` 真实实现迁 vul-pass；open-api-service 只保留 mock 桩 + 路由 |
| 5.4 Webhook 事件/案件类型注册表 | 平台层不持业务枚举，vul-pass 启动向 partner-gateway/open-api-service 注册 `TASK_COMPLETED` 等事件类型 + `TASK_SCAN` 等案件类型 + 工作台 handler |
| 5.5 前端枚举全注册表化 | `WEBHOOK_EVENT_TYPES`/`OPERATION_CASE_TYPES`/`API_OPERATIONS` 全部改注册表下发；案件工作台多态面板按注册表 case_type 渲染 |
| 5.6 OpenSocOrchestration.vue 清理 | 删除遗留未挂路由组件 |

**验收标准**：
- open-api-service 代码库无 `scan_policy`/`auto_verify`/`vulInfoStat`/`scan_phase` 等漏洞字段，无 `open_task` 等业务表；
- 新增非漏洞业务，仅靠注册接口即可跑通拦截/投递/案件渲染/路由。

**回滚**：表迁移用双写过渡，对账通过后再切。

---

## 5. 前端改造（按阶段穿插）

| 阶段 | 前端任务 |
|---|---|
| P1 | 确认 `.env.development.local` 双通道代理指向正确；mock 联调验证 |
| P2 | `enums.js` CAPABILITIES 改注册表下发（保留兜底）；`E2E_CAPABILITIES`/`scannerTypeLabel` 去硬编码；新增 `openPlatformRuntime` 注册表拉取 + 缓存 |
| P3 | 无（后端职责归位对前端透明） |
| P4 | 无（mode 切换对前端透明） |
| P5 | `WEBHOOK_EVENT_TYPES`/`OPERATION_CASE_TYPES`/`API_OPERATIONS` 全注册表化；16 个直接 import 常量的视图/组件改异步/响应式获取；删除 `OpenSocOrchestration.vue` |

**前端编码护栏保留**：`verify-utf8.js` + 生成脚本链不动，修改生成产物类 Vue 文件仍走 `scripts/` 生成脚本。

---

## 6. 风险与回滚

| 风险 | 缓解 | 回滚 |
|---|---|---|
| P1 partner-gateway mock 旁路被误开到生产 | 配置项 `partner.gateway.mock.enabled` 默认 false，生产 Nacos 强制不配；启动日志告警 | 改回 false |
| P1 切 mock 影响当前 task-center 测试 | mock 与 task-center profile 隔离，独立环境验证 | 切回 task-center profile |
| P2 能力码注册表加载失败致网关启动阻塞 | 本地兜底缓存 + 加载失败用上次缓存 + 告警不阻塞 | 回退硬编码枚举 |
| P3 调用记录上移网关后 reactive 写 DB 性能 | 异步队列写 + Kafka 削峰；监控落库延迟 | 回 open-api-service 同步写 |
| P4 vul-pass 契约不一致 | P4.1 先对齐契约再切；灰度比对 | 切回 mock |
| P5 表迁移数据不一致 | 双写过渡 + 对账 | 回退双写 |

---

## 7. 验收总标准

1. **P1 mock 端到端**：mock 模式 + gateway mock 旁路下，前端 E2E 全流程通过，不依赖任何真实引擎服务。
2. **P2 单一数据源**：能力码新增/修改只改一处（open-api-service 表），网关拦截与前端展示自动一致。
3. **P3 职责归位**：partner-gateway 独立承担鉴权 + 调用记录 + 限流，无网关→业务鉴权反向依赖。
4. **P4 vul-pass 对接**：vul-pass 模式下 E2E 全流程通过，mock 桩仍可切回联调。
5. **P5 业务下沉**：open-api-service 无漏洞业务表/字段；新增非漏洞业务零代码改动平台层即可接入。

---

## 8. 与 v1 的差异说明

| 维度 | v1（2026-06-19） | v2（本版） |
|---|---|---|
| 网关形态 | 物理合并为单一 `open-gateway` | **不合并**，partner-gateway 保持独立，职责归位 |
| 依据 | 假设两者栈相近、可合 | 摸底发现 WebFlux 2.6.3 vs MVC 2.2.10 栈冲突 |
| mock 起点 | 假设需从零补 mock | open-api-service mock **已完整**，只缺网关层 mock + 默认 mode |
| 优先级 | 解耦优先 | **mock 优先**（P1），解耦分阶段推后 |
| 能力码 | 注册表（全新建） | 单一数据源归一（先解决三处同步，再演进注册表） |
| 业务下沉 | Phase 3 | Phase 5（远期，vul-pass 稳定后） |

---

## 9. 关联文档

- `SOC对接全链路-PRD.md`、`开放平台Partner鉴权与隔离-落地方案.md`、`开放平台对外REST执行面-分期落地方案.md`、`引擎对接与Mock模式方案.md`、`Open API与vul-pass内部接口映射表.md`
- 本方案不否定各 PRD 的流程/接口/数据模型细节，只做架构归位与分期重排
- 实例域两硬约束（vulInfoID≠id、写前先查 page 换 id）、双轨存储、双阶段扫描、修复核验状态机等业务设计不变
