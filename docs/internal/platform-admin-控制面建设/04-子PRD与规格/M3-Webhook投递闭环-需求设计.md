# M3: Webhook 投递闭环 - 需求设计文档

> **版本**: v1.0  
> **日期**: 2026-06-25  
> **上游文档**: [主计划](./00-主计划.md)、[open-api-export-webhook-PRD](../../open-platform-开放平台/04-子PRD与规格/open-api-export-webhook-PRD.md)  
> **里程碑归属**: platform-admin 建设 M3

---

## 1. 背景与目标

### 1.1 背景
当前 platform-admin 已具备基础的 Webhook 消费与投递日志记录能力，但存在以下关键缺口：
- **退避重试机制缺失**: 现有 `WebhookDomainServiceImpl` 仅进行一次投递尝试，失败后不重试
- **完整 HMAC-SHA256 签名**: 虽已有 `WebhookDeliveryAdapter`，但与完整配置和签名流程的整合需要验证
- **配置查询去桩化**: 依赖 M1 完成 `PartnerWebhookConfig` 的完整实现，当前为桩代码
- **Webhook 事件解析与元数据提取**: 缺失 `WebhookDeliverySupport` 等辅助工具类
- **测试支持能力**: 缺失 `WebhookTest` 相关接口与测试接收端功能
- **投递策略配置**: 缺失 `WebhookCallbackUrlResolver` 和应用级配置项

### 1.2 目标
- 实现完整的 Webhook 投递闭环：消费 OpenPlatformWebhookEvent → 配置查询 → 签名计算 → HTTP 投递 → 退避重试 → 日志记录
- 确保与 open-api-service 的行为一致，前端接口保持不变
- 满足 API 文档 §6 的签名与协议规范
- 实现幂等投递与失败重试机制
- 补充测试支持接口

---

## 2. 需求清单

### 2.1 功能性需求 (FR)
| 编号 | 需求描述 | 优先级 | 依赖 |
|------|----------|--------|------|
| FR-M3-1 | 实现 `WebhookCallbackUrlResolver`，支持 Partner 配置与测试接收端双路解析 | 高 | M1 |
| FR-M3-2 | 实现 `WebhookDeliverySupport`，提供 eventId 解析、资源绑定等功能 | 高 | M1 |
| FR-M3-3 | 完善 `WebhookDomainServiceImpl`，实现退避重试与完整投递编排 | 高 | FR-M3-1, FR-M3-2 |
| FR-M3-4 | 实现 `IWebhookPublishService` 及其实现（如需要） | 中 | - |
| FR-M3-5 | 实现 `WebhookTest` 相关接口（测试 UI、App Service 等） | 中 | - |
| FR-M3-6 | 补充 `WebhookEventType` 枚举与相关事件模型 | 中 | - |
| FR-M3-7 | 更新 `WebhookDeliveryAdapter`，确保与 platform-admin 配置项兼容 | 高 | - |
| FR-M3-8 | 完善 `WebhookDeliveryLogDO` 与相关仓储能力 | 中 | - |

### 2.2 非功能性需求 (NFR)
| 编号 | 需求描述 |
|------|----------|
| NFR-M3-1 | 退避重试策略：默认最大重试 10 次，退避间隔 60s、300s、900s、1800s、3600s、7200s（可配置） |
| NFR-M3-2 | 幂等性：同一 eventId 只投递一次，依赖数据库唯一约束保证 |
| NFR-M3-3 | HMAC-SHA256 签名：使用 `partner_webhook_config.webhookSecret` 对 payload 签名，放入 `X-Webhook-Signature` 头 |
| NFR-M3-4 | DDD 四层合规：遵循 spore-base-ddd 基类规范 |
| NFR-M3-5 | 前端接口兼容：路径、参数、返回值与 open-api-service 保持一致 |

---

## 3. 现状分析

### 3.1 open-api-service 现有实现（参考源）
open-api-service 中已有完整的 Webhook 投递实现，主要文件清单：
- `infra/adapter/WebhookDeliveryAdapter.java` - HTTP 投递与 HMAC 签名
- `infra/webhook/WebhookCallbackUrlResolver.java` - URL 解析
- `domain/open/model/entity/WebhookDeliveryLogDO.java` - 投递记录
- `domain/open/model/support/WebhookDeliverySupport.java` - 辅助工具
- `domain/webhook/service/business/IWebhookDomainService.java + impl` - 投递编排
- `domain/webhook/service/business/IWebhookPublishService.java + impl` - 发布服务
- `domain/webhook/service/event/WebhookEventListener.java` - 事件监听
- `domain/webhook/model/event/` - 事件模型（WebhookEvent、WebhookEventType、ArtifactReadyEvent）
- `app/service/IWebhookTestAppService.java + impl` - 测试接口
- `app/convert/WebhookDeliveryLogAppConvertor.java` - 转换器
- `app/support/WebhookDeliveryEnricher.java` - 数据丰富器
- `ui/admin/WebhookTestAdminUI.java` - 测试管理 UI
- `ui/dev/WebhookTestReceiverUI.java` - 开发测试接收端
- `infra/dev/WebhookTestInbox.java` - 测试收件箱

### 3.2 platform-admin 当前现状
platform-admin 中已有部分 Webhook 相关实现，现状如下：

| 组件 | 现状 | 说明 |
|------|------|------|
| `WebhookDeliveryAdapter.java` | ✅ 已存在 | 位于 `infra/adapter/`，但需要验证与 open-api-service 的一致性 |
| `OpenPlatformWebhookEventHandler.java` | ✅ 已存在 | 消费 EventBus 事件，调用 `webhookDomainService.deliver()` |
| `WebhookDeliveryLogDO.java` | ✅ 已存在 | 位于 `domain/webhook/model/entity/`，但需要与 open-api-service 对齐字段 |
| `PartnerWebhookConfigDO.java` | ⚠️ 桩代码 | 依赖 M1 完成完整实现 |
| `IWebhookDomainService.java + impl` | ⚠️ 简化版 | 仅一次投递尝试，无重试，功能需要增强 |
| `IWebhookDeliveryLogRepository.java + impl` | ✅ 已存在 | 但可能需要增强查询能力 |
| `WebhookDeliveryLogDomainConvertor.java` | ✅ 已存在 | - |
| `WebhookCallbackUrlResolver.java` | ❌ 缺失 | - |
| `WebhookDeliverySupport.java` | ❌ 缺失 | - |
| `WebhookEventType.java` | ❌ 缺失 | - |
| `WebhookTest` 相关接口 | ❌ 缺失 | - |

---

## 4. 领域模型设计

### 4.1 DO 字段表

#### WebhookDeliveryLogDO（需与 open-api-service 对齐）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| partnerId | String | 合作方 ID |
| eventType | String | 事件类型 |
| eventId | String | 事件 ID（幂等键） |
| resourceType | String | 资源类型 |
| resourceId | String | 资源 ID |
| resourceIdsJson | String | 资源 ID 列表 JSON |
| triggerSource | String | 触发源（FIRST_ATTEMPT/AUTO_RETRY/MANUAL_RETRY） |
| payloadJson | String | 完整 payload JSON |
| callbackUrl | String | 回调 URL |
| httpStatus | Integer | HTTP 状态码 |
| retryCount | Integer | 重试次数 |
| status | String | 状态（PENDING/SUCCESS/FAILED） |
| createdAt | Date | 创建时间 |
| nextRetryAt | Date | 下次重试时间 |

### 4.2 枚举/常量
- `WebhookEventType`：事件类型枚举（TASK_COMPLETED、TASK_FAILED、EXPORT_READY、INSTANCE_VERIFY_FIX_COMPLETED、ARTIFACT_READY）
- `WebhookDeliverySupport` 常量：
  - TRIGGER_FIRST_ATTEMPT = "FIRST_ATTEMPT"
  - TRIGGER_AUTO_RETRY = "AUTO_RETRY"
  - TRIGGER_MANUAL_RETRY = "MANUAL_RETRY"
  - RESOURCE_TASK = "TASK"
  - RESOURCE_INSTANCE = "INSTANCE"
  - RESOURCE_EXPORT = "EXPORT"
  - RESOURCE_VERIFY_FIX_JOB = "VERIFY_FIX_JOB"

### 4.3 值对象
- `WebhookEvent`：事件模型
- `OpenPlatformWebhookEvent`：platform-admin 事件总线事件（已存在）
- `WebhookDeliverySupport.ResourceBinding`：资源绑定
- `WebhookDeliverySupport.ExportReadyInfo`：外发就绪信息
- `WebhookDeliverySupport.EventDeliverySummary`：投递汇总

---

## 5. 四层结构设计

### 5.1 UI 层
| 类名 | 继承基类 | 说明 |
|------|----------|------|
| `WebhookTestAdminUI` | `BaseUI` | Webhook 测试管理界面，路径 `/internal/admin/webhook-tests` |
| `WebhookTestReceiverUI` | `BaseUI` | 开发测试接收端（可选，根据实际需要） |

### 5.2 App 层
| 类名 | 继承基类/实现接口 | 说明 |
|------|------------------|------|
| `IWebhookTestAppService` | - | Webhook 测试应用服务接口 |
| `WebhookTestAppServiceImpl` | `AppServiceImpl<DS, DO, DTO>` | 应用服务实现 |
| `WebhookDeliveryLogAppConvertor` | - | DTO ↔ DO 转换器，`@Component` 注册到 ConvertHelper |
| `WebhookDeliveryEnricher` | - | 数据丰富器（可选） |

### 5.3 Domain 层
| 类名 | 继承基类/实现接口 | 说明 |
|------|------------------|------|
| `IWebhookDomainService` | - | Webhook 领域服务接口 |
| `WebhookDomainServiceImpl` | `DomainServiceImpl<Repository, DO>` | 领域服务实现（需增强） |
| `IWebhookPublishService` | - | Webhook 发布服务接口（可选） |
| `WebhookPublishServiceImpl` | - | 发布服务实现（可选） |
| `WebhookDeliverySupport` | - | 辅助工具类 |
| `WebhookEventType` | `Enum` | 事件类型枚举 |
| `WebhookEvent` | - | 事件模型 |
| `WebhookDeliveryLogDO` | `BaseDO` + `@Component @Scope("prototype")` | 投递记录 DO |

### 5.4 Infra 层
| 类名 | 继承基类/实现接口 | 说明 |
|------|------------------|------|
| `IWebhookDeliveryLogRepository` | `IDatabaseRepository<WebhookDeliveryLogDO>` | 仓储接口 |
| `WebhookDeliveryLogRepositoryImpl` | `DatabaseRepositoryImpl<Mapper, DO, PO>` | 仓储实现 |
| `IPartnerWebhookConfigRepository` | `IDatabaseRepository<PartnerWebhookConfigDO>` | 配置仓储接口（依赖 M1） |
| `PartnerWebhookConfigRepositoryImpl` | `DatabaseRepositoryImpl<Mapper, DO, PO>` | 配置仓储实现（依赖 M1） |
| `WebhookDeliveryAdapter` | - | HTTP 投递适配器 |
| `WebhookCallbackUrlResolver` | - | URL 解析器 |
| `WebhookTestInbox` | - | 测试收件箱（可选） |

---

## 6. 迁移文件清单表

| 源文件（open-api-service） | 目标文件（platform-admin） | 改动说明 |
|----------------------------|----------------------------|----------|
| `infra/adapter/WebhookDeliveryAdapter.java` | `infra/adapter/WebhookDeliveryAdapter.java` | 改包名，验证与 platform-admin 配置项兼容 |
| `infra/webhook/WebhookCallbackUrlResolver.java` | `infra/webhook/WebhookCallbackUrlResolver.java` | 改包名，适配 partnerRepository |
| `domain/open/model/support/WebhookDeliverySupport.java` | `domain/webhook/model/support/WebhookDeliverySupport.java` | 改包名，路径调整，移除对 open-api-service 特有类的依赖 |
| `domain/webhook/model/WebhookEventType.java` | `domain/webhook/model/WebhookEventType.java` | 新增 |
| `domain/webhook/model/WebhookEvent.java` | `domain/webhook/model/WebhookEvent.java` | 新增（或复用 OpenPlatformWebhookEvent） |
| `domain/webhook/service/business/IWebhookDomainService.java` | `domain/webhook/service/business/IWebhookDomainService.java` | 验证接口一致性，补充缺失方法 |
| `domain/webhook/service/business/impl/WebhookDomainServiceImpl.java` | `domain/webhook/service/business/impl/WebhookDomainServiceImpl.java` | 增强现有实现，添加退避重试、WebhookCallbackUrlResolver 集成、WebhookDeliverySupport 集成 |
| `domain/webhook/service/business/IWebhookPublishService.java` | `domain/webhook/service/business/IWebhookPublishService.java` | 新增（如需要） |
| `domain/webhook/service/business/impl/WebhookPublishServiceImpl.java` | `domain/webhook/service/business/impl/WebhookPublishServiceImpl.java` | 新增（如需要） |
| `app/service/IWebhookTestAppService.java` | `app/service/IWebhookTestAppService.java` | 新增 |
| `app/service/impl/WebhookTestAppServiceImpl.java` | `app/service/impl/WebhookTestAppServiceImpl.java` | 新增 |
| `app/convert/WebhookDeliveryLogAppConvertor.java` | `app/convert/WebhookDeliveryLogAppConvertor.java` | 新增 |
| `app/support/WebhookDeliveryEnricher.java` | `app/support/WebhookDeliveryEnricher.java` | 新增（如需要） |
| `ui/admin/WebhookTestAdminUI.java` | `ui/admin/WebhookTestAdminUI.java` | 新增 |
| `ui/dev/WebhookTestReceiverUI.java` | `ui/dev/WebhookTestReceiverUI.java` | 新增（可选） |
| `infra/dev/WebhookTestInbox.java` | `infra/dev/WebhookTestInbox.java` | 新增（可选） |

---

## 7. 接口契约

### 7.1 WebhookTestAdminUI 接口
保持与 open-api-service 完全一致：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/internal/admin/webhook-tests/send` | 发送测试 Webhook |
| GET | `/internal/admin/webhook-tests/{deliveryLogId}` | 获取投递记录详情 |
| POST | `/internal/admin/webhook-tests/{deliveryLogId}/retry` | 手动重试 |
| GET | `/internal/admin/webhook-tests` | 投递记录列表 |

---

## 8. 数据表与 Liquibase
- **共享表**: `webhook_delivery_log` - 与 open-api-service 共享 `open_api` 库，不重复建表
- **配置表**: `partner_webhook_config` - 依赖 M1 实现，共享 `open_api` 库

### 8.1 唯一约束
- `uk_webhook_delivery_log_event_id` - 确保同一 eventId 只投递一次

---

## 9. 与 EventBus 集成点
- **消费事件**: `OpenPlatformWebhookEvent` 由 `OpenPlatformWebhookEventHandler` 消费
- **事件处理**: 调用 `webhookDomainService.deliver(event)` 进行投递
- **流程**: EventBus → `OpenPlatformWebhookEventHandler` → `WebhookDomainServiceImpl` → `WebhookDeliveryAdapter` → Partner callback URL

---

## 10. 验收标准 (AC)

| 编号 | 验收场景 | 预期结果 |
|------|----------|----------|
| AC-M3-1 | 消费 OpenPlatformWebhookEvent 后执行投递 | 成功调用 Partner callback URL，携带正确的 HMAC-SHA256 签名 |
| AC-M3-2 | 投递失败场景 | 按照退避策略重试，超过最大重试次数后标记为 FAILED |
| AC-M3-3 | 幂等投递 | 同一 eventId 只投递一次，不产生重复日志 |
| AC-M3-4 | WebhookTest 接口可用 | 测试接口正常工作，可发送测试 Webhook、查看日志、手动重试 |
| AC-M3-5 | DDD 四层合规 | 所有类遵循 spore-base-ddd 基类规范，mvn compile 通过 |
| AC-M3-6 | mvn test 全绿 | 所有单元测试和集成测试通过 |

---

## 11. multi-agent 拆分建议

### 11.1 Agent 拆分方案
建议拆分为以下 3 个 Agent 并行协作：

| Agent | 职责范围 | 依赖 | 主要文件 |
|-------|----------|------|----------|
| Agent 1 | 基础设施层组件 | - | WebhookCallbackUrlResolver、WebhookDeliveryAdapter 更新、WebhookTestInbox |
| Agent 2 | 领域层增强 | Agent 1 | WebhookDeliverySupport、WebhookEventType、WebhookEvent、WebhookDomainServiceImpl 增强、WebhookPublishService |
| Agent 3 | App/UI 层实现 | Agent 2 | WebhookTestAppService、WebhookDeliveryLogAppConvertor、WebhookTestAdminUI、WebhookTestReceiverUI |

### 11.2 共享文件先行编辑
- `application.yml` - 添加 webhook 配置项（max-retry、retry-backoff 等）
- `PlatformAdminProperties.java` - 添加 Webhook 配置属性绑定

---

## 12. 风险与遗留

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| M1 未按时交付 PartnerWebhookConfig 完整实现 | 高 | 可先使用桩代码进行开发，M1 完成后替换 |
| WebhookSecret 明文存储问题 | 中 | 与 M1 协调，统一改为 webhookSecretHash |
| open-api-service 与 platform-admin 并行写入同一表 | 中 | 收口阶段完成后关闭 open-api-service 对应接口 |
| 测试接收端功能必要性 | 低 | 根据实际需要决定是否实现，可降低优先级 |

---

**文档结束**
