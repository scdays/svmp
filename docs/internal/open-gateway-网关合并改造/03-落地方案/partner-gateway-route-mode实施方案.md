# partner-gateway route-mode 实施方案（Phase 1）

> 版本：v1.0  日期：2026-06-23
> 关联：`01-架构与总览/open-gateway合并与平台业务解耦改造方案.md`（v3）Phase 1
> 前置：`06-Mock与联调/开放平台mock链路验收清单.md`（Phase 0）已通过
> 目的：让 partner-gateway 成为 mock / vul-pass 的路由决策点，所有 Partner API 经 partner-gateway 入口，按 route-mode 转发。

---

## 0. 目标

1. partner-gateway 新增 `route-mode=mock|vul-pass` 配置；
2. `/api/open/v1/**` 按 route-mode 转发到 open-api-service（mock）或 vul-pass（real）；
3. `/oauth/token` 短期仍走 open-api-service，partner-admin 建成后切 partner-admin；
4. JWT 密钥配置化，消除硬编码；
5. 调用记录采集事件模型设计（可先不落库）；
6. 保持真实 Token 链路优先，仅在本地开发支持 auth-bypass。

**Phase 1 只做路由决策点改造，不拆 partner-admin，不接 vul-pass 真实业务。**

---

## 1. route-mode 配置设计

### 1.1 配置项

`project_backend/svmp/partner-gateway/src/main/resources/application.yml`：

```yaml
partner:
  gateway:
    route-mode: mock                 # mock | vul-pass
    route-targets:
      mock: lb://open-api-service
      vul-pass: lb://vul-pass
    jwt:
      secret: ${PARTNER_GATEWAY_JWT_SECRET:fd2wfd!g021nk90fd1h3kfd902*)Y!*&c3-(dmg)1==}  # 与 open-api-service 签发一致
    mock:
      auth-bypass-enabled: false     # 仅本地调试，生产禁止开启
```

### 1.2 语义

| route-mode | `/api/open/v1/**` 目标 | 用途 |
|---|---|---|
| `mock` | `lb://open-api-service` | 当前联调/E2E/回归基线（mock 由 task-center 引擎实现，`adapter-mode=task-center`） |
| `vul-pass` | `lb://vul-pass` | 后续真实漏洞业务（Phase 4 启用） |

> 说明：早期 fixture-based mock（`adapter-mode: mock` + `classpath:mock/engine/bundles/`）已弃用。当下 open-api-service 的 mock 能力由 **task-center 引擎实现**承载，即测试环境 `adapter-mode=task-center` 即为 mock 验收环境。本方案中"mock"均指该实现，不再依赖早期 fixture bundle。

### 1.3 配置绑定

`PartnerGatewayProperties` 增加：

```java
private RouteMode routeMode = RouteMode.MOCK;
private RouteTargets routeTargets;
private Jwt jwt;
private Mock mock;

public enum RouteMode { MOCK, VUL_PASS }
```

---

## 2. 路由规则

### 2.1 当前（Phase 1）

```text
/oauth/token              → open-api-service
/api/open/v1/oauth/token  → open-api-service
/api/open/v1/**           → 按 route-mode:
                              mock     → open-api-service
                              vul-pass → vul-pass
/internal/**              → 拒绝（40101，外网不可达）
```

### 2.2 partner-admin 建成后（Phase 2+）

```text
/oauth/token              → partner-admin
/api/open/v1/**           → 按 route-mode 转发
/internal/admin/**        → 走管理面网关/直连 partner-admin，不经 partner-gateway 外网入口
```

> 注：`/internal/admin/**` 是管理面，本就不应经 partner-gateway 公网入口。Phase 1 暂不动 admin 路由。

---

## 3. 代码改造点

### 3.1 路由配置动态化

当前 4 条路由硬编码 `lb://open-api-service`。改造为根据 `route-mode` 选择 target。

方案 A（推荐）：用 Spring Cloud Gateway `RouteLocator` 编程式构造，读 `route-mode` 决定 `/api/open/v1/**` 的 uri。

方案 B：保留 YAML 路由，增加一个 `RouteModeUriResolver`，在 filter 里改写 `exchange` 的目标 uri。

**建议**：Phase 1 用方案 A，路由清晰可控。

### 3.2 PartnerGatewayProperties

新增字段：

- `routeMode`
- `routeTargets`（mock / vul-pass 两个 lb uri）
- `jwt.secret`
- `mock.authBypassEnabled`

### 3.3 PartnerJwtSupport

- `SECURITY_KEY` 改为从 `PartnerGatewayProperties.jwt.secret` 注入；
- 与 open-api-service 签发密钥共享同一 Nacos 配置项。

### 3.4 PartnerAuthFilter

- 鉴权、能力码、限流逻辑保持不变；
- 新增 `mock.authBypassEnabled` 分支：仅当 `route-mode=mock` 且 `authBypassEnabled=true` 时放行（本地调试）；
- 生产环境配置校验：`route-mode=vul-pass` 时强制 `authBypassEnabled=false`。

### 3.5 调用记录采集（设计，可先不落库）

新增 `InvocationRecordFilter`（或合并进 PartnerAuthFilter）：

- 请求进入：生成 `invocationId` / 复用 `X-Request-Id`，记录 partnerId、operationId、method、path、startTime；
- 请求结束：记录 responseCode、httpStatus、duration、endTime；
- 发布 `InvocationRecordedEvent`（内存事件 / Kafka / Redis Stream）；
- Phase 1 先发内存事件 + 日志，不落库；Phase 3 由 partner-admin 消费落库。

### 3.6 不改动的部分

- `PartnerCapability` 枚举与 17 条硬编码规则：Phase 2 注册表化；
- `PartnerTokenResolver`：redis 模式保持；
- `/internal/token/introspect`：暂保留，redis 模式不依赖。

---

## 4. /oauth/token 过渡策略

| 阶段 | `/oauth/token` 目标 |
|---|---|
| Phase 1 | open-api-service（现状不变） |
| Phase 2 | partner-admin（partner-admin 建成后切） |
| 远期 | 认证服务 |

Phase 1 不动 `/oauth/token` 路由，避免影响 mock 联调。

---

## 5. mock auth-bypass 策略

仅本地调试用，不作为正式联调方式。

```yaml
partner:
  gateway:
    route-mode: mock
    mock:
      auth-bypass-enabled: true   # 仅本地
```

行为：

- 跳过 Token 校验；
- 跳过能力码拦截；
- 仍注入 `X-Partner-Id`（从 query / header 兜底，默认 `mock-partner`）；
- 仍记录调用。

**约束**：

- 生产环境 Nacos 不配置此项，或强制 false；
- 启动时若 `authBypassEnabled=true` 打印醒目告警日志；
- `route-mode=vul-pass` 时禁止开启。

正式联调仍走真实 Token：`/oauth/token` 换 token → `Bearer` 调用。

---

## 6. 前端 / 代理配置

Phase 1 前端无需改动，代理目标不变：

| 通道 | 代理目标 |
|---|---|
| Partner `/api/open/v1`、`/oauth/token` | partner-gateway:35770 |
| Admin `/open-api-service` | 平台网关:7000 → open-api-service |

验收时确认：Partner 请求确实经 partner-gateway 进入，而非绕过直连 open-api-service:35780。

> 主应用 `config/openApiDevProxy.js` 的 `/open-api` → 35780 直连 open-api-service 仅本地调试用，正式联调不用。

---

## 7. 验收

### 7.1 配置验收

- [ ] `route-mode=mock` 配置生效
- [ ] `route-targets.mock=lb://open-api-service`
- [ ] `jwt.secret` 配置化，与 open-api-service 一致
- [ ] `auth-bypass-enabled` 生产为 false

### 7.2 路由验收

- [ ] `route-mode=mock` 时 `/api/open/v1/**` 转发到 open-api-service
- [ ] `route-mode=vul-pass` 配置存在（vul-pass 未就绪时返回 503/降级，可接受）
- [ ] `/oauth/token` 仍走 open-api-service
- [ ] `/internal/**` 外网不可达

### 7.3 鉴权验收

- [ ] 真实 Token 链路：`/oauth/token` 换 token → 调 `/api/open/v1/**` 成功
- [ ] 无 Token 调用被 40101 拒绝
- [ ] 能力码未授权被 40301 拒绝
- [ ] `auth-bypass-enabled=true`（仅本地）时放行

### 7.4 调用记录验收

- [ ] `InvocationRecordedEvent` 发布
- [ ] 日志可见 partnerId / operationId / duration / responseCode

### 7.5 mock 回归

- [ ] Phase 0 验收清单全部仍通过
- [ ] route-mode=mock 下 E2E 全流程不退化

---

## 8. 回滚

| 场景 | 回滚 |
|---|---|
| route-mode 改造导致 mock 链路异常 | `route-mode=mock`，路由回固定 `lb://open-api-service`（YAML 原配置） |
| JWT 密钥配置化导致 Token 校验失败 | 回退硬编码 SECURITY_KEY |
| 调用记录采集影响性能 | 关闭 `InvocationRecordedEvent` 发布 |

---

## 9. 不在 Phase 1 范围

- partner-admin 建项（Phase 2）；
- 能力码注册表化（Phase 2）；
- 调用记录落库与查询迁移（Phase 2/3）；
- Webhook dispatcher 迁移（Phase 3）；
- vul-pass 真实对接（Phase 4）。

Phase 1 完成后，partner-gateway 具备路由决策能力，但 mock 链路行为与 Phase 0 一致，保证可回滚。

---

## 10. 下一步

Phase 1 验收通过后，进入 Phase 2：

1. 创建 partner-admin 建项方案；
2. 首批迁移：Partner 管理、凭证管理、接口目录、开发指南、流控配置、调用记录查询、Token 签发；
3. 能力码注册表化；
4. 前端路径兼容（旧路径代理到 partner-admin）。
