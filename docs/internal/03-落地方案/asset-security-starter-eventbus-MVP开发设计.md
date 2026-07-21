# asset-security-starter-eventbus MVP 开发设计

> 版本：v1.0  日期：2026-06-24  
> 上游文档：
> - `01-架构与总览/资产安全平台控制面与EventBus-Starter架构设计.md`
> - `03-落地方案/资产安全平台控制面与EventBus-Starter实施规划.md`  
> 目标：定义 `asset-security-starter-eventbus` MVP 的包结构、核心 API、自动配置、Transport、消费注册、DLQ、配置项与测试方案。

---

## 0. MVP 结论

`asset-security-starter-eventbus` 首期只做运行时最小闭环：

```text
能发布
能消费
有统一 EventEnvelope
支持 local / kafka transport
支持基础 trace / eventId / idempotentKey
消费失败可进入 DLQ
可向 platform-admin 上报基础轨迹
```

首期不做：

```text
Outbox
Inbox
Schema 兼容校验
灰度策略
人工重放
完整 Event Center UI
```

---

## 1. 工程位置

```text
project_backend/framework/platform/asset-security-platform-starters/
└── asset-security-starter-eventbus/
    ├── pom.xml
    └── src/main/
        ├── java/com/vtc/asset/security/platform/eventbus/
        └── resources/META-INF/spring.factories
```

建议包名：

```text
com.vtc.asset.security.platform.eventbus
```

---

## 2. Maven 依赖建议

### 2.1 pom.xml

```xml
<project>
    <parent>
        <groupId>com.vtc.asset.security</groupId>
        <artifactId>asset-security-platform-starters-parent</artifactId>
        <version>3.0.2-SNAPSHOT</version>
    </parent>

    <artifactId>asset-security-starter-eventbus</artifactId>
    <packaging>jar</packaging>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-autoconfigure</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-configuration-processor</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
        <dependency>
            <groupId>org.apache.kafka</groupId>
            <artifactId>kafka-clients</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>
</project>
```

### 2.2 依赖原则

1. `kafka-clients` 首期可 optional，避免 local 模式强依赖 Kafka；
2. 不强依赖 `esmp-starter-piece` 的 Kafka Producer，避免 API 被旧 Kafka 封装限制；
3. 不依赖业务服务包；
4. 不依赖 `platform-admin`；
5. 后续 Redis Stream 单独 optional 引入 Redis 依赖。

---

## 3. 包结构

```text
com.vtc.asset.security.platform.eventbus
├── annotation
│   └── EventListener.java
├── api
│   ├── ConsumeResult.java
│   ├── DomainEvent.java
│   ├── EventBus.java
│   ├── EventContext.java
│   ├── EventEnvelope.java
│   ├── EventHandler.java
│   ├── EventPublishResult.java
│   └── EventSubscription.java
├── codec
│   ├── EventCodec.java
│   └── JacksonEventCodec.java
├── config
│   ├── EventBusAutoConfiguration.java
│   ├── EventBusProperties.java
│   └── EventBusBeanNames.java
├── core
│   ├── DefaultEventBus.java
│   ├── EventEnvelopeFactory.java
│   ├── EventListenerMethodAdapter.java
│   └── EventListenerRegistrar.java
├── dlq
│   ├── DeadLetterEvent.java
│   ├── DeadLetterPublisher.java
│   └── DefaultDeadLetterPublisher.java
├── exception
│   ├── EventBusException.java
│   ├── EventCodecException.java
│   └── EventPublishException.java
├── telemetry
│   ├── EventTelemetryReporter.java
│   ├── NoopEventTelemetryReporter.java
│   └── PlatformAdminTelemetryReporter.java
├── trace
│   ├── EventTraceProvider.java
│   └── DefaultEventTraceProvider.java
└── transport
    ├── EventMessage.java
    ├── EventMessageConsumer.java
    ├── EventTransport.java
    ├── local
    │   └── LocalEventTransport.java
    └── kafka
        ├── KafkaEventTransport.java
        ├── KafkaProducerFactory.java
        └── KafkaConsumerContainer.java
```

---

## 4. 核心 API

### 4.1 DomainEvent

```java
public interface DomainEvent {

    String eventType();

    String idempotentKey();

    default String partitionKey() {
        return idempotentKey();
    }

    default String eventVersion() {
        return "1.0";
    }
}
```

说明：

| 方法 | 说明 |
|---|---|
| `eventType()` | 事件类型，必填 |
| `idempotentKey()` | 业务幂等键，必填 |
| `partitionKey()` | MQ 分区键，默认使用幂等键 |
| `eventVersion()` | 事件版本，默认 `1.0` |

### 4.2 EventEnvelope

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

    // getters / setters
}
```

### 4.3 EventBus

```java
public interface EventBus {

    EventPublishResult publish(DomainEvent event);

    EventPublishResult publish(String topic, DomainEvent event);

    void publishAsync(DomainEvent event);

    void publishAsync(String topic, DomainEvent event);

    void publishAfterCommit(DomainEvent event);

    void publishAfterCommit(String topic, DomainEvent event);
}
```

MVP 暂不实现 `publishReliable`，该方法留到 Outbox 阶段。

### 4.4 EventPublishResult

```java
public class EventPublishResult {

    private boolean success;
    private String eventId;
    private String topic;
    private String messageId;
    private String errorCode;
    private String errorMessage;

    public static EventPublishResult success(String eventId, String topic, String messageId) { ... }

    public static EventPublishResult failure(String eventId, String topic, String errorCode, String errorMessage) { ... }
}
```

### 4.5 EventContext

```java
public class EventContext {

    private EventEnvelope<?> envelope;
    private String topic;
    private String consumerGroup;
    private String messageId;
    private Integer retryCount;
    private Long receivedAt;
}
```

### 4.6 EventHandler

```java
public interface EventHandler<T extends DomainEvent> {

    ConsumeResult handle(T event, EventContext context);
}
```

### 4.7 ConsumeResult

```java
public enum ConsumeResult {
    SUCCESS,
    RETRY,
    DISCARD
}
```

---

## 5. 注解消费设计

### 5.1 EventListener

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface EventListener {

    String topic();

    String eventType();

    String group();

    Class<?> payloadType() default Void.class;

    int maxRetry() default 3;

    boolean dlq() default true;
}
```

### 5.2 使用示例

```java
@Component
public class InvocationRecordedEventHandler {

    @EventListener(
        topic = "open-platform-invocation",
        eventType = "open-platform.invocation.recorded",
        group = "platform-admin"
    )
    public void handle(InvocationRecordedEvent event, EventContext context) {
        // 写 api_invocation
    }
}
```

### 5.3 方法签名支持

MVP 支持以下签名：

```java
void handle(MyEvent event)
void handle(MyEvent event, EventContext context)
ConsumeResult handle(MyEvent event)
ConsumeResult handle(MyEvent event, EventContext context)
```

不支持：

```text
多个业务参数
返回任意对象
泛型 payload 自动推断的复杂场景
```

---

## 6. 自动配置

### 6.1 spring.factories

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.vtc.asset.security.platform.eventbus.config.EventBusAutoConfiguration
```

### 6.2 EventBusAutoConfiguration

```java
@Configuration
@EnableConfigurationProperties(EventBusProperties.class)
@ConditionalOnProperty(prefix = EventBusProperties.PREFIX, name = "enabled", havingValue = "true", matchIfMissing = false)
public class EventBusAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public EventCodec eventCodec() {
        return new JacksonEventCodec();
    }

    @Bean
    @ConditionalOnMissingBean
    public EventTraceProvider eventTraceProvider() {
        return new DefaultEventTraceProvider();
    }

    @Bean
    @ConditionalOnMissingBean
    public EventTelemetryReporter eventTelemetryReporter() {
        return new NoopEventTelemetryReporter();
    }

    @Bean
    @ConditionalOnMissingBean
    public EventEnvelopeFactory eventEnvelopeFactory(...) {
        return new EventEnvelopeFactory(...);
    }

    @Bean
    @ConditionalOnMissingBean
    public EventTransport eventTransport(...) {
        // 根据 properties.transport 创建 local 或 kafka transport
    }

    @Bean
    @ConditionalOnMissingBean
    public EventBus eventBus(...) {
        return new DefaultEventBus(...);
    }

    @Bean
    public EventListenerRegistrar eventListenerRegistrar(...) {
        return new EventListenerRegistrar(...);
    }
}
```

### 6.3 配置前缀

```text
vtc.asset-security.eventbus
```

说明：使用 `asset-security` 前缀区分独立平台级 starter，不与 `vtc.kafka`、`vtc.redis`、`esmp` 既有配置混淆。

---

## 7. 配置项

```java
@ConfigurationProperties(prefix = EventBusProperties.PREFIX)
public class EventBusProperties {

    public static final String PREFIX = "vtc.asset-security.eventbus";

    private boolean enabled = false;
    private String transport = "local";
    private String appName;
    private String defaultTopic = "asset-security-domain-event";
    private String domain = "asset-security";

    private Async async = new Async();
    private Kafka kafka = new Kafka();
    private Dlq dlq = new Dlq();
    private Telemetry telemetry = new Telemetry();

    public static class Async {
        private int corePoolSize = 10;
        private int maximumPoolSize = 30;
        private int queueCapacity = 1000;
    }

    public static class Kafka {
        private String bootstrapServers;
        private String clientId;
        private String acks = "all";
        private int retries = 3;
        private boolean enableIdempotence = true;
        private String autoOffsetReset = "latest";
        private int pollTimeoutMs = 1000;
        private int maxPollRecords = 100;
    }

    public static class Dlq {
        private boolean enabled = true;
        private String topicSuffix = ".DLQ";
    }

    public static class Telemetry {
        private boolean enabled = false;
        private String platformAdminUrl;
        private String reportPath = "/internal/eventbus/telemetry";
    }
}
```

配置示例：

```yaml
vtc:
  asset-security:
    eventbus:
      enabled: true
      transport: kafka
      app-name: ${spring.application.name}
      default-topic: asset-security-domain-event
      domain: open-platform
      kafka:
        bootstrap-servers: 172.16.3.33:9092
        acks: all
        retries: 3
        enable-idempotence: true
      dlq:
        enabled: true
        topic-suffix: .DLQ
      telemetry:
        enabled: true
        platform-admin-url: http://platform-admin
```

---

## 8. EventEnvelopeFactory

### 8.1 职责

`EventEnvelopeFactory` 负责把业务事件包装为统一信封。

填充字段：

```text
eventId
eventType
eventVersion
topic
domain
sourceService
traceId
idempotentKey
partitionKey
occurredAt
payload
headers
```

### 8.2 eventId 生成

MVP 可用：

```text
UUID.randomUUID().toString().replace("-", "")
```

后续可切换为 Snowflake。

### 8.3 traceId 获取

顺序：

1. 当前 MDC 中的 `traceId`；
2. 请求头中透传的 `X-Trace-Id`；
3. 新生成 UUID。

MVP 可先实现 MDC + UUID。

### 8.4 tenant / subject 扩展

MVP 中 `tenantType/tenantId/subjectType/subjectId` 可通过以下方式填充：

1. 事件实现可选接口 `EventContextAware`；
2. 或从 headers 设置；
3. 没有则为空。

可选接口：

```java
public interface EventContextAware {

    default String tenantType() { return null; }

    default String tenantId() { return null; }

    default String subjectType() { return null; }

    default String subjectId() { return null; }
}
```

---

## 9. Codec 设计

### 9.1 EventCodec

```java
public interface EventCodec {

    String encode(EventEnvelope<?> envelope);

    EventEnvelope<?> decode(String message);

    <T> T convertPayload(Object payload, Class<T> payloadType);
}
```

### 9.2 JacksonEventCodec

实现要求：

1. `encode` 输出 JSON 字符串；
2. `decode` 反序列化为 `EventEnvelope`，payload 可为 `LinkedHashMap`；
3. handler 调用前通过 `convertPayload` 转换为业务事件类型；
4. 日期字段首期使用 Long 时间戳。

---

## 10. Transport 设计

### 10.1 EventTransport

```java
public interface EventTransport {

    String type();

    EventPublishResult publish(EventEnvelope<?> envelope);

    void subscribe(EventSubscription subscription, EventMessageConsumer consumer);

    default void start() { }

    default void stop() { }
}
```

### 10.2 EventMessage

```java
public class EventMessage {

    private String topic;
    private String messageId;
    private String key;
    private String body;
    private Map<String, String> headers;
}
```

### 10.3 LocalEventTransport

用途：

```text
本地开发
单元测试
无 MQ 环境验证
```

实现：

- 内存保存 subscription；
- publish 后通过 executor 异步分发；
- 只在当前 JVM 有效；
- 不保证进程重启不丢。

### 10.4 KafkaEventTransport

实现要求：

1. 使用 `KafkaProducer<String, String>` 发布；
2. key 使用 `envelope.partitionKey`；
3. value 使用 `EventCodec.encode(envelope)`；
4. consumer 按 `EventSubscription.topic/group` 创建；
5. 收到消息后交给 `EventMessageConsumer`；
6. 消费成功后提交 offset；
7. 消费异常按 retry / DLQ 策略处理。

MVP 可采用简单线程模型：

```text
每个 subscription 创建一个 KafkaConsumerContainer
每个 container 一个线程 poll
```

后续再增强并发消费。

---

## 11. DefaultEventBus

### 11.1 publish

流程：

```text
校验 event
确定 topic
EventEnvelopeFactory 创建 envelope
transport.publish(envelope)
telemetryReporter.reportPublished(envelope, result)
返回 EventPublishResult
```

### 11.2 publishAsync

流程：

```text
提交到 eventbus executor
调用 publish
异常只记录日志和 telemetry，不抛到业务主链路
```

### 11.3 publishAfterCommit

如果存在 Spring 事务：

```text
TransactionSynchronizationManager.registerSynchronization
afterCommit 后调用 publishAsync 或 publish
```

如果没有事务：

```text
直接 publishAsync
```

MVP 建议：

```text
publishAfterCommit 默认 afterCommit 后异步发布
```

避免阻塞事务提交线程。

---

## 12. EventListenerRegistrar

### 12.1 职责

扫描 Spring 容器中带 `@EventListener` 的方法，注册为 `EventSubscription`。

### 12.2 注册流程

```text
遍历所有 Bean
扫描方法上的 @EventListener
校验方法签名
解析 payloadType
创建 EventListenerMethodAdapter
创建 EventSubscription
transport.subscribe(subscription, adapter)
telemetryReporter.reportSubscription(subscription)
```

### 12.3 payloadType 解析

优先级：

1. 注解 `payloadType` 非 Void；
2. 方法第一个参数类型；
3. 无法解析则启动失败。

### 12.4 EventListenerMethodAdapter

职责：

```text
decode envelope
校验 eventType
payload 转换
构造 EventContext
反射调用业务方法
处理返回 ConsumeResult
异常转为 RETRY 或 DLQ
上报 consume trace
```

---

## 13. DLQ 设计

### 13.1 DLQ topic

默认：

```text
{originTopic}.DLQ
```

例如：

```text
open-platform-invocation.DLQ
open-platform-webhook.DLQ
```

### 13.2 DeadLetterEvent

```java
public class DeadLetterEvent {

    private String eventId;
    private String eventType;
    private String originTopic;
    private String consumerGroup;
    private String sourceService;
    private String failedService;
    private String failedHandler;
    private String errorMessage;
    private String errorStackDigest;
    private String originMessage;
    private Long deadTime;
}
```

### 13.3 进入 DLQ 条件

```text
反序列化失败
payload 转换失败
handler 连续异常超过 maxRetry
handler 返回 DISCARD 且 dlq=true
```

### 13.4 MVP 简化

MVP 可先做到：

1. 消费异常捕获；
2. 重试次数内本地重试；
3. 超过 `maxRetry` 后发 DLQ topic；
4. 记录错误日志；
5. telemetry 上报失败。

---

## 14. Telemetry 上报

### 14.1 接口

```java
public interface EventTelemetryReporter {

    void reportPublished(EventEnvelope<?> envelope, EventPublishResult result);

    void reportConsumed(EventEnvelope<?> envelope, EventContext context, ConsumeResult result, Throwable error);

    void reportSubscription(EventSubscription subscription);

    void reportDeadLetter(DeadLetterEvent deadLetterEvent);
}
```

### 14.2 MVP 实现

首期两个实现：

```text
NoopEventTelemetryReporter
PlatformAdminTelemetryReporter
```

默认：

```text
telemetry.enabled=false 时使用 Noop
```

启用后：

```text
POST {platformAdminUrl}/internal/eventbus/telemetry/published
POST {platformAdminUrl}/internal/eventbus/telemetry/consumed
POST {platformAdminUrl}/internal/eventbus/telemetry/subscriptions
POST {platformAdminUrl}/internal/eventbus/telemetry/dead-letters
```

### 14.3 失败策略

Telemetry 上报失败不能影响业务事件发布和消费。

```text
只记录日志
不抛出到业务链路
可异步重试，MVP 暂不强制
```

---

## 15. 线程池

### 15.1 EventBus Executor

Bean 名称：

```text
assetSecurityEventBusExecutor
```

用途：

```text
publishAsync
local transport 分发
telemetry 异步上报
```

### 15.2 线程命名

```text
asset-security-eventbus-%d
```

### 15.3 拒绝策略

MVP 建议：

```text
CallerRunsPolicy 或阻塞入队
```

调用记录场景应避免阻塞主链路，后续可增加丢弃策略与 metrics。

---

## 16. 首批业务事件建议

### 16.1 InvocationRecordedEvent

```java
public class InvocationRecordedEvent implements DomainEvent, EventContextAware {

    private String invocationId;
    private String requestId;
    private String partnerId;
    private String clientId;
    private String apiCode;
    private String method;
    private String path;
    private String routeMode;
    private String targetService;
    private Long startTime;
    private Long endTime;
    private Long costMillis;
    private Integer statusCode;
    private String errorCode;
    private String errorMessage;
    private String traceId;

    public String eventType() {
        return "open-platform.invocation.recorded";
    }

    public String idempotentKey() {
        return "invocation:" + invocationId;
    }

    public String tenantType() {
        return "partner";
    }

    public String tenantId() {
        return partnerId;
    }

    public String subjectType() {
        return "invocation";
    }

    public String subjectId() {
        return invocationId;
    }
}
```

### 16.2 OpenPlatformWebhookEvent

```java
public class OpenPlatformWebhookEvent implements DomainEvent, EventContextAware {

    private String eventId;
    private String partnerId;
    private String eventName;
    private String resourceType;
    private String resourceId;
    private String routeMode;
    private Long occurredAt;
    private Object payload;
    private String traceId;

    public String eventType() {
        return "open-platform.webhook.event";
    }

    public String idempotentKey() {
        return "webhook:" + eventName + ":" + resourceType + ":" + resourceId;
    }

    public String partitionKey() {
        return partnerId;
    }

    public String tenantType() {
        return "partner";
    }

    public String tenantId() {
        return partnerId;
    }

    public String subjectType() {
        return resourceType;
    }

    public String subjectId() {
        return resourceId;
    }
}
```

---

## 17. 测试方案

### 17.1 单元测试

| 测试 | 目标 |
|---|---|
| `EventEnvelopeFactoryTest` | envelope 字段生成正确 |
| `JacksonEventCodecTest` | encode/decode 正常 |
| `LocalEventTransportTest` | 本地发布消费正常 |
| `EventListenerRegistrarTest` | 注解扫描正常 |
| `EventListenerMethodAdapterTest` | 方法签名调用正常 |
| `DefaultEventBusTest` | publish / publishAsync / publishAfterCommit 正常 |

### 17.2 集成测试

| 测试 | 目标 |
|---|---|
| local transport demo | 单 JVM 事件消费 |
| kafka transport demo | Kafka 发送和消费 |
| DLQ demo | handler 抛异常后进入 DLQ |
| telemetry demo | 上报 platform-admin mock endpoint |

### 17.3 验收 demo

建议在 starter 内提供 test/demo：

```text
DemoEvent
DemoEventPublisher
DemoEventHandler
```

启动后：

```text
调用 publisher
handler 收到事件
日志打印 eventId / eventType / traceId
```

---

## 18. 风险与约束

| 风险 | 处理 |
|---|---|
| Kafka client 版本与现有工程冲突 | 依赖 optional，业务服务统一版本管理 |
| WebFlux / Servlet 环境差异 | starter 不依赖 Web MVC，只用 Spring core / boot autoconfigure |
| 反射调用 handler 异常难定位 | 日志必须打印 eventId、eventType、handler |
| payload 类型转换失败 | 进入 DLQ，记录原始消息 |
| telemetry 影响主链路 | telemetry 必须异步且失败不抛出 |
| publishAsync 队列满 | MVP 记录错误，后续提供丢弃/阻塞策略配置 |

---

## 19. MVP 验收清单

- 可通过 Maven 引入 `asset-security-starter-eventbus`；
- 配置 `vtc.asset-security.eventbus.enabled=true` 后自动启用；
- local transport 可发布和消费；
- kafka transport 可发布和消费；
- 支持 `@EventListener` 注解消费；
- 支持 `publish`、`publishAsync`、`publishAfterCommit`；
- envelope 字段完整；
- 消费失败可进入 DLQ；
- telemetry 可开关；
- 不依赖 `platform-admin` 才能启动；
- 不修改现有 `esmp-starters`。

---

## 20. 后续增强

MVP 之后继续增强：

```text
Outbox publishReliable
Inbox 幂等消费
Redis Stream transport
Schema 校验
灰度消费
批量消费
消费并发控制
手动重放
指标 metrics
OpenTelemetry / SkyWalking trace 对接
```
