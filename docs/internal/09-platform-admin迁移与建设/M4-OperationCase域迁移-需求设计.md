# M4 OperationCase 域迁移 · 需求设计文档

> **版本**：v1.1  
> **日期**：2026-06-25（原设计）/ 2026-06-29（回退）  
> **上游文档**：
> - `00-主计划.md`
> - `03-落地方案/开放平台运营案件-open_operation_case-方案.md`
> - `M4-回退方案.md`（回退记录）
> **里程碑归属**：M4 OperationCase 域迁移
> **状态**：🔄 已回退 — OperationCase 域已迁回 open-api-service，详见 M4-回退方案.md

---

## 1. 背景与目标

### 1.1 背景

| 现状 | 问题 |
|------|------|
| open-api-service 已有完整的 OperationCase 域实现（运营案件壳、工作台、多类型聚合） | 该域尚未迁入 platform-admin |
| platform-admin 定位为统一控制面/管理面 | 运营案件作为核心管理能力缺失 |
| OperationCase 域依赖 M1/M2/M3（Partner/Invocation/Webhook） | 依赖关系清晰 |

### 1.2 目标

1. **代码搬迁 + 路径保持**：将 open-api-service 的 OperationCase 域完整迁入 platform-admin，Controller 路径不变（前端无感）
2. **包名映射**：`com.vtc.openapi` → `com.vtc.platformadmin`
3. **DDD 四层合规**：所有代码必须遵循 spore-base-ddd 基类与规则
4. **共享库不迁库**：过渡期与 open-api-service 共享 `open_api` 库，不重复建表
5. **核心功能完整**：运营案件列表、统一工作台、历史回填、重试下发功能均可用

---

## 2. 需求清单

### 2.1 功能性需求

| 编号 | 需求 | 说明 |
|------|------|------|
| FR-4.1 | 运营案件列表 | 支持按 partnerId/caseType/status/primaryResourceId/caseId/时间范围分页查询 |
| FR-4.2 | 统一工作台 | 按 caseId 聚合案件基本信息、时间线（event）、目标（target）、调用记录、webhook，以及按 caseType 的业务 payload |
| FR-4.3 | 历史数据回填 | 支持对历史数据回填 case_id |
| FR-4.4 | 运营重试下发 | 支持对 TASK_SCAN 和 VERIFY_FIX 类型的案件重试下发 |
| FR-4.5 | 多类型支持 | 支持 TASK_SCAN/INSTANCE_VERIFY/INSTANCE_REMEDIATE/VERIFY_FIX/INSTANCE_BATCH 五种案件类型 |

### 2.2 非功能性需求

| 编号 | 需求 | 说明 |
|------|------|------|
| NFR-4.1 | DDD 合规 | 严格遵循 DDD 四层架构与 spore-base-ddd 基类规则 |
| NFR-4.2 | 编译通过 | `mvn compile` 全绿 |
| NFR-4.3 | 路径不变 | Controller 路径保持 `/internal/admin/operation-cases` 不变，前端无感 |
| NFR-4.4 | 数据共享 | 过渡期共享 open_api 库，不重复建表 |

---

## 3. 现状分析

### 3.1 open-api-service 现有实现（实证）

| 层次 | 文件 | 路径 |
|------|------|------|
| **Domain 层** | OpenOperationCaseDO.java | domain/operationcase/model/entity/ |
| | OpenOperationCaseEventDO.java | domain/operationcase/model/entity/ |
| | OpenOperationCaseTargetDO.java | domain/operationcase/model/entity/ |
| | OperationCaseTypes.java | domain/operationcase/model/ |
| | OperationCaseStatuses.java | domain/operationcase/model/ |
| | OperationCaseEventTypes.java | domain/operationcase/model/ |
| | OperationCaseAdminQuery.java | domain/operationcase/model/query/ |
| | OperationCaseSupport.java | domain/operationcase/model/support/ |
| | OperationCaseContext.java | domain/operationcase/context/ |
| | IOpenOperationCaseRepository.java | domain/operationcase/repository/ |
| | IOperationCaseDomainService.java | domain/operationcase/service/business/ |
| | OperationCaseDomainServiceImpl.java | domain/operationcase/service/business/impl/ |
| | OperationCaseBackfillService.java | domain/operationcase/service/business/impl/ |
| | *DomainConvertor.java x3 | domain/operationcase/model/convert/ |
| **App 层** | IOperationCaseAdminAppService.java | app/service/ |
| | OperationCaseAdminAppServiceImpl.java | app/service/impl/ |
| | OperationCaseWorkspaceAssembler.java | app/service/impl/ |
| **Infra 层** | OpenOperationCaseRepositoryImpl.java | infra/repository/ |
| | OpenOperationCaseMapper.java | infra/dao/ |
| | OpenOperationCaseEventMapper.java | infra/dao/ |
| | OpenOperationCaseTargetMapper.java | infra/dao/ |
| | *PO.java x3 | infra/dao/po/ |
| **UI 层** | OperationCaseAdminUI.java | ui/admin/ |
| | *Dto.java x11 | ui/dto/admin/ |

### 3.2 platform-admin 当前缺口（实证）

| 层次 | 现状 | 缺口 |
|------|------|------|
| **Domain 层** | 无文件 | 完全缺失 |
| **App 层** | 无文件 | 完全缺失 |
| **Infra 层** | 无文件 | 完全缺失 |
| **UI 层** | 无文件 | 完全缺失 |

---

## 4. 领域模型设计

### 4.1 DO 字段表

#### OpenOperationCaseDO

| 字段 | 类型 | 说明 |
|------|------|------|
| caseId | String | PK，案件 ID |
| partnerId | String | Partner ID |
| caseType | String | 案件类型（见 OperationCaseTypes） |
| status | String | 状态（见 OperationCaseStatuses） |
| title | String | 运营列表展示标题 |
| primaryResourceType | String | 主资源类型 |
| primaryResourceId | String | 主资源 ID |
| batchId | String | 批量幂等批次 |
| invocationId | String | 受理 API 调用 ID |
| idempotencyKey | String | 幂等键 |
| requestSummaryJson | String | 请求摘要（脱敏） |
| resultSummaryJson | String | 结果摘要 |
| errorMessage | String | 失败原因 |
| startedAt | Date | 开始时间 |
| finishedAt | Date | 结束时间 |
| createdAt | Date | 创建时间 |
| updatedAt | Date | 更新时间 |

#### OpenOperationCaseEventDO

| 字段 | 类型 | 说明 |
|------|------|------|
| caseId | String | 所属案件 ID |
| eventType | String | 事件类型（见 OperationCaseEventTypes） |
| eventPayloadJson | String | 事件载荷 |
| createdAt | Date | 创建时间 |

#### OpenOperationCaseTargetDO

| 字段 | 类型 | 说明 |
|------|------|------|
| caseId | String | 所属案件 ID |
| targetKey | String | 目标键（如 vul_info_id） |
| targetStatus | String | 目标状态 |
| prevStat | String | 前序状态 |
| resultStat | String | 结果状态 |
| payloadJson | String | 载荷 |
| createdAt | Date | 创建时间 |

### 4.2 枚举/常量

| 枚举类 | 枚举值 |
|--------|--------|
| OperationCaseTypes | TASK_SCAN/INSTANCE_VERIFY/INSTANCE_REMEDIATE/VERIFY_FIX/INSTANCE_BATCH |
| OperationCaseStatuses | ACCEPTED/RUNNING/FINISHED/FAILED/PARTIAL_FAILED/CANCELLED |
| OperationCaseEventTypes | ACCEPTED/DISPATCHED/SUB_FINISHED/STATE_CHANGED/WEBHOOK_SENT |

### 4.3 值对象/Context

| 类 | 说明 |
|----|------|
| OperationCaseAdminQuery | 管理端查询条件 |
| OperationCaseContext | 案件上下文 |
| OperationCaseSupport | 支持类 |

---

## 5. 四层结构设计

### 5.1 类清单与继承关系

| 层次 | 类名 | 继承基类 | 说明 |
|------|------|----------|------|
| **UI 层** | OperationCaseAdminUI | BaseUI | 运营案件管理 UI |
| **App 层** | IOperationCaseAdminAppService | - | App Service 接口 |
| | OperationCaseAdminAppServiceImpl | AppServiceImpl&lt;DS, DO, DTO&gt; | App Service 实现 |
| | OperationCaseWorkspaceAssembler | - | 工作台聚合器 |
| **Domain 层** | IOperationCaseDomainService | - | Domain Service 接口 |
| | OperationCaseDomainServiceImpl | DomainServiceImpl&lt;Repository, DO&gt; | Domain Service 实现 |
| | OperationCaseBackfillService | - | 历史回填服务 |
| | IOpenOperationCaseRepository | IDatabaseRepository&lt;DO&gt; | Repository 接口 |
| | OpenOperationCaseDO | BaseDO + @Component + @Scope("prototype") | 案件 DO |
| | OpenOperationCaseEventDO | BaseDO + @Component + @Scope("prototype") | 事件 DO |
| | OpenOperationCaseTargetDO | BaseDO + @Component + @Scope("prototype") | 目标 DO |
| | *DomainConvertor x3 | @Component + 注册到 ConvertHelper | DO ↔ PO 转换器 |
| **Infra 层** | OpenOperationCaseRepositoryImpl | DatabaseRepositoryImpl&lt;Mapper, DO, PO&gt; | Repository 实现 |
| | OpenOperationCaseMapper | - | MyBatis Mapper |
| | OpenOperationCaseEventMapper | - | MyBatis Mapper |
| | OpenOperationCaseTargetMapper | - | MyBatis Mapper |
| | *PO x3 | - | 持久化对象 |

### 5.2 标准调用链

```
OperationCaseAdminUI 
  → OperationCaseAdminAppServiceImpl 
    → OperationCaseDomainServiceImpl 
      → OpenOperationCaseRepositoryImpl 
        → OpenOperationCaseMapper + OpenOperationCaseEventMapper + OpenOperationCaseTargetMapper
```

---

## 6. 迁移文件清单表

| 来源路径（open-api-service） | 目标路径（platform-admin） | 改动说明 |
|-----------------------------|---------------------------|---------|
| domain/operationcase/model/entity/OpenOperationCaseDO.java | domain/operationcase/model/entity/OpenOperationCaseDO.java | 改包名 + 加 @Component + @Scope("prototype") |
| domain/operationcase/model/entity/OpenOperationCaseEventDO.java | domain/operationcase/model/entity/OpenOperationCaseEventDO.java | 改包名 + 加 @Component + @Scope("prototype") |
| domain/operationcase/model/entity/OpenOperationCaseTargetDO.java | domain/operationcase/model/entity/OpenOperationCaseTargetDO.java | 改包名 + 加 @Component + @Scope("prototype") |
| domain/operationcase/model/OperationCaseTypes.java | domain/operationcase/model/OperationCaseTypes.java | 改包名 |
| domain/operationcase/model/OperationCaseStatuses.java | domain/operationcase/model/OperationCaseStatuses.java | 改包名 |
| domain/operationcase/model/OperationCaseEventTypes.java | domain/operationcase/model/OperationCaseEventTypes.java | 改包名 |
| domain/operationcase/model/query/OperationCaseAdminQuery.java | domain/operationcase/model/query/OperationCaseAdminQuery.java | 改包名 |
| domain/operationcase/model/support/OperationCaseSupport.java | domain/operationcase/model/support/OperationCaseSupport.java | 改包名 |
| domain/operationcase/context/OperationCaseContext.java | domain/operationcase/context/OperationCaseContext.java | 改包名 |
| domain/operationcase/repository/IOpenOperationCaseRepository.java | domain/operationcase/repository/IOpenOperationCaseRepository.java | 改包名 + 继承 IDatabaseRepository&lt;DO&gt; |
| domain/operationcase/service/business/IOperationCaseDomainService.java | domain/operationcase/service/business/IOperationCaseDomainService.java | 改包名 |
| domain/operationcase/service/business/impl/OperationCaseDomainServiceImpl.java | domain/operationcase/service/business/impl/OperationCaseDomainServiceImpl.java | 改包名 + 继承 DomainServiceImpl&lt;Repository, DO&gt; |
| domain/operationcase/service/business/impl/OperationCaseBackfillService.java | domain/operationcase/service/business/impl/OperationCaseBackfillService.java | 改包名 |
| domain/operationcase/model/convert/OpenOperationCaseDomainConvertor.java | domain/operationcase/model/convert/OpenOperationCaseDomainConvertor.java | 改包名 + 加 @Component + 注册到 ConvertHelper |
| domain/operationcase/model/convert/OpenOperationCaseEventDomainConvertor.java | domain/operationcase/model/convert/OpenOperationCaseEventDomainConvertor.java | 改包名 + 加 @Component + 注册到 ConvertHelper |
| domain/operationcase/model/convert/OpenOperationCaseTargetDomainConvertor.java | domain/operationcase/model/convert/OpenOperationCaseTargetDomainConvertor.java | 改包名 + 加 @Component + 注册到 ConvertHelper |
| app/service/IOperationCaseAdminAppService.java | app/service/IOperationCaseAdminAppService.java | 改包名 |
| app/service/impl/OperationCaseAdminAppServiceImpl.java | app/service/impl/OperationCaseAdminAppServiceImpl.java | 改包名 + 继承 AppServiceImpl&lt;DS, DO, DTO&gt; |
| app/service/impl/OperationCaseWorkspaceAssembler.java | app/service/impl/OperationCaseWorkspaceAssembler.java | 改包名 |
| infra/repository/OpenOperationCaseRepositoryImpl.java | infra/repository/OpenOperationCaseRepositoryImpl.java | 改包名 + 继承 DatabaseRepositoryImpl&lt;Mapper, DO, PO&gt; |
| infra/dao/OpenOperationCaseMapper.java | infra/dao/OpenOperationCaseMapper.java | 改包名 |
| infra/dao/OpenOperationCaseEventMapper.java | infra/dao/OpenOperationCaseEventMapper.java | 改包名 |
| infra/dao/OpenOperationCaseTargetMapper.java | infra/dao/OpenOperationCaseTargetMapper.java | 改包名 |
| infra/dao/po/OpenOperationCasePO.java | infra/dao/po/OpenOperationCasePO.java | 改包名 |
| infra/dao/po/OpenOperationCaseEventPO.java | infra/dao/po/OpenOperationCaseEventPO.java | 改包名 |
| infra/dao/po/OpenOperationCaseTargetPO.java | infra/dao/po/OpenOperationCaseTargetPO.java | 改包名 |
| ui/admin/OperationCaseAdminUI.java | ui/admin/OperationCaseAdminUI.java | 改包名 + 保持路径不变 |
| ui/dto/admin/OperationCaseAdminDto.java | ui/dto/admin/OperationCaseAdminDto.java | 改包名 |
| ui/dto/admin/OperationCaseAdminPageDto.java | ui/dto/admin/OperationCaseAdminPageDto.java | 改包名 |
| ui/dto/admin/OperationCaseWorkspaceDto.java | ui/dto/admin/OperationCaseWorkspaceDto.java | 改包名 |
| ui/dto/admin/OperationCaseEventDto.java | ui/dto/admin/OperationCaseEventDto.java | 改包名 |
| ui/dto/admin/OperationCaseTaskScanPayloadDto.java | ui/dto/admin/OperationCaseTaskScanPayloadDto.java | 改包名 |
| ui/dto/admin/OperationCaseInstancePayloadDto.java | ui/dto/admin/OperationCaseInstancePayloadDto.java | 改包名 |
| ui/dto/admin/OperationCaseVerifyFixPayloadDto.java | ui/dto/admin/OperationCaseVerifyFixPayloadDto.java | 改包名 |
| ui/dto/admin/OperationCaseBatchPayloadDto.java | ui/dto/admin/OperationCaseBatchPayloadDto.java | 改包名 |
| ui/dto/admin/OperationCaseBatchTargetDto.java | ui/dto/admin/OperationCaseBatchTargetDto.java | 改包名 |
| ui/dto/admin/OperationCaseBackfillResultDto.java | ui/dto/admin/OperationCaseBackfillResultDto.java | 改包名 |
| ui/dto/admin/OperationCaseActionResultDto.java | ui/dto/admin/OperationCaseActionResultDto.java | 改包名 |

---

## 7. 接口契约

### 7.1 运营案件列表

```java
GET /internal/admin/operation-cases
  ?partnerId=&caseType=&status=&primaryResourceId=&caseId=&startedFrom=&startedTo=&page=&size=

// 响应
ApiResponse<OperationCaseAdminPageDto>
```

### 7.2 统一工作台

```java
GET /internal/admin/operation-cases/{caseId}/workspace

// 响应
ApiResponse<OperationCaseWorkspaceDto>
/*
{
  "case": { ... },
  "summary": { ... },
  "timeline": [ ... ],
  "invocations": [ ... ],
  "webhooks": [ ... ],
  "stateLogs": [ ... ],
  "payload": { } // 按 caseType 多态
}
*/
```

### 7.3 历史数据回填

```java
POST /internal/admin/operation-cases/backfill
  ?partnerId=&limit=&dryRun=

// 响应
ApiResponse<OperationCaseBackfillResultDto>
```

### 7.4 运营重试下发

```java
POST /internal/admin/operation-cases/{caseId}/actions/retry-dispatch
  ?scanPhase=&subId=

// 响应
ApiResponse<OperationCaseActionResultDto>
```

---

## 8. 数据表与 Liquibase

| 表名 | 说明 | 迁移状态 |
|------|------|---------|
| open_operation_case | 运营案件主表 | 共享 open_api 库，不重复建表 |
| open_operation_case_event | 运营案件事件表 | 共享 open_api 库，不重复建表 |
| open_operation_case_target | 运营案件目标表 | 共享 open_api 库，不重复建表 |

**注**：过渡期与 open-api-service 共享 open_api 库，不执行 Liquibase 变更。收口期再考虑物理迁库。

---

## 9. 与 EventBus 集成点

M4 OperationCase 域与 EventBus 的集成主要在过渡期：
- 业务写操作仍由 open-api-service 执行，产生事件
- platform-admin 作为管理面只读查询
- **无新增 EventBus 集成需求**

---

## 10. 验收标准

| 编号 | 验收标准 | 验证方式 |
|------|----------|---------|
| AC-4.1 | `mvn compile` 全绿 | 执行 mvn compile |
| AC-4.2 | 运营案件列表接口可用，支持所有筛选条件 | 手动/自动测试 |
| AC-4.3 | 统一工作台接口可用，正确聚合案件/event/target/invocation/webhook | 手动/自动测试 |
| AC-4.4 | 历史回填接口可用 | 手动/自动测试 |
| AC-4.5 | 重试下发接口可用 | 手动/自动测试 |
| AC-4.6 | Controller 路径保持 `/internal/admin/operation-cases` 不变 | 检查代码 |
| AC-4.7 | 所有代码符合 DDD 四层合规规则 | 代码审查 |

---

## 11. multi-agent 拆分建议

### 11.1 Agent 拆分方案

| Agent | 负责文件 | 依赖 |
|-------|---------|------|
| **Agent 4A**：Domain 层 DO/枚举/Context/Query/Support | 8 个文件 | 无 |
| **Agent 4B**：Domain 层 Repository/DomainService/BackfillService + Convertor | 7 个文件 | Agent 4A |
| **Agent 4C**：Infra 层 RepositoryImpl/Mapper/PO | 8 个文件 | Agent 4A、4B |
| **Agent 4D**：App 层 AppService/WorkspaceAssembler + UI 层 UI/DTO | 17 个文件 | Agent 4A、4B、4C |
| **Agent 4E**：收尾与验证 | 编译测试 + 验证 | Agent 4A-4D |

### 11.2 执行顺序

1. Agent 4A 完成 Domain 层基础文件
2. Agent 4B 完成 Domain 层核心业务逻辑
3. Agent 4C 完成 Infra 层持久化
4. Agent 4D 完成 App 层与 UI 层
5. Agent 4E 验证全链路

---

## 12. 风险与遗留

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| OperationCaseWorkspaceAssembler 依赖 open-api-service 的 mock/vul-pass 业务面 | 过渡期可能需要调用 open-api-service 接口获取业务 payload | 保持过渡期调用 open-api-service 接口，收口期再统一 |
| 共享 open_api 库，两边同时读写 | 数据一致性风险 | 过渡期 open-api-service 为主写，platform-admin 只读；收口期再统一 |
| OperationCaseBackfillService 依赖历史数据 | 回填逻辑复杂 | 保持现有实现，dryRun 模式先行 |
| M4 依赖 M1/M2/M3 | 必须等待前序里程碑完成 | 按主计划顺序执行，M1→M2→M3→M4 |
