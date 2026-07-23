# Multi-Agent 执行 Prompts

> **自动生成**：`2026-05-26` · 源文件 [`features/open-platform-admin-p0.yaml`](../../features/open-platform-admin-p0.yaml)  
> **功能**：开放平台集成管理后台 P0（`OP-ADMIN-P0` / P0）  
> **工作流**：[prd-to-multi-agent-工作流](../../08-工具与指南/prd-to-multi-agent-工作流.md)  
> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py

---

## 0. 功能概览

| 项 | 值 |
|----|-----|
| 功能 ID | `OP-ADMIN-P0` |
| 名称 | 开放平台集成管理后台 P0 |
| 阶段 | P0 |
| 落地方案 | `svmp/docs/internal/开放平台集成管理-完整落地方案.md` |
| 页面设计 | `svmp/docs/internal/开放平台集成管理后台-页面设计.md` |

---

## 1. 全局必读

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/external/开放平台API接口规范.md
- project_frontend/asset/docs/micro-app-scaffold.md

---

## 2. 交付门禁（Integration 核对）

- 运营：创建 Partner → 勾选能力 → 生成凭证 → 复制接入包
- 第三方：POST /oauth/token → POST /api/open/v1/tasks → api_invocation 有记录
- 访问 /openPlatform/partner qiankun 子应用正常挂载
- node project_frontend/asset/scripts/check-micro-app.js --app asset-openplatform-manage 无 FAIL
- 两家 Partner 任务数据互不可见；无 capability 返回 40301

---

## 3. Agent 索引

| Prompt | Agent | 依赖 |
|--------|-------|------|
| **H** | Doc-Design | — |
| **I** | Frontend-P0 | H |
| **D** | Backend-Admin | — |
| **F** | Backend-OpenAPI | — |
| **E** | Gateway | F |
| **G** | Integration | I, D, F, E |
| **J** | P1-Invocation | G |

---

## 4. 各 Agent Prompt

## Prompt H — Doc-Design

**负责人**：PM / 架构  

**工程**：`svmp/docs`

**可改路径**

- svmp/docs/internal/**

**禁止路径**

- project_backend/**
- project_frontend/**

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md

**必须交付**

- 页面设计文档 §4 P0 字段与交互完整
- 路由与菜单配置说明

**验证**

- 页面清单与 API 映射表无 TODO

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Doc-Design · 开放平台集成管理文档负责人。

【只改】svmp/docs/internal/ 下页面设计、组件映射类文档。
【禁止】写业务代码。

【目标】细化页面设计 §4 P0：字段、校验、空状态、错误提示、路由表。
【交付】更新后的 markdown + 变更摘要
```

---

## Prompt I — Frontend-P0

**负责人**：业务前端  

**工程**：`project_frontend/asset/asset-openplatform-manage`、`project_frontend/asset/asset-manage-master`

**可改路径**

- asset-openplatform-manage/**
- asset-manage-master/src/main.js
- asset-manage-master/public/conf/index.js
- asset-manage-master/src/router/micro-app-fallback-routes.js
- asset-manage-master/src/router/generator-routers.js
- asset-manage-master/vue.config.js

**禁止路径**

- clover-front/**
- open-api-service/**
- partner-gateway/**

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/internal/开放平台集成管理后台-页面设计.md
- svmp/docs/external/开放平台API接口规范.md
- project_frontend/asset/docs/micro-app-scaffold.md
- .cursor/skills/esmp-frontend-dev/SKILL.md
- project_frontend/asset/asset-other-manage/src/views/system/userManage/UserInfoList.vue
- project_frontend/asset/asset-openplatform-manage/src/main.js

**必须交付**

- 完整子应用脚手架（openPlatform / 13021 / activeRule /openPlatform）
- openApiRequest.js + partner.js + openPlatformCapabilities.js
- PartnerList / PartnerForm / PartnerDetail / CredentialCreateModal / OnboardingPanel
- asset-manage-master qiankun 注册 + conf URL
- Admin Key 缺失时的全局 Alert

**验证**

- npm run lint
- node project_frontend/asset/scripts/check-micro-app.js --app asset-openplatform-manage --route /openPlatform --name openPlatform --container child_openPlatform_container --conf VUE_APP_API_OPENPLATFORM_URL
- http://localhost:13001/openPlatform/partner 可访问且列表 API 200

**依赖**：Prompt H  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 asset-openplatform-manage · 开放平台集成管理 P0 前端负责人。

【可改】
- project_frontend/asset/asset-openplatform-manage/
- asset-manage-master/src/main.js 与 public/conf/index.js（仅 openPlatform 注册）

【禁止改】clover-front、partner-gateway、open-api-service。

【必读】见任务矩阵 reads 列表；UI 对齐 UserInfoList；qiankun mount/container 对齐 asset-openplatform-manage（§3.5 落地方案）。

【必须交付】
1. 子应用脚手架 + 路由 §5.1（子应用 path 为 /partner，浏览器为 /openPlatform/partner）
2. openApiRequest（X-Internal-Admin-Key + qiankun baseURL）+ partner API 封装
3. P0 五页：List / Form / Detail / CredentialModal / OnboardingPanel
4. master 注册 + conf entry（:13021，禁止指 master 自身）+ fallback route
5. Admin Key 缺失 Alert；能力码 openPlatformCapabilities.js

【约束】
- Vue.use(VueRouter)；mount 保留 props.container；App.vue 勿用 :key="$route.fullPath"
- 管理 API 走平台网关/内网，禁止 dev proxy 到 partner-gateway
- 响应 { code, data, message }，code≠0 → notification.error
- clientSecret 仅展示一次；接入说明折叠面板对齐规范 §2.1、§2.3

【交付物】文件列表 + lint + check-micro-app.js 通过 + .env.development.local 说明（勿提交密钥）
```

---

## Prompt D — Backend-Admin

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/partner/**

**禁止路径**

- partner-gateway/**
- project_frontend/**

**必读**

- .cursor/skills/esmp-backend-dev/SKILL.md
- .cursor/rules/open-api-service-ddd.mdc
- svmp/docs/internal/开放平台集成管理-完整落地方案.md

**必须交付**

- listPartners → { items, total, page, size }
- PartnerSummaryDto + partnerType、capabilities、rateLimitQps

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile
- 顶层包仅 app/domain/infra/ui；调用链 Ui → App → Domain → Repository
- mvn -pl open-api-service compile -q

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 open-api-service · Partner 管理面 P0 后端负责人。

【只改】open-api-service Partner 管理相关（ui/admin、app、domain/partner、infra）。
【禁止】gateway、前端、tasks 开放 API（除非一并指派 F）。
【DDD】必读 .cursor/skills/esmp-backend-dev/SKILL.md；禁止 common/web/handler 等顶层包。

【目标】
- 使用已有 countPartners() 包装 PartnerPageDto
- Summary 字段：partnerId, partnerName, partnerType, status, rateLimitQps, capabilities

【交付】改动文件 + verify-open-api-ddd.ps1 -Compile + curl 示例
```

---

## Prompt F — Backend-OpenAPI

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/task/**
- open-api-service/**/open/**
- open-api-service/**/invocation/**
- open-api-service/**/db/**

**禁止路径**

- partner-gateway/**
- project_frontend/**

**必读**

- svmp/openapi/v1/openapi.yaml
- svmp/docs/external/开放平台API接口规范.md
- .cursor/skills/esmp-backend-dev/SKILL.md
- .cursor/rules/open-api-service-ddd.mdc

**必须交付**

- POST/GET /api/open/v1/tasks（Partner 隔离）
- api_invocation 表写入；requestId 全链路一致

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile
- 两家 Partner 互不可见
- POST /tasks 有 invocation 记录
- 无 capability → 40301

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 open-api-service · 开放 API 执行面 P0 负责人。

【只改】tasks + open 治理 + api_invocation + 相关 Liquibase。
【对齐】openapi.yaml、external 规范 §5、落地方案 §6.3 P0 行。
【DDD】Ui → App → Domain；Filter/Adapter 在 infra/；验收脚本 verify-open-api-ddd.ps1

【交付】文件清单 + verify 命令 + P1 backlog
```

---

## Prompt E — Gateway

**负责人**：业务后端  

**工程**：`project_backend/svmp/partner-gateway`

**可改路径**

- partner-gateway/**

**禁止路径**

- open-api-service/**
- project_frontend/**

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md

**必须交付**

- 公网 /oauth/token、/api/open/v1/* 路由
- /internal/** → 40101
- 能力码鉴权、限流、X-Partner-Id 注入

**验证**

- curl 经 gateway 通 token 与 tasks

**依赖**：Prompt F  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 partner-gateway · P0 网关负责人。只改 partner-gateway。
目标见落地方案 §6.4；Token 读 Redis，不签发；/internal 不暴露。
交付：改动清单 + curl 联调步骤。
```

---

## Prompt G — Integration

**负责人**：联调  

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md

**必须交付**

- P0 评审表 §9.2 全部通过
- 联调报告

**验证**

- acceptance 列表全部满足
- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt I, Prompt D, Prompt F, Prompt E  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Integration · P0 联调负责人。按落地方案 §9.2 评审表逐项验证。
阻塞 bug 单独记录并指派对应 Agent；通过则输出联调报告。
```

---

## Prompt J — P1-Invocation

**负责人**：全栈  
**阶段说明**：P1 — 非 P0 冲刺，依赖 P0 交付完成  

**工程**：`project_frontend/asset/asset-openplatform-manage`、`project_backend/svmp/open-api-service`

**可改路径**

- asset-openplatform-manage/**/invocation/**
- open-api-service/**/invocation/**

**禁止路径**

- partner-gateway/**

**必读**

- svmp/docs/internal/开放平台集成管理后台-页面设计.md

**必须交付**

- GET /internal/admin/invocations + InvocationList 页
- Partner 详情统计 Tab

**验证**

- 列表与 DB 一致

**依赖**：Prompt G  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 P1 · 调用治理负责人。后端 invocation API + 前端 InvocationList 并行。
见页面设计 P1 章节与落地方案 §7.2 P1。
```

---

## 5. 并行执行建议

```text
Wave 1（可并行）: H, D, F
Wave 2（可并行）: I（依赖 H）, E（依赖 F）
Wave 3: G（依赖 I + D + F + E）
Wave 4（P1）: J（依赖 G）
```
