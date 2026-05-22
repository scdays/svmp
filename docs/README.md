# 文档目录

本目录存放漏洞管理平台**对外集成**相关文档，按受众分为三类。**第三方仅阅读 `external/` 与 OpenAPI**；平台研发以 `internal/` 为准。


| 目录                         | 受众         | 说明                                       |
| -------------------------- | ---------- | ---------------------------------------- |
| [external/](./external/)   | **第三方接入方** | 开放平台 REST / Webhook / 数据外发契约（不含内部实现细节）   |
| [internal/](./internal/)   | 平台研发与集成    | 架构设计、Partner 鉴权落地、组件职责与实现映射              |
| [standards/](./standards/) | 合规与测试      | 工信部 2025 年版规范原文（docx），**不替代** OpenAPI 契约 |


---

## external · 第三方接入方

**定位**：Partner（SIEM、ITSM、资产平台、安全运营系统等）的接入契约。只描述「怎么用」，不涉及内部组件实现。


| 文档                                                       | 说明                                              |
| -------------------------------------------------------- | ----------------------------------------------- |
| [开放平台API接口规范.md](./external/开放平台API接口规范.md)              | **主文档**：鉴权、REST API、Webhook、扫描结果外发、能力码、错误码、集成流程 |
| [第三方开放平台接口文档.md](./external/第三方开放平台接口文档.md)              | 旧标题跳转页                                          |
| [../openapi/v1/openapi.yaml](../openapi/v1/openapi.yaml) | OpenAPI 3.1 机器可读契约（Swagger / Postman / 代码生成）    |


**功能域概览**


| 域        | Base Path / 协议             | 说明                                                                                             |
| -------- | -------------------------- | ---------------------------------------------------------------------------------------------- |
| 鉴权       | `POST /oauth/token`（或等价端点） | `client_credentials` → Bearer Token（见 [external 规范 §2.3](./external/开放平台API接口规范.md#23-获取访问令牌)） |
| REST API | `/api/open/v1/`*           | 任务、实例生命周期、外发查询                                                                                 |
| Webhook  | Partner 提供 `callbackUrl`   | 平台推送任务/实例/外发就绪事件                                                                               |
| 数据外发     | `GET /exports/*`           | 任务结束后下载 XML / JSON 结构化结果                                                                       |


**生命周期（写接口）**

```text
排查 POST /tasks
  → 验证 POST .../verify（2 有效 / 3 误报终态）
  → 处置二选一：remediate(→5) | archive(→9)
  → 修复核验 POST .../verify-fix（→6 / 7 / 10）
```

---

## internal · 平台研发与集成

**定位**：实现方案与组件分工。第三方**不应**依赖本节内容接入。


| 文档                                                              | 说明                                                                 |
| --------------------------------------------------------------- | ------------------------------------------------------------------ |
| [漏洞管理平台对外集成能力设计方案-V2.0.md](./internal/漏洞管理平台对外集成能力设计方案-V2.0.md) | 集成架构、规范域模型、部侧合规（接口 3/4）、实施路线                                       |
| [开放平台Partner鉴权与隔离-落地方案.md](./internal/开放平台Partner鉴权与隔离-落地方案.md) | Token 在登录服务签发、网关只校验；`partnerId` 隔离、capabilities、数据表                |
| [组件职责与接口映射.md](./internal/组件职责与接口映射.md) | **完整接口清单**（零侵入）：partner-gateway / open-api-service / SVMP |
| [partner-gateway与open-api-service-模块与接口清单.md](./internal/partner-gateway与open-api-service-模块与接口清单.md) | 双模块目录、接口对照、Nacos 样例 |
| [开放平台API治理与调用生命周期.md](./internal/开放平台API治理与调用生命周期.md) | 执行平面 + 治理平面；InvocationPipeline、api_invocation |
| [开放平台集成管理后台-页面设计.md](./internal/开放平台集成管理后台-页面设计.md) | 运营后台页面 IA、字段、API 映射、P0/P1 分期 |
| [multi-agent-执行Prompts.md](./internal/multi-agent-执行Prompts.md) | 可复制 Agent 任务单（D/E/F/G + H/I/J 页面） |


### 总体架构（零侵入 · 当前采用）

```text
Partner（公网）
  → partner-gateway（专用 Partner 网关：校验 / capability / 限流 / 注入 X-Partner-Id）
  → open-api-service（Token 签发、Partner 注册、/api/open/v1、Webhook、SVMP 适配）
  → SVMP 执行层（扫描 / 处置，Partner 不直连）

morningglory / clover：门户流量，⛔ 不参与 Partner 开放平台（零改动）
```

**原则**

| 原则 | 说明 |
|------|------|
| 现有服务不变 | **morningglory**、**clover** 不做 Partner 改造 |
| Token 在 open-api-service 签发 | partner-gateway **只校验、不签发** |
| 独立 Partner 入口 | 公网域名如 `open.vuln.example.com` → **partner-gateway** |
| Partner 不直连 SVMP | 仅 open-api-service 调引擎接口 |
| 数据隔离 | 只信任 partner-gateway 注入的 `X-Partner-Id` |

> 已废弃：在 morningglory/clover 上叠加 Partner 逻辑的旧骨架方案，详见 [组件职责与接口映射 §0.2](./internal/组件职责与接口映射.md)。

### 组件职责映射

| 组件 | 代码仓库 | 职责 | 不负责 |
|------|----------|------|--------|
| **morningglory** | `project_backend/public/morningglory` | 门户网关（现有） | Partner 开放平台 ⛔ |
| **clover** | `project_backend/public/clover` | 门户 IAM（现有） | Partner 注册/Token ⛔ |
| **partner-gateway** | `project_backend/svmp/partner-gateway` | Partner 公网入口、Token 校验、capability、限流 | Token 签发、业务、SVMP |
| **open-api-service** | `project_backend/svmp/open-api-service` | Partner 身份、Open API 执行平面、**调用治理**（api_invocation）、Webhook、SVMP 适配 | 门户 IAM |
| **SVMP 执行层** | `project_backend/svmp/`（vul-pass 等） | 扫描 / 处置执行 | Partner 直连 |

### external ↔ internal 章节对照

| external（第三方可见） | internal 实现组件 |
|------------------------|-------------------|
| §2 接入准备 | open-api-service Partner 管理 + 运营后台 |
| §2.3 / §3 鉴权 | open-api-service Token + partner-gateway G1–G7 |
| §5 REST API | open-api-service |
| §6 Webhook | open-api-service 事件模块 |
| §7 数据外发 | open-api-service + [../templates/](../templates/) |
| §8 能力码 | open-api-service 存储 + partner-gateway 拦截 |
| §9 错误码 | partner-gateway（401/403/429）+ open-api-service（业务码） |
| 部侧接口 3/4 | 独立 Regulatory 模块（非 external 范围） |

### 分阶段实施（按组件）

| 阶段 | partner-gateway | open-api-service | 验收 |
|------|-----------------|------------------|------|
| **P0** | 路由、Token 校验、注入 `X-Partner-Id` | Partner 表 + Token + 任务读/写 + 隔离 | 两家 Partner 互不可见任务 |
| **P1** | capabilities 40301、限流 | 实例生命周期 + Webhook + 凭证轮换 | 与 external §6 对齐 |
| **P2** | HMAC 校验 | 外发下载 + `EXPORT_READY` | 完整 OpenAPI |
| **P3** | IP 白名单 / mTLS | — | 高安全客户 |


---

## standards · 合规与测试

部侧 2025 年版官方文档（Word），供内部设计与合规对照。详见 [standards/README.md](./standards/README.md)。

---

## 快速入口


| 角色          | 建议阅读顺序                                                                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **第三方开发者**  | [external/开放平台API接口规范.md](./external/开放平台API接口规范.md) → [openapi/v1/openapi.yaml](../openapi/v1/openapi.yaml)                                                    |
| **平台研发** | [组件职责与接口映射](./internal/组件职责与接口映射.md) → [API 治理与调用生命周期](./internal/开放平台API治理与调用生命周期.md) → [multi-agent Prompts](./internal/multi-agent-执行Prompts.md) |
| **合规 / 测试** | [standards/](./standards/) → 对照 internal 设计方案中的 MIIT-2025 Profile                                                                                               |
| **外发模板开发**  | [../README.md](../README.md) 工具脚本 → [../templates/](../templates/)                                                                                              |


**常用链接**

- 第三方接口规范：[external/开放平台API接口规范.md](./external/开放平台API接口规范.md)
- 机器可读 OpenAPI：[../openapi/v1/openapi.yaml](../openapi/v1/openapi.yaml)
- 内部设计全文：[internal/漏洞管理平台对外集成能力设计方案-V2.0.md](./internal/漏洞管理平台对外集成能力设计方案-V2.0.md)
- 仓库总览与 OpenAPI 预览：[../README.md](../README.md)

