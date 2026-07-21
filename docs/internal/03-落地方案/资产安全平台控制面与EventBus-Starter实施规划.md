# 资产安全平台控制面与 EventBus Starter 实施规划

> 版本：v1.0  日期：2026-06-24  
> 上游设计：`01-架构与总览/资产安全平台控制面与EventBus-Starter架构设计.md`  
> 目标：将 `platform-admin` 统一控制面与独立 `asset-security-platform-starters` 规划拆解为可执行开发阶段、工程任务、验收标准和风险回滚方案。

---

## 0. 实施结论

本实施规划按“先框架、再链路、再治理、再任务中心”的顺序推进：

```text
Phase 0  命名与工程边界确认
Phase 1  asset-security-platform-starters 建项
Phase 2  asset-security-starter-eventbus MVP
Phase 3  platform-admin 建项与 eventcenter 基础域
Phase 4  调用记录事件链路接入
Phase 5  Webhook 业务事件链路接入
Phase 6  Event Center 管理面与 eventbus-admin
Phase 7  Outbox / Inbox / DLQ / 重放增强
Phase 8  Task Center 融合规划落地
```

核心落地原则：

1. 先做 `asset-security-starter-eventbus` runtime，保证业务服务能发、能收；
2. 再做 `platform-admin.eventcenter` 基础治理，保证事件能查、能追踪；
3. 调用记录事件优先接入，验证异步非阻塞链路；
4. Webhook 业务事件第二批接入，验证可靠发布与幂等消费；
5. Outbox / Inbox / DLQ / 重放在业务链路跑通后增强；
6. Task Center 后续作为同一控制面模式继续融合。

---

## 1. 前置决策

### 1.1 服务命名

推荐直接采用：

```text
project_backend/svmp/platform-admin
spring.application.name = platform-admin
根包 = com.vtc.platformadmin
```

如短期必须兼容原文档中的 `partner-admin`，则：

```text
服务物理名可暂为 partner-admin；
架构定位仍按 platform-admin；
内部包与模块按 partner / eventcenter / taskcenter / webhook / invocation 等领域拆分；
后续通过服务名和路由迁移为 platform-admin。
```

优先级建议：

| 方案 | 推荐度 | 说明 |
|---|---:|---|
| 直接新建 `platform-admin` | 高 | 语义正确，避免后续改名 |
| 先建 `partner-admin`，内部按 platform-admin 规划 | 中 | 兼容已定文档，但未来有命名迁移成本 |

### 1.2 Starter 组命名

推荐：

```text
project_backend/framework/platform/asset-security-platform-starters/
```

Parent：

```text
asset-security-platform-starters-parent
```

第一批模块：

```text
asset-security-starter-eventbus
asset-security-starter-eventbus-admin
```

第二批模块：

```text
asset-security-starter-task-admin
```

### 1.3 Maven 坐标

优先建议：

```xml
<groupId>com.vtc.asset.security</groupId>
<artifactId>asset-security-platform-starters-parent</artifactId>
<version>3.0.2-SNAPSHOT</version>
```

若内部仓库规范要求统一 `com.vtc`，则使用：

```xml
<groupId>com.vtc</groupId>
<artifactId>asset-security-platform-starters-parent</artifactId>
<version>3.0.2-SNAPSHOT</version>
```

### 1.4 技术栈约束

对齐现有后端体系：

| 项 | 约束 |
|---|---|
| Java | 1.8 |
| Spring Boot 自动配置 | `META-INF/spring.factories` |
| 微服务 DDD | 对齐 esmp-support / spore-base-ddd 四层结构 |
| 默认业务参考 | `project_backend/svmp/vul-pass/` |
| Starter 风格参考 | `project_backend/framework/asset/esmp-starters/` |
| 管理服务参考 | `project_backend/svmp/open-api-service/` 与后续 `platform-admin` |

---

## 2. 目标工程结构

### 2.1 平台 starter 工程

```text
project_backend/framework/platform/asset-security-platform-starters/
├── pom.xml
├── asset-security-starter-eventbus/
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/vtc/asset/security/platform/eventbus/
│       │   ├── api/
│       │   ├── annotation/
│       │   ├── config/
│       │   ├── codec/
│       │   ├── transport/
│       │   │   ├── local/
│       │   │   ├── kafka/
│       │   │   └── redis/
│       │   ├── outbox/
│       │   ├── inbox/
│       │   ├── dlq/
│       │   ├── trace/
│       │   └── telemetry/
│       └── resources/META-INF/spring.factories
│
├── asset-security-starter-eventbus-admin/
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/vtc/asset/security/platform/eventbus/admin/
│       │   ├── catalog/
│       │   ├── schema/
│       │   ├── subscription/
│       │   ├── trace/
│       │   ├── dlq/
│       │   ├── replay/
│       │   └── audit/
│       └── resources/META-INF/spring.factories
│
└── asset-security-starter-task-admin/
    └── pom.xml
```

### 2.2 platform-admin 工程

推荐：

```text
project_backend/svmp/platform-admin/
```

包结构：

```text
com.vtc.platformadmin
├── ui
│   ├── partner
│   ├── eventcenter
│   ├── taskcenter
│   ├── webhook
│   ├── invocation
│   ├── operationcase
│   └── audit
├── app
│   ├── partner
│   ├── eventcenter
│   ├── taskcenter
│   ├── webhook
│   ├── invocation
│   ├── operationcase
│   └── audit
├── domain
│   ├── partner
│   ├── eventcenter
│   ├── taskcenter
│   ├── webhook
│   ├── invocation
│   ├── operationcase
│   └── audit
└── infra
    ├── dao
    ├── repository
    ├── config
    ├── eventbus
    └── feign
```

原则：

```text
ui → app → domain → infra
```

事件中心、任务中心、Partner 管理等域可以协作，但不直接跨域访问 Mapper / Repository。

---

## 3. Phase 0：命名与边界确认

### 3.1 目标

完成正式命名和工程边界决策，避免后续返工。

### 3.2 任务

| 编号 | 任务 | 输出 |
|---|---|---|
| P0-1 | 确认服务名使用 `platform-admin` 还是 `partner-admin` 过渡 | 服务命名决策 |
| P0-2 | 确认 starter groupId 使用 `com.vtc.asset.security` 还是 `com.vtc` | Maven 坐标决策 |
| P0-3 | 确认独立 starter 目录 | `framework/platform/asset-security-platform-starters` |
| P0-4 | 确认 EventBus 首期 transport | local + kafka |
| P0-5 | 确认调用记录是否首批接入 EventBus | 默认是 |
| P0-6 | 确认 Webhook 业务事件是否首批使用 Outbox | 默认 Phase 5 后增强 |

### 3.3 验收

- 命名不再摇摆；
- 工程目录确认；
- 首期范围确认；
- 上游架构文档与本实施规划一致。

---

## 4. Phase 1：asset-security-platform-starters 建项

### 4.1 目标

创建独立平台级 starter parent，不修改现有 `esmp-starters`。

### 4.2 任务

| 编号 | 任务 | 文件/目录 |
|---|---|---|
| P1-1 | 新建 parent 工程 | `project_backend/framework/platform/asset-security-platform-starters/pom.xml` |
| P1-2 | 新建 `asset-security-starter-eventbus` 模块 | `asset-security-starter-eventbus/` |
| P1-3 | 新建 `asset-security-starter-eventbus-admin` 模块骨架 | `asset-security-starter-eventbus-admin/` |
| P1-4 | 配置 Java 1.8、UTF-8、dependencyManagement | parent pom |
| P1-5 | 配置 starter 自动配置机制 | `META-INF/spring.factories` |
| P1-6 | 增加 README | `README.md` |

### 4.3 验收

- parent 能单独 Maven 编译；
- 子模块能被业务服务以 Maven dependency 引入；
- 不修改 `project_backend/framework/asset/esmp-starters/pom.xml`；
- starter 包名不使用 `com.vtc.eventbus` 这种过泛命名，使用平台域包名。

---

## 5. Phase 2：asset-security-starter-eventbus MVP

### 5.1 目标

实现 EventBus runtime 最小可用能力，使业务服务能以统一 API 发布和消费事件。

### 5.2 MVP 范围

包含：

```text
DomainEvent
EventEnvelope
EventBus
EventPublishResult
EventContext
@EventListener
EventTransport SPI
LocalEventTransport
KafkaEventTransport
JacksonEventCodec
EventBusProperties
EventBusAutoConfiguration
基础 traceId / eventId / idempotentKey
基础 DLQ topic 投递
```

不包含：

```text
Outbox
Inbox
完整事件中心 UI
Schema 兼容校验
灰度策略
人工重放
```

### 5.3 API 任务

| 编号 | 任务 | 包 |
|---|---|---|
| P2-1 | 定义 `DomainEvent` | `eventbus.api` |
| P2-2 | 定义 `EventEnvelope<T>` | `eventbus.api` |
| P2-3 | 定义 `EventBus` | `eventbus.api` |
| P2-4 | 定义 `EventPublishResult` | `eventbus.api` |
| P2-5 | 定义 `EventContext` | `eventbus.api` |
| P2-6 | 定义 `ConsumeResult` | `eventbus.api` |
| P2-7 | 定义 `@EventListener` | `eventbus.annotation` |

### 5.4 配置任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P2-8 | `EventBusProperties` | `vtc.asset-security.eventbus` 前缀 |
| P2-9 | `EventBusAutoConfiguration` | 自动注册 EventBus / Codec / Transport |
| P2-10 | `spring.factories` | 注册自动配置类 |
| P2-11 | `EventListenerRegistrar` | 扫描 `@EventListener` |

配置示例：

```yaml
vtc:
  asset-security:
    eventbus:
      enabled: true
      transport: kafka
      default-topic: esmp-domain-event
      kafka:
        bootstrap-servers: ${vtc.kafka.server}
      async:
        core-pool-size: 10
        maximum-pool-size: 30
        queue-capacity: 1000
```

### 5.5 Transport 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P2-12 | `EventTransport` SPI | 统一发布和订阅接口 |
| P2-13 | `LocalEventTransport` | 本地开发、单测使用 |
| P2-14 | `KafkaEventTransport` | 首期跨服务通信主实现 |
| P2-15 | `EventCodec` / `JacksonEventCodec` | JSON 序列化 |
| P2-16 | `DeadLetterPublisher` | 失败事件投递到 DLQ topic |

### 5.6 验收

- 使用 local transport 能在单 JVM 中发布和消费事件；
- 使用 kafka transport 能跨服务发送和消费 JSON 事件；
- 业务代码无需直接依赖 Kafka Producer / Consumer；
- envelope 中包含 `eventId/eventType/eventVersion/sourceService/traceId/idempotentKey/occurredAt/payload`；
- 消费异常可进入基础 DLQ；
- starter 可通过配置关闭。

---

## 6. Phase 3：platform-admin 建项与 eventcenter 基础域

### 6.1 目标

创建 `platform-admin`，承接原 `partner-admin` 规划并引入 `eventcenter` 基础域。

### 6.2 工程任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P3-1 | 新建 `project_backend/svmp/platform-admin` | 如已确定使用 platform-admin |
| P3-2 | 对齐 esmp-support / DDD 四层结构 | 参考 open-api-service / vul-pass |
| P3-3 | 配置 Nacos / Redis / MySQL | 可过渡共享 `open_api` 库 |
| P3-4 | 引入 `asset-security-starter-eventbus` | platform-admin 既消费事件也上报事件轨迹 |
| P3-5 | 建立 `eventcenter` 包结构 | ui/app/domain/infra |
| P3-6 | 建立 `invocation`、`webhook` 基础包 | 为后续接入准备 |

### 6.3 eventcenter 基础表

首期只建基础表：

```text
event_trace
event_consume_trace
event_dead_letter
```

可暂缓：

```text
event_catalog
event_schema
event_subscription
event_replay_record
event_audit_log
```

### 6.4 基础接口

| 接口 | 说明 |
|---|---|
| `GET /internal/admin/events/traces` | 查询事件发布轨迹 |
| `GET /internal/admin/events/consume-traces` | 查询消费轨迹 |
| `GET /internal/admin/events/dead-letters` | 查询 DLQ 索引 |
| `GET /internal/admin/events/{eventId}` | 查询事件详情 |

### 6.5 验收

- `platform-admin` 可启动；
- 能消费 EventBus 事件；
- 能写入基础事件轨迹；
- 能通过内部接口查询事件轨迹；
- 不影响 open-api-service mock 能力。

---

## 7. Phase 4：调用记录事件链路接入

### 7.1 目标

将调用记录从 `partner-gateway` 以事件方式异步同步到 `platform-admin.invocation`。

### 7.2 事件定义

```text
eventType = open-platform.invocation.recorded
topic = open-platform-invocation
domain = open-platform
tenantType = partner
tenantId = partnerId
subjectType = invocation
subjectId = invocationId
sourceService = partner-gateway
```

事件类：

```text
InvocationRecordedEvent
```

字段建议：

```text
invocationId
requestId
partnerId
clientId
apiCode
method
path
routeMode
targetService
startTime
endTime
costMillis
statusCode
errorCode
errorMessage
traceId
```

### 7.3 partner-gateway 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P4-1 | 引入 `asset-security-starter-eventbus` | runtime starter |
| P4-2 | 在请求完成处组装 `InvocationRecordedEvent` | start/finish 合并为一条完成事件 |
| P4-3 | 使用 `publishAsync` 发布 | 不阻塞请求 |
| P4-4 | 发布失败降级日志与 metrics | 不影响主链路 |
| P4-5 | 配置 topic 和 Kafka 参数 | `open-platform-invocation` |

### 7.4 platform-admin 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P4-6 | 新增 `InvocationRecordedEventHandler` | `@EventListener` |
| P4-7 | 写入 `api_invocation` | 或迁移后的 invocation 表 |
| P4-8 | 增加唯一约束 | `invocation_id` 防重复 |
| P4-9 | 写 `event_consume_trace` | 成功 / 失败 |
| P4-10 | 查询接口兼容原调用记录页面 | 前端低改动 |

### 7.5 验收

- Partner API 请求不因事件发送失败而失败；
- `platform-admin` 能消费调用记录事件并落库；
- 重复事件不会产生重复调用记录；
- 调用记录查询页面能查到新事件链路数据；
- Kafka 故障时有错误日志和 DLQ / 降级记录。

---

## 8. Phase 5：Webhook 业务事件链路接入

### 8.1 目标

让 `vul-pass` / `open-api-service` 只产生业务事件，`platform-admin.webhook` 负责 Webhook 投递。

### 8.2 事件定义

```text
eventType = open-platform.webhook.event
topic = open-platform-webhook
domain = open-platform 或 vul-pass
tenantType = partner
tenantId = partnerId
subjectType = instance / export / task
subjectId = 业务资源 ID
sourceService = vul-pass 或 open-api-service
```

事件类：

```text
OpenPlatformWebhookEvent
```

字段建议：

```text
eventId
partnerId
eventName
resourceType
resourceId
occurredAt
payload
routeMode
traceId
```

### 8.3 生产者任务

| 编号 | 服务 | 任务 |
|---|---|---|
| P5-1 | open-api-service | mock 业务完成后发布 `OpenPlatformWebhookEvent` |
| P5-2 | vul-pass | 真实业务完成后发布 `OpenPlatformWebhookEvent` |
| P5-3 | open-api-service / vul-pass | 使用 `publishAfterCommit` |
| P5-4 | open-api-service / vul-pass | 后续关键事件切换 `publishReliable` |

### 8.4 platform-admin 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P5-5 | 新增 Webhook 事件消费者 | `OpenPlatformWebhookEventHandler` |
| P5-6 | 根据 partnerId / eventName 查询 webhook 配置 | `partner_webhook_config` |
| P5-7 | 创建 `webhook_delivery_log` | 幂等约束 |
| P5-8 | 执行 HMAC-SHA256 签名 | dispatcher / worker |
| P5-9 | HTTP 投递 Partner webhookUrl | 出站请求 |
| P5-10 | 失败退避重试 | Webhook 自己管理，不依赖 MQ 无限重试 |
| P5-11 | 查询投递记录 | 管理页面使用 |

### 8.5 验收

- open-api-service / vul-pass 不直接执行 Webhook HTTP 投递；
- platform-admin 消费业务事件并生成 delivery；
- 重复事件不会重复创建同一 delivery；
- 投递失败可按退避策略重试；
- delivery log 可查询；
- 原 route-mode=mock 回滚链路仍可用。

---

## 9. Phase 6：Event Center 管理面与 eventbus-admin

### 9.1 目标

引入 `asset-security-starter-eventbus-admin`，完善 `platform-admin.eventcenter` 控制面。

### 9.2 Starter Admin 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P6-1 | 事件目录模型 | event_catalog |
| P6-2 | Schema 模型 | event_schema |
| P6-3 | 订阅关系模型 | event_subscription |
| P6-4 | 事件轨迹服务 | event_trace |
| P6-5 | 消费轨迹服务 | event_consume_trace |
| P6-6 | DLQ 服务 | event_dead_letter |
| P6-7 | 重放服务骨架 | event_replay_record |
| P6-8 | 审计服务 | event_audit_log |

### 9.3 platform-admin 接口任务

| 接口 | 说明 |
|---|---|
| `GET /internal/admin/event-center/catalogs` | 事件目录 |
| `GET /internal/admin/event-center/schemas` | Schema 列表 |
| `GET /internal/admin/event-center/subscriptions` | 订阅关系 |
| `GET /internal/admin/event-center/traces` | 发布轨迹 |
| `GET /internal/admin/event-center/consume-traces` | 消费轨迹 |
| `GET /internal/admin/event-center/dead-letters` | DLQ |
| `POST /internal/admin/event-center/replay` | 重放申请 / 执行 |

### 9.4 元数据上报

业务服务启动后上报：

```text
生产者声明
消费者声明
事件类型
topic
consumer group
handler class / method
服务版本
```

上报方式可选：

1. 启动时 HTTP 上报到 `platform-admin`；
2. 暴露 `/internal/eventbus/metadata`，由 `platform-admin` 拉取；
3. 通过事件上报 metadata。

首期建议使用 HTTP 上报，简单直接。

### 9.5 验收

- 能看到事件目录；
- 能看到生产者、消费者、订阅关系；
- 能按 eventId 查询发布和消费轨迹；
- 能查询 DLQ；
- 重放操作有审计记录。

---

## 10. Phase 7：Outbox / Inbox / DLQ / 重放增强

### 10.1 目标

增强可靠事件能力，支撑关键业务事件最终一致。

### 10.2 Outbox 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P7-1 | `event_outbox` 表 | 生产者本地表 |
| P7-2 | `publishReliable` | 写 outbox |
| P7-3 | `EventOutboxDispatcher` | 定时扫描发布 |
| P7-4 | 失败退避策略 | next_retry_time |
| P7-5 | DEAD 状态 | 超过最大重试 |
| P7-6 | platform-admin 查询 outbox 状态 | 可选上报 |

### 10.3 Inbox 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P7-7 | `event_inbox` 表 | 消费者本地表 |
| P7-8 | 幂等检查器 | eventId / idempotentKey |
| P7-9 | 消费事务封装 | 业务处理和 inbox 同事务 |
| P7-10 | 重复消费快速成功 | 避免 MQ 反复投递 |

### 10.4 DLQ 增强

| 编号 | 任务 | 说明 |
|---|---|---|
| P7-11 | 统一 DLQ topic 命名 | `{topic}.DLQ` |
| P7-12 | DLQ payload 包含失败原因 | exception / stack digest |
| P7-13 | DLQ 索引写 platform-admin | 便于查询 |
| P7-14 | DLQ 手动重放 | 需权限和审计 |

### 10.5 重放规则

重放必须满足：

```text
事件 replayable = true
消费者幂等已确认
操作人具备 event:dlq:replay 权限
填写重放原因
记录 event_replay_record
```

### 10.6 验收

- 业务成功但 MQ 短暂故障时，Outbox 能最终发布；
- 重复消费不会重复写业务数据；
- DLQ 可查询；
- 可对允许重放的事件执行重放；
- 重放有审计记录。

---

## 11. Phase 8：Task Center 融合落地

### 11.1 目标

将任务集中调度治理纳入 `platform-admin.taskcenter`。

### 11.2 第一阶段策略

不立即替换现有 `esmp-starter-task`，先做管理增强：

```text
esmp-starter-task
  继续负责任务 runtime

platform-admin.taskcenter
  负责任务定义、实例、调度、监控、补偿

asset-security-starter-task-admin
  提供 taskcenter 通用管理能力
```

### 11.3 任务

| 编号 | 任务 | 说明 |
|---|---|---|
| P8-1 | 分析 `esmp-starter-task` 现有模型 | TaskRoot / 实例 / 调度器适配 |
| P8-2 | 定义 Task Center 管理模型 | task_definition / task_instance / task_log |
| P8-3 | 定义任务状态机 | NEW / RUNNING / SUCCESS / FAILED / CANCELED |
| P8-4 | 接入事件总线 | 任务状态变更发布事件 |
| P8-5 | 增加任务查询接口 | 管理页面使用 |
| P8-6 | 增加失败重试 / 人工补偿 | 敏感操作审计 |

### 11.4 验收

- platform-admin 能看到任务定义和任务实例；
- 任务失败可查询原因；
- 支持人工重试或补偿；
- 任务状态变更可发布事件；
- 与 Event Center 的 traceId / audit 能串联。

---

## 12. 开发任务拆分建议

### 12.1 Agent A：Starter Parent 与 EventBus API

范围：

```text
asset-security-platform-starters parent
asset-security-starter-eventbus api / config / codec
```

输出：

```text
DomainEvent
EventEnvelope
EventBus
EventBusProperties
EventBusAutoConfiguration
spring.factories
```

### 12.2 Agent B：Transport 与消费注册

范围：

```text
LocalEventTransport
KafkaEventTransport
@EventListener registrar
DLQ publisher
```

输出：

```text
local 发布消费可用
kafka 发布消费可用
消费异常可进入 DLQ
```

### 12.3 Agent C：platform-admin 基础工程

范围：

```text
platform-admin 建项
eventcenter / invocation / webhook 包结构
基础配置
```

输出：

```text
platform-admin 可启动
引入 eventbus starter
基础内部接口可访问
```

### 12.4 Agent D：调用记录链路

范围：

```text
partner-gateway 发布 InvocationRecordedEvent
platform-admin 消费并写 api_invocation
```

输出：

```text
调用记录事件链路跑通
查询接口兼容
```

### 12.5 Agent E：Webhook 事件链路

范围：

```text
open-api-service / vul-pass 发布 OpenPlatformWebhookEvent
platform-admin webhook 消费并生成 delivery
```

输出：

```text
业务事件驱动 Webhook 投递
delivery log 幂等
```

### 12.6 Agent F：Event Center 管理面

范围：

```text
asset-security-starter-eventbus-admin
platform-admin.eventcenter API
DLQ / trace / replay / audit
```

输出：

```text
事件目录、轨迹、DLQ、重放管理可用
```

---

## 13. 验收总清单

### 13.1 工程验收

- `asset-security-platform-starters` 独立于 `esmp-starters`；
- `asset-security-starter-eventbus` 可被业务微服务引用；
- `asset-security-starter-eventbus-admin` 可被 `platform-admin` 引用；
- `platform-admin` 按统一控制面定位建项；
- 包名、artifactId、配置前缀符合资产安全平台命名。

### 13.2 事件链路验收

- `partner-gateway` 能发布调用记录事件；
- `platform-admin` 能消费调用记录事件并落库；
- `vul-pass` / `open-api-service` 能发布 Webhook 业务事件；
- `platform-admin.webhook` 能消费事件并生成 delivery；
- 重复事件不会重复写入业务数据；
- 事件失败可进入 DLQ 或错误轨迹。

### 13.3 管理面验收

- 可查看事件目录；
- 可查看生产者 / 消费者 / 订阅关系；
- 可按 eventId 查询发布和消费轨迹；
- 可查看 DLQ；
- 可执行受控重放；
- 敏感操作有审计。

### 13.4 非功能验收

- 调用记录发布不阻塞 Partner API 主链路；
- Kafka 短时故障不导致业务接口失败；
- 事件 payload 不记录敏感明文，或按策略脱敏；
- DLQ / replay 权限独立；
- Event Center 表增长有归档策略；
- platform-admin 不直接侵入各业务服务数据库。

---

## 14. 风险与回滚

| 风险 | 缓解 | 回滚 |
|---|---|---|
| `platform-admin` 范围过大 | 按领域包隔离，接口边界清晰 | 后续拆出 event-center / task-center |
| EventBus starter 初期复杂度高 | MVP 只做 local + kafka + envelope | 先退化为 Kafka 封装 |
| 调用记录事件丢失 | gateway 记录错误日志和 metrics | 临时回 open-api-service / platform-admin 直接写 DB |
| Webhook 重复投递 | idempotentKey + delivery 唯一约束 | 暂停新 dispatcher，回旧投递逻辑 |
| Outbox 表膨胀 | 分批清理、归档、状态索引 | 关闭 reliable 发布，保留 async 发布 |
| DLQ 重放误操作 | 权限 + 审批 + 审计 + 幂等检查 | 禁用重放入口，仅人工脚本处理 |
| 服务命名从 partner-admin 改 platform-admin 影响前端 | 网关/nginx 路径兼容 | 保留旧路径代理 |

---

## 15. 建议执行顺序

如果后续进入开发，建议严格按以下顺序：

```text
1. 确认命名：platform-admin / groupId / starter 目录
2. 建 asset-security-platform-starters parent
3. 做 asset-security-starter-eventbus MVP
4. 建 platform-admin 基础工程
5. 接调用记录事件链路
6. 接 Webhook 业务事件链路
7. 做 eventbus-admin 与 Event Center 查询治理
8. 做 Outbox / Inbox / DLQ / 重放增强
9. 规划并落地 Task Center
```

不要一开始同时做 EventBus、Event Center UI、Outbox、Task Center，避免范围失控。

---

## 16. 下一步建议

本实施规划确认后，建议继续输出两份开发级文档：

1. `asset-security-starter-eventbus-MVP开发设计.md`
   - 类图；
   - 包结构；
   - API 签名；
   - 自动配置；
   - Kafka transport；
   - 本地测试方案。

2. `platform-admin建项与首批EventCenter落地方案.md`
   - 工程坐标；
   - 端口；
   - DDD 包结构；
   - eventcenter 表结构；
   - invocation / webhook 首批接入；
   - 内部管理接口。
