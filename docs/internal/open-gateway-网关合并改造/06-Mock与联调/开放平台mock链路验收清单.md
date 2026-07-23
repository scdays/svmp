# 开放平台 mock 链路验收清单（Phase 0）

> 版本：v1.0  日期：2026-06-23
> 关联：`01-架构与总览/open-gateway合并与平台业务解耦改造方案.md`（v3）Phase 0
> 目的：把 open-api-service 已上线的 mock 能力固化为正式验收基线，作为后续 partner-gateway route-mode 改造、partner-admin 拆分、vul-pass 对接的回滚基线。

---

## 0. 验收目的

确认以下三件事：

1. 当前测试环境确实运行在 mock 模式；
2. Partner 请求经 partner-gateway 入口可完成端到端 E2E；
3. 治理页面能查到 mock 流程产生的调用记录、Webhook、运营案件、Export。

满足后，才允许进入 Phase 1（partner-gateway route-mode）。

---

## 1. 环境配置检查

### 1.1 open-api-service adapter-mode

检查 `project_backend/svmp/open-api-service/src/main/resources/application.yml`：

```yaml
open-api:
  engine:
    adapter-mode: task-center   # 当下 mock 即由 task-center 引擎实现
```

> 说明：早期 fixture-based mock（`adapter-mode: mock` + `classpath:mock/engine/bundles/`）已弃用。当下 mock 模式采用 **task-center 引擎实现**，即 `adapter-mode=task-center` 即为 mock 验收环境。`application-mock.yml` / fixture bundle 不再作为验收依据。

**验收点**：

- [ ] 测试环境 `adapter-mode=task-center` 已确认
- [ ] task-center 引擎链路可用（vuln-task-center 服务可达，或其 mock/stub 就绪）
- [ ] 不再依赖早期 `mock/engine/bundles/` fixture

### 1.2 partner-gateway 路由

检查 `project_backend/svmp/partner-gateway/src/main/resources/application.yml`：

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: open-api-v1
          uri: lb://open-api-service
          predicates:
            - Path=/api/open/v1/**
```

**验收点**：

- [ ] `/api/open/v1/**` 路由到 `open-api-service`
- [ ] `/oauth/token` 路由到 `open-api-service`
- [ ] partner-gateway 启动正常，Nacos 注册可见
- [ ] Redis（database=2）可连，`partner:token:{sha256}` key 可读写

### 1.3 前端代理

检查 `asset-manage-master/vue.config.js` 与 `asset-openplatform-manage/config/openPlatformDevProxy.js`：

**验收点**：

- [ ] `/open-api-service` → 平台网关（7000）
- [ ] `/api/open/v1`、`/oauth/token` → partner-gateway（35770）
- [ ] `.env.development.local` 的 `VUE_APP_OPEN_API_ADMIN_KEY` 已配置
- [ ] 主应用 `public/conf/index.js` 下发的 `VUE_APP_OPEN_API_BASE_URL`、`VUE_APP_OPEN_API_ADMIN_KEY` 正确

---

## 2. 前端入口验证

四个核心入口必须全部跑通。

### 2.1 接入测试 MockE2eConsole

路由：`/openPlatform/mock-e2e`

**验收点**：

- [ ] 创建 Partner（或选用已有 `e2e-` 前缀 Partner）
- [ ] 创建 Credential，secret 仅展示一次
- [ ] `/oauth/token` 获取 access_token 成功
- [ ] `POST /api/open/v1/tasks/vul` 建任务成功，返回 taskId
- [ ] mock 导入报告（NSFocus XML）成功
- [ ] 任务进度查询返回 FINISHED
- [ ] 实例搜索返回实例列表

### 2.2 风险排查 OpenTaskWorkspace

路由：`/openPlatform/open-task/workspace/:taskId`

**验收点**：

- [ ] 任务工作台概览可加载
- [ ] 排查子任务 / 验证子任务 Tab 可查
- [ ] 排查结果（存活/端口/系统漏洞）按 scanPhase 展示
- [ ] 漏洞实例 Tab 可查实例列表
- [ ] Partner 回调 Tab 可查

### 2.3 修复核验 VerifyFixWorkspace

路由：`/openPlatform/verify-fix-jobs/:jobId`

**验收点**：

- [ ] 核验作业列表可加载
- [ ] 创建 / 查询 verify-fix job 成功
- [ ] 导入复扫 XML 成功
- [ ] `completeVerifyFixAllFixed` 或 `AllUnfixed` 或 `ByCompare` 完成成功
- [ ] 复扫结果 Tab 可查
- [ ] 实例状态跃迁到 6（核验修复）/ 7（核验未修复）

### 2.4 处置测试 VerifyFixOps

路由：`/openPlatform/verify-fix-ops`

**验收点**：

- [ ] Partner 会话绑定成功（粘贴 Token 或 clientId+Secret 换 Token）
- [ ] 实例筛选可用
- [ ] `verify` 单个实例成功，状态 1→2
- [ ] `remediate` 单个实例成功，状态→5
- [ ] `verify-fix` 受理成功
- [ ] 批量 `:batch` 接口成功（verify/remediate/verify-fix）
- [ ] 误报分支 verify FALSE_POSITIVE 状态 1→3 可验证（可选）

---

## 3. 接口链路验收

按顺序执行，每步记录响应。

### 3.1 鉴权与任务

| 步骤 | 接口 | 期望 |
|---|---|---|
| 1 | 创建 Partner | 200，partnerId 返回 |
| 2 | 创建 Credential | 200，clientId/secret 返回 |
| 3 | `POST /oauth/token` | 200，access_token 返回 |
| 4 | `POST /api/open/v1/tasks/vul` | 200，taskId 返回 |
| 5 | mock 导入报告 | 200，实例入库 |
| 6 | `GET /api/open/v1/tasks/{taskId}` | 200，进度 FINISHED |
| 7 | `POST /api/open/v1/instances/search` | 200，实例列表 |

### 3.2 实例状态机

| 步骤 | 接口 | 期望状态 |
|---|---|---|
| 8 | `POST /api/open/v1/instances/{vulInfoID}/verify` | 1→2 |
| 9 | `POST /api/open/v1/instances/{vulInfoID}/remediate` | →5 |
| 10 | `POST /api/open/v1/instances/{vulInfoID}/verify-fix` | 受理 PENDING |
| 11 | 完成修复核验 job | 6 / 7 |
| 12 | 批量 `:batch` 接口 | 共享 verifyFixJobId |

### 3.3 外发与治理

| 步骤 | 接口 | 期望 |
|---|---|---|
| 13 | `GET /api/open/v1/tasks/{taskId}/exports` | 200，export 列表 |
| 14 | `GET /api/open/v1/exports/{exportId}` | 200，元数据 |
| 15 | `GET /api/open/v1/exports/{exportId}/download` | 200，文件下载 |
| 16 | `GET /internal/admin/webhook-deliveries` | 投递记录可查 |
| 17 | `GET /internal/admin/operation-cases` | 案件可查 |
| 18 | `GET /internal/admin/invocations` | 调用记录可查 |

---

## 4. 治理面数据验证

mock 产生的数据必须能在治理页面查到。

| 页面 | 路由 | 数据来源 | 验收点 |
|---|---|---|---|
| 流量治理 | `/openPlatform/invocation` | `api_invocation` | [ ] 能查到上述步骤的调用记录 |
| 推送记录 | `/openPlatform/webhook-log` | `webhook_delivery_log` | [ ] 能查到 TASK_COMPLETED / EXPORT_READY 投递 |
| 运营案件 | `/openPlatform/operation-cases` | `open_operation_case` | [ ] 能查到 case 与 timeline |
| 接口目录 | `/openPlatform/api-catalog` | `api_operation` | [ ] operationId/path/method/capability 展示正常 |
| 流控策略 | `/openPlatform/quota` | partner quota/stats | [ ] Partner 配额/调用统计展示 |
| Export 下载 | 工作台内 | `open_export` | [ ] mock 外发文件可下载 |

---

## 5. Webhook 投递验证

**验收点**：

- [ ] mock 任务完成触发 `TASK_COMPLETED` 事件
- [ ] mock 修复核验完成触发 `INSTANCE_VERIFY_FIX_COMPLETED` 事件
- [ ] export 就绪触发 `EXPORT_READY` 事件
- [ ] 投递记录 `webhook_delivery_log` 状态为 SUCCESS
- [ ] 投递包含 `X-Webhook-Signature`（HMAC-SHA256）和 `X-Webhook-Timestamp`
- [ ] 失败投递可重试（retryWebhookDelivery）

> 注：当前 Webhook 投递仍在 open-api-service。Phase 3 迁 partner-admin 后，事件产生方不变，投递方改为 partner-admin dispatcher。

---

## 6. 验收结论分级

| 项 | 状态 |
|---|---|
| P0.1 open-api-service mock 能力上线 | 已完成 |
| P0.2 mock 链路前端入口验证 | 待补记录 |
| P0.3 mock 链路经 partner-gateway 验证 | 待补记录 |
| P0.4 mock 治理面数据验证 | 待补记录 |
| P0.5 Webhook 投递验证 | 待补记录 |

全部勾选完成后，认定为：

> **当前 mock 链路完整、稳定、可验收，作为 P1 改造的回滚基线。**

---

## 7. 缺陷记录模板

发现问题时记录：

```text
- 编号：
- 所属步骤：
- 现象：
- 复现路径：
- 期望：
- 实际：
- 严重度：阻塞 / 重要 / 一般
- 负责人：
- 状态：待处理 / 处理中 / 已修复 / 已验证
```

---

## 8. 验收后行动

1. 验收记录归档到本目录；
2. 进入 Phase 1：`03-落地方案/partner-gateway-route-mode实施方案.md`；
3. mock 保持可用，后续所有改造必须能切回 mock。
