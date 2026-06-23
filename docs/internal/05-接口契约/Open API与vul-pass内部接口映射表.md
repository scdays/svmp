# Open API ↔ vul-pass 内部接口映射表

> **状态**：✅ 已冻结 — Agent R 2026-06-13 基于 vul-pass 实码确认
> **读者**：open-api-service 后端、联调工程师
> **约束**：Partner 不可见 vul-pass 路径与字段

**契约对齐**：[API 接口文档 §5](../external/网络安全漏洞管理平台%20·%20API%20接口文档V1.0.4.md) 与 [openapi.yaml](../../openapi/v1/openapi.yaml)

---

## 1. 映射原则

| 原则 | 说明 |
|------|------|
| Partner 字段优先 | 对外平台 DTO 以 openapi 为准，不泄漏引擎字段 |
| 归属在 open-api | 所有写操作前校验 `open_vuln_instance.partner_id` |
| 状态机在 Domain | verify/remediate/verify-fix 的前置 stat 在 Domain 校验，再调 vul-pass |
| 以 vul-pass 实码为准 | 以 vul-pass **实际 Controller** 为准（非口头约定，2026-05） |
| **Mock 可切换** | `open-api.engine.adapter-mode=mock` 时走 fixture，**Partner 无感知**；见 [引擎对接与Mock模式方案](./引擎对接与Mock模式方案.md) |

---

## 2. 任务域（OP-OPENAPI-P0 — 已实现）

| Open API | operationId | vul-pass | 说明 |
|----------|-------------|----------|------|
| POST /tasks/vul | createTaskByJson | `POST /vul-scan-task/dispatch` | `SvmpEngineAdapterImpl` |
| POST /tasks/file | createTaskByFile | 同上（XML 解析后转 dispatch） | `ScanTaskXmlParser` |
| GET /tasks/{taskId} | getTask | `GET /vul-scan-task/page2?id=` | 状态映射 PENDING/RUNNING/FINISHED/FAILED |
| GET /tasks | listTasks | 平台表 `open_task`（不穿透） | — |

**配置项**：`open-api.svmp.dispatch.order-id`、`engHashes` 等见 `OpenApiProperties`；联调可用 `adapter-mode=mock`（不依赖 vul-pass）。

---

## 3. 实例域（OP-OPENAPI-P1 — 契约已定义，vul-pass 接口已确认）

### 3.1 读接口

| Open API | operationId | vul-pass 实际接口 | 请求映射 | 响应映射 | 状态 |
|----------|-------------|-------------------|----------|----------|------|
| POST /instances/search | searchInstances | `GET /vul-scan-task-sub-system/page` | 见下方请求映射详表 | `PageInfo<VulScanTaskSubSystemDTO>` → §5.2 items[] | ✅ 已确认 |
| GET /instances/{vulInfoID} | getInstance | `GET /vul-scan-task-sub-system/page`（vulInfoId 过滤） | vulInfoId→`VulInstParam.vulInfoIds`（单值 List） | 同上，取 records[0] | ✅ 已确认 |

**searchInstances 请求映射详表**（`VulInstParam` 字段）：

| Open API 请求字段 | vul-pass `VulInstParam` 字段 | 说明 |
|-------------------|-------------------------------|------|
| taskId | `taskId`（Long） | 必填其一（taskId 或 vul-pass 内部 tskSubId） |
| vulInfoStatList | `vulInfoStat`（List<Integer>） | 漏洞状态过滤 |
| vulNetAddr | `vulNetAddr`（String, LIKE） | 网络地址模糊匹配 |
| assetName | `assetName`（String, LIKE） | 资产名称模糊匹配 |
| vulName | `vulName`（String, LIKE） | 漏洞名称模糊匹配 |
| orgVulId | `orgVulId`（String, LIKE） | CVE 编号模糊匹配 |
| vulId | `vulId`（String） | 产品漏洞 ID 精确匹配 |
| isAccess | `isAccess`（Integer） | 网络位置：0-内网 1-互联网 |
| unitType | `unitType`（String） | 网络单元类型 |
| page / pageSize | `PageRequest.current` / `PageRequest.size` | spore 分页基类 |

**响应映射**（`VulScanTaskSubSystemDTO` → Open API Instance）：

| vul-pass 字段 | Open API 字段 | 说明 |
|---------------|---------------|------|
| `id`（Long, 自增主键） | — | vul-pass 内部主键，不暴露给 Partner |
| `vulInfoId`（String） | `vulInfoID` | 系统漏洞 ID，即 Open API 的 vulInfoID |
| `vulInfoStat`（Integer） | `status` | 状态映射见 §3.2 状态码表 |
| `vulId` | `vulId` | 产品漏洞 ID |
| `orgVulId` | `cveId` | CVE 编号 |
| `vulName` | `vulName` | 漏洞名称 |
| `assetId` | `assetId` | 资产 ID |
| `assetName` | `assetName` | 资产名称 |
| `vulNetAddr` | `vulNetAddr` | 网络层地址 |
| `vulAddrType` | `vulAddrType` | 网络协议类型 |
| `vulTransProto` | `vulTransProto` | 传输协议类型 |
| `vulPort` | `vulPort` | 传输层端口 |
| `vulSvc` | `vulSvc` | 应用层服务名称 |
| `vulInstCpe` | `vulInstCpe` | 组件 CPE |
| `vulInstVendor` | `vulInstVendor` | 组件厂商 |
| `vulInstClass` | `vulInstClass` | 组件大类 |
| `vulInstName` | `vulInstName` | 组件名称 |
| `vulInstVer` | `vulInstVer` | 组件版本 |
| `isAccess` | `isAccess` | 网络位置 |
| `unitType` | `unitType` | 网络单元类型 |
| `method` | `srcMethod` | 处置方式编码 |
| `lvRsn` | `lvRsn` | 未修复原因 |
| `remedDesc` | `remedDesc` | 修复方案说明 |
| `remedTime` | `remedTime` | 修复耗时 |
| `fixLnk` | `fixLnk` | 补丁链接 |
| `createTime` | `createdAt` | 创建时间 |
| `updateTime` | `updatedAt` | 更新时间 |

**分页结构**：vul-pass 返回 `PageInfo<VulScanTaskSubSystemDTO>`，含 `records`、`total`、`current`、`size`，直接映射到 Open API 的 `{ items, total, page, pageSize }`。

### 3.2 写接口（单条）

| Open API | operationId | vul-pass 实际接口 | 状态约束（Open API 侧） | 状态 |
|----------|-------------|-------------------|------------------------|------|
| POST .../verify | verifyInstance | `PUT /vul-scan-task-sub-system` | vulInfoStat∈{0,1} → 2（已验证有效）或 3（已验证误报） | ✅ 已确认 |
| POST .../remediate | remediateInstance | `PUT /vul-scan-task-sub-system` | vulInfoStat∈{2} → 5（已修复） | ✅ 已确认 |
| POST .../verify-fix | verifyFixInstance | `PUT /vul-scan-task-sub-system` | vulInfoStat∈{5} → 6（核验修复）或 7（核验未修复） | ✅ 已确认 |

**vul-pass 写操作关键机制**：

1. vul-pass 的 `PUT /vul-scan-task-sub-system` 调用 `appService.updateById(dto)`
2. **update 时 vulInfoId 被强制置 null**（`dto.setVulInfoId(null)`），通过 `id`（Long 自增主键）定位记录
3. 因此 Open API 调用前**必须先查一次 page 接口**，用 `vulInfoId` 换取 vul-pass 内部 `id`，再带着 `id` 调 PUT
4. vul-pass **没有**独立的 verify/remediate/verify-fix 专用接口，统一走 PUT + 字段更新

**字段映射模板**（写操作）：

| Open API 字段 | vul-pass DTO 字段 | 备注 |
|---------------|-------------------|------|
| — | `id`（Long） | vul-pass 内部主键，由 page 查询获得 |
| vulInfoID | `vulInfoId`（写入时被置 null） | 用于查询，不用于 PUT body |
| status → 目标状态 | `vulInfoStat` | 见下方状态码表 |
| srcMethod | `method` | 处置方式编码 |
| remedDesc | `remedDesc` | 修复时必填 |
| lvRsn | `lvRsn` | 未修复原因 |
| remedTime | `remedTime` | 修复耗时 |
| fixLnk | `fixLnk` | 补丁链接 |

**状态码映射**（`VulStateEnum`）：

| code | vul-pass 枚举 | 含义 | Open API 对应 |
|------|---------------|------|---------------|
| 0 | POTENTIAL_WARNING | 潜在预警 | POTENTIAL_WARNING |
| 1 | INITIAL_DISCOVERY | 初始发现 | INITIAL_DISCOVERY |
| 2 | VALIDATED_TRUE | 已验证有效 | VALIDATED_TRUE |
| 3 | VALIDATED_FALSE | 已验证误报 | VALIDATED_FALSE |
| 5 | FIXED | 已修复 | FIXED |
| 6 | VERIFIED_FIXED | 核验修复 | VERIFIED_FIXED |
| 7 | VERIFIED_UNFIXED | 核验未修复 | VERIFIED_UNFIXED |
| 8 | VALIDATION_FAILED | 验证失败 | VALIDATION_FAILED |
| 9 | FIX_FAILED | 修复失败 | FIX_FAILED |
| 10 | VERIFICATION_FAILED | 核验失败 | VERIFICATION_FAILED |

### 3.3 写接口（批量）

| Open API | operationId | 实现策略 | 状态 |
|----------|-------------|----------|------|
| POST /instances/verify:batch | verifyInstanceBatch | Open API Domain 循环单条 PUT + 聚合 success/failed | ✅ 已确认 |
| POST /instances/remediate:batch | remediateInstanceBatch | 同上 | ✅ 已确认 |
| POST /instances/verify-fix:batch | verifyFixInstanceBatch | 同上 | ✅ 已确认 |

**决策依据**：vul-pass **无原生批量写接口**。Repository 层仅有 `saveBatch`（批量新增），无批量 update。批量写操作在 Open API Domain 层循环调用单条 PUT，聚合结果返回。

---

## 4. 外发域（OP-OPENAPI-P2 — 待设计）

| Open API | operationId | vul-pass / 引擎 | 状态 |
|----------|-------------|-----------------|------|
| GET /exports/{exportId} | getExport | 本地表 `open_export` + vul-pass `POST /vul-scan-task-sub-system/export` 组装 | 🟡 P2 暂留 |
| GET /exports/{exportId}/download | downloadExport | vul-pass 导出结果为 xlsx 流，需落盘或转存 | 🟡 P2 暂留 |
| GET /tasks/{taskId}/exports | listTaskExports | `open_export` 表（不穿透 vul-pass） | 🟡 P2 暂留 |

**vul-pass 导出接口**：`POST /vul-scan-task-sub-system/export`（`VulScanTaskSubSystemUi.export`），参数 `VulInstParam`，直接写入 xlsx 到 `HttpServletResponse`。另有 `POST /vul-scan-task-sub-system/fields` 可查询可导出字段列表。

**注意**：vul-pass 导出是**同步流式写回**，Open API 如需异步导出须自行收集流后落盘。

---

## 5. Webhook 出站（OP-OPENAPI-P1-d）

| 事件 | 触发点 | Partner 侧 |
|------|--------|------------|
| TASK_COMPLETED | 任务 FINISHED | POST defaultCallbackUrl |
| INSTANCE_STATUS_CHANGED | 实例写成功 | 同上 |
| EXPORT_READY | 外发组装完成（P2） | 同上 |

**落库**：`webhook_delivery_log`（列表已有）；**不是** Partner REST。

---

## 6. 决策记录（Agent R 填写）

| # | 问题 | 结论 | 日期 | 决策人 |
|---|------|------|------|--------|
| 1 | 实例写操作是否走 PUT sub-system？ | **是**。vul-pass 只有通用 `PUT /vul-scan-task-sub-system`（`updateById`），无独立 verify/remediate/verify-fix 接口。写操作统一通过修改 `vulInfoStat` + `method` 等字段实现。 | 2026-06-13 | Agent R |
| 2 | vulInfoID 与 vul-pass 主键对应关系 | **vulInfoID ≠ id**。`vulInfoId`（String）是系统漏洞 ID（业务标识），`id`（Long）是自增主键。vul-pass PUT 操作**必须**通过 `id` 定位（update 时 vulInfoId 被置 null），因此 Open API 写操作前须先查 page 接口，用 vulInfoId 换取内部 `id`。 | 2026-06-13 | Agent R |
| 3 | 验证/核验是否需要异步复扫任务 | **不需要（vul-pass 侧）**。vul-pass 的状态变更是同步 PUT 更新，不触发复扫任务。Open API 侧的 verifyFix 语义是"确认修复结果"，直接修改 vulInfoStat 为 6 或 7 即可。若后续需要真实复扫（重新探测），需另行设计。 | 2026-06-13 | Agent R |
| 4 | 外发文件存储位置 | **P2 待定**。vul-pass 导出接口 `POST /export` 为同步流式写 xlsx，Open API 需收集后落盘到文件存储（如 MinIO/本地），再通过 download 接口提供下载。具体存储方案 P2 阶段确定。 | 2026-06-13 | Agent R |
| 5 | 联调周是否默认 mock | **是**；生产 fixture 到位后热替换 bundle | 2026-05-21 | — |
| 6 | 批量写实现策略 | **Open API Domain 循环单条 PUT**。vul-pass 无批量 update 接口（Repository 仅有 saveBatch 批量新增）。循环中捕获单条失败，聚合返回 `{ success: [...], failed: [...] }`。 | 2026-06-13 | Agent R |

---

## 7. Mock 模式（联调优先）

| 项 | mock | vul-pass |
|----|------|----------|
| 配置 | `open-api.engine.adapter-mode=mock` | `vul-pass` |
| 任务进度 | 模拟 FINISHED | Feign 查 vul-pass |
| 实例读 | `open_vuln_instance` ← fixture 入库 | Feign `GET /vul-scan-task-sub-system/page` |
| 实例写 | 仅本地状态机 | Feign `PUT /vul-scan-task-sub-system`（需先查 id） |
| 批量写 | Domain 循环 mock 写 | Domain 循环 Feign 单条 PUT |
| 文档 | [引擎对接与Mock模式方案.md](./引擎对接与Mock模式方案.md) | 本节 §3 |

---

## 8. 变更日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 0.1 | 2026-05-21 | 骨架；待确认项由 Agent R 冻结 |
| 0.2 | 2026-05-21 | 增加 Mock 模式；联调周默认 mock |
| 0.3 | 2026-06-13 | Agent R 冻结全部 P1 项：§3.1 读接口映射、§3.2 写接口路径与状态约束、§3.3 批量策略、§6 决策记录 #1-#6；§4 外发域保留 🟡（P2） |

---

## 附录 A. vul-pass 实例相关源码索引

| 层级 | 文件路径 | 说明 |
|------|----------|------|
| UI (Controller) | `ui/pass/v3/VulScanTaskSubSystemUi.java` | `@RequestMapping("/vul-scan-task-sub-system")` |
| UI (Controller) | `ui/pass/v3/VulArchiveInstUI.java` | `@RequestMapping("/vul-archive-inst")`，系统漏洞档案库 |
| AppService 接口 | `app/service/IVulScanTaskSubSystemAppService.java` | page / export / getExportFields |
| AppService 实现 | `app/service/impl/VulScanTaskSubSystemAppServiceImpl.java` | 含 page、export 实现 |
| DomainService | `domain/pass/service/business/IVulScanTaskSubSystemDomainService.java` | 标准 DDD 基类 |
| DomainService 实现 | `domain/pass/service/business/impl/VulScanTaskSubSystemDomainServiceImpl.java` | 标准 DDD 基类 |
| Repository 接口 | `domain/pass/repository/IVulScanTaskSubSystemRepository.java` | saveBatch / listByTaskIdList / pageList |
| Repository 实现 | `infra/repository/VulScanTaskSubSystemRepositoryImpl.java` | 含 pageList 查询条件 |
| DTO | `ui/dto/VulScanTaskSubSystemDTO.java` | 完整字段定义 |
| DO | `domain/pass/model/entity/VulScanTaskSubSystemDO.java` | 领域模型 |
| PO | `infra/dao/po/VulScanTaskSubSystemPO.java` | `@TableName("vul_scan_task_sub_system")` |
| Mapper | `infra/dao/VulScanTaskSubSystemMapper.java` | MyBatis Mapper |
| Mapper XML | `resources/mapper/VulScanTaskSubSystemMapper.xml` | SQL 映射 |
| 参数类 | `ui/params/VulInstParam.java` | 分页查询参数 |
| 状态枚举 | `infra/utils/dict/VulStateEnum.java` | 漏洞生命周期状态（0-10） |
