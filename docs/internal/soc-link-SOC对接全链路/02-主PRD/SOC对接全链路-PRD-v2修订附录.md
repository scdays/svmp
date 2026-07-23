# SOC 对接全链路 PRD · 修订附录

> **状态**：正式采纳
> **日期**：2026-06-17
> **关联**：
> - 主 PRD：`SOC对接全链路-PRD.md`
> - 双阶段方案：`双阶段交叉扫描方案-SOC并集与部侧交集统一.md`
> - 任务矩阵：`features/soc-link-task-matrix.yaml`
> - 对外 API 文档：`external/网络安全漏洞管理平台 · API 接口文档.md`（v1.0.6）
> **范围**：本附录是对主 PRD 的正式修订，涉及创建任务接口、状态流转、回调时机、外发内容。主 PRD 中与之冲突的部分以本附录为准。

---

## 一、修订摘要

| # | 修订点 | 影响范围 | 优先级 |
|---|--------|----------|--------|
| 1 | 创建任务新增 `autoVerify` 参数（默认 true） | §5.1.2 创建任务、附录 G.2、open_task 表、vul_scan_task 表 | P0 |
| 2 | autoVerify=true 时推迟 Webhook 回调至验证阶段完成 | §1.3.1 状态流转、§6 Webhook | P0 |
| 3 | autoVerify=true 时 EXPORT_READY 外发含两阶段合并结果 | §5.6 数据外发 | P0 |
| 4 | 双阶段扫描编排（排查→验证自动衔接） | vul-pass 内部 | P0 |
| 5 | 双扫结果合并策略接入定制（部侧交集 / SOC 并集） | vul-pass 内部 | P0 |
| 6 | SOC_DUAL 概念废弃，改为 autoVerify + verify_scanner_vendors 组合 | 数据模型 | P0 |

**不修订的部分**：状态码定义（附录 A）、verify/remediate/verify-fix 接口约束、Webhook 事件类型清单。

---

## 二、创建任务接口修订

### 2.1 POST /tasks/vul 请求体新增字段

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|:--:|------|------|
| autoVerify | boolean | ○ | **true** | 是否开启自动验证阶段。true 时排查完成后平台自动触发验证阶段扫描，全部完成后统一回调 `TASK_COMPLETED` 与 `EXPORT_READY`；false 时排查完成即回调（原语义），实例为 1（初始发现），由 Partner 主动 verify。双扫结果合并策略在接入 Partner 时定制，详见下方说明 |

> **autoVerify 双扫合并策略**：开启自动验证时，平台执行两阶段扫描（排查 + 验证），双扫结果合并策略在接入 Partner 时定制，支持以下两种模式：
>
> 1. **部侧标准（交集）**：第一次扫描结果为初始发现（`vulInfoStat=1`）；第二次交叉扫描验证，两次均发现 → 已验证有效（`2`），仅一次发现 → 已验证误报（`3`）。
> 2. **SOC 标准（并集）**：两次扫描结果取并集，合并后均为初始发现（`vulInfoStat=1`）；其中交叉部分（两次均发现）→ 已验证有效（`2`）。

**请求示例**：

```json
{
  "extTaskId": "EXT-TASK-2026-0001",
  "type": "VULN_SYSTEM",
  "targets": {
    "hosts": ["10.10.1.2"]
  },
  "scanTemplateId": 1001,
  "autoVerify": true,
  "callbackUrl": "https://partner.example.com/webhooks/svmp"
}
```

### 2.2 POST /tasks/file 配置文件（附录 G.2）

XML 创建任务（§5.1.1）的请求体不新增参数行，autoVerify 通过附录 G.2 的 XML 路径配置：

```xml
<scanTask>
  <server>
    <taskName>2026Q2-核心业务系统排查</taskName>
    <autoVerify>true</autoVerify>
    <targets>10.10.1.2</targets>
  </server>
  ...
</scanTask>
```

XML 路径：`/scanTask/server/autoVerify`，类型 boolean，可选，默认 true。

### 2.3 Partner 级默认配置

Partner 开通时可配置默认 `autoVerify` 值，请求体未传时取 Partner 默认。SOC 接入方默认 `true`，普通 Partner 可设为 `false`。

| 配置项 | 说明 | SOC 默认 | 普通 Partner 默认 |
|--------|------|----------|------------------|
| `defaultAutoVerify` | 创建任务时 autoVerify 缺省值 | true | false |
| `autoVerifyScannerVendors` | 自动验证使用的扫描器厂商 | NESSUS,LM | — |
| `autoVerifyMergeStrategy` | 自动验证合并策略 | **SOC 标准（并集）** | **部侧标准（交集）** |

### 2.4 响应（不变）

```json
{
  "code": 0,
  "data": {
    "taskId": "TASK-7f3a2b1c",
    "status": "ACCEPTED",
    "createdAt": "2026-05-18T08:00:00Z"
  }
}
```

---

## 三、状态流转修订

### 3.1 autoVerify=true（SOC 默认）

```text
创建任务（排查阶段）
  → vulInfoStat = 1（初始发现）
  → 【不回调，不外发】
  → 自动触发验证阶段

验证阶段（二次扫描，双扫结果合并策略接入定制）
  → 按合并策略确定 vulInfoStat：
     部侧标准（交集）：两次均发现 → 2（已验证有效）；仅一次发现 → 3（已验证误报）
     SOC 标准（并集）：合并后均为 1（初始发现）；交叉部分 → 2（已验证有效）
  → 【全部完成】

统一回调
  → Webhook: TASK_COMPLETED（instances[].vulInfoStat 为验证后终态）
  → EXPORT_READY（exportStage=TASK_COMPLETED，含两阶段合并结果）

后续（Partner 驱动）
  → remediate → 5/9
  → verify-fix → 6/7/10
```

### 3.2 autoVerify=false（普通 Partner，原语义）

```text
创建任务（排查阶段）
  → vulInfoStat = 1（初始发现）
  → Webhook: TASK_COMPLETED（instances[].vulInfoStat = 1）
  → EXPORT_READY

后续（Partner 驱动）
  → verify → 2/3
  → remediate → 5/9
  → verify-fix → 6/7/10
```

### 3.3 状态约束（不修订）

- verify 前置 `vulInfoStat ∈ {0,1}`（保持原约束）
- autoVerify=true 时 Partner 通常不主动调 verify（实例已是终态）
- 3（误报）后禁止修复/备案（不变）

---

## 四、Webhook 回调时机修订

### 4.1 回调时机矩阵

| 事件 | autoVerify=true | autoVerify=false |
|------|------------------|-------------------|
| `TASK_COMPLETED` | 排查+验证全部完成后 | 排查完成后 |
| `TASK_FAILED` | 任一阶段失败时 | 排查失败时 |
| `EXPORT_READY` | 验证完成后 | 排查完成后 |
| `INSTANCE_VERIFY_COMPLETED` | （autoVerify 不走 verify 接口） | Partner 调 verify 后 |
| `INSTANCE_REMEDIATE_COMPLETED` | Partner 调 remediate 后 | 同左 |
| `INSTANCE_VERIFY_FIX_COMPLETED` | Partner 调 verify-fix 后 | 同左 |

### 4.2 TASK_COMPLETED payload（autoVerify=true）

```json
{
  "eventId": "evt-20260518-0001",
  "eventType": "TASK_COMPLETED",
  "occurredAt": "2026-05-18T10:30:00Z",
  "partnerId": "partner-soc-01",
  "payload": {
    "taskId": "TASK-7f3a2b1c",
    "extTaskId": "EXT-TASK-2026-0001",
    "status": "COMPLETED",
    "summary": {
      "totalInstances": 3,
      "verifiedValid": 2,
      "falsePositive": 1,
      "initialDiscovery": 0
    }
  }
}
```

autoVerify=true 时，TASK_COMPLETED 的 `summary` 反映验证后终态统计，Partner 收到即为终态。

### 4.3 不新增 Webhook 事件

保持原有 6 个事件类型，不新增 `INSTANCE_AUTO_VERIFIED`。验证阶段的结果通过推迟的 `TASK_COMPLETED` 统一交付。

---

## 五、扫描结果数据外发修订

### 5.1 exportStage 语义调整

| exportStage | autoVerify=true | autoVerify=false |
|-------------|------------------|-------------------|
| `TASK_COMPLETED` | 验证阶段完成后的汇总外发（含两阶段合并结果） | 排查完成后的外发（原语义） |
| `VERIFY_SCAN` | 不产生（自动验证不单独外发） | Partner 调 verify 触发复扫后 |
| `VERIFY_FIX_SCAN` | Partner 调 verify-fix 后 | 同左 |

### 5.2 autoVerify=true 时 EXPORT_READY 内容

外发内容包含**排查+验证两阶段的合并结果**：

```text
TaskExport / taskExport
├── export                 # 外发记录元数据
├── task                   # 任务信息
├── summary                # 汇总统计（验证后终态）
│   ├── totalInstances
│   ├── verifiedValid (stat=2)
│   ├── falsePositive (stat=3)
│   └── initialDiscovery (stat=1, 验证阶段新发现)
├── targets / target[]                    # 扫描目标
├── liveProbeResults / liveProbeResult[]  # 存活探测（排查阶段）
├── portScanResults / portScanResult[]    # 端口扫描（排查阶段）
├── vulnerabilities / vulnerability[]     # 漏洞聚合
│   └── instances[]
│       ├── vulInfoStat: 2/3/1            # 验证后最终状态
│       ├── evidence                      # 证据
│       └── scanPhase: 1/2               # 标识该实例由哪个阶段发现
└── appendices[]                          # 附录
```

### 5.3 EXPORT_READY payload（autoVerify=true）

```json
{
  "eventId": "evt-20260518-0002",
  "eventType": "EXPORT_READY",
  "payload": {
    "exportId": "EXP-20260518-7f3a",
    "taskId": "TASK-7f3a2b1c",
    "extTaskId": "EXT-TASK-2026-0001",
    "format": "json",
    "exportStage": "TASK_COMPLETED",
    "dataType": "SYSTEM_VULNERABILITY",
    "recordCount": 3,
    "downloadUrl": "https://..."
  }
}
```

---

## 六、数据模型修订

### 6.1 open_task 表新增

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `auto_verify` | TINYINT(1) | 1 | 是否开启自动验证阶段 |

### 6.2 vul_scan_task 表新增

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `auto_verify` | TINYINT(1) | 1 | 是否开启自动验证 |
| `verify_merge_strategy` | VARCHAR(16) | INTERSECT | 验证阶段合并策略：UNION（SOC 并集）/ INTERSECT（部侧交集），接入 Partner 时定制 |
| `verify_scanner_vendors` | VARCHAR(256) | — | 验证阶段扫描器厂商列表，逗号分隔 |

### 6.3 vul_scan_task_sub 表新增

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `scan_phase` | TINYINT | 1 | 扫描阶段：1=排查，2=验证 |
| `scanner_vendor` | VARCHAR(16) | — | 扫描器厂商：NESSUS/LM/AH |
| `verify_round` | INT | — | 验证轮次（同一验证阶段的多扫描器编号） |

### 6.4 SOC_DUAL 概念废弃

原 `scan_policy=SOC_DUAL` 废弃，改为：

```text
auto_verify = true
verify_scanner_vendors = NESSUS,LM
verify_merge_strategy = UNION
```

### 6.5 三发起方统一矩阵

| 维度 | OPEN（SOC） | METRIC | ASSESS（部侧） |
|------|-------------|--------|----------------|
| autoVerify | true（默认） | 可选 | 不涉及（部侧走原有工单） |
| 排查阶段扫描器 | 单（engHash 轮询） | 单 | 单/多 |
| 验证阶段扫描器 | NESSUS + LM | 可选 | 厂商A + 厂商B |
| 验证合并策略 | **SOC 标准（并集）** | 可选 | **部侧标准（交集）** |
| procMethod（排查） | 1021 | 1021 | 1021 |
| procMethod（验证） | 1026 | 1026 | 1026 |
| tskPhase（排查） | 1 | 1 | 1 |
| tskPhase（验证） | 2 | 2 | 2 |
| TASK_COMPLETED 回调 | 验证后 | 排查后 | 不涉及 |

---

## 七、完整时序示例

### 7.1 SOC 接入（autoVerify=true，SOC 并集）

```text
T0  Partner POST /tasks/vul { autoVerify: true, targets: {hosts:["10.10.1.2"]} }
    → open_task 创建 (auto_verify=1)
    → vul_scan_task 创建 (tsk_phase=1, proc_method=1021, auto_verify=1)
    → vul-pass dispatch（排查阶段，单扫描器）
    → 返回 taskId, status=ACCEPTED

T1  排查阶段完成
    → vul_archive_inst 入库:
       VI-001: CVE-2021-1@10.10.1.2:22, vulInfoStat=1
       VI-002: CVE-2021-2@10.10.1.2:80, vulInfoStat=1
    → 【不回调 TASK_COMPLETED】
    → 【不外发 EXPORT_READY】
    → autoVerify=true，自动触发验证阶段

T2  [平台内部] 自动触发验证阶段
    → vul_scan_task 创建 (tsk_phase=2, proc_method=1026)
    → verify_scanner_vendors=NESSUS,LM
    → 双扫描器下发:
       sub-1: scan_phase=2, scanner_vendor=NESSUS, verify_round=1
       sub-2: scan_phase=2, scanner_vendor=LM, verify_round=2

T3  验证阶段双扫描器完成
    → 拉取各 survey 结果:
       NESSUS: [CVE-2021-1@22, CVE-2021-3@443]
       LM:     [CVE-2021-1@22, CVE-2021-2@80]
    → mergeVerifyResults（SOC 并集）:
       合并结果 = [CVE-2021-1@22, CVE-2021-3@443, CVE-2021-2@80]
    → 按合并策略确定状态:
       CVE-2021-1@22: 两次均发现 → 交叉部分 → VALIDATED_TRUE(2)
       CVE-2021-3@443: 仅 NESSUS 发现 → 合并后初始发现 → INITIAL_DISCOVERY(1)
       CVE-2021-2@80: 仅 LM 发现 → 合并后初始发现 → INITIAL_DISCOVERY(1)
    → 【全部完成】

T4  统一回调
    → Webhook: TASK_COMPLETED
       payload: {
         taskId, status: COMPLETED,
         summary: { totalInstances:3, verifiedValid:1, falsePositive:0, initialDiscovery:2 }
       }
    → EXPORT_READY (exportStage=TASK_COMPLETED)
       含 targets[] + liveProbeResults[] + portScanResults[] + vulnerabilities[]
       vulnerabilities[].instances[].vulInfoStat = 2/1/1（验证后终态）

T5  Partner 收到 TASK_COMPLETED
    → 实例状态已是终态
    → 可继续 remediate / verify-fix
```

### 7.2 部侧标准（autoVerify=true，部侧交集）

```text
T0  Partner POST /tasks/vul { autoVerify: true, targets: {hosts:["10.10.1.2"]} }
    → 返回 taskId, status=ACCEPTED

T1  排查阶段完成
    → vul_archive_inst 入库:
       VI-001: CVE-2021-1@10.10.1.2:22, vulInfoStat=1
       VI-002: CVE-2021-2@10.10.1.2:80, vulInfoStat=1
    → 自动触发验证阶段

T2  验证阶段双扫描器完成
    → NESSUS: [CVE-2021-1@22, CVE-2021-3@443]
    → LM:     [CVE-2021-1@22, CVE-2021-2@80]
    → mergeVerifyResults（部侧交集）:
       交叉部分 = [CVE-2021-1@22]
    → 按合并策略确定状态:
       VI-001 (CVE-2021-1@22): 两次均发现 → VALIDATED_TRUE(2)
       VI-002 (CVE-2021-2@80): 仅排查发现，验证未发现 → VALIDATED_FALSE(3)

T3  统一回调
    → Webhook: TASK_COMPLETED
       summary: { totalInstances:2, verifiedValid:1, falsePositive:1, initialDiscovery:0 }
```

### 7.3 普通 Partner（autoVerify=false）

```text
T0  Partner POST /tasks/vul { autoVerify: false }
    → 返回 taskId, status=ACCEPTED

T1  排查阶段完成
    → vul_archive_inst 入库: vulInfoStat=1
    → Webhook: TASK_COMPLETED（instances[].vulInfoStat=1）
    → EXPORT_READY

T2  Partner 自行 verify
    → POST /instances/VI-001/verify { verifyResult: VALID, srcMethod: 1021 }
    → vulInfoStat → 2
    → Webhook: INSTANCE_VERIFY_COMPLETED
```

---

## 八、任务矩阵修订

### 8.1 W1b 任务清单

| 任务 ID | 工程 | 说明 | 工时 | 依赖 |
|---------|------|------|------|------|
| W1b-PASS-ORCH | vul-pass | 双阶段扫描编排（排查→验证自动衔接） | 16h | W1a-VTC-API |
| W1b-PASS-MERGE | vul-pass | 验证结果合并器（UNION/INTERSECT） | 12h | W1b-PASS-ORCH |
| W1b-PASS-VERIFY | vul-pass | 验证阶段 Kafka 监听与生命周期衔接 | 16h | W1b-PASS-MERGE, W1a-VTC-API |
| W1b-OPEN-AUTOVERIFY | open-api-service | 创建任务新增 auto_verify 参数 | 6h | W1b-PASS-ORCH |
| W1b-OPEN-DEFERRED-CALLBACK | open-api-service | 推迟回调控制（autoVerify=true） | 10h | W1b-OPEN-AUTOVERIFY, W1b-PASS-VERIFY |

**废弃任务**：W1b-PASS-DUAL（原 SOC_DUAL 双扫拆分）

### 8.2 任务依赖图

```text
W1a-VTC-API (vuln-task-center API)
    │
    ├──> W1b-PASS-ORCH (vul-pass 双阶段编排)
    │        │
    │        ├──> W1b-PASS-MERGE (合并器)
    │        │        │
    │        │        └──> W1b-PASS-VERIFY (验证阶段监听)
    │        │                 │
    │        │                 └──> W1b-OPEN-DEFERRED-CALLBACK (推迟回调)
    │        │
    │        └──> W1b-OPEN-AUTOVERIFY (auto_verify 参数)
    │                     │
    │                     └──> W1b-OPEN-DEFERRED-CALLBACK (推迟回调)
    │
    └──> W1c-PASS-LIFECYCLE (双轨存储，已有)
```

---

## 九、对外 API 接口文档修订说明

### 9.1 已修订章节（v1.0.6）

| 章节 | 修订内容 |
|------|----------|
| §1.3.1 状态流转 | 补充 autoVerify=true/false 两种回调时机说明及验证阶段合并策略 |
| §5.1.2 创建任务（JSON） | 请求体新增 autoVerify 参数（默认 true）及双扫合并策略说明 |
| §5.1.2 请求示例 | JSON 示例补充 `"autoVerify": true` |
| 附录 G.2 `<server>` 元素表 | 新增 `/scanTask/server/autoVerify` XML 路径 |
| §5.6.2 外发触发场景 | `TASK_COMPLETED` 补充 autoVerify=true 时含两阶段合并结果 |
| §6 TASK_COMPLETED payload | 新增 `summary.initialDiscovery` 字段 |

### 9.2 不修订的章节

| 章节 | 不修订原因 |
|------|------------|
| 附录 A 状态码 | 状态码定义不变 |
| §5.1.1 创建任务（XML） | 请求体不新增参数行，autoVerify 通过附录 G.2 XML 路径配置 |
| §5.3 verify 接口 | 前置状态约束不变（{0,1}），autoVerify=true 时通常不主动调 verify |
| §5.4 remediate 接口 | 不变 |
| §5.5 verify-fix 接口 | **v2.1 补充编排链路**（§8.4 / 附录十一） |
| §6 Webhook 事件类型清单 | 不新增事件 |

---

## 十、变更日志

| 版本 | 日期 | 说明 |
|------|------|------|
| v2.1 | 2026-06-17 | 纳入 §5.5 修复核验全链路编排（单厂商全量复扫、结果过滤判定） |
| v2 | 2026-06-17 | 采纳 autoVerify 参数 + 推迟回调方案；合并策略接入定制（部侧交集 / SOC 并集）；API 改动最小化 |

## 十一、修复核验（verify-fix）编排修订（v2.1）

> **状态**：正式纳入 PRD 正文 §8.4。
> **依据**：`external/网络安全漏洞管理平台 · API 接口文档.md` §5.5、§6.4、§7（VERIFY_FIX_SCAN）

### 11.1 修订摘要

| # | 修订项 | 影响范围 | 优先级 |
|---|--------|----------|--------|
| 7 | 补齐修复核验全链路：Partner 发起 -> 解析 vulInfoID -> 资产 IP -> 最近扫描器 -> task-center 全量复扫 -> 过滤判定 6/7/10 | open-api / vul-pass / vuln-task-center / W3 | P0 |

### 11.2 与 autoVerify 双阶段的关系

- **排查 + 验证**（autoVerify）：仍走双阶段 + 可选 SOC_DUAL 并集。
- **修复核验**：独立异步链路，**单扫描器全量复扫**，不参与 UNION/INTERSECT 合并。

### 11.3 扫描下发要点

1. 从 `vulInfoID` 加载系统漏洞实例，取影响资产 IP 作为 targets。
2. 查询 `vul_scan_task_sub` 最近完成记录取 `scanner_vendor`。
3. task-center 下发**全量扫描**（不支持指定产品漏洞）。
4. 回收时 handler 仅对目标 `vulInfoID` 做存在性判定。

### 11.4 修订记录补充

| 版本 | 日期 | 说明 |
|------|------|------|
| v2.1 | 2026-06-17 | 纳入 §5.5 修复核验编排、外发 VERIFY_FIX_SCAN、W3 验收 |
