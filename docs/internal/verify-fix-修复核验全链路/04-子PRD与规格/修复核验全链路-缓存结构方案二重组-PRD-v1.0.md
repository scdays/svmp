# 修复核验全链路 - 缓存结构方案二重组 PRD v1.0

> **范围**：修复核验预览方案缓存（CachedPlan）按数据类别重组、瘦身、计数自包含（方案二）。
> **对应权威文档**：
> - 前序：[修复核验全链路-缓存数据结构严谨化与规模适配-PRD-v1.0.md](修复核验全链路-缓存数据结构严谨化与规模适配-PRD-v1.0.md)（R-1~R-10，已落地 S1/S2/S4/S3.2）
> - 字段参考：[../../08-工具与指南/修复核验预览方案缓存字段说明.md](../../08-工具与指南/修复核验预览方案缓存字段说明.md)
> - 真实大单 dump：`../../_archive/3.21 Wave R（07-22）- 统一设备匹配 + 缓存数据结构优化.txt`（922KB，5969 IP，阶段0-3）
> **对应开发计划**：[修复核验全链路-缓存结构方案二重组-开发计划-v1.0.md](修复核验全链路-缓存结构方案二重组-开发计划-v1.0.md)
> **日期**：2026-07-24
> **状态**：待评审
> **工程边界**：后端 `project_backend/svmp/vul-pass` + 前端 `project_frontend/asset/asset-newleak-manage`，分支 `feature/fix-ledger-log-records`

---

## 1. 背景与目标

### 1.1 背景

S1/S2/S4/S3.2 已落地（引用 + 强校验 + 精确物化 + 体积护栏 + 死字段清理）。基于真实大单缓存 dump（922KB，5969 资产 IP，阶段0-3 单 VUL_SCAN 组）分析，缓存结构仍存在以下问题：

1. **字段零散**：`DispatchPlanGroup` 30+ flat 字段；`previewContext` 混杂工单上下文 / 用户参数 / 资产 / 漏洞 / SQL 片段 / 计数，未按类别归组。
2. **展示型字段进了缓存但下发不用**：`engName/engTypeLabel/devIp/vendor/candidateDevices/warnings/batchLabel/subTaskTypeName/suggestedReportTypeName/processHints/reportTypeHint/targetScale/dependHint/role` 等仅用于页面展示；而 `AppServiceImpl:531 dto.setVerifyFixPlan(null)` 已把 verifyFixPlan 在响应里显式置空、不重展示，`buildSubTaskFromPlanGroup` 下发时也不读这些字段 -> **缓存内死数据**。
3. **SQL 片段与结构化数据重复**：`assetInfoRange`(`asset_port.ip in (...)`) 与 `assetList[].assetIp` 重复存资产 IP；`vulInfoId`/`vulKeys` 与 `vulInstSnapshots` 重复存漏洞范围；且裸 SQL 片段 schema 耦合（列名硬编码在缓存）。
4. **计数下发期重算、非缓存权威**：`ast_num`=`filterAssetsByIps().size()`、`vul_num`=收窄后 `distinct vulId`，均在下发期计算而非读缓存 -> 预览/下发计数有漂移风险。
5. **ast_num 语义错误**：当前 `filterAssetsByIps().size()` 实为"资产 IP 条数"，与部侧"`ast_num`=要求排查资产数量（资产 ID 数）"不符（订单级 astNum=资产ID数，子任务级却=IP数，系统内自相矛盾）。
6. **pw_num / vul_inst_num 缺失**：`pw_num` 仍订单级继承（未按组拆）；`vul_inst_num`（系统漏洞数量）无 DB 列（D-1 此前 defer）。

### 1.2 目标

| 目标 | 说明 |
|------|------|
| 类别化重组 | CachedPlan 按数据类别分块（lifecycle / orderContext / userParams / assets / vulns / mainTask / subTasks），消除零散 flat 字段 |
| 缓存最瘦 | 缓存只留**下发必需**；展示型字段移出缓存（留响应 VO） |
| 计数自包含 | 7 计数在 mainTask + 每个 subTask 预览期算好、下发直读，零重算 |
| 计数准确 | ast_num=资产ID数（修 bug）；新增 ast_ip_num=IP数；pw_num/vul_inst_num 补齐 |
| SQL 结构化 | SQL 片段拆为结构化列表（vulIds/stat），消除 schema 耦合与重复 |
| 分数展示 | 前端按子任务展示"子任务数/工单要求数"分数，hover 中文名 |
| 平滑迁移 | schemaVersion 升 2，在途 v1 缓存被版本校验拒绝（提示重新预览） |

### 1.3 非目标

- 不改 scope 引用模型（assets/vulns 全局存一份，subTask 用 assetIps/instanceIds 引用，下发精确物化）--经分析单批大单组内自包含不优于引用，且引用 + S1 强校验已保一致性。
- 不改 token / 锁 / 幂等 / Repository 基础设施。
- 不改 lifecycle 字段（owner/schemaVersion/expiresAt/verifyFixFlow/dispatchAttemptCount/token/checksum/status）。

---

## 2. 核心设计决策

### 2.1 缓存只留下发必需

`task.verifyFixPlan` 响应置空（`AppServiceImpl:531`）、不重展示；下发物化只读 dispatch-essential 字段。故缓存移除所有展示型字段（engName/candidateDevices/warnings/batchLabel 等），它们仅保留在 preDispatch 响应 VO（DPA 装配）。**缓存 = 下发物化权威源；响应 VO = 页面展示源。**

### 2.2 计数自包含、下发直读

7 计数（`astNum/astIpNum/vulNum/pwNum/prcAstNum/prcVulNum/vulInstNum`）在 mainTask（订单级）+ 每个 subTask（子任务级）预览期算好写入缓存；下发期 `buildSubTaskFromPlanGroup` 直读 `subTask.counts` 到 `VulScanTaskSubDO`，**删掉** `filterAssetsByIps().size()` 与 `distinct vulId` 重算。保证预览计数 == 下发计数。

### 2.3 计数语义（部侧规范 + 本需求）

| 字段 | 含义 | 取值 |
|---|---|---|
| `ast_num` | 要求排查资产数量 | 资产 ID 数（去重） |
| `ast_ip_num` | 资产 IP 数（本需求新增） | IP 数（直观核对 astUnitNum 分配） |
| `vul_num` | 要求扫描产品漏洞数量 | distinct vulId 数 |
| `pw_num` | 要求扫描弱口令数量 | 弱口令数（暴破任务） |
| `prc_ast_num` | 实际排查资产数（=ast_num） | 下发时=ast_num，回传后更新 |
| `prc_vul_num` | 实际排查产品漏洞数（=vul_num） | 下发时=vul_num，回传后更新 |
| `vul_inst_num` | 系统漏洞数量（本需求） | 漏洞实例数（=instanceIds.size） |

- mainTask.counts = 订单级合计；subTask.counts = 子任务级。
- 前端分数 = `subTask.count / mainTask.count`（如 27/55），hover 显示中文名。

### 2.4 scope 保留引用模型

`assets`（assetList）与 `vulns`（snapshots）全局存一份；subTask 用 `scope.assetIps/instanceIds` 引用；下发期按引用从 assets/vulns 精确物化（S1 `DispatchPlanIntegrityValidator` 校验引用一致 + 精确收窄保一致）。

### 2.5 SQL 片段结构化

`assetInfoRange`/`vulInfoId`/`vulKeys`/`vulInfoStat` 裸 SQL -> 结构化：`vulns.vulIds[]`（漏洞ID列表）、`vulns.stat[]`（状态码集合）；资产 IP 由 `assets.assetList[].assetIp` 覆盖，删 `assetInfoRange`。消费时按需拼 SQL。

### 2.6 schemaVersion 升 2

结构变更，`CachedPlan.CURRENT_SCHEMA_VERSION = 2`。在途 v1 缓存被 S1 的版本校验拒绝（"预览方案版本已升级，请重新预览"），自然迁移。

### 2.7 D-1 vul_inst_num 加列

`vul_scan_task_sub` 增 `vul_inst_num` 列（部侧未要求，本需求），物化时写入 `subTask.vulInstNum`。

---

## 3. 新缓存结构（方案二）

```
CachedPlan
├ lifecycle: owner, schemaVersion(=2), expiresAtEpochMs, verifyFixFlow,
│            dispatchAttemptCount, token, checksum, status
├ orderContext（工单）
│   orderId, orderType, orderSubType, ctxCode, srcTktPrsn, dstTktPrsn,
│   assetOwnerInfo, astUnitNum
├ userParams（任务参数）
│   tskType, tskModel, tskAction, tskPhase, procMethod, source,
│   autoSubmit, syncAssetPort
├ assets（资产全局）
│   assetList[]{ assetIp, assetInfo[资产ID,逗号分隔], targetPortFileLoc, source, astNum }
├ vulns（漏洞全局，结构化）
│   snapshots[]{ vulInstId, assetId, vulNetAddr, vulTransProto, vulPort, srcMethod, stat, vulId },
│   vulIds[], stat[]
├ mainTask（主任务）
│   tskName, transId, dispatchMode, subTaskCount, allDevicesMatched,
│   counts{ astNum, astIpNum, vulNum, pwNum, prcAstNum, prcVulNum, vulInstNum }
└ subTasks[]（子任务，counts 自包含、scope 引用）
    ├ id{ groupKey, wave, subTaskKind, batchIndex, processOrder }
    ├ type{ tskType, procMethod, srcMethod, expectAlive, suggestedReportType }
    ├ device{ engHash, candidateEngHashes, defaultEngHash, scannerSource,
    │         deviceRequired, deviceMatched }
    ├ scope{ assetIps, instanceIds }
    └ counts{ astNum, astIpNum, vulNum, pwNum, prcAstNum, prcVulNum, vulInstNum }
```

### 3.1 从缓存移除（留响应 VO 或删）

| 类别 | 字段 | 处置 |
|---|---|---|
| 死字段 | srcMethod105X、evidenceCapabilities、dependsOnGroupIndex、orderProcMethod、forcedEngHashes(缓存副本)、createdAtEpochMs | 删 |
| 展示型（留响应 VO） | engName、engType、engTypeLabel、engTypeLabels、devIp、vendor、actualEngTypeLabel、candidateDevices、subTaskTypeName、batchLabel、suggestedReportTypeName、warnings、processHints、reportTypeHint、targetScale、dependHint、role、dispatchModeLabel、phaseChain、dualVendor、canConfirm、message | 缓存删；DPA 装配响应时从 pre-cache plan 保留 |
| SQL 片段 | assetInfoRange、vulInfoId、vulKeys、vulInfoStat | 结构化为 vulns.vulIds/stat；assetInfoRange 删（assets 覆盖） |

### 3.2 保留（下发必需）

- lifecycle 全部。
- orderContext：工单字段（重建主任务）。
- userParams：任务参数（重建主任务）。
- assets.assetList：资产范围（物化子任务资产）。
- vulns.snapshots + vulIds + stat：漏洞范围（物化子任务漏洞实例）。
- mainTask：主任务物化参数 + 计数。
- subTasks：每个子任务的 type/device/scope/counts + id。

---

## 4. 7 计数字段计算规则

| 字段 | 预览期计算（与 scope 同源） |
|---|---|
| `astNum` | subTask：组 assetIps 对应 assets.assetList 的资产ID去重数；mainTask：全量资产ID去重数 |
| `astIpNum` | subTask：`scope.assetIps.size`；mainTask：全量 IP 数 |
| `vulNum` | subTask：`scope.instanceIds` 对应 snapshots 的 distinct vulId；mainTask：全量 distinct vulId |
| `pwNum` | subTask：组内弱口令数（暴破任务，从 pw 数据源）；非暴破=0；mainTask：合计 |
| `prcAstNum` | = astNum（下发时；回传后更新） |
| `prcVulNum` | = vulNum（下发时；回传后更新） |
| `vulInstNum` | subTask：`scope.instanceIds.size`；mainTask：全量实例数 |

下发期：`subTask.setAstNum(group.counts.astNum)` 等直读，删重算。

---

## 5. 与现有文档/代码的关系

| 现有 | 本 PRD 关系 |
|---|---|
| 严谨化 PRD R-1/R-2（scope 引用模型） | 延续（scope 不改） |
| 严谨化 PRD R-3（计数） | **重写**：7 计数自包含 + ast_ip_num + 下发直读 + 修 ast_num bug |
| 严谨化 PRD R-6.1（schemaVersion） | 升级为 2 |
| 严谨化 PRD R-10（死字段） | 扩大：删展示型字段 + SQL 结构化 |
| S2.2 group.assetCount/vulNum | 重命名为 astNum/vulNum，补全 7 字段，移入 subTask.counts 块 |
| S2.3 subTask vulNum 重算 | 改为直读 subTask.counts.vulNum |
| D-1（vul_inst_num 列） | 本次实施 |

---

## 6. 验收标准

1. **结构**：CachedPlan 按类别分块（orderContext/userParams/assets/vulns/mainTask/subTasks）；subTask 内 id/type/device/scope/counts 块；无 flat 零散字段。
2. **缓存最瘦**：展示型字段不在缓存（留响应 VO）；死字段清零；SQL 片段结构化。
3. **计数自包含**：mainTask + 每个 subTask 带 7 计数；下发直读，无 `filterAssetsByIps().size()`/`distinct vulId` 重算。
4. **计数准确**：ast_num=资产ID数（非IP数）；ast_ip_num/pw_num/vul_inst_num 齐备。
5. **D-1**：vul_scan_task_sub.vul_inst_num 列 + 物化写入。
6. **前端**：DispatchPlanPreview 按子任务展示 5 分数（ast/ast_ip/vul/pw/vul_inst 的 subtask/main），hover 中文名。
7. **迁移**：schemaVersion=2；在途 v1 缓存被拒。
8. **测试**：结构/计数/直读 各单测；mvn test 无新增红；eslint 通过。

---

## 7. 待决策项

| 编号 | 决策点 | 倾向 |
|---|---|---|
| E-1 | pw_num 按组算的口令数据来源 | 暴破任务从 pw 字典/实例数据按组 scope 计数；非暴破=0 |
| E-2 | mainTask.counts 计算 | 由 subTasks 合计 vs 从订单独立算--二者应一致，倾向订单独立算再与合计交叉校验 |
| E-3 | phaseChain(阶段0-3) 是否进缓存 | 阶段0-3 下发物化是否需要；不需要则留响应 VO |

请评审；确认后进入开发计划执行。
