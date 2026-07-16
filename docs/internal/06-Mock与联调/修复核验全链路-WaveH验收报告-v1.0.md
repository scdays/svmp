# 修复核验全链路 — Wave H 状态码迁移验收报告 v1.0

> **对应计划**：`修复核验全链路-WaveH-状态码迁移开发计划-v1.0.md`  
> **执行日期**：2026-07-16  
> **分支**：`feature/fix-ledger-log-records`

---

## 1. 验收结论

| 维度 | 结论 | 说明 |
|------|------|------|
| **主/子枚举** | **通过** | `MainTaskStatEnum` / `SubTaskStatEnum` |
| **读兼容** | **通过** | `TaskStatCompatMapper` + 前端 `normalizeMainStat` / `normalizeSubStat` |
| **写路径新码** | **通过（单测）** | 生产写路径不再写旧 4～8 语义 |
| **文案** | **通过** | 无「离线导入」「预览态」「门闸」状态文案 |
| **v2 / Wave G 回归** | **通过** | 定向单测绿 |
| **刷数 / 快照表** | **未做** | 按计划延后 |

**Wave H 总评**：**定向验收通过**；未 commit（待用户指令）。

---

## 2. 目标码表（已落地）

### 主任务

| code | 中文 |
|------|------|
| 10 | 任务预检 |
| 20 | 待启动 |
| 30 | 执行中 |
| 40 | 结果回收 |
| 50 | 稽核完成 |
| 60 | 任务结束 |
| 90 | 失败 |

### 子任务

| code | 中文 |
|------|------|
| 0 | 待启动 |
| 1 | 已完成 |
| 2 | 失败 |
| 3 | 执行中 |
| 4 | 已跳过 |

---

## 3. 交付物

### 后端（vul-pass）

- `MainTaskStatEnum` / `SubTaskStatEnum`
- `TaskStatCompatMapper` + 单测
- `VulScanTaskStatEnum` 保留并 `@Deprecated`
- 写路径：`VulScanTaskSubDomainServiceImpl` / `VulScanTaskAppServiceImpl` / `VulScanTaskSubAppServiceImpl`
- `TaskLifecycleResolver` 适配新主状态

### 前端（asset-newleak-manage）

- `constants/taskStatDict.js`
- `TaskDrawer` / `MainTaskSummary` / `SubTaskCardList` 字典拆分
- `BaseInfo`：「离线导入」→「离线任务」（模式文案，非状态）

### 文档

- PRD v1.4.7 + §17.2 码表重写
- 本验收报告

---

## 4. 执行记录

```bash
mvn test "-Dtest=TaskStatCompatMapperTest,TaskLifecycleResolverTest,VulScanTaskSubDomainServiceGateCascadeTest,VulScanTaskSubDomainServiceSetTaskTest,VulScanTaskSubDomainServiceVerifyLedgerTest,VerifyFixDispatchPlannerTest"
# exit 0

# 前端相关文件 lint：通过（H-2 Agent）
```

---

## 5. 遗留

| 项 | 说明 |
|----|------|
| 全库刷数 | 未做；读兼容即可展示 |
| lifecycle 快照表 | 低优延后 |
| 全量 `mvn test` | 合并前建议 |
| commit / push | 待用户指令 |

---

## 6. 结论

Wave H **定向验收通过**。主/子状态已拆分，在线与离线统一为「待启动」等通用描述。
