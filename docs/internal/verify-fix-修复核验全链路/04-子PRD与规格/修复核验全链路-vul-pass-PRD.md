# 修复核验全链路（vul-pass）— 产品需求文档（PRD）

> **用途**：部侧考核合规改造与修复核验业务闭环的**唯一产品规格**。  
> **版本**：**v2.1.0** · **日期**：2026-07-22 · **状态**：定稿  
> **修订记录**：
> - v2.1.0（2026-07-22）：补充全阶段下发模型统一（DispatchPlan）、全阶段缓存策略、统一设备匹配策略（EngDeviceMatcher 唯一入口）、全阶段设备选择、缓存数据结构优化；对应开发计划 v3.0 Wave O/P/Q/R。
> - v2.1.0 补充（2026-07-22）：追加 Wave S 设备选择增强--a-select tooltip 显示设备详情（hash/全部设备类型/注册状态）；弱口令扫描设备映射 1030/1031/1032 -> WEAK_PASSWORD(bit 8)；1026 交叉扫描 -> VERSION_LOGIN 映射修复 + 双厂商默认设备自动分配 + 前端冲突校验；移除预览页 SafeSourceDriver/DualVendorScannerPick，设备选择全走 per-group a-select；对应开发计划 v3.0 Wave S。
> - v2.0.0（2026-07-21）：由 v1.4.10 及 Wave A～L 全部迭代文档统一重构，只保留当前有效口径；历史演进见《修复核验全链路-开发计划-v3.0》Wave 演进纪要。

| 属性 | 值 |
|------|-----|
| 功能编号 | **VULPASS-VERIFYFIX-P0** ~ **P3** |
| 模块名称 | 修复核验全链路（工单接入 → 编排预览 → 离线导入 → 判定 → 台账） |
| 主服务 | **`vul-pass`**（唯一业务执行面） |
| 前端工程 | **`asset-newleak-manage`**（qiankun 子应用） |
| 开发分支 | 两端统一 **`feature/fix-ledger-log-records`** |
| 关联服务 | `vuln-task-center`（在线扩展，本期默认离线）；`asset-other-manage`（BAS/等效防护，P2） |
| **明确不做** | **`open-api-service` 业务改造**（仅保留对外 API 薄层，能力后续 Feign 至 vul-pass） |
| 参考规范 | 《建设指南(2025)》《接口规范(2025)》《测试规范(2025)》；`svmp/docs/standards/` |
| 关联 PRD | `修复核验运营工作台-PRD.md`（open-api 运营面，与本 PRD 解耦） |
| 工程路径 | 后端 `project_backend/svmp/vul-pass`；前端 `project_frontend/asset/asset-newleak-manage` |

---

## 1. Why — 背景与目标

### 1.1 背景

工信部专项漏洞排查工单考核中，基于台账日志分析发现两类不合规项：

| 考核项 | 问题描述 |
|--------|----------|
| **排查 IP ↔ 台账** | 排查任务发现漏洞的资产 IP 未出现在台账日志 `onlineAddrFileLoc` 中 |
| **修复核验存活一致性** | 「漏洞核验方式与目标存活状态不匹配」；存活一致性比率未达标（要求 ≥80%） |

**建设指南核心要求（修复核验）：**

> 对于闭环漏洞需核实修复或已防护状态，并提供判定证据。  
> 支持记录修复方式；**对在线的已修复资产业务连通性检测**；  
> **补丁修复** → 登录扫描或远程版本扫描核验；  
> **等效防护或方式未知** → POC、BAS 攻击模拟验证安全效果。

**指南释义：**

- 「方式未知」**不等于** 1051–1053；指未登记修复方式的情形。本期**不实现**未知分支，空/`非105x` 拒绝进入编排。
- 指南**未逐条**规定 1052/1053 的检测手段；本期按修复语义默认 **仅连通性（expect_alive=false）**，属产品推断，需在设计说明中留痕。

### 1.2 目标

1. **合规**：专项排查与修复核验回传后，排查 IP 覆盖与存活一致性达标。
2. **门闸 + 策略化**：**先 1028 连通性门闸**（主机存活+端口），再按实例 `src_method` 结案或二次技术核验。
3. **可确认**：预览后用户仅确认/取消；确认前不可下发（confirmToken）。
4. **离线优先**：`tsk_model=1`（0=在线，1=离线）；离线可用完整报告内生存活段**等价完成 Gate**（须可举证）。
5. **外壳/内层字段收敛**：台账 `logType` ← **主任务** `procMethod`；实例/rela `srcMethod` ← **子任务** `procMethod`（实际手段）。

### 1.3 成功标准（可衡量）

| 指标 | 标准 | 验证方式 |
|------|------|----------|
| 排查 IP 覆盖率 | 专项工单 `vulNetAddr` ⊆ 台账 `onlineAddrFileLoc` | SQL / 台账查询 |
| 存活一致性比率 | `alive_consistent=true` 占比 **≥80%**（口径见 §3.6） | 靶标 / ComplianceMetrics |
| 核验方式匹配率 | Gate 子任务 `proc_method=1028`；1050 存活后再 1022/1027(配置项)；1051 存活后固定 1021 POC（BAS 1061 暂未落地）；禁止对不存活 1050/1051 做技术核验结论 | 子任务 `proc_method` + 编排顺序 |
| 台账完整性 | 每条物理 subTask 一对 **9+10**，Gate 的 10 必含 `onlineAddrFileLoc`；**logType=主任务外壳** | logNum = subTask×2；logType 抽样 |
| 混合工单 | 共用 Gate；1052/1053 Gate 后结案；1050/1051 仅存活进入二次 Scan | 联调 |

### 1.4 不做边界

- 不改造 `open-api-service` 修复核验编排/Job/Webhook。
- 不改 Partner `verify-fix` REST；不改部侧协议字段。
- **不引入「修复方式未知」分支**（仅 1050–1053）。
- 本期默认离线；在线 VTC 为 P3 可选。
- **禁止**将 PORT 拆成独立半截台账物理子任务；**允许**「1028 Gate → 条件二次 Scan」两波物理任务。

---

## 2. Who — 角色与用户故事

| 角色 | 说明 | 核心操作 |
|------|------|----------|
| **部侧平台** | 下发核验工单（34/1063）、拉取台账与系统漏洞表 | 考核验收 |
| **漏管运营** | 处理本地 BPMN 修复核验节点或部侧工单 | 预览方案 → 确认 → 导入报告 → 提交 |
| **安全运维** | 维护安全资源设备（engHash/engType） | 保障扫描器/POC/BAS/连通性设备可用 |
| **研发/测试** | 联调靶标与生产 XLSX 路径 | 按验收用例回归 |

| ID | 作为… | 我希望… | 以便… | 阶段 |
|----|-------|---------|-------|------|
| US-01 | 运营 | 收到修复核验工单后，系统自动解析待核验实例及各自 src_method | 不用手工分组 | P0 |
| US-02 | 运营 | 下发前看到「扫描器语义」子任务预览（策略类、设备、IP 批次、证据能力说明） | 确认无误再处置 | P1 |
| US-03 | 运营 | 确认后按建议模板导入 NSFOCUS XML 或平台 XLSX | 离线完成核验 | P1 |
| US-04 | 系统 | **Gate(1028)** 完成后再做 1050/1051 二次技术核验；1052/1053 Gate 即结案 | 堵住「方式与存活不匹配」 | P2′ |
| US-05 | 系统 | 按 src_method 判定 6/7/10（1052/1053：存活→7，不可达→6） | 闭环合规 | P2 |
| US-06 | 系统 | 每条物理 subTask 完整 9/10，Gate 必写 onlineAddr | 部侧审计通过 | P0 |
| US-07 | 运营 | 混合工单一次预览：Gate 批 + 条件二次 Scan 批 | 常见生产场景可用 | P1 |
| US-08 | 运营 | 主任务列表点行看摘要，全页查看子任务编排/结果/台账，子任务可去处置 | 核验过程可追踪、可操作 | P2′ |
| US-09 | 运营 | 主任务一点「自动化处置」，按顺序/并行编排驱动多子任务完成处置 | 少点「去处置」、减少漏跑波次 | P2′ |

**入口与触发：**

| 入口 | 指令/节点 | 主任务 proc_method | 说明 |
|------|-----------|-------------------|------|
| 部侧核验工单 | `CommandSubType` **34** / 回传 **44** | 一般为 **1060** | `CommandListener` |
| 跨级联动核验 | **1063** | **1060** | 同上 |
| 本地 BPMN | `UserRiskRemReinvest6/7` | 1060 或工单指定 | 修复核验节点 |

---

## 3. What — 业务规则

### 3.1 实例加载规则

从工单 `vulInfoRange` / 指定 `vulInfoID` 加载：

```text
条件:
  vulInfoStat = 5（已修复）
  src_method IN (1050, 1051, 1052, 1053)

拒绝:
  src_method 为空或非 105x → 提示先完成修复处置并记录修复方式
  1050 无 fixLnk / 1051|1052 无 defDev → 校验失败（与处置阶段一致）
```

### 3.2 门闸编排（1028 Gate → 条件 Scan）

对准部侧考核「漏洞核验方式与目标存活状态不匹配」。跨级/本地工单技术处置方式外壳为 **1060（修复核验自适应扫描）** 时：

```text
【Wave-Gate】对工单影响资产做连通性检测（主机存活 + 端口扫描）
  · 子任务 proc_method（实际手段）/ 实例内层 srcMethod = 1028
  · 台账外壳 logType = 主任务 proc_method = 1060（格式同系统漏洞排查/弱口令；BAS 规范未下发前同此）
  · 必写 onlineAddrFileLoc（覆盖本批；支撑四元组匹配）
  · 可按 astUnitNum 对唯一 IP 切批；engType bit=16；可受 eng_hash_cnt 池约束

【分流】按实例修复史 src_method ∈ {1050,1051,1052,1053}：

  · 1052 / 1053（§3.3）
      探测目标仍存活(IP+端口+协议+服务) → vulInfoStat=7 核验未修复
      探测目标不可达               → vulInfoStat=6 核验修复
      无法判定                     → vulInfoStat=10
      Gate 完成后即结案，不进入二次技术扫描

  · 1050 / 1051 且目标不存活 → vulInfoStat=10 核验失败（禁止再发登录/版本/POC）

  · 1050 且存活 → 【Wave-Scan】手段 ∈ {1020,1022,1023,1024,1027}（默认 1022，Nacos 可配；工单可盖）
  · 1051 且存活 → 【Wave-Scan】手段 ∈ {1021, 1061}（BAS 1061 暂未落地，固定 1021 POC）
```

- 二次 Scan 资产集 ⊆ Gate 存活集；Gate/Scan 各自必须是完整 9+10。
- 离线导入：若运营一次导入含存活+漏洞的完整 XML，可用报告内生存活段 **等价完成 Gate 判定**，再对存活 1050/1051 取漏洞/POC 段；须在预览/台账标明证据来源，考核仍以可解析存活证据为准。

**物理子任务展开：**

| 波次 | 策略类 | 覆盖实例 | 子任务 `proc_method`（实际手段） | 台账外壳 logType（←主任务） | 切批 |
|------|--------|----------|----------------------------------|------------------------------|------|
| Gate | CONNECTIVITY_CHECK | 工单内全部待核验实例的资产 | **1028**（主机存活+端口扫描） | **1060** | ×astUnitNum |
| Scan | VUL_SCAN | Gate 后仍存活的 **1050** | 配置项 `default-version-login`：**1022** 漏洞扫描(混合) / **1027** 登录扫描 / 1020 指纹插件 | 1060 | ×astUnitNum |
| Scan | POC_BAS | Gate 后仍存活的 **1051** | **1021** POC 插件 | 1060 | ×astUnitNum |

混合示例（astUnitNum=-1，四类都有且全部主机存活）：**1 Gate + 1 VUL_SCAN + 1 POC_BAS**。若存在不存活 1050/1051，二次 Scan **不得**包含这些实例。

### 3.3 1052 / 1053 实例级连通性识别与结论

判定对象是 **系统漏洞实例**。复用 `handlerPort` / `MatchAssetRuleEnum` 键：

```text
探测目标 T = vulNetAddr + vulTransProto + vulPort(+ vulSvc)
actual_alive = Gate/报告开放端口索引中 T 是否仍可达

结论：
  actual_alive == true  → stat=7 核验未修复
  actual_alive == false → stat=6 核验修复
  actual_alive == null  → stat=10 核验失败（无法判定）

alive_consistent（考核口径）：
  使用 1028 且 actual 可判定 → true；无法判定 → false
```

| | 1052 连通性阻断 | 1053 资产下线 |
|--|-----------------|---------------|
| 主匹配 | **漏洞端口/URL 级**（IP+端口[+协议]） | **主机级优先**；有明确端口可叠加 |
| 无有效 vulPort | 预览告警；incomplete→10 | 允许仅 IP |
| 报告无此 key | 默认可达=false（严格通过）；可配 incomplete→10 | 同左 |

URL 类实例单独 HTTP 可达规则，不硬套 `ip:port`。

### 3.4 外壳 / 内层取值矩阵（全阶段 · 定稿口径）

| 阶段 | 主任务 `proc_method`（外壳→logType） | 子任务 `proc_method`（实际→实例 srcMethod） | 说明 |
|------|--------------------------------------|---------------------------------------------|------|
| **排查** | 与子任务一致（如 1020/1022…） | 同主任务 | 主子同源 |
| **验证** | 工单约定 | 默认同主；**交叉扫描**可不一致 | 不一致时内层跟子任务 |
| **修复** | 工单可为 **105** 等外壳 | 实际下发 **1050–1053** | 外壳跟主；手段跟子 |
| **核验** | **1060**（或显式 1061） | Gate **1028** / Scan **1022/1021…** | 部侧考核核心：logType=1060，srcMethod=102x |

**proc_method 优先级（工单覆盖策略）：**

```text
IF 工单 proc_method == 1060（修复核验自适应） → 按 src_method 默认策略
ELSE IF 工单 proc_method ∈ {1020, 1027, ...}（显式指定） → 工单值优先，覆盖 1050 组默认方式
ELSE IF 工单 proc_method == 1061 → 1051 组优先 BAS/POC；1050 组仍走 1050 策略
```

| src_method | 默认（1060 工单） | 工单覆盖示例 |
|------------|-------------------|--------------|
| 1050 | VUL_SCAN 默认 **1022**（可 Nacos 配置 `default-version-login`） | 工单 **1027** → 登录扫描；**1020** → 指纹插件 |
| 1051 | 固定 **POC(1021)**（待 `bas-enabled=true` 后支持 1061） | 工单 **1061** 且 bas-enabled → 攻击模拟 |

### 3.5 设备匹配（硬约束：必须命中合法设备）

依据《接口规范》安全资源设备（engDev）**engType**（bit 可并存）：

| 值 | 含义 | | 值 | 含义 |
|----|------|---|----|------|
| 1 | 主机扫描器 | | 16 | 连通性探测工具 |
| 2 | WEB 扫描器 | | 32 | BAS 设备 |
| 4 | POC 引擎 | | 0 | 其他 |
| 8 | 弱口令工具 | | | |

- 匹配判定（禁止等值）：`(eng_type & requiredBit) != 0`。
- 策略类 → requiredBit：CONNECTIVITY(11)→16；VUL_SCAN(13)→1；POC(14)→4；BAS(15)→32；WEAK_PASSWORD(16)→8（Wave S 新增）。
- 候选池：工单 `eng_hash_cnt`（JSON 字符串数组）非空 → **强制仅池内**（仍须满足 engType bit）；否则全量可用设备。
- 解析顺序：构造候选池 → LastScannerResolver（仅 1050/1051 优先）→ STRATEGY_MATCH 按 engType bit → 仍失败 `deviceMatched=false`，预览红标，**禁止确认下发**。
- 禁止用与策略 engType 不符、或落在 eng_hash_cnt 池外的 hash 冒充已匹配。溯源仅排查 102x，不含 1026。

### 3.6 离线导入与结果判定

**处置方式（页面）**：从 `VulReportTypeEnum` 选择。

| 场景 | reportType | code | 说明 |
|------|------------|------|------|
| 部侧考核靶标 | NSFOCUS_XML_III | 10 | 绿盟 XML V1.2，含存活/端口/漏洞 |
| 生产专项/常态化 | PLATFORM_VUL_INST_XLSX_V2 | 3 | 平台 XLSX，实例字段为主 |

解析：导入 → Parser → 标准中间模型 → 按本物理 subTask 负责 IP/实例集合过滤 → 同报告内提取存活、端口、漏洞或 POC 段 → 供判定使用。XLSX 推断连通性标记 `dataSource=INFERRED`（默认允许；考核以 XML 为准）。

**判定顺序（VerifyFixVerdictService）：**

```text
1. 以 Gate（或等价报告存活段）解析实例级 actual_alive（§3.3）
2. 1052/1053：actual=true → 7；false → 6；null → 10
3. 1050/1051 且 actual!=true → 10，禁止技术通过结论
4. 1050 存活后看二次 Scan 漏洞段 → 6/7/10
5. 1051 存活后看 POC/BAS → 6/7/10
```

| src_method | stat=6 核验修复 | stat=7 核验未修复 | stat=10 核验失败 |
|------------|-----------------|-------------------|------------------|
| **1052/1053** | 探测目标不可达 | **探测目标仍存活** | 无法判定 |
| **1050** | 存活 + 扫描未再检出 | 存活 + 仍检出 | 不存活或异常 |
| **1051** | 存活 + 攻击未命中 | 存活 + 攻击仍成功 | 不存活或异常 |

**存活一致性比率** = count(`alive_consistent=true`) / count(参与核验实例) ≥ **80%**。

### 3.7 台账（106 类，硬约束）

**每一条物理 subTask**（含 Gate 与 Scan）必须有一对完整台账：

| opCode | 动作 | 实现类 |
|--------|------|--------|
| **9** | 下发验证任务 | `IssueVerifyTaskActionService` |
| **10** | 获取验证结果 | `VerifyResultActionService` |

**取值硬规则：**

```text
logInfoReqParams.logType          ← 主任务.procMethod（外壳）
实例 / rela / content.srcMethod   ← 子任务.procMethod（实际手段；有拆分时）
台账管理类型 / 是否走 106 类 9+10 ← 主任务.procMethod
禁止：用子任务实际手段覆盖 logType
禁止：核验场景把实例 srcMethod 写成主任务 1060（丢掉 1028/1022）
禁止：把修复史 1050–1053 当作核验上报内层 srcMethod
```

**opCode=10 关键字段：**

- `prcAstNum`、`prcVulNum`（可 0）、`vulInfo`、`vulPocInfo`
- `onlineAddrFileLoc`：经 **OnlineAddrMerger**；**Gate 必填且覆盖本批负责 IP**
- `logType`：主任务外壳（1060 或 bas-enabled 时二次显式 1061）；内容 srcMethod 为子任务真实 1028/1022/1027/1021

**交叉扫描特例**：验证阶段若子任务 `proc_method` 与主任务不一致，**logType 仍跟主任务**；实例实际手段跟该子任务。产品可选强制子=主以简化，不得反向把核验内层改成只写 1060。

### 3.8 处置类型（reportType）自动分配

工单来源 `source`（0=企业本地工单 / 1=部侧工单，外层工单字段，任务表不存，预览/下发透传或按 orderId 回查）；业务场景 `ctxCode=3` 为行业漏洞专项排查。**禁止**用 `ctxCode==2` 判断企业。

| 条件 | reportType |
|------|------------|
| 扫描手段（1020/1022/1023/1024/1027）且 source=0 | **3** 常态化 XLSX |
| 扫描手段且 source=1 且 ctxCode=3 | **3** |
| 扫描手段且 source=1 且其它 ctxCode（或 source 缺失） | **10** 绿盟 XML V1.2 |
| **1028 连通性检测** | **34**（CONNECTIVITY_CHECK_V1，固定，hidden=1，upload=1） |

其它手段沿用现网：1021→23；1026→21；1040→22；1050~1053→31；1060/1061→32；1080→51。

### 3.9 下发模式（dispatchMode）

配置项 `compliance.verify-fix.dispatch-mode`：

| 模式 | 下发行为 | 回收/报告处理顺序 |
|------|----------|-------------------|
| `sequential`（默认） | 仅下发连通性检测；连通性全终态后派生修复核验 | 先连通性，后修复核验 |
| `parallel` | 同时下发两类子任务（参数互不关联） | **仍**先连通性，后修复核验 |

### 3.10 主任务自动化处置

不替代 preDispatch/dispatch；只对**已下发且待处置**子任务，按 wave 编排自动驱动 `recycle` / `recycle/auto`。

| 模式 | 行为 |
|------|------|
| `online` | 子任务 `reportType.upload≠1`：后端编排器自动调用在线 recycle，使用已落库 reportType |
| `offline-batch` | 需上传：返回有序槽位；连通性未终态时修复核验槽位锁定；前端按槽位调现有 `/recycle` |

失败策略：同波次单失败不阻断（`continueOnError` 默认 true）；连通性波次未全部成功时不自动进入修复核验；支持 pause/resume；可随时回退单条「去处置」；提交处置直接使用子任务已落库 `reportType`。

核验跃迁单路径：主任务 recycle 与单条子任务 `handlerVulProcess` 在通用插件跃迁后，均调用 `VerifyFixVerdictService` 覆盖写实例 6/7/10。

---

## 4. 领域与状态模型

### 4.1 子任务唯一键与类型

```text
subTaskKey = (wave, strategyClass, proc_method实际手段, eng_hash, astUnitNum分片)
wave ∈ { CONNECTIVITY_CHECK, REPAIR_VERIFY }（兼容历史 GATE/SCAN；读写经 VerifyFixSubTaskKind，禁止写死）
strategyClass ∈ { CONNECTIVITY_CHECK, VUL_SCAN, POC_BAS }
```

- PORT(12) **不落物理子任务**（仅证据能力，合并进报告解析）。
- `tsk_type` 表示任务类型（设备 engType 匹配粒度）：10 DEFAULT / 11 CONNECTIVITY / 13 VUL_SCAN / 14 POC / 15 BAS / 16 WEAK_PASSWORD（Wave S 新增）；`wave` 表示编排阶段，二者互补，UI 勿都叫「类型」。

### 4.2 表字段（定稿）

`vul_scan_task_sub`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `src_method` | smallint | 覆盖实例修复史源处置方式 1050–1053（编排分流用） |
| `tsk_type` | tinyint | 任务类型（§4.1） |
| `proc_method` | smallint | **实际手段**：核验 Gate=1028、Scan=1022/1021…；修复下发=1050–1053；排查可与主任务一致。**写入实例/rela 内层 srcMethod 的依据** |
| `expect_alive` | boolean | 策略预期存活 |
| `actual_alive` | boolean | 导入解析实测 |
| `alive_consistent` | boolean | expect 与 actual 是否一致 |
| `scanner_source` | varchar(16) | LAST_SCAN / FALLBACK / MANUAL / STRATEGY_MATCH / ENG_HASH_CNT |
| `confirm_token` | varchar(64) | 主任务级预览令牌（冗余便于查询） |
| `wave` | varchar(32) | 编排阶段 CONNECTIVITY_CHECK / REPAIR_VERIFY |
| `depend_gate_id` | bigint | 关联连通性检测子任务 ID |

`vul_scan_task`：

| 字段 | 说明 |
|------|------|
| `proc_method` | **外壳**：工单约定技术处置方式；核验一般 **1060**；**台账 logType / 管理类型依据** |
| `tsk_model` | **0=在线, 1=离线导入**；核验默认 **1** |
| `tsk_phase` | **4** 核验阶段（`OrderPhaseEnum.PHASE_VERIFICATION`） |
| `confirm_token` | 预览确认令牌 |
| `ast_unit_num` | 部侧工单拆分粒度 |

### 4.3 主 / 子任务状态码（Wave H 定稿）

主任务 `vul_scan_task.tsk_stat`：

| code | 枚举 | 中文 |
|------|------|------|
| 10 | PRECHECK | 任务预检 |
| 20 | PENDING_START | 待启动 |
| 30 | RUNNING | 执行中 |
| 40 | RECYCLING | 结果回收 |
| 50 | AUDIT_DONE | 稽核完成 |
| 60 | FINISHED | 任务结束 |
| 90 | FAILED | 失败 |

子任务 `vul_scan_task_sub.tsk_stat`：

| code | 枚举 | 中文 |
|------|------|------|
| 0 | PENDING_START | 待启动 |
| 1 | FINISHED | 已完成 |
| 2 | FAILED | 失败 |
| 3 | RUNNING | 执行中 |
| 4 | SKIPPED | 已跳过 |

旧码读兼容（摘要）：旧 4→主 10；旧 5/0→主 20 或 30 / 子 0；旧 3/6/7→主 30 / 子 3；旧 8→主 40（orderAct≠0→50）/ 子 1；旧 1→主 60 / 子 1；旧 2→主 90 / 子 2。读路径强制走 `TaskStatCompatMapper`。

### 4.4 全阶段主链路（Wave G 定稿）

```text
任务预检 → 任务下发 → [阶段子任务链] → 结果回收 → 稽核完成 → 任务结束
```

| tskPhase | 阶段子任务链（互斥选一支） |
|----------|---------------------------|
| 0 潜在预警 | 关联分析 |
| 1 排查 | 漏洞扫描 |
| 2 验证 | 漏洞扫描（1026=主扫+交叉扫双厂家；非1026 单条，不再产二次扫描） |
| 3 修复 | 漏洞修复 |
| 4 核验 | 连通性检测 → 修复核验 |

### 4.5 流程实例（Wave L 定稿）

主任务 1:1 流程实例 + 节点实例，关键状态变迁写库；步骤条优先读库，`TaskLifecycleResolver` 推导作兼容兜底。

| 数据 | 权威落点 |
|------|----------|
| 当前节点、节点状态、执行时间线 | **`vul_task_proc_inst` / `vul_task_proc_node`** |
| 编排阶段码 | **节点表 `node_code`（CHAIN）为权威**；`sub.wave` 过渡冗余 |
| 扫描执行（设备/资产/报告/进度） | `vul_scan_task_sub` |

写库时机：`dispatch` 成功建实例并展开链节点（预检节点记成功）；连通性终态 spawn 修复核验推进；回收/稽核/结束依次推进；失败记节点 status=3。写库与业务事务同边界。

---

## 5. 接口与页面

### 5.1 API 清单

| 方法 | 路径 | 说明 | 前端封装键 |
|------|------|------|------------|
| POST | `/vul-pass/vul-scan-task/pre/dispatch` | 编排预览（plan + confirmToken） | `getVulnScanTaskPreDispatch` |
| POST | `/vul-pass/vul-scan-task/dispatch` | 确认下发（需 confirmToken） | `saveVulnScanTaskDispatch` |
| POST | `/vul-pass/vul-scan-task/preview` | 导入文件预览 | `previewVulnScanTask` |
| POST | `/vul-pass/vul-scan-task/recycle` | 离线报告回收 | `getVulnScanTaskRecycle` |
| POST | `/vul-pass/vul-scan-task/recycle/auto` | 自动回收 | `getVulnScanTaskRecycleAuto` |
| POST | `/vul-pass/vul-scan-task/submit` | 稽核完成 / 工单回传 | `submitVulnScanTaskSub` |
| GET | `/vul-pass/compliance/verify-fix/metrics` | 存活一致性等指标（P3 可选） | 待新增 |
| POST | `/vul-pass/vul-scan-task/auto-dispose/preview` | 自动化处置队列预览 | `previewVulnScanTaskAutoDispose` |
| POST | `/vul-pass/vul-scan-task/auto-dispose` | 启动自动化处置 | `startVulnScanTaskAutoDispose` |
| GET | `/vul-pass/vul-scan-task/auto-dispose/{runId}` | 查询进度 | `getVulnScanTaskAutoDispose` |
| POST | `/vul-pass/vul-scan-task/auto-dispose/{runId}/pause` | 暂停 | `pauseVulnScanTaskAutoDispose` |
| POST | `/vul-pass/vul-scan-task/auto-dispose/{runId}/resume` | 继续 | `resumeVulnScanTaskAutoDispose` |
| POST | `/vul-pass/vul-scan-task/auto-dispose/{runId}/notify` | 子任务终态通知 | — |

### 5.2 预览与确认（preDispatch）

- 响应 `summary`：实例数、按 src_method 统计、物理子任务总数、`allDevicesMatched`；`confirmToken` 30 分钟有效。
- 每个 group 返回：
  - `groupKey`：全局唯一子任务标识，用于 dispatch 时精确映射设备分配。
  - `engHash` / `engName` / `engType`：默认自动匹配设备。
  - `candidateEngHashes[]`：满足该子任务策略 engType bit 且受 `eng_hash_cnt` 池约束的候选设备列表。
- 确认下发前允许在候选池内调整每个子任务的 `engHash`；**禁止**增删子任务、修改策略类/批次/实例集合。
- 任一 group 无可用候选设备时前端禁用确认；用户未分配设备时按默认自动匹配值下发。
- 确认下发携带 `confirmToken` + `groupEngHashAssignments`；后端校验 token + 设备在候选池内且满足 engType → 落库，写 opCode=9。
- 预览行 = 一条物理子任务；dispatch 阶段只落 Gate 波（sequential 模式 Scan 波待 Gate 回收后动态派生）。

### 5.2.1 缓存与一致性策略（绝对安全）

**核心原则**：

1. **一份 plan 只对应一个 confirmToken**：token 是 plan 的唯一句柄，plan 是 token 的唯一内容。
2. **token 强归属**：token 与 `用户 + 会话 + 工单` 绑定，无法伪造、无法跨会话共享。
3. **原子化消费**：dispatch 是"查-验-写-删"的原子操作，中间状态加分布式锁。
4. **成功即销毁**：dispatch 成功必须立即删除 plan；失败保留但限制重试；过期由 Redis 兜底清除。
5. **强一致性优先于可用性**：Redis 异常时拒绝 dispatch，不允许降级重新生成 plan。

**confirmToken 设计**：

```text
confirmToken = Sign(userId + ":" + sessionId + ":" + tenantId + ":" + orderId + ":" + timestamp + ":" + nonce)
```

- 服务端解析 token 即可知归属；防止伪造和跨会话共享。
- 同一用户同一工单每次 preview 生成新 token，旧 token 不覆盖、自然过期。

**Redis Key 结构**：

| Key | 用途 | TTL |
|------|------|-----|
| `vul:dispatch-plan-cache:plan:{confirmToken}` | 缓存 preview 生成的 plan | 30 分钟 |
| `vul:dispatch-plan-cache:dispatched:{confirmToken}` | 幂等标记，防止重复下发 | 7 天 |
| `vul:dispatch-plan-cache:lock:dispatch:{confirmToken}` | 分布式锁，防止并发 dispatch | 30 秒 |

**Plan 缓存 Value 结构**：

```json
{
  "version": 1,
  "checksum": "sha256(planJson)",
  "createdAt": "2026-07-21T10:00:00Z",
  "ttlSeconds": 1800,
  "owner": { "userId": "...", "sessionId": "...", "tenantId": "...", "orderId": "..." },
  "status": "PREVIEWED",
  "dispatchAttemptCount": 0,
  "maxDispatchAttempts": 3,
  "plan": { "groups": [ ... ] }
}
```

**添加策略（preDispatch）**：

1. 生成签名 confirmToken。
2. 构建 CachedPlan，计算 plan 内容 checksum。
3. Redis `SET NX EX` 写入：`vul:dispatch-plan-cache:plan:{confirmToken}`，TTL 30 分钟。
4. key 冲突时拒绝覆盖，提示重新预览。

**查询策略（dispatch）**：

1. 解析并校验 confirmToken 签名与归属。
2. 查 Redis 获取 CachedPlan；不存在则报错"预览已过期，请重新预览"。
3. 校验 checksum，反序列化失败或校验不通过则拒绝下发。
4. 二次校验 value 中的 owner 与当前请求一致。
5. 校验 status = `PREVIEWED`；校验 `groupEngHashAssignments` 中每个 engHash 在该 group 的 `candidateEngHashes` 中。

**删除/销毁策略**：

| 场景 | 操作 |
|------|------|
| dispatch 成功 | 立即原子删除 plan key，并设置幂等 key |
| dispatch 业务失败 | status → `FAILED`，`dispatchAttemptCount++`；保留 plan 允许重试 |
| dispatch 失败超限 | 删除 plan key |
| 用户主动取消/关闭抽屉/切换工单 | 前端调 cancel API 删除 plan key |
| token 自然过期 | Redis TTL 自动清除 |

**原子消费脚本（Lua）**：

```lua
if redis.call('exists', KEYS[1]) == 1 then
    redis.call('setex', KEYS[2], 604800, '1')
    redis.call('del', KEYS[1])
    return 1
else
    return 0
end
-- KEYS[1] = vul:dispatch-plan-cache:plan:{confirmToken}
-- KEYS[2] = vul:dispatch-plan-cache:dispatched:{confirmToken}
```

**并发控制**：

- dispatch 前获取分布式锁 `vul:dispatch-plan-cache:lock:dispatch:{confirmToken}`。
- 锁获取失败返回"下发进行中，请勿重复提交"。
- 幂等 key 已存在时直接拒绝重复提交。

**异常处理**：

- **Redis 不可用**：直接拒绝 dispatch，提示"系统繁忙，请重新预览"；不允许降级重新生成 plan。
- **plan 反序列化/checksum 失败**：拒绝 dispatch，要求重新预览。
- **owner 不匹配**：拒绝 dispatch，防止跨会话共享。

### 5.3 预览 UI 规格

| 列名 | 数据 | 展示规则 |
|------|------|----------|
| 策略类 | `strategyClass` | 漏洞扫描型 / POC·BAS型 / 连通性核验型 |
| 原修复方式 | `srcMethods[]` | 白底描边 Tag + `SetName`/`VulProcessMethod`（多值多个 Tag） |
| 核验方式 | `procMethod`（子任务实际手段） | 与原修复方式同一套白底描边 Tag 样式 |
| 安全资源 | `engHash`（可编辑 Select） | 默认展示自动匹配设备；点击下拉从 `candidateEngHashes` 中选择；未匹配/候选池空红标 |
| 漏洞实例数 | `instanceCount` | 本组系统漏洞实例条数 |
| IP 数 | `uniqueIpCount` | assetIps 去重后数量；astUnitNum 切批依据 |
| 核验过程 | `evidenceCapabilities[]` | Tag：连通性 / 端口 / 补丁·版本 / POC / BAS 等 |
| 警告 | `warnings[]` | 有则橙标 |

- 无「建议导入报告」列（报告类型仅在处置抽屉选择）。
- `allDevicesMatched=false`（任一子任务无可用候选设备）→ 禁用「确认下发」；有 `eng_hash_cnt` 时提示「受跨级联动指定设备池约束」。

### 5.3.1 设备分配交互（方案 A：行内快捷分配 + 智能批量填充）

**定位**：最小改动、最贴近现有表格交互的设备分配方案。

**行内编辑：**

- 预览表「安全资源」列每行渲染为 `Select` 组件：
  - 默认选项 = 后端自动匹配结果（`engHash`）。
  - 下拉选项 = 该子任务 `candidateEngHashes`（已按策略 engType bit + `eng_hash_cnt` 强制池过滤）。
  - 选项展示：`engName + engTypeLabel + devIp`（多行友好）。
  - 选中项不满足 engType 时红标并禁用确认。
- 用户切换设备后，前端仅更新本地 `groupEngHashAssignments` Map，**不实时调用后端写缓存**。

**顶部批量操作按钮：**

| 按钮 | 行为 |
|------|------|
| **按自动策略重填** | 所有子任务恢复后端默认匹配值 |
| **按策略类批量应用** | 选择一个设备 → 自动应用到所有同策略类（同 engType bit 需求）的子任务；若某子任务候选池不含该设备则跳过并标红 |
| **清空所选** | 清空手动选择，恢复默认；清空后任一子任务无设备则禁用确认 |

**状态提示：**

- 全部子任务有设备 → `allDevicesMatched=true`，确认按钮可用。
- 存在子任务候选池为空 → 该行红标，顶部 Alert 提示「N 个子任务无可用安全资源，请维护设备后重新预览」。
- 用户手动选择后，行尾显示「已手动」小 Tag，便于识别。

**一致性保障：**

- 用户选择只存在前端内存，点击「确认下发」时随 `confirmToken` 一起回传 `groupEngHashAssignments`。
- 后端从 Redis 取出缓存 plan，按 `groupKey` 校验 `engHash ∈ candidateEngHashes`，校验通过后落库。
- 禁止增删子任务、修改策略类/批次/实例集合。

### 5.4 任务详情工作台 UI 定稿

> **原型**：`svmp/docs/internal/verify-fix-修复核验全链路/prototypes/修复核验-任务详情工作台-原型.html`（交互定稿）。

**信息架构（两层模式）：**

| 模式 | 触发 | 布局 |
|------|------|------|
| **列表 + 行内摘要** | 主任务列表点击行（再次点击收起） | 行下轻量嵌入主任务摘要（字段网格 + 核验状态机步骤 + 快捷入口） |
| **任务全页** | 行内快捷入口 / 操作列「详情·结果·台账」 | 上部主任务摘要固定；下部四标签：概览 / 子任务 / 下发详情 / 结果摘要 |

**主任务列表定稿：**

- 展示列：序号、任务ID、任务状态、稽核状态、资产单元、排查资产/产品漏洞/弱口令、创建时间、操作。
- **不展示**「处置方式」「工单业务阶段」（改在摘要/全页查看）。

**主任务摘要（MainTaskSummary）定稿：**

- 上行：身份/状态 Tag（处置方式、业务阶段、任务状态、任务模式、稽核状态；枚举全文；无标题 Tag 悬停显示 `属性名：完整值`）。
- 下行：指标流式排列（资产单元、排查资产、产品漏洞、弱口令、创建时间；有则附带 confirmToken、src_method 分布）。
- 长字段（confirmToken 等）与其它指标同一 flex 行，`flex: 1 1 280px`，不单独占满一行。
- 数值：短数字/时间蓝色 `#1890ff` 常规字重；长串深灰 `#595959` 可换行。
- 容器与子任务卡片统一 `padding: 12px 14px`；顶栏已有主任务 ID 时摘要内不重复。

**核验状态机（仅 procMethod=1060/1061）：**

- 步骤：任务预检 → 任务下发 → [阶段子任务链] → 结果回收 → 稽核完成 → 任务结束。
- 有 `lifecycleSteps` 时始终展示；后端未返回时前端按 `tskPhase` 兜底。
- 已完成步骤静态；当前/未完成步骤数字可闪（仅 `opacity`）；数字正体无倾斜。

**任务全页四标签定稿：**

| Tab | 内容 |
|-----|------|
| 概览 | 基础信息 KV + 审计时间线（台账摘要） |
| 子任务 | 纵向卡片列表（见下） |
| 下发详情 | **仅**范围明细（复用 TaskInfoDrawer 嵌入）；不堆与摘要重复的 KV |
| 结果摘要 | Tab 切换：任务结果 \| 台账日志 |

**子任务卡片（SubTaskCardList）定稿：**

- 顶栏：子任务 ID（边框盒，高约 22px）+ Tag 区 + 进度。
- Tag：编排阶段（wave）、处置方式（子任务 procMethod=实际手段）、处置类型（reportType，若有）、任务状态；**不展示 tskType、不展示「阶段」**。
- 指标：资产/实际、实际产品漏洞、设备匹配；engHash 与指标同一行（`flex: 1 1 280px`，`#595959` 全文）。
- 操作：任务详情 / 追踪 / 结果 / 台账；`tskStat≠1` 且非跳过时显示「去处置」。
- 进度口径：`tskProgress` 0/1 →「未执行/已完成」；1～100 →「进度 n%」。
- 悬浮：无标题 Tag、ID、长串均支持「属性：值」提示。

**子任务全页（SubTaskWorkbench）：**

- 顶栏「← 返回子任务列表」+ `子任务 {id} · {当前 Tab 名}`；全宽展示。
- Tab：任务详情（系统漏洞/资产/产品漏洞/弱口令范围 + 底部「处置」）/ 任务结果 / 台账日志 / 任务追踪。
- 从「结果/台账」入口进入时仅展示「任务结果 | 台账日志」两 Tab。

**处置弹窗（复用 ProMethodDrawer）：**

| 字段 | 规则 |
|------|------|
| 技术处置方式 | 继承主任务 `procMethod`，**禁用**（1060/1061） |
| 漏洞业务阶段 | 继承子任务/主任务 `tskPhase`，**禁用** |
| 处置类型 | `VulReportTypeEnum` 可选；1060/1061 默认 **32**；考核/生产路径仍支持 **10 / 3**；子任务已落库 reportType 优先 |
| 上传文件 | `upload=1` 的类型显示上传区 |
| 资产匹配方式 | `MatchAssetRuleEnum` 多选 |
| 智能稽核 | reportType 为 10/11/23 时可改，其余默认勾选 |

**视觉与实现约定：**

```text
短指标值 #1890ff / 长串值 #595959（word-break: break-all）
处置 vs 核验 Tag：volcano vs geekblue，禁止同色
业务字段禁止 CSS/代码省略号截断（产品未书面同意前）
在 TaskDrawer.vue 上扩展，不新建独立路由；复用 TaskInfoDrawer/ProMethodDrawer/LogLedgerDrawer/SearchTask
前后端状态码以后端枚举为唯一数据源；颜色/标签一律按 code 查找，禁止用状态码做数组下标
```

**改版自检清单：**

1. 主任务列表无「处置方式 / 工单业务阶段」列
2. 摘要 Tag 不贴顶；confirmToken 不独占整行
3. 短值蓝、长串灰；无浅蓝数值底框
4. 子任务无「阶段」；有处置方式 Tag；engHash 同行
5. 下发详情无重复 KV
6. 状态机：进行中当前步可闪、完成步不闪
7. 相关文件 `npm run lint:nofix` 通过

### 5.5 统一预览 dispatchPlan（Wave M / Wave Q，**已落地**）

> 来源：《任务下发页面整改方案 v2.0》（已采纳并合入；原件已归档至 `svmp/docs/internal/verify-fix-修复核验全链路/_archive/design/`）。Wave Q（v2.1.0）进一步统一为全阶段通用 `DispatchPlan` 模型。

- **已定稿口径**：`/pre/dispatch` 出参归一为**单一 `dispatchPlan`**（`DispatchPlanAssembler.fromDispatchPlan` 装配）——核验阶段（4）以 `verifyFixPlan`（`VerifyFixDispatchPlanner`）为唯一权威产出；阶段 0～3 由阶段子任务链预览产出；`PhaseDispatchPreviewBuilder` 在阶段 4 不再产生示意行，下发裁决权（`canConfirm`）归唯一 plan。
- **Wave Q 模型统一**（v2.1.0）：`VerifyFixDispatchPlan` -> `DispatchPlan`（含 `DispatchPlanGroup` / `DispatchPlanSummary`），消除 `PhaseDispatchPreviewVO` / `PhaseDispatchPreviewRowVO`；`DispatchPlanGroup` 扩展全阶段字段（修复核验物化字段 + 阶段0-3 展示字段）；`DispatchPlanAssembler` 合并为 `fromDispatchPlan` 单一入口；`PhaseDispatchPreviewBuilder` 改输出 `DispatchPlan`。详见 §5.7。
- 阶段 0～4 均有下发前预览表（一行 = 一条将下发的物理子任务）；跨级联动按 AstUnitNum 自动切批；1026 交叉扫描必须选择两个不同厂家扫描器（`role` 标注）。
- **批次口径统一**（Wave N，已落地）：`ast_unit_num` 阶段 0～3 与阶段 4 统一按 IP 维度切批；预览/下发同口径；1060 批次列对多批场景显示。详见 `04-子PRD与规格/任务下发批次口径统一-按IP拆分-开发计划-v1.0.md`。

### 5.6 前端落点（`asset-newleak-manage`）

| 类型 | 路径 | 说明 |
|------|------|------|
| 路由/入口 | `/VulnManagePlat/OrderManage/SysVulnOrder` | 系统漏洞工单主入口（含核验 34） |
| 路由 | `/VulnManagePlat/TaskManage/GangedTask` | 跨级联动（含 1063 核验） |
| 下发抽屉 | `VulnManagePlat/components/TaskSend/AddTaskDrawer.vue` | 确认下发 + confirmToken |
| 基础信息 | `.../TaskSend/BaseInfo.vue` | preDispatch 策略类 groups |
| 预览组件 | `.../TaskSend/DispatchPlanPreview.vue` | 统一下发预览（全阶段通用；per-group a-select 设备选择 + tooltip 设备详情） |
| 设备选择 | ~~`.../TaskSend/SafeSourceDriver.vue`~~ / ~~`.../TaskSend/DualVendorScannerPick.vue`~~ | Wave S 移除预览页引用，设备选择全走 `DispatchPlanPreview` per-group a-select |
| 任务抽屉 | `.../TaskDetails/TaskDrawer.vue` | 主/子任务列表与工作台宿主 |
| 工作台组件 | `MainTaskSummary.vue` / `SubTaskCardList.vue` / `SubTaskWorkbench.vue` / `ResultSummaryPanel.vue` | §5.4 定稿 |
| 离线处置 | `.../TaskDetails/ProMethodDrawer.vue` | reportType 默认 3/10/32；preview→submit |
| 自动化处置 | `.../TaskDetails/AutoDisposeDrawer.vue` | 队列预览 + 在线一键 / 离线有序批量导入 |
| API | `src/api/Assembly/NewLeakVulnInfo.js` | plan/confirmToken；`changeTskPhase` 与 token 同步 |

**页面交互要点：**

1. 按钮仅「确认下发」「取消」；无合法设备时禁用确认。
2. 处置：选 `VulReportTypeEnum`（考核默认 10，生产默认 3）→ 上传一份完整报告 → recycle → 看分层判定。
3. proc_method=1060 展示「自适应」；工单指定 1020/1027 时只读展示覆盖结果。
4. confirmToken：父组件须在 `changeTskPhase`/预览回写后保留 token，下发必带。全阶段（0-4）预览均返回 confirmToken，下发均携带 confirmToken（Wave Q）。

### 5.7 全阶段下发模型统一与缓存策略（Wave O/P/Q/R，v2.1.0 补充）

> 本节补录 2026-07-22 会话完成的架构改造：全阶段下发模型统一、全阶段缓存化、统一设备匹配、缓存数据结构优化、设备选择增强（tooltip/弱口令/交叉扫描双厂商/移除设备列表）。对应开发计划 v3.0 Wave O/P/Q/R/S。

#### 5.7.1 全阶段下发模型统一

**核心目标**：消除修复核验（阶段4）与阶段0-3 的模型分离，`DispatchPlan` 成为全阶段通用下发模型。

| 改造点 | 改造前 | 改造后（Wave Q） |
|--------|--------|------------------|
| 下发模型 | `VerifyFixDispatchPlan`（阶段4）/ `PhaseDispatchPreviewVO`（阶段0-3） | `DispatchPlan`（全阶段通用，含 `DispatchPlanGroup` / `DispatchPlanSummary`） |
| 阶段0-3 VO | `PhaseDispatchPreviewVO` / `PhaseDispatchPreviewRowVO` | 消除，阶段0-3 直接产出 `DispatchPlan` |
| Group 字段 | 修复核验与阶段0-3 字段分离 | `DispatchPlanGroup` 扩展全阶段字段（修复核验物化字段 + 阶段0-3 展示字段） |
| 装配入口 | `fromPhasePreview` / `fromVerifyFixPlan` 两条路径 | `DispatchPlanAssembler.fromDispatchPlan` 单一入口 |
| 预览构建器 | `PhaseDispatchPreviewBuilder` 输出 `PhaseDispatchPreviewVO` | `PhaseDispatchPreviewBuilder` 输出 `DispatchPlan` |
| 缓存 plan 类型 | `VerifyFixDispatchPlan` | `DispatchPlan`；`verifyFixFlow` 标志控制物化路径 |

**物化保留两套**（按 `verifyFixPlan != null` 选择）：

| 物化路径 | 驱动 | 适用场景 |
|----------|------|----------|
| `buildSubTasksFromDispatchPlan` | `plan.groups` | 修复核验门闸物化（阶段4，1028 Gate -> 条件 Scan） |
| `astUnitHandle` | `assetList`（按 IP 分批） | 全阶段通用物化（阶段0-3） |

**去 VerifyFix 命名**（非门闸专属类统一改名）：

| 改造前 | 改造后 |
|--------|--------|
| `VerifyFixPlanCache*` | `DispatchPlanCache*`（Repository/Validator/Service） |
| `IVerifyFixDispatchLock` | `IDispatchLock` |
| `VerifyFixDeviceAssignmentValidator` | `DispatchDeviceAssignmentValidator` |
| `VerifyFixDispatchMode` | `DispatchMode` |
| 配置 `vul.verify-fix-plan` | `vul.dispatch-plan-cache` |
| Redis key `vul:verify-fix-plan:` | `vul:dispatch-plan-cache:` |

**保留 VerifyFix 命名**（1028 门闸专属，不改动）：`VerifyFixDispatchPlanner`、`VerifyFixInstanceValidator`、`VerifyFixStrategyResolver`、`VerifyFixSubTaskKind`、`VerifyFixAliveConsistencyChecker`、`VerifyFixVerdictService`、`VerifyFixAutoDispose*`、`isVerifyFixFlow`。

#### 5.7.2 全阶段缓存策略

**核心策略**：所有阶段（0-4）preDispatch 生成 confirmToken + 缓存，dispatch 从缓存消费；保留旧路径 fallback（缓存未命中时走原 dispatch 逻辑）。

| 阶段 | preDispatch | dispatch |
|------|-------------|----------|
| 0-3（排查/验证/修复） | 生成 confirmToken + 写缓存（`DispatchPlan` + `PreviewContext`） | 从缓存消费（校验 owner/token/status + CAS consume）；缓存未命中走旧路径 |
| 4（核验） | 生成 confirmToken + 写缓存（`DispatchPlan` + `PreviewContext`） | 从缓存消费（校验 owner/token/status + 设备分配 + CAS consume）；缓存未命中走旧路径 |

**配置开关**：`vul.dispatch-plan-cache.enabled`（默认 false），关闭时所有阶段走旧 dispatch 逻辑。

**DDD 下沉**（Wave P）：缓存相关 15 个方法从 `VulScanTaskAppServiceImpl` 下沉到 `VulScanTaskDomainServiceImpl`；新增 `DispatchParam` 领域参数对象替代 `VulTaskDispatchDTO` 传入 DomainService。AppService 保留 `buildOwner`/`resolveSessionId`/auto-dispose 编排/DTO 装配。

**跨级切批语义修正**（Wave P）：从「按资产拆多主任务」改为「一个主任务多子任务」。`plan.groups` 按 `astUnitNum` 切批（含 `batchIndex`），由 `buildSubTasksFromDispatchPlan` 物化多子任务。删除 `dispatchGangedBatches` / `sliceGangedBatches` / `VerifyFixPlanBatchSlicer`。

#### 5.7.3 统一设备匹配策略（EngDeviceMatcher 全阶段唯一入口）

**核心策略**：`EngDeviceMatcher` 作为阶段0-4 统一设备匹配入口，阶段0-3 不再各自实现设备匹配。

**procMethod -> tskType -> engType bit 映射**：

| procMethod | tskType | engType bit | 设备类型 |
|------------|---------|-------------|----------|
| 1028 | CONNECTIVITY(11) | 16 | 连通性探测工具 |
| 1021 | POC(14) | 4 | POC引擎 |
| 1022 / 1027 / 1026 | VERSION_LOGIN(13) | 1 | 主机扫描器 |
| 1030 / 1031 / 1032 | WEAK_PASSWORD(16) | 8 | 弱口令工具 |
| 1061 | BAS(15) | 32 | BAS设备 |

> Wave S 补充：1026（交叉扫描验证）-> VERSION_LOGIN(13) -> bit 1；1030（字典组合暴破）/1031（规则猜测暴破）/1032（配置文件分析）-> WEAK_PASSWORD(16) -> bit 8。`TskTypeEnum` 新增 `WEAK_PASSWORD(16, "弱口令扫描")`；`EngDeviceMatcher` 新增 `ENG_WEAK_PASSWORD=8`/`ENG_WEB_SCANNER=2` 常量。

**设备类型 bit 定义**（与 §3.5 一致，完整 7 项）：

| bit 值 | 含义 | EngDeviceMatcher 常量 | 对应 procMethod |
|--------|------|----------------------|-----------------|
| 1 | 主机扫描器 | `ENG_HOST_SCANNER` | 1022 / 1027 / 1026 |
| 2 | WEB 扫描器 | `ENG_WEB_SCANNER` | （预留，Wave S 定义常量） |
| 4 | POC 引擎 | `ENG_POC` | 1021 |
| 8 | 弱口令工具 | `ENG_WEAK_PASSWORD` | 1030 / 1031 / 1032 |
| 16 | 连通性探测工具 | `ENG_CONNECTIVITY` | 1028 |
| 32 | BAS 设备 | `ENG_BAS` | 1061 |
| 0 | 其他 | - | - |

- 匹配判定（禁止等值）：`(eng_type & requiredBit) != 0`。
- 阶段0-3 也用 `EngDeviceMatcher.matchRequired` 生成 `candidateDevices` + `defaultEngHash`。
- `candidateDevices` 填充设备详情：`CandidateDevice` 内部类（`engHash`/`engName`/`vendor`/`devIp`/`engType`/`engTypeLabel` + Wave S 新增 `engTypeLabels`（全部设备类型标签列表）/`status`（注册状态：0-在线/-1-离线）），前端 a-select 直接展示。
- `EngDeviceMatcher.engTypeLabels(int engType)` 遍历 6 bit（1/2/4/8/16/32）展开全部类型标签，供前端 tooltip 展示设备全部类型。
- 候选池约束：工单 `eng_hash_cnt` 非空 -> 强制仅池内（仍须满足 engType bit）；否则全量可用设备。

#### 5.7.4 全阶段设备选择

**交互设计**：全阶段（0-4）预览表「安全资源」列均渲染为 `a-select` 组件。

| 要素 | 规则 |
|------|------|
| 默认选项 | 后端 `EngDeviceMatcher.matchRequired` 匹配首选 `defaultEngHash`，前端默认选中 |
| 下拉选项 | 该子任务 `candidateDevices`（已按策略 engType bit + `eng_hash_cnt` 强制池过滤） |
| 选项展示 | `engName（vendor / devIp）`；Wave S 新增 `a-tooltip` 悬浮显示设备详情（HASH + 全部设备类型 `engTypeLabels` + 注册状态 `status`） |
| 用户切换 | 仅更新前端 `groupEngHashAssignments` Map，不实时调用后端写缓存 |
| 确认下发 | 随 `confirmToken` 一起回传 `groupEngHashAssignments`；后端从缓存校验 `engHash` 在 `candidateDevices` 内 |

- 全阶段统一：阶段0-3 与阶段4 使用相同的设备选择交互，不再有差异化处理。
- 无可用候选设备时该行红标，禁用确认下发。

**a-select tooltip 设备详情（Wave S）**：

每个 `a-select-option` 外层包裹 `a-tooltip`，悬浮显示：
- HASH：设备 engHash 完整值。
- 设备类型：`engTypeLabels` 全部展开（如设备 engType=3 则显示「主机扫描器，WEB扫描器」）。
- 注册状态：`status=0` 显示「在线」，`status=-1` 显示「离线」。

**交叉扫描双厂商默认设备（Wave S）**：

1026 交叉扫描验证需选择两个不同厂家的扫描器，系统自动分配不同厂商默认设备：

| 环节 | 规则 |
|------|------|
| 后端默认分配 | `PhaseDispatchPreviewBuilder.adjustCrossScanDualVendor`：填充设备后调整交叉扫 group 的 `defaultEngHash` 为不同厂商设备；无不同厂商设备时至少选不同设备（`DualVendorScannerGuard` 报厂家相同） |
| 前端冲突校验 | `crossScanConflict` 检测同厂商/同设备冲突：主扫与交叉扫 engHash 相同 -> 「不能是同一台设备」；厂商相同 -> 「要求两个不同厂家的扫描器」；冲突时禁用确认下发 |
| 1026 映射 | `procMethodToTskType` 补 1026 -> VERSION_LOGIN(13) -> ENG_HOST_SCANNER(1)（Wave S 修复缺失映射） |

**移除预览页设备列表组件（Wave S）**：

- 移除预览页 `SafeSourceDriver` + `DualVendorScannerPick` 组件引用。
- 设备选择全部走 `DispatchPlanPreview` 的 per-group `a-select`，不再有独立的设备列表区域。
- `saveorSubmit` 从 `groupEngHashAssignments` 提取设备 hash；1026 主扫/交叉扫分别提取 `primaryEngHash`/`crossEngHash`。

#### 5.7.5 缓存数据结构

**PreviewContext.assetList 优化**：

| 改造前 | 改造后（Wave R） |
|--------|------------------|
| 完整 `VulTaskDispatchAssetDTO` 列表 | `List<VulScanTaskSubAssetDO>`（按 IP 分组紧凑存储） |

紧凑存储结构（与 `vul_scan_task_sub_asset` 表一致）：

| 字段 | 说明 |
|------|------|
| `assetIp` | 资产 IP |
| `assetInfo` | 资产 ID 列表（同一 IP 多资产合并） |
| `astNum` | 资产数量 |
| `targetPortFileLoc` | 目标端口文件位置 |

**其他优化**：

| 优化项 | 说明 |
|--------|------|
| `assetIps` 去重 | `buildBaseGroup` 用 `LinkedHashSet` 去重 IP |
| `DispatchAssetGrouper` | 新建类，提取 IP 分组逻辑（从 `convertAssetListGroupBy`/`convertSubAssetList` 中抽出） |
| `VulScanTaskDO.subAssetList` | 增加 `transient` 字段，缓存路径传递紧凑资产列表 |
| `astUnitHandle` 缓存路径兼容 | `subAssetList` 非空时直接用，跳过 `convertAssetListGroupBy`/`convertSubAssetList`；旧路径（subAssetList 为空）不变 |

**CachedPlan Value 结构**（v2.1.0 更新）：

```json
{
  "version": 1,
  "checksum": "sha256(planJson)",
  "createdAt": "2026-07-22T10:00:00Z",
  "ttlSeconds": 1800,
  "owner": { "userId": "...", "sessionId": "...", "tenantId": "...", "orderId": "..." },
  "status": "PREVIEWED",
  "dispatchAttemptCount": 0,
  "maxDispatchAttempts": 3,
  "previewContext": {
    "orderContext": { "...": "工单上下文" },
    "userParams": { "...": "用户参数" },
    "assetList": [ { "assetIp": "10.0.0.1", "assetInfo": "id1,id2", "astNum": 2, "targetPortFileLoc": "..." } ],
    "vulInstList": [ { "...": "系统漏洞实例" } ],
    "forcedEngHashes": ["hash-1", "hash-2"]
  },
  "plan": { "groups": [ ... ], "summary": { ... } }
}
```

> `plan` 字段类型从 `VerifyFixDispatchPlan` 改为 `DispatchPlan`（Wave Q）。

---

## 6. 验收标准（交付门禁）

### 6.1 功能

- [ ] 仅 stat=5 且 src_method∈105x 进入编排
- [ ] 1060 工单：先 Gate(1028)，1052/1053 Gate 后结案；1050/1051 仅存活进入二次 Scan
- [ ] 1052/1053：目标仍存活 → **stat=7**；不可达 → **stat=6**；无法判定 → 10
- [ ] 1050/1051 不存活 → **stat=10**，且不得生成/不得采纳二次技术「通过」结论
- [ ] 未 confirm 的 dispatch 拒绝；每条物理 subTask（Gate/Scan）写完整 9+10
- [ ] Gate 的 opCode=10 必含 `onlineAddrFileLoc`；外壳 logType=1060，内层手段 1028/1020…
- [ ] 台账 logType ← 主任务 procMethod；实例/rela srcMethod ← 子任务 procMethod

### 6.2 合规

- [ ] 排查 onlineAddr 覆盖 vulNetAddr
- [ ] 存活一致性 ≥80%（靶标；口径见 §3.6）
- [ ] logNum = 物理 subTask 数 × 2

### 6.3 非功能

- [ ] feature flag 关闭走 legacy
- [ ] 50 实例预览 < 5s
- [ ] 任务详情工作台交互符合 §5.4

### 6.4 测试用例

| 用例 ID | 场景 | 期望 |
|---------|------|------|
| TC-01 | 仅 1050 且全存活，astUnitNum=-1 | **1 Gate + 1 VUL_SCAN** |
| TC-02 | 1050+1051 全存活，-1 | **1 Gate + 1 VUL_SCAN + 1 POC_BAS** |
| TC-03 | 1050+1051+1052+1053 全存活，-1 | **1 Gate + 2 Scan**（1052/1053 无二次） |
| TC-04 | astUnitNum=2 切 IP | Gate/Scan 各自按 IP 批增加 |
| TC-05 | 1053 实例目标不可达 | **stat=6** |
| TC-06 | 1052 漏洞端口仍 open | **stat=7（未修复）** |
| TC-07 | 1050 不存活 | **stat=10**，无二次 Scan 或无技术通过 |
| TC-08 | 1050 存活且未再检出 | 二次手段后 **stat=6** |
| TC-09 | 无 confirmToken 下发 | 拒绝 |
| TC-10 | 排查 onlineAddr | ⊇ vulNetAddr |
| TC-11 | 台账 logType=1060 且 Gate 内层=1028；主=1060、子=1028 | 对齐接口测试注 |
| TC-12 | Gate 完成后，1050/1051 全不存活 | 不生成 Scan 子任务；该批实例 stat=10 |
| TC-13 | Gate 完成后，1050 部分存活；跨级 eng_hash_cnt 非空仅从池内选设备 | 仅存活实例生成 Scan；池内无 bit 匹配禁止确认 |
| TC-14 | 离线完整报告一次性导入 | 写 Gate+Scan 各自完整 9+10；分别有 1028 和 1020…/1021 内层手段 |

---

## 7. 术语表与已冻结决策

### 7.1 术语表

| 词 | 含义 |
|----|------|
| 实例 **src_method**（修复史） | 修复阶段源处置方式 **1050–1053**（实例上记录「怎么修的」） |
| **主任务** `proc_method` | **外壳**：工单约定技术处置方式（核验多为 **1060**；修复工单可为 **105** 等） |
| **子任务** `proc_method` | **实际手段**：本物理子任务真正执行的方式（核验 Gate=**1028**、Scan=**1022/1021…**；修复下发=**1050–1053**） |
| 台账 **logType** | **始终取自主任务** `proc_method`（部侧外壳） |
| 实例/rela **srcMethod**（回传内层） | 核验等拆分场景取自 **子任务** `proc_method`；排查主子一致时可同源 |
| **wave** | 编排阶段：CONNECTIVITY_CHECK（连通性检测）/ REPAIR_VERIFY（修复核验） |
| **tsk_type** | 任务类型（设备 engType 匹配粒度）：11/13/14/15 |
| **dispatchMode** | 下发模式：sequential（默认）/ parallel（§3.9） |
| expect_alive / actual_alive / alive_consistent | 策略预期存活 / 导入实测存活 / 二者一致性（考核口径） |

> **已废弃**：子任务字段 `verify_src_method` / API `verifySrcMethod`（职责并入子任务 `proc_method`，Wave K 已删除）。

### 7.2 已冻结决策表

| # | 决策 |
|---|------|
| Q7 | XLSX 推断存活允许 INFERRED |
| Q9 | LastScanner 范围仅排查 102x |
| Q10 | 1052/1053 台账：logType←主任务 1060；内层←子任务 1028 |
| Q11 | 物理子任务模型：允许 1028 Gate → 条件 Scan；禁止 PORT 半截台账 |
| Q12 | 1052/1053 检测：仅 1028 连通性；Gate 后结案（产品推断，留痕） |
| Q13 | 「方式未知」不等于 1051–1053；本期不做 |
| Q14 | 1052/1053 匹配粒度：1052 端口/URL；1053 主机优先；复用 MatchAssetRule 键 |
| Q15 | 1052 与 1053 共用 Gate；不单独二次 Scan |
| Q16 | 设备未命中禁止确认下发；不得 silent 空 hash |
| Q17 | 预览计数：列名「IP 数」+「漏洞实例数」（底层仍去重 IP） |
| Q18 | 预览删除「建议导入报告」列 |
| Q19 | engType 严格按部侧 engDev.engType bit；按位与匹配 |
| Q20 | eng_hash_cnt 非空则强制候选池；仍须满足 engType |
| Q21 | 「证据能力」列定名「核验过程」 |
| Q22 | 核验方式样式与原修复方式同：白底描边 Tag |
| Q23 | 1052/1053 仍存活 → stat=7 核验未修复（非 10） |
| Q24 | 1060 台账外壳：logType←主任务；内层 srcMethod←子任务实际手段 |
| Q25 | 二次手段：1050∈{1020,1022,1023,1024,1027}；1051∈{1021,1061} |
| Q26 | 字段收敛：子任务 proc_method=实际手段；主任务 proc_method=外壳→logType；废弃 verify_src_method |
| Q27 | 交叉扫描：logType 仍跟主任务；实例手段跟子任务；不得内层只写外壳 |
| Q28 | 主/子状态码：主 10~90 / 子 0~4；读兼容旧 0~8；不做批量刷数 |
| Q29 | 主链路第一步定名「任务预检」；流程实例持久化后步骤条优先读库 |
| Q30 | reportType：source=0 或 ctxCode=3 → 3；其它扫描 → 10；1028 固定 34 |
| Q31 | 统一预览：pre/dispatch 出参归一单一 dispatchPlan（Wave M 已落地）；批次口径统一按 IP 拆分为下一波 |
| Q32 | 设备分配：preDispatch 返回 candidateEngHashes + groupKey；dispatch 回传 groupEngHashAssignments；后端校验 engHash 在候选池内 |
| Q33 | 缓存一致性：preview plan 写入 Redis，key=vul:dispatch-plan-cache:plan:{confirmToken}（Wave Q 去 VerifyFix 前缀）；dispatch 原子查-验-写-删；成功立即删除；失败可重试 3 次；Redis 异常拒绝 dispatch |
| Q34 | 全阶段模型统一：DispatchPlan 全阶段通用，消除 VerifyFixDispatchPlan/PhaseDispatchPreviewVO 模型分离（Wave Q） |
| Q35 | 全阶段缓存化：所有阶段 preDispatch 生成 confirmToken + 缓存，dispatch 从缓存消费；保留旧路径 fallback；配置 vul.dispatch-plan-cache.enabled 默认关闭 |
| Q36 | 统一设备匹配：EngDeviceMatcher 全阶段唯一入口；procMethod->tskType->engType bit 映射（1028->16, 1021->4, 1022/1027->1, 1061->32）；阶段0-3 不再各自实现 |
| Q37 | 全阶段设备选择：a-select 统一交互，默认选中 defaultEngHash（后端匹配首选）；candidateDevices 填充设备详情 |
| Q38 | 缓存数据结构：assetList 改 List<VulScanTaskSubAssetDO> 按 IP 紧凑存储；assetIps 去重（LinkedHashSet）；DispatchAssetGrouper 提取 IP 分组 |
| Q39 | DDD 下沉：缓存相关 15 方法从 AppService 下沉 DomainService；DispatchParam 替代 VulTaskDispatchDTO 入 DomainService |
| Q40 | 跨级切批语义：一个主任务多子任务（plan.groups 按 astUnitNum 切批）；删除 dispatchGangedBatches/sliceGangedBatches/VerifyFixPlanBatchSlicer |
| Q41 | 设备选择 tooltip：a-select-option 外层 a-tooltip 悬浮显示设备详情（HASH + 全部设备类型 engTypeLabels + 注册状态 status）；CandidateDevice 新增 status/engTypeLabels 字段；EngDeviceMatcher.engTypeLabels 遍历 6 bit 展开全部类型标签（Wave S） |
| Q42 | 弱口令设备映射：1030/1031/1032 -> WEAK_PASSWORD(16) -> ENG_WEAK_PASSWORD(8 弱口令工具)；TskTypeEnum 新增 WEAK_PASSWORD(16)；1026 -> VERSION_LOGIN(13) -> ENG_HOST_SCANNER(1) 映射修复（Wave S） |
| Q43 | 交叉扫描双厂商默认：1026 主扫/交叉扫自动分配不同厂商默认设备（adjustCrossScanDualVendor）；前端 crossScanConflict 检测同厂商/同设备冲突禁用确认；移除预览页 SafeSourceDriver/DualVendorScannerPick，设备选择全走 per-group a-select（Wave S） |

---

## 8. 附录

### 8.1 参考文档

- `svmp/docs/standards/基础电信企业网络安全漏洞管理平台建设指南(2025年版).docx`
- `svmp/docs/standards/基础电信企业网络安全漏洞管理平台接口规范(2025年版).docx`
- `svmp/docs/standards/基础电信企业网络安全漏洞管理平台测试规范(2025年版).docx`
- `svmp/docs/internal/verify-fix-修复核验全链路/04-子PRD与规格/修复核验全链路-开发计划-v3.0.md`（执行状态 / Wave 演进 / 缺陷记录 / 测试索引）
- `svmp/docs/internal/verify-fix-修复核验全链路/04-子PRD与规格/修复核验全链路-文档地图与索引-v1.2.md`（文档群索引）
- `svmp/docs/internal/verify-fix-修复核验全链路/04-子PRD与规格/修复核验运营工作台-PRD.md`（open-api，独立）
- `svmp/docs/internal/soc-link-SOC对接全链路/04-子PRD与规格/OPEN状态跃迁与考核隔离说明.md`（状态路径与考核线禁改约束）
- `svmp/docs/internal/verify-fix-修复核验全链路/prototypes/修复核验-任务详情工作台-原型.html`（§5.4 定稿依据）
- `project_backend/svmp/vul-pass/.../event/log/README.md`（台账动作链）

### 8.2 风险与依赖

| 风险 | 缓解 |
|------|------|
| XLSX 无独立存活段 | INFERRED + 考核主路径 XML |
| 无匹配 engType 设备 | **阻断确认**；引导运营维护安全资源 |
| LastScanner 无历史或不合法 | STRATEGY_MATCH 按 engType 匹配；仍无则阻断 |
| 混合工单 subTask 过多 | 预览分页；考核规模可控 |
| 1052/1053「仅连通性」为产品推断（Q12） | 联调留痕；考核靶标回归 |

| 依赖 | 说明 |
|------|------|
| `vul_inst_log_rela` | LastScanner 溯源 |
| `PlatEngRegDet` / engType | 设备匹配 |
| 现有 Parser 体系 | NSFOCUS_XML_III、PLATFORM_VUL_INST_XLSX_V2、ConnectivityCheckParser |
