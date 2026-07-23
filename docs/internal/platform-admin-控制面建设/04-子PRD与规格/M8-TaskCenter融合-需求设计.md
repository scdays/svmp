# M8 Task Center 融合需求设计

> ⚠️ 状态：**搁置（2026-06-25）**。事件流方向与 esmp-starter-task 的关系未定，本文档为探索过程中的草稿，不代表最终方案。待重新设计后再启动。
>
> 版本：v1.0  日期：2026-06-25
> 上游文档：[00-主计划.md](./00-主计划.md)、`03-落地方案/资产安全平台控制面与EventBus-Starter实施规划.md` Phase 8
> 里程碑归属：M8（规划内最后一个里程碑）
> 设计决策（与用户确认）：**与 EventBus 同构——双 starter（task-event + task-admin）+ platform-admin.taskcenter 控制面**
>
> 命名说明：runtime 桥接 starter 命名为 `task-event`（非 task-client）。因其职责是"任务状态变更事件化"——监听 esmp-starter-task 状态变更 → 发布 TaskStatusChangedEvent，本质是事件桥接层，`task-event` 语义比泛指的 `task-client` 更准确。仍作为独立 starter 模块存在。

---

## 1. 背景与设计思想

### 1.1 背景

当前任务体系现状（实证核对）：

| 层 | 位置 | 职责 | 状态 |
|----|------|------|------|
| esmp-starter-task | `framework/asset/esmp-starters/` | 任务 runtime：TaskRoot/TaskDO/TaskInstanceDO/调度器/JobEnum 状态机；TaskUI/TaskInstanceUI 暴露查询 | ✅ 既有，不动 |
| open-api-service TaskCenter* | `open-api-service/infra/adapter/taskcenter/`（30+ 类） | 扫描任务业务集成（Kafka 回收/SFTP 报告/survey 编排） | ✅ 既有，属业务执行面，不迁 |
| platform-admin.taskcenter | — | 任务**管理控制面** | ❌ 待建（M8） |
| task-event starter | — | 桥接 esmp-starter-task 状态变更到 EventBus（事件化） | ❌ 待建（M8） |
| task-admin starter | — | taskcenter 通用管理能力 | ❌ 待建（M8） |

### 1.2 设计思想：与 EventBus 同构

platform-admin 的 taskcenter 与 eventbus **采用相同思想**：

```
EventBus 模式（M0/M6 已落地）：
  asset-security-starter-eventbus       ← runtime starter（发布/消费）
  asset-security-starter-eventbus-admin ← admin starter（目录/Schema/订阅/重放/审计）
  platform-admin.eventcenter            ← 控制面（查询/治理）

TaskCenter 模式（M8 落地，同构）：
  asset-security-starter-task-event      ← runtime 事件桥接 starter（监听 esmp-starter-task 状态变更 → 发 EventBus 事件）
  asset-security-starter-task-admin     ← admin starter（任务定义/实例视图/日志/审计/重试补偿）
  platform-admin.taskcenter             ← 控制面（任务集中管理）
```

核心：**platform-admin 不直接侵入 esmp-starter-task 的库/接口，而是通过 EventBus 事件解耦**——task-event 桥接 runtime 状态变更为事件，task-admin 消费事件落"任务视图"，platform-admin.taskcenter 查询视图 + 执行管理操作。

### 1.3 目标

1. 任务集中调度治理纳入 platform-admin.taskcenter
2. 不替换 esmp-starter-task runtime，只做管理增强（第一阶段策略，对齐实施规划 §11.2）
3. 任务状态变更通过 EventBus 事件流转，与 EventCenter 的 traceId/audit 串联
4. 支持失败查询、人工重试/补偿（敏感操作审计）

---

## 2. 需求清单

### 2.1 功能性需求

| 编号 | 需求 | 优先级 |
|------|------|--------|
| FR-1 | 新建 asset-security-starter-task-event：桥接 esmp-starter-task 状态变更 → 发 TaskStatusChangedEvent | 高 |
| FR-2 | 新建 asset-security-starter-task-admin：管理模型 + 状态机 + audit + 重试补偿 | 高 |
| FR-3 | platform-admin.taskcenter 四层域：任务定义/实例查询/失败原因/重试补偿端点 | 高 |
| FR-4 | 任务状态机 NEW/RUNNING/SUCCESS/FAILED/CANCELED，映射 esmp-starter-task JobEnum | 高 |
| FR-5 | 任务状态变更发 EventBus 事件，traceId 与 EventCenter 串联 | 中 |
| FR-6 | 重试/补偿敏感操作落审计（接 M6 audit） | 中 |

### 2.2 非功能需求

- DDD 四层合规（platform-admin 侧）；starter 不耦合业务 ORM
- Java 1.8，spring.factories 自动配置
- 不修改 esmp-starter-task 代码（只读对接/事件桥接）

---

## 3. 架构设计

### 3.1 三层职责

```
esmp-starter-task（runtime，不动）
    │ 1. 任务调度/执行，状态变更
    ▼
asset-security-starter-task-event（新建，runtime 事件桥接）
    │ 2. 监听 TaskEventUI/TaskInstanceEventUI（esmp-starter-task 既有事件）
    │    → 转换为 TaskStatusChangedEvent
    │    → 通过 EventBus（asset-security-starter-eventbus）发布
    ▼
EventBus（M0 已落地）
    │ 3. 事件投递
    ▼
asset-security-starter-task-admin（新建，admin 能力）
    │ 4. @EventListener 消费 TaskStatusChangedEvent
    │    → 落任务视图（task_instance_view）/ task_log / audit
    │    + 管理模型：task_definition / task_instance_view / task_log
    │    + 状态机 + 重试补偿服务
    ▼
platform-admin.taskcenter（新建域）
    │ 5. ui/app/domain/infra 四层
    │    查询任务定义/实例/失败原因
    │    执行重试/补偿（委托 task-admin）
    │    端点 /internal/admin/task-center/*
    ▼
EventCenter（M6 已建）traceId/audit 串联
```

### 3.2 数据模型

| 模型 | 位置 | 字段 | 说明 |
|------|------|------|------|
| TaskDefinitionDO | task-admin | taskId, taskName, taskType, cron, status, description, createdAt | 任务定义（管理视图，来源 esmp-starter-task task 表或事件上报） |
| TaskInstanceViewDO | task-admin | instanceId, taskId, status, payload, errorMsg, startedAt, finishedAt, traceId | 任务实例视图（**事件驱动投影表**，由消费 TaskStatusChangedEvent 落库） |
| TaskLogDO | task-admin | logId, instanceId, action, operator, detail, operatedAt | 任务操作日志 |
| TaskStatusChangedEvent | task-event | eventId, instanceId, taskId, fromStatus, toStatus, occurredAt, traceId | 状态变更事件（DomainEvent） |

### 3.3 状态机（映射 esmp-starter-task JobEnum）

| TaskCenter 状态 | esmp-starter-task 对应 | 触发事件 |
|----------------|----------------------|---------|
| NEW | 任务创建 | TaskStatusChangedEvent(→NEW) |
| RUNNING | JobStatus.RUNNING | TaskStatusChangedEvent(→RUNNING) |
| SUCCESS | RuningStatus.SUCCESS | TaskStatusChangedEvent(→SUCCESS) |
| FAILED | RuningStatus.FAILURE | TaskStatusChangedEvent(→FAILED) |
| CANCELED | JobStatus.PAUSE（人工暂停） | TaskStatusChangedEvent(→CANCELED) |

---

## 4. 四层结构（platform-admin.taskcenter）

### 4.1 类清单

| 层 | 类 | 继承/实现 | 说明 |
|----|----|----------|------|
| UI | TaskCenterUi | extends BaseUI | `/internal/admin/task-center/{definitions,instances,instances/{id},instances/{id}/retry,compensate}` |
| App | ITaskCenterAppService + impl | extends AppServiceImpl | 委托 task-admin 仓储/服务 |
| Domain | ITaskCenterDomainService + impl | extends DomainServiceImpl | 任务查询/重试补偿领域逻辑 |
| Infra | — | — | task-admin starter 提供 Repository（platform-admin 注入） |
| DTO | TaskDefinitionDTO, TaskInstanceDTO, TaskLogDTO, RetryRequestDTO | extends BaseDTO | — |

### 4.2 调用链
```
TaskCenterUi → TaskCenterAppServiceImpl → TaskCenterDomainServiceImpl → task-admin Repository
```

---

## 5. multi-agent 拆分（3 agent + 验证）

| Agent | 职责 | 独占文件 |
|-------|------|---------|
| **A: task-event starter** | 新模块 pom + 父 pom 注册 + TaskStatusChangedEvent + esmp-starter-task 事件监听桥接 + EventBus 发布 + AutoConfig + spring.factories | asset-security-starter-task-event/* |
| **B: task-admin starter** | 新模块 pom + 父 pom 注册 + TaskDefinitionDO/TaskInstanceViewDO/TaskLogDO + 3 Repository(InMemory) + 状态机 + @EventListener 消费 TaskStatusChangedEvent 落视图 + audit 接入 + 重试补偿服务 + AutoConfig | asset-security-starter-task-admin/* |
| **C: platform-admin.taskcenter 接入** | pom 加双依赖 + taskcenter 域四层 + TaskCenterUi 端点 + DTO | platform-admin ui/taskcenter, app/taskcenter, domain/taskcenter |

### 验证（收尾 agent）
- 两个新 starter install SUCCESS
- platform-admin mvn test 全绿（38 既有测试不回归）
- 端到端：task-event 发事件 → task-admin 消费落视图 → taskcenter 查询可见（单测覆盖）

---

## 6. 验收标准

| 编号 | 验收 | 验证 |
|------|------|------|
| AC-1 | asset-security-starter-task-event 模块存在且 install 成功 | mvn install |
| AC-2 | asset-security-starter-task-admin 模块存在且 install 成功 | mvn install |
| AC-3 | 父 pom 注册两个新模块 | pom 检查 |
| AC-4 | TaskStatusChangedEvent 通过 EventBus 发布并被 task-admin 消费 | 单测 |
| AC-5 | platform-admin.taskcenter 四层 + TaskCenterUi 端点存在 | grep |
| AC-6 | 任务定义/实例查询接口可用 | 单测 |
| AC-7 | 失败重试/补偿端点可用 + 落审计 | 单测 |
| AC-8 | 任务状态变更与 EventCenter traceId 串联 | 代码检查 |
| AC-9 | platform-admin mvn test 全绿 | mvn test |

---

## 7. 依赖与风险

- **依赖**：M6（audit/trace 串联）✅ 已完成；M0（EventBus runtime）✅ 已完成
- **风险①**：esmp-starter-task 既有事件机制（TaskEventUI/TaskInstanceEventUI）需确认是否有 Spring 事件或回调可桥接。若无，task-event 可降级为轮询查询 + 发事件（记 TODO）。**agent A 需先 Read esmp-starter-task 事件层确认。**
- **风险②**：状态映射语义缺口（PAUSE vs CANCELED）——M8 在状态机注释中说明映射关系，不强行改 runtime 语义。
- **风险③**：task-admin 的 Repository 用 InMemory（同 M6 模式），JDBC 持久化作为后续（同 eventbus-admin 一致）。
- **风险④**：platform-admin 不直连 esmp-starter-task 库——纯事件驱动视图表，解耦干净（用户已确认此方向）。

---

## 8. 与 EventBus 的同构对照表

| 维度 | EventBus（M0/M6） | TaskCenter（M8） |
|------|------------------|-----------------|
| runtime starter | asset-security-starter-eventbus | asset-security-starter-task-event |
| admin starter | asset-security-starter-eventbus-admin | asset-security-starter-task-admin |
| 控制面域 | platform-admin.eventcenter | platform-admin.taskcenter |
| 事件 | DomainEvent/EventEnvelope | TaskStatusChangedEvent（继承 DomainEvent） |
| 投递 | EventBus publish | EventBus publish（复用） |
| 消费 | @EventListener | @EventListener（复用） |
| admin 模型 | catalog/schema/subscription/replay/audit | definition/instance_view/log + audit |
| 持久化 | InMemory（M6）+ JDBC（M0） | InMemory（M8），JDBC 后续 |
| 管理端点 | /internal/admin/event-center/* | /internal/admin/task-center/* |

> 同构收益：复用 M0 的 EventBus runtime（不发新轮子）、M6 的 audit、EventCenter 的 traceId 串联；platform-admin 控制面风格统一。
