# 任务下发页重构 · 方案 A - 开发计划 v1.0

> **用途**：本重构的执行权威：任务拆分、文件清单、数据流、验收。  
> **版本**：v1.0 · **日期**：2026-07-23  
> **对应 PRD**：`./任务下发页重构-方案A-PRD-v1.0.md`  
> **分支**：`feature/fix-ledger-log-records`

---

## 1. 当前状态

- 方案 A 已选型，原型已确认。
- 数据齐备：工单 `model`（orderId/ctxCode/orderSubType/procMethod）；`baseInfo`（5 统计 + lifecycleSteps）；`VulBusinessContextEnum` 后端已就绪。
- `TaskExecutionOverview.vue`（v1.0，含 tags+stats+lifecycle）需 rework 为 lifecycle-only（tags+stats 上移到基本信息）。

## 2. 任务拆分

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| T1 | rework `TaskExecutionOverview` -> lifecycle 步骤链 only（去 tags/stats） | `TaskSend/TaskExecutionOverview.vue` | ⏳ |
| T2 | 重构 `BaseInfo`：基本信息卡(只读 tags+stats) + 任务信息卡(配置条+lifecycle+预览)；拉取 `businessContextData` | `TaskSend/BaseInfo.vue` | ⏳ |
| T3 | `eslint` 验证 | - | ⏳ |

## 3. T1 `TaskExecutionOverview` rework

- **props** 收敛：`baseInfo`(lifecycleSteps)、`tskPhase`、`orderPhaseEnumData`（核心编排标题用）。**移除** `procMethod`/`proMethodData`/`orderType`（tags 已上移）。
- **移除**：标签行、5 统计格、`orderTypeLabel`/`stats`/`tskPhaseName` 中 tags 相关、`SetName` import、`fmt`。
- **保留**：`lifecycleSteps`/`isPreview`/`stateLabel`/`displaySteps`/`pipeline`/`pipeSegments`/`summary`/`tskPhaseLabel`（核心编排标题）/`dotColor`/`labelColor`；模板仅留「执行管线」标题 + pipeline + 说明条。
- 模板根 `v-if="lifecycleSteps.length"`。

## 4. T2 `BaseInfo` 重构

### 4.1 模板结构

```
<a-spin>
  <!-- 基本信息（只读，表单外） -->
  <div class="card basic-info">
    <div class="card-title"><span class="bar"></span>基本信息</div>
    <div class="card-inner">
      <div class="tags">
        指令ID(model.orderId) / 业务场景(SetName businessContextData model.ctxCode)
        任务类型(SetName orderType model.orderSubType, label 随 orderId 首位)
        处置方式(SetName proMethodData model.procMethod isShowCode)
      </div>
      <div class="divider"></div>
      <div class="stats">5 项(baseInfo.*)</div>
    </div>
  </div>
  <!-- 任务信息 -->
  <div class="card task-info">
    <div class="card-title"><span class="bar"></span>任务信息</div>
    <div class="card-inner">
      <a-form :form="form" v-bind="formLayout">
        <div class="cfg-bar">⚙ 下发配置(前置条件) + 处置方式/业务阶段 selects</div>
      </a-form>
      <TaskExecutionOverview v-if="baseInfo.lifecycleSteps&&length" :baseInfo :tskPhase="watchTskPhase" :orderPhaseEnumData />
      <DispatchPlanPreview v-if="dispatchPlan" .../>
      <legacy previews/>
    </div>
  </div>
</a-spin>
```

### 4.2 data/created 改动

- `data` 增 `businessContextData: []`。
- `created` 增：`ajaxInterface(getVulBusinessContextEnum + '?type=VulBusinessContextEnum', {}, 'GET').then(res => this.businessContextData = res)`。
- 保留 `watchProcMethod`/`watchTskPhase`/`form`/`baseInfo` 等既有逻辑。
- `a-form` 仅包裹配置条；`onSubmit`/`checkSave`/`getData`/`setTaskeType`/`changeprocMethod`/`changeTskPhase` 不变。

### 4.3 移除

- 原 form 式工单摘要（指令ID/工单类型/执行方式/排查资产 a-form 行）、折叠统计行（showMore）、`.config-block`。
- `isInvalidNum`（若仅折叠统计用）保留以备用或移除。

## 5. 数据流

```
工单 model -> 基本信息 tags（只读，立显）
用户改配置条 处置方式/业务阶段 -> watchProcMethod/watchTskPhase -> getData()
  -> baseInfo = {...data}（5 统计 + lifecycleSteps）-> 指标行 + TaskExecutionOverview + DispatchPlanPreview 刷新
```

## 6. 不改动

`DispatchPlanPreview`、后端、阶段逻辑、`getData`/`onSubmit`/`checkSave`、旧预览兜底、下发确认链路。

## 7. 验收

见 PRD §8。`eslint` 通过；双卡结构；基本信息 4 标签(含业务场景=ctxCode)；配置条前置驱动预览；lifecycle 随阶段切换；风格与 MainTaskSummary 一致。

## 8. 提交建议

单提交：`feat(vul-pass): 任务下发页重构为基本信息+任务信息双区(方案A)`，含 `TaskExecutionOverview.vue`(rework) + `BaseInfo.vue`(重构) + PRD/开发计划。
