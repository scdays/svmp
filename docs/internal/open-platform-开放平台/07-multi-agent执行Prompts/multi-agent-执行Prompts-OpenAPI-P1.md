# Multi-Agent 执行 Prompts

> **自动生成**：`2026-06-13` · 源文件 [`features/open-platform-openapi-p1.yaml`](../../features/open-platform-openapi-p1.yaml)  
> **功能**：开放平台对外 REST 执行面 P1（`OP-OPENAPI-P1` / P1）  
> **工作流**：[prd-to-multi-agent-工作流](../../08-工具与指南/prd-to-multi-agent-工作流.md)  
> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py

---

## 0. 功能概览

| 项 | 值 |
|----|-----|
| 功能 ID | `OP-OPENAPI-P1` |
| 名称 | 开放平台对外 REST 执行面 P1 |
| 阶段 | P1 |
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

- POST /instances/search、GET /instances/{vulInfoID} 与 openapi §5.2 一致，跨 Partner 返回 40003
- POST verify/remediate/verify-fix 单条与 §5.3–5.5 一致，状态机错误码 40002/40005
- 三个 :batch 返回 success[] + failed[]，符合 §4.2 幂等
- Webhook 出站投递写入 webhook_delivery_log，TASK_COMPLETED / INSTANCE_STATUS_CHANGED 可触发
- partner-gateway 端到端 curl 通过（含 capability INSTANCE_*）
- powershell verify-open-api-ddd.ps1 -Compile 通过

---

## 3. Agent 索引

| Prompt | Agent | 依赖 |
|--------|-------|------|
| **R** | Mapping-Freeze-vul-pass | — |
| **S** | Backend-P1-Instance-Read | R |
| **T** | Backend-P1-Instance-Write-Single | S |
| **U** | Backend-P1-Instance-Write-Batch | T |
| **V** | Backend-P1-Webhook-Outbound | T |
| **W** | Gateway-P1-Instance-Capability | S |
| **X** | Frontend-P1-InvocationDetail-Optional | — |
| **Y** | Integration-P1-OpenAPI | S, T, U, V, W |

---

## 4. 各 Agent Prompt

## Prompt R — Mapping-Freeze-vul-pass

**负责人**：架构/联调  

**工程**：`project_backend/svmp`

**可改路径**

- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- vul-pass/**/controller/**
- open-api-service/**/infra/adapter/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- svmp/openapi/v1/openapi.yaml
- project_backend/svmp/vul-pass

**必须交付**

- 映射表 §3 全部 🟡 改为 ✅ 或明确废弃路径
- §6 决策记录 4 项填写结论
- 实码引用（Controller 类名 + 方法签名）

**验证**

- 映射表无「待确认」阻塞 P1-a 编码

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent R · vul-pass 映射冻结负责人。

【只改】`Open API与vul-pass内部接口映射表.md`（可只读 vul-pass 源码核对）。
【禁止】直接写 Partner REST Controller（留给 S/T/U）。

【目标】
1. 对照 vul-pass 实码，冻结实例读/写 8 接口的 Feign 路径与字段映射
2. 填写 §6 决策记录（PUT sub-system 与否、vulInfoID 主键、异步复扫、外发存储占位）
3. 标注每条映射的 vul-pass Controller#method 引用

【交付】
- 更新后的映射表 diff 摘要
- 仍不确定项清单（应为空或仅 P2 外发）
```

---

## Prompt S — Backend-P1-Instance-Read

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`、`project_backend/svmp/partner-gateway`

**可改路径**

- open-api-service/**/instance/**
- open-api-service/**/ui/open/**
- open-api-service/**/ui/dto/open/**
- open-api-service/**/app/**
- open-api-service/**/domain/instance/**
- open-api-service/**/infra/adapter/**
- open-api-service/**/db/**
- partner-gateway/**/capability/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- svmp/openapi/v1/openapi.yaml
- .cursor/rules/open-api-service-ddd.mdc

**必须交付**

- OpenInstanceUI：POST /instances/search、GET /instances/{vulInfoID}
- IVulnInstanceGateway + vul-pass 适配
- api_operation seed searchInstances/getInstance
- InvocationPipeline 接入 + Partner 隔离

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt R  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 open-api-service · P1 实例读负责人（Agent S）。

【依赖】Agent R 已冻结映射表 §3.1。
【只改】open-api-service、partner-gateway capability（INSTANCE_READ）。
【禁止】project_frontend、实例写接口。

【目标】
1. 实现 POST /instances/search、GET /instances/{vulInfoID}
2. 统一 InvocationPipeline；resourceId=vulInfoID
3. 跨 Partner 访问 → 40003

【交付】改动清单 + curl 示例 + 编译结果
```

---

## Prompt T — Backend-P1-Instance-Write-Single

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/instance/**
- open-api-service/**/ui/open/**
- open-api-service/**/domain/instance/**
- open-api-service/**/infra/adapter/**

**禁止路径**

- project_frontend/**
- partner-gateway/**

**必读**

- svmp/docs/internal/Open API与vul-pass内部接口映射表.md
- svmp/openapi/v1/openapi.yaml

**必须交付**

- verifyInstance / remediateInstance / verifyFixInstance 单条三接口
- Domain 状态机校验（40002/40005）
- api_invocation 写记录

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt S  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent T · 实例写单条负责人。

【依赖】Agent S 实例读与 open_vuln_instance 归属已就绪。
【目标】实现 §5.3–5.5 单条 verify/remediate/verify-fix。
【约束】Partner DTO 仅 ui/dto/open；调 vul-pass 走映射表 adapter。
```

---

## Prompt U — Backend-P1-Instance-Write-Batch

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/instance/**
- open-api-service/**/domain/instance/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/openapi/v1/openapi.yaml

**必须交付**

- verifyInstanceBatch / remediateInstanceBatch / verifyFixInstanceBatch
- success[] + failed[] 聚合，单条逻辑复用 T

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt T  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent U · 实例批量写负责人。

【目标】三个 :batch 接口；复用 T 的 Domain 单条逻辑；符合 §4.2 幂等语义。
```

---

## Prompt V — Backend-P1-Webhook-Outbound

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/webhook/**
- open-api-service/**/domain/webhook/**
- open-api-service/**/infra/**/webhook/**

**禁止路径**

- project_frontend/**

**必读**

- svmp/docs/internal/开放平台对外REST执行面-分期落地方案.md
- svmp/docs/external/网络安全漏洞管理平台 · API 接口文档V1.0.4.md

**必须交付**

- Webhook 出站投递（TASK_COMPLETED、INSTANCE_STATUS_CHANGED）
- webhook_delivery_log 写入
- 失败重试策略（至少指数退避 + 最大次数）

**验证**

- 任务 FINISHED 或实例写成功后 delivery_log 有记录

**依赖**：Prompt T  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent V · Webhook 出站负责人。

【目标】§6 Webhook 出站；非 Partner REST。
【触发】任务完成、实例状态变更；POST Partner defaultCallbackUrl。
【落库】webhook_delivery_log（与 admin 查询对齐）。
```

---

## Prompt W — Gateway-P1-Instance-Capability

**负责人**：网关  

**工程**：`project_backend/svmp/partner-gateway`

**可改路径**

- partner-gateway/**

**禁止路径**

- open-api-service/**
- project_frontend/**

**必读**

- svmp/openapi/v1/openapi.yaml

**必须交付**

- PartnerCapabilityMatcher 补全 instances 8 路径
- INSTANCE_VERIFY / REMEDIATE / VERIFY_FIX capability 映射

**验证**

- 无 capability 时 40301

**依赖**：Prompt S  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent W · partner-gateway 能力码负责人。

【目标】instances 相关路径与 capability 与 openapi 一致；可与 S 并行。
```

---

## Prompt X — Frontend-P1-InvocationDetail-Optional

**负责人**：业务前端  

**工程**：`project_frontend/asset/asset-openplatform-manage`

**可改路径**

- asset-openplatform-manage/**

**禁止路径**

- open-api-service/**
- partner-gateway/**

**必读**

- svmp/docs/internal/开放平台集成管理后台-页面设计.md

**必须交付**

- InvocationDetail Drawer 或详情页（可选）
- instance 写 operation 展示增强

**验证**

- npm run build

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent X · 管理面前端小增强（可选，不阻塞 P1 后端）。

【目标】InvocationDetail；WebhookDeliveryList 重试按钮（若 admin retry API 已有）。
```

---

## Prompt Y — Integration-P1-OpenAPI

**负责人**：联调验收  

**可改路径**

- svmp/docs/internal/**

**必读**

- svmp/docs/internal/开放平台对外REST执行面-分期落地方案.md

**必须交付**

- 联调手册-P1-OpenAPI.md
- acceptance 逐项结论

**验证**

- acceptance 列表全部通过
- 经 partner-gateway curl 脚本可复现

**依赖**：Prompt S, Prompt T, Prompt U, Prompt V, Prompt W  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent Y · OP-OPENAPI-P1 联调验收负责人。

【依赖】S/T/U/V/W 完成。
【产出】`联调手册-P1-OpenAPI.md`：Token → search → get → verify → remediate → verify-fix → batch → Webhook 日志核对。
【输出】通过项 / 阻塞项 / 修复建议。
```

---

## 5. 并行执行建议

```text
Wave 1（可并行）: H, D, F
Wave 2（可并行）: I（依赖 H）, E（依赖 F）
Wave 3: G（依赖 I + D + F + E）
Wave 4（P1）: J（依赖 G）
```
