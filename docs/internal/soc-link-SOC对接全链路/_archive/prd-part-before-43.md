# vuln-task-center 扫描治理中心 — 产品需求文档（PRD）

> **用途**：Multi-Agent 自动化开发的**上游输入**。将 `vuln-task-center` 从「任务下发通道」升级为「扫描资源与任务治理中心」。  
> **状态**：`草稿`  
> **关联落地方案**（待拆分）：`vuln-task-center-扫描治理中心-落地方案.md`（PRD 评审通过后产出）

| 属性 | 值 |
|------|-----|
| 功能编号 | **VTC-GOV-P0** ~ **VTC-GOV-P4** |
| 模块名称 | 扫描治理中心（Scanner Governance Center） |
| 主服务 | `vuln-task-center`（port 18087） |
| 关联服务 | `vul-pass`（计划/工单下发）、`vuln-model`（漏洞库）、`open-api-service`（Partner 任务，P4） |
| 参考规范 | 绿盟：`svmp/docs/standards/绿盟远程安全评估系统API接口文档V6.0.8-20230403.doc`；安恒：`svmp/docs/standards/扫描器/明鉴漏洞扫描系统API手册V5.0-20230801.docx` |
| 目标阶段 | P0（LM 核心抽象+对账）→ P1（AH 适配+操控）→ P4（开放与观测） |

---

## 1. Why — 背景与目标

### 1.1 背景

`vuln-task-center` 当前承担 SVMP **扫描任务调度**角色，已具备：

- 多厂商下发（绿盟 LM、安恒 AH、启明 QM、天融信 TRX、Nessus、安智 AZ、加特林 JTL）
- 三层 Redis 队列（send / wait / execute）+ 简单负载均衡
- Kafka + tools-scheduler / SOAR 双通道
- 绿盟侧部分同步（`sys_status`、`active_list`、弱口令/基线模板）
- 安恒侧部分同步（`MsgSendAH` module 0/5/8 下发、`VulnTaskListenerAH` vulId 增量拉取）
- 2026 年新增的 `scan_sub_task` 子任务模型

**痛点：**

| 痛点 | 表现 |
|------|------|
| 能力单一 | 以「下发 + 收结果」为主，缺设备深度治理 |
| 厂商耦合 | `MsgSendLM/AH/...` 硬编码，接入新扫描器需改代码 |
| 执行态双轨 | `scan_sub_task` 与 ES `vuln_scan_node_execute` 并存，非统一真相源 |
| 对账缺失 | 平台下发超时、绕行任务、状态漂移无法系统化发现 |
| 监控分散 | 节点 cpu/disk/memory 仅 LM 定时回写，无统一 API 与告警 |
| 模板/能力未标准化 | LM 基线/弱口令较全，AH 策略/字典未纳入能力注册表 |

**厂商 API 参考：**

- **绿盟 RSAS V6.0.8**：任务 CRUD、active_list、system.status、模板/字典等 → **P0 首个 Capability Profile（LM）**
- **安恒明鉴 DAS-RAS V5.0**（API 手册 2023-08-01，文档版本 04）：Token 认证、create→start 两阶段下发、task/list/V2 对账、system.resource 监控、policy/dict 同步 → **P1 第二个 Capability Profile（AH）**

### 1.2 目标

将 `vuln-task-center` 演进为三层能力模型：

```text
┌─────────────────────────────────────────────────────────────┐
│  平台层：vul-pass / open-api-service（计划、工单、Partner）   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  vuln-task-center · 扫描治理中心                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 设备治理层   │  │ 调度编排层   │  │ 厂商适配层 (Plugin)  │  │
│  │ Registry    │  │ Router/LB   │  │ ScannerAdapter-LM   │  │
│  │ Metrics     │  │ Reconcile   │  │ ScannerAdapter-AH   │  │
│  │ Template    │  │ SubTask     │  │ ...                 │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    物理/逻辑扫描器（RSAS / DAS-RAS 等）
```

**核心目标：**

1. **设备深度管理**：负载均衡、性能监控、任务对账、模板/漏洞能力同步
2. **API 集中管理**：能力注册表 + `ScannerAdapter` 插件化接入
3. **任务全生命周期**：筛选可用扫描器、参数详情、子任务监控、异常恢复

### 1.3 成功标准（可衡量）

| 指标 | 标准 | 阶段 |
|------|------|------|
| 对账覆盖率（LM） | 绿盟节点 100% 可触发对账，ORPHAN/MISSING/DRIFT 可查询 | P0 |
| 对账覆盖率（AH） | 安恒节点可通过对账 REST 查询差异（task.list.v2 + getTaskStatus） | P1 |
| 执行态统一 | 新下发任务以 `scan_sub_task` 为唯一执行真相源，ES 仅作查询索引 | P0 |
| 监控 API | 任意节点可通过 REST 获取 cpu/memory/disk/task_running | P1 |
| 下发前预览 | 给定 taskType + IP + templateId，返回可用节点列表及不可选原因 | P1 |
| 任务操控（LM） | 绿盟子任务支持 pause/resume/retry/sync-status API | P1 |
| 任务操控（AH） | 安恒子任务支持 suspend/start/stop/sync-status（create 后需 start） | P1 |
| LM 适配器 | 绿盟能力 ≥80% 经 `ScannerAdapter-LM` 实现，不再新增 `MsgSendLM` 逻辑 | P0 |
| AH 适配器 | 安恒核心能力经 `ScannerAdapter-AH` 实现（create+start、对账、resource） | P1 |
| 模板同步（LM） | 绿盟 sysvuln/webvuln/baseline 模板可手动/定时同步并缓存 | P2 |
| 模板/策略同步（AH） | 安恒 policy.get / getPolicyTemplates、dict.list 可同步并缓存 | P2 |
| 开放对接 | open-api-service 任务下发可走治理中心路由（可选节点策略） | P4 |

### 1.4 不做边界

- **不重写** tools-scheduler / SOAR 引擎本身，仅抽象调用面
- **不替换** vul-pass 工单流程与 vuln-model 漏洞库主数据
- **P0–P2 不做** 完整前端大屏（可先 REST + 现有管理页扩展）
- **不一次性** 迁移全部 9 家厂商：**P0 仅 LM 完整适配**；**P1 扩展 AH（明鉴 V5.0）** 对账/监控/操控；QM/TRX 等保持现有 `MsgSend*` 通道
- **不做** 扫描器固件升级、VPN 组网等设备运维
- **不做** 省份定制 endpoint 收敛（独立 P 后续治理）

---

## 2. Who — 角色与用户

| 角色 | 说明 | 核心操作 |
|------|------|----------|
| 安全运营 | 日常扫描计划管理 | 查看节点负载、对账差异、暂停/恢复子任务 |
| 平台管理员 | 扫描器接入与配置 | 注册节点、同步模板/字典、配置能力、健康检查 |
| vul-pass 系统 | 上游业务 | 下发扫描计划、查询任务状态（Feign 不变或增强） |
| open-api Partner | 外部调用方（P4） | 通过 open-api 间接使用节点筛选与任务查询 |
| 审计/合规 | 监管场景 | 查看设备审计日志、绕行任务、下发参数快照 |

---

## 3. What — 功能范围

### 3.1 用户故事（按优先级）

#### 设备治理

| ID | 作为… | 我希望… | 以便… | 阶段 |
|----|-------|---------|-------|------|
| US-D01 | 平台管理员 | 查看扫描器实时 CPU/内存/磁盘/并发任务数 | 判断节点是否可接新任务 | P1 |
| US-D02 | 平台管理员 | 主动触发节点健康检查 | 发现认证失效、API 不可达 | P1 |
| US-D03 | 平台管理员 | 查看节点已注册 API 能力及最后验证时间 | 接入新厂商时有清单可依 | P0 |
| US-D04 | 平台管理员 | 同步绿盟漏洞/Web/基线模板到平台缓存 | 下发前校验 template_id 有效 | P2 |
| US-D05 | 平台管理员 | 同步弱口令/策略字典（LM userpwd、AH dict.list） | 与平台字典映射一致 | P2 |
| US-D06 | 安全运营 | 查看节点插件库版本、漏洞库版本 | 评估扫描能力覆盖 | P1 |

#### 任务对账

| ID | 作为… | 我希望… | 以便… | 阶段 |
|----|-------|---------|-------|------|
| US-R01 | 安全运营 | 对比平台子任务与扫描器活跃任务列表 | 发现绕行/遗留任务 | P0/P1 |
| US-R02 | 安全运营 | 平台有、设备无的任务标记为 MISSING | 下发超时后确认是否失败 | P0/P1 |
| US-R03 | 安全运营 | 状态/进度不一致标记为 DRIFT 并支持 sync-status | 网络波动后恢复一致 | P0/P1 |
| US-R04 | 安全运营 | 对 ORPHAN 任务执行忽略/终止/纳管 | 清理非平台任务 | P1 |
| US-R05 | 安全运营 | 定时自动对账（可配置间隔） | 无需人工巡检 | P1 |

> LM 对账源：`active_list`（P0）；AH 对账源：`task/list/V2` state∈{1,2,3}（P1）。

#### 任务调度与操控

| ID | 作为… | 我希望… | 以便… | 阶段 |
|----|-------|---------|-------|------|
| US-T01 | vul-pass | 下发前预览可用扫描器及评分原因 | 自动或手动选择节点 | P1 |
| US-T02 | 安全运营 | 查看 survey 下所有 subTask 及完整下发参数 | 排查参数问题 | P0 |
| US-T03 | 安全运营 | 对单个子任务 pause/resume/retry/cancel | 异常中断后继续 | P1 |
| US-T04 | 安全运营 | 大任务按 IP 上限自动拆分子任务 | 不超扫描器单次限制 | P0（增强现有） |
| US-T05 | 安全运营 | 下发前凭据/连通性预检 | 降低失败率 | P2 |

> LM：`auth.login_verify`；AH：`asset/checkConnection`（P2）。

#### API 集中管理

| ID | 作为… | 我希望… | 以便… | 阶段 |
|----|-------|---------|-------|------|
| US-A01 | 平台管理员 | 在能力注册表维护厂商 API 定义 | 新厂商按 Profile 接入 | P0 |
| US-A02 | 调度引擎 | 按任务 requiredCapabilities 过滤节点 | 不支持 web 的节点不接 web 任务 | P1 |
| US-A03 | 研发 | 新厂商仅实现 ScannerAdapter + 配置 | 不改 QueueAppServiceImpl 主流程 | P0 |

### 3.2 分期功能矩阵

| 能力域 | P0 | P1 | P2 | P3 | P4 |
|--------|----|----|----|----|-----|
| ScannerAdapter 抽象 + LM 实现 | ✅ | | | | |
| ScannerAdapter-AH 实现（明鉴 V5.0） | | ✅ | | | |
| 能力注册表（DB + 种子 LM + AH） | ✅ | 扩展 | | | |
| scan_sub_task 真相源 | ✅ | | | | |
| 任务对账（LM active_list） | ✅ | | | | |
| 任务对账（AH task.list.v2） | | ✅ | | | |
| 节点 metrics API | | ✅ | | | |
| preview-scanners | | ✅ | | | |
| 子任务操控 API（LM/AH） | | ✅ | | | |
| 模板/字典同步（LM + AH policy/dict） | | | ✅ | | |
| 登录/连通性预检 | | | ✅ | | |
| 负载策略增强（亲和/QoS） | | | | ✅ | |
| Prometheus/告警 | | | | ✅ | |
| open-api 对接 | | | | | ✅ |

### 3.3 页面 / 接口清单

#### 3.3.1 新增 REST API（vuln-task-center）

**设备治理**

| 方法 | 路径 | 说明 | 阶段 |
|------|------|------|------|
| GET | `/v1/scanner/node/{nodeId}/metrics` | 实时指标（LM system.status / AH system.resource） | P1 |
| GET | `/v1/scanner/node/{nodeId}/metrics/history` | 历史趋势 | P3 |
| POST | `/v1/scanner/node/{nodeId}/health/check` | 主动探活（含 AH token 校验） | P1 |
| GET | `/v1/scanner/dashboard` | 集群概览 | P1 |
| GET | `/v1/scanner/capability/catalog` | 能力目录（LM + AH Profile） | P0 |
| GET | `/v1/scanner/node/{nodeId}/capabilities` | 节点已启用能力 | P0 |
| POST | `/v1/scanner/node/{nodeId}/capabilities/verify` | 验证能力可用 | P1 |
| GET | `/v1/scanner/node/{nodeId}/templates` | 模板列表（按 type / vendor） | P2 |
| POST | `/v1/scanner/node/{nodeId}/templates/sync` | 触发模板/策略同步 | P2 |

**任务对账**

| 方法 | 路径 | 说明 | 阶段 |
|------|------|------|------|
| GET | `/v1/reconcile/tasks` | 对账结果查询（nodeId/surveyId/vendor） | P0 |
| POST | `/v1/reconcile/tasks/trigger` | 主动触发对账（按节点 Adapter） | P0 |
| GET | `/v1/reconcile/tasks/diff` | 差异报告详情 | P0 |
| POST | `/v1/reconcile/tasks/orphan/handle` | 绕行任务：IGNORE/STOP/ADOPT | P1 |

**任务调度与操控**

| 方法 | 路径 | 说明 | 阶段 |
|------|------|------|------|
| POST | `/v1/scan/task/preview-scanners` | 下发前可用节点预览 | P1 |
| GET | `/v1/scan/task/{surveyId}/dispatch-detail` | 下发参数详情（平台+适配器+subTasks） | P0 |
| GET | `/v1/scan/task/{surveyId}/sub-tasks/summary` | 子任务聚合进度 | P0 |
| POST | `/v1/scan/sub-task/{id}/pause` | 暂停（LM pause / AH suspend） | P1 |
| POST | `/v1/scan/sub-task/{id}/resume` | 继续（LM resume / AH start） | P1 |
| POST | `/v1/scan/sub-task/{id}/retry` | 重试下发（AH 需 create+start） | P1 |
| POST | `/v1/scan/sub-task/{id}/cancel` | 取消（LM stop / AH stop） | P1 |
| POST | `/v1/scan/sub-task/{id}/sync-status` | 主动拉取设备状态 | P0 |

#### 3.3.2 保留并增强的现有 API

| 路径 | 增强点 | 阶段 |
|------|--------|------|
| `/v1/scan/node` | 增加 health_status、supported_capabilities、last_heartbeat_at | P0 |
| `/v1/scanner` | 与能力注册联动 | P0 |
| `/v1/scan/sub/task` | 标准化 sendParamsInfo、关联 reconcile 状态 | P0 |
| `/v1/queue` | 展示与 reconcile 联动 | P1 |

#### 3.3.3 前端（可选，按阶段）

| 页面 | 说明 | 阶段 |
|------|------|------|
| 扫描器仪表盘 | 节点负载、健康、队列深度 | P1 |
| 任务对账页 | 差异列表、ORPHAN 处理（LM/AH） | P1 |
| 子任务详情抽屉 | 下发参数、操控按钮 | P1 |
| 能力注册管理 | 厂商 Profile（LM + AH）只读展示 | P2 |

> 前端工程建议：`asset-other-manage` 或新建子模块，P0 可仅后端 API + Postman/Swagger 验收。

### 3.4 状态与异常

#### 对账结果状态

| 状态 | 含义 | 期望行为 |
|------|------|----------|
| MATCHED | 平台与设备一致 | 绿色，无操作 |
| ORPHAN | 设备有、平台无 | 列表高亮，可 IGNORE/STOP/ADOPT |
| MISSING | 平台有、设备无 | 提示 retry 或标记失败 |
| DRIFT | 双方都有但 state/progress 不一致 | 提供 sync-status |

#### 子任务状态（沿用 scan_sub_task）

| state | 含义 |
|-------|------|
| 0 | 未开始 |
| 1 | 执行中 |
| 2 | 已完成 |
| 3 | 失败 |
| 4 | 暂停 |

#### 节点健康

| health_status | 含义 |
|---------------|------|
| healthy | 探活成功、metrics 正常 |
| degraded | API 可达但负载过高或证书临期 |
| offline | 不可达或认证失败 |

#### 异常场景

| 场景 | 期望行为 |
|------|----------|
| 扫描器 API 401 | 节点标记 offline，任务进入 wait 或失败，告警 |
| 下发超时无回调 | 自动触发 reconcile；若设备已有 task_id 则 ADOPT |
| pause 时任务已结束 | 返回明确错误码，sync-status 刷新 |
| AH create 后未 start | Adapter 自动 start；失败则 MISSING + retry |
| 不支持的能力 | preview-scanners 排除并说明原因 |
| tools-scheduler 与直连 API 双轨 | P0/P1 LM/AH 同步走 Adapter；下发仍兼容 Kafka/SOAR |

---

## 4. How — 技术约束

### 4.1 工程边界

| 工程 | 职责 |
|------|------|
| `vuln-task-center` | 治理中心全部 P0–P4 能力 |
| `vul-pass` | 计划创建/下发入口；Feign 调用增强（可选） |
| `vuln-model` | 漏洞库；模板 CVE 覆盖查询（P2 联动） |
| `open-api-service` | Partner 任务路由对接（P4） |

### 4.2 架构约束

1. **DDD 四层**：UI → App → Domain → Infra，遵循 `esmp-backend-dev` / `backend-ddd-layers`
2. **ScannerAdapter 接口**：厂商差异只允许出现在 `infra/adapter/scanner/{vendor}/`
3. **能力注册表**：`scanner_vendor`、`scanner_api_capability`、`scanner_node_capability`
4. **对账引擎**：Domain 层独立 `ReconcileDomainService`，不耦合 QueueAppServiceImpl
5. **迁移策略**：保留 `MsgSend*`，LM/AH 逻辑逐步委托给 Adapter，禁止大爆炸删除
6. **执行真相源**：新任务必须写 `scan_sub_task`；Observer 同步更新 ES
