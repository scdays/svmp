# partner-admin 建项与首批迁移方案（Phase 2）

> 版本：v1.0  日期：2026-06-24
> 关联：`01-架构与总览/open-gateway合并与平台业务解耦改造方案.md`（v3）Phase 2
> 前置：`06-Mock与联调/开放平台mock链路验收清单.md`（Phase 0）通过；`03-落地方案/partner-gateway-route-mode实施方案.md`（Phase 1）完成
> 目的：新建 `partner-admin` 微服务，承接 open-api-service 的平台治理管理面，open-api-service 保留 mock 业务能力不变。

---

## 0. 目标与范围

### 0.1 目标

1. 新建 `partner-admin` 微服务，对齐 esmp-support 脚手架与 DDD 四层结构；
2. 首批迁移平台管理面能力（Partner 管理、凭证、接口目录、流控配置、调用记录查询、Webhook 投递记录查询、运营案件壳、Token 签发）；
3. open-api-service 保留 mock 业务能力不变（风险排查、修复核验、接入测试、处置测试）；
4. 前端通过路径兼容过渡，不一次性大改。

### 0.2 Phase 2 范围

**迁入 partner-admin：**

- Partner 管理（CRUD）
- 凭证管理（clientId/clientSecret 生成、查询）
- Webhook Secret 轮换
- 接口目录查询（`api_operation`）
- 调用记录查询（`api_invocation`）
- Webhook 投递记录查询（`webhook_delivery_log`）
- 流控策略/统计（quota/stats）
- 运营案件壳（`open_operation_case` 系列）
- Token 签发（`/oauth/token`，短期）

**保留 open-api-service（不动）：**

- mock 风险排查、mock 修复核验、mock 接入测试、mock 处置测试
- mock 报告导入、mock verify-fix job
- mock 业务事件产生、mock 业务案件 payload
- Partner 契约 `/api/open/v1/**` mock 实现

**不在 Phase 2 范围：**

- Webhook 投递执行（dispatcher）迁 partner-admin → Phase 3
- 能力码注册表化（partner-gateway 加载） → Phase 2 末尾或 Phase 3
- vul-pass 真实对接 → Phase 4
- open-api-service 纯 mock 化收口 → Phase 5

---

## 1. partner-admin 建项规格

### 1.1 工程坐标

| 项 | 值 |
|---|---|
| 目录 | `project_backend/svmp/partner-admin` |
| groupId | `com.mvtech`（继承父工程） |
| artifactId | `partner-admin` |
| version | `1.0.0` |
| 父工程 | `com.mvtech:esmp-support:3.0.2-SNAPSHOT`（与 open-api-service / vul-pass 一致） |
| Java | 1.8 |
| 根包 | `com.vtc.partneradmin` |
| 启动类 | `com.vtc.partneradmin.ApplicationStart` |

### 1.2 端口与服务名

已占用端口：{8086, 18087, 21127, 23000, 35678, 35770, 35780}。

| 项 | 值 | 说明 |
|---|---|---|
| `spring.application.name` | `partner-admin` | svmp 目录无同名服务，无冲突 |
| `server.port` | **35781** | 紧邻 open-api-service(35780)，端口段连续 |

### 1.3 Nacos / Redis / MySQL

对齐 open-api-service：

| 项 | 值 |
|---|---|
| Nacos server-addr | `172.16.3.33:8848`（与 open-api-service 一致） |
| namespace | `ESMP` |
| group | `DEV` |
| config file-extension | `yaml` |
| Redis host/port/database | `172.16.3.32` / `6379` / `2`（与 open-api-service 同库，共享 token context） |
| MySQL | **共享 `open_api` 库**（过渡期，表不迁移只共享读写） |

> 关键决策：Phase 2 **不迁库**。partner-admin 与 open-api-service 共享 `open_api` 库，平台表（partner/api_invocation 等）两边都能读写。物理迁库推迟到 Phase 5 收口，避免 Phase 2 同时改代码又迁数据的高风险。

### 1.4 启动类注解

对齐 open-api-service：

```java
@EnableAsync
@EnableScheduling
@EnableLiquibase
@EnableFeignClients({"com.vtc.partneradmin"})
@SpringCloudApplication
@MapperScan("com.vtc.partneradmin.infra.dao")
@EnableConfigurationProperties(PartnerAdminProperties.class)
```

### 1.5 DDD 四层包结构

```
com.vtc.partneradmin
├── ui                      // Controller + DTO + params
│   ├── admin               // 管理面 Controller
│   ├── auth                // Token 签发 Controller
│   ├── dto
│   └── params
├── app                     // 应用服务
│   ├── convert
│   └── service (impl)
├── domain                  // 领域层
│   ├── partner             // Partner / 凭证 / 能力 / webhook config
│   ├── open                // api_operation / api_invocation / webhook_delivery_log
│   ├── operationcase       // 运营案件壳
│   └── auth                // Token 签发领域
└── infra                   // 基础设施
    ├── config
    ├── dao (po)
    ├── feign
    ├── filter              // InternalAdminAuthFilter
    ├── redis               // PartnerTokenRedisStore（共享）
    └── repository
```

调用链：`*Ui → *AppServiceImpl → *DomainServiceImpl → *RepositoryImpl → Mapper/PO → DB`（与 open-api-service 一致）。

### 1.6 pom 依赖

对齐 open-api-service，去掉 mock/task-center/vul-pass 引擎相关依赖：

- `esmp-starter-core`（排除 hibernate-validator）
- `esmp-starter-redis`
- `spring-cloud-starter-openfeign` + `feign-okhttp`
- `spring-boot-starter-validation`
- `spring-security-crypto`（BCrypt 校验凭证）
- `spring-kafka`（Phase 3 webhook dispatcher 用，先引入）
- `fastjson:1.2.83`
- `lombok:1.18.30`
- 父工程继承：`spore-base-ddd`、`spore-starter-liquibase`、nacos、spring-boot-starter-web、actuator 等

**不需要**：`jsch`（SFTP，open-api-service 用于报告上传，partner-admin 不涉及）、扫描引擎适配器。

---

## 2. 首批迁移清单（按能力）

> 迁移方式：**代码搬迁 + 路径保持**。Controller 路径、接口方法签名、DTO 字段全部保持不变，前端无感。迁移后 open-api-service 对应接口可保留为转发壳或直接下线（Phase 5）。

### 2.1 Partner 管理

| 项 | 来源（open-api-service） | 目标（partner-admin） |
|---|---|---|
| Controller | `ui/admin/PartnerAdminUI.java` `/internal/admin/partners` | `ui/admin/PartnerAdminUI.java` 同路径 |
| 接口 | createPartner / listPartners / getPartner / updatePartner | 同 |
| AppService | `IPartnerAdminAppService` + impl | 同 |
| DomainService | `IPartnerDomainService` + impl | 同 |
| Repository | `PartnerRepositoryImpl`（管 4 表） | 同 |
| Mapper | PartnerMapper / PartnerCredentialMapper / PartnerCapabilityMapper / PartnerWebhookConfigMapper | 同 |
| 表 | partner / partner_credential / partner_capability / partner_webhook_config | 共享 open_api 库 |

### 2.2 凭证管理

随 2.1 Partner 管理一起迁（同 Controller、同 Repository）。`createCredential` 用 `BCryptPasswordEncoder` 编码 secret，逻辑不变。

### 2.3 Webhook Secret 轮换

随 2.1 一起迁。`rotateWebhookSecret` → `WebhookSecretGenerator.generate()` → 写 `partner_webhook_config`。

> 遗留问题（open-api-service 现状）：`saveWebhookSecret` 写明文 `webhookSecret` 列，不填 `webhookSecretHash`。迁移时保留现状，不在此处改（避免行为变更），记为 TODO 待 Phase 3 webhook dispatcher 时统一处理。

### 2.4 接口目录

| 项 | 来源 | 目标 |
|---|---|---|
| Controller | `ui/admin/ApiCatalogAdminUI.java` `/internal/admin/api-operations` | 同路径 |
| 接口 | listApiOperations | 同 |
| 表 | api_operation | 共享 |

### 2.5 调用记录查询

| 项 | 来源 | 目标 |
|---|---|---|
| Controller | `ui/admin/InvocationAdminUI.java` `/internal/admin/invocations` | 同路径 |
| 接口 | listInvocations / getInvocationDetail / getInvocationResponseBody / getInvocationRequestBody | 同 |
| 表 | api_invocation | 共享 |
| 说明 | Phase 1 起 invocation 采集由 partner-gateway 负责；partner-admin 只查询。过渡期 open-api-service 仍在写，两边都能读 |

### 2.6 Webhook 投递记录查询

| 项 | 来源 | 目标 |
|---|---|---|
| Controller | `InvocationAdminUI` `/internal/admin/webhook-deliveries` | 同路径 |
| 接口 | listWebhookDeliveries / getWebhookDeliveryDetail / retryWebhookDelivery | 同 |
| 表 | webhook_delivery_log | 共享 |
| 说明 | Phase 2 只迁查询；投递执行仍在 open-api-service。Phase 3 迁 dispatcher |

### 2.7 流控策略/统计

| 项 | 来源 | 目标 |
|---|---|---|
| Controller | `InvocationAdminUI` `/internal/admin/quotas`、`PartnerAdminUI` `/{partnerId}/stats` | 同路径 |
| 接口 | listPartnerQuotas / getPartnerStats | 同 |
| 表 | api_invocation（统计）、partner | 共享 |
| 说明 | 配置/查询在 partner-admin；执行在 partner-gateway（Phase 1 已设计） |

### 2.8 运营案件壳

| 项 | 来源 | 目标 |
|---|---|---|
| Controller | `ui/admin/OperationCaseAdminUI.java` `/internal/admin/operation-cases` | 同路径 |
| 接口 | listCases / getWorkspace / backfill / retryDispatch | 同 |
| 表 | open_operation_case / _event / _target | 共享 |
| 说明 | **工作台 payload 聚合**：partner-admin 读取案件壳 + timeline + invocation + webhook，按 case_type 调 open-api-service mock 获取业务 payload。Phase 2 先保持现有聚合逻辑（仍调 open-api-service），Phase 4 起 case_type 按 route-mode 调 mock/vul-pass |

### 2.9 Token 签发

| 项 | 来源 | 目标 |
|---|---|---|
| Controller | `ui/auth/PartnerTokenUI.java` `/oauth/token`、`/api/open/v1/oauth/token` | 同路径 |
| 接口 | issueToken / introspect | 同 |
| Redis | `PartnerTokenRedisStore`（`partner:token:{sha256}`） | 共享 Redis db=2 |
| 说明 | Phase 2 partner-gateway 的 `/oauth/token` 路由切到 partner-admin；Token 校验仍走 partner-gateway redis 模式，无感 |

### 2.10 开发指南（特殊处理）

**事实：open-api-service 后端不存在 `/internal/admin/developer-docs` 代码实现**（前端 `catalog.js` 有 `listDeveloperDocs` 调用，后端无 Controller）。

处理：

- Phase 2 在 partner-admin 新建 `DeveloperDocAdminUI`，`GET /internal/admin/developer-docs` 返回静态文档配置（先返回空列表或占位）；
- 或确认前端该接口是否实际被页面调用，若未调用则 partner-admin 也不实现，前端移除调用；
- **不阻塞 Phase 2 主流程**，作为附带项处理。

---

## 3. 数据库与 Liquibase

### 3.1 Phase 2 不迁库

partner-admin 与 open-api-service 共享 `open_api` 库。平台表两边读写，无需数据迁移。

### 3.2 Liquibase 脚本

partner-admin 的 `src/main/resources/db/mysql/` **不重复建表脚本**（表已存在于 open_api 库）。

处理方式二选一：

- **方案 A（推荐）**：partner-admin `common.data.enable: false`，关闭 Liquibase 自动建表，PO 类直接映射已有表；
- 方案 B：partner-admin Liquibase 脚本只放空 changelog 或前置检查，不 create table。

> 避免两个服务都对同一张表跑 create table 导致 Liquibase 冲突。Phase 5 物理迁库时再由 partner-admin 接管建表脚本。

### 3.3 PO 类

从 open-api-service 搬迁对应 PO（`@TableName` 不变）：

- `PartnerPO`、`PartnerCredentialPO`、`PartnerCapabilityPO`、`PartnerWebhookConfigPO`
- `ApiOperationPO`
- `ApiInvocationPO`、`WebhookDeliveryLogPO`
- `OpenOperationCasePO`、`OpenOperationCaseEventPO`、`OpenOperationCaseTargetPO`

---

## 4. 路由与前端兼容

### 4.1 partner-gateway 路由调整（Phase 2）

Phase 1 已实现 `route-mode`。Phase 2 新增 `/oauth/token` 与管理面路由：

```yaml
partner:
  gateway:
    route-mode: mock
    routes:
      oauth-token-target: lb://partner-admin      # Phase 2 切
      mock-target: lb://open-api-service
      vul-pass-target: lb://vul-pass
      admin-target: lb://partner-admin            # /internal/admin/** 走管理面网关
```

> 注：`/internal/admin/**` 本不经 partner-gateway 公网入口（管理面内网直达）。Phase 2 前端通过主应用/nginx 代理把 `/open-api-service/internal/admin/**` 按路径分流到 partner-admin 或 open-api-service。

### 4.2 前端路径兼容（核心策略）

**前端短期不改 API 文件**，通过代理层分流。在 `asset-manage-master/vue.config.js` 与 nginx 配置中：

```text
/open-api-service/internal/admin/partners            → partner-admin:35781
/open-api-service/internal/admin/api-operations      → partner-admin:35781
/open-api-service/internal/admin/invocations         → partner-admin:35781
/open-api-service/internal/admin/webhook-deliveries  → partner-admin:35781
/open-api-service/internal/admin/quotas              → partner-admin:35781
/open-api-service/internal/admin/operation-cases     → partner-admin:35781
/oauth/token                                         → partner-admin:35781
/open-api-service/internal/admin/mock-tasks          → open-api-service:35780
/open-api-service/internal/admin/mock-verify-fix     → open-api-service:35780
/open-api-service/internal/admin/open-tasks          → open-api-service:35780  (mock payload)
/open-api-service/internal/admin/verify-fix          → open-api-service:35780  (mock payload)
/api/open/v1/**                                      → partner-gateway:35770 → open-api-service(mock)
```

这样前端 `partner.js`、`invocation.js`、`operationCase.js`、`catalog.js`、`quota.js` 无需改 baseURL，仍走 `/open-api-service`，代理层按子路径分流。

### 4.3 前端中期改造（Phase 2 末尾或 Phase 3）

新增运行时配置：

```js
VUE_APP_PARTNER_ADMIN_BASE_URL=/partner-admin
VUE_APP_OPEN_MOCK_BASE_URL=/open-api-service
```

API 文件分组改 baseURL：

| API 文件 | 目标 |
|---|---|
| `partner.js` | partner-admin |
| `catalog.js` | partner-admin |
| `invocation.js` | partner-admin |
| `quota.js` | partner-admin |
| `operationCase.js` | partner-admin |
| `mockTask.js` | open-api-service |
| `mockVerifyFix.js` | open-api-service |
| `openTask.js` | open-api-service（mock payload） |
| `verifyFix.js` | open-api-service（mock payload） |
| `openPartnerApi.js` | partner-gateway |

可分批改，每改一组验证一组。

---

## 5. Token 签发迁移专项

### 5.1 风险

`/oauth/token` 是 Partner 入口关键路径，迁移不当会导致所有 Partner 调用失败。

### 5.2 迁移步骤

1. partner-admin 实现 `PartnerTokenUI.issueToken`，逻辑与 open-api-service 完全一致（BCrypt 校验 → JWT 签发 → Redis 存 token context）；
2. JWT 密钥：partner-admin 与 open-api-service、partner-gateway 共享同一 Nacos 配置项（Phase 1 已配置化）；
3. Redis：共享 db=2，`partner:token:{sha256}` key 格式不变，`PartnerTokenContext` 序列化不变；
4. partner-gateway `/oauth/token` 路由灰度切到 partner-admin；
5. 验证：partner-gateway redis 模式校验 partner-admin 签发的 token 通过；
6. open-api-service `/oauth/token` 保留为兜底，确认稳定后下线（Phase 5）。

### 5.3 回滚

partner-gateway `/oauth/token` 路由切回 open-api-service。

---

## 6. 实施步骤

### Step 1：建项骨架

1. 创建 `project_backend/svmp/partner-admin` 工程；
2. pom.xml 对齐 open-api-service（去引擎依赖）；
3. bootstrap.yml / application.yml（端口 35781、共享 open_api 库、Redis db=2、Liquibase 关闭建表）；
4. 启动类 + 四层包结构；
5. Nacos 注册可见，启动正常。

### Step 2：搬迁 Partner 领域

1. 搬 Partner / 凭证 / 能力 / webhook config 的 PO、Mapper、Repository、DomainService、AppService、Controller；
2. 路径与签名不变；
3. InternalAdminAuthFilter 搬迁（`X-Internal-Admin-Key` 校验）；
4. 本地验证 `/internal/admin/partners` CRUD。

### Step 3：搬迁查询面

1. 接口目录、调用记录查询、Webhook 投递记录查询、流控统计；
2. 本地验证各查询接口。

### Step 4：搬迁运营案件壳

1. 运营案件 Controller / DomainService / Repository / Mapper / PO；
2. 工作台聚合逻辑保持调 open-api-service mock 获取 payload；
3. 本地验证案件列表与工作台。

### Step 5：搬迁 Token 签发

1. PartnerTokenUI + PartnerTokenRedisStore；
2. 灰度切 partner-gateway 路由；
3. 验证 Token 签发与校验闭环。

### Step 6：代理层分流与前端验证

1. 配置 nginx / vue.config.js 代理分流；
2. 前端全量验证：Partner 管理、流量治理、推送记录、运营案件、流控、接口目录、接入测试、风险排查、修复核验、处置测试；
3. 确认 mock 链路不退化（Phase 0 验收清单仍通过）。

### Step 7：open-api-service 接口保留为壳

1. 已迁接口在 open-api-service 保留转发壳或直接停用（视代理分流情况）；
2. 正式下线推迟到 Phase 5。

---

## 7. 验收标准

### 7.1 建项

- [ ] partner-admin 启动正常，Nacos 注册可见
- [ ] 端口 35781 无冲突
- [ ] 共享 open_api 库读写正常
- [ ] Redis db=2 token context 读写正常

### 7.2 能力迁移

- [ ] Partner 管理 CRUD 在 partner-admin 可用
- [ ] 凭证管理在 partner-admin 可用
- [ ] Webhook Secret 轮换在 partner-admin 可用
- [ ] 接口目录查询在 partner-admin 可用
- [ ] 调用记录查询在 partner-admin 可用
- [ ] Webhook 投递记录查询在 partner-admin 可用
- [ ] 流控策略/统计在 partner-admin 可用
- [ ] 运营案件列表/工作台在 partner-admin 可用
- [ ] `/oauth/token` 在 partner-admin 签发，partner-gateway 校验通过

### 7.3 前端无感

- [ ] 前端 API 文件未改（或仅代理层分流），全部页面可用
- [ ] Phase 0 mock 验收清单仍全部通过
- [ ] 接入测试 / 风险排查 / 修复核验 / 处置测试 不退化

### 7.4 边界

- [ ] open-api-service 仍保留 mock 业务能力
- [ ] partner-admin 不含 mock 业务、不含漏洞业务编排
- [ ] partner-admin 不含扫描引擎适配器

---

## 8. 风险与回滚

| 风险 | 缓解 | 回滚 |
|---|---|---|
| Token 签发迁移导致 Partner 登录失败 | 灰度切路由，JWT 密钥共享配置，Redis 共享 | partner-gateway `/oauth/token` 路由切回 open-api-service |
| 共享库并发写冲突 | Phase 2 不迁库只共享读，写仍以 open-api-service 为主，partner-admin 逐步接管写 | partner-admin 接口停用，回 open-api-service |
| 代理分流配置错误致前端 404 | 先本地代理验证，再上测试环境；按子路径逐条验证 | 代理回全量 open-api-service |
| 运营案件工作台聚合调 open-api-service 失败 | 保持现有聚合逻辑不变，仅迁壳 | 工作台回 open-api-service |
| Liquibase 双服务建表冲突 | partner-admin 关闭建表（`common.data.enable: false`） | — |

---

## 9. 不在 Phase 2 范围

- Webhook 投递执行 dispatcher 迁 partner-admin → Phase 3
- 能力码注册表化（partner-gateway 从 partner-admin 加载） → Phase 3
- 调用记录采集上移 partner-gateway 落库 → Phase 3
- vul-pass 真实对接 → Phase 4
- open-api-service 纯 mock 化收口、物理迁库 → Phase 5

---

## 10. 下一步

Phase 2 验收通过后，进入 Phase 3：

1. Webhook dispatcher 迁 partner-admin（消费业务事件 → 签名 → 投递 → 写 delivery_log）；
2. 能力码注册表化（partner-gateway 启动从 partner-admin 加载，替换硬编码 17 条规则）；
3. 调用记录采集落库（partner-gateway 发事件，partner-admin 消费写 api_invocation）；
4. 前端枚举注册表下发（capabilities / case types / webhook event types）。
