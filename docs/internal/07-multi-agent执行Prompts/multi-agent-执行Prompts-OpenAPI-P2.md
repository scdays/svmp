# Multi-Agent 执行 Prompts

> **自动生成**：`2026-06-13` · 源文件 [`features/open-platform-openapi-p2.yaml`](./features/open-platform-openapi-p2.yaml)  
> **功能**：开放平台对外 REST 执行面 P2（`OP-OPENAPI-P2` / P2）  
> **工作流**：[prd-to-multi-agent-工作流](./prd-to-multi-agent-工作流.md)  
> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py

---

## 0. 功能概览

| 项 | 值 |
|----|-----|
| 功能 ID | `OP-OPENAPI-P2` |
| 名称 | 开放平台对外 REST 执行面 P2 |
| 阶段 | P2 |
| 落地方案 | `svmp/docs/internal/开放平台对外REST执行面-分期落地方案.md` |

---

## 1. 全局必读

- svmp/docs/internal/开放平台对外REST执行面-分期落地方案.md
- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- svmp/docs/external/网络安全漏洞管理平台 · API 接口文档V1.0.4.md
- svmp/openapi/v1/openapi.yaml
- .cursor/skills/esmp-backend-dev/SKILL.md
- .cursor/rules/open-api-service-ddd.mdc

---

## 2. 交付门禁（Integration 核对）

- GET /exports/{exportId}、/download、/tasks/{taskId}/exports 与 §5.6 一致
- TaskExport 聚合结构符合 §5.6.3（非原始 XML 透传）
- exportStage 支持 TASK_COMPLETED / VERIFY_SCAN / VERIFY_FIX_SCAN
- EXPORT_READY Webhook 触发且 webhook_delivery_log 有记录
- Partner 无法下载他人 exportId → 40003
- partner-gateway EXPORT_READ capability 校验通过

---

## 3. Agent 索引

| Prompt | Agent | 依赖 |
|--------|-------|------|
| **AA** | Mapping-P2-Export-Freeze | — |
| **AB** | Backend-P2-Export-Read | AA |
| **AC** | Backend-P2-TaskExport-Assembler | AB |
| **AD** | Backend-P2-Export-Webhook | AC |
| **AE** | Gateway-P2-Export-Capability | AB |
| **AF** | Integration-P2-OpenAPI | AB, AC, AD, AE |

---

## 4. 各 Agent Prompt

## Prompt AA — Mapping-P2-Export-Freeze

**负责人**：架构/联调  

**工程**：`project_backend/svmp`

**可改路径**

- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- vul-pass/**/export/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- svmp/openapi/v1/openapi.yaml

**必须交付**

- 映射表 §4 外发域全部确认
- §6 决策记录第 4 项（外发存储）结论

**验证**

- §4 无 🟡 阻塞 P2 编码

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent AA · P2 外发映射冻结负责人。

【目标】冻结 §4 外发三接口与 vul-pass/文件存储关系；确认 TaskExport 数据来源。
```

---

## Prompt AB — Backend-P2-Export-Read

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/export/**
- open-api-service/**/ui/open/**
- open-api-service/**/domain/export/**
- open-api-service/**/infra/**
- open-api-service/**/db/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- svmp/openapi/v1/openapi.yaml

**必须交付**

- OpenExportUI 三接口
- open_export 表（若尚未存在则 Liquibase）
- InvocationPipeline + Partner 隔离

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt AA  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent AB · 外发读接口负责人。

【目标】§5.6 三 GET 接口；metadata + download 流 + 任务下列表。
```

---

## Prompt AC — Backend-P2-TaskExport-Assembler

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/export/**
- open-api-service/**/domain/export/**
- open-api-service/**/infra/adapter/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/docs/external/网络安全漏洞管理平台 · API 接口文档V1.0.4.md

**必须交付**

- TaskExport 组装器（targets/liveProbeResults/vulnerabilities）
- exportStage 枚举与触发点挂钩（任务完成/验证复扫/核验复扫）

**验证**

- 样例 export 与 §5.6.3 JSON 结构一致

**依赖**：Prompt AB  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent AC · TaskExport 组装负责人。

【目标】从 vul-pass/扫描结果聚合 TaskExport；download 返回 xml/json。
```

---

## Prompt AD — Backend-P2-Export-Webhook

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/webhook/**
- open-api-service/**/domain/webhook/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/docs/internal/开放平台对外REST执行面-分期落地方案.md

**必须交付**

- EXPORT_READY 出站事件（复用 P1 Webhook 引擎）

**验证**

- 外发就绪后 delivery_log eventType=EXPORT_READY

**依赖**：Prompt AC  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent AD · EXPORT_READY Webhook 负责人。

【依赖】P1 Webhook 出站引擎（Agent V）；外发组装完成时触发。
```

---

## Prompt AE — Gateway-P2-Export-Capability

**负责人**：网关  

**工程**：`project_backend/svmp/partner-gateway`

**可改路径**

- partner-gateway/**

**禁止路径**

- open-api-service/**

**必须交付**

- /exports/* 路径 EXPORT_READ capability

**验证**

- 无 EXPORT_READ → 40301

**依赖**：Prompt AB  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent AE · gateway 外发 capability 负责人。
```

---

## Prompt AF — Integration-P2-OpenAPI

**负责人**：联调验收  

**可改路径**

- svmp/docs/internal/**

**必读**

- svmp/docs/internal/开放平台对外REST执行面-分期落地方案.md

**必须交付**

- 联调手册-P2-OpenAPI.md
- acceptance 逐项结论

**验证**

- acceptance 全部通过

**依赖**：Prompt AB, Prompt AC, Prompt AD, Prompt AE  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent AF · OP-OPENAPI-P2 联调验收负责人。

【产出】联调手册-P2-OpenAPI.md：任务完成 → list exports → get → download → EXPORT_READY Webhook。
```

---

## 5. 并行执行建议

```text
Wave 1（可并行）: H, D, F
Wave 2（可并行）: I（依赖 H）, E（依赖 F）
Wave 3: G（依赖 I + D + F + E）
Wave 4（P1）: J（依赖 G）
```
