# 文档目录

本目录存放漏洞管理平台**对外集成**相关文档，按受众分为三类。**第三方仅阅读 `external/` 与 OpenAPI**；平台研发以 `internal/` 为准。

| 目录 | 受众 | 说明 |
|------|------|------|
| [external/](./external/) | **第三方接入方** | 开放平台 REST / Webhook / 数据外发契约（不含内部实现细节） |
| [internal/](./internal/) | 平台研发与集成 | 集成管理后台落地方案与页面设计 |
| [standards/](./standards/) | 合规与测试 | 工信部 2025 年版规范原文（docx），**不替代** OpenAPI 契约 |

---

## external · 第三方接入方

**定位**：Partner（SIEM、ITSM、资产平台、安全运营系统等）的接入契约。只描述「怎么用」，不涉及内部组件实现。

| 文档 | 说明 |
|------|------|
| [开放平台API接口规范.md](./external/开放平台API接口规范.md) | **主文档**：鉴权、REST API、Webhook、扫描结果外发、能力码、错误码、集成流程 |
| [第三方开放平台接口文档.md](./external/第三方开放平台接口文档.md) | 旧标题跳转页 |
| [../openapi/v1/openapi.yaml](../openapi/v1/openapi.yaml) | OpenAPI 3.1 机器可读契约（Swagger / Postman / 代码生成） |

**功能域概览**

| 域 | Base Path / 协议 | 说明 |
|----|------------------|------|
| 鉴权 | `POST /oauth/token`（或等价端点） | `client_credentials` → Bearer Token（见 [external 规范 §2.3](./external/开放平台API接口规范.md#23-获取访问令牌)） |
| REST API | `/api/open/v1/*` | 任务、实例生命周期、外发查询 |
| Webhook | Partner 提供 `callbackUrl` | 平台推送任务/实例/外发就绪事件 |
| 数据外发 | `GET /exports/*` | 任务结束后下载 XML / JSON 结构化结果 |

**生命周期（写接口）**

```text
排查 POST /tasks
  → 验证 POST .../verify（2 有效 / 3 误报终态）
  → 处置二选一：remediate(→5) | archive(→9)
  → 修复核验 POST .../verify-fix（→6 / 7 / 10）
```

---

## internal · 平台研发与集成

**定位**：集成管理后台与开放平台实现方案。第三方**不应**依赖本节内容接入。

| 文档 | 说明 |
|------|------|
| [开放平台集成管理-完整落地方案.md](./internal/开放平台集成管理-完整落地方案.md) | **总方案**：独立子应用 + 主应用注册 + 后端/网关 + P0–P3 分期 |
| [开放平台集成管理后台-页面设计.md](./internal/开放平台集成管理后台-页面设计.md) | 运营后台页面 IA、字段、API 映射、P0/P1 分期 |

### 总体架构（零侵入）

```text
Partner（公网）
  → partner-gateway（校验 / capability / 限流 / 注入 X-Partner-Id）
  → open-api-service（Token 签发、Partner 注册、/api/open/v1、治理、SVMP 适配）
  → SVMP 执行层（扫描 / 处置，Partner 不直连）

asset-manage-master → asset-openplatform-manage（集成管理后台，运营登记 Partner）

morningglory / clover：门户流量，⛔ 不参与 Partner 开放平台（零改动）
```

### 组件职责

| 组件 | 代码仓库 | 职责 |
|------|----------|------|
| **partner-gateway** | `project_backend/svmp/partner-gateway` | Partner 公网入口、Token 校验、capability |
| **open-api-service** | `project_backend/svmp/open-api-service` | Partner 身份、Open API、治理、Webhook |
| **asset-openplatform-manage** | `project_frontend/asset/asset-openplatform-manage` | 集成管理后台（新建） |
| **morningglory / clover** | `project_backend/public/` | 门户 IAM，不改造 |

---

## standards · 合规与测试

部侧 2025 年版官方文档（Word），供内部设计与合规对照。详见 [standards/README.md](./standards/README.md)。

---

## 快速入口

| 角色 | 建议阅读顺序 |
|------|--------------|
| **第三方开发者** | [external/开放平台API接口规范.md](./external/开放平台API接口规范.md) → [openapi/v1/openapi.yaml](../openapi/v1/openapi.yaml) |
| **平台研发** | [完整落地方案](./internal/开放平台集成管理-完整落地方案.md) → [页面设计](./internal/开放平台集成管理后台-页面设计.md) |
| **合规 / 测试** | [standards/](./standards/) |
| **外发模板开发** | [../README.md](../README.md) 工具脚本 → [../templates/](../templates/) |

**常用链接**

- 第三方接口规范：[external/开放平台API接口规范.md](./external/开放平台API接口规范.md)
- 机器可读 OpenAPI：[../openapi/v1/openapi.yaml](../openapi/v1/openapi.yaml)
- 集成管理落地方案：[internal/开放平台集成管理-完整落地方案.md](./internal/开放平台集成管理-完整落地方案.md)
