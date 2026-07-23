# 扫描时间窗管理（vul-pass）— 产品需求文档（PRD）

> **用途**：漏洞管理平台「扫描时间窗（Scan Window）+ 超窗暂停/恢复」能力的**唯一内部产品规格**；对齐对外《网络安全漏洞管理平台 · API 接口文档》1.0.7 变更；Multi-Agent 自动化开发的上游输入。
> **状态**：`草稿` · **v1.0 首版**（业务模型 + DDL + 状态机 + 调度器 + 对外接口）
> **版本**：v1.0
> **日期**：2026-07-16

| 属性 | 值 |
|------|-----|
| 功能编号 | **VULPASS-SCANWINDOW-P0** ~ **P3** |
| 模块名称 | 扫描时间窗管理（窗口策略 → 超窗暂停 → 到窗恢复 → 变更同步） |
| 主服务 | **`vul-pass`**（唯一业务执行面：窗口存储、调度、暂停/恢复语义） |
| 对外薄层 | **`open-api-service`**（仅对外 API 契约 + 鉴权 + Feign→vul-pass，**不承载调度业务**） |
| 契约源 | 《网络安全漏洞管理平台 · API 接口文档》1.0.7：§5.1.2 `scanWindows`、§5.1.3 暂停字段、§5.1.5 追加窗口、§5.1.6 暂停、§5.1.7 启动、§6.2/§6.7 `TASK_PAUSED`、§8 `TASK_WINDOW_WRITE`/`TASK_CONTROL`、§11 |
| **明确不做** | **`open-api-service` 修复核验编排改造**（CLAUDE.md 约束）；扫描器厂商私有 API 细节（封装在适配层，对 Partner 黑盒） |
| 关联 PRD | [`修复核验全链路-vul-pass-PRD.md`](../../verify-fix-修复核验全链路/04-子PRD与规格/修复核验全链路-vul-pass-PRD.md)（子任务/状态枚举复用）、`open-api-export-webhook-PRD.md`（Webhook 投递链路复用） |
| 工程路径 | 后端 `project_backend/svmp/vul-pass`；对外 `project_backend/svmp/open-api-service` |

---

## 0. 已确认产品决策

| # | 议题 | **结论** | 依据 |
|---|------|----------|------|
| D-01 | 扫描器不支持续扫时如何恢复 | **平台内部重新下发扫描任务 + 任务台重新绑定**；对 Partner 黑盒，`taskId` 不变 | 用户确认：平台对 Partner 不暴露扫描器任务分配 |
| D-02 | 重下发的成本失控保护 | **累计扫描次数上限 `maxScanAttempts`**；超限转 `FAILED` 并告警，防「超窗→重下→再超窗」僵尸循环 | 见 §9 风险 G2 |
| D-03 | 窗口如何同步给接入方 | **接口拉取为主（`GET 窗口策略`）+ 变更 Webhook 推送（`SCAN_WINDOW_CHANGED`）**；不以线下分发为唯一手段 | 用户确认「目前缺失」；线下无审计、易失联 |
| D-04 | 窗口建模范式 | **允许窗（ALLOW）+ 禁扫窗（DENY），DENY 优先**；有效可扫时间 = ALLOW − DENY | 补 1.0.7 仅有 ALLOW 的短板 |
| D-05 | 窗口时区 | **统一 UTC 存储；策略带 `timezone` 按机构本地时区解释**；展示层转本地 | 防 UTC/本地混用导致白天误扫（合规红线） |
| D-06 | 对外状态 vs 内部状态 | **分离**：对外 `PAUSED_WAITING_SCAN_WINDOW`/`PAUSED_NO_SCAN_WINDOW`；内部新增 `VulScanTaskStatEnum` 值，映射放 `open-api-service` assembler | 内部枚举保持业务语义 |
| D-07 | 创建任务是否接收窗口入参 | **不接收**。创建任务不含 `scanWindows` 入参；创建响应**新增 `estimatedStartAt`（预计启动时间）/ `matchedScanWindow` / `windowSource=POLICY`**。窗口一律走平台策略，接入方经 `GET /scan-windows/policy` 只读 | 走方案 A：纯策略，避免接入方维护第二份窗口 |

---

## 1. Why — 背景与目标

### 1.1 背景

对外 API 1.0.7 引入「扫描窗口 + 超时暂停处理」：任务下发可带 `scanWindows`（允许扫描时段），超窗未回收报告则任务进入暂停态,等待下一窗口或人工介入。当前 `vul-pass` / `open-api-service` **尚无任何扫描窗口 / 暂停能力的实现**（已核对 backend 源码，无 scanWindow/PAUSED 业务代码），属全新增量。

业务现实驱动：

| 场景 | 说明 |
|------|------|
| **变更/维护窗约束** | 运营商生产网禁止业务高峰主动扫描，仅维护窗（如凌晨）可扫 |
| **重保/护网封网** | 护网期、两会、大促期全程或分时段禁扫（**禁扫窗**，非可扫窗） |
| **超时暂停** | 单次扫描超出窗口仍未回收报告，需暂停等待下一窗口，而非直接失败 |
| **窗口动态变更** | 临时封网/临时加窗需同步给接入方，线下分发无法保证一致性 |

### 1.2 目标

1. **窗口权威化**：平台侧建模 ALLOW/DENY 多类型窗口策略，作为可扫时间的唯一权威。
2. **超窗自愈**：超窗未回收报告 → 自动暂停 → 到下一窗口自动恢复；无窗口 → 转人工介入态。
3. **契约对齐**：对外接口/状态/Webhook 与 API 1.0.7 完全一致。
4. **同步通道**：接入方可通过接口拉取窗口策略，并经 Webhook 感知变更。
5. **成本可控**：续扫不可用时重下发有次数上限，杜绝僵尸循环。

### 1.3 成功标准

| 指标 | 标准 |
|------|------|
| 超窗暂停 | RUNNING 任务超 `currentWindow.endAt` 且报告未回收 → 自动置 `PAUSED_*` 并发 `TASK_PAUSED` |
| 自动恢复 | `PAUSED_WAITING_SCAN_WINDOW` 到达下一窗口 → 自动置 `RUNNING`，恢复报告轮询 |
| 人工介入 | 无剩余窗口 → `PAUSED_NO_SCAN_WINDOW`，`manualOptions` 含追窗/启动 |
| DENY 优先 | 任一时刻命中 DENY 窗即不可扫，即使同时命中 ALLOW 窗 |
| 幂等 | 重复 pause/start 幂等；窗口边界迁移用乐观锁，多实例不重复下发扫描器指令 |
| 同步 | Partner 可 `GET` 拉取窗口策略；策略变更发 `SCAN_WINDOW_CHANGED` |
| 成本 | 重下发累计次数达 `maxScanAttempts` → `FAILED` + 告警 |

---

## 2. What — 时间窗业务模型（核心）

### 2.1 建模范式：ALLOW − DENY

> **有效可扫时间 = 命中至少一个 ALLOW 窗 且 未命中任何 DENY 窗**（DENY 优先级高于 ALLOW）

### 2.2 窗口类型

**A. 允许扫描窗（ALLOW，可扫白名单）**

| 类型 | 例子 | 表达（timeSpec.kind） |
|------|------|----------------------|
| A1 一次性绝对窗 | 2026-05-19 00:00–06:00 | `ONCE`（startAt/endAt，对齐 1.0.7 现有） |
| A2 每日周期窗 | 每天 00:00–06:00 | `DAILY`（dailyBands） |
| A3 每周周期窗 | 每周六日全天 | `WEEKLY`（weekdays + dailyBands） |

**B. 禁止扫描窗（DENY，禁扫黑名单，优先级高）**

| 类型 | 例子 | 备注 |
|------|------|------|
| B1 整日禁扫 | 春节/国庆/月结日全天禁扫 | 「哪天不能扫」 |
| B2 日期范围+固定时段禁扫 | 6/1–6/18 大促，每天 08:00–24:00 禁扫 | 「指定日期范围的固定时段不可扫描」 |
| B3 重大保障期整段禁扫 | 护网 9/1–9/15 全程禁扫 | 安全行业刚需 |
| B4 周期性禁扫 | 每周一 09:00–12:00 禁扫 | 业务高峰 |

**C. 扩展维度（P2/P3）**

| 维度 | 说明 | 期 |
|------|------|----|
| C1 资产/网段差异化 | 核心生产网仅凌晨扫，测试网 7×24 | P2 |
| C2 速率/并发窗口 | 窗内限并发/速率（白天低速、夜间全速） | P3 |
| C3 应急突破 | `ignoreScanWindow=true` + 审批留痕（1.0.7 已有） | P0（例外规则） |
| C4 时区绑定 | 窗口按机构本地时区解释 | P0（D-05） |

### 2.3 窗口策略数据结构（概念）

```
窗口策略（可绑到 全局 / 资产组 / 任务）:
  windowType:  ALLOW | DENY
  timeSpec:
    kind:       ONCE | DAILY | WEEKLY | DATE_RANGE
    startAt / endAt          (ONCE)
    dailyBands: [08:00-24:00]     (DAILY / DATE_RANGE)
    weekdays:  [SAT, SUN]         (WEEKLY)
    dateFrom / dateTo             (DATE_RANGE)
    timezone:  Asia/Shanghai
  priority:    DENY > ALLOW
  scope:       GLOBAL | ASSET_GROUP:{id} | TASK:{id}
  reason / operator             (审计)
```

**判定算法**：任务在时刻 T 可扫 ⇔ `∃ ALLOW 窗命中 T ∧ ∄ DENY 窗命中 T`。周期窗需先按 `timezone` 展开为当日绝对区间再比较。

> **内外分离（重要）**：上述 `windowType/timeSpec/kind/weekdays/priority/scope/timezone` 是**内部存储与裁决模型**，**不对接入方暴露**。对外 `GET /scan-windows/policy` 仅返回**投影后的净可用窗口列表** `availableWindows`（= ALLOW − DENY，展开为未来 N 天的绝对 UTC 区间），无 timezone / scope / allow-deny 结构。接入方只消费「什么时候能扫」，不理解平台策略规则。投影逻辑落在 `open-api-service` assembler + vul-pass `queryAvailableWindows(days)`。

---

## 3. 数据模型（DDL）

### 3.1 主任务表 `vul_scan_task` 扩展

| 列 | 类型 | 说明 |
|----|------|------|
| `tsk_stat` | int | 扩展枚举（见 §4） |
| `pause_reason` | varchar(48) | `SCAN_WINDOW_EXPIRED_REPORT_PENDING` / `NO_REMAINING_SCAN_WINDOW` / `MANUAL_PAUSE` |
| `current_window_id` | bigint | 当前生效窗口 |
| `scan_attempts` | int | 累计（重）下发扫描次数，默认 0（D-02） |

### 3.2 新增 `vul_scan_task_window`（任务级窗口实例）

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | bigint PK | |
| `tsk_id` | bigint | 关联任务 |
| `window_type` | varchar(8) | ALLOW / DENY |
| `start_at` | datetime | UTC 绝对区间起（周期窗展开后落地，或直接 ONCE） |
| `end_at` | datetime | UTC 绝对区间止 |
| `source` | varchar(16) | CREATE（下发带入）/ APPEND（追加）/ POLICY（策略展开） |
| `operator` | varchar(64) | 追加/变更操作人 |
| `reason` | varchar(255) | 审计 |
| `status` | varchar(16) | PENDING / ACTIVE / EXPIRED / CONSUMED |
| `create_time` | datetime | |

> 独立成表而非 JSON 列：支持追加、按 `start_at` 索引查「下一窗口」、单条窗口来源审计。

### 3.3 新增 `vul_scan_window_policy`（可复用窗口策略，P2）

存 §2.3 结构（含 DAILY/WEEKLY/DATE_RANGE + scope + timezone）；调度时展开为 `vul_scan_task_window` 的绝对区间。P0 可先只支持 ONCE（任务级），P2 再引入策略表与周期展开。

---

## 4. 状态机

### 4.1 内部枚举扩展（`VulScanTaskStatEnum`）

现有：0待处置/1已完成/2失败/3进行中/4预览/5待离线导入/6-8核验门闸。新增：

| 内部枚举（建议） | code | 对外（API 1.0.7） |
|------------------|------|-------------------|
| `PAUSED_WAITING_WINDOW` | 20 | `PAUSED_WAITING_SCAN_WINDOW` |
| `PAUSED_NO_WINDOW` | 21 | `PAUSED_NO_SCAN_WINDOW` |

> code 取 20/21 避开现有 0–8 及核验预留区间，防越界（参考 v1.4.1 §18.4 前端状态数组越界教训）。对外映射放 `open-api-service` assembler，禁止内部直接吐对外字符串。

### 4.2 状态跃迁

```
PENDING ──下发──► RUNNING
RUNNING ──超窗未回收报告 & 有下一窗口──► PAUSED_WAITING_WINDOW  (pauseReason=SCAN_WINDOW_EXPIRED_REPORT_PENDING)
RUNNING ──超窗未回收报告 & 无剩余窗口──► PAUSED_NO_WINDOW        (pauseReason=NO_REMAINING_SCAN_WINDOW)
RUNNING ──SOC 手动暂停──► PAUSED_*                              (pauseReason=MANUAL_PAUSE)
PAUSED_WAITING_WINDOW ──到达下一窗口(自动)──► RUNNING
PAUSED_* ──追加窗口 + start / start(ignoreScanWindow=true)──► RUNNING
RUNNING ──报告回收完成──► FINISHED
PAUSED_* / RUNNING ──scan_attempts ≥ maxScanAttempts──► FAILED (告警)
```

> 补 1.0.7 契约缺口（§9 瑕疵）：`PAUSED_NO_WINDOW` 可经 `maxScanAttempts` 或人工终止转 `FAILED`，避免僵尸任务。

---

## 5. 核心调度器（vul-pass 领域服务 `ScanWindowScheduler`）

窗口感知的报告回收调度器，定时轮询（建议每分钟）：

```
for 每个 RUNNING / PAUSED_WAITING_WINDOW 任务:
  now = UTC.now()

  ┌─ RUNNING 且 now > currentWindow.endAt 且 报告未回收:
  │    nextWindow = 查 start_at > now 的最近 ALLOW 窗（且未被 DENY 覆盖）
  │    if nextWindow != null:
  │        pause(内部) → PAUSED_WAITING_WINDOW, pauseReason=SCAN_WINDOW_EXPIRED_REPORT_PENDING
  │        发 Webhook TASK_PAUSED
  │    else:
  │        pause(内部) → PAUSED_NO_WINDOW, pauseReason=NO_REMAINING_SCAN_WINDOW
  │        发 Webhook TASK_PAUSED（带 manualOptions）
  │
  └─ PAUSED_WAITING_WINDOW 且 now ∈ nextWindow:
       start(内部, ignoreScanWindow=false) → RUNNING, 恢复报告轮询
```

**关键实现点**：

1. **幂等 + 并发**：`pause`/`start` 迁移用乐观锁 `update ... where tsk_stat=?`（或分布式锁），多实例调度不重复下发扫描器指令。
2. **续扫适配（D-01）**：`ScanEngineClient` 适配层封装 pause/continue 能力探测；扫描器不支持续扫时，`start` = **重新下发 + 任务台重绑**，`scan_attempts++`，对 Partner 黑盒。
3. **成本保护（D-02）**：每次重下发前校验 `scan_attempts < maxScanAttempts`，超限转 `FAILED` + 告警。
4. **报告轮询 guard**：现有 recycle 轮询加 `tsk_stat NOT IN (PAUSED_*)` 条件，暂停时停止回收。
5. **DENY 优先**：查下一窗口时排除被 DENY 覆盖的区间。

---

## 6. 对外接口（open-api-service，Feign→vul-pass）

全部薄控制器：校验 + 能力位鉴权后 Feign 到 vul-pass 领域服务。**不承载调度逻辑。**

| 端点 | vul-pass 领域方法 | 能力位 | 校验 |
|------|-------------------|--------|------|
| `POST /tasks/vul`（改） | 创建任务：**移除 `scanWindows` 入参**；响应补 `estimatedStartAt`/`matchedScanWindow`/`windowSource=POLICY` | `TASK_WRITE` | 创建时按策略匹配下一可扫窗口填 `estimatedStartAt`；无窗口则 null |
| `POST /tasks/{id}/scan-windows` | `appendScanWindow()` | `TASK_WINDOW_WRITE` | 窗口合法（startAt<endAt 且 startAt>now，无重叠）否则 40006；任务已完成 40002 |
| `POST /tasks/{id}/pause` | `pauseTask(MANUAL_PAUSE)` | `TASK_CONTROL` | 仅 RUNNING 可暂停 |
| `POST /tasks/{id}/start` | `startTask(ignoreScanWindow)` | `TASK_CONTROL` | 仅 PAUSED_*；ignoreScanWindow=false 且非窗口期 → 40002 |
| `GET /tasks/{id}` | 补 `status`/`pauseReason`/`currentScanWindow`/`nextScanWindow`/`manualOptions` | 读 | assembler 做内→外状态映射 |
| **`GET /scan-windows/policy`**（新增，D-03） | `queryAvailableWindows(days)` | 读 | 返回**投影后净可用窗口列表** `availableWindows`（ALLOW−DENY 展开，绝对 UTC），无 timezone/scope；接入方只读 |

**幂等**：`pause`/`start` 支持 `Idempotency-Key`；对已处于目标态的重复调用返回当前态（幂等成功，不报错）——补 1.0.7 未定义的幂等语义（§9 瑕疵）。

---

## 7. Webhook

| 事件 | 触发 | payload 关键字段 |
|------|------|------------------|
| `TASK_PAUSED`（1.0.7 §6.2/§6.7） | 迁移到 `PAUSED_*` | `status`、`pauseReason`、`currentScanWindow`、`nextScanWindow`、`manualOptions` |
| **`SCAN_WINDOW_CHANGED`**（新增，D-03） | 窗口策略追加/变更 | `taskId`（或 scope）、`windows`、`operator`、`reason` |

复用现有 Webhook 投递链路（`open-api-export-webhook-PRD.md` 的 deliver/重试/`webhook_delivery_log`；投递已迁 eventplus，见 partner_webhook_config 迁移）。

---

## 8. 审计

追加窗口 / pause / start / `ignoreScanWindow` 突破 均属人工介入，按 1.0.7 §11 记录 `operator` / `reason` / `time` / `remark`（突破窗口时必填沟通说明），落 `vul_scan_task_window` 或独立操作审计表。

---

## 9. 风险与 1.0.7 契约缺口（评审意见）

| # | 缺口 | 风险 | 本 PRD 处置 |
|---|------|------|-------------|
| G1 | 续扫语义未定义 | 扫描器不支持续扫时 start=全量重扫 | D-01 重下发+重绑，适配层封装（已消解） |
| G2 | 窗口<单次耗时的死循环 | 超窗→重下→再超窗僵尸任务 | D-02 `maxScanAttempts` 转 FAILED |
| G3 | 时区约定 | UTC/本地混用致白天误扫 | D-05 UTC 存储 + timezone 解释 |
| G4 | 无周期窗表达 | 一次性列表需反复追加 | §3.3 策略表 DAILY/WEEKLY（P2） |
| 瑕疵1 | 状态机不闭环 | PAUSED_NO_WINDOW→FAILED 未定义 | §4.2 补齐 |
| 瑕疵2 | manualOptions 命名映射不一致 | ADD_SCAN_WINDOW vs scan-windows | assembler 给对照 |
| 瑕疵3 | pause/start 幂等未定义 | 重复调用语义不明 | §6 幂等成功语义 |
| 新增缺口 | 缺平台→接入方窗口同步通道 | 线下分发不一致 | D-03 GET 策略 + Webhook |
| 窗口入参 | 创建任务不接收 `scanWindows` 入参 | 接入方维护第二份窗口易不一致 | **D-07：创建响应回传 `estimatedStartAt`；由 `GET /scan-windows/policy` 只读、`SCAN_WINDOW_CHANGED` Webhook 同步**（已对齐对外 API 文档 §5.1.8/§6.2） |

**接入前必须与扫描器厂商 + SOC 对齐的两个问题**：G1（续扫能力）、G3（时区）。

---

## 10. 实施分期

| 期 | 内容 |
|----|------|
| **P0** | §3.1/3.2 DDL（任务级 ONCE 窗）+ §4 状态枚举 + 内外映射 + §6 四个对外接口（手动 pause/start/追窗/GET）+ §8 审计 |
| **P1** | §5 `ScanWindowScheduler`（超窗自动暂停 + 到窗自动恢复）+ §7 `TASK_PAUSED` Webhook |
| **P2** | §3.3 策略表 + DAILY/WEEKLY/DATE_RANGE 周期展开 + DENY 窗 + C1 资产差异化 + `SCAN_WINDOW_CHANGED` + GET 策略 |
| **P3** | C2 速率/并发窗 + G4 RRULE + 续扫真实适配（若厂商支持） |

---

## 11. 与既有约束的一致性

- **CLAUDE.md**：调度/暂停业务落 `vul-pass`；`open-api-service` 仅对外薄层 + Feign，不改修复核验编排。
- **java-hard-ban**：状态码常量化（枚举），无魔法值；对外状态字符串不散落。
- **test-required-strict**：每个 P0/P1 领域方法需可运行回归测试（窗口判定算法、状态迁移幂等、调度器边界）。
- **文档先行**：本 PRD 为后续开发唯一依据；新增缺陷/变更须回写本文件版本记录。

---

## 12. 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-16 | 首版：ALLOW/DENY 窗口模型、DDL、状态机、`ScanWindowScheduler`、对外接口、同步通道、1.0.7 契约缺口评审 |
| v1.1 | 2026-07-16 | D-07：创建任务不含 `scanWindows` 入参、响应加 `estimatedStartAt`；对外新增 `GET /scan-windows/policy`（返回投影后可用窗口列表）、`SCAN_WINDOW_CHANGED` Webhook |
