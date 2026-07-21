# 资产安全平台控制面与 EventBus Starter 架构设计

> 版本：v1.0  日期：2026-06-24  
> 适用范围：资产安全产品部网络安全管理平台、`platform-admin`、开放平台治理域、Event Center、Task Center、独立平台级 Starter 体系  
> 关联文档：
> - `01-架构与总览/open-gateway合并与平台业务解耦改造方案.md`
> - `03-落地方案/partner-admin建项与首批迁移方案.md`
> - `03-落地方案/资产安全平台控制面与EventBus-Starter实施规划.md`
> - `03-落地方案/asset-security-starter-eventbus-MVP开发设计.md`
> - `03-落地方案/platform-admin建项与首批EventCenter落地方案.md`

---

## 0. 结论

本方案将原规划中的 `partner-admin` 升级为更通用的 `platform-admin`：

```text
platform-admin
  资产安全产品部网络安全管理平台的统一控制面服务
```

`platform-admin` 不再只承载 Partner 管理，而是作为平台治理控制面，融合以下管理域：

```text
platform-admin
  ├── partner          Partner / 凭证 / 能力 / 流控配置
  ├── eventcenter      事件中心：事件目录、Schema、订阅、轨迹、DLQ、重放、审计
  ├── taskcenter       任务中心：集中调度、任务实例、失败补偿、调度监控
  ├── webhook          Webhook 配置、投递、重试、投递日志
  ├── invocation       调用记录、流控命中、调用统计
  ├── operationcase    运营案件壳、timeline、workspace 聚合
  └── audit            平台审计、操作留痕
```

同时，EventBus 不放入现有 `project_backend/framework/asset/esmp-starters/`，而是规划为独立平台级 Starter 体系：

```text
project_backend/framework/platform/asset-security-platform-starters/
  ├── asset-security-platform-starters-parent
  ├── asset-security-starter-eventbus
  ├── asset-security-starter-eventbus-admin
  └── asset-security-starter-task-admin     // 后续规划
```

核心架构原则：

```text
业务微服务引用 runtime starter，负责数据面执行；
platform-admin 引用 admin starter，负责控制面治理。
```

---

## 1. 背景

现有开放平台解耦方案已规划四类服务角色：

```text
partner-gateway
  入站网关执行面

partner-admin
  平台治理管理面 + 查询面 + 异步治理 Worker

open-api-service
  纯 mock 业务服务

vul-pass
  真实漏洞业务服务
```

其中 `partner-admin` 原始职责包括：

- Partner 管理；
- 凭证管理；
- 接口目录；
- 流控配置；
- 调用记录查询；
- Webhook 配置与投递记录；
- 运营案件壳；
- 短期 Token 签发；
- 后续 Webhook dispatcher / worker。

随着 EventBus、Event Center、Task Center 等平台能力引入，`partner-admin` 这个名称和边界会逐渐偏窄。为了避免后续服务语义失真，本方案建议将其升级为 `platform-admin`。

---

## 2. 设计目标

### 2.1 平台控制面目标

`platform-admin` 作为资产安全产品部网络安全管理平台的统一控制面，目标是：

1. 少建一个独立 Event Center 微服务，降低早期部署和治理成本；
2. 统一承载 Partner、事件、任务、Webhook、调用治理等控制面能力；
3. 保持领域边界清晰，未来具备按域拆分为独立服务的能力；
4. 为开放平台、vul-pass、后续安全管理域提供统一治理入口；
5. 支撑事件追踪、灰度、版本兼容、幂等、DLQ、审计、重放等能力。

### 2.2 Starter 体系目标

独立 `asset-security-platform-starters` 的目标是：

1. 与既有 `esmp-starters` 解耦，避免平台治理基础设施与通用 ESMP starter 混杂；
2. 形成资产安全产品部自己的平台级能力套件；
3. 支持微服务按需引用；
4. 支持 `platform-admin` 统一治理；
5. 为后续 Task Center、Audit Center、Monitor Center 等能力预留扩展空间。

---

## 3. 总体架构

```text
┌────────────────────────────────────────────────────────────────────┐
│                           platform-admin                            │
│     资产安全产品部网络安全管理平台统一控制面                         │
│                                                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │ partner     │ │ eventcenter │ │ taskcenter  │ │ webhook     │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                  │
│  │ invocation  │ │ operationcase│ │ audit       │                  │
│  └─────────────┘ └─────────────┘ └─────────────┘                  │
│                                                                    │
│  引用：asset-security-starter-eventbus-admin                       │
│       asset-security-starter-task-admin                            │
└───────────────────────────────▲────────────────────────────────────┘
                                │
                  metadata / trace / dlq / replay / command
                                │
┌───────────────────────────────┴────────────────────────────────────┐
│                asset-security-platform-starters                     │
│                                                                    │
│  asset-security-starter-eventbus                                    │
│    - publish / subscribe / envelope / codec                         │
│    - local / kafka / redis-stream transport                         │
│    - outbox / inbox / dlq / trace / telemetry                       │
│                                                                    │
│  asset-security-starter-eventbus-admin                              │
│    - catalog / schema / subscription / trace / dlq / replay / audit │
└───────────────────────────────▲────────────────────────────────────┘
                                │
                      Kafka / Redis Stream / Local
                                │
     ┌──────────────────────────┼──────────────────────────┐
     │                          │                          │
┌────┴────────────┐      ┌──────┴───────┐          ┌───────┴─────────┐
│ partner-gateway │      │ vul-pass     │          │ open-api-service│
│ 发布调用记录事件 │      │ 发布业务事件 │          │ 发布 mock 事件  │
└─────────────────┘      └──────────────┘          └─────────────────┘
```

---

## 4. 服务定位

### 4.1 platform-admin

`platform-admin` 是统一控制面服务，不是单一 Partner CRUD 服务。

职责：

| 管理域 | 职责 |
|---|---|
| partner | Partner、凭证、能力授权、流控配置 |
| eventcenter | 事件目录、Schema、订阅、事件轨迹、消费轨迹、DLQ、重放、审计 |
| taskcenter | 集中调度、任务定义、任务实例、执行轨迹、失败补偿、调度监控 |
| webhook | Webhook 配置、Secret 轮换、投递、重试、delivery log |
| invocation | API 调用记录、限流命中、调用统计 |
| operationcase | 运营案件壳、timeline、workspace 聚合 |
| audit | 管理操作审计、敏感操作留痕 |

设计要求：

1. `eventcenter` 保持通用，不命名、不建模成 Partner 专属；
2. `partner` 是平台管理域之一，不是整个服务边界；
3. 管理域之间通过应用服务协作，避免跨域直接访问 Repository；
4. 表、权限、接口命名预留未来按域拆分能力。

### 4.2 partner-gateway

入站网关执行面。

职责：

- Partner API 唯一入口；
- Token 校验；
- 能力码拦截；
- 限流执行；
- 调用记录采集；
- 请求追踪；
- route-mode 决策，路由到 mock 或 vul-pass；
- 发布 `InvocationRecordedEvent`。

不承担：

- Partner 管理；
- Webhook 投递；
- 事件治理；
- DLQ / 重放管理。

### 4.3 open-api-service

保留 mock 业务服务定位。

职责：

- mock 风险排查；
- mock 修复核验；
- mock 接入测试；
- mock 处置测试；
- mock Export / Webhook / OperationCase 业务事件产生；
- 作为 route-mode=mock 的回滚基线。

### 4.4 vul-pass

真实漏洞业务服务。

职责：

- 真实漏洞实例；
- 真实验证 / 处置 / 修复核验；
- 真实扫描编排；
- 真实业务 payload；
- 发布真实业务事件，例如修复核验完成、导出完成等。

---

## 5. 独立 Starter 组规划

### 5.1 工程目录

建议新增：

```text
project_backend/framework/platform/asset-security-platform-starters/
```

该目录与现有：

```text
project_backend/framework/asset/esmp-starters/
```

保持独立。

### 5.2 Parent 坐标建议

优先建议：

```xml
<groupId>com.vtc.asset.security</groupId>
<artifactId>asset-security-platform-starters-parent</artifactId>
<version>3.0.2-SNAPSHOT</version>
<packaging>pom</packaging>
```

如果内部 Maven 规范要求统一 `com.vtc`，可退化为：

```xml
<groupId>com.vtc</groupId>
<artifactId>asset-security-platform-starters-parent</artifactId>
<version>3.0.2-SNAPSHOT</version>
<packaging>pom</packaging>
```

### 5.3 第一阶段模块

```text
asset-security-platform-starters
  ├── asset-security-starter-eventbus
  └── asset-security-starter-eventbus-admin
```

#### asset-security-starter-eventbus

业务微服务按需引用。

职责：

- `EventBus` 发布 API；
- `@EventListener` 消费 API；
- `EventEnvelope` 标准；
- 事件序列化 / 反序列化；
- local / kafka / redis-stream transport；
- 异步发布；
- 事务提交后发布；
- Outbox 可靠发布；
- Inbox / 幂等消费辅助；
- DLQ 投递；
- traceId / eventId / idempotentKey 注入；
- 元数据、发布轨迹、消费轨迹上报。

#### asset-security-starter-eventbus-admin

`platform-admin` 引用。

职责：

- 事件目录；
- 事件 Schema；
- 生产者登记；
- 消费者登记；
- 订阅关系；
- 事件轨迹查询；
- 消费轨迹查询；
- DLQ 查询；
- 事件重放；
- 事件审计；
- 事件治理权限模型。

### 5.4 第二阶段模块

```text
asset-security-starter-task-admin
```

用于承接任务中心管理能力。

说明：

- 不强制替代现有 `esmp-starter-task`；
- 短期可作为 `esmp-starter-task` 的集中治理增强；
- 长期可根据实际情况演进为新的平台级任务 runtime + admin 双 starter。

职责：

- 任务定义；
- 调度计划；
- 任务实例；
- 执行轨迹；
- 失败重试；
- 人工补偿；
- 调度审计；
- 调度监控。

### 5.5 后续扩展模块

```text
asset-security-starter-audit
asset-security-starter-monitor
asset-security-starter-notification
asset-security-starter-approval
asset-security-starter-workflow
asset-security-starter-risk-rule
```

---

## 6. 包名建议

推荐 Java 包名前缀：

```text
com.vtc.asset.security.platform
```

EventBus runtime：

```text
com.vtc.asset.security.platform.eventbus.api
com.vtc.asset.security.platform.eventbus.annotation
com.vtc.asset.security.platform.eventbus.config
com.vtc.asset.security.platform.eventbus.codec
com.vtc.asset.security.platform.eventbus.transport
com.vtc.asset.security.platform.eventbus.outbox
com.vtc.asset.security.platform.eventbus.inbox
com.vtc.asset.security.platform.eventbus.dlq
com.vtc.asset.security.platform.eventbus.trace
com.vtc.asset.security.platform.eventbus.telemetry
```

EventBus admin：

```text
com.vtc.asset.security.platform.eventbus.admin.catalog
com.vtc.asset.security.platform.eventbus.admin.schema
com.vtc.asset.security.platform.eventbus.admin.subscription
com.vtc.asset.security.platform.eventbus.admin.trace
com.vtc.asset.security.platform.eventbus.admin.dlq
com.vtc.asset.security.platform.eventbus.admin.replay
com.vtc.asset.security.platform.eventbus.admin.audit
```

---

## 7. EventBus Runtime 设计

### 7.1 事件模型

业务事件接口：

```java
public interface DomainEvent {

    String eventType();

    String idempotentKey();

    default String partitionKey() {
        return idempotentKey();
    }
}
```

事件信封：

```java
public class EventEnvelope<T> {

    private String eventId;
    private String eventType;
    private String eventVersion;
    private String topic;

    private String domain;
    private String sourceService;

    private String tenantType;
    private String tenantId;
    private String subjectType;
    private String subjectId;

    private String traceId;
    private String idempotentKey;
    private String partitionKey;

    private Long occurredAt;
    private T payload;
    private Map<String, String> headers;
}
```

其中：

| 字段 | 说明 |
|---|---|
| `eventId` | 全局唯一事件 ID |
| `eventType` | 事件类型，例如 `open-platform.invocation.recorded` |
| `eventVersion` | 事件版本，例如 `1.0` |
| `domain` | 业务域，例如 `open-platform`、`vul-pass` |
| `sourceService` | 生产者服务，例如 `partner-gateway` |
| `tenantType` | 租户类型，例如 `partner`、`internal`、`system` |
| `tenantId` | 租户 ID，例如 `partnerId` |
| `subjectType` | 事件主体类型，例如 `invocation`、`instance` |
| `subjectId` | 事件主体 ID |
| `traceId` | 链路追踪 ID |
| `idempotentKey` | 业务幂等键 |
| `partitionKey` | MQ 分区键 |

### 7.2 发布 API

```java
public interface EventBus {

    EventPublishResult publish(DomainEvent event);

    EventPublishResult publish(String topic, DomainEvent event);

    void publishAsync(DomainEvent event);

    void publishAfterCommit(DomainEvent event);

    void publishReliable(DomainEvent event);
}
```

语义：

| 方法 | 场景 |
|---|---|
| `publish` | 非事务场景立即发布 |
| `publishAsync` | 调用记录等高频低价值异步事件 |
| `publishAfterCommit` | 事务提交后发布，避免业务回滚但事件已发出 |
| `publishReliable` | 写 Outbox，由 dispatcher 保证最终发布 |

### 7.3 消费 API

注解方式：

```java
@Component
public class OpenPlatformWebhookEventHandler {

    @EventListener(
        topic = "open-platform-webhook",
        eventType = "open-platform.webhook.event",
        group = "platform-admin-webhook-dispatcher"
    )
    public void handle(OpenPlatformWebhookEvent event, EventContext context) {
        // 业务处理
    }
}
```

接口方式：

```java
public interface EventHandler<T extends DomainEvent> {

    ConsumeResult handle(T event, EventContext context);
}
```

### 7.4 Transport SPI

```java
public interface EventTransport {

    String type();

    EventPublishResult publish(EventEnvelope<?> envelope);

    void subscribe(EventSubscription subscription, EventMessageConsumer consumer);
}
```

实现：

```text
LocalEventTransport
KafkaEventTransport
RedisStreamEventTransport
```

配置：

```yaml
vtc:
  asset-security:
    eventbus:
      enabled: true
      transport: kafka # local / kafka / redis-stream
```

---

## 8. Event Center 控制面设计

### 8.1 管理能力

`platform-admin.eventcenter` 提供以下能力：

```text
事件目录
事件 Schema
生产者登记
消费者登记
订阅关系
事件轨迹
消费轨迹
DLQ
重放
审计
灰度策略
告警配置
```

### 8.2 数据表规划

#### event_catalog

事件目录。

```text
event_type
event_name
domain
description
owner_service
owner_team
current_version
topic
replayable
status
created_time
updated_time
```

#### event_schema

事件 Schema。

```text
event_type
version
schema_json
sample_payload
compatibility_mode
status
created_time
updated_time
```

#### event_producer

生产者登记。

```text
event_type
source_service
source_module
topic
enabled
last_report_time
```

#### event_subscription

订阅关系。

```text
event_type
topic
consumer_service
consumer_group
handler_class
handler_method
enabled
gray_rule
last_report_time
```

#### event_trace

事件发布轨迹。

```text
event_id
event_type
event_version
topic
domain
source_service
tenant_type
tenant_id
subject_type
subject_id
trace_id
idempotent_key
occurred_at
published_at
payload_digest
status
```

#### event_consume_trace

事件消费轨迹。

```text
event_id
event_type
consumer_service
consumer_group
handler
consume_status
retry_count
last_error
started_at
finished_at
```

#### event_dead_letter

死信事件。

```text
event_id
event_type
topic
consumer_group
source_service
failed_reason
payload
headers
retry_count
dead_time
replay_status
```

#### event_replay_record

重放记录。

```text
replay_id
event_id
operator
reason
target_topic
target_consumer_group
status
created_time
finished_time
```

#### event_audit_log

事件中心操作审计。

```text
audit_id
operator
operation
resource_type
resource_id
before_value
after_value
operate_time
client_ip
```

---

## 9. Outbox / Inbox 可靠性设计

### 9.1 Outbox

关键业务事件应使用 Outbox，保证业务事务和事件生成一致。

生产者本地事务：

```text
写业务表
写 event_outbox
事务提交
```

后台 dispatcher：

```text
扫描 NEW / FAILED
发布到 Kafka / Redis Stream
成功标记 PUBLISHED
失败重试
超过阈值进入 DEAD
```

表：

```text
event_outbox
  id
  event_id
  event_type
  topic
  partition_key
  idempotent_key
  source_service
  payload
  headers
  status
  retry_count
  next_retry_time
  last_error
  created_time
  updated_time
```

### 9.2 Inbox / 幂等

消费者必须幂等。

通用表：

```text
event_inbox
  id
  event_id
  event_type
  consumer_group
  idempotent_key
  status
  consumed_time
  created_time
```

对于 Webhook 场景，可结合 `webhook_delivery_log` 唯一约束：

```text
event_id + webhook_config_id
```

或：

```text
idempotent_key + consumer_group
```

---

## 10. open-gateway 解耦场景落地

### 10.1 调用记录事件

链路：

```text
partner-gateway
  ↓ InvocationRecordedEvent
platform-admin.eventcenter / invocation
  ↓
api_invocation
```

事件：

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

建议：

- 使用 `publishAsync`；
- 不走 Outbox；
- 不阻塞 Partner API 主链路；
- `api_invocation.invocation_id` 做唯一约束。

### 10.2 Webhook 业务事件

链路：

```text
vul-pass / open-api-service
  ↓ OpenPlatformWebhookEvent
platform-admin.eventcenter
  ↓
platform-admin.webhook
  ↓
webhook_delivery_log
  ↓
HTTP 投递 Partner webhookUrl
```

事件：

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

建议：

- 重要业务事件使用 `publishAfterCommit` 或 `publishReliable`；
- Webhook 投递重试由 `platform-admin.webhook` 管理；
- EventBus 只负责把业务事件可靠交给控制面；
- `webhook_delivery_log` 做业务幂等。

### 10.3 运营案件 timeline

事件轨迹可以进入运营案件 timeline：

```text
Partner API 调用
  → InvocationRecordedEvent
  → 业务处理
  → OpenPlatformWebhookEvent
  → WebhookDelivery
  → OperationCase timeline
```

---

## 11. Task Center 融合规划

`platform-admin.taskcenter` 后续承接集中调度和任务治理。

初期定位：

```text
复用或兼容现有 esmp-starter-task；
在 platform-admin 中增加集中调度、查询、补偿、监控能力。
```

后续新增：

```text
asset-security-starter-task-admin
```

负责：

- 任务定义管理；
- 调度策略；
- 任务实例；
- 执行轨迹；
- 失败重试；
- 人工补偿；
- 调度审计；
- 调度监控。

Task Center 与 Event Center 可复用：

```text
traceId
operator
审计日志
状态机
重试策略
告警策略
tenant / partner context
```

---

## 12. 权限模型

Event Center 权限独立于 Partner 管理权限。

建议权限码：

```text
event:catalog:view
event:catalog:manage
event:schema:view
event:schema:manage
event:subscription:view
event:subscription:manage
event:trace:view
event:dlq:view
event:dlq:replay
event:replay:approve
event:audit:view
```

Task Center 权限：

```text
task:definition:view
task:definition:manage
task:instance:view
task:instance:retry
task:instance:cancel
task:schedule:manage
task:audit:view
```

重放、补偿、重试属于敏感操作，必须审计。

---

## 13. 演进路线

### Phase 1：架构落位与 EventBus MVP

目标：

- 新建独立 starter parent；
- 新建 `asset-security-starter-eventbus`；
- 支持 EventEnvelope、发布 API、消费 API；
- 支持 local / kafka transport；
- 支持基础 trace、idempotentKey、DLQ；
- 支撑调用记录和 Webhook 业务事件。

交付：

```text
asset-security-starter-eventbus
platform-admin.eventcenter 基础接入
partner-gateway 发布 InvocationRecordedEvent
vul-pass / open-api-service 发布 OpenPlatformWebhookEvent
```

### Phase 2：Event Center 管理面

目标：

- 新建 `asset-security-starter-eventbus-admin`；
- `platform-admin.eventcenter` 提供事件目录、订阅关系、轨迹、DLQ 查询；
- 支持事件元数据上报；
- 支持基础重放。

### Phase 3：可靠事件与治理增强

目标：

- Outbox；
- Inbox；
- 重放审计；
- Schema 管理；
- 消费灰度；
- 指标与告警。

### Phase 4：Task Center 融合

目标：

- 引入 `asset-security-starter-task-admin`；
- 平台化管理 `esmp-starter-task` 或新任务 runtime；
- 支持集中调度、任务实例、失败补偿、调度审计。

### Phase 5：服务拆分评估

当满足以下条件时，评估是否从 `platform-admin` 拆出独立服务：

- 非开放平台业务大量接入事件中心；
- event_trace / consume_trace 写入量显著影响管理面；
- Event Center 与 Partner 管理部署节奏明显不同；
- 权限和运维边界需要独立；
- 数据库存储周期和容量差异过大。

---

## 14. 命名迁移建议

现有文档中的 `partner-admin` 可按阶段迁移为 `platform-admin`。

短期为了兼容既有方案，可采用：

```text
服务名：partner-admin 或 platform-admin 二选一
架构定位：platform-admin
内部模块：partner / eventcenter / taskcenter / webhook / invocation
```

如果当前尚未建项，建议直接使用：

```text
project_backend/svmp/platform-admin
spring.application.name = platform-admin
根包 = com.vtc.platformadmin
```

如果已按 `partner-admin` 建项，则建议：

```text
保留服务名 partner-admin 过渡；
代码内部先按 platform-admin 的领域边界建设；
后续再通过服务名和路由迁移切换。
```

---

## 15. 最终边界

### 15.1 esmp-starters

继续作为既有 ESMP / asset 框架 starter 集合。

```text
project_backend/framework/asset/esmp-starters/
```

不新增 EventBus / EventBus Admin。

### 15.2 asset-security-platform-starters

作为资产安全产品部网络安全管理平台的独立平台级 starter 集合。

```text
project_backend/framework/platform/asset-security-platform-starters/
```

承载：

```text
EventBus
EventBus Admin
Task Admin
Audit
Monitor
Notification
Workflow
```

### 15.3 platform-admin

作为统一控制面服务。

承载：

```text
Partner 管理
Event Center
Task Center
Webhook Center
Invocation Center
Operation Case
Audit Center
```

---

## 16. 关键决策摘要

| 决策 | 结论 |
|---|---|
| 是否新增独立 Event Center 微服务 | 暂不新增，放入 `platform-admin` |
| `partner-admin` 是否继续作为服务定位 | 升级为 `platform-admin` 更合适 |
| Partner 在新架构中的定位 | `platform-admin` 的一个管理域，不是服务边界 |
| EventBus 是否放入 `esmp-starters` | 不放入，独立 starter 组 |
| 新 starter 组路径 | `project_backend/framework/platform/asset-security-platform-starters/` |
| EventBus runtime starter | `asset-security-starter-eventbus` |
| EventBus admin starter | `asset-security-starter-eventbus-admin` |
| Task Center 是否可融合 | 可以，作为 `platform-admin.taskcenter` |
| 未来是否可拆分 | 可以，按 eventcenter / taskcenter 等领域拆分 |
