# ESMP AI Skills 索引

## 1. 索引用途

本文按公司级、asset-security 产品线级、项目级梳理当前 ESMP Skills，用于判断：

- Skill 属于哪一层。
- 负责什么任务流程。
- 必须叠加哪些 Rules。
- 能与哪些 Skill 组合。
- 禁止事项是什么。
- 如何验收。

Skills 的真实数据源在 `.cursor/skills/<name>/SKILL.md`，Claude Code 通过 `.claude/skills/<name>/` junction 发现并加载。

## 2. 公司级 Skills

### 2.1 `esmp-rd-standards`

| 项目 | 内容 |
|------|------|
| 层级 | 公司级 |
| 职责 | 网安事业部研发规范与编码标准基础入口，规定 GitFlow、提交格式、GitLab 强制规约、编码质量、安全红线 |
| 必须叠加 Rules | 按任务类型叠加 Java、DDD、测试、安全、Maven、Starter、前端规则 |
| 组合关系 | 所有开发、Bugfix、Starter、Review Skill 的基础 |
| 禁止事项 | 禁止绕过 GitFlow、提交格式、GitLab 强制规约；禁止拼音命名、魔法值、中文标识符；禁止违反 Java 强制规约 |
| 验收方式 | GitLab 强制项、`mvn compile` / `npm run lint`、Commit `[TYPE]`、UTF-8 无 BOM |

### 2.2 `auto-dev-orchestrator`

| 项目 | 内容 |
|------|------|
| 层级 | 公司级 |
| 职责 | 用户一句话自动完成规划、任务拆分、多 Agent 并行开发、联调验收 |
| 必须叠加 Rules | `esmp-rd-standards` + 当前任务涉及的公司级 / 产品线级 / 项目级 Rules |
| 组合关系 | 总编排 Skill，按任务类型调用后端、前端、Starter、Bugfix、Review、PRD 拆分 Skill |
| 禁止事项 | 禁止让用户复制 Prompt、开新会话、手跑脚本；未确认计划前禁止派子 Agent、禁止改业务代码 |
| 验收方式 | 开发计划、Wave 执行、Integration / Review、verify 命令、通过/未通过清单 |

### 2.3 `esmp-code-review-strict`

| 项目 | 内容 |
|------|------|
| 层级 | 公司级 |
| 职责 | 严格代码审查，统一检查公司级、产品线级、项目级规则 |
| 必须叠加 Rules | 当前 diff 涉及的所有规则 |
| 组合关系 | 可独立使用，也可作为自动开发最后验收阶段 |
| 禁止事项 | 禁止只说“看起来没问题”；禁止无文件行号；禁止发现编译失败仍给通过结论 |
| 验收方式 | 阻塞问题 / 非阻塞建议 / 验证命令 / 最终结论 |

## 3. asset-security 产品线级 Skills

### 3.1 `esmp-backend-dev`

| 项目 | 内容 |
|------|------|
| 层级 | asset-security 产品线级 |
| 职责 | 基于 spore-base-ddd 与 esmp-starter 的 ESMP 后端功能开发 |
| 必须叠加 Rules | `backend-framework-context.mdc`、`asset-security-platform-context.mdc`、`java-hard-ban.mdc`、`backend-ddd-layers.mdc`、`backend-layer-boundary-strict.mdc`、`backend-naming.mdc`、`test-required-strict.mdc`、`security-hard-ban.mdc` |
| 组合关系 | 与 `esmp-rd-standards` 必然叠加；Bugfix 时叠加 `esmp-bugfix-dev`；Review 时叠加 `esmp-code-review-strict` |
| 禁止事项 | UI 层不写业务逻辑；Domain 不依赖 UI DTO；不绕过基类手写 CRUD；不破坏 open-api-service 顶层包约束 |
| 验收方式 | `mvn compile`、脚手架清单、DDD 分层检查；open-api-service 必跑 `verify-open-api-ddd.ps1 -Compile` |

### 3.2 `esmp-frontend-dev`

| 项目 | 内容 |
|------|------|
| 层级 | asset-security 产品线级 |
| 职责 | 基于 qiankun、Vue2、Ant Design Vue 的 ESMP 前端开发 |
| 必须叠加 Rules | `frontend-framework-context.mdc`；涉及 asset-openplatform-manage 时叠加 `asset-openplatform-utf8.mdc` |
| 组合关系 | 与 `esmp-rd-standards` 必然叠加；Review 时叠加 `esmp-code-review-strict` |
| 禁止事项 | 禁止子应用独立 `permission.js`；禁止裸用 axios；禁止硬编码后端 IP；禁止破坏中文编码 |
| 验收方式 | `npm run lint`；asset-openplatform-manage 需执行 UTF-8 验证流程 |

### 3.3 `esmp-starter-dev`

| 项目 | 内容 |
|------|------|
| 层级 | asset-security 产品线级 |
| 职责 | ESMP / asset-security 平台 Starter 开发，包含 AutoConfiguration、spring.factories、optional 依赖、条件装配 |
| 必须叠加 Rules | `asset-security-platform-context.mdc`、`starter-dev-strict.mdc`、`maven-dependency-strict.mdc`、`java-hard-ban.mdc`、`test-required-strict.mdc`、`security-hard-ban.mdc` |
| 组合关系 | 与 `esmp-rd-standards` 必然叠加；涉及业务服务接入时叠加 `esmp-backend-dev` |
| 禁止事项 | Starter 不依赖业务服务；不写具体业务流程；不开关即启动后台线程；不启动即连接外部中间件；不吞初始化异常 |
| 验收方式 | 标准包结构、`enabled` 开关、条件装配、optional 依赖、最小单测、`mvn test` / `mvn compile` |

### 3.4 `esmp-bugfix-dev`

| 项目 | 内容 |
|------|------|
| 层级 | asset-security 产品线级 |
| 职责 | ESMP Bugfix：复现、根因分析、最小修复、回归验证 |
| 必须叠加 Rules | `esmp-rd-standards` + bug 涉及代码类型对应 Rules |
| 组合关系 | 后端 bug 叠加 `esmp-backend-dev`；前端 bug 叠加 `esmp-frontend-dev`；Starter bug 叠加 `esmp-starter-dev` |
| 禁止事项 | 禁止未定位根因就大范围重构；禁止删除异常逻辑让编译通过；禁止吞异常掩盖问题；禁止无验证宣称修复 |
| 验收方式 | 根因分析、最小改动、回归测试、编译/单测/专项 verify 命令 |

### 3.5 `prd-to-multi-agent`

| 项目 | 内容 |
|------|------|
| 层级 | asset-security 产品线级 |
| 职责 | 将 PRD / 落地方案拆分为 multi-agent 任务矩阵和可执行 Prompt |
| 必须叠加 Rules | `esmp-rd-standards` + 任务涉及的后端、前端、Starter、项目级 Rules |
| 组合关系 | 通常为 `auto-dev-orchestrator` 的前置拆分能力 |
| 禁止事项 | 禁止整份 PRD 丢给单 Agent；禁止省略 `deny_paths`；禁止跳过 Integration wave |
| 验收方式 | feature yaml 完整，shared_reads 包含基础规范和专项 Rules，Wave 切分合理，generate 脚本成功 |

## 4. 项目级 Skills

当前不建议新增大量项目级 Skill。项目级差异优先通过 Rule、feature yaml、落地方案表达。

后续仅当某个项目长期复杂、且形成稳定流程时，再考虑新增：

| 候选 Skill | 新增条件 |
|------------|----------|
| `open-api-service-dev` | open-api-service 长期存在大量专属开发流程，Rule 已不足以表达 |
| `platform-admin-dev` | platform-admin 服务成型，管理域开发流程稳定 |
| `asset-openplatform-dev` | 开放平台前端长期有稳定页面模式和联调流程 |

## 5. Skill 组合图

```text
auto-dev-orchestrator
├─ prd-to-multi-agent
├─ esmp-rd-standards
├─ esmp-backend-dev
│  ├─ backend-framework-context
│  ├─ asset-security-platform-context
│  ├─ java-hard-ban
│  ├─ backend-layer-boundary-strict
│  ├─ test-required-strict
│  └─ security-hard-ban
├─ esmp-frontend-dev
│  ├─ frontend-framework-context
│  └─ asset-openplatform-utf8（按路径）
├─ esmp-starter-dev
│  ├─ asset-security-platform-context
│  ├─ starter-dev-strict
│  └─ maven-dependency-strict
├─ esmp-bugfix-dev
└─ esmp-code-review-strict
```

## 6. 新增 / 修改 Skill 的维护要求

1. 真实文件只放 `.cursor/skills/<name>/`。
2. `.claude/skills/<name>/` 只建 junction。
3. 新增 Skill 必须在 `CLAUDE.md` 登记。
4. Skill 必须声明：层级、职责、必读规则、禁止事项、验收方式。
5. Skill 不能复制大量 Rule 正文，只引用 Rule 路径，避免分叉。
