# platform-admin 建项与首批 EventCenter 落地方案

> 版本：v1.0  日期：2026-06-24  
> 上游文档：
> - `01-架构与总览/资产安全平台控制面与EventBus-Starter架构设计.md`
> - `03-落地方案/资产安全平台控制面与EventBus-Starter实施规划.md`
> - `03-落地方案/asset-security-starter-eventbus-MVP开发设计.md`  
> 目标：定义 `platform-admin` 建项规格、领域包结构、首批 EventCenter 表结构、内部接口、调用记录与 Webhook 事件接入方案。

---

## 0. 结论

建议直接新建：

```text
project_backend/svmp/platform-admin
```

作为资产安全产品部网络安全管理平台统一控制面。

首批实现范围：

```text
platform-admin
  ├── eventcenter    事件轨迹、消费轨迹、DLQ 基础查询
  ├── invocation     消费 InvocationRecordedEvent，写调用记录
  ├── webhook        消费 OpenPlatformWebhookEvent，生成 delivery log 并执行投递
  └── partner        复用/迁移原 Partner 管理域的基础能力
```

首批不做：

```text
完整事件目录审批
Schema 兼容治理
复杂灰度策略
Outbox 可靠发布管理
Task Center 完整调度
独立 Event Center 微服务
```

---

## 1. 工程建项规格

### 1.1 工程坐标

| 项 | 值 |
|---|---|
| 目录 | `project_backend/svmp/platform-admin` |
| groupId | `com.mvtech` 或继承 svmp 父工程配置 |
| artifactId | `platform-admin` |
| version | `1.0.0` |
| 父工程 | 对齐 `open-api-service` / `vul-pass` 使用的 esmp-support 体系 |
| Java | 1.8 |
| 根包 | `com.vtc.platformadmin` |
| 启动类 | `com.vtc.platformadmin.ApplicationStart` |

### 1.2 服务名与端口

已知：

```text
partner-gateway :35770
open-api-service :35780
```

建议：

| 项 | 值 |
|---|---|
| `spring.application.name` | `platform-admin` |
| `server.port` | `35781` |

说明：如果已有文档或环境使用 `partner-admin:35781`，可先保持端口不变，仅将服务名升级为 `platform-admin`。

### 1.3 Nacos / Redis / MySQL

首期建议对齐原 `partner-admin` 规划：

| 项 | 建议 |
|---|---|
| Nacos namespace | `ESMP` |
| Nacos group | `DEV` |
| Redis | 与 open-api-service 共用 token context 库，过渡期不变 |
| MySQL | 过渡期共享 `open_api` 库，新增 `event_*` 表 |

说明：

1. Phase 1 不迁库，降低风险；
2. `event_*` 表先放在同库；
3. 后续如事件轨迹量大，可单独拆 `event_center` 库。

---

## 2. 启动类与依赖

### 2.1 启动类注解

```java
@EnableAsync
@EnableScheduling
@EnableLiquibase
@EnableFeignClients({"com.vtc.platformadmin"})
@SpringCloudApplication
@MapperScan("com.vtc.platformadmin.infra.dao")
@EnableConfigurationProperties(PlatformAdminProperties.class)
public class ApplicationStart {

    public static void main(String[] args) {
        SpringApplication.run(ApplicationStart.class, args);
    }
}
```

### 2.2 首批依赖

```xml
<dependency>
    <groupId>com.vtc.asset.security</groupId>
    <artifactId>asset-security-starter-eventbus</artifactId>
    <version>3.0.2-SNAPSHOT</version>
</dependency>
```

后续 EventCenter 管理增强：

```xml
<dependency>
    <groupId>com.vtc.asset.security</groupId>
    <artifactId>asset-security-starter-eventbus-admin</artifactId>
    <version>3.0.2-SNAPSHOT</version>
</dependency>
```

如 groupId 最终使用 `com.vtc`，依赖同步调整。

---

## 3. DDD 包结构

```text
com.vtc.platformadmin
├── ui
│   ├── eventcenter
│   ├── invocation
│   ├── webhook
│   ├── partner
│   ├── operationcase
│   └── audit
├── app
│   ├── service
│   │   ├── eventcenter
│   │   ├── invocation
│   │   ├── webhook
│   │   └── partner
│   └── convert
├── domain
│   ├── eventcenter
│   │   ├── model
│   │   ├── repository
│   │   └── service
│   ├── invocation
│   ├── webhook
│   └── partner
└── infra
    ├── dao
    │   ├── eventcenter
    │   ├── invocation
    │   └── webhook
    ├── repository
    │   ├── eventcenter
    │   ├── invocation
    │   └── webhook
    ├── config
    ├── eventbus
    └── client
```

调用链遵循：

```text
*Ui → *AppServiceImpl → *DomainServiceImpl → *RepositoryImpl → Mapper/PO
```

---

## 4. 配置规划

### 4.1 application 配置

```yaml
spring:
  application:
    name: platform-admin

server:
  port: 35781

vtc:
  asset-security:
    eventbus:
      enabled: true
      transport: kafka
      app-name: ${spring.application.name}
      domain: open-platform
      kafka:
        bootstrap-servers: ${PLATFORM_KAFKA_SERVERS:172.16.3.33:9092}
      dlq:
        enabled: true
        topic-suffix: .DLQ
      telemetry:
        enabled: false
```

说明：

- `platform-admin` 自己是消费者，也可以作为 telemetry 接收端；
- 首期 telemetry 可先关闭，避免自调用复杂度；
- EventCenter 基础轨迹可由消费者 handler 直接写入。

### 4.2 topic 规划

```text
open-platform-invocation
open-platform-webhook
open-platform-invocation.DLQ
open-platform-webhook.DLQ
```

### 4.3 consumer group

```text
platform-admin-invocation
platform-admin-webhook-dispatcher
platform-admin-eventcenter-dlq
```

---

## 5. 首批数据表

### 5.1 event_trace

事件发布轨迹。

```sql
CREATE TABLE event_trace (
    id BIGINT PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    event_version VARCHAR(32),
    topic VARCHAR(128) NOT NULL,
    domain VARCHAR(64),
    source_service VARCHAR(128),
    tenant_type VARCHAR(64),
    tenant_id VARCHAR(128),
    subject_type VARCHAR(64),
    subject_id VARCHAR(128),
    trace_id VARCHAR(128),
    idempotent_key VARCHAR(256),
    occurred_at DATETIME,
    published_at DATETIME,
    payload_digest VARCHAR(128),
    status VARCHAR(32),
    created_time DATETIME,
    updated_time DATETIME,
    UNIQUE KEY uk_event_id (event_id),
    KEY idx_event_type (event_type),
    KEY idx_topic (topic),
    KEY idx_trace_id (trace_id),
    KEY idx_tenant (tenant_type, tenant_id),
    KEY idx_subject (subject_type, subject_id),
    KEY idx_created_time (created_time)
);
```

### 5.2 event_consume_trace

事件消费轨迹。

```sql
CREATE TABLE event_consume_trace (
    id BIGINT PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    topic VARCHAR(128) NOT NULL,
    consumer_service VARCHAR(128) NOT NULL,
    consumer_group VARCHAR(128) NOT NULL,
    handler VARCHAR(256),
    consume_status VARCHAR(32) NOT NULL,
    retry_count INT DEFAULT 0,
    last_error TEXT,
    started_at DATETIME,
    finished_at DATETIME,
    created_time DATETIME,
    updated_time DATETIME,
    KEY idx_event_id (event_id),
    KEY idx_event_type (event_type),
    KEY idx_consumer_group (consumer_group),
    KEY idx_status (consume_status),
    KEY idx_created_time (created_time)
);
```

### 5.3 event_dead_letter

死信事件索引。

```sql
CREATE TABLE event_dead_letter (
    id BIGINT PRIMARY KEY,
    event_id VARCHAR(64),
    event_type VARCHAR(128),
    origin_topic VARCHAR(128) NOT NULL,
    dlq_topic VARCHAR(128),
    consumer_group VARCHAR(128),
    source_service VARCHAR(128),
    failed_service VARCHAR(128),
    failed_handler VARCHAR(256),
    failed_reason TEXT,
    payload TEXT,
    headers TEXT,
    retry_count INT DEFAULT 0,
    dead_time DATETIME,
    replay_status VARCHAR(32),
    created_time DATETIME,
    updated_time DATETIME,
    KEY idx_event_id (event_id),
    KEY idx_event_type (event_type),
    KEY idx_origin_topic (origin_topic),
    KEY idx_consumer_group (consumer_group),
    KEY idx_dead_time (dead_time)
);
```

### 5.4 api_invocation

调用记录表可优先复用现有 `api_invocation`。

新增或确认唯一键：

```sql
UNIQUE KEY uk_invocation_id (invocation_id)
```

### 5.5 webhook_delivery_log

Webhook 投递记录可复用现有表。

建议唯一约束：

```sql
UNIQUE KEY uk_event_webhook_config (event_id, webhook_config_id)
```

或：

```sql
UNIQUE KEY uk_idempotent_delivery (idempotent_key, webhook_config_id)
```

---

## 6. EventCenter 领域模型

### 6.1 EventTraceDO

字段对应 `event_trace`。

职责：

```text
记录事件发布信息
支持按 eventId / traceId / tenant / subject 查询
```

### 6.2 EventConsumeTraceDO

字段对应 `event_consume_trace`。

职责：

```text
记录每个消费者处理事件的结果
```

### 6.3 EventDeadLetterDO

字段对应 `event_dead_letter`。

职责：

```text
记录 DLQ 索引和失败原因
```

### 6.4 Repository

```text
IEventTraceRepository
IEventConsumeTraceRepository
IEventDeadLetterRepository
```

### 6.5 DomainService

```text
IEventTraceDomainService
IEventConsumeTraceDomainService
IEventDeadLetterDomainService
```

### 6.6 AppService

```text
IEventCenterAppService
```

提供聚合查询：

```text
事件详情 = event_trace + consume_trace + dead_letter
```

---

## 7. 内部管理接口

### 7.1 EventCenterUi

路径前缀：

```text
/internal/admin/event-center
```

接口：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/traces` | 查询事件发布轨迹 |
| GET | `/consume-traces` | 查询消费轨迹 |
| GET | `/dead-letters` | 查询死信事件 |
| GET | `/events/{eventId}` | 查询事件详情 |
| GET | `/events/{eventId}/timeline` | 查询事件时间线 |

### 7.2 查询参数

事件轨迹查询：

```text
eventType
topic
sourceService
tenantType
tenantId
subjectType
subjectId
traceId
status
startTime
endTime
pageNum
pageSize
```

消费轨迹查询：

```text
eventId
eventType
consumerService
consumerGroup
consumeStatus
startTime
endTime
pageNum
pageSize
```

DLQ 查询：

```text
eventType
originTopic
consumerGroup
failedService
replayStatus
startTime
endTime
pageNum
pageSize
```

---

## 8. Telemetry 接收接口

如果启用 starter telemetry，`platform-admin` 提供以下接口。

路径前缀：

```text
/internal/eventbus/telemetry
```

接口：

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/published` | 接收发布轨迹 |
| POST | `/consumed` | 接收消费轨迹 |
| POST | `/dead-letters` | 接收 DLQ 索引 |
| POST | `/subscriptions` | 接收订阅元数据 |

MVP 可选策略：

1. 首批不启用 telemetry，平台自身消费时直接写轨迹；
2. 调用记录和 Webhook 链路跑通后，再让各服务上报 telemetry；
3. telemetry 接口必须幂等，按 eventId + consumerGroup 去重。

---

## 9. 调用记录事件接入

### 9.1 事件消费者

```java
@Component
public class InvocationRecordedEventHandler {

    @EventListener(
        topic = "open-platform-invocation",
        eventType = "open-platform.invocation.recorded",
        group = "platform-admin-invocation"
    )
    public void handle(InvocationRecordedEvent event, EventContext context) {
        // 1. 写 event_trace / consume_trace
        // 2. 按 invocationId 幂等
        // 3. 写 api_invocation
    }
}
```

### 9.2 处理流程

```text
接收事件
  ↓
解析 envelope
  ↓
写 event_trace（如不存在）
  ↓
按 invocationId 查询 api_invocation
  ↓
不存在则写入 api_invocation
  ↓
写 event_consume_trace SUCCESS
```

异常：

```text
写 event_consume_trace FAILED
抛出异常给 EventBus，由 starter 判断是否重试 / DLQ
```

### 9.3 幂等规则

```text
invocation_id 唯一
```

重复事件：

```text
如果 api_invocation 已存在，直接视为 SUCCESS
```

### 9.4 字段映射

| 事件字段 | api_invocation 字段 |
|---|---|
| invocationId | invocation_id |
| requestId | request_id |
| partnerId | partner_id |
| clientId | client_id |
| apiCode | api_code |
| method | method |
| path | path |
| routeMode | route_mode |
| targetService | target_service |
| startTime | start_time |
| endTime | end_time |
| costMillis | cost_millis |
| statusCode | status_code |
| errorCode | error_code |
| errorMessage | error_message |
| traceId | trace_id |

---

## 10. Webhook 业务事件接入

### 10.1 事件消费者

```java
@Component
public class OpenPlatformWebhookEventHandler {

    @EventListener(
        topic = "open-platform-webhook",
        eventType = "open-platform.webhook.event",
        group = "platform-admin-webhook-dispatcher"
    )
    public void handle(OpenPlatformWebhookEvent event, EventContext context) {
        // 1. 写 event_trace / consume_trace
        // 2. 查询 webhook 配置
        // 3. 生成 delivery log
        // 4. 执行投递或进入待投递状态
    }
}
```

### 10.2 处理流程

```text
接收 OpenPlatformWebhookEvent
  ↓
写 event_trace
  ↓
根据 partnerId + eventName 查询启用的 partner_webhook_config
  ↓
为每个 webhook_config 生成 webhook_delivery_log
  ↓
根据 idempotentKey 去重
  ↓
投递 Worker 读取待投递记录
  ↓
HMAC-SHA256 签名
  ↓
HTTP POST Partner webhookUrl
  ↓
记录响应和状态
```

### 10.3 delivery 状态

```text
PENDING
SENDING
SUCCESS
FAILED
RETRY_WAIT
DEAD
```

### 10.4 幂等规则

推荐：

```text
event_id + webhook_config_id 唯一
```

如果生产者 eventId 每次重试会变化，则使用：

```text
idempotent_key + webhook_config_id 唯一
```

### 10.5 重试策略

Webhook 投递重试由 webhook 模块管理，不依赖 Kafka 无限重试。

建议：

```text
最大重试次数：10
退避：1m, 5m, 15m, 30m, 1h, 2h ...
最终状态：DEAD
```

---

## 11. DLQ 接入

### 11.1 DLQ 消费者

可新增：

```java
@Component
public class EventDeadLetterHandler {

    @EventListener(
        topic = "open-platform-webhook.DLQ",
        eventType = "asset-security.event.dead-letter",
        group = "platform-admin-eventcenter-dlq"
    )
    public void handle(DeadLetterEvent event, EventContext context) {
        // 写 event_dead_letter
    }
}
```

调用记录 DLQ：

```text
open-platform-invocation.DLQ
```

Webhook DLQ：

```text
open-platform-webhook.DLQ
```

### 11.2 DLQ 索引

`event_dead_letter` 只作为索引和排查记录，原始消息可根据存储策略决定：

1. 直接存 payload；
2. 存 payload 摘要；
3. 存外部对象存储引用。

MVP 可先存 payload，但需注意敏感字段脱敏。

---

## 12. 审计与权限

### 12.1 首批权限

```text
event:trace:view
event:dlq:view
event:dlq:replay
```

### 12.2 首批审计

首期审计以下操作：

```text
查看 DLQ 详情
触发重放
修改 Webhook delivery 状态
人工重试 Webhook
HTTP 发布事件（自动记录操作人，通过 CurrentUser.get() 提取）
```

> 事件身份追溯（谁发布、谁重放、归属哪个租户）详见 `事件总线治理面页面实现设计.md` §7。

---

## 13. 前端页面建议

> 详细设计已独立成文：`09-platform-admin迁移与建设/事件总线治理面页面实现设计.md`（v1.1），本节仅保留概要。

`asset-openplatform-manage` 子应用接入，侧边栏新增「事件治理」一级菜单，下挂 6 个页面：

| 路由 | 页面 | 说明 |
|------|------|------|
| `/event-center/traces` | EventTraceList | 事件轨迹列表（含操作人/租户身份列） |
| `/event-center/events/:eventId` | EventDetail | 事件详情（发布轨迹 + 消费轨迹 + 死信 + 时间线） |
| `/event-center/dead-letters` | DeadLetterList | 死信列表 + 重放 |
| `/event-center/publish` | EventPublish | 事件发布调试台（自动捕获操作人身份） |
| `/event-center/catalogs` | EventCatalog | 事件目录（卡片网格） |
| `/event-center/subscriptions` | SubscriptionList | 订阅关系 |

事件详情页展示完整身份追溯链：操作人 → 来源服务 → topic → 消费组 → 重放记录。

---

## 14. 与现有 partner-admin 方案的差异

原 `partner-admin` 方案：

```text
Partner 管理 + 调用记录 + Webhook + 运营案件
```

升级后 `platform-admin`：

```text
Partner 管理 + 调用记录 + Webhook + 运营案件 + EventCenter + TaskCenter 预留
```

需要同步调整的文档/配置：

| 原项 | 新项 |
|---|---|
| `partner-admin` | `platform-admin` |
| `com.vtc.partneradmin` | `com.vtc.platformadmin` |
| `/internal/admin/partners` | 保持不变，可由 platform-admin 提供 |
| `partner-admin webhook-dispatcher` | `platform-admin webhook-dispatcher` |
| `partner-admin consumer` | `platform-admin consumer` |

---

## 15. 开发任务清单

### 15.1 建项任务

| 编号 | 任务 |
|---|---|
| PA-1 | 新建 `project_backend/svmp/platform-admin` |
| PA-2 | 配置 pom、启动类、Nacos、Redis、MySQL |
| PA-3 | 配置 DDD 四层包结构 |
| PA-4 | 引入 `asset-security-starter-eventbus` |
| PA-5 | 新增 Liquibase changelog |

### 15.2 EventCenter 任务

| 编号 | 任务 |
|---|---|
| EC-1 | 新建 `EventTraceDO/PO/Mapper/Repository/Service` |
| EC-2 | 新建 `EventConsumeTraceDO/PO/Mapper/Repository/Service` |
| EC-3 | 新建 `EventDeadLetterDO/PO/Mapper/Repository/Service` |
| EC-4 | 新建 `EventCenterUi` 查询接口 |
| EC-5 | 新建 telemetry 接收接口 |

### 15.3 Invocation 任务

| 编号 | 任务 |
|---|---|
| INV-1 | 定义 `InvocationRecordedEvent` |
| INV-2 | 新建 `InvocationRecordedEventHandler` |
| INV-3 | 写入 `api_invocation` |
| INV-4 | 增加幂等处理 |
| INV-5 | 查询接口兼容原调用记录页面 |

### 15.4 Webhook 任务

| 编号 | 任务 |
|---|---|
| WH-1 | 定义 `OpenPlatformWebhookEvent` |
| WH-2 | 新建 `OpenPlatformWebhookEventHandler` |
| WH-3 | 查询 webhook config |
| WH-4 | 生成 delivery log |
| WH-5 | 实现 HMAC-SHA256 签名 |
| WH-6 | 实现投递 Worker |
| WH-7 | 实现失败退避重试 |

---

## 16. 验收标准

### 16.1 工程验收

- `platform-admin` 可启动；
- 服务注册名为 `platform-admin`；
- 引入 `asset-security-starter-eventbus` 后自动注册消费者；
- `event_trace/event_consume_trace/event_dead_letter` 表创建成功。

### 16.2 调用记录验收

- `partner-gateway` 发布调用记录事件；
- `platform-admin` 消费并写入调用记录；
- 重复 invocationId 不重复写入；
- 管理接口可查询调用记录。

### 16.3 Webhook 验收

- `open-api-service` / `vul-pass` 发布 Webhook 业务事件；
- `platform-admin` 消费并生成 delivery；
- Webhook 投递由 `platform-admin` 执行；
- delivery log 可查询；
- 重复事件不重复 delivery。

### 16.4 EventCenter 验收

- 可查询事件轨迹；
- 可查询消费轨迹；
- 可查询 DLQ；
- 事件详情能串联 publish / consume / dead-letter；
- 敏感字段不明文暴露或有脱敏策略。

---

## 17. 风险与回滚

| 风险 | 缓解 | 回滚 |
|---|---|---|
| 新建 platform-admin 影响既有 partner-admin 文档 | 同步更新文档，保留兼容路径 | 继续使用 partner-admin 服务名，内部按 platform-admin 结构 |
| 调用记录事件消费失败 | DLQ + 日志 + 失败轨迹 | 临时回直接写 DB |
| Webhook 重复投递 | delivery 唯一约束 | 暂停 dispatcher，回旧投递逻辑 |
| event_trace 表增长快 | 加索引、归档、按时间清理 | 临时关闭 telemetry 详细 payload |
| platform-admin 控制面过重 | 领域隔离，后续可拆 | 拆出 event-center / task-center |

---

## 18. 后续增强

```text
event_catalog
事件 Schema 管理
event_subscription 自动登记
DLQ 手动重放
重放审批
Outbox 状态查询
Inbox 幂等查询
Task Center 集中调度
事件与运营案件 timeline 聚合
```
