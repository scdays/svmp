# 修复核验全链路 — Wave I 处置类型分配验收报告 v1.0

> **对应计划**：`修复核验全链路-WaveI-处置类型分配开发计划-v1.0.md`  
> **执行日期**：2026-07-16  
> **分支**：`feature/fix-ledger-log-records`

---

## 1. 验收结论

| 维度 | 结论 | 说明 |
|------|------|------|
| **ReportTypeAssignStrategy** | **通过** | source/ctxCode/1028 规则单测绿 |
| **枚举 34 + Parser** | **通过** | `CONNECTIVITY_CHECK_V1` + `ConnectivityCheckParser` |
| **预览/下发落库** | **通过（代码）** | suggestedReportType → sub.reportType；source 透传 |
| **前端去误判** | **通过（lint）** | 不再用 ctxCode==2；优先已有 reportType |
| **刷数 / 任务表存 source** | **未做** | 按计划透传/回查 |

**Wave I 总评**：**定向验收通过**；未 commit（待用户指令）。

---

## 2. 策略落地

| 条件 | reportType |
|------|------------|
| source=0（企业）+ 扫描手段 | **3** |
| source=1 且 ctxCode=3 + 扫描手段 | **3** |
| 其它扫描手段 | **10** |
| 1028 | **34** |

扫描手段：1020 / 1022 / 1023 / 1024 / 1027。

---

## 3. source 透传

```text
外层工单 source
  → 前端 preDispatch/dispatch 入参
  → VulTaskDispatchDTO.source
  → resolveOrderSource（入参优先，否则 orderId 回查工单）
  → ReportTypeAssignStrategy
  → plan.suggestedReportType → 子任务 reportType
```

任务表 **不存** source。

---

## 4. 交付物

### 后端
- `ReportTypeAssignStrategy` + Test
- `VulReportTypeEnum.CONNECTIVITY_CHECK_V1(34)`
- `ConnectivityCheckParser`
- Planner / StrategyResolver / AppService / SubDomain 接入

### 前端
- `constants/reportTypeAssign.js`
- `ProMethodDrawer` / `VerifyFixPlanPreview` / TaskSend 透传 source

### 文档
- PRD v1.4.8；本验收报告

---

## 5. 执行记录

```bash
mvn test "-Dtest=ReportTypeAssignStrategyTest,VerifyFixDispatchPlannerTest,TaskLifecycleResolverTest,TaskStatCompatMapperTest"
# exit 0
```

前端相关文件 lint：通过（I-2 Agent）。

---

## 6. 遗留

| 项 | 说明 |
|----|------|
| ConnectivityCheckParser 对各类连通性报告的完备性 | 当前复用绿盟 XML 端口语义 + 在线 exchange；复杂样例待联调 |
| commit / push | 待用户指令 |

---

## 7. 结论

Wave I **定向验收通过**。
