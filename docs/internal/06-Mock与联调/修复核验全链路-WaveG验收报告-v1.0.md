# 修复核验全链路 — Wave G 全阶段主链路验收报告 v1.0

> **对应计划**：`修复核验全链路-WaveG-全阶段主链路开发计划-v1.0.md`  
> **术语**：主链路第一步为 **任务预检**（非「任务预览」）  
> **执行日期**：2026-07-16  
> **分支**：`feature/fix-ledger-log-records`

---

## 1. 验收结论

| 维度 | 结论 | 说明 |
|------|------|------|
| **G-0 文档** | **通过** | PRD v1.4.6；设计方案/计划文案统一为「任务预检」 |
| **G-1/G-2 后端推导** | **通过** | `TaskLifecycleResolver` + DTO 瞬态字段；App 层 enrich |
| **G-3 前端步骤条** | **通过（lint）** | `MainTaskSummary` 优先用 `lifecycleSteps`，按 phase 兜底 |
| **v2 不回归** | **通过** | 定向单测含 Planner / GateCascade / SetTask / VerifyLedger |
| **真实工单 E2E** | **待环境** | 需联调环境走查各 phase |

**Wave G 总评**：**代码与定向验收通过**；未 commit（待用户指令）。

---

## 2. 主链路展示（已落地）

```text
任务预检 → 任务下发 → [阶段子任务链] → 结果回收 → 稽核完成 → 任务结束
```

| tskPhase | 中间子任务链 |
|----------|--------------|
| 0 潜在预警 | 关联分析 |
| 1 排查 | 漏洞扫描 |
| 2 验证 | 漏洞扫描 → 二次扫描 |
| 3 修复 | 漏洞修复 |
| 4 核验 | 连通性检测 → 修复核验 |

---

## 3. 交付物

### 后端（vul-pass）

| 路径 | 说明 |
|------|------|
| `domain/pass/service/lifecycle/*` | Step / Template / Resolver |
| `ui/dto/LifecycleStepVO.java` | 步骤 VO |
| `ui/dto/VulScanTaskDTO.java` | lifecycleStep / lifecycleSteps / currentStepCode |
| `app/.../VulScanTaskAppServiceImpl.java` | enrichLifecycle |
| `TaskLifecycleResolverTest.java` | 单测 |

### 前端（asset-newleak-manage）

| 文件 | 说明 |
|------|------|
| `MainTaskSummary.vue` | 配置化步骤条；任务预检；全阶段展示 |

### 文档（svmp）

| 文件 | 说明 |
|------|------|
| PRD v1.4.6 | Wave G 变更记录 + §7.5.7 步骤文案 |
| Wave G 开发计划 | 术语修正 |
| 子任务类型设计方案 | 统一链路文案 |

---

## 4. 执行记录

```bash
mvn test "-Dtest=TaskLifecycleResolverTest,VerifyFixDispatchPlannerTest,VulScanTaskSubDomainServiceGateCascadeTest,VulScanTaskSubDomainServiceSetTaskTest,VulScanTaskSubDomainServiceVerifyLedgerTest"
# exit 0

npx vue-cli-service lint --no-fix MainTaskSummary.vue
# No lint errors found
```

---

## 5. 遗留

| 项 | 说明 |
|----|------|
| 排查/修复/预警真实子任务派生 | 本 Wave 仅模板 + UI；编排未改 |
| 验证阶段「二次扫描」真实派生 | UI 占位；1026 编排可后续挂接 |
| 全量 `mvn test` | 合并前建议 |
| commit / push | 待用户指令 |

---

## 6. 结论

Wave G **定向验收通过**。步骤条文案已与需求对齐为「任务预检」起头的全阶段主链路。
