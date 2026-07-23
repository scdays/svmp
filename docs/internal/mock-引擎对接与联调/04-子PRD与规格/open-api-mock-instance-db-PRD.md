# Mock 实例 MySQL 落库（方案一）产品需求文档（PRD）

> **用途**：Multi-Agent / 全自动开发编排输入。任务矩阵见 `features/op-mock-p1-db.yaml`
>
> **状态**：`草稿` | 待执行

| 属性 | 值 |
|------|-----|
| 功能编号 | **OP-MOCK-P1-DB** |
| 模块名称 | 开放平台 Mock 实例持久化（MySQL） |
| 目标阶段 | P1 |
| 主工程 | `open-api-service` |
| 运行 | `spring.profiles.active=mock`、`open-api.engine.adapter-mode=mock` |
| 参考 | 附录 H 扫描/报告模板；`NsfocusXmlParserV4` fixture；`open_vuln_instance` 表已建但未接业务 |

---

## 1. Why — 背景与目标

### 1.1 背景

当前 Mock 模式下：

- **扫描样本**：在 `mock/engine/bundles/*/instances.json`，classpath 重启可加载，**不丢**
- **开放平台任务**：写入 MySQL `open_task`，**不丢**
- **实例查询**每次从内存 fixture 读取，**不落库**；修改写在 `VulnInstanceGatewayMockImpl` 内存 Map，**重启丢失**
- Mock **引擎任务进度**在 `SvmpEngineAdapterMockImpl` 内存 Map，重启后 `engineTaskId` 可能查失败
- 配置项 `open-api.engine.mock.auto-ingest-instances-on-finish=true` **尚未实现**；`open_vuln_instance` **无 Repository/Mapper**

接入方联调需要：**创建任务 → 等待完成 → 分页查实例 → 改状态 → 重启服务 → 数据仍在**，不能仅靠内存。

### 1.2 目标

1. 任务 **FINISHED** 后，将 Mock 扫描结果**一次性写入 MySQL**，与 `open_task` 生命周期一致
2. Mock 模式实例**读**优先查库；**写**更新库表，不再依赖内存 Map
3. 服务重启后历史任务、实例与状态变更**可继续查询与处置**
4. 表结构与 `adapter-mode=vul-pass` **共用**，Mock 仅替换数据来源与 ingest 路径

### 1.3 成功标准

| 指标 | 标准 |
|------|------|
| 数据完整性 | `scanTemplateId=1001` 任务完成后 `open_vuln_instance` 条数与 fixture 一致（约 500 条），可按 `taskId`/`extTaskId` 过滤 |
| 契约一致性 | 对外实例列表、详情、`vulInfoStat` 与改造前一致 |
| 写操作持久化 | 处置/修改状态后为库表新值 |
| 性能 | 单任务 500 条 ingest ≤ 3s；列表 P95 ≤ 500ms |
| 幂等 | 同一 `taskId` 重复 ingest 不产生重复行、不报错 |

### 1.4 不做边界

- 不做 vul-pass 真实实例面（`adapter-mode=vul-pass` 另 PRD）
- 不做 Redis 缓存（本期以库 + fixture 为准，后续可加）
- 不修改现有 XML 解析与 import 脚本逻辑
- 不做 Partner 实例迁移工具

---

## 2. Who — 角色与用户

| 角色 | 说明 | 核心操作 |
|------|------|----------|
| 接入方开发者 | 调用 Open API | 创建任务、查实例、处置/修改 |
| 平台联调工程师 | 内部 Mock 联调 | 配置 bundle、验证条数 |
| 运营/管理员 | 控制台（可选） | 查看 ingest 状态 |

---

## 3. What — 功能范围

### 3.1 用户故事

| ID | 行为者 | 我希望… | 以便… |
|----|-------|---------|-------|
| US-01 | 接入方 | 任务完成后实例自动落库 | 不依赖进程内存 |
| US-02 | 接入方 | 按 extTaskId/taskId 查实例 | 符合 API §5.2 |
| US-03 | 接入方 | 处置/修改状态持久化 | 重启后仍可继续流程 |
| US-04 | 联调工程师 | 1001/1002/1003 模板命中对应数据 | 模板 Mock 验收 |
| US-05 | 联调工程师 | ingest 失败可感知 | 便于排查 |
| US-06 | 运维 | 重启后任务进度仍为 FINISHED | 避免 engine task not found |

### 3.2 接口范围（经 Partner Gateway）

| API | 变更 |
|-----|------|
| POST /tasks | 完成后触发 ingest |
| GET /tasks/{taskId} | FINISHED 响应可依赖库 |
| POST /instances/search | Mock 读 `open_vuln_instance` |
| GET /instances/{vulInfoId} | Mock 读库 + snapshot |
| PUT 核验/处置/验证修复 | Mock 更新库表 |

### 3.3 扫描模板 Mock 对照

| scanTemplateId | reportTemplateId | type | bundle | 说明 |
|----------------|------------------|------|--------|------|
| 1001 | 2001/2002 | 1,2 | scan-1001-vul | 漏洞扫描结果约 500 条 |
| 1001 | 2001/2002 | 3 | scan-1001-pwd | 弱口令 |
| 1002 | 2001/2002 | 1–3 | scan-1002-live | 存活探测 |
| 1003 | 2001/2002 | 1–3 | scan-1003-port | 端口 appendix |

### 3.4 状态与异常

| 场景 | 处理 |
|------|------|
| FINISHED 无匹配 bundle | 记录 ingest 失败，实例查询为空 |
| 重复 ingest | 幂等跳过 |
| auto-ingest=false | 不落库；可回退读 fixture |
| 重启后 Mock 引擎 | 读 `open_task`，不再依赖内存 taskStates |

---

## 4. How — 技术方案

### 4.1 数据模型扩展

**`open_vuln_instance` 新增字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | VARCHAR(64) | 平台 taskId |
| `ext_task_id` | VARCHAR(128) | Partner 幂等键 |
| `scan_template_id` | INT | 扫描模板 |
| `report_template_id` | INT | 报告模板 |
| `bundle_id` | VARCHAR(64) | mock bundle 来源 |
| `ingest_status` | VARCHAR(16) | SUCCESS/FAILED/SKIPPED |
| `ingest_at` | DATETIME | 入库时间 |

**索引**：`(partner_id, task_id)`、`(partner_id, ext_task_id)`

**`vul_info_id`**：入库时生成平台唯一 ID，含 `taskId` 前缀，避免跨任务 UK 冲突

**`open_task` 可选扩展**：`instances_ingested`、`ingest_error`

### 4.2 模块改动

| 模块 | 改动 |
|------|------|
| `OpenTaskDomainServiceImpl.mergeEngineProgress` | 首次 FINISHED 触发 ingest |
| **新增** `InstanceIngestDomainService` | fixture → 批量入库 |
| **新增** `OpenVulnInstanceRepository` | CRUD + 分页 |
| `VulnInstanceGatewayMockImpl` | 读/写改库；移除内存 overrides |
| `SvmpEngineAdapterMockImpl` | 任务进度读 `open_task` |

### 4.3 配置

| 配置 | 默认 | 说明 |
|------|------|------|
| `open-api.engine.mock.auto-ingest-instances-on-finish` | true | 关闭则保持 fixture 读 |

---

## 5. 验收标准

| 编号 | 预期 |
|------|------|
| AC-01 | 1001+type1 FINISHED 后约 500 条落库 |
| AC-02 | 经网关 search 与 fixture 一致 |
| AC-03 | 处置后 GET 状态为库值 |
| AC-04 | type3 弱口令条数正确 |
| AC-05 | 1002/1003 模板条数正确 |
| AC-06 | 重启后 GET 任务仍为 FINISHED |
| AC-07 | 重复 ingest 幂等 |
| AC-08 | auto-ingest=false 不落库 |

---

## 6. 里程碑与排期

| 阶段 | 内容 | 工期 |
|------|------|------|
| M1 | DDL + PO/Mapper/Repository | 1–2d |
| M2 | Ingest + mergeEngineProgress | 2d |
| M3 | Mock 网关读写库 | 2d |
| M4 | 重启恢复 + AC 全通过 | 1d |

---

## 7. 附录

- Mock bundle：`open-api-service/src/main/resources/mock/engine/bundles/`
- 导入脚本：`svmp/docs/internal/scripts/import-nsfocus-xml-to-mock-bundle.py`
- Mock 总方案：`svmp/docs/internal/引擎对接与Mock模式方案.md`
- API 附录 H：`svmp/docs/external/网络安全漏洞管理平台 · API 接口文档V1.0.4.md`
- 任务矩阵：`svmp/docs/internal/features/op-mock-p1-db.yaml`
- Multi-Agent Prompts：`svmp/docs/internal/multi-agent-执行Prompts-Mock-P1-DB.md`
