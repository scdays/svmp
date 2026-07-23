# 修复核验全链路 — Wave L 流程实例持久化 开发计划 v1.0

> **状态**：已同意执行并落地（2026-07-17）  
> **日期**：2026-07-17  
> **前置**：Wave G 主链路推导（`TaskLifecycleResolver`，**不落库**）；`wave` 全阶段预留；核验子任务编排已落地  
> **分支**：继续 `feature/fix-ledger-log-records`（或按规范从 `developer` 切 `feature/task-flow-instance`）

---

## 0. 已确认口径（2026-07-17）

### 0.1 全阶段主链路 + 互斥子链

```text
任务预检 → 任务下发 → [阶段子任务链] → 结果回收 → 稽核完成 → 任务结束
```

展示名：**任务预检**（非「任务分配」）。括号内按 `tskPhase` **互斥选一支**（`|`），支内用 `→` 顺序：

| tskPhase | 阶段子任务链 |
|----------|----------------|
| 0 潜在预警 | 关联分析 |
| 1 排查 | 漏洞扫描 |
| 2 验证 | 漏洞扫描 → 二次扫描 |
| 3 修复 | 漏洞修复 |
| 4 核验 | 连通性检测 → 修复核验 |

### 0.2 表职责 / 范式

| 数据 | 权威落点 |
|------|----------|
| 当前节点、节点状态、执行时间线 | **`vul_task_proc_inst` / `vul_task_proc_node`（从表）** |
| 编排阶段码（原 sub.wave 语义） | **节点表 `node_code`（CHAIN）为权威** |
| 扫描执行（设备/资产/报告/进度） | `vul_scan_task_sub` |
| `sub.wave` / `depend_gate_id` | 过渡期可保留作热路径冗余；避免与节点表双写冲突，读展示优先节点表 |

---

## 1. 背景与目标

当前工作台步骤条（任务预检 → 下发 → 连通性检测 → 修复核验 → …）由 **`TaskLifecycleResolver` 运行时推导**，刷新依赖主/子任务状态，**无真实执行履历**。

既有「任务编排」（阶段子任务链），就应有 **流程实例**：

1. 记录真实执行轨迹（何时进入/离开某节点）  
2. 持久化**当前节点**与**各节点状态**  
3. 与 **全阶段** `tskPhase` 绑定（上表 0.1），模板可扩展  

**目标一句话**：主任务 1:1 流程实例 + 节点实例表；关键状态变迁写库；步骤条优先读库，推导作兼容兜底。

---

## 2. 与现有模型关系

| 现有 | 角色 | Wave L 关系 |
|------|------|-------------|
| `vul_scan_task` | 主任务 | 流程实例绑定 `tsk_id`（1:1） |
| `vul_scan_task_sub` | 执行面 | 链节点经 `sub_tsk_id` 关联；不承载流程履历 |
| `vul_scan_task_sub.wave` | 历史编排字段 | 过渡冗余；**权威迁至 `proc_node.node_code`** |
| `TaskLifecycleResolver` | 展示推导（不落库） | **保留作兜底**；有实例则读库 |
| `PhaseSubTaskChainTemplate` | 阶段→子任务链模板 | 升级为流程定义来源（对齐 §0.1） |
| `TaskLifecycleStep` | 主链路步骤码 | 节点 `node_code`（MAIN）对齐 |

```text
主链路（固定骨架）
  ASSIGN_PRECHECK → DISPATCHED → [阶段子任务链展开] → RECYCLE → AUDIT_DONE → FINISHED

阶段子任务链（按 tskPhase 互斥，见 §0.1）
```

---

## 3. 数据模型（定稿草案）

### 3.1 流程实例 `vul_task_proc_inst`

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | BIGINT PK | 实例 ID |
| `tsk_id` | BIGINT UK | 主任务 ID（1:1） |
| `order_id` | VARCHAR | 冗余工单 |
| `tsk_phase` | VARCHAR/TINYINT | 业务阶段，绑定模板 |
| `def_code` | VARCHAR(64) | 流程定义码，如 `PHASE_4_VERIFY_FIX` |
| `current_node_code` | VARCHAR(64) | 当前节点 |
| `status` | TINYINT | 0 进行中 / 1 成功结束 / 2 失败结束 / 3 取消 |
| `started_at` / `ended_at` | DATETIME | |
| `create_time` / `update_time` | DATETIME | |

### 3.2 节点实例 `vul_task_proc_node`

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | BIGINT PK | |
| `inst_id` | BIGINT | 流程实例 |
| `tsk_id` | BIGINT | 冗余主任务，便于按任务查 |
| `node_code` | VARCHAR(64) | `ASSIGN_PRECHECK` / `DISPATCHED` / `CONNECTIVITY_CHECK` / … |
| `node_kind` | VARCHAR(16) | `MAIN` 主链路骨架 / `CHAIN` 阶段子任务链 |
| `seq` | INT | 展示顺序（与步骤条一致） |
| `status` | TINYINT | 0 待执行 / 1 进行中 / 2 成功 / 3 失败 / 4 跳过 |
| `sub_tsk_id` | BIGINT NULL | 链节点关联子任务（可空；主骨架节点为空） |
| `started_at` / `ended_at` | DATETIME NULL | |
| `message` | VARCHAR(512) NULL | 失败/跳过原因 |
| `extra_json` | TEXT NULL | 扩展（如 confirmToken、批次号） |
| `create_time` / `update_time` | DATETIME | |

**唯一约束**：`(inst_id, node_code)` 或 `(inst_id, seq)`。

### 3.3 流程定义（本期）

- **默认代码注册表**（扩展 `PhaseSubTaskChainTemplate`）：按 `tskPhase` 生成节点清单。  
- **不强制**再建 `vul_task_proc_def` 表（P1 可选）；先保证实例可落、可查。

---

## 4. 状态机与写库时机

| 事件 | 实例动作 |
|------|----------|
| `preDispatch` 成功（核验预览） | 创建实例；节点初始化为待执行；当前=`ASSIGN_PRECHECK`；预检节点→进行中/成功 |
| `dispatch` 成功 | 下发节点成功；展开链节点；当前进入首个 CHAIN 节点（核验=连通性检测）；绑定已落库 `sub_tsk_id` |
| 连通性子任务终态 / spawn 修复核验 | 连通性节点成功；当前→修复核验；绑定新子任务 |
| 链内全部终态 | 链节点收口；当前→`RECYCLE` |
| `recycle` 成功 | 回收节点成功；当前→`AUDIT_DONE`（或待稽核口径与 Wave G 一致） |
| `submit`/稽核完成 | 稽核节点成功；当前→`FINISHED`；实例 status=结束 |
| 失败路径 | 对应节点 status=失败；实例可标记失败（可配置是否阻断） |

**原则**：写库与业务事务同边界（dispatch/recycle/submit）；禁止仅前端改节点状态。

---

## 5. 读路径（步骤条）

```text
IF 存在 vul_task_proc_inst(tsk_id)
  → 按 seq 读 vul_task_proc_node 组装 lifecycleSteps + currentStepCode
ELSE
  → TaskLifecycleResolver 推导（兼容历史任务）
```

DTO 仍用现有 `lifecycleStep` / `lifecycleSteps` / `currentStepCode`，前端**尽量无改**。

---

## 6. 验收标准

- [x] Liquibase 建 `vul_task_proc_inst` / `vul_task_proc_node`
- [x] 核验任务：下发后建实例；当前节点=连通性检测；链节点可绑定 `sub_tsk_id`（单测覆盖）
- [x] sequential 派生修复核验后：连通性成功、当前=修复核验（`onSpawnRepairVerify`）
- [x] 回收/提交后节点推进到稽核/结束（`onRecycleDone` / `onSubmitDone`）
- [x] 无实例的老任务仍走 Resolver 兜底（`enrichLifecycle`）
- [x] 模板覆盖全 `tskPhase`（`TaskFlowDefRegistry`）；写库推进以核验为主，其它阶段下发亦建实例
- [x] 单测：`TaskFlowInstanceServiceTest` 绿

**口径说明（ponytail）**：`preDispatch` 无持久化 `tskId`，流程实例在 **`dispatch` 成功** 时创建；预检节点在下发时记为已成功（confirmToken 路径等价预检通过）。前端步骤条仍消费原 DTO，本期无 Vue 改动。

## 7. 不改什么

- 不推倒 `wave` / confirmToken / 台账 9+10 / Wave K 外壳内层口径  
- 不引入 Camunda/Flowable 等重型引擎（自研轻量表即可）  
- 不改 `open-api-service`  
- 本期不要求运营可视化流程设计器  

---

## 8. 任务矩阵

| Wave | Agent | 改什么 | 交付物 |
|------|-------|--------|--------|
| **L-0** | 文档 | PRD § 流程实例 + 本计划定稿 | docs |
| **L-1** | 后端-模型 | Liquibase + PO/DO/Repository + 定义注册表扩展 | Java + groovy |
| **L-2** | 后端-运行时 | `TaskFlowInstanceService`：create/advance/bindSub；挂 preDispatch/dispatch/recycle/spawn/submit | Java + 单测 |
| **L-3** | 后端-读路径 | `enrichLifecycle` 优先读实例 | Java + 单测 |
| **L-4** | 前端 | 步骤条仍消费 DTO；必要时展示节点失败 tip | Vue（小改） |
| **L-5** | Review | 验收 + 严格审查 | 摘要 |

**预计并行**：L-1 完成后 L-2∥L-4；L-3 依赖 L-2。

---

## 9. 分支与规范

| 项 | 值 |
|----|-----|
| 分支 | `feature/fix-ledger-log-records`（同功能线）或新切 `feature/task-flow-instance` |
| 规范 | `esmp-rd-standards`；Commit `[ADD]`/`[IMP]` |
| Skills | `esmp-backend-dev`、`esmp-frontend-dev`、`esmp-code-review-strict` |
| Rules | `java-hard-ban`、`backend-layer-boundary-strict`、`test-required-strict`、`security-hard-ban` |

---

## 10. 风险

| 风险 | 缓解 |
|------|------|
| 与 Resolver 双源不一致 | 有实例只信库；无实例才推导；禁止双写两套规则 |
| 历史任务无实例 | 兜底推导；可选后台批补（不做本期） |
| 节点与子任务多对一 | 链节点按 wave 聚合；多子任务同 wave 取最差/最新策略写清 |
| 事务膨胀 | 节点更新与业务同事务；禁止异步乱序改状态 |

---

**落地摘要（2026-07-17）**：`TaskFlowInstanceService` 挂在 `dispatch` / sequential spawn / `recycle` / `submit`；`enrichLifecycle` 优先读库。
