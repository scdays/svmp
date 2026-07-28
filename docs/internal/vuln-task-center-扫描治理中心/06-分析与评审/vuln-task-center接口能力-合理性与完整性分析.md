# vuln-task-center 接口能力文档 — 合理性与业务完整性分析

| 项 | 值 |
|----|----|
| 分析对象 | `04-子PRD与规格/vuln-task-center提供的接口能力.md`（15 接口 + 1 回调） |
| 分析依据 | `project_backend/svmp/vuln-task-center/` 现有代码（Ui / App / Domain / Infra 全层盘点） |
| 分析日期 | 2026-07-27 |
| 结论 | 文档主干合理（主/子两级粒度、通知+拉取双模式、三创建模式、四客户端分配差异化），但**任务类型范畴未定义、状态机缺失、回调通道未约定、异常/幂等/权限/终点等业务完整性存在 8 项缺口**。建议先落 WP1+WP2+WP3 基础层再补接口。 |

> 本报告仅做文档分析与评审，**不含代码实施**。后续开发方向见第 5 节，已确认的决策记录于第 6 节。

---

## 1. 现状对照（分析基础）

### 1.1 接口能力现状矩阵

| # | 文档接口 | 实现状态 | 现有落点 | 备注 |
|---|---------|---------|---------|------|
| 1a | 任务下发（仅记录不下发） | 部分 | `ScanTaskUi#addFirstHalf` → `ScanTaskServiceImpl#saveFirstHalf` | 仅 DB 落库不调 mint，但硬编码 `flag="7"`，专用于"上半场"流程，非通用运营指标分发 |
| 1b | 任务执行（确认后下发） | 部分 | `ScanTaskUi#addSecondHalf` → `ScanTaskServiceImpl#saveSecondHalf` | 删旧记录 + mintClient.add；**无"安全员确认"环节**，无运营指标语义 |
| 1c | 任务创建（自动调度） | 已有 | `ScanTaskUi#add` → `ScanTaskServiceImpl#save` | DB 落库 + mintClient.add 一步完成 |
| 1d | 4 类客户端区分 | 缺失 | 无 `clientType` 字段、无路由分发 | 扫描器分配仅按 sceneId + 用户权限，不区分四类来源 |
| 1e | 子任务列表回调通知 | 缺失 | `ui/event/*` 全为入站端点 | 无主动推送子任务列表能力 |
| 2 | 主任务详情查询 | 已有 | `ScanTaskUi#vulnScanBasicInfo` | 返回主任务基础信息 |
| 3 | 子任务列表查询 | 已有 | `ScanSubTaskUi#page/list` | 子任务维度查询已有 |
| 4 | 主任务暂停/启动 | 已有 | `ScanTaskUi#pause/resume` + `classifyPause/Resume` | 调度级 + 实例级，主任务级批量已有 |
| 5 | 主任务删除 | 已有 | `ScanTaskUi#delete` → `removeByIds` | 级联删子任务 |
| 6 | 主任务生成报告 | 部分 | `ScanTaskUi#downloadReportLmByAll` | **仅绿盟(LM)**，无通用厂商入口 |
| 7 | 主任务报告生成结束通知 | 缺失 | 无主动通知 | 仅 `queryDownloadReport` 拉取 |
| 8 | 查询主任务报告进度/状态 | 已有 | `ScanTaskUi#queryDownloadReport` | 基于 Redis Hash + `ScanTaskLmReportDO` |
| 9 | 查询扫描器任务列表 | 部分 | `ScanTaskUi#vulnScanScanNodeList` | **按 surveyId 维度**，无法跨 survey 列某扫描器全部任务 |
| 10 | 子任务详情查询 | 已有 | `ScanSubTaskUi#findById` | — |
| 11 | 子任务暂停/启动 | 缺失 | `ScanSubTaskUi` 仅 6 个 CRUD | 无子任务级 pause/resume |
| 12 | 子任务删除 | 已有 | `ScanSubTaskUi#delete` | 方法名 `pause` 实为 delete，命名误导 |
| 13 | 子任务生成报告 | 部分 | `ScanTaskUi#downloadReportLmById` | **仅绿盟** |
| 14 | 子任务报告生成结束通知 | 缺失 | 无主动通知 | 同 #7 |
| 15 | 查询子任务报告进度/状态 | 部分 | 复用 `queryDownloadReport` | 入参 surveyId 非 subTaskId，需客户端自行匹配 |

### 1.2 领域模型现状

- **三套并行任务概念，无统一父抽象**：
  - `TaskInfoDO`：mint 调度元数据（`appHost`/`path`/`cron`），非业务任务本身
  - `ScanTaskDO` + `ScanTaskSurveyDO`(执行实例) + `ScanSubTaskDO`(按扫描节点拆分的子任务)：扫描任务核心
  - `WorkbenchVulnOrderDO` / `WorkbenchVulnTaskDO`：部侧工单/任务，**独立领域**，仅靠 `scanTaskId` 弱关联 `ScanTaskDO`，状态模型互不兼容
- **任务类型双维度字符串**：`taskType`(vuln/pwd/baseline/port/alive) × `classifyId`(LM/AH/QM/TRX...)，靠 `if("port_scan".equals(taskType))` 硬编码分发（`ScanTaskAppServiceImpl` ~line 430）
- **状态硬编码字符串散落 3 套**：
  - `ScanTaskDO.taskState`：0未开始/1启动/2暂停/3完成
  - `ScanTaskSurveyDO.state`：0未开始/1执行中/2已完成/3失败/4暂停/5重启
  - `ScanSubTaskDO.state`：0未开始/1执行中/2已完成/3失败/4暂停
  - DB 用数字字符串，ES 层 `VulnScanNodeExecuteAttrEnum` 用英文枚举(finish/executing/pause)，需手工映射
- **无状态机**：仅 `classifyPause`/`classifyResume` 两处有状态前置校验，计划级 pause/resume/delete 无校验
- **4 类客户端任务分散在 3 个领域**：task / workbench / event，无统一 facade

### 1.3 调度 / 回调 / 分配 / 报告现状

- **调度**：mint 外部 cron + **单机 `java.util.Timer`**(`InitHandler#initTimerTask`) + Redis 队列；非真正分布式调度，多实例部署 Timer 重复执行
- **回调通知**：
  - `ui/event/*` 全是**入站** REST 端点（被 mint / 外部服务调用），非主动推送
  - 主动通知仅有：WebSocket(前端进度)、Kafka(vuln-model 等下游服务)
  - `ScanTaskDTO.appHost/path` 字段标注"回调服务名/路径"，**仅透传给 mint，从未用于回调任务创建客户端**
- **扫描器分配**：`QueueAppServiceImpl#getNodeScannerMap` 最小负载算法（满足 vtc 负载均衡）；`vulnRescan(Map)` 中 nodeId/scannerId 指定逻辑**已被注释**；无 `scannerHash` 概念
- **报告**：仅 LM 厂商；`ScanTaskLMReportListener` 轮询生成后写 DB/FTP，**无主动通知**；客户端只能轮询

---

## 2. 合理性分析

### 2.1 合理之处

| # | 优点 | 说明 |
|---|------|------|
| A1 | 主/子任务两级操作粒度清晰 | 创建/查询/暂停启动/删除/报告 各自分主任务级(批量)与子任务级(单条)，契合扫描任务"一主多子"天然结构 |
| A2 | 报告"通知 + 拉取"双模式 | 接口 7/14 主动通知 + 8/15 阻断时主动拉取，异步解耦稳健 |
| A3 | 三种创建模式分离 | 下发/执行/创建 匹配运营指标任务"管理员分发 → 安全员确认执行"两阶段审批语义 |
| A4 | 四客户端分配策略差异化 | 负载均衡 / 指定节点 / 指定 HASH / 指定厂商，反映真实业务来源差异 |

### 2.2 合理性问题

| # | 问题 | 影响 | 代码佐证 |
|---|------|------|---------|
| P1 | **"上层不同类型任务"范畴未定义** | 文档反复提"不同类型任务"但未列举类型清单与各自生命周期差异；现状有 ScanTask(6 种 taskType) × Workbench 工单/任务 × 开放平台任务，接口适用对象不明 | 4 类任务分散在 `domain/task`、`domain/workbench`、`ui/event/ScanTaskEvent#outsideScan` |
| P2 | **"运营指标任务"语义模糊** | 任务下发/执行"仅适用于运营指标任务"，但未定义其与其他类型边界、状态差异、与 `builtInTask`/`vmId` 的关系 | `ScanTaskDO` `builtInTask`(line ~163)、`vmId`(line ~188)、`saveFirstHalf` 硬编码 `flag="7"` |
| P3 | **状态机缺失** | 列出暂停/启动/删除等操作，但未定义状态枚举与合法转换矩阵（已完成能否暂停？失败能否恢复？删除前置条件？），无法约束非法操作 | 计划级 pause/resume/delete 无状态前置校验（`ScanTaskAppServiceImpl#pause` ~line 1487） |
| P4 | **回调通道未约定** | "vuln-task-center 主动发起，客户端接收"——未约定通道(Feign/Kafka/Webhook)、回调地址注册、失败重试、幂等性 | `ScanTaskDTO.appHost/path` 字段存在但仅透传给 mint，未用于回调客户端 |
| P5 | **子任务列表回调时机模糊** | 子任务在 `executeScanTask` 时按扫描节点拆分创建。回调时机是"全部创建后"还是"流式"？周期任务跨多 survey，每次执行都回调？ | `ScanTaskAppServiceImpl#executeScanTask` ~line 421、`saveSurvey` ~line 1941 |
| P6 | **主任务报告 vs 子任务报告关系未定义** | 接口 6"生成每一个子任务的原始报告" vs 接口 13"子任务生成报告"——包含关系(主=子聚合)还是独立触发？ | `downloadReportLmByAll` vs `downloadReportLmById` |
| P7 | **接口 9 维度不清** | "查询扫描器任务列表"——某扫描器当前执行中还是历史全部？是否分页？ | 现有 `vulnScanScanNodeList` 仅按 surveyId 查，无法跨 survey |
| P8 | **文档术语/拼写不统一** | "domnload"(download)、"声明周期"(生命周期)、接口 12"返回子任务列表信息"(删除应返回删除结果) | 文档原文 |

---

## 3. 业务完整性缺口

| # | 缺口 | 说明 | 归类 |
|---|------|------|------|
| C1 | 异常/失败场景未覆盖 | 扫描器不可用、下发失败、扫描超时、报告生成失败 的状态流转与通知未定义 | 状态/通知 |
| C2 | 并发与幂等语义未定义 | 重复创建、重复暂停/启动、并发操作同一主任务的语义缺失 | 并发 |
| C3 | 权限模型不完整 | 仅运营指标任务提到"管理员分发/安全员确认"，其他 3 类客户端任务的权限与操作边界未定义 | 权限 |
| C4 | 生命周期终点未定义 | 任务完成是否自动归档？报告保留期？删除逻辑还是物理？ | 生命周期 |
| C5 | 复扫接口缺失 | 文档提到"修复核验复扫时客户端指定节点"，但无独立复扫接口定义 | 接口缺失 |
| C6 | 进度聚合查询缺失 | 子任务详情含进度，但主任务整体进度聚合查询未明确 | 接口缺失 |
| C7 | 任务统计/审计缺失 | 无任务概览、统计、操作审计接口 | 接口缺失 |
| C8 | 回调地址生命周期未定义 | 客户端回调地址如何注册/更新/失效？多客户端隔离？ | 回调 |

---

## 4. 现状关键缺口清单（对照文档）

| 缺口 | 影响 | 涉及接口 |
|------|------|---------|
| 子任务列表回调通知 | 客户端无法被动获知子任务状态/节点IP/厂商，只能轮询 | 1e |
| 报告生成结束通知（主+子） | 客户端无法被动获知报告就绪，只能轮询 | 7、14 |
| 子任务级暂停/启动 | 无法对单个扫描器任务精细化控制 | 11 |
| 4 类客户端区分 + 分配策略 | 无 clientType；不支持指定 HASH/节点/厂商路由 | 1d |
| 三创建模式未对齐运营指标语义 | saveFirstHalf/SecondHalf 与"上半场"耦合，硬编码 flag="7" | 1a、1b |
| 查询扫描器任务列表（跨 survey） | 现有仅按 surveyId 查 | 9 |
| 报告生成厂商通用化 | 仅 LM，未覆盖 AH/QM/TRX/POC/Nessus 等 | 6、13 |
| 子任务报告进度按 subTaskId 直查 | 现有入参 surveyId，需客户端自行匹配 | 15 |
| 回调通道基础设施缺失 | 无回调地址注册、无回调 Feign/Kafka 通道 | 1e、7、14 |
| 真正分布式调度缺失 | 单机 Timer，多实例重复执行 | 调度 |

---

## 5. 后续完善方向建议（开发参考，本次不实施）

> 以下为基于本次分析的后续开发建议方向，遵循 ponytail（YAGNI/最小 diff）与 DDD 分层硬约束：**不重构现有领域模型，在其之上建立统一生命周期管控层，渐进增强**。

### 5.1 总体架构

```
┌─────────────────────────────────────────────────────┐
│  统一任务生命周期 Facade（新增，app/service/lifecycle）│  ← 4 类客户端统一入口
│  create / dispatch / execute / pause / resume /      │
│  delete / report / query                             │
└──────────┬──────────────────────────────────────────┘
           │ 按 TaskCategory 路由
   ┌───────┼───────┬───────────────┐
   ▼       ▼       ▼               ▼
ScanTask  OpsMetric  DeptWorkorder  OpenPlatform
(现有)    (复用+增强) (现有workbench) (现有event)
   │       │           │               │
   ▼       ▼           ▼               ▼
┌─────────────────────────────────────────────────────┐
│  统一状态机 + 生命周期事件 + 回调通道（新增 domain 层）│
└──────────┬──────────────────────────────────────────┘
           ▼
   现有 ScanTaskServiceImpl / QueueAppServiceImpl / mint
```

### 5.2 工作包

| WP | 内容 | 核心产出 |
|----|------|---------|
| WP1 | 统一任务类型与创建模式建模 | `TaskCategoryEnum`(SCAN_MANAGE/OPS_METRIC/DEPT_WORKORDER/OPEN_PLATFORM)、`CreateModeEnum`(DISPATCH_ONLY/CONFIRM_EXECUTE/CREATE_AND_SCHEDULE)；`ScanTaskDO` 增 `category` 字段（或复用 flag+builtInTask 映射）；`save/saveFirstHalf/saveSecondHalf` 重构为基于 CreateMode 的策略分发；解耦 saveSecondHalf 的"删除重建"为"更新并下发" |
| WP2 | 统一状态枚举与状态机 | `TaskLifecycleStatusEnum` + `SubTaskLifecycleStatusEnum`（包装现有 3 套字符串，**包装兼容**）；状态转换矩阵 + `TaskStateMachine` 校验器；计划级 pause/resume/delete 补状态前置校验 |
| WP3 | 生命周期领域事件 + 回调通道 | `TaskLifecycleEvent`(Created/Dispatched/Executing/Paused/Resumed/Completed/Failed/Deleted/ReportReady/SubTaskListReady)；**Kafka 回调 topic** 方案（定义回调 topic，客户端订阅）；回调地址注册（复用 appHost/path 或新增 task_callback_config 表）；失败重试 + 幂等键 |
| WP4 | 补齐缺失接口 | 子任务暂停/启动、通用报告生成(多厂商 ReportGenerateStrategy)、查询扫描器任务列表(跨 survey)、子任务报告进度按 subTaskId 直查 |
| WP5 | 4 类客户端分配差异化 | 复扫指定节点(恢复注释逻辑)、部侧 scannerHash、开放平台专属入口、按 clientType 路由 |
| WP6 | 异常/幂等/终点治理 | 异常状态流转+通知、操作幂等键、归档与报告保留策略 |

### 5.3 建议实施顺序
**WP1 → WP2 → WP3 → WP4 → WP5 → WP6**（前三个是基础，WP4/5 接口补齐，WP6 治理增强）

---

## 6. 决策记录（已确认）

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 本次实施范围 | **WP1+WP2+WP3 基础层** | 建立统一抽象与状态机基础，不新增对外接口；后续迭代再补 WP4/5/6 |
| 回调通知通道 | **Kafka 回调 topic** | 定义回调 topic，客户端订阅；与现有 Kafka 体系一致 |
| 状态机改造程度 | **包装兼容** | 新增统一枚举包装现有 3 套字符串，状态机校验新增操作路径，旧硬编码赋值渐进替换，向后兼容 |
| 本次下一步 | **仅输出文档分析报告** | 开发另起；本报告为后续开发的需求/设计输入 |

---

## 附录：关键代码索引

| 关注点 | 路径 |
|--------|------|
| 主任务 UI（50+ 端点） | [ScanTaskUi.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/ui/ScanTaskUi.java) |
| 子任务 UI（仅 6 CRUD） | [ScanSubTaskUi.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/ui/ScanSubTaskUi.java) |
| mint 回调执行入口 | [ScanTaskEvent.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/ui/event/ScanTaskEvent.java) |
| 核心 App 实现（5000+ 行） | [ScanTaskAppServiceImpl.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/app/service/impl/ScanTaskAppServiceImpl.java) |
| 三创建模式实现 | [ScanTaskServiceImpl.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/service/impl/ScanTaskServiceImpl.java) |
| 调度元数据实体 | [TaskInfoDO.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/model/entity/TaskInfoDO.java) |
| 扫描任务主表 | [ScanTaskDO.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/model/entity/ScanTaskDO.java) |
| 任务执行实例 | [ScanTaskSurveyDO.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/model/entity/ScanTaskSurveyDO.java) |
| 子任务 | [ScanSubTaskDO.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/model/entity/ScanSubTaskDO.java) |
| 部侧工单/任务 | [WorkbenchVulnOrderDO.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/workbench/model/entity/WorkbenchVulnOrderDO.java) |
| 队列与负载均衡 | [QueueAppServiceImpl.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/app/service/impl/QueueAppServiceImpl.java) |
| mint 调度 Feign | [IMintClient.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/infrastructure/feign/IMintClient.java) |
| Timer 初始化 | [InitHandler.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/service/event/init/InitHandler.java) |
| LM 报告轮询 | [ScanTaskLMReportListener.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/domain/task/service/event/timerTask/ScanTaskLMReportListener.java) |
| Kafka 消费 | [Consumer.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/infrastructure/utils/kafka/Consumer.java) |
| WebSocket | [WebSocketServer.java](project_backend/svmp/vuln-task-center/src/main/java/com/mvtech/vuln/task/infrastructure/utils/webSocket/WebSocketServer.java) |
