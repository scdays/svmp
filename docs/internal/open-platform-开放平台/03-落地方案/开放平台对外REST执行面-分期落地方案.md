# 开放平台 · 对外 REST 执行面 · 分期落地方案

> **定位**：Partner 可调用的 **`/oauth/token` + `/api/open/v1/*`** 实现与分期计划。  
> **与集成管理的关系**：[`开放平台集成管理-完整落地方案.md`](./开放平台集成管理-完整落地方案.md) 的 **OP-ADMIN-P0/P1/P2** 解决「运营怎么配、怎么看」；本文 **OP-OPENAPI-P0/P1/P2** 解决「Partner 能调什么 REST、平台怎么推 Webhook/外发」。  
> **契约源**：[`../external/网络安全漏洞管理平台 · API 接口文档V1.0.4.md`](../../../external/网络安全漏洞管理平台%20·%20API%20接口文档V1.0.4.md) §5–§7 与 [`../../openapi/v1/openapi.yaml`](../../../../openapi/v1/openapi.yaml)

---

## 一、两条产品线（不要混 Agent）

| 代号 | 范围 | 路径 | 前端 | 状态（以代码核对为准） |
|------|------|------|------|----------------------|
| **OP-ADMIN-P0/P1/P2** | 集成管理后台 | `/internal/admin/*` | asset-openplatform-manage | **你方称已完成** |
| **OP-ADMIN-P3** | 版本/告警/SLA | `/internal/admin/*` | 新增 3 页 | 未开始 |
| **OP-OPENAPI-P0** | 鉴权 + Token | `/api/open/v1/tasks/*` | 无 | **已完成（F0 契约对齐）** |
| **OP-OPENAPI-P1** | 实例 + Webhook 出站 | `/api/open/v1/instances/*` + 投递 | 管理页小增强 | **待开发** |
| **OP-OPENAPI-P2** | 结果外发 | `/api/open/v1/exports/*` | 可后置页 | **待开发** |

```text
Partner 调用链：
  partner-gateway → open-api-service（执行面 Handler + InvocationPipeline）
                  → vul-pass（内部 Feign，Partner 不可见）

运营配置链：
  asset-openplatform-manage → open-api-service（/internal/admin/* 治理读模型）
```

---

## 二、§5 接口实现对照（当前）

| 域 | 方法 | 路径 | 能力码 | OP-OPENAPI 阶段 | 实现状态 |
|----|------|------|--------|-----------------|----------|
| 鉴权 | POST | `/oauth/token` | — | P0 | ✅ |
| 任务 | POST | `/tasks/vul` | TASK_WRITE | P0 | ✅ |
| 任务 | POST | `/tasks/file` | TASK_WRITE | P0 | ✅ |
| 任务 | GET | `/tasks` | TASK_READ | P0 | ✅ |
| 任务 | GET | `/tasks/{taskId}` | TASK_READ | P0 | ✅ |
| 实例 | POST | `/instances/search` | INSTANCE_READ | **P1-a** | ❌ |
| 实例 | GET | `/instances/{vulInfoID}` | INSTANCE_READ | **P1-a** | ❌ |
| 实例 | POST | `.../verify` | INSTANCE_VERIFY | **P1-b** | ❌ |
| 实例 | POST | `/instances/verify:batch` | INSTANCE_VERIFY | **P1-c** | ❌ |
| 实例 | POST | `.../remediate` | INSTANCE_REMEDIATE | **P1-b** | ❌ |
| 实例 | POST | `/instances/remediate:batch` | INSTANCE_REMEDIATE | **P1-c** | ❌ |
| 实例 | POST | `.../verify-fix` | INSTANCE_VERIFY_FIX | **P1-b** | ❌ |
| 实例 | POST | `/instances/verify-fix:batch` | INSTANCE_VERIFY_FIX | **P1-c** | ❌ |
| 外发 | GET | `/exports/{exportId}` | EXPORT_READ | **P2** | ❌ |
| 外发 | GET | `/exports/{exportId}/download` | EXPORT_READ | **P2** | ❌ |
| 外发 | GET | `/tasks/{taskId}/exports` | EXPORT_READ | **P2** | ❌ |

**说明**：`api_operation` 表可 seed 对应 operationId，但 **实例/外发 Controller 尚未实现**。

---

## 三、架构约束（各阶段共用）

### 3.1 双平面

| 平面 | 职责 | 关键组件 |
|------|------|----------|
| **执行平面** | 实现 §5 REST，调 vul-pass | `OpenXxxUI` → `InvocationPipeline` → Domain → `IXxxGateway` |
| **治理平面** | 审计、统计、配置查询 | `api_invocation`、`webhook_delivery_log`、`/internal/admin/*` |

**禁止**：每个 REST 接口手写重复审计；**统一**走 `InvocationPipeline.invoke(operationId, handler)`。

### 3.2 三类 DTO（勿混用）

| 层 | 包路径 | 对齐文档 |
|----|--------|----------|
| Partner REST | `ui/dto/open/**` | openapi.yaml / API 接口文档 §5 |
| 运营 Admin | `ui/dto/admin/**` | 页面设计 / 方案 §6 |
| 引擎适配 | `infra/adapter/**` | [`Open API与vul-pass内部接口映射表.md`](../05-接口契约/Open%20API与vul-pass内部接口映射表.md) |

### 3.3 Partner 隔离

| 资源 | 业务键 | 表/索引 |
|------|--------|---------|
| 任务 | partnerId + extTaskId | `open_task`、`partner_task_map` |
| 实例 | partnerId + vulInfoID | `open_vuln_instance` |
| 外发 | partnerId + taskId/exportId | `open_export`（P2 新增） |

### 3.4 网关

- 鉴权、限流、Token：**partner-gateway**  
- open-api-service 只读 Partner 配置（rateLimitQps、capabilities）

---

## 四、分期交付

### 4.1 OP-OPENAPI-P0（已完成）

**范围**：§5.1 四接口 + Token + `api_invocation` + requestId。

**验收**：

- [x] `POST /tasks/vul`、`POST /tasks/file` 与 openapi 示例字段一致  
- [x] 跨 Partner 任务互不可见  
- [x] 无 capability → 40301（经 gateway）  
- [x] 每次写操作 `api_invocation` 有记录  

**Agent 来源**：`features/open-platform-admin-p0.yaml` 中 Prompt **F / E / G**（历史任务含执行面 P0）。

---

### 4.2 OP-OPENAPI-P1（下一里程碑，约 3–4 周）

**范围**：§5.2–5.5 实例 8 接口 + §6 Webhook **出站投递** + 联调验收。

**子阶段**（同一 Sprint 内按顺序，可拆 Agent）：

| 子阶段 | 接口 | 依赖 |
|--------|------|------|
| **P1-0** | 冻结 vul-pass 映射表 | 无 |
| **P1-a** | search + get | 映射表 + 任务 FINISHED 后实例入库 |
| **P1-b** | verify / remediate / verify-fix（单条） | P1-a + 状态机 |
| **P1-c** | 三个 `:batch` | P1-b + §4.2 幂等 |
| **P1-d** | Webhook 投递 + 写 `webhook_delivery_log` | Partner defaultCallbackUrl |
| **P1-e** | gateway capability 补全 + 联调手册 | P1-a–d |

**核心目录建议**：

```text
open-api-service/src/main/java/com/vtc/openapi/
├── domain/instance/          # 命令、状态机、Partner 隔离
├── domain/webhook/           # 出站投递、重试策略
├── ui/open/OpenInstanceUI.java
├── infra/adapter/IVulnInstanceGateway.java
├── infra/adapter/WebhookDeliveryAdapter.java
```

**验收门禁**：

```text
1. POST /instances/search 可选 exportProfile；taskId/extTaskId 归属校验
2. GET /instances/{vulInfoID} 跨 Partner → 40003
3. verify：前置 stat∈{0,1}；→(3) 终态；remediate → 40002
4. remediate：→5 或 →9；重复 → 40005
5. verify-fix：前置 stat=5
6. 批量：success[] + failed[] 结构
7. 每次写接口 api_invocation.resourceId = vulInfoID
8. 任务完成触发 Webhook（如 TASK_COMPLETED），日志表有记录
9. 经 partner-gateway 端到端 curl 通过
```

**管理面前端（小增强，不阻塞 P1 后端）**：

| 项 | 说明 |
|----|------|
| InvocationDetail | 展示 instance 写操作 |
| Webhook 重试按钮 | 调用 `POST /internal/admin/webhook-deliveries/{id}/retry`（P1 可选） |

**Agent 矩阵**：[`features/open-platform-openapi-p1.yaml`](../../features/open-platform-openapi-p1.yaml)

---

### 4.3 OP-OPENAPI-P2（约 2–3 周）

**范围**：§5.6 外发三接口 + `TaskExport` 组装 + `EXPORT_READY` Webhook。

| 接口 | 说明 |
|------|------|
| `GET /exports/{exportId}` | 元数据 |
| `GET /exports/{exportId}/download` | xml/json 文件流 |
| `GET /tasks/{taskId}/exports` | 任务下外发列表 |

**技术难点**：`TaskExport` 聚合封装（非原始 XML 透传），对齐 API 文档 §5.6.3。

**验收**：

- exportStage：TASK_COMPLETED / VERIFY_SCAN / VERIFY_FIX_SCAN  
- Partner 只能下载本 Partner 任务的外发  
- 外发就绪时 Webhook `EXPORT_READY` + invocation 有记录  

**Agent 矩阵**：[`features/open-platform-openapi-p2.yaml`](../../features/open-platform-openapi-p2.yaml)

---

### 4.5 联调周策略：Mock 优先（vul-pass 未就绪）

**背景**：vul-pass 实例/外发 API 尚未开发；接入方下周联调不能等引擎。

| 项 | 做法 |
|----|------|
| 配置 | 联调环境 `spring.profiles.active=mock`（见 [引擎对接与Mock模式方案](../../mock-引擎对接与联调/03-落地方案/引擎对接与Mock模式方案.md)） |
| 数据 | 先用 `bundles/default` 占位；**生产扫描原始结果**到位后导入 `bundles/prod-sample-001/` |
| 开发顺序 | P1 后端 **mock 与 vul-pass 实现并行**：Domain/UI 不变，只换 Gateway |
| 切换 | vul-pass α 就绪 → `adapter-mode=vul-pass` 做对比回归 |

**不阻塞项**：映射表 §3 vul-pass 列、Agent R 冻结 — 可与 mock 联调并行。

---

### 4.4 OP-OPENAPI-P3 / OP-ADMIN-P3（可选、后置）

| 项 | 说明 |
|----|------|
| API 版本治理 | `api_operation.status=DEPRECATED` + 网关告警头 |
| SLA / 告警 | 管理页 + `/internal/admin/alerts`（待设计） |
| 新 §5 接口 | **不**在本执行面分期内 |

---

## 五、集成后台是否还要新开发页面？

### 5.1 对 §5 REST **不需要**新的大模块

| 已有页面 | P1/P2 可变化 |
|----------|--------------|
| InvocationList | 增加 instance/export operation 筛选 |
| ApiCatalog | 随 seed 展示补全 |
| PartnerDetail 统计/Webhook | 事件类型会更丰富 |
| QuotaLimit | 随流量更准确 |

### 5.2 建议补的管理面小项（可与 OP-OPENAPI-P1 并行）

| 项 | 优先级 | 路由/组件 |
|----|--------|-----------|
| InvocationDetail | P1 高 | Drawer 或 `/openPlatform/invocation/:id` |
| Webhook 手动重试 | P1 中 | WebhookDeliveryList 中按钮 |
| Credential 接入说明 | P0 收尾 | `DeliveryGuidePanel.vue` |
| 运营看板 | P2 | `/openPlatform/dashboard` |
| 版本/告警/SLA | P3 | 新页面（OP-ADMIN-P3） |

---

## 六、治理 API 扩展（管理面，非 Partner 契约）

| 方法 | 路径 | 阶段 | 页面 |
|------|------|------|------|
| GET | `/internal/admin/invocations` | ADMIN-P1 ✅ | InvocationList |
| GET | `/internal/admin/invocations/{invocationId}` | **P1 建议补** | InvocationDetail |
| GET | `/internal/admin/partners/{id}/stats` | ADMIN-P1 ✅ | 统计 Tab |
| GET | `/internal/admin/webhook-deliveries` | ADMIN-P1 ✅ | Webhook 列表 |
| POST | `/internal/admin/webhook-deliveries/{id}/retry` | **P1 建议补** | 重试按钮 |
| GET | `/internal/admin/api-operations` | ADMIN-P2 ✅ | ApiCatalog |
| GET | `/internal/admin/quotas` | ADMIN-P2 ✅ | QuotaLimit |

---

## 七、Multi-Agent 执行顺序（OP-OPENAPI-P1）

```text
Wave 0   R — 冻结/补全 vul-pass 映射表（阻塞后续编码）
Wave 1   S — 实例读（search + get）+ gateway 路由
Wave 2   T — 实例写单条（verify / remediate / verify-fix）
Wave 3   U — 实例写批量（:batch 共 3 个）
Wave 4   V — Webhook 出站 + delivery_log
Wave 5   W — gateway 能力补全（可与 Wave 1 并行小规模）
Wave 6   X — 管理面前端小增强（InvocationDetail，可选）
Wave 7   Y — Integration 验收 + 联调手册-P1-OpenAPI.md
```

生成 Prompt 文件：

```powershell
cd svmp/docs/internal/scripts
py -3 generate-multi-agent-prompts.py features/open-platform-openapi-p1.yaml --out ../multi-agent-执行Prompts-OpenAPI-P1.md
py -3 generate-multi-agent-prompts.py features/open-platform-openapi-p2.yaml --out ../multi-agent-执行Prompts-OpenAPI-P2.md
```

---

## 八、文档清单

| 文档 | 用途 |
|------|------|
| 本文 | 执行面总分期与验收 |
| [`Open API与vul-pass内部接口映射表.md`](../05-接口契约/Open%20API与vul-pass内部接口映射表.md) | 实例/外发 ↔ vul-pass（**P1 编码前冻结**） |
| [`features/open-platform-openapi-p1.yaml`](../../features/open-platform-openapi-p1.yaml) | P1 Agent 矩阵 |
| [`features/open-platform-openapi-p2.yaml`](../../features/open-platform-openapi-p2.yaml) | P2 Agent 矩阵 |
| [`引擎对接与Mock模式方案.md`](../../mock-引擎对接与联调/03-落地方案/引擎对接与Mock模式方案.md) | **联调周 mock 切换 + 生产 fixture 导入** |
| `联调手册-P1-OpenAPI.md` | Integration Agent 产出（待生成） |
| `联调手册-P2-OpenAPI.md` | Integration Agent 产出（待生成） |

---

## 九、与《完整落地方案》如何衔接

在 [`开放平台集成管理-完整落地方案.md`](./开放平台集成管理-完整落地方案.md) §十六中：

| 原「执行平面」 | 对应本文 |
|----------------|----------|
| P0 tasks | OP-OPENAPI-P0 ✅ |
| P1 实例 + Webhook | OP-OPENAPI-P1 |
| P2 exports | OP-OPENAPI-P2 |

**集成管理后台 P0–P2 完成后**，对外 REST 开发 **以 openapi.yaml 为准**；管理页只做 §5.2 观测小增强。

---

## 十、总结

1. **主要工作**：补 **OP-OPENAPI-P1/P2**；与已完成的 **OP-ADMIN** 分开排 Agent。  
2. **阻塞项**：P1 编码前冻结 **vul-pass 映射表**；用 **features yaml** 生成 Prompt。  
3. **新页面**：§5 本身不强制新页；建议补 **InvocationDetail** 与 **Webhook 重试**；P3 告警/版本页以后做。
