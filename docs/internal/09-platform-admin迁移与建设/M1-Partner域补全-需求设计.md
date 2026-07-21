# M1 Partner 域补全需求设计

> 版本：v1.0
> 日期：2026-06-25
> 上游文档：[00-主计划.md](./00-主计划.md)
> 里程碑归属：M1

---

## 1. 背景与目标

### 1.1 背景

目前 platform-admin 已经完成了基础骨架搭建和 EventCenter 接入，但 Partner 域仅完成了基础 Partner 实体的迁移，缺少：
- 凭证管理（PartnerCredential）
- 能力管理（PartnerCapability）
- Webhook 配置管理（PartnerWebhookConfig）
- Webhook Secret 生成器
- Partner 常量与上下文

此外，PartnerWebhookConfigRepositoryImpl 当前是桩实现，返回 null，导致 Webhook 投递功能无法正常工作。

### 1.2 目标

补全 platform-admin Partner 域的所有缺失能力，确保：
- 凭证管理完整可用（创建、查询）
- 能力查询完整可用
- Webhook 配置查询与 Secret 轮换完整可用
- PartnerWebhookConfigRepositoryImpl 去桩，真实查询数据库
- 所有代码遵循 DDD 四层合规要求
- 接口路径与字段保持不变，前端无感

---

## 2. 需求清单

### 2.1 功能性需求

| 编号 | 需求描述 | 优先级 |
|------|---------|-------|
| FR-1 | 迁移 PartnerCredentialDO 并补充 @Component/@Scope | 高 |
| FR-2 | 迁移 PartnerCapabilityDO 并补充 @Component/@Scope | 高 |
| FR-3 | 调整 PartnerWebhookConfigDO 位置到 domain/partner 下，补充完整字段 | 高 |
| FR-4 | 创建 PartnerCredentialPO、PartnerCapabilityPO、PartnerWebhookConfigPO | 高 |
| FR-5 | 创建 PartnerCredentialMapper、PartnerCapabilityMapper、PartnerWebhookConfigMapper | 高 |
| FR-6 | 创建对应的 DomainConvertor | 高 |
| FR-7 | 创建 IPartnerCredentialRepository、IPartnerCapabilityRepository、IPartnerWebhookConfigRepository | 高 |
| FR-8 | 创建对应的 RepositoryImpl，继承 DatabaseRepositoryImpl | 高 |
| FR-9 | 迁移 PartnerConstants | 中 |
| FR-10 | 迁移 PartnerContext | 中 |
| FR-11 | 迁移 WebhookSecretGenerator，保留现状（写明文 secret），记 TODO 待 M3 | 中 |
| FR-12 | 完善 PartnerAdminUI，补充凭证管理、Webhook Secret 轮换接口 | 高 |
| FR-13 | 完善 IPartnerAdminAppService 及实现类，补充相关业务方法 | 高 |
| FR-14 | 完善 PartnerDomainService，补充相关领域方法 | 中 |

### 2.2 非功能性需求

| 编号 | 需求描述 | 优先级 |
|------|---------|-------|
| NFR-1 | 所有代码遵循 DDD 四层合规要求 | 高 |
| NFR-2 | 接口路径、方法签名、DTO 字段保持不变，前端无感 | 高 |
| NFR-3 | 共享 open_api 库，不重复建表 | 高 |
| NFR-4 | mvn test 全绿 | 高 |

---

## 3. 现状分析

### 3.1 open-api-service 现有实现

open-api-service 中 Partner 域已完整实现，包括：
- 实体：PartnerCredentialDO、PartnerCapabilityDO、PartnerWebhookConfigDO
- PO：PartnerCredentialPO、PartnerCapabilityPO、PartnerWebhookConfigPO
- Mapper：PartnerCredentialMapper、PartnerCapabilityMapper、PartnerWebhookConfigMapper
- Convertor：PartnerCredentialDomainConvertor、PartnerCapabilityDomainConvertor、PartnerWebhookConfigDomainConvertor
- 支持类：PartnerConstants、PartnerContext、WebhookSecretGenerator
- UI：PartnerAdminUI 包含完整的凭证管理、Webhook Secret 轮换接口

### 3.2 platform-admin 当前缺口

| 组件 | 现状 | 缺口 |
|------|------|------|
| PartnerCredentialDO | ❌ 缺失 | 需要创建，补充 @Component/@Scope |
| PartnerCapabilityDO | ❌ 缺失 | 需要创建，补充 @Component/@Scope |
| PartnerWebhookConfigDO | ⚠️ 存在但位置不对、字段不全 | 在 domain/webhook 下，需要移到 domain/partner 下，补充完整字段 |
| PO | ❌ 全部缺失 | 需要创建 3 个 PO |
| Mapper | ❌ 全部缺失 | 需要创建 3 个 Mapper |
| Convertor | ❌ 全部缺失 | 需要创建 3 个 DomainConvertor |
| Repository | ❌ 全部缺失 | 需要创建 3 个 Repository 接口及实现 |
| PartnerWebhookConfigRepositoryImpl | ⚠️ 桩实现 | 需要去桩，真实查询数据库 |
| PartnerConstants | ❌ 缺失 | 需要迁移 |
| PartnerContext | ❌ 缺失 | 需要迁移 |
| WebhookSecretGenerator | ❌ 缺失 | 需要迁移 |
| PartnerAdminUI | ⚠️ 部分实现 | 需要补充凭证管理、Webhook Secret 轮换接口 |

---

## 4. 领域模型设计

### 4.1 DO 字段表

#### PartnerCredentialDO

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| partnerId | String | 合作伙伴 ID |
| clientId | String | 客户端 ID |
| clientSecretHash | String | 客户端 Secret 哈希 |
| status | String | 状态 |
| expiresAt | Date | 过期时间 |
| createdAt | Date | 创建时间 |
| updatedAt | Date | 更新时间 |

**注解要求**：@Component、@Scope("prototype")、继承 BaseDO

#### PartnerCapabilityDO

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| partnerId | String | 合作伙伴 ID |
| capability | String | 能力 |
| createdAt | Date | 创建时间 |

**注解要求**：@Component、@Scope("prototype")、继承 BaseDO

#### PartnerWebhookConfigDO

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| partnerId | String | 合作伙伴 ID |
| callbackUrl | String | 回调 URL |
| webhookSecretHash | String | Webhook Secret 哈希 |
| webhookSecret | String | Webhook Secret 明文 |
| downloadableStages | String | 允许下载的阶段，逗号分隔 |
| updatedAt | Date | 更新时间 |

**位置调整**：从 domain/webhook/model/entity 移到 domain/partner/model/entity

**注解要求**：@Component、@Scope("prototype")、继承 BaseDO

### 4.2 枚举/常量

#### PartnerConstants

| 常量名 | 值 | 说明 |
|--------|----|------|
| STATUS_ACTIVE | "ACTIVE" | 激活状态 |
| STATUS_DISABLED | "DISABLED" | 禁用状态 |

### 4.3 值对象

无新增值对象。

---

## 5. 四层结构设计

### 5.1 层类清单

#### UI 层

| 类名 | 位置 | 说明 |
|------|------|------|
| PartnerAdminUI | ui/partner/ | 完善现有类，补充凭证管理、Webhook Secret 轮换接口 |

#### App 层

| 类名 | 位置 | 说明 |
|------|------|------|
| IPartnerAdminAppService | app/service/ | 补充业务方法接口 |
| PartnerAdminAppServiceImpl | app/service/impl/ | 补充业务方法实现 |
| PartnerCredentialAppConvertor | app/convert/ | 凭证 DTO 与 DO 转换 |
| PartnerWebhookSecretDTO | ui/dto/ | Webhook Secret DTO |

#### Domain 层

| 类名 | 位置 | 说明 |
|------|------|------|
| PartnerCredentialDO | domain/partner/model/entity/ | 新建 |
| PartnerCapabilityDO | domain/partner/model/entity/ | 新建 |
| PartnerWebhookConfigDO | domain/partner/model/entity/ | 调整位置并补充字段 |
| PartnerCredentialDomainConvertor | domain/partner/model/convert/ | 新建 |
| PartnerCapabilityDomainConvertor | domain/partner/model/convert/ | 新建 |
| PartnerWebhookConfigDomainConvertor | domain/partner/model/convert/ | 新建 |
| IPartnerCredentialRepository | domain/partner/repository/ | 新建，继承 IDatabaseRepository |
| IPartnerCapabilityRepository | domain/partner/repository/ | 新建，继承 IDatabaseRepository |
| IPartnerWebhookConfigRepository | domain/partner/repository/ | 调整位置 |
| IPartnerDomainService | domain/partner/service/business/ | 现有，可能需要补充方法 |
| PartnerDomainServiceImpl | domain/partner/service/business/impl/ | 现有，可能需要补充方法 |
| PartnerConstants | domain/partner/model/ | 新建 |
| PartnerContext | domain/partner/context/ | 新建 |
| WebhookSecretGenerator | domain/partner/model/support/ | 新建 |

#### Infra 层

| 类名 | 位置 | 说明 |
|------|------|------|
| PartnerCredentialPO | infra/dao/po/ | 新建 |
| PartnerCapabilityPO | infra/dao/po/ | 新建 |
| PartnerWebhookConfigPO | infra/dao/po/ | 新建 |
| PartnerCredentialMapper | infra/dao/ | 新建，继承 IBaseMapper |
| PartnerCapabilityMapper | infra/dao/ | 新建，继承 IBaseMapper |
| PartnerWebhookConfigMapper | infra/dao/ | 新建，继承 IBaseMapper |
| PartnerCredentialRepositoryImpl | infra/repository/ | 新建，继承 DatabaseRepositoryImpl |
| PartnerCapabilityRepositoryImpl | infra/repository/ | 新建，继承 DatabaseRepositoryImpl |
| PartnerWebhookConfigRepositoryImpl | infra/repository/ | 调整位置并去桩 |

---

## 6. 迁移文件清单表

| 来源文件（open-api-service） | 目标文件（platform-admin） | 改动说明 |
|---------------------------|---------------------------|---------|
| domain/partner/model/entity/PartnerCredentialDO.java | domain/partner/model/entity/PartnerCredentialDO.java | 改包名，补充 @Component/@Scope |
| domain/partner/model/entity/PartnerCapabilityDO.java | domain/partner/model/entity/PartnerCapabilityDO.java | 改包名，补充 @Component/@Scope |
| domain/partner/model/entity/PartnerWebhookConfigDO.java | domain/partner/model/entity/PartnerWebhookConfigDO.java | 改包名，移动位置，从现有简化版替换为完整版本 |
| domain/partner/model/convert/PartnerCredentialDomainConvertor.java | domain/partner/model/convert/PartnerCredentialDomainConvertor.java | 改包名 |
| domain/partner/model/convert/PartnerCapabilityDomainConvertor.java | domain/partner/model/convert/PartnerCapabilityDomainConvertor.java | 改包名 |
| domain/partner/model/convert/PartnerWebhookConfigDomainConvertor.java | domain/partner/model/convert/PartnerWebhookConfigDomainConvertor.java | 改包名 |
| domain/partner/model/PartnerConstants.java | domain/partner/model/PartnerConstants.java | 改包名 |
| domain/partner/context/PartnerContext.java | domain/partner/context/PartnerContext.java | 改包名，调整依赖（如 OpenApiException 可能需要处理） |
| domain/partner/model/support/WebhookSecretGenerator.java | domain/partner/model/support/WebhookSecretGenerator.java | 改包名，保留现状，记 TODO 待 M3 |
| infra/dao/po/PartnerCredentialPO.java | infra/dao/po/PartnerCredentialPO.java | 改包名 |
| infra/dao/po/PartnerCapabilityPO.java | infra/dao/po/PartnerCapabilityPO.java | 改包名 |
| infra/dao/po/PartnerWebhookConfigPO.java | infra/dao/po/PartnerWebhookConfigPO.java | 改包名 |
| infra/dao/PartnerCredentialMapper.java | infra/dao/PartnerCredentialMapper.java | 改包名 |
| infra/dao/PartnerCapabilityMapper.java | infra/dao/PartnerCapabilityMapper.java | 改包名 |
| infra/dao/PartnerWebhookConfigMapper.java | infra/dao/PartnerWebhookConfigMapper.java | 改包名 |
| - | domain/partner/repository/IPartnerCredentialRepository.java | 新建，参考 IPartnerRepository 风格 |
| - | domain/partner/repository/IPartnerCapabilityRepository.java | 新建，参考 IPartnerRepository 风格 |
| domain/webhook/repository/IPartnerWebhookConfigRepository.java | domain/partner/repository/IPartnerWebhookConfigRepository.java | 移动位置 |
| - | infra/repository/PartnerCredentialRepositoryImpl.java | 新建，参考 PartnerRepositoryImpl 风格 |
| - | infra/repository/PartnerCapabilityRepositoryImpl.java | 新建，参考 PartnerRepositoryImpl 风格 |
| infra/repository/PartnerWebhookConfigRepositoryImpl.java | infra/repository/PartnerWebhookConfigRepositoryImpl.java | 去桩，改为继承 DatabaseRepositoryImpl，参考 PartnerRepositoryImpl 风格 |
| ui/dto/admin/PartnerCredentialDTO.java | ui/dto/PartnerCredentialDTO.java | 改包名 |
| ui/dto/admin/PartnerWebhookSecretDTO.java | ui/dto/PartnerWebhookSecretDTO.java | 改包名 |
| app/convert/PartnerCredentialAppConvertor.java | app/convert/PartnerCredentialAppConvertor.java | 改包名 |

---

## 7. 接口契约

### 7.1 Controller 路径与方法签名

**路径保持不变，前端无感**

#### PartnerAdminUI

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /internal/admin/partners | 创建 Partner |
| GET | /internal/admin/partners | 分页查询 Partner |
| GET | /internal/admin/partners/{partnerId} | 查询 Partner 详情 |
| PUT | /internal/admin/partners/{partnerId} | 更新 Partner |
| POST | /internal/admin/partners/{partnerId}/credentials | 创建 Partner 凭证 |
| GET | /internal/admin/partners/{partnerId}/credentials | 查询 Partner 凭证列表 |
| POST | /internal/admin/partners/{partnerId}/webhook-secret/rotate | 轮换 Webhook Secret |

### 7.2 入参/出参 DTO

#### PartnerCredentialDTO

```java
// 字段保持与 open-api-service 一致
```

#### PartnerWebhookSecretDTO

```java
// 字段保持与 open-api-service 一致
```

---

## 8. 数据表与 Liquibase

### 8.1 数据表

| 表名 | 说明 | 状态 |
|------|------|------|
| partner_credential | 合作伙伴凭证表 | 已存在于 open_api 库，共享不重建 |
| partner_capability | 合作伙伴能力表 | 已存在于 open_api 库，共享不重建 |
| partner_webhook_config | 合作伙伴 Webhook 配置表 | 已存在于 open_api 库，共享不重建 |

### 8.2 Liquibase

**无需新增 Liquibase changelog**，platform-admin 不重复建表，直接共享 open_api 库现有表。

---

## 9. 与 EventBus 集成点

| 集成点 | 说明 | 状态 |
|------|------|------|
| 事件发布 | 无新增事件发布 | - |
| 事件消费 | 无新增事件消费 | - |
| 事件查询 | 无新增事件查询 | - |

**注意**：M1 不涉及 EventBus 集成，仅补全 Partner 域基础能力。

---

## 10. 验收标准

| 编号 | 验收内容 | 验证方式 |
|------|---------|---------|
| AC-1 | PartnerCredentialDO 创建成功，包含完整字段和正确注解 | 代码检查 |
| AC-2 | PartnerCapabilityDO 创建成功，包含完整字段和正确注解 | 代码检查 |
| AC-3 | PartnerWebhookConfigDO 调整到正确位置，包含完整字段 | 代码检查 |
| AC-4 | 3 个 PO 创建成功，正确映射表名 | 代码检查 |
| AC-5 | 3 个 Mapper 创建成功，继承 IBaseMapper | 代码检查 |
| AC-6 | 3 个 DomainConvertor 创建成功，注册为 @Component | 代码检查 |
| AC-7 | 3 个 Repository 接口创建成功，继承 IDatabaseRepository | 代码检查 |
| AC-8 | 3 个 RepositoryImpl 创建成功，继承 DatabaseRepositoryImpl，PartnerWebhookConfigRepositoryImpl 去桩 | 代码检查 |
| AC-9 | PartnerConstants、PartnerContext、WebhookSecretGenerator 迁移成功 | 代码检查 |
| AC-10 | PartnerAdminUI 补充了凭证管理、Webhook Secret 轮换接口 | 代码检查、接口测试 |
| AC-11 | 所有代码遵循 DDD 四层合规要求 | 代码检查 |
| AC-12 | mvn test 全绿 | 测试验证 |
| AC-13 | 接口路径与字段保持不变，前端调用正常 | 接口测试 |
| AC-14 | PartnerWebhookConfigRepositoryImpl 能真实查询数据库，Webhook 投递不再因配置缺失而跳过 | 集成测试 |

---

## 11. multi-agent 拆分建议

### 11.1 Agent 划分

| Agent 名称 | 负责文件 | 依赖 |
|-----------|---------|------|
| Agent 1 | 实体与 PO：PartnerCredentialDO、PartnerCapabilityDO、PartnerWebhookConfigDO、3 个 PO | - |
| Agent 2 | Mapper 与 Convertor：3 个 Mapper、3 个 DomainConvertor | Agent 1 |
| Agent 3 | Repository 层：3 个 Repository 接口、3 个 RepositoryImpl | Agent 2 |
| Agent 4 | 支持类：PartnerConstants、PartnerContext、WebhookSecretGenerator | - |
| Agent 5 | App 与 UI 层：完善 PartnerAdminUI、IPartnerAdminAppService 及实现、AppConvertor、DTO | Agent 3、Agent 4 |

### 11.2 执行顺序

1. Agent 1 → Agent 2 → Agent 3 → Agent 5
2. Agent 4 可与 Agent 1 并行
3. 最后全量验证，运行 mvn test

---

## 12. 风险与遗留

### 12.1 风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| PartnerWebhookConfigDO 位置调整导致现有引用报错 | 中 | 同步调整相关引用（如 IPartnerWebhookConfigRepository、WebhookDomainService） |
| PartnerContext 依赖 OpenApiException，platform-admin 可能没有该类 | 低 | 调整为 platform-admin 已有异常类型，或创建简单替代 |
| WebhookSecretGenerator 写明文 secret，与最佳实践不符 | 中 | M1 保留现状，记 TODO 待 M3 dispatcher 阶段统一改 hash |

### 12.2 遗留

| 遗留项 | 说明 | 处理计划 |
|------|------|---------|
| WebhookSecretGenerator 写明文 secret | M1 保留现状 | M3 dispatcher 阶段统一改 hash |
| PartnerContext 可能需要调整异常处理 | 视 platform-admin 已有异常体系而定 | M1 先迁移，后续根据需要优化 |

---
