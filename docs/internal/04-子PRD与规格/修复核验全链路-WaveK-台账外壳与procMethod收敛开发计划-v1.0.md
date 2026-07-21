# 修复核验全链路 — Wave K 台账外壳与 procMethod 收敛 开发计划 v1.0

> **状态**：已执行（代码落地，待单测确认）  
> **日期**：2026-07-17  
> **PRD**：`修复核验全链路-vul-pass-PRD.md` **v1.4.10**（§5.4 / §5.4.1 / §6.7 / Q26–Q27）  
> **分支**：`feature/fix-ledger-log-records`（后端 `vul-pass` + 前端 `asset-newleak-manage`）

---

## 1. 目标

定稿口径落地：

| 写入点 | 取值 |
|--------|------|
| 台账 `logType` / 管理类型外壳 | **主任务** `procMethod` |
| 实例 / rela / content `srcMethod`（实际手段） | **子任务** `procMethod` |
| 子任务 `procMethod` 语义 | **实际手段**（Gate=1028、Scan=1022/1021…；修复=1050–1053） |
| `verify_src_method` / `verifySrcMethod` | **废弃并删除**（职责并入子任务 `procMethod`） |

满足部侧：1060 时 `logType=1060`，内层手段为 1028/1020…；其它阶段 logType 与外壳处置方式一致。

## 2. 验收标准

- [x] 核验子任务落库：`proc_method`=实际手段（1028/1022/1021…），**不再**写 1060 到子任务
- [x] 主任务仍为外壳 1060（或显式 1061）；台账 `logType` **等于主任务** `procMethod`
- [x] recycle / 实例 / rela 的 `srcMethod` 取自**子任务** `procMethod`（非主任务 1060、非已删列）
- [x] Liquibase：存量 `verify_src_method` → `proc_method` 回填（仅当子任务仍为外壳时）；随后 **dropColumn**
- [x] Java/DTO/VO/API：**无** `verifySrcMethod` 字段引用
- [x] 前端预览/卡片/自动化处置：**只展示**子任务处置方式（实际手段）；无 `verifySrcMethod`
- [x] 单测：TC-11 改为「主=1060、子=1028、logType=1060、内层=1028」；相关 `mvn test` 绿
- [x] 交叉扫描：文档口径已定（logType 跟主、手段跟子）；本 Wave **不做强制一致**，仅保证取值规则正确

## 3. 不改什么

- 不改 Wave G/H 状态码、Wave I reportType 策略表、Wave J 自动化处置编排语义
- 不重写 `IssueVerify` / `VerifyResult` 台账动作链骨架
- 不改 `open-api-service`、Partner 契约
- 不改 `tskType` / `wave` 设备匹配与编排阶段语义
- 本 Wave **不**强制交叉扫描子=主（仅保证外壳/内层取值）

---

## 4. 改造要点（实现约束）

### 4.1 后端关键路径

| 模块 | 动作 |
|------|------|
| `VerifyFixDispatchPlanner` / spawn | 子任务 `procMethod` ← 策略实际手段；主任务保持外壳 |
| `VulScanTaskSubDomainServiceImpl.doWriteLedger` | 传入/解析 **主任务** procMethod 作为 logType |
| `AbstractLedgerLog.initLog` | logType ← 主任务外壳（禁止被子任务覆盖） |
| recycle / `initRecycle` / rela 写入 | 内层 srcMethod ← 子任务 `procMethod`；**禁止**用主任务 1060 盖写内层 |
| `ReportTypeAssignStrategy` / `VerifyFixStrategyResolver` | 入参改读子任务 `procMethod`（原 verifySrcMethod 优先逻辑删除） |
| PO/DO/DTO/VO | 删除 `verifySrcMethod`；Mapper/XML 同步 |
| Liquibase `vul_scan_task_sub.groovy` | **未发版合并**：`2026-07-14-01` 一次加入策略字段 + wave/depend_gate_id；**不建** `verify_src_method`，无迁移/drop 变更集 |

### 4.2 数据迁移建议

```sql
-- 语义：若子任务仍存外壳码且 verify_src_method 有值，则把实际手段落到 proc_method
UPDATE vul_scan_task_sub
SET proc_method = verify_src_method
WHERE verify_src_method IS NOT NULL
  AND proc_method IN (1060, 1061);  -- 按现网实际外壳集合微调
-- 再 dropColumn verify_src_method
```

排查/验证主子本就一致的行：`verify_src_method` 为空时无需改 `proc_method`。

### 4.3 前端落点

| 文件（示意） | 动作 |
|--------------|------|
| `SubTaskCardList` | 去掉核验手段双 Tag；处置方式=子任务 `procMethod` |
| `VerifyFixPlanPreview` | 列「核验方式」绑 `procMethod` |
| `AutoDisposeDrawer` 等 | 去掉 `verifySrcMethod` 展示/传参 |

### 4.4 交叉扫描

- 默认：**不特殊改产品行为**，只保证 logType←主、srcMethod←子。
- 若后续担心实例手段展示，另开小需求（强制子=主或 UI 提示），**不阻塞**本 Wave。

---

## 5. 任务矩阵

| Wave | Agent | 改什么 | 交付物 |
|------|-------|--------|--------|
| **K-0** | 文档 | PRD v1.4.10 + 本计划（已完成） | docs |
| **K-1** | 后端-台账/回收 | `doWriteLedger` / `initLog` / recycle / rela 取值纠偏 | Java + 单测 |
| **K-2** | 后端-模型/DDL | Planner 落库语义；PO/DTO 删字段；Liquibase 迁移+删列 | Java + groovy |
| **K-3** | 前端 | 预览/卡片/抽屉去 `verifySrcMethod`，只显实际处置方式 | Vue |
| **K-4** | Review | 对照验收标准 + `esmp-code-review-strict` + 相关单测 | 验收摘要 |

**预计并行**：K-1 与 K-3 可并行；K-2 宜在 K-1 取值纠偏后或同波紧耦合执行（先改语义再删列，避免中间态读空）。

---

## 6. 分支与规范

| 项 | 值 |
|----|-----|
| 分支 | 继续 `feature/fix-ledger-log-records`（不新开，除非冲突） |
| 研发规范 | `esmp-rd-standards`：Commit `[IMP]`/`[REF]`/`[REM]`；UTF-8 无 BOM |
| 专项 Skills | `esmp-backend-dev`、`esmp-frontend-dev`、`esmp-code-review-strict` |
| 严格 Rules | `java-hard-ban`、`backend-layer-boundary-strict`、`test-required-strict`、`security-hard-ban` |

---

## 7. 风险

| 风险 | 缓解 |
|------|------|
| 存量子任务 `proc_method=1060` 未回填就删列 | Liquibase 先 UPDATE 再 DROP；上线前抽数 |
| 某处仍用子任务写 logType | 单测 TC-11 + Grep `verifySrcMethod` / ledger 入参 |
| 修复阶段 105 外壳 vs 1050–1053 | 与核验同规则；本 Wave 顺带核对修复路径是否误用子任务写 logType |
| 前端缓存旧字段 | 接口契约删除后前端必改，避免静默 undefined |

---

请回复 **同意执行** 开始 Wave K 改码；或说明要改的地方。
