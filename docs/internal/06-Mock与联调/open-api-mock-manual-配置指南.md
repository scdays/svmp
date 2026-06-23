# open-api-service Mock 半人工联调配置指南

> **适用场景**：接入方通过开放平台建任务，但扫描在 **vuln-task-center / 绿盟扫描器** 侧人工执行；回收 Aurora XML 后由运营导入，触发 **FINISHED → 实例入库 → Webhook → 外发**。  
> **关联**：[引擎对接与 Mock 模式方案](./引擎对接与Mock模式方案.md) · [Mock fixture 说明](../../project_backend/svmp/open-api-service/src/main/resources/mock/engine/README.md) · [运营 UI](../../project_frontend/asset/asset-openplatform-manage/src/views/openPlatform/MockManualIngest.vue)

---

## 1. 配置项速查（勿混淆）

| 配置 | 合法值 | 说明 |
|------|--------|------|
| `open-api.engine.adapter-mode` | **`mock`** 或 **`vul-pass`** | 引擎适配器；**不能**写 `mock-manual` |
| `open-api.engine.mock.ingest-mode` | **`auto`** 或 **`manual`** | `auto`：delay 后自动 FINISHED；`manual`：保持 RUNNING 直到导入 XML |
| `spring.profiles.active` | 可含 **`mock-manual`** | Profile 名，不是 `adapter-mode` 的值 |

```text
错误示例：adapter-mode: mock-manual   → Mock Bean 不会加载
正确示例：adapter-mode: mock + ingest-mode: manual
```

---

## 2. 三种配置方式

### 方式 A：Spring Profile（本地 / 联调推荐）

**启动参数或 `application.yml`：**

```yaml
spring:
  profiles:
    active: mock-manual
```

等价加载：

- `application-mock-manual.yml`（`ingest-mode: manual`、`xml-import-mode: java` 等）
- 通过 `spring.profiles.include: mock` 叠加 `application-mock.yml`（`adapter-mode: mock`）

**路径**：`project_backend/svmp/open-api-service/src/main/resources/application-mock-manual.yml`

### 方式 B：Nacos / 集中配置（部署推荐）

在 **open-api-service** 专属配置（或 shared 中仅对该服务生效的片段）写入：

```yaml
open-api:
  engine:
    adapter-mode: mock
    mock:
      ingest-mode: manual
      data-dir: file:/data/open-api-mock
      auto-ingest-instances-on-finish: true
      xml-import-mode: java
      xml-import-profile: auto
      default-bundle: default
      task-finish-delay-seconds: 5
      verify-scan-delay-seconds: 3
```

说明：

- `data-dir` 使用 `file:` 时任务级 bundle 持久化在磁盘；使用 `classpath:mock/engine` 时导入写入 `${java.io.tmpdir}/open-api-mock`。
- **无需 Python**（`xml-import-mode: java` 为默认）；仅回退时配置 `xml-import-mode: python` 与 `import-script-path`。

### 方式 C：仅改 `application.yml`（不启用 Profile）

在仓库 `application.yml` 的 `open-api.engine` 段：

```yaml
open-api:
  engine:
    adapter-mode: mock
    mock:
      data-dir: classpath:mock/engine
      ingest-mode: manual
      auto-ingest-instances-on-finish: true
      xml-import-mode: java
      xml-import-profile: auto
```

与 Profile 方式二选一即可，避免重复覆盖导致困惑。

---

## 3. 完整配置项说明

| 键 | 默认 | 说明 |
|----|------|------|
| `adapter-mode` | `vul-pass` | 生产用 `vul-pass`；开放平台 Mock 联调用 **`mock`** |
| `mock.data-dir` | `classpath:mock/engine` | fixture 根目录；半人工建议 `file:/data/open-api-mock` |
| `mock.ingest-mode` | `auto` | **`manual`** = 半人工 |
| `mock.auto-ingest-instances-on-finish` | `true` | 任务 FINISHED 后是否从 bundle 入库 |
| `mock.task-finish-delay-seconds` | `5` | 仅 **`ingest-mode=auto`** 时生效 |
| `mock.xml-import-mode` | `java` | `java`：内嵌解析；`python`：调用脚本 |
| `mock.xml-import-profile` | `auto` | `auto` / `vul` / `pwd` / `live` / `port` |
| `mock.import-script-path` | 空 | **仅 python 模式**；如 `svmp/docs/internal/scripts/import-nsfocus-xml-to-mock-bundle.py` |
| `mock.python-command` | `python` | **仅 python 模式** |
| `admin.api-key` | — | 内网 Admin API；请求头 `X-Internal-Admin-Key` |

**模板校验（`ingest-mode=manual` + Java 导入）**：导入 XML 时按任务 `scanTemplateId` 校验 profile：

| scanTemplateId | 期望 profile |
|----------------|--------------|
| 1001 + vulnType=3 | `pwd` |
| 1001 其他 | `vul` |
| 1002 | `live` |
| 1003 | `port` |

---

## 4. 模式对照

| 场景 | `adapter-mode` | `ingest-mode` | Partner 建任务后 |
|------|----------------|---------------|------------------|
| 生产 | `vul-pass` | — | 真实引擎进度 |
| Mock 全自动 E2E | `mock` | `auto` | 约 5s 后 `FINISHED` + 自动 ingest |
| Mock 半人工 | `mock` | **`manual`** | 长期 **`RUNNING`**，导入 XML 后 `FINISHED` |

---

## 5. 配套配置（非 open-api-service）

### 5.1 内网 Admin Key

```yaml
open-api:
  admin:
    api-key: <your-internal-admin-key>
```

请求 `/internal/admin/**` 时携带：`X-Internal-Admin-Key: <key>`

### 5.2 运营后台子应用（asset-openplatform-manage）

`project_frontend/asset/asset-openplatform-manage/.env.development` 或 `.env.development.local`：

```env
VUE_APP_OPEN_API_BASE_URL=/open-api
VUE_APP_OPEN_API_ADMIN_KEY=<与 admin.api-key 一致>
VUE_APP_OPEN_API_PROXY_TARGET=http://<open-api-host>:35780
```

访问路径（主应用）：`/openPlatform/mock-manual`  
支持 query：`?taskId=<平台 taskId>`

### 5.3 Partner Webhook（可选）

Partner `defaultCallbackUrl` 或任务级 `callbackUrl` 指向联调收件端，例如：

`http://<open-api>:35780/internal/dev/webhook/receive`

需 `open-api.webhook.test-receiver-enabled: true`（联调默认开启）。

### 5.4 file-sharing-center（外发 READY）

外发组装依赖文件服务；不可用时外发可能 SKIP/FAIL，与 ingest 模式无关。

---

## 6. 配置生效验证

1. **启动日志**：应出现 `Engine adapter mode: MOCK`（`SvmpEngineAdapterMockImpl`）。
2. **不应**出现仅 `vul-pass` 适配器且无 Mock 相关 Bean。
3. **建任务**：`POST /api/open/v1/tasks/vul` 后 `GET /tasks/{taskId}` → **`RUNNING`**（manual 模式）。
4. **Admin API**：
   - `GET /internal/admin/mock-tasks/{taskId}/dispatch-packet` → `ingestMode: manual`
   - `GET /internal/admin/mock-tasks/{taskId}/bundle-status` → 200
5. **全自动误配检查**：若 manual 未生效，任务会在 `task-finish-delay-seconds` 后变 `FINISHED`，说明 `ingest-mode` 仍为 `auto` 或未加载 `mock-manual` profile。

---

## 7. 运营联调流程（配置完成后）

| 步骤 | 操作 |
|------|------|
| 1 | Partner 创建任务 → 状态 `RUNNING` |
| 2 | 运营打开 **Mock 半人工导入** 页，或 `GET dispatch-packet` 查看目标/模板/目录 |
| 3 | 在 vuln-task-center / 扫描器执行扫描，回收 NSFocus Aurora XML |
| 4 | 页面上 **预览解析** 或 `POST .../preview-report` |
| 5 | **确认导入** 或 `POST .../import-report`（已入库可 `force=true` 重导） |
| 6 | 任务 `FINISHED`，`POST /instances/search` 可查实例；检查 Webhook / 外发 |

**Admin API 摘要**

| 方法 | 路径 |
|------|------|
| GET | `/internal/admin/mock-tasks/{taskId}/dispatch-packet` |
| GET | `/internal/admin/mock-tasks/{taskId}/bundle-status` |
| POST | `/internal/admin/mock-tasks/{taskId}/preview-report`（multipart `file`） |
| POST | `/internal/admin/mock-tasks/{taskId}/import-report?force=false` |

---

## 8. 脚本与 E2E

| 脚本 | 用途 |
|------|------|
| `open-api-service/scripts/e2e-mock-flow.ps1` | Mock **自动** ingest |
| `open-api-service/scripts/e2e-mock-manual-flow.ps1` | Mock **半人工**（需服务 `mock-manual` profile） |

PowerShell 示例：

```powershell
# 服务已 spring.profiles.active=mock-manual
powershell -File project_backend\svmp\open-api-service\scripts\e2e-mock-manual-flow.ps1 `
  -Base http://127.0.0.1:35780 `
  -AdminKey <your-admin-key>
```

---

## 9. 常见问题

**Q：`adapter-mode: mock-manual` 后 Admin 导入 404？**  
A：改为 `adapter-mode: mock`，`ingest-mode: manual`（或使用 profile `mock-manual`）。

**Q：导入报「XML profile 与 scanTemplateId 不匹配」？**  
A：检查 XML 报告类型与建任务时的 `scanTemplateId` / `type`；或调整 `xml-import-profile`（高级）。

**Q：classpath `data-dir` 下找不到导入的 bundle？**  
A：classpath 不可写，导入落在 `java.io.tmpdir/open-api-mock/tasks/{taskId}`；生产联调请用 `file:/data/open-api-mock`。

**Q：想用 Python 解析？**  
A：`xml-import-mode: python` + `import-script-path` + 本机安装 Python。

---

## 10. 相关文件索引

| 文件 | 说明 |
|------|------|
| `open-api-service/src/main/resources/application-mock.yml` | Profile `mock` |
| `open-api-service/src/main/resources/application-mock-manual.yml` | Profile `mock-manual` |
| `open-api-service/src/main/java/com/vtc/openapi/infra/config/OpenApiProperties.java` | 配置绑定 |
| `open-api-service/scripts/e2e-mock-manual-flow.ps1` | 半人工 E2E |
| `asset-openplatform-manage/src/views/openPlatform/MockManualIngest.vue` | 运营 UI |
