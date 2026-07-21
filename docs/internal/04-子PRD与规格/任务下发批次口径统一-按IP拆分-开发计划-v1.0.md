# 任务下发批次口径统一 - 按 IP 拆分 - 开发计划 v1.0

> 范围：`/vul-pass/vul-scan-task/pre/dispatch` 预览 + 跨级联动下发 `dispatchGangedBatches` + `VerifyFixDispatchPlanner` 批次标号 + 前端 `DispatchPlanPreview.vue` 批次列
> 目标：(1) `ast_unit_num` 统一按**资产 IP 维度**拆分（阶段0-3 与阶段4 一致）；(2) 跨级联动预览页批次列对所有阶段（含 1060）显示并按批次排序
> 原则：YAGNI、最小 diff、改根因、零功能回归；复用已实现的 `shardByAstUnit` IP 分批能力，不重复造轮子
> 前置：v2.0 预览归一（dispatchPlan）+ WaveI 处置类型策略已合入

---

## 一、现状根因（两个确认问题）

### 问题1：ast_unit_num 拆分维度不一致

| 阶段 | 拆分方法 | 维度 | 是否按 IP |
|------|---------|------|----------|
| 阶段4（1060） | `VerifyFixDispatchPlanner.shardByAstUnit`（[:314-339](project_backend/svmp/vul-pass/src/main/java/com/vtc/security/domain/pass/service/verify/VerifyFixDispatchPlanner.java#L314)） | 按 IP：`Map byIp` 按 `vulNetAddr` 分组，每 astUnitNum 个 IP 切一批 | ✅ |
| 阶段0-3 | `AssetBatchSplitter.split`（[:60-75](project_backend/svmp/vul-pass/src/main/java/com/vtc/security/domain/pass/service/dispatch/AssetBatchSplitter.java#L60)） | 按资产数量：类注释"按资产数量切批"，用 `astTotal` 数字按序号切 | ❌ |

**下发链路同理**：`dispatchGangedBatches`（[:481-482](project_backend/svmp/vul-pass/src/main/java/com/vtc/security/app/service/impl/VulScanTaskAppServiceImpl.java#L481)）用 `AssetBatchSplitter.splitList(allAssets, true, astUnitNum)` 按资产条数切，不按 IP。

### 问题2：1060 批次列缺失

- `VerifyFixPlanGroup` **无 `batchIndex`/`batchLabel` 字段**（Grep 零匹配）
- `VerifyFixDispatchPlanner` 产出的 gate/scan group 不带批次信息
- `DispatchPlanAssembler.fromVerifyFixPlan` 算 batchCount：`subTasks.map(batchIndex).filter(>0).distinct().count()` -> 全 null -> **batchCount=1**
- 前端 `showBatchCol = batchCount > 1` = false -> 批次列不显示

### 阶段4 批次标号难点

`planInternal`（[:98-175](project_backend/svmp/vul-pass/src/main/java/com/vtc/security/domain/pass/service/verify/VerifyFixDispatchPlanner.java#L98)）：
- **gate**：`shardByAstUnit(instances, astUnitNum)` 全局按 IP 切 N 批，每批一个 gate group
- **scan**：每个 bucket（strategyClass）各自 `shardByAstUnit(bucket.instances, astUnitNum)` 切，**per-bucket 分批，与 gate 的批次划分不一致**

所以 scan group 不能直接用 shard 序号作为 batchIndex（会和 gate 批次错位）。

---

## 二、统一设计

### 2.1 批次定义（治本）

**批次 = 按全局唯一 IP 列表 + astUnitNum 切分，每 astUnitNum 个 IP 一批，同 IP 不拆散。**

- 阶段0-3：用**资产 IP**（`assetEvent.getAssetInfo(assetInfoRange)` -> `assetIp`）
- 阶段4：用**漏洞实例 IP**（`instances.vulNetAddr`）-- 保持现状
- 预览与下发用同一套 IP 分批核心逻辑

### 2.2 阶段4 批次归属（gate + scan 都标号）

`planInternal` 改造：
1. 先算全局 IP 批次：`ipBatches = shardIps(allIps, astUnitNum)` -> N 批，建立 `ip -> batchIndex` 映射
2. **gate**：每批产一个 gate group，`batchIndex = i+1`（保持当前 gateShards 逻辑，补标号）
3. **scan**：重构为按全局批次归属 -- 每个 bucket 的 instances 按 `ip->batchIndex` 归属到批次，**每批每 bucket 产一个 scan group**，`batchIndex = i+1`
   - 当前 per-bucket `shardByAstUnit` 改为 per-batch per-bucket 划分
   - scan group 数 = 批次数 × bucket 数（可能比当前多，但语义正确：每批每策略一个 scan 子任务）

### 2.3 统一契约

`dispatchPlan.subTasks[].batchIndex` + `batchLabel` 所有阶段都有值（单批时 batchIndex=1）。前端按 `batchIndex` 排序、`batchCount > 1` 时显示批次列。

---

## 三、后端改动清单

| # | 文件 | 改动 | 说明 |
|---|------|------|------|
| B1 | 新增 `IpBatchSharder`（service/dispatch） | `static List<List<String>> shardIps(List<String> ips, int astUnitNum)`：按 IP 顺序、每 astUnitNum 个 IP 切一批（同 IP 不拆散）；`<=0` 或 IP 数 <= astUnitNum 时单批 | 提取公共 IP 分批核心，阶段0-3 与阶段4 共用 |
| B2 | `VerifyFixDispatchPlanner.shardByAstUnit` | 改为调用 `IpBatchSharder.shardIps` 得到 IP 批次，再映射到 instances；`planInternal` 给 gate/scan group 标 `batchIndex`/`batchLabel`（见 §2.2） | scan 重构 per-batch per-bucket |
| B3 | `VerifyFixPlanGroup`（vo/verify） | 加 `Integer batchIndex` + `String batchLabel` | 承载批次信息 |
| B4 | `PhaseDispatchPreviewBuilder.build` | 签名加 `List<String> assetIps`（替代 `astNum` 驱动分批）；用 `IpBatchSharder.shardIps` 按 IP 切批，每批产 previewRows 并带 `batchIndex`/`batchLabel` | 替代 `AssetBatchSplitter.split(astTotal,...)` |
| B5 | `VulScanTaskAppServiceImpl.buildPhaseDispatchPreview` | 加载资产 IP：`assetEvent.getAssetInfo(task.getAssetInfoRange())` -> 提取 IP 列表 -> 传给 builder | 复用现成资产查询（[:477](project_backend/svmp/vul-pass/src/main/java/com/vtc/security/app/service/impl/VulScanTaskAppServiceImpl.java#L477)） |
| B6 | `VulScanTaskAppServiceImpl.dispatchGangedBatches` | `allAssets` 按 IP 分组切批（`IpBatchSharder.shardIps`），替代 `AssetBatchSplitter.splitList`；每批资产按 IP 归属 | 下发口径与预览一致；事务边界不变（每批独立 dispatch） |
| B7 | `DispatchPlanAssembler.fromVerifyFixPlan` | 映射 `group.batchIndex`/`batchLabel` 到 subTask；batchCount 按batchIndex 去重 | 修复 1060 batchCount=1 |
| B8 | `DispatchPlanAssembler.fromPhasePreview` | 已映射 batchIndex（v2.0 已有），确认 IP 拆分后 batchCount 正确 | 验证 |

---

## 四、前端改动清单

| # | 文件 | 改动 |
|---|------|------|
| F1 | `DispatchPlanPreview.vue` | `tableData` 按 `batchIndex` 升序排序（再按 `processOrder`）；`showBatchCol` 保持 `batchCount > 1`；批次列显示 `batchLabel`（已有，确认 1060 生效） |

---

## 五、单元测试清单（ponytail：非平凡逻辑配失败单测）

| 测试 | 覆盖点 |
|------|--------|
| `IpBatchSharderTest#shardByIp_basic` | 10 IP / astUnitNum=3 -> 4 批（3+3+3+1），同 IP 不拆散 |
| `IpBatchSharderTest#shardByIp_noBatch` | astUnitNum<=0 或 IP 数<=astUnitNum -> 单批 |
| `PhaseDispatchPreviewBuilderTest#preview_ganged_shardByIp` | 跨级联动按 IP 拆批，每批 previewRows 带 batchIndex |
| `VerifyFixDispatchPlannerTest#plan_ganged_batchIndex` | 跨级联动 gate/scan group 都带 batchIndex，batchCount>1 |
| `DispatchPlanAssemblerTest#fromVerifyFixPlan_batchCount` | 阶段4 多批 -> batchCount>1，subTask 带 batchIndex |
| `dispatchGangedBatches` 回归 | 下发按 IP 切批，批次数与预览一致（人工/集成验证，因 private 不便单测） |

---

## 六、风险与兼容

| 风险 | 缓解 |
|------|------|
| 阶段0-3 预览加载资产 IP 的性能（资产多如 12029） | 下发链路早已查（[:477](project_backend/svmp/vul-pass/src/main/java/com/vtc/security/app/service/impl/VulScanTaskAppServiceImpl.java#L477)），预览多查一次可接受；必要时加缓存 |
| scan 重构 per-batch per-bucket 导致 scan group 数变化 | 下发时 `VerifyFixPlanBatchSlicer.slice` 仍按 batchIps 过滤（不变），仅预览侧标号；回归阶段4 下发链路 |
| 下发批次划分变化（按 IP vs 按条数） -> 每批资产集合变 | 批次划分口径变，但总资产不变、每批仍是 astUnitNum 个 IP 的资产；事务边界不变（每批独立 dispatch，任一批失败中止） |
| `VerifyFixPlanBatchSlicer.slice` 是否依赖 group 顺序 | 需 Grep 确认 slice 逻辑；若按 IP 过滤则 batchIndex 不影响 |
| 旧工单 astUnitNum=-1 | 不分批，单批全量，batchIndex=1（兼容） |

---

## 七、不碰清单

- 不改 `VerifyFixDispatchPlanner` 的设备匹配 / 策略解析算法（仅批次标号 + scan 分批基准）
- 不改 confirmToken 生成/校验/下发协议
- 不改 `VerifyFixPlanBatchSlicer.slice` 的 IP 过滤逻辑（除非确认需依赖 batchIndex）
- 不改其他任务类型（上传/同步/口令）与非 pre/dispatch 接口
- 不新增第三方依赖

---

## 八、提交拆分（待用户确认后逐个执行）

- **提交1（公共能力）**：B1 `IpBatchSharder` + B2 `shardByAstUnit` 改调它 + B3 `VerifyFixPlanGroup` 加字段 + B2 planInternal 批次标号 + 单测
- **提交2（阶段4 批次列）**：B7 Assembler 映射 batchIndex + F1 前端排序 + 单测 -> **先让 1060 批次列显示**
- **提交3（阶段0-3 按 IP）**：B4 builder 签名 + B5 预览加载资产 IP + B8 验证 + 单测
- **提交4（下发按 IP）**：B6 `dispatchGangedBatches` 改按 IP 切批 + 回归 -> **下发口径与预览一致**

> 提交1-2 完成即可解决 1060 批次列显示；提交3-4 解决阶段0-3 按 IP 拆分。可分两批合入。
