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
| US-P04 | 平台管理员 | 维护「报告模板 ↔ 厂商 report_template_id」映射 | LM/AH 模板 id 变更可配置 | P2 |
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
