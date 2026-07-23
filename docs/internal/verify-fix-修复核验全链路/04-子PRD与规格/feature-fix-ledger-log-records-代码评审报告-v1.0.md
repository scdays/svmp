# feature/fix-ledger-log-records 分支代码评审报告

> **报告用途**：供人工评审分支改动，确认对原有功能的影响、新增代码质量与核心代码复用程度，通过后方可继续后续开发任务。  
> **分析范围**：`project_backend/svmp/vul-pass` 与 `project_frontend/asset/asset-newleak-manage` 两个独立 Git 仓库的 `feature/fix-ledger-log-records` 分支，包含从分支创建到 HEAD 的所有已提交改动，以及当前工作区未提交改动。  
> **版本**：v1.0  
> **日期**：2026-07-21

---

## 1. 概览

### 1.1 仓库与分支

| 工程 | 仓库路径 | 当前分支 | 基础分支 | 分支点 Commit | 分支时间 |
|---|---|---|---|---|---|
| 后端 | `project_backend/svmp/vul-pass` | `feature/fix-ledger-log-records` | `origin/develop` | `832665b1` | 2026-06-09 |
| 前端 | `project_frontend/asset/asset-newleak-manage` | `feature/fix-ledger-log-records` | `origin/developer` | `bb773bbe` | 2026-07-13 |

### 1.2 提交统计

| 工程 | 提交数 | 新增文件 | 修改文件 | 删除文件 | 新增行 | 删除行 |
|---|---|---|---|---|---|---|
| 后端 vul-pass | 6 | 112 | 23 | 0 | 13,107 | 118 |
| 前端 asset-newleak-manage | 12 | 55 | 41 | 0 | 8,041 | 1,218 |
| **合计** | **18** | **167** | **64** | **0** | **21,148** | **1,336** |

### 1.3 功能主题

| 主题 | 后端提交 | 前端提交 | 说明 |
|---|---|---|---|
| **修复核验闭环** | `4de41a3b`, `a791dcc2`, `8b845b0c`, `5a02a6bd` | `309502db`, `05c5797b`, `b7538e51`, `62421729`, `6f23ce6b` | 1028 门闸编排、sequential/parallel 下发、台账合规、主/子状态码拆分 |
| **任务下发预览归一** | `cbc78acc` | `21bfaa83` | 分批次/双厂商/扫描窗口预览统一 |
| **自动化处置** | `b2cca63c` | `fe19386a` | Redis 状态机、流程实例、全阶段 wave 推进、WS 静默推送 |
| **抽屉升全页** | — | `56309a09`, `056d7592`, `8e161bb9`, `abf85142`, `42dc7cd7` | 工单/任务管理从抽屉交互改为全页子页 |

---

## 2. 后端 `vul-pass` 对原有功能的修改及功能影响

### 2.1 原有功能修改清单

| 文件 | 修改点 | 影响说明 |
|---|---|---|
| `ApplicationStart.java` | 新增 `ComplianceProperties` 配置注入 | 低：启动类扩展 |
| `application.yml` | 新增 `vul.auto-dispose`、`compliance` 配置；**删除 Kafka 明文密码** | 中：配置变更需确认生产注入方式 |
| `VulScanTaskAppServiceImpl.java` | 重写 `getById/getOne/list/page`，注入 `enrichLifecycle`；`dispatch` 增加双厂商/确认令牌/跨级切批分支；新增 8 个自动化处置方法 | **高**：查询全链路附加生命周期数据；核心下发路径行为变更 |
| `VulScanTaskSubAppServiceImpl.java` | 新增回收方法；`initTask` 状态码改为 `MainTaskStatEnum`；`initRecycle` 增加 procMethod 保护 | **高**：状态码写入切换 |
| `VulScanTaskSubDomainServiceImpl.java` | `dispatch` 后调用流程实例；`recycle` 增加 sequential 派生修复核验；`handlerVulProcess` 增加 verify-fix 判定 | **高**：核心回收/稽核链路被新逻辑包裹 |
| `AbstractLedgerLog.java` | `logType` 优先取主任务 `procMethod` | **高**：台账外壳字段来源变更 |
| `TaskResultActionService.java` / `VerifyResultActionService.java` | `onlineAddrFileLoc` 合并 `portList` + 实例 `vulNetAddr` | **高**：台账存活地址集合变大 |
| `VulScanTaskStatEnum.java` | 新增状态码并标记 `@Deprecated` | **高**：旧枚举废弃 |
| `MainTaskStatEnum.java` / `SubTaskStatEnum.java` | 新增 | **高**：新状态码体系 |
| `VulScanTaskDO.java` / `VulScanTaskSubDO.java` / PO / DTO | 新增修复核验相关字段；`subDO.procMethod` 语义改为“实际手段” | **高**：字段语义变更 |
| `VulScanTaskUi.java` | 新增 `/auto-dispose/*` 8 个端点 | 低：纯扩展 |
| `vul_scan_task.groovy` / `vul_scan_task_sub.groovy` | 新增字段 | 中：schema 变更 |

### 2.2 行为变更（非纯新增）

| # | 变更 | 影响 |
|---|---|---|
| 1 | 台账 `logType` 优先取主任务 `procMethod` | 修复核验子任务实际手段为 1028/1022 时，台账外壳仍用 1060/1061 |
| 2 | 台账 `onlineAddrFileLoc` 合并实例 IP | 存活地址集合变大，影响合规统计与下游对账 |
| 3 | 任务查询全部附加生命周期推导 | 历史任务首次查询可能静默写库；列表页性能风险 |
| 4 | 子任务 `procMethod` 语义变为“实际手段” | 所有读取 `subTask.procMethod` 的旧逻辑可能误判 |
| 5 | 状态码写入从 `VulScanTaskStatEnum` 切换到 `MainTaskStatEnum`/`SubTaskStatEnum` | 数据库状态码值变化，下游/前端硬编码比较会出错 |
| 6 | `dispatch` 增加跨级切批 | 同一请求生成多个主任务，preview 与 dispatch 口径必须一致 |
| 7 | `recycle` 增加 sequential 模式 | 连通性检测后自动派生修复核验子任务，改变子任务生命周期 |

### 2.3 风险等级

| 风险 | 等级 | 说明 |
|---|---|---|
| 主/子状态码拆分与旧枚举废弃 | **高** | 历史数据、下游、前端可能仍依赖旧枚举 |
| `VulScanTaskAppServiceImpl` 查询方法全重写 | **高** | 性能与 DTO 内容变化 |
| `recycle` / `handlerVulProcess` 核心路径变更 | **高** | 原有回收/稽核链路被包裹 |
| `subDO.procMethod` 语义变更 | **高** | 旧消费者可能误判 |
| feature flag 默认开启 | **高** | 新逻辑直接作用于生产 |
| 台账 `onlineAddr` 合并规则变更 | 中 | 台账内容变化 |
| 跨级切批 | 中 | preview/dispatch 口径一致性 |
| 历史任务首次查询写库 | 中 | 首次批量查询风险 |
| Kafka 凭证删除 | 中 | 需确认生产注入方式 |

---

## 3. 前端 `asset-newleak-manage` 对原有功能的修改及功能影响

### 3.1 原有功能修改清单

| 文件 | 修改点 | 影响说明 |
|---|---|---|
| `src/App.vue` | `router-view :key` 改为 `buildStableRouteKey`，忽略 `_sub/_from/refresh` | **高**：全局组件生命周期与缓存 |
| `src/components/MultiTab/MultiTab.vue` | 页签同样使用稳定 key | **高**：多标签行为改变 |
| `src/config/router.config.js` | 8 个菜单 `component` 改为 `subpages/Entry.vue` | **高**：菜单入口整体替换 |
| 8 个列表页（`*Order.vue` / `*Task.vue`） | 行操作从抽屉改为全页子页；删除页内抽屉声明；混入 `createListSubPageMixin` | **高**：交互架构改变 |
| 各菜单 `module/*Drawer.vue` / `ReturnTest.vue` / `OrderResult.vue` | 改为 `pageMode` 双模式渲染 | 中：抽屉模式回归风险 |
| `TaskDrawer.vue` | 重大重构：新增 `viewMode`、主任务工作台、子任务卡片、自动化处置抽屉、新状态字典 | **高**：任务详情交互全变 |
| `TaskInfoDrawer.vue` / `SearchTask.vue` | 改为 `pageMode`/`embedded` 兼容 | 中 |
| `ProMethodDrawer.vue` | `reportType` 初始化改为基于 `source`/`ctxCode` 的策略 | **高**：默认上报类型可能变化 |
| `AddTaskDrawer.vue` / `BaseInfo.vue` / `SafeSourceDriver.vue` | 新增预览组件、确认禁用逻辑、双厂商选择 | 中：下发流程变更 |
| `ReturnHistory.vue` / `ReturnHistoryDrawer.vue` | 改为 `pageMode` 兼容；二级全页打开 | 中 |

### 3.2 行为变更（非纯新增）

| # | 变更 | 影响 |
|---|---|---|
| 1 | 行操作从抽屉变为全页 | 8 个菜单的所有详情/结果/历史入口交互改变 |
| 2 | 列表级「任务下发」入口消失 | `SysVulnOrder` / `ProVulnWarnTask` / `GangedTask` 列表页不再支持下发 |
| 3 | 返回行为改变 | 子页关闭不再 `$emit('close')`，而是通过 `_from` 回退 |
| 4 | 列表保活 | `display:none` 隐藏列表，返回时通过 `refresh=1` 触发 `table.refresh()` |
| 5 | 任务详情交互重构 | `TaskDrawer` 工作台取代嵌套抽屉 |
| 6 | `reportType` 默认策略变更 | 修复核验/扫描波次默认 `reportType` 按 `source` + `ctxCode` 计算 |
| 7 | `SearchTask` 删除条件「处置」按钮 | 可能影响原有使用路径 |

### 3.3 风险等级

| 风险 | 等级 | 说明 |
|---|---|---|
| 全局路由 key 与页签改造 | **高** | 影响整个子应用生命周期、缓存、后退、多标签 |
| 8 个菜单入口改为 `Entry.vue` | **高** | `createListEntry` 强依赖 `$refs.table.refresh()`，不一致会白屏 |
| `TaskDrawer.vue` 重构 | **高** | 任务详情 UI 与交互全变 |
| `ProMethodDrawer.vue` 的 `reportType` 策略 | **高** | 默认上报类型可能变化 |
| 列表级任务下发入口移除 | **高** | 业务可见行为变更 |
| 抽屉/全页双模式改造 | 中 | 面广但模式统一 |
| 下发前置校验 | 中 | 需验证各阶段下发流程 |
| `ProVulnUploadTask.returnTest` 空记录跳转 | 中 | 可能空数据 |
| `SearchTask` 删除处置按钮 | 中 | 需确认替代路径 |

---

## 4. 后端新增代码质量与核心代码复用评估

### 4.1 整体质量

| 维度 | 评级 | 说明 |
|---|---|---|
| DDD 分层 | 中上 | 未出现 Ui 直接注入 Mapper/PO，但 `VulScanTaskAppServiceImpl` / `VulScanTaskSubDomainServiceImpl` 严重膨胀 |
| 命名 | 中 | 类名/后缀基本合规，存在拼音 author 标签、无意义注释 |
| 异常处理 | 中下 | 多处空 catch / 仅 `e.getMessage()` |
| 日志 | 中 | 总体使用 SLF4J，部分异常未带堆栈 |
| 事务 | **差** | 核心状态机写操作未加 `@Transactional` |
| 并发 | 中下 | `InMemoryAutoDisposeLock` 过期判断非原子；token store 仅内存实现 |
| 测试覆盖 | 中 | 新增 20+ 单测，但核心状态机路径覆盖不足 |
| 安全风险 | 中 | `application.yml` 删除 Kafka 明文密码是正面改进；`LocalAutoDisposeReportFileStore` 有路径遍历防护 |

### 4.2 阻塞问题（必须修复）

| # | 问题 | 文件/位置 | 修复建议 |
|---|---|---|---|
| 1 | 完全限定名直接使用 | `VulScanTaskAppServiceImpl.java` 多处 | 改为 `import` |
| 2 | 空 catch | `VulScanTaskAppServiceImpl.java:412`、`VulScanTaskSubDomainServiceImpl.java:3610` 等 | 补日志或说明忽略原因 |
| 3 | `BytesMultipartFile` 与 `InMemoryMultipartFile` 重复 | `infra/repository/BytesMultipartFile.java` | 删除 `BytesMultipartFile`，复用 `InMemoryMultipartFile` |
| 4 | 包装类型用 `==` 比较业务值 | `PhaseDispatchPreviewBuilder.java:7507` | 改为 `Objects.equals` |
| 5 | 核心状态机写操作无事务 | `VerifyFixAutoDisposeOrchestrator`、`TaskFlowInstanceService`、`trySpawnRepairVerifyAfterConnectivity` | 加 `@Transactional(rollbackFor = Exception.class)` |

### 4.3 高优先级建议

| # | 问题 | 建议 |
|---|---|---|
| 1 | `VulScanTaskAppServiceImpl` / `VulScanTaskSubDomainServiceImpl` 过度膨胀 | 拆分为 `VerifyFixDispatchAppService`、`VerifyFixAutoDisposeAppService`、`VerifyFixRecycleDomainService` |
| 2 | 魔法字符串/数字散落 | 抽取为枚举：`AutoDisposeItemStatusEnum`、`AutoDisposePhaseEnum`、`WaveNameConstants` |
| 3 | 核心状态机测试覆盖不足 | 补充 online/offline 全路径、异常路径、暂停/继续、并发启动、token 过期等测试 |
| 4 | 多实例部署下内存 token/锁失效 | 为 `VerifyFixConfirmTokenStore` 补 Redis 实现；`InMemoryAutoDisposeLock.tryLock` 原子化 |
| 5 | 历史任务首次查询写库 | 评估是否需要异步回填或默认关闭 |
| 6 | `LocalAutoDisposeReportFileStore` 无条件注册 | 加 `@ConditionalOnProperty` 或补共享存储实现 |

### 4.4 复用评估

| 新增类 | 已有可复用类 | 结论 |
|---|---|---|
| `BytesMultipartFile` | `InMemoryMultipartFile` | **重复，立即合并** |
| `IAutoDisposeLock` + 实现 | `RedisString.setIfAbsent` | 可复用模式，建议统一 |
| `VerifyFixConfirmTokenStore` | `IVerifyFixAutoDisposeRunRepository` 双实现模式 | 应补 Redis 实现保持一致 |
| `LocalAutoDisposeReportFileStore` | `IFileServiceFeign`（file-sharing-center） | 多实例下应复用文件中心 |
| `TaskFlowInstanceService` | `VulTicketTaskDiagram`（COLA 状态机） | 面向不同聚合根，可保留；建议文档化为何不复用 COLA |

---

## 5. 前端新增代码质量与核心代码复用评估

### 5.1 整体质量

| 维度 | 评级 | 说明 |
|---|---|---|
| 架构分层 | 中上 | `?_sub` 路由、`drawerPageMode`、`SubPageLayout` 抽象合理 |
| 组件拆分 | 中下 | `AutoDisposeDrawer.vue` 1562 行、`TaskDrawer.vue` 职责过重 |
| 状态管理 | 中 | `sessionStorage` 传递子页数据，已知刷新丢失约束 |
| 复用性 | 中下 | 子页模板、`drawerBind`、`formatVulStat` 大量重复 |
| 可读性 | 中 | 命名规范，但残留 `console.log`、`v-if="false"`、死代码 |
| 性能 | 中 | 保活策略正确；`vulPlatFormatters.setdstVulInfoStatCnt` 使用 `find` 效率低 |
| 常量管理 | 中上 | 新增 `taskStatDict.js`、`reportTypeAssign.js` 职责清晰 |

### 5.2 阻塞问题（必须修复）

| # | 问题 | 文件/位置 | 修复建议 |
|---|---|---|---|
| 1 | `console.log` 调试语句 | `SysVulnOrder/module/DetailsDrawer.vue:134`、`GangedTask/module/DetailsDrawer.vue:138`、`ProVulnWarnTask/module/DetailsDrawer.vue:121` | 删除 |
| 2 | `setdstVulInfoStatCnt` 未统一且性能差 | `utils/vulPlatFormatters.js`、`SysVulnOrder.vue:488`、`GangedTask.vue:481`、`ProVulnWarnTask.vue:377` | 统一使用新 util，改用 Map 索引 |
| 3 | `v-if="false"` 死代码 | `components/TaskSend/AddTaskDrawer.vue:34` | 删除或恢复为配置项 |
| 4 | 分支范围蔓延 | `AutoDisposeDrawer` / `TaskSend v2.0` 相关改动 | 拆出独立分支/PR |

### 5.3 高优先级建议

| # | 问题 | 建议 |
|---|---|---|
| 1 | `formatVulStat` 在 15+ 子页重复 | 下沉到 `subPageMixin.js` 统一注入 |
| 2 | `drawerBind` / `wrapperTag` 在每个 Drawer 重复 | 扩展 `drawerPageMode.js`，通过 props 配置 title/width |
| 3 | `embedded` 覆盖 mixin | 把 `embedded` prop 加入 `drawerPageMode.js` |
| 4 | 子页模板大量重复 | 提供 `createDetailPage(component, title, extraProps)` 工厂 |
| 5 | `ResultSummaryPanel` 与 `TaskResultContent` 重复 | 合并为一个可配置组件 |
| 6 | 框架文件反向引用业务模块工具 | `App.vue` / `MultiTab.vue` 引用 `views/VulnManagePlat/utils/stableRouteKey.js` | 上提到 `src/utils/` |
| 7 | `autoDisposeSilentPush.js` 200ms 轮询 WebSocket | 改为事件监听 |
| 8 | `AutoDisposeDrawer.vue` / `TaskDrawer.vue` 单文件过大 | 拆分子组件 |

### 5.4 复用评估

| 维度 | 复用情况 | 评价 |
|---|---|---|
| `SetName` / `STable` / `SearchWrap` / `ajaxInterface` | 已正确复用 | 好 |
| 子页路由/导航/保活 | 本次新建，无历史同类抽象 | 可接受 |
| 抽屉→全页 wrapper | 本次新建 `drawerPageMode.js` | 可接受 |
| 子页模板/抽屉 wrapper 绑定 | 大量复制粘贴 | **差** |
| 任务状态字典 | 新建 `taskStatDict.js`，列表页未切换 | **差** |
| 自动化处置 / 任务下发 v2.0 | 与“抽屉升全页”无关，属于夹带私货 | **差** |

---

## 6. 总体结论

### 6.1 是否影响原有功能

**明确结论：影响。**

后端和前端均存在大量非纯新增的行为变更，核心影响点：

1. **后端状态机**：主/子任务状态码拆分并切换写库路径，旧枚举废弃。
2. **后端台账**：`logType` 来源与 `onlineAddrFileLoc` 合并规则改变。
3. **后端查询**：所有任务查询附加生命周期推导，历史任务可能静默写库。
4. **后端下发/回收**：`dispatch` 增加跨级切批，`recycle` 增加 sequential 派生修复核验。
5. **前端交互**：8 个菜单从抽屉改为全页子页，`TaskDrawer` 重构为工作台。
6. **前端下发**：列表级任务下发入口移除，`reportType` 默认策略变更。

### 6.2 新增代码质量

- **功能目标达成度高**，编译与现有测试均通过。
- **工程债务显著**：事务缺失、多实例内存状态、Service 类过度膨胀、魔法字符串、前后端均有重复代码和死代码。
- **核心复用不足**：后端 `BytesMultipartFile` 重复；前端子页模板/`drawerBind`/`formatVulStat` 大量重复；分支混入自动化处置/任务下发 v2.0 等独立需求，违反最小 diff 原则。

### 6.3 是否可继续后续开发

**建议：在阻塞项修复并经人工回归验证前，不宜继续在该分支叠加新功能。**

原因：当前分支已经承担过多主题（修复核验、自动化处置、预览归一、抽屉升全页），继续开发会进一步加剧范围蔓延和回归风险。

---

## 7. 阻塞项清单（必须修复/确认）

### 后端

| # | 事项 | 验收标准 |
|---|---|---|
| 1 | 完全限定名改为 import | 编译通过，无新增完全限定名 |
| 2 | 空 catch 补日志或说明 | 所有新增 catch 块均有日志或明确注释 |
| 3 | 删除 `BytesMultipartFile`，复用 `InMemoryMultipartFile` | 删除文件，引用替换，编译通过 |
| 4 | `PhaseDispatchPreviewBuilder` 包装类型比较改为 `Objects.equals` | 编译通过 |
| 5 | 核心状态机/流程实例/子任务派生写操作加事务 | 单测覆盖跨 Repository 写失败回滚 |
| 6 | `compliance.verify-fix-strategy-enabled`、`vul.auto-dispose.async-enabled` 默认关闭或确认生产已就绪 | 配置默认 `false`，通过 Nacos 灰度开启 |
| 7 | 确认 Kafka 凭证删除后生产注入方式 | 运维确认 Nacos/环境变量/K8s secret 已配置 |

### 前端

| # | 事项 | 验收标准 |
|---|---|---|
| 1 | 删除所有新增 `console.log` | 全局搜索无新增 console.log |
| 2 | 统一 `setdstVulInfoStatCnt` 实现并优化性能 | 列表页使用 `vulPlatFormatters.js`，改为 Map 索引 |
| 3 | 删除 `v-if="false"` 死代码 | 编译运行无残留 |
| 4 | 拆分自动化处置 / 任务下发 v2.0 到独立分支 | 本分支仅保留抽屉升全页相关改动 |
| 5 | `formatVulStat` 下沉到 mixin | 子页不再重复声明 |
| 6 | `drawerBind` / `wrapperTag` 下沉到 `drawerPageMode.js` | 各 Drawer 组件不再重复 |

---

## 8. 回归验证清单（建议人工逐项验证）

### 后端

1. 旧任务（状态 0/1/2/3）在列表/详情显示正确。
2. 新任务状态 10/20/30... 在前端/下游正确映射。
3. 台账 `logType` / `onlineAddrFileLoc` 抽样对账。
4. 跨级切批 preview 与 dispatch 口径一致。
5. 非修复核验任务回收/稽核仍按旧状态机结束。
6. sequential 修复核验：连通性检测后正确派生修复核验子任务。
7. 历史任务首次查询是否静默写库、性能是否可接受。
8. `subTask.getProcMethod()` 所有调用点确认无误判。

### 前端

1. 8 个菜单直接点击、F5 刷新、带 `?_sub=Detail` 刷新正常。
2. 子页返回后 `$refs.table.refresh()` 正确触发。
3. 二级子页返回链路（详情 → 任务详情 → 任务结果 → 返回）。
4. `TaskDrawer` 重构后任务结果/台账/追踪链路可用。
5. `ProMethodDrawer` 各类 `procMethod` 默认 `reportType` 与旧逻辑一致。
6. `AddTaskDrawer` 无设备/双厂商未选/计划不可确认时禁用下发。
7. `SearchTask` 删除处置按钮后的替代路径确认。
8. `ProVulnUploadTask` 回传测试空记录跳转正常。

---

## 9. 后续开发建议

1. **严格执行最小 diff / YAGNI**：一个分支只承载一个主题，避免修复核验、自动化处置、抽屉升全页混在一个分支。
2. **复用优先**：
   - 后端：优先使用既有 `InMemoryMultipartFile`、COLA 状态机、文件中心 Feign。
   - 前端：优先使用既有公共组件、mixin、utils，子页模板工厂化。
3. **拆大 Service**：后端 `VulScanTaskAppServiceImpl` / `VulScanTaskSubDomainServiceImpl` 超过 800 行新增必须拆分。
4. **事务与并发**：所有跨 Repository 写操作必须加事务；多实例状态必须走 Redis。
5. **核心路径必须有单测**：状态机、流程推进、子任务派生等必须覆盖正常/异常/并发路径。
6. **文档先行**：后续新增能力必须先在 PRD 中明确状态机、契约、数据模型，再写代码。

---

## 10. 附录：分析 Agent 输出索引

| Agent | 任务 | 输出文件 |
|---|---|---|
| `a651dd3af30f9e863` | 提交历史与改动清单 | `tasks/a651dd3af30f9e863.output` |
| `a6a2d08e484ce2196` | 后端功能影响分析 | `tasks/a6a2d08e484ce2196.output` |
| `a235e944691a4cad1` | 前端功能影响分析 | `tasks/a235e944691a4cad1.output` |
| `acde5bc79cf5b60e6` | 后端代码质量与复用 | `tasks/acde5bc79cf5b60e6.output` |
| `afaee49a2f82b4955` | 前端代码质量与复用 | `tasks/afaee49a2f82b4955.output` |
