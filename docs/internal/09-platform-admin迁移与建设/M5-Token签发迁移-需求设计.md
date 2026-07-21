# M5 Token 签发迁移 · 需求设计文档

> **版本**：v1.0  
> **日期**：2026-06-25  
> **上游文档**：  
> - [开放平台Partner鉴权与隔离-落地方案.md](../03-落地方案/开放平台Partner鉴权与隔离-落地方案.md)  
> - [00-主计划.md](./00-主计划.md)  
> **里程碑归属**：M5 Token 签发迁移

---

## 1. 背景与目标

### 1.1 背景
当前 Partner Token 签发与校验能力（`/oauth/token`、`/internal/token/introspect`、Redis 缓存操作）均在 `open-api-service` 实现。随着 `platform-admin` 作为统一控制面的建设，需将该能力迁移至 `platform-admin`，实现以下目标：

1. **职责收敛**：Partner 身份管理、凭证管理、Token 签发统一在 `platform-admin` 实现，与 `open-api-service` 的业务执行职责分离
2. **共享资源复用**：Token 缓存（Redis DB=2）与 open-api-service 共享，保证 gateway 无感切换
3. **路径保持不变**：对外接口路径不变，前端与第三方无感知

### 1.2 目标
完成 Token 签发与校验能力从 `open-api-service` 到 `platform-admin` 的迁移，满足：
- platform-admin 可签发 Partner Token（client_credentials 模式）
- platform-admin 提供 introspect 接口供 gateway 降级使用
- Redis 缓存与 open-api-service 共享，gateway 可无缝切换路由
- 代码符合 DDD 四层架构规范

---

## 2. 需求清单

### 2.1 功能性需求（编号 FR-x）

| 编号 | 需求描述 | 优先级 |
|------|----------|--------|
| FR-1 | 提供 `POST /oauth/token` 接口，支持 client_credentials 模式签发 Token | P0 |
| FR-2 | 提供 `POST /api/open/v1/oauth/token` 接口（路径兼容） | P0 |
| FR-3 | 提供 `POST /internal/token/introspect` 接口，供 gateway 降级校验 Token | P0 |
| FR-4 | Token 存 Redis，键为 `partner:token:{sha256(token)}`，TTL 与 expires_in 一致 | P0 |
| FR-5 | 凭证校验使用 M1 迁入的 PartnerCredentialDO 的 clientSecretHash（BCrypt） | P0 |
| FR-6 | 迁移 PartnerContextFilter，设置 partnerId/requestId 到请求上下文 | P1 |

### 2.2 非功能性需求
- **性能**：Token 签发接口 P99 < 50ms
- **可用性**：与 open-api-service 共享 Redis，保证单点故障不影响 Token 校验
- **可测试性**：提供单元测试覆盖核心逻辑

---

## 3. 现状分析

### 3.1 open-api-service 现有实现
以下文件位于 `open-api-service/src/main/java/com/vtc/openapi/`（待实证扫描）：

| 文件路径 | 职责 |
|----------|------|
| `ui/auth/PartnerTokenUI.java` | 提供 `/oauth/token`、`/api/open/v1/oauth/token`、`/internal/token/introspect` 接口 |
| `ui/dto/auth/PartnerTokenIssueRequest.java` | Token 签发请求 DTO |
| `ui/dto/auth/PartnerTokenIssueResponse.java` | Token 签发响应 DTO |
| `ui/dto/auth/PartnerTokenIntrospectRequest.java` | Token 校验请求 DTO |
| `ui/dto/auth/PartnerTokenIntrospectResponse.java` | Token 校验响应 DTO |
| `app/service/IPartnerTokenAppService.java` | Token 应用服务接口 |
| `app/service/impl/PartnerTokenAppServiceImpl.java` | Token 应用服务实现 |
| `infra/redis/PartnerTokenRedisStore.java` | Token Redis 存储操作（saveToken/getByToken/saveCredentialMeta/sha256Hex） |
| `infra/filter/PartnerContextFilter.java` | 设置 partnerId/requestId 到请求上下文 |

### 3.2 platform-admin 当前缺口
- Token 签发相关文件完全缺失
- 无 Redis 相关操作类
- 无 PartnerContextFilter

---

## 4. 领域模型设计

### 4.1 核心数据结构
Token 域无需独立 DO，复用 M1 迁入的 PartnerCredentialDO。Redis 缓存结构如下：

```json
{
  "subjectType": "PARTNER",
  "partnerId": "partner-siem-01",
  "capabilities": ["TASK_WRITE", "TASK_READ"],
  "clientId": "cli_abc123",
  "issuedAt": 1747785600,
  "expiresAt": 1747872000
}
```

| 字段 | 说明 | 来源 |
|------|------|------|
| subjectType | 固定 "PARTNER" | 常量 |
| partnerId | Partner ID | PartnerCredentialDO.partnerId |
| capabilities | 开通能力列表 | PartnerCapabilityDO |
| clientId | 客户端 ID | PartnerCredentialDO.clientId |
| issuedAt | 签发时间戳（秒） | 当前时间 |
| expiresAt | 过期时间戳（秒） | 当前时间 + expires_in |

### 4.2 常量与枚举
- `TOKEN_CACHE_PREFIX = "partner:token:"`
- `DEFAULT_EXPIRES_IN = 86400`（24小时）
- `SHA256_HEX` 工具方法

---

## 5. 四层结构设计

### 5.1 分层职责
| 层级 | 职责 |
|------|------|
| **UI 层** | PartnerTokenUI 提供对外接口，注入 AppService，返回 DTO |
| **App 层** | PartnerTokenAppService 编排凭证校验、Token 生成、缓存存储 |
| **Domain 层** | 本域无独立 DomainService，复用 Partner 域能力 |
| **Infra 层** | PartnerTokenRedisStore 实现 Redis 操作；PartnerContextFilter 实现上下文设置 |

### 5.2 类清单
| 类名 | 路径 | 继承/实现 | 说明 |
|------|------|-----------|------|
| PartnerTokenUI | `com.vtc.platformadmin.ui.auth` | extends BaseUI | Token 接口 Controller |
| PartnerTokenIssueRequest | `com.vtc.platformadmin.ui.dto.auth` | - | 签发请求 DTO |
| PartnerTokenIssueResponse | `com.vtc.platformadmin.ui.dto.auth` | - | 签发响应 DTO |
| PartnerTokenIntrospectRequest | `com.vtc.platformadmin.ui.dto.auth` | - | 校验请求 DTO |
| PartnerTokenIntrospectResponse | `com.vtc.platformadmin.ui.dto.auth` | - | 校验响应 DTO |
| IPartnerTokenAppService | `com.vtc.platformadmin.app.service` | - | Token 应用服务接口 |
| PartnerTokenAppServiceImpl | `com.vtc.platformadmin.app.service.impl` | extends AppServiceImpl | Token 应用服务实现 |
| PartnerTokenRedisStore | `com.vtc.platformadmin.infra.redis` | @Component | Redis 存储操作 |
| PartnerContextFilter | `com.vtc.platformadmin.infra.filter` | extends OncePerRequestFilter | 请求上下文过滤器 |

---

## 6. 迁移文件清单表

| 来源（open-api-service） | 目标（platform-admin） | 改动说明 |
|--------------------------|-------------------------|----------|
| `ui/auth/PartnerTokenUI.java` | `com.vtc.platformadmin.ui.auth.PartnerTokenUI` | 改包名；适配 BaseUI；注入 AppService 而非直接调用 Redis |
| `ui/dto/auth/PartnerTokenIssueRequest.java` | `com.vtc.platformadmin.ui.dto.auth.PartnerTokenIssueRequest` | 改包名 |
| `ui/dto/auth/PartnerTokenIssueResponse.java` | `com.vtc.platformadmin.ui.dto.auth.PartnerTokenIssueResponse` | 改包名 |
| `ui/dto/auth/PartnerTokenIntrospectRequest.java` | `com.vtc.platformadmin.ui.dto.auth.PartnerTokenIntrospectRequest` | 改包名 |
| `ui/dto/auth/PartnerTokenIntrospectResponse.java` | `com.vtc.platformadmin.ui.dto.auth.PartnerTokenIntrospectResponse` | 改包名 |
| `app/service/IPartnerTokenAppService.java` | `com.vtc.platformadmin.app.service.IPartnerTokenAppService` | 改包名 |
| `app/service/impl/PartnerTokenAppServiceImpl.java` | `com.vtc.platformadmin.app.service.impl.PartnerTokenAppServiceImpl` | 改包名；适配 AppServiceImpl；注入 PartnerDomainService 与 PartnerTokenRedisStore |
| `infra/redis/PartnerTokenRedisStore.java` | `com.vtc.platformadmin.infra.redis.PartnerTokenRedisStore` | 改包名；保持 sha256Hex 等核心逻辑 |
| `infra/filter/PartnerContextFilter.java` | `com.vtc.platformadmin.infra.filter.PartnerContextFilter` | 改包名；适配 Spring Boot 自动配置 |

---

## 7. 接口契约

### 7.1 POST /oauth/token
签发 Partner Token（client_credentials 模式）。

**请求**：
```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=cli_abc123&client_secret=***
```

**响应**：
```json
{
  "access_token": "xxx",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### 7.2 POST /api/open/v1/oauth/token
路径兼容接口，逻辑同 `/oauth/token`。

### 7.3 POST /internal/token/introspect
供 gateway 降级校验 Token。

**请求**：
```json
{
  "token": "xxx"
}
```

**响应**：
```json
{
  "active": true,
  "subjectType": "PARTNER",
  "partnerId": "partner-siem-01",
  "capabilities": ["TASK_WRITE", "TASK_READ"],
  "clientId": "cli_abc123",
  "exp": 1747872000
}
```

---

## 8. 数据表与 Liquibase
无需新建表，共享 `open_api` 库的 `partner_credential`、`partner_capability` 表（由 M1 迁入）。

---

## 9. 与 EventBus 集成点
无直接集成点。

---

## 10. 验收标准（编号 AC-x）

| 编号 | 验收描述 | 测试方法 |
|------|----------|----------|
| AC-1 | platform-admin 可通过 `/oauth/token` 接口签发 Token | 手动调用接口验证 |
| AC-2 | Token 写入 Redis，键为 `partner:token:{sha256(token)}` | 检查 Redis 数据 |
| AC-3 | `/internal/token/introspect` 接口可正确校验 Token | 手动调用接口验证 |
| AC-4 | gateway 可无缝切换路由至 platform-admin，Token 校验正常 | 集成测试 |
| AC-5 | 代码符合 DDD 四层规范 | 代码审查 |
| AC-6 | mvn test 全绿 | 执行测试 |

---

## 11. multi-agent 拆分建议

### 11.1 Agent 划分
| Agent 名称 | 负责文件 | 依赖 |
|------------|----------|------|
| **Agent A：DTO 与 UI 层** | PartnerTokenIssueRequest/Response、PartnerTokenIntrospectRequest/Response、PartnerTokenUI | M1 PartnerCredentialDO |
| **Agent B：App 与 Infra 层** | IPartnerTokenAppService、PartnerTokenAppServiceImpl、PartnerTokenRedisStore、PartnerContextFilter | Agent A、M1 PartnerDomainService |
| **Agent C：验证与测试** | 单元测试、集成测试 | Agent A、Agent B |

### 11.2 执行顺序
1. Agent A：创建 DTO 与 PartnerTokenUI
2. Agent B：创建 AppService 与 Infra 层组件
3. Agent C：编写测试并验证

---

## 12. 风险与遗留

### 12.1 风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Redis 共享导致缓存键冲突 | 低 | 高 | 保持键前缀 `partner:token:` 与 open-api-service 一致 |
| gateway 路由切换导致服务不可用 | 中 | 高 | 先灰度切换，验证通过后全量 |

### 12.2 遗留
- open-api-service 的 Token 接口在迁移后需保留一段时间，待 gateway 全量切换后下线

---
