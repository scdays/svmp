# Multi-Agent 执行 Prompts

> **自动生成**：`2026-05-26` · 源文件 [`features/open-platform-admin-p1.yaml`](../../features/open-platform-admin-p1.yaml)  
> **功能**：开放平台集成管理后台 P1（`OP-ADMIN-P1` / P1）  
> **工作流**：[prd-to-multi-agent-工作流](../../08-工具与指南/prd-to-multi-agent-工作流.md)  
> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py

---

## 0. 功能概览

| 项 | 值 |
|----|-----|
| 功能 ID | `OP-ADMIN-P1` |
| 名称 | 开放平台集成管理后台 P1 |
| 阶段 | P1 |
| 落地方案 | `svmp/docs/internal/开放平台集成管理-完整落地方案.md` |
| 页面设计 | `svmp/docs/internal/开放平台集成管理后台-页面设计.md` |

---

## 1. 全局必读

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/internal/开放平台集成管理后台-页面设计.md
- .cursor/skills/esmp-frontend-dev/SKILL.md
- .cursor/skills/esmp-backend-dev/SKILL.md

---

## 2. 交付门禁（Integration 核对）

- 后端提供 GET /internal/admin/invocations，支持分页与筛选
- 后端提供 GET /internal/admin/partners/{partnerId}/stats
- 前端新增 InvocationList 页面并支持筛选与分页
- PartnerDetail 新增统计 Tab 并接入 stats API
- 编译通过且联调数据与接口返回一致

---

## 3. Agent 索引

| Prompt | Agent | 依赖 |
|--------|-------|------|
| **K** | Backend-P1-Invocation | — |
| **L** | Frontend-P1-Invocation | — |
| **M** | Integration-P1 | K, L |

---

## 4. 各 Agent Prompt

## Prompt K — Backend-P1-Invocation

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/invocation/**
- open-api-service/**/partner/**
- open-api-service/**/ui/admin/**
- open-api-service/**/app/**
- open-api-service/**/domain/**
- open-api-service/**/infra/**
- open-api-service/**/db/**

**禁止路径**

- partner-gateway/**
- project_frontend/**

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/internal/开放平台集成管理后台-页面设计.md
- .cursor/skills/esmp-backend-dev/SKILL.md
- .cursor/rules/open-api-service-ddd.mdc

**必须交付**

- GET /internal/admin/invocations 查询能力（分页+筛选）
- GET /internal/admin/partners/{partnerId}/stats 接口
- DTO、应用服务、领域服务、仓储查询链路补齐

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile
- mvn -pl open-api-service compile -q

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 open-api-service · P1 调用治理后端负责人。

【只改】open-api-service 中 invocation 与 partner stats 相关代码。
【禁止】project_frontend、partner-gateway。

【目标】
1. 实现 GET /internal/admin/invocations（支持 partnerId、operationId、response_code、时间范围筛选与分页）
2. 实现 GET /internal/admin/partners/{partnerId}/stats（用于详情统计 Tab）
3. 严格遵循 DDD 调用链：Ui -> App -> Domain -> Repository

【要求】
- 响应结构与现有 admin 接口风格一致
- 仅做 P1 必需改动，不扩展到 P2/P3
- 补充必要 DTO 与查询对象，避免破坏现有 P0 接口

【交付】
- 改动文件清单
- 关键 API 示例返回
- 编译/校验命令结果
```

---

## Prompt L — Frontend-P1-Invocation

**负责人**：业务前端  

**工程**：`project_frontend/asset/asset-openplatform-manage`、`project_frontend/asset/asset-manage-master`

**可改路径**

- asset-openplatform-manage/**
- asset-manage-master/src/router/**
- asset-manage-master/public/conf/index.js
- asset-manage-master/src/main.js

**禁止路径**

- clover-front/**
- open-api-service/**
- partner-gateway/**

**必读**

- svmp/docs/internal/开放平台集成管理后台-页面设计.md
- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- .cursor/skills/esmp-frontend-dev/SKILL.md

**必须交付**

- src/api/openPlatform/invocation.js
- InvocationList.vue + 路由接入（/openPlatform/invocation）
- PartnerDetail 统计 Tab（对接 stats API）
- 必要样式对齐与交互态（loading/empty/error）

**验证**

- npm run lint
- npm run build
- /openPlatform/invocation 页面可访问

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 asset-openplatform-manage · P1 调用治理前端负责人。

【可改】
- project_frontend/asset/asset-openplatform-manage/
- asset-manage-master 仅 openPlatform 路由注册必要改动

【禁止】
- clover-front、open-api-service、partner-gateway

【目标】
1. 新增 API 调用记录页 InvocationList：筛选 + 分页 + 列表展示
2. 新增 invocation API 封装
3. PartnerDetail 增加统计 Tab，接入 /partners/{partnerId}/stats
4. 风格保持与现有 PartnerList/Ant Design Vue 一致

【约束】
- 统一使用 openApiRequest，沿用 code/data/message 处理模式
- 避免破坏已完成的 P0 页面与路由
- 仅交付 P1 页面，不扩展 P2/P3

【交付】
- 改动文件清单
- 构建结果
- 页面访问路径与手工验证步骤
```

---

## Prompt M — Integration-P1

**负责人**：联调验收  

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/internal/开放平台集成管理后台-页面设计.md

**必须交付**

- P1 验收清单结论
- 端到端联调记录

**验证**

- acceptance 列表逐项核对
- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt K, Prompt L  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Integration · P1 联调验收负责人。

基于 P1 验收标准逐项核对：
- invocation 列表 API 与前端页面一致
- partner stats API 与详情统计 Tab 一致
- 编译与基础校验通过

输出：
1. 通过项
2. 未通过项与阻塞原因
3. 修复建议（若有）
```

---

## 5. 并行执行建议

```text
Wave 1（可并行）: H, D, F
Wave 2（可并行）: I（依赖 H）, E（依赖 F）
Wave 3: G（依赖 I + D + F + E）
Wave 4（P1）: J（依赖 G）
```
