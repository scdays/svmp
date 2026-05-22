# Multi-Agent 执行 Prompts（零侵入架构）

> **用法**：每个 Prompt **单独开一个新对话**，整段复制发送。你本人只做集成验收，不要让一个 Agent 同时改 partner-gateway 与 open-api-service 的同一模块。  
> **原则**：禁止提交「大量 TODO 却声称完成」的代码；未完成项写入 **P1 backlog**。

**推荐顺序**：D → E → F → G（可选 Prompt 0 并行文档）

**架构文档**：[组件职责与接口映射](./组件职责与接口映射.md) · [开放平台API治理与调用生命周期](./开放平台API治理与调用生命周期.md)

---

## Prompt 0 · 文档对齐（可选）

```markdown
你只更新文档，不写业务代码。

1. 确认 `svmp/docs/internal/组件职责与接口映射.md`、`docs/README.md` 与「零侵入 + partner-gateway + open-api-service + 双平面」一致
2. 在 `开放平台Partner鉴权与隔离-落地方案.md` 文首增加「历史方案说明」：morningglory/clover Partner 改造已废弃，见组件映射 §0.2
3. 不修改 external 第三方可见契约语义

交付：修改文件列表 + 3 行摘要。
```

---

## Prompt D · open-api-service · Partner 身份与 Token（先做）

```markdown
你是 **open-api-service · Partner 身份与 Token** 负责人。
严格只改 `project_backend/svmp/open-api-service/`，禁止修改 morningglory、clover、partner-gateway、vul-pass 业务逻辑。

## 必读（先 Read 再动手）
- `svmp/docs/internal/组件职责与接口映射.md` §5.1–5.3
- `svmp/docs/internal/开放平台API治理与调用生命周期.md` §5（Partner 表）
- `svmp/docs/external/开放平台API接口规范.md` §2.1、§2.3
- `svmp/openapi/v1/openapi.yaml` — `/oauth/token`

## P0 必须交付（可运行，禁止 TODO 冒充完成）
1. Liquibase + MyBatis：`partner`、`partner_capability`、`partner_credential`
2. `POST /internal/admin/partners`、`PUT .../{partnerId}`、`POST .../credentials`
3. `POST /oauth/token`（`client_credentials`）+ Redis `partner:token:{sha256}`
4. `POST /internal/token/introspect`
5. `mvn compile` 通过 + curl 验证流程

## 禁止
- 实现 `/api/open/v1/tasks`（Agent F）
- 修改 partner-gateway / morningglory / clover
- 内存仓储作为最终方案

## 交付
变更清单、curl 示例、P1 backlog（凭证轮换、会话吊销）
```

---

## Prompt E · partner-gateway · 校验与转发（D 完成后）

```markdown
你是 **partner-gateway** 负责人。只改 `project_backend/svmp/partner-gateway/`。

## 必读
- `svmp/docs/internal/组件职责与接口映射.md` §4
- `svmp/docs/internal/partner-gateway与open-api-service-模块与接口清单.md` §2

## 前置
Agent D 的 Token + Redis 键格式已验收；否则在交付说明中写清测试用的 Redis 手工数据。

## P0 必须交付
1. 路由样例：`/oauth/token`、`/api/open/v1/**` → open-api-service
2. PartnerAuthFilter G1–G6，错误体 `{code,message,data,requestId}`
3. `mvn compile` + curl：无 Token → 40101；无 capability → 40301

## 禁止
改 morningglory/clover/open-api-service 业务、在网关签发 Token

## 交付
变更清单、Nacos 样例、curl、P1 backlog（G7 限流）
```

---

## Prompt F · open-api-service · 业务 P0 + 调用治理（修订版 · D 完成后）

```markdown
你是 **open-api-service · 执行平面 + 治理平面 P0** 负责人。
只改 `project_backend/svmp/open-api-service/`。Partner/Token 由 Agent D 完成，**不得破坏**。

## 必读（必须 Read）
- `svmp/docs/internal/开放平台API治理与调用生命周期.md`（全文：双平面、Pipeline、api_invocation）
- `svmp/docs/internal/组件职责与接口映射.md` §5.4.1
- `svmp/openapi/v1/openapi.yaml` — `/tasks`
- `project_backend/svmp/vul-pass` — 扫描任务真实 API

## 架构要求（核心）

### 执行平面
- 只信任 Header `X-Partner-Id`
- `POST/GET /api/open/v1/tasks` + `SvmpEngineAdapter` 真实对接 vul-pass
- `(partner_id, ext_task_id)` 幂等；extTaskId 不下发 SVMP
- 跨 Partner 访问 → 40003

### 治理平面（P0 必须，不是可选项）
- 表 `api_operation`（OpenAPI operation 种子数据）
- 表 `api_invocation`（每次业务调用一条记录）
- `InvocationPipeline`（或等价）：环绕 Handler，统一写 invocation、统一响应包装
- `requestId` 与响应、`X-Request-Id`、DB 字段 **一致**
- **禁止**在每个 Controller 重复写审计/日志代码

### 实现结构（建议）
- `governance/InvocationService`、`InvocationContext`
- `pipeline/InvocationPipeline`
- `handler/TaskHandler`
- `ui/open/OpenTaskUI` 薄层，只调 Pipeline

## P0 禁止
- 实例 lifecycle、Webhook、exports
- TODO 冒充完成；未实现写 backlog
- 改 partner-gateway / morningglory / clover

## 验收
1. `mvn compile` 通过
2. 两家 Partner 各建任务互不可见
3. **每次** `POST /tasks` 在 `api_invocation` 有记录，且 `request_id` 与 JSON 响应一致
4. 更新 `svmp/docs/internal/联调手册-P0.md` 业务 + 治理验证 SQL 示例

## 交付
文件清单、curl、SVMP 接口对照表、invocation 验证步骤、P1 backlog（span、报表 API）
```

---

## Prompt G · 联调验收（E、F 完成后）

```markdown
你是 **开放平台 P0 联调工程师**。最小 diff，不写新功能。

## 目标
Partner → partner-gateway → open-api-service（执行+治理）→ SVMP

## 必读
- `svmp/docs/internal/联调手册-P0.md`
- `svmp/docs/internal/开放平台API治理与调用生命周期.md` §8 验收项

## 交付
1. 更新联调手册：步骤 0–4 + invocation 查询示例
2. 修复集成不一致（Redis 键、Header、错误 body、requestId）
3. 检查清单；阻塞项单独列出

禁止改 morningglory/clover；禁止留 TODO 冒充完成。
```

---

## 验收总表（你本人）

| 步骤 | 验证 |
|------|------|
| D | `/oauth/token` + Redis + introspect |
| E | 40101 / 40301 + `X-Partner-Id` 注入 |
| F | 两家 Partner 任务隔离 + `api_invocation` 有记录 |
| G | 联调手册端到端通 |
