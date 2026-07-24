# SOC 对接全链路 · 设计文档集

本目录按**需求**分目录组织，每个需求目录内部再用编号子目录细分文档类型（`01-架构与总览` / `02-主PRD` / `03-落地方案` / `04-子PRD与规格` / `05-接口契约` / `06-Mock与联调` / `07-multi-agent执行Prompts`，外加 `prototypes/` `_archive/`）。同一需求的 PRD、落地方案、契约、验收报告、原型集中在一处，便于检索与维护。

## 需求目录索引

| 需求目录 | 定位 | 关键文档 |
|---|---|---|
| [soc-link-SOC对接全链路/](soc-link-SOC对接全链路/) | 三发起方(OPEN/METRIC/ASSESS)统一、双轨存储、状态机、SOC 事件链路 | `02-主PRD/` 三份（v1.0 → v2修订附录 → 代码分析修正）、`03-落地方案/双阶段交叉扫描`、`05-接口契约/漏扫任务事件接口文档` |
| [open-platform-开放平台/](open-platform-开放平台/) | 开放平台对外 REST 执行面、Partner 鉴权、集成管理后台、运营案件 | `03-落地方案/` 6 份、`05-接口契约/` 映射表 + internal-api.yaml、`07-multi-agent执行Prompts/` 5 份、`prototypes/` |
| [open-gateway-网关合并改造/](open-gateway-网关合并改造/) | 网关合并 + 平台/业务解耦 + mock 纯桩化的目标架构与分期 | `01-架构与总览/` 改造方案 + 开发计划、`03-落地方案/partner-gateway-route-mode`、`06-Mock与联调/开放平台mock链路验收清单`（Phase 0 基线） |
| [platform-admin-控制面建设/](platform-admin-控制面建设/) | platform-admin 统一控制面、业务能力迁移 M1-M9、EventBus 治理 | `01-架构与总览/控制面与EventBus-Starter架构设计`、`03-落地方案/` 4 份、`04-子PRD与规格/` 00-主计划 + M1-M9、`prototypes/事件总线治理面原型` |
| [verify-fix-修复核验全链路/](verify-fix-修复核验全链路/) | 修复核验（vul-pass）全链路：PRD + 开发计划双权威、Wave 验收、自动化处置 | `04-子PRD与规格/修复核验全链路-文档地图与索引-v1.2.md`（**文档群总入口**）、`06-Mock与联调/` 11 份验收报告、`prototypes/` 7 个、`_archive/` 18 份迭代留痕 |
| [vuln-task-center-扫描治理中心/](vuln-task-center-扫描治理中心/) | 扫描治理中心三层能力模型、ScannerAdapter、对账四态、厂商适配 | `04-子PRD与规格/扫描治理中心-PRD` + `prototype-v3-spec`、`05-接口契约/vuln-task-center-ab-contract.yaml`、`prototypes/` |
| [scan-window-扫描时间窗/](scan-window-扫描时间窗/) | 漏洞管理平台扫描时间窗 + 超窗暂停/恢复（VULPASS-SCANWINDOW-P0~P3） | `04-子PRD与规格/扫描时间窗管理-vul-pass-PRD-v1.0.md` |
| [vuln-model-扫描任务迁移/](vuln-model-扫描任务迁移/) | vuln-model 扫描任务重构迁移至 vul-pass | `03-落地方案/`（**注意：该文件内容为 GBK 编码且存在历史乱码，未改写**） |
| [mock-引擎对接与联调/](mock-引擎对接与联调/) | adapter-mode=mock 联调策略、Mock Instance DB、半人工导入 | `03-落地方案/引擎对接与Mock模式方案`、`04-子PRD与规格/open-api-mock-instance-db-PRD`、`06-Mock与联调/` 配置指南 + 联调手册、`07-multi-agent执行Prompts/Mock-P1-DB` |

## 共享工程资产（顶层，跨需求复用）

| 目录 | 内容 | 说明 |
|---|---|---|
| `features/` | 任务拆分矩阵 YAML（P0/P1/P2、SOC-LINK、Mock 等） | 被 `.cursor/skills/prd-to-multi-agent` 与 `scripts/generate-multi-agent-prompts.py` 硬编码引用 |
| `templates/` | PRD 模板、需求分析模板、任务拆分矩阵模板 | 被 skills 引用 |
| `scripts/` | DDL 应用、PRD/原型生成、multi-agent prompts 生成、open-api DDD 校验等 | 被 `.cursor/rules`、`.cursor/skills`、项目 README 引用 |
| `08-工具与指南/` | Cursor 指南、一句话自动开发、ESMP AI Rules/Skills 工程化治理与索引、prd-to-multi-agent-工作流 | 被 `CLAUDE.md`、`.cursor/rules`、`.cursor/skills` 引用 |
| `_archive/杂物/` | 误存/测试残留文件（install.cmd、xxx.html、_enc_test.html） | 仅留痕 |

## 权威性提示

主 PRD 三份存在版本演进：`SOC对接全链路-PRD.md`(v1.0) → `SOC对接全链路-PRD-v2修订附录.md`(正式采纳) → `SOC对接全链路-PRD-代码分析修正.md`(工程代码校准)。**冲突处以最新版本为准**，关键演进点（SOC_DUAL 废弃、verify-fix 真实复扫、任务域路径、UNION 状态落库）已在各文档内标注。

修复核验文档群以 [verify-fix-修复核验全链路/04-子PRD与规格/修复核验全链路-文档地图与索引-v1.2.md](verify-fix-修复核验全链路/04-子PRD与规格/修复核验全链路-文档地图与索引-v1.2.md) 为总入口：有效执行文档为 **PRD v2.0.0 + 开发计划 v2.0** 双权威。

## 已知失效链接（迁移前即失效，未回改）

以下链接在重构前就已指向不存在的文件，本次按需求分目录后**未改动其目标**，仅在此登记，待对应文档补齐后再修：

- `联调手册-P0.md`、`partner-gateway与open-api-service-模块与接口清单.md`、`组件职责与接口映射.md`、`开放平台API治理与调用生命周期.md`、`漏洞管理平台对外集成能力设计方案-V2.0.md` — 见于 `open-platform-开放平台/03-落地方案/` 多份文档及 `svmp/README.md`、`project_backend/svmp/open-api-service/README.md`、`project_backend/svmp/partner-gateway/README.md`
- `../external/开放平台API接口规范.md` — `svmp/docs/external/` 下无此文件
- `vuln-model-扫描任务迁移/03-落地方案/vuln-model扫描任务重构迁移至vul-pass-落地方案.md` 内容本身为 GBK 编码且含历史乱码，内部链接未校验

## 目录调整记录

- 2026-07-21：由原「按文档类型分目录」（01-架构与总览 … 09-platform-admin）重构为「按需求分目录」。共享工程资产（features/templates/scripts/08-工具与指南）保持顶层不动；垃圾文件移入 `_archive/杂物/`；同步更新 `.cursor/rules/asset-security-platform-context.mdc`、`.cursor/rules/auto-dev-orchestrator.mdc`、`.cursor/skills/{auto-dev-orchestrator,prd-to-multi-agent,esmp-frontend-dev}/SKILL.md` 中的文档路径引用，并修复被移动文档内的相对链接。
