# ESMP AI Rules & Skills 工程化治理方案

## 1. 背景与目标

当前仓库同时被 Cursor 与 Claude Code 使用，规则与 Skills 的唯一数据源已经收敛到 `.cursor/`：

- `.cursor/rules/*.mdc`：Cursor 规则，Claude Code 由 `CLAUDE.md` 约定触发。
- `.cursor/skills/<name>/SKILL.md`：标准 Skill 定义。
- `.claude/skills/<name>/`：指向 `.cursor/skills/<name>/` 的目录联接，不复制内容。

本方案用于把 Rules 与 Skills 从“按文件散落”升级为“三层治理模型”：

```text
公司级 Company
  └─ 研发流程、编码规范、安全红线、测试底线、AI Agent 工作方式

asset-security 产品线级 Product Line
  └─ ESMP / 资产安全平台技术栈、DDD 分层、微前端、Starter、平台架构决策

项目级 Project / Service / Feature
  └─ open-api-service、asset-openplatform-manage、platform-admin、具体 PRD / feature 约束
```

目标：

1. 每条 Rule 都能说明自己属于哪一层、约束什么、何时触发、是否强制。
2. 每个 Skill 都能说明自己负责什么流程、必须叠加哪些 Rule、如何验收。
3. 公司级规则不被下层覆盖，产品线级规则沉淀长期架构，项目级规则只补充具体服务/工程差异。
4. Cursor 与 Claude Code 继续共用 `.cursor/`，避免规则/技能分叉。

## 2. 三层治理模型

### 2.1 公司级

公司级规则只描述跨项目通用底线，不写具体服务名、表名、页面名。

典型内容：

- GitFlow、Commit 格式、GitLab 强制规约。
- Java / 前端编码质量底线。
- 安全红线、日志、异常、测试要求。
- AI Agent 自动开发流程的基本纪律。

代表 Skill / Rule：

| 类型 | 名称 | 定位 |
|------|------|------|
| Skill | `esmp-rd-standards` | 研发规范基础入口 |
| Skill | `auto-dev-orchestrator` | 自动开发总编排 |
| Skill | `esmp-code-review-strict` | 严格审查框架 |
| Rule | `java-hard-ban.mdc` | Java 通用硬禁止项 |
| Rule | `security-hard-ban.mdc` | 安全红线 |
| Rule | `test-required-strict.mdc` | 测试底线 |
| Rule | `maven-dependency-strict.mdc` | Maven 依赖硬约束 |

公司级原则：

1. 下层不得覆盖公司级强制规则。
2. 所有开发类 Skill 必须叠加 `esmp-rd-standards`。
3. 所有 Review 类 Skill 必须检查公司级强制规则。
4. 公司级规则可被产品线级、项目级补充，但不能被削弱。

### 2.2 asset-security 产品线级

产品线级规则描述 ESMP / 资产安全平台长期架构和工程模式。

典型内容：

- spore / esmp-starter / spore-base-ddd 后端模型。
- qiankun + Vue2 + Ant Design Vue 前端微前端模型。
- DDD 四层调用链：`*Ui → *AppServiceImpl → *DomainServiceImpl → *RepositoryImpl → Mapper/PO`。
- Starter 开发、自动配置、条件装配、optional 依赖。
- 资产安全平台 `platform-admin`、EventCenter、TaskCenter、EventBus starter 等长期架构决策。

代表 Skill / Rule：

| 类型 | 名称 | 定位 |
|------|------|------|
| Rule | `backend-framework-context.mdc` | ESMP 后端框架上下文 |
| Rule | `frontend-framework-context.mdc` | ESMP 前端微前端上下文 |
| Rule | `asset-security-platform-context.mdc` | 资产安全平台产品线架构上下文 |
| Rule | `backend-layer-boundary-strict.mdc` | DDD 分层边界 |
| Rule | `starter-dev-strict.mdc` | Starter 开发硬约束 |
| Skill | `esmp-backend-dev` | ESMP 后端开发模式 |
| Skill | `esmp-frontend-dev` | ESMP 前端开发模式 |
| Skill | `esmp-starter-dev` | 平台 Starter 开发模式 |
| Skill | `esmp-bugfix-dev` | ESMP Bugfix 流程 |
| Skill | `prd-to-multi-agent` | PRD / 落地方案拆分流程 |

产品线级原则：

1. 产品线级规则不得覆盖公司级红线。
2. 产品线级规则应描述长期稳定的架构模型，不承载单个 feature 的临时状态。
3. 产品线级 Skill 负责“怎么做”，Rule 负责“不能违反什么”。
4. asset-security 产品线级规则命名使用 `asset-security-*` 前缀。

### 2.3 项目级

项目级规则绑定具体仓库、服务、前端子应用或 feature。

典型内容：

- `open-api-service` 包结构、调用链、DTO 转换禁忌、验证脚本。
- `asset-openplatform-manage` UTF-8 防乱码与安全编辑流程。
- `platform-admin`、`partner-gateway` 等具体服务的边界补充。
- `svmp/docs/internal/features/*.yaml` 中的具体任务拆分、allow/deny、验收命令。

代表 Rule / 文档：

| 类型 | 名称 | 定位 |
|------|------|------|
| Rule | `open-api-service-ddd.mdc` | open-api-service 项目级 DDD 约束 |
| Rule | `asset-openplatform-utf8.mdc` | asset-openplatform-manage UTF-8 项目约束 |
| Doc | `svmp/docs/internal/features/*.yaml` | feature 任务矩阵 |
| Doc | `svmp/docs/internal/03-落地方案/*.md` | 具体落地方案 |

项目级原则：

1. 项目级规则只能收紧或补充上层规则，不能放宽上层红线。
2. 项目级规则应绑定明确路径或服务边界。
3. 临时 feature 状态优先放入 feature yaml / 落地方案，不沉淀为长期 Rule。
4. 如果某项目长期复杂，再评估是否新增项目级 Skill；默认先用 Rule 描述边界。

## 3. Rule 与 Skill 职责边界

### 3.1 Rule 负责“不能违反什么”

示例：

- 不能跨层调用。
- 不能硬编码密钥。
- 不能新增未声明 Maven 依赖。
- 不能破坏 UTF-8。
- 不能绕过 `request` / `ajaxInterface`。
- 不能把 EventBus runtime 放进 `platform-admin`。
- 不能把资产安全 EventBus starter 放进既有 `esmp-starters`。

### 3.2 Skill 负责“怎么完成任务”

示例：

- 怎么做后端功能。
- 怎么做前端页面。
- 怎么做 Starter。
- 怎么修 Bug。
- 怎么拆 PRD。
- 怎么做 Code Review。
- 怎么自动编排多 Agent。

### 3.3 CLAUDE.md 负责“启动时加载什么”

`CLAUDE.md` 不承载大量细节，只做：

1. `.cursor/` 唯一数据源说明。
2. alwaysApply rules 索引。
3. 按文件类型触发 rules 索引。
4. 可用 skills 索引。
5. 新增 skill 的 junction 维护说明。

## 4. 当前治理结论

### 4.1 保留

这些规则职责清晰，应保留：

- `auto-dev-orchestrator.mdc`
- `backend-framework-context.mdc`
- `frontend-framework-context.mdc`
- `asset-security-platform-context.mdc`
- `java-hard-ban.mdc`
- `security-hard-ban.mdc`
- `maven-dependency-strict.mdc`
- `test-required-strict.mdc`
- `starter-dev-strict.mdc`
- `open-api-service-ddd.mdc`
- `asset-openplatform-utf8.mdc`

### 4.2 暂缓合并

以下规则存在职责相近现象，但第一阶段不重命名、不删除，避免破坏 Cursor 触发：

- `backend-ddd-layers.mdc`
- `backend-naming.mdc`
- `backend-ui-api.mdc`
- `backend-starter-usage.mdc`

后续可考虑：

- 将 DDD 职责、命名、UI API 逐步归并进 `backend-layer-boundary-strict.mdc`。
- 将 starter 选用指引逐步归并进 `maven-dependency-strict.mdc` 或保留为轻量说明。

## 5. 新增 Rule / Skill 标准流程

### 5.1 新增 Rule

1. 判断层级：公司级 / asset-security 产品线级 / 项目级。
2. 判断是否长期有效：临时 feature 状态不要写成 Rule。
3. 命名：
   - 公司级：表达通用红线或流程。
   - 产品线级：asset-security 产品线规则使用 `asset-security-*` 前缀。
   - 项目级：明确项目或服务名。
4. frontmatter 至少包含：

```yaml
---
description: 一句话说明
alwaysApply: true|false
globs: path/**/*.ext
---
```

5. 更新 `CLAUDE.md` 索引。
6. 如被 Skill 使用，更新对应 Skill 的必读规则清单。

### 5.2 新增 Skill

1. 先在 `.cursor/skills/<name>/SKILL.md` 创建真实文件。
2. 不在 `.claude/skills/` 复制内容。
3. 创建 junction：

```powershell
powershell.exe -NoProfile -Command "New-Item -ItemType Junction -Path 'D:/ai_project_workspace/3.0/.claude/skills/<NAME>' -Target 'D:/ai_project_workspace/3.0/.cursor/skills/<NAME>'"
```

4. 更新 `CLAUDE.md` 的 Skill 索引。
5. 明确该 Skill 的层级、职责、必读 Rules、禁止事项和验收方式。

## 6. Agent 使用示例

### 6.1 后端功能开发

```text
公司级：esmp-rd-standards
asset-security 产品线级：backend-framework-context + esmp-backend-dev + DDD/Java/安全/测试 Rules
项目级：目标服务专属 Rule，如 open-api-service-ddd
```

### 6.2 Starter 开发

```text
公司级：esmp-rd-standards + Maven/安全/测试底线
asset-security 产品线级：esmp-starter-dev + starter-dev-strict + asset-security-platform-context
项目级：具体 starter 模块设计文档 / feature yaml
```

### 6.3 开放平台前端开发

```text
公司级：esmp-rd-standards
asset-security 产品线级：frontend-framework-context + esmp-frontend-dev
项目级：asset-openplatform-utf8 + 页面设计文档
```

## 7. 后续演进路线

1. 第一阶段：文档化三层模型，新增 `asset-security-platform-context.mdc`，最小更新 `CLAUDE.md`。
2. 第二阶段：逐步给现有 Rule frontmatter 补充逻辑层级元数据，但不影响 Cursor 使用。
3. 第三阶段：评估是否合并后端 DDD 相关重复规则。
4. 第四阶段：当 `platform-admin`、`partner-gateway` 等服务成型后，再补项目级服务规则。
