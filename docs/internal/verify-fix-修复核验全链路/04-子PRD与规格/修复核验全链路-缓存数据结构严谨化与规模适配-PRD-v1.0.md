# 修复核验全链路 - 缓存数据结构严谨化与规模适配 PRD v1.0

> **范围**：修复核验预览方案缓存（CachedPlan）的数据结构严谨化、零静默降级、规模适配。
> **对应权威文档**：
> - 需求基线：[修复核验全链路-vul-pass-PRD.md](修复核验全链路-vul-pass-PRD.md) v2.0.0 §5.2
> - 技术设计：[修复核验全链路-缓存一致性与设备分配技术设计-v1.0.md](修复核验全链路-缓存一致性与设备分配技术设计-v1.0.md)（本 PRD 细化/收严其 §5.9 降级策略、§10.2 风险、§12 待确认点 Q5/Q6/Q7）
> - 字段说明：[../../08-工具与指南/修复核验预览方案缓存字段说明.md](../../08-工具与指南/修复核验预览方案缓存字段说明.md)（本 PRD 处置其附录 A 死字段）
> **对应开发计划**：[修复核验全链路-缓存数据结构严谨化与规模适配-开发计划-v1.0.md](修复核验全链路-缓存数据结构严谨化与规模适配-开发计划-v1.0.md)
> **日期**：2026-07-24
> **状态**：待评审
> **工程边界**：后端 `project_backend/svmp/vul-pass` + 前端 `project_frontend/asset/asset-newleak-manage`，分支 `feature/fix-ledger-log-records`

---

## 1. 背景与目标

### 1.1 背景

修复核验预览方案缓存（CachedPlan）已实现"预览-确认"原子消费链路（v1.0 技术设计 R11~R14）。在缓存数据结构复盘（`_archive/3.21 Wave R（07-22）` 样例 + 字段说明文档）中，发现以下问题：

1. **静默降级路径**：子任务物化阶段 `filterAssetsByIps` 过滤为空时走 `syntheticAssetsFromIps` 造 IP 空壳，子任务资产范围悄悄丢资产 ID/端口，用户无感。
2. **漏洞范围精度丢失**：确认落库时子任务 `vulInstList` 继承订单级全量（构造器拷贝），核验判定时 `ScanResultStageSlicer` 仅按 IP 切片，同 IP 跨 srcMethod 混切，与预览中精确的 `group.instanceIds` 不符。
3. **计数错误**：子任务 `vulNum/prcVulNum` 继承订单级，非组级；`targetScale` 为拼接字符串，与结构化字段双源。
4. **死字段**：`aliveInstanceIds/deadInstanceIds/forcedEngHashes/srcMethod105X` 等只写不读，强制设备池等约束形同虚设。
5. **规模风险**：部侧下发工单资产 IP 可达几万、资产 ID 20万不止；`astUnitNum` 默认 -1（不限制）时全量进单组，单组 `assetIps`/`instanceIds` 体积巨大。

### 1.2 目标

| 目标 | 说明 |
|------|------|
| 零静默降级 | 任何参数不一致/缺失必须**拦截 + 用户可感知提示**，禁止兜底降级（部侧下发严谨底线） |
| 预览即下发 | 预览呈现的资产/漏洞/设备范围 == 确认后实际下发的范围，全链路无损 |
| 规模适配 | 几万 IP / 20万+ 资产 ID 的部侧大单可正常预览与下发，缓存与响应体可控 |
| 数据结构收敛 | 消除死字段与双源，结构化计数替代拼接字符串 |
| 有效性窗口 | 确认时轻量复核快照仍成立，防止 30min 窗口内数据漂移导致按过期快照下发 |

### 1.3 非目标

- 不重做缓存基础设施（token/锁/幂等/Repository，v1.0 已实现，仅收严配置）。
- 不复活 `dependsOnGroupIndex` 依赖消费链（已 @deprecated，见 R-4）。
- 不缓存 `lifecycleSteps`（派生视图，见 R-5）。

---

## 2. 核心设计决策

### 2.1 引用 + 强校验 + 失败即拦截（不复制全量数据）

> **决策**：重数据（`previewContext.assetList`、`previewContext.vulInstSnapshots`）**只存一份于订单级**；group 仅持**轻量引用**（`assetIps`、`instanceIds`）+ **结构化计数**。预览构建期对引用做强校验，确认期按引用精确物化，**任何不一致即拦截 + 提示**。

**否决"组内预拆全量数据"方案的理由（规模）**：

- `IpBatchSharder.shardIps`：`astUnitNum <= 0` 时 `max = Integer.MAX_VALUE`，**全量 IP 进同一批**。部侧默认 `astUnitNum = -1`（"以上级平台为准"，不限制），故几万 IP 的大单 = **1 个连通性组 + 若干核验组**，单组即承载几万 IP / 20万+ 实例。
- 若按"组内预拆 assetList/snapshots"复制，单组重数据即 4MB+（assetInfo 串）× wave 数翻倍，缓存值与预览响应体双双爆炸（v1.0 设计 §10.2 已定"只存实例 ID，不存完整 DTO"）。
- 引用模型下，group 仅多持 `assetIps`（IP 串，几万 × ~15B ≈ 几百 KB）与 `instanceIds`（已有，strip 后响应不回传），重数据零复制。

> **与原"建议1/建议2"的关系**：用户原始建议是"预览时把 assetList/vulInstSnapshots 按子任务拆好放入 group"。经规模分析，**不采纳组内复制**，改用等价的"引用 + 强校验 + 精确物化"达成相同目标（预览=下发、可展示子任务范围），且不引入规模风险。

### 2.2 零静默降级原则

全链路所有 `fallback / synth / default / derive` 路径逐一审计，统一改造为"校验失败即抛业务异常 + 用户可感知提示"。已识别降级点见 R-6。

### 2.3 严谨化优先于性能

部侧下发工单/任务必须严谨。确认时轻量复核（R-7）增加少量查询延迟，可接受；缓存体积护栏（R-8）可能拒绝超大单预览，可接受（优于静默截断/超时）。

---

## 3. 需求条目

> 代码点引用约定同字段说明文档：`类:行`，类位于 `project_backend/svmp/vul-pass/src/main/java/com/vtc/security/`。缩写：VTDSI=VulScanTaskDomainServiceImpl，VTSUB=VulScanTaskSubDomainServiceImpl，VFD=VerifyFixDispatchPlanner，SRSL=ScanResultStageSlicer，DPA=DispatchPlanAssembler，RDCR=RedisDispatchPlanCacheRepository。

### R-1 资产范围严谨化（对应建议 1+3）

| 项 | 内容 |
|---|---|
| 问题 | `VTSUB.buildSubTaskFromPlanGroup:3372-3375` 按 `group.assetIps` 过滤 `task.assetList`，过滤为空走 `syntheticAssetsFromIps` 造 IP 空壳（丢资产 ID/端口），静默降级。 |
| 决策 | ① 删除 `syntheticAssetsFromIps` 兜底；`filterAssetsByIps` 结果为空 -> 抛 `DispatchPlanIntegrityException` + 提示"子任务[{groupKey}]资产范围与工单资产快照不一致，请重新预览"。② 预览构建期强校验：每个 `group.assetIps` ⊆ `previewContext.assetList` 的 IP 集合，不符即拒绝预览（不写缓存）。③ `group.assetIps` 维持组级资产 IP 权威引用（轻量，保留）；`previewContext.assetList` 维持订单级全量（存一份）。④ **不采纳组内预拆 assetList**。 |
| 代码点 | VTSUB:3372-3375（删兜底）；新增 `DispatchPlanIntegrityValidator`（预览校验）；VTDSI.saveDispatchPlanToCache 前调用。 |
| 验收 | 构造 group.assetIps 含 assetList 外 IP -> 预览即报错不缓存；过滤空 -> 下发即报错不造空壳；正常路径资产 ID/端口完整落库。 |

### R-2 漏洞范围严谨化（对应建议 2）

| 项 | 内容 |
|---|---|
| 问题 | ① `VulScanTaskSubDO(task)` 构造器:306 把订单级全量 `vulInstList` 拷给每个子任务，`buildSubTaskFromPlanGroup` 不按 `group.instanceIds` 收窄。② 核验判定 `SRSL.sliceInstances:34-48` 仅按 IP 切片，同 IP 跨 srcMethod 混切（批1 的 1050 组与 1051 组 IP 相同，切出相同 21 实例，而非精确的 9/12）。 |
| 决策 | ① `buildSubTaskFromPlanGroup` 按 `group.instanceIds` 精确收窄 `subTask.vulInstList`（替代构造器全量继承）。② `SRSL.sliceInstances`/`slicePorts` 改以 `subTask` 精确实例集合为准（而非 IP-only 推导）。③ 预览构建期强校验：`group.instanceIds` ⊆ `previewContext.vulInstSnapshots` 的 ID 集合；同 wave 内实例无丢失、无跨批重复（Σ `group.instanceCount` == 该 wave 应覆盖实例数）。④ **不采纳组内预拆快照**。 |
| 代码点 | VTSUB:3287-3382（buildSubTaskFromPlanGroup 收窄）；VTSUB 构造器:306（评估是否取消 vulInstList 继承）；SRSL:29-48；`DispatchPlanIntegrityValidator`。 |
| 验收 | 核验判定实例集 == 预览 group.instanceIds；同 IP 不同 srcMethod 组判定集互斥；instanceIds 含快照外 ID -> 预览报错。 |

### R-3 targetScale 拆分与计数正确性（对应建议 4）

| 项 | 内容 |
|---|---|
| 问题 | ① `targetScale` 拼接字符串"资产IP x / 排查资产 y / 系统漏洞 z"与结构化字段双源。② 子任务 `vulNum/prcVulNum` 继承订单级（构造器:300,304），非组级。③ 系统漏洞实例数无 DB 列。④ 快照缺 `vulId`，组级去重漏洞数不可算。 |
| 决策 | ① group 增结构化字段：`assetCount`（按组 IP 从 assetList assetInfo 去重计数）、`vulInstCount`（统一 `instanceCount` 命名/语义）、`uniqueIpCount`（已有）、`vulNum`（组级去重漏洞数）。② **移除 `targetScale` 字符串**，前端由结构化字段组合展示（消除双源）。③ 落库纠正：`subTask.vulNum/prcVulNum` 按组写入。④ `vulInstSnapshots` 补 `vulId` 字段（`buildVulInstSnapshots`/`convertVulInstSnapshots` 双向改）。⑤ 系统漏洞实例数：**决策项 D-1**（新增 `vul_inst_num` 列 vs 仅缓存/展示层持有）。 |
| 代码点 | VTDSI:471-491,375-401（快照补 vulId）；VFD group 构建处（结构化计数）；VTSUB:300,304（vulNum 按组）；DPA + 前端 DispatchPlanPreview（展示）。 |
| 验收 | group 结构化计数与 assetList/instanceIds 一致；subTask.vulNum == 组级去重漏洞数（非订单级）；前端展示无字符串双源。 |

### R-4 依赖/解锁维持现状（对应建议 5，经分析抉择不改）

| 项 | 内容 |
|---|---|
| 分析 | ① `astUnitNum=-1`（部侧默认）-> 单批 -> "每批依赖"自然成立（单批即全依赖 == 当前 `dependsOnGroupIndex=0` 语义）。② `astUnitNum>0` 多批 + `sequential` 模式：`trySpawnRepairVerifyAfterConnectivity` 在连通性回收后派生核验子任务，已实现批次级。③ 依赖机制已由 `summary.dispatchMode`（sequential/parallel）表达；`dependsOnGroupIndex` 已 **@deprecated（v2 起子任务无业务依赖，执行态不消费）**（字段说明附录 A + DispatchPlanGroup 注释）。 |
| 决策 | **维持现状不改**，不复活 `dependsOnGroupIndex` 消费链（与 v2 废弃决策一致，避免再造死字段）。已知限制：`parallel + 多批` 场景为波级门禁（非批次级），列为已知约束，未来需要再单独立项。预览 `summary` 显式标注当前依赖模式 + 批次数，让用户感知。 |
| 验收 | summary 标注 dispatchMode + batchCount；文档固化"parallel+多批=波级门禁"已知限制。 |

### R-5 lifecycleSteps 不缓存（对应建议 6）

| 项 | 内容 |
|---|---|
| 决策 | 维持现状不缓存。`lifecycleSteps` 为 `TaskLifecycleResolver` 每次请求从 `PhaseSubTaskChainTemplate`（静态模板）+ 任务实时状态派生的视图；预览全 PENDING 供展示，任务详情实时状态。预览=执行的不变量由**同源模板**保证，非缓存。确认时 `TaskFlowInstanceService` 亦从模板重建，不读预览响应。 |
| 验收 | 文档固化决策；lifecycleSteps 不进入 CachedPlan。 |

### R-6 零静默降级审计与改造（用户核心约束）

> **约束**：部侧下发的工单和任务，任何参数不确定性都必须让用户感知并拦截提醒，**禁止静默降级**。

逐一处置已识别降级点：

| 降级点 | 现状 | 改造 |
|---|---|---|
| `syntheticAssetsFromIps` | 过滤空造 IP 空壳 | R-1 删除，改抛异常 |
| `subTask.vulInstList` 订单级继承 | 全量拷贝 | R-2 按 instanceIds 收窄 |
| `subTask.vulNum/prcVulNum` 订单级继承 | 错误计数 | R-3 按组写入 |
| `SRSL.sliceInstances/slicePorts` IP-only | 粗切 | R-2 按精确集合 |
| `defaultEngHash` blankToDefault 兜底（PDPB:167,269,508） | 未匹配静默选默认 | **审计**：设备未匹配应 `allDevicesMatched=false` 拦截下发，不应静默兜底（除非用户显式选默认）。改为兜底前校验 `deviceRequired && !deviceMatched` -> 拦截 |
| `forcedEngHashes` write-only | 强制设备池未消费 | **接入或移除**（D-2）：接入则候选池必须经 forcedEngHashes 过滤且空交集即拦截；移除则删字段 |
| `dispatchAttemptCount` 无阈值 | 重试无界 | 接入 `maxDispatchAttempts`（v1.0 §5.8 设计=3），超限删 key + 提示重新预览 |
| 缓存 schema 兼容 fallback | 旧字段缺失静默走旧逻辑 | R-6.1 schemaVersion fail-loud |

**R-6.1 缓存 schemaVersion**：`CachedPlan` 增 `schemaVersion` 字段；确认时校验版本，不符 -> 拒绝 + "预览方案版本已升级，请重新预览"（替代静默兼容 fallback，发布期在途 token 30min 内自然失效）。

### R-7 有效性窗口确认时轻量复核（部侧严谨）

| 项 | 内容 |
|---|---|
| 问题 | 确认侧只校验 token/owner/checksum/状态，信任 30min 前快照；窗口内实例 stat/设备可用性可能变化。checksum 仅保证"缓存未被篡改"，不保证"现实未变化"。 |
| 决策 | 确认时增加**轻量复核**（不重载全量）：① 实例仍存在且 stat 仍在预期集合（或实例数一致）。② 用户分配设备仍在线（status=0）且仍在候选池。复核不过 -> 拦截 + "预览后数据已变化（实例/设备状态变更），请重新预览"。 |
| 权衡 | 复核增加少量查询延迟，部侧严谨优先，可接受。实现可选计数校验（不逐条）降低开销。 |
| 代码点 | VTDSI.dispatchWithCachedPlan（校验后、消费前插入复核）。 |
| 验收 | 窗口内实例 stat 变更 -> 下发拦截 + 提示；设备离线 -> 下发拦截 + 提示。 |

### R-8 规模护栏（用户规模提醒）

| 项 | 内容 |
|---|---|
| 背景 | 部侧大单：资产 IP 几万、资产 ID 20万不止；`astUnitNum=-1` 全量进单组。 |
| 决策 | ① **缓存体积护栏**：预览构建期序列化后超阈值（默认 16MB，`vul.dispatch-plan-cache.maxCacheBytes` 可配） -> 拒绝预览 + "工单规模超限，请联系管理员缩减范围或分单"，避免 Redis 大 key + 响应超时。② **前端响应护栏**：预览响应已 strip instanceIds；单组 `assetIps` 超阈值（如 > 5000 IP）时只回传计数，IP 明细按需分页拉取（**决策项 D-3**）。③ **astUnitNum=-1 单组超大**：评估预览页组内 IP 分页展示（前端，D-3）。 |
| 验收 | 构造超大单 -> 预览拒绝 + 明确提示（不超时/不截断）；阈值可配。 |

### R-9 tokenSecret 部署严谨

| 项 | 内容 |
|---|---|
| 问题 | `vul.dispatch-plan-cache.tokenSecret` 未配置时启动随机生成；多实例/重启后所有在途 token 验签静默失败。 |
| 决策 | 未配置 + 多实例/集群部署 -> **启动 fail-fast**；单实例开发允许显式 escape 但启动告警。消除跨实例验签静默失败。 |
| 验收 | 集群模式未配 tokenSecret 启动失败；配置后跨实例验签一致。 |

### R-10 死字段清理（字段说明附录 A）

| 字段 | 处置 |
|---|---|
| `aliveInstanceIds`/`deadInstanceIds` | 删除（零读写） |
| `evidenceCapabilities`（group 层） | 接入消费或删除（D-4） |
| `srcMethod105X`（summary） | 接入消费或删除（D-4） |
| `forcedEngHashes` | 见 R-6（接入或移除，D-2） |
| `dispatchAttemptCount` | 见 R-6（接入阈值） |
| `source`/`orderProcMethod` | 评估接入或删除 |

---

## 4. 待决策项

| 编号 | 决策点 | 选项 | 倾向 |
|---|---|---|---|
| D-1 | 系统漏洞实例数存储 | a) 新增 `vul_scan_task_sub.vul_inst_num` 列；b) 仅缓存/展示层持有 | a（便于后续台账/统计，与 astNum 同级） |
| D-2 | forcedEngHashes | a) 接入候选池过滤 + 空交集拦截；b) 移除字段 | a（强制设备池是部侧约束，应生效） |
| D-3 | 超大组 IP 展示 | a) 前端组内 IP 分页 + 按需拉取；b) 仅展示计数 | a（保留可查性，b 作降级展示） |
| D-4 | evidenceCapabilities / srcMethod105X | a) 接入消费；b) 删除 | 评审定（倾向删除冗余，除非有消费方） |

---

## 5. 与现有文档的关系

| 现有文档 | 本 PRD 关系 |
|---|---|
| 缓存一致性技术设计 v1.0 §5.9 降级策略 | 收严：所有"降级"改为"拦截 + 提示"，Redis 不可用仍拒绝（保留） |
| 缓存一致性技术设计 v1.0 §10.2 风险"plan 数据过大" | 细化：引用模型 + 体积护栏（R-8），重申"只存 ID 不存 DTO" |
| 缓存一致性技术设计 v1.0 §12 待确认点 | 解答 Q5（不压缩，用体积护栏）、Q6（快照存关键字段+vulId）、Q7（assetList 存订单级全量，组级用引用） |
| 缓存字段说明 附录 A 死字段 | 本 PRD R-10 逐项处置 |
| PRD v2.0.0 §5.2 预览=下发 | 本 PRD 是其"数据结构严谨化"的具体落地 |

---

## 6. 验收标准

1. **零静默降级**：R-6 所有降级点改造后，构造异常输入均触发拦截 + 用户提示，无任何兜底静默路径。
2. **预览即下发**：资产 ID/端口、漏洞实例集、设备 hash 在预览与落库/判定全链路一致（R-1/R-2）。
3. **计数正确**：subTask.vulNum/prcVulNum/astNum 为组级精确值（R-3）。
4. **规模可控**：几万 IP / 20万+ 资产 ID 大单预览不超时/不截断，超阈值拒绝 + 提示（R-8）。
5. **有效性窗口**：窗口内 stat/设备变化触发确认拦截（R-7）。
6. **部署严谨**：集群未配 tokenSecret 启动失败（R-9）。
7. **死字段清零**：附录 A 字段全部接入消费或删除（R-10）。
8. **测试**：新增 `DispatchPlanIntegrityValidatorTest`、`ScanResultStageSlicerPrecisionTest`、规模护栏/确认复核集成测试；全量 `mvn test` 通过。

---

## 7. 评审待确认

- D-1~D-4 决策项定向。
- R-7 确认复核的查询开销是否可接受（是否计数校验）。
- R-8 缓存体积阈值默认值（16MB）与前端 IP 分页阈值（5000）是否合理。
- 本波是否独立分支（如 `feature/cache-data-rigor`）还是续用 `feature/fix-ledger-log-records`。

请评审；确认后进入开发计划执行。
