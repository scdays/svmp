# 任务下发页重构 · 方案 A - PRD v1.0

> **用途**：任务下发页面（`AddTaskDrawer` -> `BaseInfo`）整体结构重构的需求规格。  
> **版本**：v1.0 · **日期**：2026-07-23  
> **分支**：`feature/fix-ledger-log-records`  
> **关联**：取代 `任务下发-基本信息执行总览-PRD-v1.0.md`（执行总览块融入新结构）；开发计划 `./任务下发页重构-方案A-开发计划-v1.0.md`；原型 `prototypes/task-dispatch-redesign-prototype.html`

---

## 1. 背景与目标

当前「基本信息」区为 form 式（a-form 行：指令ID/工单类型/执行方式/排查资产 + 折叠统计 + 配置块），统计分散、与任务详情页风格不一致。

**目标**：
1. 重构为「基本信息 + 任务信息」双区结构（方案 A）。
2. 与任务详情页 `MainTaskSummary` **风格统一**（标签行 + 指标行 + lifecycle 步骤链视觉语言），不做两套风格。
3. 「本次下发配置」(处置方式/业务阶段) 作为预览/编排的**前置条件**，单独成条、醒目前置。
4. **废弃原 form 式「基本信息」区**。

## 2. 方案选型

已评审方案 A（双区+配置条前置）/ 方案 B（单卡+配置内嵌），原型对比后选定 **方案 A**：基本信息(只读) + 任务信息(可编辑配置+预览) 双卡分层，配置条显式前置。

## 3. 页面结构（方案 A）

```
┌ 基本信息 ───────────────────────────────────────┐
│ [指令ID][业务场景][任务类型][处置方式]             │ ← 只读标签行（取自工单 model）
│ 封装单元│排查资产│产品漏洞│系统漏洞│弱口令          │ ← 只读指标行（取自 baseInfo 预览）
└────────────────────────────────────────────────┘
┌ 任务信息 ───────────────────────────────────────┐
│ ⚙ 下发配置（前置条件·调整后刷新预览）              │ ← 可编辑配置条（a-form: 处置方式/业务阶段）
│   技术处置方式[▼]  漏洞业务阶段[▼]               │
│ ────────────────────────────────────────────── │
│ 任务执行编排（预览）                              │
│ ①预检->②下发->┌核心编排┐->⑤回收->⑥稽核->⑦结束     │ ← lifecycle 预览链
│ 说明: <白话总述>                                 │
│ ────────────────────────────────────────────── │
│ 子任务预览（DispatchPlanPreview 表）             │ ← 已定版，不变
└────────────────────────────────────────────────┘
[取消]  [确认下发]
```

## 4. 数据来源

### 4.1 基本信息（只读，取自工单 `model` = `VulnDisposeOrderDTO`）

| 标签 | 字段 | 渲染 |
|------|------|------|
| 指令ID | `model.orderId` | 原值，mono |
| 业务场景 | `model.ctxCode` | `SetName` + `VulBusinessContextEnum`（name 已含编码，如「5-漏洞管理能力达标考核」） |
| 任务类型 | `model.orderSubType` | `SetName` + `orderType`（标签按 `orderId` 首位：1=工单类型，2=任务类型） |
| 处置方式 | `model.procMethod` | `SetName` + `proMethodData`（`isShowCode`，name 已含编码） |

### 4.2 基本信息指标行（5 项，取自 `baseInfo` = pre/dispatch 响应）

`astUnitNum` / `astNum` / `vulNum` / `vulInstNum` / `pwNum`；无效值显示 `-`。

### 4.3 任务信息

- **下发配置条**：a-form 可编辑 `procMethod`/`tskPhase`（`v-decorator`，`changeprocMethod`/`changeTskPhase` 驱动 `getData`）。为前置条件，调整后刷新编排与子任务预览。
- **任务执行编排**：`baseInfo.lifecycleSteps`（`{code,label,kind=MAIN/CHAIN,status}`），预览态全 `PENDING`，首步"即将开始"。
- **子任务预览**：`DispatchPlanPreview`（不变）。

> `lifecycleSteps` 已随 pre/dispatch 响应展开进 `baseInfo`，无需额外捕获。

## 5. 处置方式 呈现说明（待确认）

- **基本信息** 处置方式 = `model.procMethod`（工单原始，**只读上下文**）。
- **任务信息** 下发配置条 处置方式 = 表单可编辑 `procMethod`（默认取工单值，可调整驱动预览）。
- 即处置方式在「基本信息(只读上下文)」与「任务信息(可编辑配置)」各出现一次（context vs config）。**如需去除重复**（处置方式只读、配置条仅留业务阶段），请确认。

## 6. 风格统一

- 基本信息 标签行 + 指标行 + 任务信息 lifecycle 步骤链，复用 `MainTaskSummary` 视觉语言（标签 pill、指标格、编号步骤链、核心编排分组）。
- `TaskExecutionOverview` 组件承载 lifecycle 步骤链（与任务详情同款 pipeline 渲染）。

## 7. 不改动

- `DispatchPlanPreview`（子任务预览，已定版）。
- 后端、阶段逻辑、`getData`/`onSubmit`/`checkSave` 表单逻辑、旧预览兜底。
- 下发确认链路。

## 8. 验收标准

1. 页面呈「基本信息」+「任务信息」双卡，废弃原 form 式基本信息区。
2. 基本信息标签行 4 标签：指令ID / 业务场景(ctxCode) / 任务类型 / 处置方式，取自工单 `model`，只读。
3. 业务场景正确显示 `VulBusinessContextEnum` name（如「5-漏洞管理能力达标考核」，编码不重复）。
4. 任务类型标签随指令ID首位（1=工单类型，2=任务类型），值取 `orderType` name。
5. 指标行 5 项统计正确，无效值 `-`。
6. 任务信息下发配置条（处置方式/业务阶段 可编辑）为前置条件，调整后刷新编排与子任务预览。
7. lifecycle 编排预览随阶段切换更新；各阶段核心编排正确。
8. 视觉与任务详情 `MainTaskSummary` 风格一致。
9. `eslint` 通过；不破坏下发链路。

## 9. 风险与备注

- `VulBusinessContextEnum` 需前端拉取（`getVulBusinessContextEnum?type=VulBusinessContextEnum`），存 `businessContextData`。
- `a-form` 仅包裹下发配置条（可编辑字段）；基本信息(只读)在表单外。
- 处置方式 context/config 双显见 §5（待确认）。
