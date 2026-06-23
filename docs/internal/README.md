# SOC 对接全链路 · 设计文档集

本目录是「SOC 对接全链路」项目的设计文档集，覆盖开放平台网关、Partner 鉴权、漏洞业务编排、扫描治理、运营案件、修复核验、Mock 联调等全链路设计。

## 推荐阅读路径

> 新人按编号顺序读 01 → 06 即可建立全貌；07/08 为辅助工具。

1. **01-架构与总览** — 先看整体架构与最新改造方向
2. **02-主PRD** — 全链路基础设计（含版本演进）
3. **03-落地方案** — 各子域工程落地方案
4. **04-子PRD与规格** — 子系统 PRD 与原型规格
5. **05-接口契约** — 对外/内部接口映射与事件契约
6. **06-Mock与联调** — 联调期 Mock 配置与缺口记录
7. **07-multi-agent执行Prompts** — AI 多智能体执行编排（辅助）
8. **08-工具与指南** — Cursor/自动开发使用指南（辅助）

## 权威性提示

主 PRD 三份存在版本演进：`SOC对接全链路-PRD.md`(v1.0) → `SOC对接全链路-PRD-v2修订附录.md`(正式采纳) → `SOC对接全链路-PRD-代码分析修正.md`(工程代码校准)。**冲突处以最新版本为准**，关键演进点（SOC_DUAL 废弃、verify-fix 真实复扫、任务域路径、UNION 状态落库）已在各文档内标注。

---

## 01-架构与总览

| 文档 | 说明 |
|---|---|
| [一、架构总览线条.md](01-架构与总览/一、架构总览线条.md) | 全链路架构分层、Partner REST 执行面 17 接口清单、Mock 引擎跑通链路总览 |
| [open-gateway合并与平台业务解耦改造方案.md](01-架构总览/open-gateway合并与平台业务解耦改造方案.md) | 架构纠偏：网关合并 + 平台/业务解耦 + mock 纯桩化的目标架构与分期（最新改造方向） |
| [open-gateway改造开发计划.md](01-架构与总览/open-gateway改造开发计划.md) | 上述方案的任务卡级开发计划：Phase 0-4 任务卡、依赖图、里程碑、风险跟踪 |

## 02-主PRD

| 文档 | 说明 |
|---|---|
| [SOC对接全链路-PRD.md](02-主PRD/SOC对接全链路-PRD.md) | 主 PRD v1.0：三发起方(OPEN/METRIC/ASSESS)统一、双轨存储、状态机、Wave 矩阵 |
| [SOC对接全链路-PRD-v2修订附录.md](02-主PRD/SOC对接全链路-PRD-v2修订附录.md) | v2 修订（正式采纳）：废弃 SOC_DUAL、autoVerify 双阶段、推迟回调、Webhook 时机矩阵 |
| [SOC对接全链路-PRD-代码分析修正.md](02-主PRD/SOC对接全链路-PRD-代码分析修正.md) | 工程代码校准：已有 vs 需新建清单、Feign/Kafka 契约、接口路径修正 |

## 03-落地方案

| 文档 | 说明 |
|---|---|
| [开放平台Partner鉴权与隔离-落地方案.md](03-落地方案/开放平台Partner鉴权与隔离-落地方案.md) | Partner Token 签发/校验、能力码拦截、partner_id 隔离、三套入口鉴权 |
| [开放平台对外REST执行面-分期落地方案.md](03-落地方案/开放平台对外REST执行面-分期落地方案.md) | Open API 对外 REST 执行面 OP-OPENAPI-P0~P3 分期、Wave 顺序 |
| [开放平台集成管理-完整落地方案.md](03-落地方案/开放平台集成管理-完整落地方案.md) | 集成管理后台工程边界、qiankun 子应用、P0~P2 页面、治理面展示约束 |
| [开放平台集成管理后台-页面设计.md](03-落地方案/开放平台集成管理后台-页面设计.md) | 后台页面交互与信息架构设计 |
| [open-api-vtc-pass-落地方案.md](03-落地方案/open-api-vtc-pass-落地方案.md) | open-api → vul-pass 内部接口落地方案、新任务域路径 `/internal/open/v1/tasks` |
| [漏洞实例与生命周期双轨存储-落地方案.md](03-落地方案/漏洞实例与生命周期双轨存储-落地方案.md) | vul_archive_inst 主档 + oper/report 双轨、部侧查询改造、SQL 改造 |
| [vuln-model扫描任务重构迁移至vul-pass-落地方案.md](03-落地方案/vuln-model扫描任务重构迁移至vul-pass-落地方案.md) | vuln-model 扫描任务重构迁移至 vul-pass 的落地方案 |
| [引擎对接与Mock模式方案.md](03-落地方案/引擎对接与Mock模式方案.md) | adapter-mode=mock 联调策略、bundles 占位、切流回归 |
| [双阶段交叉扫描方案-SOC并集与部侧交集统一.md](03-落地方案/双阶段交叉扫描方案-SOC并集与部侧交集统一.md) | 排查单扫 + 验证双扫、UNION/INTERSECT 合并策略、dedupKey、SOC 时序 |
| [开放平台运营案件-open_operation_case-方案.md](03-落地方案/开放平台运营案件-open_operation_case-方案.md) | case_id 统一句柄、5 表关联、case_type 枚举、统一工作台、渐进迁移 |

## 04-子PRD与规格

| 文档 | 说明 |
|---|---|
| [open-api-export-webhook-PRD.md](04-子PRD与规格/open-api-export-webhook-PRD.md) | Webhook 外发双格式(xml+json)、downloadUrl 构造、上传与投递 |
| [open-api-mock-instance-db-PRD.md](04-子PRD与规格/open-api-mock-instance-db-PRD.md) | Mock Instance DB 设计 |
| [vuln-task-center-扫描治理中心-PRD.md](04-子PRD与规格/vuln-task-center-扫描治理中心-PRD.md) | 扫描治理中心三层能力模型、ScannerAdapter、对账四态、厂商适配(LM/AH)、P0~P4 分期 |
| [修复核验运营工作台-PRD.md](04-子PRD与规格/修复核验运营工作台-PRD.md) | verify-fix job 维度工作台、复用 open_task_sub(scan_phase=3)、双 Kafka 闭环 |
| [OPEN状态跃迁与考核隔离说明.md](04-子PRD与规格/OPEN状态跃迁与考核隔离说明.md) | OPEN 三条状态路径冻结、UNION 不走 PassRoot、考核线禁改清单 |
| [vuln-task-center-prototype-v3-spec.md](04-子PRD与规格/vuln-task-center-prototype-v3-spec.md) | 扫描治理中心原型 v3 交付规格（以 survey 实例工作台为主轴） |

## 05-接口契约

| 文档 | 说明 |
|---|---|
| [Open API与vul-pass内部接口映射表.md](05-接口契约/Open%20API与vul-pass内部接口映射表.md) | 对外 Open API ↔ vul-pass 内部接口映射、实例域两硬约束、状态码表 |
| [漏扫任务事件接口文档.md](05-接口契约/漏扫任务事件接口文档.md) | SOC 事件接口：SurveyEvent 查询 + ScanTaskEvent 创建扫描计划入口 |
| [open-api-vtc-pass-internal-api.yaml](05-接口契约/open-api-vtc-pass-internal-api.yaml) | open-api ↔ vul-pass 内部接口 OpenAPI 契约定义 |

## 06-Mock与联调

| 文档 | 说明 |
|---|---|
| [open-api-mock-manual-配置指南.md](06-Mock与联调/open-api-mock-manual-配置指南.md) | 半人工 Mock 报告导入配置指南 |
| [联调手册-Mock-Instance-DB.md](06-Mock与联调/联调手册-Mock-Instance-DB.md) | Mock Instance DB 联调手册 |
| [1. 当前缺口：修复核验没接报告回调.md](06-Mock与联调/1.%20当前缺口：修复核验没接报告回调.md) | 修复核验报告回调缺口分析与修复路径（VFS skip 根因） |

## 07-multi-agent执行Prompts

| 文档 | 说明 |
|---|---|
| [multi-agent-执行Prompts.md](07-multi-agent执行Prompts/multi-agent-执行Prompts.md) | 多智能体执行 Prompts 总入口 |
| [multi-agent-执行Prompts-P1.md](07-multi-agent执行Prompts/multi-agent-执行Prompts-P1.md) | P1 阶段执行 Prompts |
| [multi-agent-执行Prompts-P2.md](07-multi-agent执行Prompts/multi-agent-执行Prompts-P2.md) | P2 阶段执行 Prompts |
| [multi-agent-执行Prompts-OpenAPI-P1.md](07-multi-agent执行Prompts/multi-agent-执行Prompts-OpenAPI-P1.md) | OpenAPI P1 阶段执行 Prompts |
| [multi-agent-执行Prompts-OpenAPI-P2.md](07-multi-agent执行Prompts/multi-agent-执行Prompts-OpenAPI-P2.md) | OpenAPI P2 阶段执行 Prompts |
| [multi-agent-执行Prompts-Mock-P1-DB.md](07-multi-agent执行Prompts/multi-agent-执行Prompts-Mock-P1-DB.md) | Mock P1 DB 阶段执行 Prompts |
| [multi-agent-执行Prompts-SOC-LINK.md](07-multi-agent执行Prompts/multi-agent-执行Prompts-SOC-LINK.md) | SOC 全链路执行 Prompts |
| [prd-to-multi-agent-工作流.md](07-multi-agent执行Prompts/prd-to-multi-agent-工作流.md) | PRD 转多智能体工作流说明 |

## 08-工具与指南

| 文档 | 说明 |
|---|---|
| [Cursor使用指南.md](08-工具与指南/Cursor使用指南.md) | Cursor 编辑器使用指南 |
| [一句话自动开发.md](08-工具与指南/一句话自动开发.md) | 一句话驱动自动开发的用户说明 |

---

## 工程产物目录（非文档）

| 目录 | 内容 |
|---|---|
| `contracts/` | 接口契约 YAML（如 vuln-task-center-ab-contract.yaml） |
| `features/` | 功能特性定义 YAML（P0/P1/P2 分期、任务矩阵） |
| `prototypes/` | HTML 原型与构建脚本（admin/vtc/task-center 原型） |
| `scripts/` | 工程脚本（DDL、PRD 生成、原型构建、中文文件写入等） |
| `templates/` | PRD 模板与任务拆分矩阵模板 |

## 历史归档

`_archive/` 存放已合并进主 PRD 的拆分过程碎片（`prd-part-*`、`_ah_section_43`）与 PRD 合并/格式化过程脚本（`merge_prd*.py`、`fix_prd_format.py` 等），仅供历史追溯，不再维护。

根目录保留 `SOC对接全链路-PRD.7z` 为原始压缩归档。
