# 双阶段交叉扫描方案 · SOC 并集与部侧交集统一模型

> **状态**：正式采纳
> **日期**：2026-06-17
> **关联**：
> - 对外 API 文档：`external/网络安全漏洞管理平台 · API 接口文档.md`（v1.0.6）
> - PRD 修订附录：`SOC对接全链路-PRD-v2修订附录.md`
> - 任务矩阵：`features/soc-link-task-matrix.yaml`
> **读者**：vul-pass / vuln-task-center / open-api-service 后端、产品

---

## 一、问题陈述

### 1.1 两种合并需求

| 场景 | 来源 | 扫描器 | 合并策略 | 理由 |
|------|------|--------|----------|------|
| **SOC 接入** | Partner 创建任务 | Nessus + 绿盟 | **并集**（UNION） | 最大化覆盖，两次扫描结果合并后均为初始发现，交叉部分为已验证有效 |
| **部侧考核** | 部侧交叉扫描验证 | 厂商A + 厂商B | **交集**（INTERSECT） | 交叉验证，第一次初始发现，第二次两次均发现为已验证有效，仅一次发现为已验证误报 |

### 1.2 核心矛盾

- 部侧规范要求交叉扫描取**交集**（验证有效性）
- SOC 接入要求取**并集**（最大化覆盖）
- 直接在任务下发层做 `SOC_DUAL` 特殊定制，违反"规避定制化"原则

### 1.3 解决思路

**将"双扫描器下发"从排查阶段的特殊策略，重构为验证阶段的通用能力**：

```text
排查阶段（PHASE_SURVEY / tskPhase=1）
  → 单扫描器下发（按 engHash 轮询分配）
  → 结果回收 → 漏洞实例初始发现（vulInfoStat=1）

验证阶段（PHASE_VALIDATION / tskPhase=2）
  → 多扫描器交叉下发（可配置厂商列表）
  → 结果回收 → 按合并策略确定状态
     ├── 部侧标准（INTERSECT，默认）：两次均发现 → 2（已验证有效），仅一次发现 → 3（已验证误报）
     └── SOC 标准（UNION）：合并后均为 1（初始发现），交叉部分 → 2（已验证有效）
```

**关键洞察**：vul-pass 已有 `CROSS_SCAN_VERIFICATION`（procMethod=1026）和 `PHASE_VALIDATION` 验证阶段状态跃迁规则，本方案是**复用和扩展**现有能力，而非新建。

### 1.4 状态归属解决

通过 `autoVerify` 参数（默认 true）+ 推迟回调机制解决状态归属：

- autoVerify=true：排查完成后自动触发验证阶段，全部完成后统一回调 `TASK_COMPLETED`，实例状态为验证后终态
- autoVerify=false：排查完成即回调，实例为 1（初始发现），由 Partner 主动 verify

**不新增 Webhook 事件、不新增 verify_source 字段、不放宽 verify 接口前置状态约束。**

---

## 二、现有代码基础

### 2.1 已有的交叉扫描能力

| 能力 | 代码位置 | 现状 |
|------|----------|------|
| 交叉扫描验证处置方式 | `VulProcessMethodEnum.CROSS_SCAN_VERIFICATION`（1026） | 已定义 |
| 验证阶段状态跃迁 | `TransitionEnum` PHASE_VALIDATION 规则 | EXISTENT→3, STILL_EXIST→2 |
| 交叉扫描结果解析器 | `VulCrossVerifyParser` | 已实现，输出 VALIDATED_TRUE |
| 多设备结果合并 | `CommonUtil.buildVulInfoLstByEngHashMap` | 按 inst.id 去重合并 logIDLst |
| 交叉扫描触发行 | `VulScanTaskSubDomainServiceImpl.shouldExecuteScanV2` | subType=32/1062 且 procMethod=1026 时扫描 |
| BPMN 流程定义 | `T2.bpmn` | 已定义交叉扫描节点 |

### 2.2 现有 transition 验证阶段规则

```java
// 验证阶段：档案库有 + 本次未发现 → 已验证误报(3)
addRule(PHASE_VALIDATION, EXISTENT, INITIAL_DISCOVERY(1), VALIDATED_FALSE(3));
// 验证阶段：档案库有 + 本次仍发现 → 已验证有效(2)
addRule(PHASE_VALIDATION, STILL_EXIST, INITIAL_DISCOVERY(1), VALIDATED_TRUE(2));
```

**关键**：transition 的 `EXISTENT`/`STILL_EXIST` 是基于「档案库 vs 本次扫描」的 diff 计算结果。多扫描器场景下，"本次扫描"的结果需要先合并，再与档案库 diff。

### 2.3 现有合并逻辑分析

`buildVulInfoLstByEngHashMap`（procMethod=1026 分支）：
- 将多个 engHash（扫描器）的结果汇总
- 按 `inst.id` 去重，重复的合并 `logIDLst`
- **本质是并集**（所有扫描器发现的结果都保留）

**差距**：缺少交集模式（仅保留所有扫描器都发现的结果）。

---

## 三、方案设计

### 3.1 双阶段扫描模型

```text
┌─────────────────────────────────────────────────────────────────┐
│  阶段 1：排查（PHASE_SURVEY / tskPhase=1）                        │
│  procMethod = 1021（漏洞扫描）或 1022（在线扫描）                  │
│                                                                   │
│  vul-pass dispatch                                                │
│    → 单扫描器下发（engHash 轮询分配）                              │
│    → task-center 执行                                             │
│    → 结果回收 → handlerReport → handlerVulProcess                 │
│    → transition: NEW_DISCOVERY → vulInfoStat=1（初始发现）        │
│    → 写入 vul_archive_inst + rela_oper/report                    │
│                                                                   │
│  产出：漏洞实例库（状态=1 初始发现）                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  阶段 2：验证（PHASE_VALIDATION / tskPhase=2）                    │
│  procMethod = 1026（交叉扫描验证）                                 │
│                                                                   │
│  vul-pass dispatch（验证任务）                                     │
│    → 多扫描器下发（按 verifyScannerVendors 配置）                  │
│       ├── SOC: [NESSUS, LM]                                      │
│       └── 部侧: [厂商A, 厂商B]                                    │
│    → task-center 执行 N 个 survey                                 │
│    → 结果回收 → mergeVerifyResults(mergeStrategy)                 │
│       ├── UNION（SOC 并集）：合并后均为初始发现，交叉部分为已验证有效 │
│       └── INTERSECT（部侧交集）：两次均发现为已验证有效，仅一次为误报 │
│    → handlerVulProcess → transition                               │
│    → 更新 vul_archive_inst + rela_oper/report                    │
│                                                                   │
│  产出：漏洞实例库（状态=2 已验证有效 / 3 已验证误报 / 1 初始发现）  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 合并策略枚举

```java
public enum VerifyMergeStrategy {
    /**
     * 并集：两次扫描结果取并集，合并后均为初始发现，交叉部分为已验证有效。
     * SOC 接入场景：最大化覆盖。
     */
    UNION,

    /**
     * 交集：两次均发现为已验证有效，仅一次发现为已验证误报。
     * 部侧考核场景：交叉验证有效性。
     */
    INTERSECT
}
```

### 3.3 合并策略与状态确定

**部侧标准（INTERSECT，交集）**：

| 扫描器A发现 | 扫描器B发现 | 合并结果 | 状态确定 |
|-----------|-----------|---------|---------|
| ? | ? | 保留 | 已验证有效（2） |
| ? | ? | 丢弃 | 已验证误报（3） |
| ? | ? | 丢弃 | 已验证误报（3） |
| ? | ? | 丢弃 | 已验证误报（3） |

**SOC 标准（UNION，并集）**：

| 扫描器A发现 | 扫描器B发现 | 合并结果 | 状态确定 |
|-----------|-----------|---------|---------|
| ? | ? | 保留 | 已验证有效（2） |
| ? | ? | 保留 | 初始发现（1） |
| ? | ? | 保留 | 初始发现（1） |
| ? | ? | 丢弃 | 已验证误报（3） |

### 3.4 配置模型

#### 3.4.1 Partner 级配置（open-api-service）

| 字段 | 类型 | SOC 默认 | 普通 Partner 默认 |
|------|------|---------|------------------|
| `defaultAutoVerify` | BOOLEAN | true | false |
| `autoVerifyScannerVendors` | VARCHAR(256) | NESSUS,LM | — |
| `autoVerifyMergeStrategy` | VARCHAR(16) | UNION | INTERSECT |

#### 3.4.2 任务级配置（vul_scan_task）

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `auto_verify` | TINYINT(1) | 1 | 是否开启自动验证 |
| `verify_merge_strategy` | VARCHAR(16) | INTERSECT | 验证阶段合并策略：UNION/INTERSECT，接入 Partner 时定制 |
| `verify_scanner_vendors` | VARCHAR(256) | — | 验证阶段扫描器厂商列表，逗号分隔 |

#### 3.4.3 子任务标记（vul_scan_task_sub）

| 字段 | 类型 | 说明 |
|------|------|------|
| `scan_phase` | TINYINT | 1=排查阶段 / 2=验证阶段 |
| `scanner_vendor` | VARCHAR(16) | NESSUS / LM / AH |
| `verify_round` | INT | 验证轮次（同一验证阶段的多扫描器编号） |

### 3.5 SOC 接入完整流程

```text
Partner POST /api/open/v1/tasks/vul { autoVerify: true }
  → open-api 创建 open_task (auto_verify=1)
  → open-api 调 vul-pass POST /internal/open/v1/tasks
     → vul-pass 创建 vul_scan_task
       biz_line=OPEN, auto_verify=1
       tsk_phase=1（排查阶段）, proc_method=1021
       verify_merge_strategy=UNION（继承 Partner 配置）
       verify_scanner_vendors=NESSUS,LM
     → vul-pass dispatch（排查阶段）
       → 单扫描器下发（engHash 轮询）
       → task-center 执行 1 个 survey
       → 结果回收 → handlerVulProcess
       → transition: NEW_DISCOVERY → vulInfoStat=1
     → 排查完成，auto_verify=true 自动触发验证阶段
     → vul-pass dispatch（验证阶段）
       tsk_phase=2, proc_method=1026
       → 多扫描器下发（NESSUS + LM 各 1 个 survey）
       → task-center 执行 2 个 survey
       → 结果回收
       → mergeVerifyResults（SOC 并集）
       → 按合并策略确定状态
     → 验证完成
  → vul-pass 通知 open-api (tsk_phase=2, FINISHED)
  → open-api 统一回调
     → Webhook: TASK_COMPLETED（summary 反映验证后终态）
     → EXPORT_READY（含两阶段合并结果）
```

### 3.6 部侧考核流程（复用现有）

```text
部侧 dispatch(orderId)
  → vul-pass dispatch（排查阶段）
    tsk_phase=1, proc_method=1021
    → 单扫描器下发
    → 结果回收 → vulInfoStat=1
  → 部侧发起验证工单（subType=32）
  → vul-pass dispatch（验证阶段）
    tsk_phase=2, proc_method=1026
    verify_merge_strategy=INTERSECT（默认）
    → 多扫描器下发（厂商A + 厂商B）
    → 结果回收
    → mergeVerifyResults（部侧交集）
    → 按合并策略确定状态
  → 验证完成，回传部侧
```

---

## 四、核心实现

### 4.1 mergeVerifyResults 方法

```java
/**
 * 合并多扫描器验证结果
 * @param surveyResults 各扫描器 survey 的结果列表（已拉取并标准化）
 * @param strategy 合并策略
 * @param dedupKeyFunction 去重键函数
 * @return 合并后的结果列表
 */
public List<VulScanTaskSubResultDO> mergeVerifyResults(
        List<List<VulScanTaskSubResultDO>> surveyResults,
        VerifyMergeStrategy strategy,
        Function<VulScanTaskSubResultDO, String> dedupKeyFunction) {

    if (surveyResults.size() == 1) {
        return surveyResults.get(0);
    }

    // 按扫描器分组，每组转为 dedupKey -> result 的 Map
    List<Map<String, VulScanTaskSubResultDO>> maps = surveyResults.stream()
            .map(list -> list.stream().collect(
                Collectors.toMap(dedupKeyFunction, r -> r, (a, b) -> a, LinkedHashMap::new)))
            .collect(Collectors.toList());

    if (strategy == VerifyMergeStrategy.UNION) {
        // 并集：所有扫描器结果的 key 取并集
        Set<String> allKeys = maps.stream()
                .flatMap(m -> m.keySet().stream())
                .collect(Collectors.toSet());
        return allKeys.stream()
                .map(key -> maps.stream()
                        .filter(m -> m.containsKey(key))
                        .map(m -> m.get(key))
                        .reduce(this::mergeConflict))
                .filter(Optional::isPresent)
                .map(Optional::get)
                .collect(Collectors.toList());
    } else {
        // 交集：所有扫描器都发现的 key
        Set<String> commonKeys = new HashSet<>(maps.get(0).keySet());
        for (int i = 1; i < maps.size(); i++) {
            commonKeys.retainAll(maps.get(i).keySet());
        }
        return commonKeys.stream()
                .map(key -> maps.get(0).get(key))
                .collect(Collectors.toList());
    }
}
```

### 4.2 冲突解决

```java
/**
 * 并集模式下，同一漏洞被多扫描器发现时的字段合并
 */
private VulScanTaskSubResultDO mergeConflict(VulScanTaskSubResultDO a, VulScanTaskSubResultDO b) {
    VulScanTaskSubResultDO merged = new VulScanTaskSubResultDO();
    merged.setAssetId(a.getAssetId());
    merged.setVulId(a.getVulId());
    merged.setVulPort(a.getVulPort());
    merged.setVulTransProto(a.getVulTransProto());
    merged.setVulSvc(a.getVulSvc());
    merged.setVulLevel(Math.max(a.getVulLevel(), b.getVulLevel()));
    merged.setVulName(StringUtils.firstNonBlank(a.getVulName(), b.getVulName()));
    merged.setVulDesc(StringUtils.firstNonBlank(a.getVulDesc(), b.getVulDesc()));
    merged.setEngHash("MULTI");
    merged.setEvidenceSources(Arrays.asList(a.getEngHash(), b.getEngHash()));
    if (a.getTransferTime() != null && b.getTransferTime() != null) {
        merged.setTransferTime(a.getTransferTime().compareTo(b.getTransferTime()) < 0
                ? a.getTransferTime() : b.getTransferTime());
    }
    return merged;
}
```

### 4.3 dedupKey 函数

```java
/**
 * 漏洞实例去重键，与 vul_archive_inst 唯一键一致
 */
public static String dedupKey(VulScanTaskSubResultDO r) {
    return Constant.concat(
        r.getAssetId(),
        r.getVulPort(),
        r.getVulTransProto(),
        r.getVulSvc(),
        r.getVulId()
    );
}
```

### 4.4 验证阶段编排（vul-pass OpenTaskOrchestrator 扩展）

```java
/**
 * 排查阶段完成后，autoVerify=true 时自动触发验证阶段
 */
public void triggerVerificationPhase(VulScanTaskDO surveyTask) {
    VulScanTaskDO verifyTask = new VulScanTaskDO();
    verifyTask.setBizLine(surveyTask.getBizLine());
    verifyTask.setTskPhase("2");
    verifyTask.setProcMethod(VulProcessMethodEnum.CROSS_SCAN_VERIFICATION.getCode());
    verifyTask.setVerifyMergeStrategy(surveyTask.getVerifyMergeStrategy());
    verifyTask.setVerifyScannerVendors(surveyTask.getVerifyScannerVendors());
    verifyTask.setExternalTaskId(surveyTask.getExternalTaskId());
    verifyTask.setPartnerId(surveyTask.getPartnerId());

    List<VulArchiveInstDO> surveyFindings = vulArchiveInstRepository
            .findByTskSubIds(surveyTask.getSubTaskIds());

    List<String> vendors = Arrays.asList(verifyTask.getVerifyScannerVendors().split(","));
    for (int i = 0; i < vendors.size(); i++) {
        String vendor = vendors.get(i);
        VulScanTaskSubDO subTask = new VulScanTaskSubDO();
        subTask.setScanPhase(2);
        subTask.setScannerVendor(vendor);
        subTask.setVerifyRound(i + 1);
        subTask.setVulKeys(surveyFindings.stream()
                .map(VulArchiveInstDO::getVulId)
                .collect(Collectors.joining(",")));
        String surveyId = taskClient.createAndDispatch(subTask);
        subTask.setExternalSurveyId(surveyId);
    }

    vulScanTaskRepository.save(verifyTask);
    vulScanTaskSubRepository.saveBatch(verifyTask.getSubTasks());
}
```

### 4.5 验证阶段结果回收（Kafka 监听扩展）

```java
/**
 * 监听验证阶段子任务完成，所有验证子任务完成后触发合并
 */
@KafkaListener(topics = "dr_vul_scan_task_status")
public void onVerifySubTaskStatusChanged(SubTaskStatusEvent event) {
    if (event.getScanPhase() != 2) return;

    VulScanTaskDO verifyTask = vulScanTaskRepository.findBySubTaskId(event.getPassSubTaskId());
    List<VulScanTaskSubDO> allSubs = verifyTask.getSubTasks();
    List<VulScanTaskSubDO> finishedSubs = allSubs.stream()
            .filter(s -> "FINISHED".equals(s.getTskStat()))
            .collect(Collectors.toList());

    if (finishedSubs.size() == allSubs.size()) {
        List<List<VulScanTaskSubResultDO>> surveyResults = new ArrayList<>();
        for (VulScanTaskSubDO sub : finishedSubs) {
            List<VulScanTaskSubResultDO> results = taskClient
                    .getSurveyResults(sub.getExternalSurveyId());
            surveyResults.add(results);
        }

        List<VulScanTaskSubResultDO> merged = mergeVerifyResults(
                surveyResults,
                VerifyMergeStrategy.valueOf(verifyTask.getVerifyMergeStrategy()),
                r -> dedupKey(r));

        handlerVulProcess(verifyTask.getSubTasks().get(0), merged);

        // 通知 open-api-service（携带 tsk_phase=2，供推迟回调判断）
        notifyOpenApi(verifyTask, 2);
    }
}
```

---

## 五、与现有代码的兼容性

### 5.1 不改动的部分

| 能力 | 现有代码 | 保持不变 |
|------|----------|----------|
| transition 状态跃迁规则 | `TransitionEnum` 静态规则表 | ? |
| PHASE_VALIDATION 跃迁 | EXISTENT→3, STILL_EXIST→2 | ? |
| handlerVulProcess 核心 | recycle → transition → writeVulInstLedger | ? |
| CROSS_SCAN_VERIFICATION | procMethod=1026 | ? |
| VulCrossVerifyParser | 交叉扫描结果解析 | ? |
| buildVulInfoLstByEngHashMap | 多设备结果合并（并集） | ?（UNION 模式可复用） |

### 5.2 新增的部分

| 能力 | 位置 | 说明 |
|------|------|------|
| `VerifyMergeStrategy` 枚举 | `infra/utils/enums/` | UNION / INTERSECT |
| `mergeVerifyResults` 方法 | `domain/pass/service/business/impl/` | 合并逻辑 |
| `triggerVerificationPhase` 方法 | `OpenTaskOrchestrator` | 排查→验证自动衔接 |
| `auto_verify` 字段 | `vul_scan_task` 表 | Liquibase 新增 |
| `verify_merge_strategy` 字段 | `vul_scan_task` 表 | Liquibase 新增 |
| `verify_scanner_vendors` 字段 | `vul_scan_task` 表 | Liquibase 新增 |
| `scan_phase` 字段 | `vul_scan_task_sub` 表 | Liquibase 新增 |
| `verify_round` 字段 | `vul_scan_task_sub` 表 | Liquibase 新增 |
| 验证阶段 Kafka 监听 | `SubTaskStatusKafkaListener` | scanPhase=2 时触发合并 |

### 5.3 部侧考核不受影响

- 部侧验证工单（subType=32）走现有 dispatch 链路
- `verify_merge_strategy` 默认 `INTERSECT`
- 部侧不配置 `verify_scanner_vendors`，沿用现有 engHash 分配逻辑
- transition 规则不变

---

## 六、SOC_DUAL 概念修订

### 6.1 原方案

```text
scan_policy=SOC_DUAL → 排查阶段同时下发 NESSUS + LM → 并集入库
```

**问题**：在排查阶段做双扫描器并集，是特殊定制，且与部侧交集语义冲突。

### 6.2 修订方案

```text
autoVerify=true（排查阶段单扫描器）
verify_merge_strategy=UNION（验证阶段 SOC 并集）
verify_scanner_vendors=NESSUS,LM（验证阶段双扫描器）
```

### 6.3 修订后的三发起方矩阵

| 维度 | OPEN（SOC） | METRIC | ASSESS（部侧） |
|------|-------------|--------|----------------|
| autoVerify | true（默认） | 可选 | 不涉及 |
| 排查阶段扫描器 | 单（engHash 轮询） | 单 | 单/多 |
| 验证阶段扫描器 | NESSUS + LM | 可选 | 厂商A + 厂商B |
| 验证合并策略 | **SOC 标准（并集）** | 可选 | **部侧标准（交集）** |
| procMethod（排查） | 1021 | 1021 | 1021 |
| procMethod（验证） | 1026 | 1026 | 1026 |
| tskPhase（排查） | 1 | 1 | 1 |
| tskPhase（验证） | 2 | 2 | 2 |
| TASK_COMPLETED 回调 | 验证后 | 排查后 | 不涉及 |

### 6.4 ScanPolicyEnum 修订

```java
public enum ScanPolicyEnum {
    SINGLE,   // 单扫描器（默认）
    CUSTOM;   // 自定义（保留扩展）
}
```

**`SOC_DUAL` 枚举值废弃**，改为 `autoVerify=true` + `verify_merge_strategy=UNION` + `verify_scanner_vendors=NESSUS,LM` 的组合。

---

## 七、数据流完整示例（SOC 接入，并集）

### 7.1 排查阶段

```text
输入: targets=10.10.1.2, scanTemplateId=1001

vul_scan_task:
  id=1001, biz_line=OPEN, auto_verify=1, tsk_phase=1, proc_method=1021
  verify_merge_strategy=UNION, verify_scanner_vendors=NESSUS,LM

vul_scan_task_sub:
  id=2001, tsk_id=1001, scan_phase=1, scanner_vendor=NESSUS
  external_survey_id=SV-001

task-center 执行 SV-001 (Nessus):
  结果: [{vulId=CVE-2021-1, asset=10.10.1.2, port=22}, {vulId=CVE-2021-2, asset=10.10.1.2, port=80}]

vul_archive_inst 入库:
  VI-001: CVE-2021-1, 10.10.1.2:22, vulInfoStat=1
  VI-002: CVE-2021-2, 10.10.1.2:80, vulInfoStat=1
```

### 7.2 验证阶段（SOC 并集）

```text
vul_scan_task:
  id=1002, biz_line=OPEN, auto_verify=1, tsk_phase=2, proc_method=1026
  verify_merge_strategy=UNION, verify_scanner_vendors=NESSUS,LM

vul_scan_task_sub:
  id=2002, tsk_id=1002, scan_phase=2, scanner_vendor=NESSUS, verify_round=1
  external_survey_id=SV-002
  id=2003, tsk_id=1002, scan_phase=2, scanner_vendor=LM, verify_round=2
  external_survey_id=SV-003

task-center 执行:
  SV-002 (Nessus): [{CVE-2021-1, 10.10.1.2:22}, {CVE-2021-3, 10.10.1.2:443}]
  SV-003 (LM):     [{CVE-2021-1, 10.10.1.2:22}, {CVE-2021-2, 10.10.1.2:80}]

mergeVerifyResults（SOC 并集）:
  dedupKey = assetId + vulPort + vulTransProto + vulSvc + vulId
  Nessus: {10.10.1.2:22:CVE-2021-1, 10.10.1.2:443:CVE-2021-3}
  LM:     {10.10.1.2:22:CVE-2021-1, 10.10.1.2:80:CVE-2021-2}
  UNION:  {10.10.1.2:22:CVE-2021-1, 10.10.1.2:443:CVE-2021-3, 10.10.1.2:80:CVE-2021-2}

按合并策略确定状态:
  CVE-2021-1@22: 两次均发现 → 交叉部分 → VALIDATED_TRUE(2)
  CVE-2021-3@443: 仅 NESSUS 发现 → 合并后初始发现 → INITIAL_DISCOVERY(1)
  CVE-2021-2@80: 仅 LM 发现 → 合并后初始发现 → INITIAL_DISCOVERY(1)

最终:
  VI-001: vulInfoStat=2 (已验证有效)
  VI-002: vulInfoStat=1 (初始发现)
  VI-003: vulInfoStat=1 (初始发现，验证阶段新发现)
```

### 7.3 对比：部侧交集模式

```text
mergeVerifyResults（部侧交集）:
  INTERSECT: {10.10.1.2:22:CVE-2021-1}  (仅两边都发现的)

按合并策略确定状态:
  VI-001 (CVE-2021-1@22): 两次均发现 → VALIDATED_TRUE(2)
  VI-002 (CVE-2021-2@80): 仅排查发现，验证未发现 → VALIDATED_FALSE(3)

最终:
  VI-001: vulInfoStat=2 (已验证有效)
  VI-002: vulInfoStat=3 (已验证误报)
```

---

## 八、对 PRD 和任务矩阵的影响

### 8.1 PRD 修订项

| 章节 | 原内容 | 修订为 |
|------|--------|--------|
| §六.2 SOC 双扫并集规则 | 排查阶段 SOC_DUAL 双扫并集 | 排查阶段单扫 + 验证阶段 SOC 并集，autoVerify=true |
| §六.3 结果回收 | 排查完成直接并集入库 | 排查完成→自动触发验证阶段→合并→推迟回调 |
| §四 数据模型 | scan_policy=SOC_DUAL | autoVerify + verify_merge_strategy + verify_scanner_vendors |
| §三 Wave 矩阵 | W1 含 SOC_DUAL 并集 | W1 含双阶段编排 + mergeVerifyResults |

### 8.2 任务矩阵修订

| 任务 | 原范围 | 修订范围 |
|------|--------|----------|
| W1b-PASS-ORCH | SOC_DUAL 双扫拆分 | 双阶段编排：排查→验证自动衔接 |
| W1b-PASS-MERGE | SOC 并集合并器 | `mergeVerifyResults`（UNION + INTERSECT） |
| W1b-PASS-VERIFY | （新增） | `triggerVerificationPhase` + 验证阶段 Kafka 监听 |
| W1b-OPEN-AUTOVERIFY | （新增） | 创建任务新增 autoVerify 参数 |
| W1b-OPEN-DEFERRED-CALLBACK | （新增） | 推迟回调控制（autoVerify=true） |

### 8.3 新增 DDL

```sql
-- vul_scan_task 新增
ALTER TABLE vul_scan_task ADD COLUMN auto_verify TINYINT(1) DEFAULT 1;
ALTER TABLE vul_scan_task ADD COLUMN verify_merge_strategy VARCHAR(16) DEFAULT 'INTERSECT';
ALTER TABLE vul_scan_task ADD COLUMN verify_scanner_vendors VARCHAR(256);

-- vul_scan_task_sub 新增
ALTER TABLE vul_scan_task_sub ADD COLUMN scan_phase TINYINT DEFAULT 1;
ALTER TABLE vul_scan_task_sub ADD COLUMN verify_round INT;

-- open_task 新增
ALTER TABLE open_task ADD COLUMN auto_verify TINYINT(1) DEFAULT 1;
```

---

## 九、风险与对策

| 风险 | 对策 |
|------|------|
| 验证阶段双扫增加任务耗时 | autoVerify 可配置，Partner 可选择仅排查（false） |
| UNION 模式产生大量初始发现 | SOC 场景合并后初始发现单独标记，Partner 可后续验证 |
| INTERSECT 模式误报率升高 | 部侧场景已有成熟流程，transition 规则不变 |
| 验证阶段扫描器选择与排查阶段不同 | verify_scanner_vendors 可配置为与排查阶段相同或不同 |
| 多扫描器结果字段冲突 | mergeConflict 策略：vulLevel 取高、描述取非空、engHash 记 MULTI |

---

## 十、变更日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-06-17 | 双阶段模型、UNION/INTERSECT 策略、autoVerify + 推迟回调、SOC 并集与部侧交集统一 |

## 七、修复核验阶段（verify-fix）- OPEN 专用

> 与 §3 双阶段「排查 + 验证」并列，为实例生命周期**第三条扫描链路**。

### 7.1 定位

| 维度 | 排查+验证（autoVerify） | 修复核验（verify-fix） |
|------|-------------------------|----------------------|
| 触发 | 创建任务 / autoVerify 自动衔接 | Partner POST verify-fix |
| 扫描器 | 可双扫（SOC UNION / 部侧 INTERSECT） | **单厂商**（最近一次 scanner_vendor） |
| 扫描类型 | 排查 + 交叉验证 | **全量复扫**（不支持指定产品漏洞） |
| 结果处理 | 并集/交集合并入库 | 全量回收，**仅过滤目标 vulInfoID** 改状态 |
| 状态 | 1 -> 2/3 | 5 -> 6/7/10 |

### 7.2 流程

```text
Partner verify-fix (vulInfoStat=5)
  -> vul-pass 解析 vulInfoID
  -> 系统漏洞库取 assetIp
  -> 最近 sub.scanner_vendor
  -> task-center 全量 survey
  -> recycle 全量结果
  -> 仅目标漏洞：未检出->6，仍检出->7，失败->10
  -> Webhook + VERIFY_FIX_SCAN 外发
```
