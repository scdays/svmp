# 自动化处置 — DDD 状态外置（Redis）+ 全阶段编排 开发计划 v1.2

> **状态**：已同意执行并完成主路径落地（2026-07-17）  
> **验收摘要**：Redis Repository + Lock；Orchestrator 外置状态；`advance`/`advanceOne`；统一导入去大事务+FileStore+异步；全阶段 wave 解析；单测与 lint 通过  
> **日期**：2026-07-17  
> **工程**：`project_backend/svmp/vul-pass` + `project_frontend/asset/asset-newleak-manage`  
> **分支**：继续 `feature/fix-ledger-log-records`  
> **本期范围**：  
> - **状态外置：只做 Redis**（不做 DB 表；单测可用内存实现，生产默认 Redis）  
> - **其他全做**：Domain 重构、`advanceOne`、异步推进、去大事务、FileStore、分布式锁、**全阶段（tskPhase 0～4）**、前端适配  
> **约束**：ponytail；DDD 分层；不在 App 堆 Redis/状态机；不上 BPM

---

## 0. 目标与口径

### 0.1 目标一句话

自动化处置升级为 Domain 编排能力：预览/执行共用排队、**Redis 持久化会话**、全阶段子任务链可推进，并具备异步、事务边界、互斥与报告续跑。

### 0.2 本期 / 明确不做（状态存储）

| | 本期 | 不做（后续可评估） |
|--|------|-------------------|
| 状态外置 | **仅 Redis**（`I…RunRepository` Redis 实现） | DB 表 + DDD 全套实体 |
| 单测 | 允许内存 Repository 实现，**不作为生产配置主推** | — |
| 编排能力 | Domain / Strategy / advanceOne / 锁 / 异步 / FileStore / **全阶段** / 前端 | BPM、重写 recycle 内核 |

### 0.3 「全阶段」定义

| tskPhase | 阶段子任务链 | 本期 |
|----------|--------------|------|
| 0 潜在预警 | 关联分析 | preview + 可推进（端口不足则提示单条处置） |
| 1 排查 | 漏洞扫描 | 同上 |
| 2 验证 | 漏洞扫描 → 二次扫描 | 顺序推进 |
| 3 修复 | 漏洞修复 | 同上 |
| 4 核验 | 连通性检测 → 修复核验 | 对齐 Wave J，不回归 |

权威：DB 子任务 / 流程节点；编排 run 为 Redis 上的进度投影。

### 0.4 设计模式

| 能力 | 手法 |
|------|------|
| 预览 = 执行排队 | 共享 `buildQueue` |
| online / offline | AdvanceStrategy |
| 阶段推进 | Domain private 步骤 / 按 wave |
| 存储 | **仅 Redis Repository**（接口可换，本期只交 Redis） |
| 文件 / 锁 | FileStore、Lock 端口，Redis 锁实现 |

---

## 1. 分层

```text
Ui → App（用例/事务/异步/wsLoginName）
   → DomainService（preview/start/advanceOne/notify/buildQueue 全阶段）
        → AdvanceStrategy
        → IVerifyFixAutoDisposeRunRepository  → Redis 实现（本期唯一生产实现）
        → IAutoDisposeReportFileStore
        → IAutoDisposeLock → Redis
        → RecyclePort
   → SilentPush（仅推送）
```

---

## 2. 验收标准

- [ ] preview/start 共用 `buildQueue`（含全阶段映射）；start 写入 **Redis**
- [ ] 生产路径无 JVM Map 作为唯一状态源；无 DB 编排表
- [ ] `advanceOne` + 异步；unified-import 无大事务；FileStore 可续跑
- [ ] Redis 分布式锁（tskId/runId）
- [ ] tskPhase 0～4 均可 preview；核验回归不破；非核验能推进或明确降级提示
- [ ] 前端适配异步 import + 全阶段文案
- [ ] 编译/单测/lint + 分层 Review 通过

---

## 3. 不改什么

- 不做编排状态 **DB 表**
- 不改 `open-api-service`、Partner、recycle 内核、不上 BPM
- 未要求不 commit / push

---

## 4. Wave 任务拆分

| Wave | Agent | 改什么 | 交付物 |
|------|-------|--------|--------|
| **W1** | 后端-Domain | DomainService；buildQueue（全阶段扩展）；Strategy；advanceOne；拆分推进步骤 | Domain API + 单测 |
| **W2** | 后端-Infra | **Redis** RunRepository + Lock + TTL + 配置（默认 redis） | Redis 外置可用 |
| **W3** | 后端-App | 去大事务；FileStore；异步；App 瘦身 | 可中断续跑 |
| **W4** | 后端-全阶段 | `PhaseSubTaskChainTemplate` 对齐；非核验端口/降级 | 0～4 preview/推进 |
| **W5** | 前端 | 异步 import；全阶段文案 | Drawer |
| **W6** | Review | 验收清单 | 报告 |

**并行**：W1 后 W2∥W4；W3 依赖 W1+W2；W5 依赖 W3；W6 最后。

---

## 5. 接口契约

| 接口 | 变化 |
|------|------|
| preview | queue 可含全阶段 wave |
| start | 异步推进（可配置兼容同步） |
| GET runId?snapshot= | 从 Redis 读 |
| unified-import | 落盘 + 投递；快返回 |
| active | 从 Redis 读 active |

---

## 6. Redis 与配置

| 项 | 说明 |
|----|------|
| key | `auto-dispose:run:{runId}`、`auto-dispose:active:{tskId}`、`auto-dispose:lock:*` |
| 文件 | `auto-dispose/report/{runId}/{batchId}` |
| 配置 | `vul.auto-dispose.store=redis`（本期生产只认 redis）；`async-enabled` |
| TTL | run 24h；文件 72h |

---

## 7. 分支与规范

- **分支**：`feature/fix-ledger-log-records`
- **Commit**：`[REF]`/`[ADD]`/`[FIX]`；UTF-8 无 BOM
- **Skills / Rules**：同 v1.0（backend/frontend/rd-standards/ponytail/分层/测试/安全）

---

## 8. 风险

| 风险 | 缓解 |
|------|------|
| 异步回归 | 开关 + 核验用例先绿 |
| 非核验 recycle 不足 | 降级单条处置 + 明确 message |
| 文件多实例 | 共享存储 |

---

## 9. 同意后顺序

W1 Domain → W2 Redis → W3 异步/文件 → W4 全阶段 → W5 前端 → W6 Review
