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
| 报告能力分散 | LM 报告下载逻辑着散在 ScanTaskAppServiceImpl / Kafka，无统一模板与状态 |

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
4. **结果与报告交付**：按报告模板生成、进度跟踪、下载/投递（LM/AH）

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

### 3.0 产品域模型（v0.3 重构）

> **设计原则**：从「设备管理 + 任务管理」两个菜单，升级为 **以扫描实例（survey）为主线的全生命周期治理**。设备/能力是支撑域，不是运营主入口。

#### 3.0.1 四大产品域

| 域 | 定位 | 核心对象 | 对应原 3.1 |
|----|------|----------|------------|
| **A. 扫描执行** | 运营主路径 | survey → sub_task | US-T*、US-R*（执行期） |
| **B. 资源与能力** | 平台管理员配置 | node / scanner / capability / 扫描模板 | US-D*、US-A* |
| **C. 结果与报告** | 扫描价值交付 | report_job / report_template / 交付物 | **新增 US-P*** |
| **D. 治理与观测** | 稳定性与合规 | reconcile / metrics / alert / audit | US-R*（对账）、仪表盘 |

#### 3.0.2 扫描实例生命周期（原型必须能走通）

```text

创建/下发 → 预览扫描器 → 路由下发 → 子任务执行 → 对账一致

    → 结果回传(vuln-model) → 报告触发生成 → 模板渲染 → 下载/投递

         ↑__________________ DRIFT/MISSING 可在此链路任意环节介入 __________________↑

```

#### 3.0.3 信息架构（菜单 v3，替代 v2 零散页面）

| 一级菜单 | 二级 | 说明 |
|----------|------|------|
| **工作台** | 运营首页 | 待对账、MISSING、报告待生成、队列积压、节点 offline |
| **扫描中心** | 计划 / 实例列表 | 主列表；点击进入 **实例工作台**（非分散页） |
| | 实例工作台 | Tab：概览 / 子任务 / 下发参数 / 对账 / 结果 / **报告** |
| | 新建扫描 | 向导：场景→目标→预览→确认 |
| **资源中心** | 节点 / 逻辑扫描器 / 场景 | 管理员域 |
| | 能力目录 | LM + AH Profile |
| | 模板与字典 | 扫描模板 + **报告模板** 分 Tab |
| **报告中心** | 报告任务 | 全平台 report_job 列表、状态、重试 |
| | 模板配置 | 报告模板与厂商 template 映射 |
| | 导出记录 | 下载历史、FTP/MinIO 路径、投递 vul-pass |
| **治理中心** | 任务对账 | ORPHAN/MISSING/DRIFT + diff |
| | 队列监控 | send/wait/execute |
| | 仪表盘 / 告警 | 观测 |

#### 结果与报告 — 用户故事

| ID | 作为… | 我希望… | 以便… | 阶段 |
|----|-------|---------|-------|------|
| US-P01 | 安全运营 | 在 survey 详情看到各子任务报告生成状态（未生成/生成中/可下载/失败） | 知道何时可取报告 | P1 |
| US-P02 | 安全运营 | 按 **报告模板**（汇总/主机/基线/弱口令等）为已完成子任务触发生成 | 不同场景输出不同格式 | P1 |
| US-P03 | 安全运营 | 批量下载 HTML/PDF/XML 或打包 ZIP | 交付审计或上传工单 | P1 |
| US-P04 | 平台管理员 | 维护「报告模板 ? 厂商 report_template_id」映射 | LM/AH 模板 id 变更可配置 | P2 |
| US-P05 | 安全运营 | 报告生成失败一键重试，查看 progress / 失败原因 | 减少人工 FTP 排查 | P1 |
| US-P06 | vul-pass | 扫描完成后自动触发默认报告模板并回写工单附件 | 工单闭环 | P2 |
| US-P07 | 安全运营 | 查看报告与 scan_sub_task / plan_id 关联及生成参数快照 | 审计可追溯 | P1 |

> **与现有代码关系**：`ScanTaskUi` 已有 LM 报告下载（`/vulnScan/domnload/report/*`）、`report_download` syn_type；v0.3 目标为统一 `ReportAdapter` + 状态机，不再分散在 ScanTaskAppServiceImpl。

#### 报告 REST API（新增）

| 方法 | 路径 | 说明 | 阶段 |
|------|------|------|------|
| GET | `/v1/scan/report/jobs` | 报告任务列表（surveyId/subTaskId/status） | P1 |
| GET | `/v1/scan/report/jobs/{id}` | 单报告任务详情（progress、模板、输出格式） | P1 |
| POST | `/v1/scan/report/jobs` | 触发生成（subTaskId + reportTemplateCode + format） | P1 |
| POST | `/v1/scan/report/jobs/{id}/retry` | 失败重试 | P1 |
| GET | `/v1/scan/report/jobs/{id}/download` | 下载/重定向到存储 URL | P1 |
| GET | `/v1/scan/report/templates` | 平台报告模板目录 | P2 |
| POST | `/v1/scan/report/templates/sync` | 从厂商同步 report template 列表 | P2 |
| GET | `/v1/scan/task/{surveyId}/reports/summary` | survey 维度报告聚合状态 | P1 |

#### 厂商报告 Capability（补充 4.3）

| capability_code | LM RSAS API | AH DAS-RAS API | 阶段 |
|-----------------|-------------|----------------|------|
| report.template.list | GET /api/report/template/list | —（AH 策略模板复用 policy） | P2 |
| report.generate | POST /api/generate_report/ | GET /api/normal/task/doReport | P1 |
| report.progress | GET /api/get_report_progress/{id} | task.progress（复用） | P1 |
| report.download | GET /api/download_report/... | doReport 返回 / 联调 | P1 |
| report.task | GET /api/report/task/{task_id} | task.result（部分场景） | P2 |

#### 报告任务状态

| report_status | 含义 |
|---------------|------|
| pending | 扫描未完成，不可生成 |
| queued | 已排队等待生成 |
| generating | 厂商生成中 |
| ready | 可下载 |
| failed | 生成失败 |
| delivered | 已投递 vul-pass/FTP |

#### 成功标准（补充）

| 指标 | 标准 | 阶段 |
|------|------|------|
| 报告闭环 | LM 子任务完成后可经 API 触发生成并 download | P1 |
| 模板可选 | 至少支持 2 种报告模板（如汇总+主机） | P1 |
| survey 聚合 | survey 详情可看到各 sub_task 报告状态汇总 | P1 |

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
| 扫描报告生成与下载（ReportAdapter） | | ✅ | 增强 | | |
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
### 4.3 能力代码映射（Scanner Capability Profile）

能力注册表以 **vendor_code + capability_code** 唯一标识；各厂商 API 路径不同，但对上层暴露统一 capability 语义。
P0 种子数据：**LM**；P1 扩展：**AH**（安恒明鉴 DAS-RAS V5.0）。

#### 4.3.1 绿盟 RSAS V6.0.8（vendor_code=LM）

| capability_code | RSAS API | 平台 syn_type（现有） | 阶段 |
|-----------------|----------|----------------------|------|
| task.create | POST /api/task/create | taskCreate | P0 |
| task.status | GET /api/task/status/{id} | — | P0 |
| task.active_list | GET /api/task/active_list | active_list | P0 |
| task.list | GET /api/task/list | — | P1 |
| task.pause | POST /api/task/pause/{id} | task_pause | P0 |
| task.resume | POST /api/task/resume/{id} | task_resume | P0 |
| task.stop | POST /api/task/stop/{id} | — | P1 |
| task.delete | POST /api/task/delete/{id} | task_delete | P1 |
| system.status | GET /api/system/status | sys_status | P0 |
| template.sysvuln.list | GET /api/template/sysvuln/list | syn_sysvuln_data | P2 |
| template.baseline.list | GET /api/template/baseline/list | syn_baseline_data | P2 |
| userpwd.list | GET /api/userpwd/list | syn_pwd_data | P2 |
| report.task | GET /api/report/task/{id} | — | P2 |
| auth.login_verify | POST /api/auth/login_verify | — | P2 |

参考：svmp/docs/standards/_extracted/lm-api-v608.txt

#### 4.3.2 安恒明鉴 DAS-RAS V5.0（vendor_code=AH）

**协议**：HTTPS · Base {ip}:{port}/api/normal/* · UTF-8  
**认证**：GET /api/normal/token?userName=&userCode=（userCode=密码 MD5，见 MsgSendAH.queryToken）  
**模块 module**（附录1；下发/对账必带）：

| module | 扫描类型 | 平台 taskType（MsgSendAH） |
|--------|----------|---------------------------|
| 0 | 网站 webscan | web |
| 1 | 数据库 dbscan | — |
| 5 | 基线 baseline | base_line_scan |
| 8 | 主机 hostscan | vuln / weak_password_scan |
| capability_code | DAS-RAS API | 说明 | 阶段 |
|-----------------|-------------|------|------|
| auth.token | GET /api/normal/token | Token 认证 | P1 |
| engine.list | GET /api/normal/getEngines | 引擎列表 | P1 |
| engine.list.v5 | GET /api/normal/getEngines/v5 | V5 引擎 state 600–603 | P1 |
| task.create | POST /api/normal/task/create | 创建，返回 taskId | P1 |
| task.create.from_asset | POST /api/normal/task/createFromExistAsset | 从资产创建 | P2 |
| task.start | POST /api/normal/task/start | **创建后需 start 才执行** | P1 |
| task.suspend | POST /api/normal/task/suspend | 暂停 | P1 |
| task.resume | POST /api/normal/task/start | 暂停后恢复（手册无独立 resume，与 start 联调确认） | P1 |
| task.stop | POST /api/normal/task/stop | 停止 | P1 |
| task.delete | POST /api/normal/task/delete | 删除 | P1 |
| task.progress | POST /api/normal/task/progress | 进度 0–100 | P1 |
| task.status | GET /api/normal/task/getTaskStatus | state + progress | P1 |
| task.list | GET /api/normal/task/list | 任务列表 | P1 |
| task.list.v2 | GET /api/normal/task/list/V2 | 按 state/时间筛选（**对账源** ） | P1 |
| task.result | GET /api/normal/task/result | 扫描结果 | P2 |
| policy.get | GET /api/normal/policy/get | 策略 | P2 |
| policy.templates | GET /api/normal/policy/getPolicyTemplates | 策略模板 | P2 |
| system.version | GET /api/normal/system/version | 版本 | P1 |
| system.resource | GET /api/normal/system/resouceuasge | CPU/内存 metrics | P1 |
| dict.list | GET /api/normal/dict/list | 弱口令字典 | P2 |
| asset.check_connection | POST /api/normal/asset/checkConnection | 连通性预检 | P2 |
| report.generate | GET /api/normal/task/doReport | 报表 | P3 |

**明鉴 state（附录2）→ 平台 scan_sub_task.state：**

| AH state | 含义 | 平台 |
|----------|------|------|
| 1 | 等待调度 | 0 |
| 2 | 正在扫描 | 1 |
| 3 | 暂停 | 4 |
| 4 | 停止 | 3 |
| 5 | 结束 | 2 |
| 6 | 异常 | 3 |

**AH 对账**：活跃任务源 `GET /api/normal/task/list/V2`（state∈{1,2,3}）+ getTaskStatus；ORPHAN/MISSING/DRIFT 规则同 4.5。

**现有代码**：MsgSendAH（module 0/5/8、SOAR/tools-scheduler）、VulnTaskListenerAH（vulId 增量同步）。  
P1 目标：AhScannerAdapter 封装 create→start 两阶段 + reconcile。

参考：svmp/docs/standards/扫描器/明鉴漏洞扫描系统API手册V5.0-20230801.docx  
提取：svmp/docs/standards/_extracted/ah-api-v5.txt

#### 4.3.3 跨厂商 capability 对齐

| 统一 capability | LM | AH |
|-------------------|----|----|
| 对账活跃任务 | task.active_list | task.list.v2 |
| 单任务状态 | task.status | task.getTaskStatus |
| 系统负载 | system.status | system.resource |
| 任务创建 | 一步 create | create + start |
| 模板/策略 | template.*.list | policy.get / getPolicyTemplates |
| 凭据预检 | auth.login_verify | asset.checkConnection |

### 4.4 数据模型（新增/扩展）

**扩展 scan_node**

| 字段 | 类型 | 说明 |
|------|------|------|
| health_status | varchar | healthy/degraded/offline |
| last_heartbeat_at | datetime | 最后探活 |
| supported_capabilities | json | 能力 code 数组 |
| vendor_device_hash | varchar | 设备 hash（LM hash / AH 版本等） |

**新增 scanner_api_capability**

| 字段 | 说明 |
|------|------|
| vendor_code | LM/AH/... |
| capability_code | task.create 等 |
| http_method, path_template | API 定义 |
| required | 是否接入必选 |
| min_firmware_version | 最低版本 |

**新增 reconcile_task_diff**

| 字段 | 说明 |
|------|------|
| node_id, survey_id, sub_task_id | 关联 |
| vendor_task_id | 设备侧 task_id（LM plan_id / AH taskId） |
| diff_type | MATCHED/ORPHAN/MISSING/DRIFT |
| platform_state, vendor_state | 对比 |
| handled_action | IGNORE/STOP/ADOPT |
| reconcile_at | 对账时间 |

**新增 scanner_template（P2）**

| 字段 | 说明 |
|------|------|
| node_id, template_type, vendor_template_id | 模板标识 |
| name, content_hash, raw_json, synced_at | 内容与版本 |

### 4.5 对账匹配规则

#### 4.5.1 绿盟（LM）

1. **主键**：`scan_sub_task.plan_id` ↔ 绿盟 `task_id`
2. **辅键**：`classify_task_name` + `time_start_scan` + `user_account`（fuzzy）
3. **活跃任务源**：`GET /api/task/active_list`
4. **ORPHAN**：在 active_list 中且 plan_id 不在平台 sub_task 表
5. **MISSING**：平台 sub_task 为执行中/未开始，且 active_list + task.status 均不存在
6. **DRIFT**：plan_id 匹配但 state 映射不一致（LM: 0/2/4/5/8 → 平台 0/1/2/4/3）

#### 4.5.2 安恒（AH）

1. **主键**：`scan_sub_task.plan_id` ↔ 明鉴 `taskId`（字符串）
2. **module 维度**：对账与下发须携带 module（0=web / 5=baseline / 8=host），与 `MsgSendAH` 映射一致
3. **活跃任务源**：`GET /api/normal/task/list/V2?module={m}&state=1,2,3`（等待/扫描/暂停）
4. **状态拉取**：`GET /api/normal/task/getTaskStatus?taskId=` + `POST /api/normal/task/progress`
5. **ORPHAN / MISSING / DRIFT**：语义同 4.5.1；state 映射见 4.3.2 附录2
6. **两阶段下发**：平台 MISSING 时需区分「create 成功未 start」与「create 失败」

### 4.6 禁止改动

- `clover-front/**`
- 其他省份定制 flag 逻辑（本 PRD 不收敛）
- vul-pass 工单状态机核心（仅 Feign 增强）

---

## 5. 分期交付详述

### 5.1 VTC-GOV-P0（约 3–4 周）— LM 核心抽象 + 对账

**范围**

- `ScannerAdapter` 接口 + `LmScannerAdapter` 实现（封装现有 LM 同步链）
- 能力注册表 DDL + **绿盟**种子数据
- `scan_node` 扩展字段
- 对账引擎 + REST（trigger/diff/query），**LM active_list**
- `dispatch-detail`、`sub-tasks/summary`、`sync-status`
- 新下发任务强制写 `scan_sub_task`（与现有 Queue 流程集成）

**验收**

- [ ] 绿盟节点手动触发对账，返回 MATCHED/ORPHAN/MISSING/DRIFT
- [ ] 模拟下发超时后 reconcile 可发现 MISSING 或 ADOPT
- [ ] `GET dispatch-detail` 含 platformParams、adapterParams、subTasks
- [ ] `MsgSendLM` 无新增代码；新 LM 同步走 Adapter
- [ ] mvn compile + 现有扫描下发回归通过

### 5.2 VTC-GOV-P1（约 3–4 周）— 设备治理 + AH 适配 + 任务操控

**范围**

- `AhScannerAdapter` 实现（Token、create+start、list.v2 对账、getTaskStatus、resource metrics）
- 能力注册表 **AH 种子数据**（见 4.3.2）
- metrics / health.check / dashboard API（LM + AH）
- preview-scanners（taskType + IP + template + capabilities + load）
- sub-task pause/resume/retry/cancel（LM/AH 映射）
- 定时对账 Job（LM + AH）
- ORPHAN handle API

**验收**

- [ ] AH 节点对账可发现 ORPHAN/MISSING/DRIFT
- [ ] metrics API：LM 对齐 system.status；AH 对齐 system.resource（注意厂商路径拼写 `resouceuasge`）
- [ ] preview-scanners 返回节点 score 与 excludedReasons（含 AH module 不匹配）
- [ ] AH 子任务 create→start 后 state 与设备一致；suspend/start 操控可用
- [ ] 暂停/恢复绿盟子任务后 state 与设备一致
- [ ] 定时对账 10min 内可发现注入的 ORPHAN

### 5.3 VTC-GOV-P2（约 2–3 周）— 模板与预检

**范围**

- scanner_template 表 + sync API
- LM：sysvuln/webvuln/baseline 模板同步
- AH：policy.get / getPolicyTemplates、dict.list 同步
- LM auth.login_verify；AH asset.checkConnection 下发前预检（可选开关）
- 弱口令字典与 platform 映射增强

**验收**

- [ ] 模板 sync 后 preview-scanners 可校验 template_id / policyNo
- [ ] 预检失败任务不下发，返回明确原因

### 5.4 VTC-GOV-P3（约 2 周）— 调度增强 + 观测

**范围**

- 负载策略：亲和性、场景 QoS、抢占（可选）
- metrics 历史表 + 简单趋势
- Prometheus 指标暴露 + 离线/证书临期告警规则

### 5.5 VTC-GOV-P4（约 2 周）— 开放对接

**范围**

- open-api-service 下发链路可选走 preview-scanners
- Partner 任务状态查询聚合 sub_task 进度

---

## 6. 验收标准（交付门禁）

### P0 总门禁

- [ ] 成功标准表中 P0 指标全部满足
- [ ] 绿盟端到端：创建计划 → 下发 → sub_task 落库 → 对账 MATCHED
- [ ] 人为在 RSAS 建任务 → 对账 ORPHAN → handle IGNORE/STOP 可用
- [ ] 代码审查：QueueAppServiceImpl 无新增厂商 if-else
- [ ] Liquibase 迁移脚本可重复执行
- [ ] 文档：`落地方案` + `任务拆分矩阵 YAML` 已产出

### P1 总门禁（含 AH）

- [ ] 安恒端到端：create+start → sub_task 落库 → 对账 MATCHED
- [ ] AH DRIFT（人工 suspend）→ sync-status / start 恢复
- [ ] 能力注册表含 LM + AH 完整 Profile 种子
- [ ] `MsgSendAH` 无新增下发逻辑；对账/监控/操控走 `AhScannerAdapter`

### 非功能

- [ ] 对账单节点耗时 < 30s（100 活跃任务内）
- [ ] metrics API P99 < 3s（含扫描器 RTT）
- [ ] 敏感字段（password）不出现在 dispatch-detail 明文（脱敏）

---

## 7. 风险与依赖

| 风险 | 缓解 |
|------|------|
| tools-scheduler 与直连 API 行为不一致 | Adapter 内统一；对账以设备 API 为准 |
| SOAR 通道 LM/AH 无法直连 | SOAR 模式走现有 MsgSend，Adapter 仅 read 类能力 |
| 双轨执行态迁移 | P0 仅新任务强制 sub_task；旧 ES 只读 |
| AH create 后须 start | Adapter 封装两阶段；失败可 retry |
| AH API 路径拼写错误（resouceuasge） | 按手册原样实现，配置项可覆盖 |
| AH resume 无独立接口 | 联调确认 start 或 suspend 语义；文档化 |
| QM/AZ 能力不全 | 能力注册 required=false，preview 自动过滤 |
| 依赖 | 说明 |
|------|------|
| 绿盟 RSAS 测试环境 | LM 对账/操控验收 |
| 安恒 DAS-RAS V5.0 测试环境 | AH 对账/操控验收 |
| tools-scheduler | 下发通道保持不变 |
| vul-pass Feign | IVulnTaskCenterClient 可选扩展 |

---

## 8. 附录

### 8.1 参考文档

| 厂商 | 原始文档 | 提取文本 |
|------|----------|----------|
| 绿盟 LM | `svmp/docs/standards/绿盟远程安全评估系统API接口文档V6.0.8-20230403.doc` | `svmp/docs/standards/_extracted/lm-api-v608.txt` |
| 安恒 AH | `svmp/docs/standards/扫描器/明鉴漏洞扫描系统API手册V5.0-20230801.docx` | `svmp/docs/standards/_extracted/ah-api-v5.txt` |

- 现有实现：`project_backend/svmp/vuln-task-center/`
- 研发规范：`.cursor/skills/esmp-backend-dev/SKILL.md`、`.cursor/skills/esmp-rd-standards/SKILL.md`

### 8.2 现有代码锚点

| 主题 | 路径 |
|------|------|
| 队列与负载 | `QueueAppServiceImpl.getNodeScannerMap` |
| LM 定时同步 | `VulnTaskListenerLM` |
| AH 定时同步 | `VulnTaskListenerAH` |
| 同步分发 | `SynVulnDataBySchedulerAnalysis` |
| 子任务 | `ScanSubTaskDO` / `ScanSubTaskUi` |
| 厂商消息 LM | `MsgSendLM` |
| 厂商消息 AH | `MsgSendAH`（module 0/5/8、queryToken、SOAR/tools-scheduler） |

### 8.3 拆分检查清单

- [x] 成功标准可验收
- [x] 页面/接口清单含阶段标记
- [x] 不做边界已写清
- [x] 工程边界已知
- [x] 验收标准与成功标准一致
- [x] 双厂商（LM + AH）Capability Profile 已定义

**下一步**：PRD 评审通过后 → 产出 `vuln-task-center-扫描治理中心-落地方案.md` → 填写 `features/vtc-gov-p0.yaml` → 用户回复「同意执行」后走 auto-dev 编排。

---

## 9. 修订记录

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|------|
| 0.1 草稿 | 2026-06-14 | — | 基于目标架构 + 绿盟 API V6.0.8 首版 |
| 0.2 草稿 | 2026-06-14 | — | 新增安恒明鉴 DAS-RAS V5.0 Capability Profile、对账/操控/P1 交付范围 |
| 0.3 草稿 | 2026-06-14 | — | 产品域模型 3.0、结果与报告域 US-P*、原型 v3 交付规格 |

---

> 原型 v3 交付规格见：`vuln-task-center-prototype-v3-spec.md`
