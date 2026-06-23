# Multi-Agent 执行 Prompts

> **自动生成**：`2026-05-26` · 源文件 [`features/open-platform-admin-p2.yaml`](./features/open-platform-admin-p2.yaml)  
> **功能**：开放平台集成管理后台 P2（`OP-ADMIN-P2` / P2）  
> **工作流**：[prd-to-multi-agent-工作流](./prd-to-multi-agent-工作流.md)  
> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py

---

## 0. 功能概览

| 项 | 值 |
|----|-----|
| 功能 ID | `OP-ADMIN-P2` |
| 名称 | 开放平台集成管理后台 P2 |
| 阶段 | P2 |
| 落地方案 | `svmp/docs/internal/开放平台集成管理-完整落地方案.md` |
| 页面设计 | `svmp/docs/internal/开放平台集成管理后台-页面设计.md` |

---

## 1. 全局必读

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/internal/开放平台集成管理后台-页面设计.md
- svmp/openapi/v1/openapi.yaml
- .cursor/skills/esmp-frontend-dev/SKILL.md
- .cursor/skills/esmp-backend-dev/SKILL.md

---

## 2. 交付门禁（Integration 核对）

- API 目录页可展示 api_operation 清单，并支持基础筛选（能力码/状态/tag）
- 开发者文档页可查看外部规范并提供 openapi.yaml 入口（只读）
- 配额与限流页可展示 Partner 维度用量与限流相关统计
- 页面路由可访问：/openPlatform/api-catalog、/openPlatform/developer-doc、/openPlatform/quota
- 前端 build 通过、后端编译与 DDD 校验通过（若后端有改动）

---

## 3. Agent 索引

| Prompt | Agent | 依赖 |
|--------|-------|------|
| **N** | Backend-P2-ReadModel | — |
| **O** | Frontend-P2-Pages | — |
| **P** | Integration-P2 | N, O |

---

## 4. 各 Agent Prompt

## Prompt N — Backend-P2-ReadModel

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/ui/admin/**
- open-api-service/**/app/**
- open-api-service/**/domain/open/**
- open-api-service/**/infra/**
- open-api-service/**/ui/dto/admin/**

**禁止路径**

- partner-gateway/**
- project_frontend/**

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/internal/开放平台集成管理后台-页面设计.md
- .cursor/skills/esmp-backend-dev/SKILL.md

**必须交付**

- API 目录只读查询接口（基于 api_operation）
- 配额与限流读取接口（Partner 维度）
- DTO/分页/筛选参数与管理 API 风格统一

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile
- mvn -pl open-api-service compile -q 或模块内 mvn compile -q

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 open-api-service · P2 读模型后端负责人。

【只改】open-api-service。
【禁止】project_frontend、partner-gateway。

【目标】
1. 提供 API 目录只读管理接口（数据源 api_operation，支持筛选）
2. 提供配额与限流页面所需只读接口（Partner 维度限流/调用统计）
3. 保持 DDD 分层：Ui -> App -> Domain -> Repository

【约束】
- 仅实现 P2 页面必须接口，不扩展 P3
- 返回结构与现有 /internal/admin 风格一致
- 如需新增 DTO/Query/PO 转换器，补全 ConvertHelper 所需 convertor

【交付】
- 改动文件列表
- 新增接口清单（路径、参数、返回示例）
- 校验与编译结果
```

---

## Prompt O — Frontend-P2-Pages

**负责人**：业务前端  

**工程**：`project_frontend/asset/asset-openplatform-manage`、`project_frontend/asset/asset-manage-master`

**可改路径**

- asset-openplatform-manage/**
- asset-manage-master/src/router/**
- asset-manage-master/src/main.js
- asset-manage-master/public/conf/index.js

**禁止路径**

- clover-front/**
- open-api-service/**
- partner-gateway/**

**必读**

- svmp/docs/internal/开放平台集成管理后台-页面设计.md
- svmp/docs/internal/prototypes/open-platform-admin-prototype.html
- .cursor/skills/esmp-frontend-dev/SKILL.md

**必须交付**

- API 目录页（只读）
- 开发者文档页
- 配额与限流页
- 三个页面对应 API 封装 + 子应用路由 + 主应用 fallback 路由
- 保持与现有 P0/P1 页面一致的紧凑布局风格

**验证**

- npm run build

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 asset-openplatform-manage · P2 前端负责人。

【可改】
- project_frontend/asset/asset-openplatform-manage/
- asset-manage-master 仅 openPlatform fallback 路由必要改动

【禁止】
- open-api-service、partner-gateway、clover-front

【目标】
1. 新增 API 目录（只读）页面，支持筛选与表格展示
2. 新增开发者文档页面，提供规范查看与 openapi.yaml 入口
3. 新增配额与限流页面，展示 Partner 维度统计
4. 与现有 PartnerList/InvocationList 的紧凑布局保持一致

【约束】
- 统一用 openApiRequest，沿用 code/data/message 处理
- 尽量按后端现有接口对接；若接口缺失，先做前端兼容兜底
- 不改 P0/P1 已有流程逻辑

【交付】
- 改动文件列表
- 页面访问路径
- 构建结果
```

---

## Prompt P — Integration-P2

**负责人**：联调验收  

**必读**

- svmp/docs/internal/开放平台集成管理-完整落地方案.md
- svmp/docs/internal/开放平台集成管理后台-页面设计.md

**必须交付**

- P2 验收结果（通过/阻塞）
- 联调证据与风险项

**验证**

- acceptance 清单逐项核对
- npm run build（前端）
- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile（后端）

**依赖**：Prompt N, Prompt O  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Integration · P2 联调验收负责人。

请对 P2 三个页面（API 目录、开发者文档、配额与限流）逐项验收：
- 路由可访问
- 数据展示与接口一致
- 只读能力符合要求
- 编译构建通过

输出：
1. 通过项
2. 未通过项与阻塞原因
3. 建议的最小修复项
```

---

## 5. 并行执行建议

```text
Wave 1（可并行）: H, D, F
Wave 2（可并行）: I（依赖 H）, E（依赖 F）
Wave 3: G（依赖 I + D + F + E）
Wave 4（P1）: J（依赖 G）
```
