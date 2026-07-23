# OPEN 状态跃迁与考核隔离说明

> **状态**：已确认 v1.0 · 2026-06-17  
> **读者**：vul-pass OPEN 编排开发、Review

## 一、产品确认（已冻结）

| # | 决策 |
|---|------|
| 1 | SOC UNION 验证：仅一侧发现 → **1 初始发现**；两侧均发现 → **2 已验证有效** |
| 2 | verify-fix：**不走** `PassRoot.doVulTransition`；按目标漏洞是否仍检出 → **6 / 7 / 10** |
| 3 | OPEN 实例轨迹：**只写** `vul_inst_log_rela_oper`（`data_origin=OPEN`），不写 `vul_inst_log_rela` 上报轨 |

## 二、考核线禁改清单

以下类/路径 **禁止修改**（可 **public 方法调用**）：

- `VulScanTaskUi` `/dispatch`、`/recycle`
- `VulScanTaskAppServiceImpl.dispatch`、`recycle`
- `VulScanTaskSubDomainServiceImpl` 内部实现
- `PassRoot`、`TransitionEnum`
- `CommonUtil.buildVulInfoLstByEngHashMap`
- `VulnGangedTaskDomainServiceImpl`
- `VulCrossVerifyParser`、`PlatformDefaultHandleXlsxParserV2`

OPEN 代码包：`com.vtc.security.domain.open.*`、`com.vtc.security.ui.open.*`

## 三、三条状态路径

### 3.1 排查阶段（tskPhase=1）

```
B results → SurveyResultsAdapter → handlerVulProcess(procMethod=1021)
  → PassRoot（NEW_DISCOVERY → 1）  ✅ 复用现有 transition
  → OpenInstOperRelaWriter（oper 轨）
```

### 3.2 验证阶段

| 策略 | 合并 | 状态落库 |
|------|------|----------|
| **INTERSECT**（部侧） | `VerifyMergeService.INTERSECT` | `handlerVulProcess` + PassRoot ✅ |
| **UNION**（SOC） | `VerifyMergeService.UNION` | `OpenVerifyStatusResolver` → `OpenVerifyFinalizeService` ❌ 不走 PassRoot |

### 3.3 修复核验（scan_phase=3）

```
VerifyFixOrchestrator → B 全量复扫 → VerifyFixRecycleHandler
  → 仅匹配目标 vulInfoID → 6/7/10
  → OpenInstOperRelaWriter
```

## 四、实现类对照

| 类 | 职责 |
|----|------|
| `VerifyMergeService` | UNION / INTERSECT 多扫描器结果合并 |
| `OpenVerifyStatusResolver` | UNION 下按扫描器命中数赋 1/2 |
| `OpenVerifyFinalizeService` | OPEN+UNION 实例持久化 + oper 轨 |
| `OpenSurveyRecycleService` | Kafka 触发 → 拉 B results → 分流上述路径 |
| `OpenInstOperRelaWriter` | 写 `vul_inst_log_rela_oper` |
