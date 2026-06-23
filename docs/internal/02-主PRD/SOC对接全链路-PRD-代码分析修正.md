# SOC 对接全链路 PRD · 代码分析修正附录（v1.1）

> **状态**：基于四工程深度代码分析后的校准
> **日期**：2026-06-17
> **关联**：`SOC对接全链路-PRD.md`（v1.0 主文档）

本文档是对主 PRD 的修正补充，基于对 vul-pass、vuln-task-center、open-api-service、asset-newleak-manage 四个工程的代码分析结果。

---

## 一、Feign 互通现状与修正

| 调用方向 | 现状 | 修正 |
|----------|------|------|
| vul-pass → vuln-task-center | **不存在** ITaskClient | W1 新建 Feign，调 first/half、second/half、results、report API |
| open-api → vul-pass | 已有 IVulPassScanTaskFeign（调 `/vul-scan-task/dispatch` 旧路径） | W1c 修改现有 Feign 路径为 `/internal/open/v1/tasks`，修改 SvmpEngineAdapterImpl 翻译层 |
| vuln-task-center → vul-pass | 无 Feign（通过 Kafka topic `dr_vul_scan_task_status` 通知） | W1 沿用 Kafka 回调，vul-pass 新建 Kafka 监听器 |

---

## 二、open-api-service 已具备能力（W1c/W4 简化）

| 能力 | 现状代码 | W1c/W4 动作 |
|------|----------|-------------|
| open_task 表 | 已有 pass_task_id、scan_policy 字段 | 无需新增 DDL |
| 双模式引擎适配 | SvmpEngineAdapterImpl（vul-pass）/ MockEngineAdapter | W1c 修改 SvmpEngineAdapterImpl 翻译层 |
| Webhook 机制 | WebhookDomainServiceImpl + HMAC-SHA256 + 重试3次 + webhook_delivery_log | 直接复用，新增 TASK_COMPLETED 触发 |
| 幂等双层 | extTaskId 业务幂等 + IdempotencyInterceptor（24h Redis） | 直接复用 |
| open_export 表 | 已存在，MockTaskExportAssembler 已实现组装管道 | W4 将 Mock 数据源替换为真实 vul-pass 数据源 |
| Webhook 事件类型 | 已有 TASK_COMPLETED/TASK_FAILED/EXPORT_READY | W4 补充 ARTIFACT_READY、INSTANCE_VERIFY_FIX_COMPLETED |
| Token 鉴权 | OAuth2 client_credentials + JWT + Redis 缓存 + Token Introspect | 直接复用 |
| Partner 管理 | partner/partner_credential/partner_capability/partner_webhook_config | 直接复用 |

---

## 三、vuln-task-center 差距

| 能力 | 现状 | 差距 |
|------|------|------|
| ScannerAdapter | **不存在**，仅有 MsgSendAbstract（2 抽象方法），路由靠 classifyId 硬编码 | W2 从零建接口，封装现有 MsgSendLM 逻辑 |
| 对账机制 | **不存在**，仅有超时检测（10min 心跳 VulnTaskListenerOther.queryScanVulResult） | W2 新建 ReconcileDomainService |
| results API | 不存在，结果散在 ES vuln_scan_node_execute + scan_sub_task | W1a 新建聚合 API |
| report 生成 | 散在 ScanTaskAppServiceImpl（~5000行），无统一状态机 | W1a 新建 ReportJob 统一管理 |
| 三套调度模式 | interface-model / tools-scheduler / SOAR 并存 | W1~W2 不收敛，Adapter 封装 read 类能力 |
| scan_sub_task | 已有表和 DO，含 surveyId/planId/state/sendParamsInfo | W1 复用，新增 pass_task_id/pass_sub_task_id 字段透传 |
| Kafka 消费者 | 已有 Consumer.java（11 个 topic 监听） | W1 新增 pass 状态回调 topic 或复用 dr_vul_scan_task_status |

---

## 四、vul-pass 差距

| 能力 | 现状 | 差距 |
|------|------|------|
| biz_line/data_origin | PO/DO 已有字段，dispatch 流程**未赋值** | W1 OpenTaskOrchestrator 主动赋值 |
| ITaskClient Feign | **不存在** | W1 新建 |
| Kafka 监听 | 无 task-center 状态监听 | W1 新建 SubTaskStatusKafkaListener |
| writeVulInstLedger | 统一写 vul_inst_log_rela（混轨），有 3 个变体 | W2 拆分 appendOperRela / appendReportRela |
| transition 状态机 | TransitionEnum 静态规则表（完整且严谨），PassRoot.doVulTransition | **不改**，仅按 biz_line 分流 rela 写入 |
| handlerVulProcess | recycle → transition → writeVulInstLedger → 台账 → 回传 order | W2 按 biz_line 分流（OPEN 跳过台账和回传） |
| dispatch 链路 | 8 步校验 + loadSubTasks 负载均衡 + writeLedger | W2 ASSESS 增加调 task-center 下发分支 |
| VulStateEnum | 0/1/2/3/5/6/7/8/9/10（完整） | 不改，与 API 文档附录 A 一致 |

---

## 五、前端可复用资产

| 资产 | 位置 | 复用方式 |
|------|------|----------|
| AssetBlock | window.commonComponents.AssetBlock（50+ 引用） | 任务工作台漏洞展示 |
| Search | window.commonComponents.Search（20+ 引用） | 任务列表筛选 |
| s-table | 全局组件 | 任务/实例列表 |
| 路由结构 | router.config.js asyncRouterMap | 新增 /open-task/* 路由 |
| API 封装 | BaseHttpClient + ajaxInterface | 新建 api/open-task.js |
| 三级工单页面 | VulnManagePlat/SecurityVulnManage/ | 参考布局结构 |
| 图表组件 | BarChart/LineChart/PieChart | 并集可视化 |

---

## 六、任务矩阵修正

| 任务 | 原计划 | 修正后 |
|------|--------|--------|
| W1c-OAS-ADAPTER | 新建 VulPassInternalClient Feign | 修改现有 IVulPassScanTaskFeign + SvmpEngineAdapterImpl |
| W4-OAS-EXPORT | 新建 open_export 表 + Export 组装 | 复用现有 open_export + 替换 MockTaskExportAssembler 数据源 |
| W1b-PASS-ORCH | 复用 ITaskClient | 新建 ITaskClient（当前不存在） |
| W2-VTC-ADAPTER-LM | 实现 ScannerAdapter | 从零建接口，封装 MsgSendLM 逻辑（不重写） |
| W1a-VTC-KAFKA | 新建 Kafka 生产者 | 复用现有 dr_vul_scan_task_status topic，消息体增加 passTaskId/passSubTaskId 字段 |

---

## 七、vul-pass 核心调用链（代码确认）

### 7.1 任务下发链路

```
VulScanTaskUi.dispatch(VulTaskDispatchDTO)
 → VulScanTaskAppServiceImpl.dispatch()
   1. verifyDispatchRequest — 参数校验
   2. initTsk — 初始化任务DO
   3. loadOrder — 加载部侧工单参数（commandEvent.getVulCommonParams）
   4. loadEngHash — 校验安全资源设备
   5. verify2F — 2FA验证
   6. initParams — 初始化参数（资产/漏洞/弱口令数量）
   7. vulScanTaskRepository.save — 持久化主任务
   8. VulScanTaskSubDomainServiceImpl.dispatch()
      → loadParams — 加载资产/漏洞列表
      → loadSubTasks — 按astUnitNum拆分子任务 + 负载均衡分配设备
      → saveBatch(subTasks) — 持久化子任务
      → subTaskAssetHandle — 持久化子任务资产
      → loadSubTaskVulSystem — 持久化系统漏洞
      → loadSubTaskVulList — 持久化产品漏洞
      → getHistories — 持久化审批历史
      → writeLedger — 写台账日志
      → commandEvent.updateStatus — 更新指令状态
```

### 7.2 结果回收链路

```
VulScanTaskUi.recycle(file, params)
 → VulScanTaskAppServiceImpl.recycle()
   → parseRequest — 选择解析器（VulReportTypeEnum）
   → handlerReport(subTask, scanResult) — 报告解析 + 标准化
     → handlerInvestRawResult — 加工原始结果
     → handlerRawVulResult — 标准化系统漏洞
   → handlerVulProcess(subTask, vulResultList) — 生命周期处理
     → transitionV2 → PassRoot.doVulTransition — 状态跃迁
     → vulArchiveInstRepository.saveOrUpdateBatch — 持久化漏洞实例
     → writeVulInstLedger — 写漏洞实例-台账关系
     → resetOrderAct + refreshTaskStatus — 刷新任务/工单状态
```

### 7.3 状态跃迁规则（TransitionEnum）

| 阶段 | 跃迁类型 | 源状态 | 目标状态 |
|------|----------|--------|----------|
| 排查(1) | NEW_DISCOVERY | NONE | 初始发现(1) |
| 排查(1) | STILL_EXIST | 潜在预警(0) | 初始发现(1) |
| 验证(2) | EXISTENT | 初始发现(1) | 已验证误报(3) |
| 验证(2) | STILL_EXIST | 初始发现(1) | 已验证有效(2) |
| 修复(3) | EXISTENT/STILL_EXIST | 已验证有效(2) | 已修复(5) |
| 核验(4) | EXISTENT | 已修复(5) | 核验已修复(6) |
| 核验(4) | STILL_EXIST | 已修复(5) | 核验已修复(6) |

**W3 实例 API 的 transition 复用此规则**，按 verifyResult/remediateResult 映射跃迁类型。

---

## 八、vuln-task-center 核心调用链（代码确认）

### 8.1 任务下发链路

```
ScanTaskUi.add (first/half + second/half)
 → ScanTaskAppServiceImpl.saveFirstHalf — 建计划不下发
 → ScanTaskAppServiceImpl.saveSecondHalf — 创建survey + 下发mint
   → executeScanTask
     → QueueAppServiceImpl.sendToQueue → Redis ZSet(sendQueueZset)
     → Kafka(sendQueue) → Consumer.handleSendQueue
       → getNodeScannerMap — 负载均衡选节点
         优先 currentTaskCount=0 → 负载率最低 → scanRange 评分
       → setIpCountAndSend — IP超限拆分
       → send(classifyId路由)
         LM → msgSendLM.createTaskSendKafka
         AH → msgSendAH.createTaskSendKafka
         Nessus → msgSendNessus.createTaskSendKafka
         ...
       → saveScanSubTask — 保存子任务（surveyId/planId/sendParamsInfo）
```

### 8.2 结果回调链路

```
Kafka(vuln_scan_lm_result / vuln_scan_result_topic)
 → VulnScanAnalysis / VulnScanBySchedulerAnalysis.receive()
 → 更新 scan_sub_task.state + progress
 → VulnTaskListenerOther.sendKafkaToInformLifecycle()
   → Kafka(dr_vul_scan_task_status) — 通知任务完成
```

**W1 Kafka 回调修正**：复用 `dr_vul_scan_task_status` topic，消息体增加 `passTaskId` + `passSubTaskId` 字段。

## 九、修复核验（verify-fix）实现要点（v1.2 补充）

### 9.1 当前 open-api 现状

| 模块 | 现状 | W3 目标 |
|------|------|---------|
| InstanceDomainServiceImpl | Mock 本地改 stat + 延迟触发 VERIFY_FIX_SCAN | Feign vul-pass，不再本地改终态 |
| MockInstanceScanFollowUpService | 定时模拟外发 | 由 vul-pass notify 驱动真实回收 |
| ExportAssemblyDomainServiceImpl | 已支持 VERIFY_FIX_SCAN 组装 | 对接 vul-pass 真实扫描结果 |

### 9.2 vul-pass 待建能力

| 组件 | 职责 |
|------|------|
| `VerifyFixOrchestrator` | 解析 vulInfoID -> 资产 IP + scanner_vendor -> 创建 SINGLE 扫描任务 |
| `VerifyFixRecycleHandler` | 全量 recycle，仅匹配目标 vulInfoID 判定 6/7/10 |
| `OpenInstanceUi` verify-fix | internal API，受理返回 verifyFixJobId |

### 9.3 与部侧考核 recycle 复用

- 复用 `handlerReport` / `handlerVulProcess` / `transition` 框架。
- `procMethod=1060`，OPEN 专用 `scan_phase=3`。
- **不**走 `MergeService`（单 survey）。
