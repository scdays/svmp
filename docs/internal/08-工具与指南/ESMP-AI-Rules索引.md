# ESMP AI Rules 索引

## 1. 索引用途

本文按公司级、asset-security 产品线级、项目级梳理 `.cursor/rules/*.mdc`，用于判断：

- Rule 属于哪一层。
- 何时触发。
- 适用哪些路径。
- 依赖哪些上层规则。
- 被哪些 Skill 使用。
- 是否强制。
- 后续是保留、补充、合并还是暂缓。

## 2. 公司级 Rules

| Rule | 触发方式 | 适用范围 | 上层依赖 | 主要使用 Skill | 强制 | 建议 |
|------|----------|----------|----------|----------------|------|------|
| `.cursor/rules/auto-dev-orchestrator.mdc` | `alwaysApply: true` | 用户提出完整功能需求、自动开发需求 | 无 | `auto-dev-orchestrator` | 是 | 保留 |
| `.cursor/rules/java-hard-ban.mdc` | `project_backend/**/*.java` | 后端 Java 文件 | `esmp-rd-standards` | `esmp-backend-dev`、`esmp-starter-dev`、`esmp-bugfix-dev`、`esmp-code-review-strict` | 是 | 保留 |
| `.cursor/rules/security-hard-ban.mdc` | `project_backend/**/*.{java,yml,yaml,properties}` | 后端 Java 与配置文件 | `esmp-rd-standards` | 后端、Starter、Bugfix、Review | 是 | 保留 |
| `.cursor/rules/test-required-strict.mdc` | `project_backend/**/*.java` | 后端 Java 文件 | `esmp-rd-standards` | 后端、Starter、Bugfix、Review | 是 | 保留 |
| `.cursor/rules/maven-dependency-strict.mdc` | `project_backend/**/pom.xml` | Maven 模块 | `esmp-rd-standards` | 后端、Starter、Review | 是 | 保留 |

说明：`esmp-rd-standards` 是公司级 Skill，不是 Rule，但所有公司级规则均应接受它的研发规范约束。

## 3. asset-security 产品线级 Rules

| Rule | 触发方式 | 适用范围 | 上层依赖 | 主要使用 Skill | 强制 | 建议 |
|------|----------|----------|----------|----------------|------|------|
| `.cursor/rules/backend-framework-context.mdc` | `alwaysApply: true` | ESMP 后端框架上下文 | 公司级研发规范 | `esmp-backend-dev` | 是 | 保留 |
| `.cursor/rules/frontend-framework-context.mdc` | `alwaysApply: true` | ESMP 前端微前端上下文 | 公司级研发规范 | `esmp-frontend-dev` | 是 | 保留 |
| `.cursor/rules/asset-security-platform-context.mdc` | `alwaysApply: true` | 资产安全平台产品线架构上下文 | 公司级研发规范 | 后端、Starter、Bugfix、Review、PRD 拆分 | 是 | 新增并保留 |
| `.cursor/rules/backend-ddd-layers.mdc` | `project_backend/**/*.java` | 后端 DDD 四层职责 | `backend-framework-context.mdc` | `esmp-backend-dev` | 是 | 第一阶段保留，后续评估合并 |
| `.cursor/rules/backend-layer-boundary-strict.mdc` | `project_backend/**/*.java` | DDD 严格分层边界 | `backend-framework-context.mdc`、`backend-ddd-layers.mdc` | 后端、Bugfix、Review | 是 | 保留 |
| `.cursor/rules/backend-naming.mdc` | `project_backend/**/*.java` | 后端类名、包名、后缀 | `backend-ddd-layers.mdc` | `esmp-backend-dev` | 是 | 第一阶段保留，后续评估合并 |
| `.cursor/rules/backend-ui-api.mdc` | `project_backend/**/*Ui.java`、`**/*UI.java` | UI 层 REST API | `backend-layer-boundary-strict.mdc` | 后端、Review | 是 | 第一阶段保留，后续评估合并 |
| `.cursor/rules/backend-starter-usage.mdc` | `project_backend/**/pom.xml` | ESMP starter 选用 | `backend-framework-context.mdc` | 后端、Starter | 是 | 第一阶段保留，后续评估合并 |
| `.cursor/rules/starter-dev-strict.mdc` | `project_backend/framework/platform/**/*.java`、`project_backend/framework/asset/esmp-starters/**/*.java`、`project_backend/framework/asset/esmp-starters-*/**/*.java` | 平台 / 框架 Starter 开发 | 公司级 Maven、安全、测试规则 | `esmp-starter-dev` | 是 | 保留 |

## 4. 项目级 Rules

| Rule | 触发方式 | 适用范围 | 上层依赖 | 主要使用 Skill | 强制 | 建议 |
|------|----------|----------|----------|----------------|------|------|
| `.cursor/rules/open-api-service-ddd.mdc` | `project_backend/svmp/open-api-service/**/*` | `open-api-service` | 后端框架、DDD 分层、Java、安全、测试 | `esmp-backend-dev`、`esmp-bugfix-dev`、`esmp-code-review-strict` | 是 | 保留 |
| `.cursor/rules/asset-openplatform-utf8.mdc` | `project_frontend/asset/asset-openplatform-manage/**/*.{vue,js}` | `asset-openplatform-manage` | 前端框架、研发规范 | `esmp-frontend-dev`、`esmp-code-review-strict` | 是 | 保留 |

## 5. Rule 使用决策表

| 任务类型 | 必读 Rule |
|----------|-----------|
| 后端 Java 开发 | `backend-framework-context.mdc`、`asset-security-platform-context.mdc`、`java-hard-ban.mdc`、`backend-ddd-layers.mdc`、`backend-layer-boundary-strict.mdc`、`backend-naming.mdc`、`test-required-strict.mdc`、`security-hard-ban.mdc` |
| 后端 UI / REST API | 后端 Java 开发清单 + `backend-ui-api.mdc` |
| Maven / 依赖调整 | `maven-dependency-strict.mdc`、`backend-starter-usage.mdc` |
| Starter 开发 | `asset-security-platform-context.mdc`、`starter-dev-strict.mdc`、`maven-dependency-strict.mdc`、`java-hard-ban.mdc`、`test-required-strict.mdc`、`security-hard-ban.mdc` |
| open-api-service 修改 | 后端 Java 开发清单 + `open-api-service-ddd.mdc` |
| asset-openplatform-manage 前端修改 | `frontend-framework-context.mdc`、`asset-openplatform-utf8.mdc` |
| vul-pass / asset-newleak-manage 任务域 | 后端/前端对应清单 + **`ponytail.mdc`（YAGNI/最小 diff 硬门禁，对齐 yc 样板）** |
| Bugfix | 按代码类型加载对应规则 + `test-required-strict.mdc` + `security-hard-ban.mdc` |
| Code Review | 当前 diff 涉及的所有公司级、产品线级、项目级规则 |

## 6. 后续整理建议

第一阶段不重命名、不删除现有 Rule。后续可按以下方向逐步整理：

1. 将 `backend-ddd-layers.mdc`、`backend-naming.mdc`、`backend-ui-api.mdc` 的重复内容沉淀到 `backend-layer-boundary-strict.mdc`。
2. 将 `backend-starter-usage.mdc` 与 `maven-dependency-strict.mdc` 的依赖边界说明统一。
3. 当 `platform-admin` 成为实际工程后，新增项目级 `platform-admin-context.mdc`。
4. 当 `partner-gateway` 改造进入开发阶段后，新增项目级 `partner-gateway-context.mdc`。
5. `ponytail.mdc`（2026-07-17）：对 `vul-pass` / `asset-newleak-manage` 升为按 globs 硬门禁；样板对齐 `vul_scan_task` / `vul_scan_task_sub` / `vul_archive_inst`（yc）。审查维度仍可与 `esmp-code-review-strict` 18-20、`esmp-bugfix-dev` 叠加。