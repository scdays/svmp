
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
