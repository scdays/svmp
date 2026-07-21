# M9 独立库 + Groovy 建表 + 路由转移 执行方案

> 版本：v1.0  日期：2026-06-25
> 性质：对 M0 主计划"共享 open_api 库 + Liquibase XML"决策的修订。改为独立库 + Groovy 建表 + 路由转移。

---

## 0. 背景：发现的真实问题

核查 spore-starter-liquibase 源码（`LiquibaseExecutor.load()`）发现：
- 执行器只扫描 `common.data.dir` 目录下 `.groovy` / `.xlsx` / `.sql` 文件，**不扫描 `.xml`**
- platform-admin 现有 5 个 `.xml` changelog（event_trace/ebus_outbox 等 8 张表）**从未被自动执行**
- 即：platform-admin 部署到干净库时，事件相关表不会被创建 → 运行时报错

ESMP 体系标准建表方式是 **groovy DSL**（参照 esmp-starter-task `db/mysql/task.groovy`、open-api-service 18 个 groovy）。platform-admin 之前用 XML 是错的，必须统一为 groovy。

---

## 1. 决策（用户确认：按推荐方案）

| 决策点 | 方案 |
|--------|------|
| 路由转移 | 只转 `/oauth/token` + `/api/open/v1/oauth/token` → platform-admin；internal 管理面 `/internal/admin/**` 由 platform-admin 直连不经 gateway；`/api/open/v1/**` 保留 open-api-service（含未迁 mock） |
| 数据迁移 | 仅迁 M1-M5 业务表 groovy 建表脚本到 platform-admin，不迁存量数据 |
| open-api-service | 保留 M1-M5 代码过渡（不删），双写期共享 |
| 建表机制 | platform-admin 现有 5 个 XML 全转 groovy；新增 M1-M5 业务表 groovy |

---

## 2. Groovy 加载机制（spore-starter-liquibase）

- `@EnableLiquibase` → `LiquibaseExecutor` 扫描 `common.data.dir`（= `db/mysql`）
- 自动执行目录下**所有 `.groovy`** 文件，每个文件独立 `databaseChangeLog`，无需 master changelog
- groovy DSL 格式：`databaseChangeLog(logicalFilePath: 'xxx.groovy') { changeSet(...) { createTable(...) {...} } }`
- 数据初始化用 `.xlsx`（`common.data.init.enable=true`）
- platform-admin application.yml 已配 `common.data.dir: db/${common.data.type}`，无需改配置

---

## 3. 执行任务

### 任务1：platform-admin 事件表 XML → groovy 转换
将 5 个 XML changelog 转为 groovy DSL：
- `20260624-init-eventcenter-tables.xml` → `event_trace.groovy` + `event_consume_trace.groovy` + `event_dead_letter.groovy`（拆分，与 open-api-service 一表一文件风格一致）
- `20260624-init-webhook-tables.xml` → `webhook_delivery_log.groovy` + `partner_webhook_config.groovy`
- `20260625-init-ebus-*.xml` → `ebus_outbox.groovy` + `ebus_inbox.groovy` + `ebus_dlq.groovy`
- 删除原 XML 文件

### 任务2：M1-M5 业务表 groovy 迁移
从 open-api-service `db/mysql/` 复制 M1-M5 业务表 groovy 到 platform-admin `db/mysql/`：
- M1: `partner.groovy` / `partner_credential.groovy` / `partner_capability.groovy` / `partner_webhook_config.groovy`（与任务1合并，不重复）/ `partner_task_map.groovy`
- M2: `api_invocation.groovy` / `api_operation.groovy`
- M3: `webhook_delivery_log.groovy`（与任务1合并）
- M4: `open_operation_case.groovy`（确认是否含 event/target 子表）
- changeSet id 加 platform-admin 前缀避免与 open-api-service 冲突（如已执行过同 id 会跳过）

### 任务3：partner-gateway 路由转移
修改 `partner-gateway/application.yml`：
- `/oauth/token`、`/api/open/v1/oauth/token` 路由 `uri` 从 `lb://open-api-service` → `lb://platform-admin`
- 其余路由（`/api/open/v1/**`、swagger）不动

### 任务4：建表验证
- 删库重建（或用 H2 测试）确认 groovy 全部执行、表创建成功
- platform-admin `mvn test` 全绿

---

## 4. multi-agent 拆分（2 agent + 验证）

| Agent | 职责 | 独占文件 |
|-------|------|---------|
| **A: 事件表 XML→groovy** | 5 个 XML 转 groovy + 删 XML | platform-admin db/mysql/*.groovy（事件表） |
| **B: 业务表 groovy 迁移 + 路由** | 从 OAS 复制 M1-M5 业务表 groovy + 改 gateway 路由 | platform-admin db/mysql/*.groovy（业务表）+ partner-gateway application.yml |

### 验证 agent
- 删 XML 后 groovy 全部能编译
- platform-admin mvn test 全绿
- gateway 路由确认 oauth 指向 platform-admin

---

## 5. 验收

- platform-admin `db/mysql/` 下只有 `.groovy`，无 `.xml`
- 8 张事件表 + M1-M5 业务表 groovy 齐全
- groovy changeSet id 不与 open-api-service 冲突（或能共存）
- partner-gateway `/oauth/token` 路由指向 platform-admin
- platform-admin mvn test 全绿

---

## 6. 风险

- **changeSet id 冲突**：从 OAS 复制的 groovy 若 id 与 OAS 库已执行记录冲突，Liquibase 会跳过（按 DATABASECHANGELOG 记录）。干净库无此问题。需确认 id 唯一性或加前缀。
- **表结构对齐**：groovy 表结构必须与 platform-admin 的 PO/Mapper 注解（@TableName/@TableId）完全一致，否则运行时报错。需逐一核对。
- **路由转移影响**：oauth 转 platform-admin 后，若 platform-admin 的 PartnerTokenAppServiceImpl 实现有缺陷（M5 留的边界），token 签发会失败。需 M5 已验证（已过 38 测试）。
