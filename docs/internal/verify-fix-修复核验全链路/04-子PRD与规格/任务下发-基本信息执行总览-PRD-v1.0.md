# 任务下发 · 基本信息执行总览 - PRD v1.0

> **用途**：任务下发页面「基本信息」区顶部新增「任务执行编排」总览区块的需求规格。  
> **版本**：v1.0 · **日期**：2026-07-23  
> **分支**：`feature/fix-ledger-log-records`  
> **关联**：`修复核验全链路-vul-pass-PRD.md` v2.1.0；开发计划 `./任务下发-基本信息执行总览-开发计划-v1.0.md`；原型 `prototypes/basic-info-overview-prototype.html`

---

## 1. 背景与目标

任务下发页面（`AddTaskDrawer` -> `BaseInfo`）当前「基本信息」区：指令ID/工单类型/执行方式/排查资产 常显；封装资产单元/系统漏洞/产品漏洞/弱口令 折叠隐藏；处置方式/业务阶段 为可编辑下拉；下方为子任务预览（`DispatchPlanPreview`）。

**问题**：统计分散成 `a-tag`、缺总览；新手难以一眼理解任务"做什么、做多大、怎么执行"。

**目标**：在基本信息区顶部新增「任务执行编排」总览，参考任务结果页展开态（`MainTaskSummary`）的要素，以**方案 C（阶段流水线 + 核心编排分组）**呈现，让新手一看就明白任务原理、逻辑与执行过程。

## 2. 方案选型

已评审 3 套方案并产出可交互原型对比：
- 方案 A：横向编排条（镜像任务结果页，最贴近现有风格）
- 方案 B：纵向时间轴 + 步骤释义（新手理解度最高）
- 方案 C：阶段流水线 + 核心编排分组（结构感/专业度最强）

**选定方案 C**：MAIN 步骤为简洁阶段卡，CHAIN（阶段专属）步骤聚成高亮"核心编排"块，附白话总述。核心编排突出、结构清晰。

## 3. 范围

- **仅前端**（`asset-newleak-manage`），**无后端改动**。
- 新增组件 `TaskExecutionOverview.vue`；集成进 `BaseInfo.vue` 顶部。
- **不动**：「本次下发配置」可编辑区、`DispatchPlanPreview`、后端、阶段逻辑、旧预览兜底。

## 4. 数据来源

| 内容 | 来源 | 字段 |
|------|------|------|
| 指令ID（标签） | `pre/dispatch` 响应 | `baseInfo.orderId` |
| 工单类型/任务类型（标签） | `baseInfo.orderSubType` -> `orderType` 反查 name；**标签按 `orderId` 首位区分**（1=工单类型，2=任务类型） | `baseInfo.orderSubType` + `orderType` |
| 处置方式（标签） | 当前表单 procMethod -> `proMethodData`，用 `SetName` 渲染（`item.name` 已含编码，**避免编码重复**） | `watchProcMethod`（reactive 代理） |
| 业务阶段（标签） | 当前表单 tskPhase -> `orderPhaseEnumData` 反查 name，**去括号及内部内容** | `watchTskPhase` |
| 封装资产单元 | `pre/dispatch` 响应 | `baseInfo.astUnitNum` |
| 排查资产 | `pre/dispatch` 响应 | `baseInfo.astNum` |
| 产品漏洞 | `pre/dispatch` 响应 | `baseInfo.vulNum` |
| 系统漏洞 | `pre/dispatch` 响应 | `baseInfo.vulInstNum` |
| 弱口令 | `pre/dispatch` 响应 | `baseInfo.pwNum` |
| 编排步骤 | `pre/dispatch` 响应 `lifecycleSteps` | `baseInfo.lifecycleSteps`（`{code,label,kind=MAIN/CHAIN,status}`） |

> `lifecycleSteps` 已随 `pre/dispatch` 响应（`VulScanTaskDTO`）展开进入 `BaseInfo.baseInfo`（`getData` 中 `this.baseInfo = { ...data }`），**无需额外捕获**。

## 5. 展示规格（方案 C）

### 5.1 结构

```
┌ 任务执行编排 ────────────────────────────────────┐
│ [指令ID: 2-1063-...] [任务类型: 跨级联动漏洞扫描核验任务]        │  标签行
│ [处置方式: 1060-修复核验自适应扫描] [业务阶段: 核验阶段]          │  (4 标签，顺序：指令ID/工单类型/处置方式/业务阶段)
│ ──────────────────────────────────────────────── │
│ [封装单元][排查资产][产品漏洞][系统漏洞][弱口令]   │  5 统计格
│ ──────────────────────────────────────────────── │
│ 执行管线:                                        │
│ [预检]○->[下发]○->┌核心编排─────┐->[回收]○->[稽核]○->[结束]○
│                 │③连通性检测 ○│                  │
│                 │④修复核验   ○│                  │
│                 └────────────┘                  │
│ 说明: <白话总述>                                 │
└──────────────────────────────────────────────────┘
```

### 5.1.1 标签行数据处理

- **指令ID**：`baseInfo.orderId` 原值显示（mono 字体）。
- **工单类型/任务类型**：值 = `orderType` 按 `baseInfo.orderSubType` 反查 name；**标签**按 `orderId` 首位字符区分：`1`->「工单类型」，`2`->「任务类型」，其余->「类型」。
- **处置方式**：用 `SetName` 渲染 `proMethodData`（`item.name` 已含编码如「1060-修复核验自适应扫描」），**不再手动拼编码**，避免重复。
- **业务阶段**：`orderPhaseEnumData` 反查 name 后**去括号及内部内容**（如「核验阶段(系统漏洞工单/跨级联动任务)」->「核验阶段」）。

### 5.2 管线分组规则

`lifecycleSteps` 顺序：`ASSIGN_PRECHECK, DISPATCHED, [CHAIN...], RECYCLE, AUDIT_DONE, FINISHED`。
- **head 主卡**：`ASSIGN_PRECHECK`（任务预检）、`DISPATCHED`（任务下发）
- **核心编排块**：`kind=CHAIN` 的步骤（阶段专属；核验=连通性检测->修复核验；排查=漏洞扫描；验证=漏洞扫描->二次扫描；修复=漏洞修复）
- **tail 主卡**：`RECYCLE`（结果回收）、`AUDIT_DONE`（稽核完成）、`FINISHED`（任务结束）
- 主卡与核心编排块之间以 `→` 箭头连接

### 5.3 状态与配色（预览态）

`pre/dispatch` 预览态 `lifecycleSteps` 全 `PENDING`。显示策略：**首步标"即将开始"**（蓝 `#1890ff` 闪烁），余待执行（灰 `#d9d9d9`）。

状态色（预留，预览态仅首步蓝、余灰）：待执行灰 / 进行中蓝 `#1890ff` / 已完成绿 `#52c41a` / 失败红 `#f5222d`。核心编排块：紫 `#722ed1` 虚线边框 + 浅紫底 `#f9f0ff`。

### 5.4 白话总述

前端 `code->desc` 常量表（CHAIN 步骤码）：`CORRELATION_ANALYSIS / VUL_SCAN / CROSS_SCAN / VUL_REPAIR / CONNECTIVITY_CHECK / REPAIR_VERIFY / GENERIC_SUBTASK`。总述 = 核心 CHAIN 步骤 `desc` 以"；"拼接。

### 5.5 统计格

5 格等宽 flex；每格 = 标签（灰 `#8c8c8c` 12px）+ 数值（`#1890ff` 20px 加粗）。无效值（`null`/空/负）显示 `-`。

## 6. 交互

- 只读总览，无操作项。
- **随预览刷新**：用户改处置方式/业务阶段 -> `setTaskeType`/`changeTskPhase` -> `getData()` -> `baseInfo.lifecycleSteps` + 统计更新 -> 总览自动更新（标签用 `watchProcMethod`/`watchTskPhase` 立即更新）。
- 仅当 `baseInfo.lifecycleSteps` 非空时渲染；否则隐藏。
- 下方「本次下发配置」可编辑区与 `DispatchPlanPreview` 不变。

## 7. 验收标准

1. 基本信息区顶部出现「任务执行编排」总览，**首行 4 标签**（顺序：指令ID / 工单类型或任务类型 / 处置方式 / 业务阶段）+ 5 统计 + 管线 + 总述。
2. 标签数据处理：处置方式**编码仅显示一次**（如「1060-修复核验自适应扫描」）；业务阶段**无括号及内容**（如「核验阶段」）；工单类型**标签随指令ID首位**（1->工单类型，2->任务类型），值取 `orderType` name。
3. 切换处置方式/业务阶段，总览标签与管线（核心编排步骤）随之更新。
4. 各阶段核心编排步骤正确：核验=连通性检测->修复核验；排查=漏洞扫描；验证=漏洞扫描->二次扫描；修复=漏洞修复。
5. 5 项统计正确显示，无效值显示 `-`。
6. 预览态首步"即将开始"蓝、余灰；核心编排块紫色高亮。
7. `eslint` 通过；不破坏既有 `DispatchPlanPreview` / 下发链路。

## 8. 风险与备注

- `LifecycleStepVO` 无 `desc` 字段 -> 白话总述用前端常量表（非后端数据）。
- `a-form` 字段值非 Vue reactive -> 处置方式/业务阶段 用 `watchProcMethod`/`watchTskPhase` reactive 代理驱动标签。
- 预览态全 `PENDING` -> 首步"即将开始"为 UI affordance（非真实状态）。
