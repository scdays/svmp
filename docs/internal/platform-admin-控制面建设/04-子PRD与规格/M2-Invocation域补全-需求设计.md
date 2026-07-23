# M2 Invocation 域补全需求设计

> 版本：v1.0  
> 日期：2026-06-25  
> 上游文档：00-主计划.md  
> 里程碑归属：M2

---

## 1. 背景与目标

### 1.1 背景
platform-admin 作为统一控制面，需要接管 open-api-service 中与调用治理、API 目录管理相关的能力。当前 M0 已完成基础调用记录的事件链路接入，但存在以下缺口：
- 缺少 API 目录（api_operation）的管理能力
- 调用记录不支持详情查询、请求/响应报文二次加载
- 缺少调用统计、Partner 配额与统计的查询能力

### 1.2 目标
- 迁移 open-api-service 的 API 目录管理能力到 platform-admin
- 补全调用记录的详情、请求/响应报文查询能力
- 迁移调用统计、Partner 配额与统计的查询能力
- 保持所有 API 路径与契约不变，前端无感
- 遵循 DDD 四层架构，代码符合 spore-base-ddd 规范

---

## 2. 需求清单

### 2.1 功能性需求（FR）
| 编号 | 需求描述 | 优先级 |
|------|----------|--------|
| FR-1 | 提供 API 目录分页查询接口 | 高 |
| FR-2 | 提供调用记录详情查询接口 | 高 |
| FR-3 | 提供调用记录请求报文按需查询接口 | 高 |
| FR-4 | 提供调用记录响应报文按需查询接口 | 高 |
| FR-5 | 提供 Partner 配额与调用统计分页查询接口 | 高 |

### 2.2 非功能性需求（NFR）
| 编号 | 需求描述 |
|------|----------|
| NFR-1 | 所有查询接口响应时间 < 500ms（P95） |
| NFR-2 | 遵循 DDD 四层架构，代码符合 spore-base-ddd 规范 |
| NFR-3 | mvn test 全绿 |
| NFR-4 | API 路径与契约与 open-api-service 完全一致，前端无感 |

---

## 3. 现状分析

### 3.1 open-api-service 现有实现
open-api-service 已实现完整的调用治理与 API 目录管理能力，包含：
- Domain layer：ApiOperationDO、ApiInvocationDO、IApiCatalogDomainService、IInvocationDomainService 等
- Infra layer：ApiOperationMapper、ApiOperationPO、ApiOperationRepositoryImpl 等
- App layer：IApiCatalogAdminAppService、IInvocationAdminAppService 等
- UI layer：ApiCatalogAdminUI、InvocationAdminUI 等

### 3.2 platform-admin 当前缺口
platform-admin 当前已实现：
- ApiInvocationDO（完整字段）、IApiInvocationRepository、ApiInvocationRepositoryImpl
- 基础的调用记录分页查询（InvocationUi）

但缺少：
- ApiOperationDO、IApiOperationRepository、ApiOperationRepositoryImpl、ApiOperationPO、ApiOperationMapper
- API 目录查询接口（ApiCatalogAdminUI）
- 调用记录详情、请求/响应报文查询接口
- 调用统计相关代码与接口
- 完整的 InvocationAdminUI（当前只有 InvocationUi）

---

## 4. 领域模型设计

### 4.1 ApiOperationDO
| 字段 | 类型 | 说明 |
|------|------|------|
| operationId | String | API 操作 ID（主键） |
| apiVersion | String | API 版本 |
| httpMethod | String | HTTP 方法 |
| pathPattern | String | 路径模式 |
| requiredCapability | String | 所需能力 |
| domain | String | 所属域 |
| status | String | 状态 |
| publishedAt | Date | 发布时间 |
| openapiTag | String | OpenAPI 标签 |
| summary | String | 摘要 |

### 4.2 统计相关结果类
- InvocationDailyTrendStat：调用日趋势统计
- InvocationErrorCodeStat：调用错误码统计
- PartnerInvocationStatsResult：Partner 调用统计结果
- PartnerQuotaStatResult：Partner 配额统计结果

---

## 5. 四层结构设计

### 5.1 UI 层
| 类名 | 路径 | 说明 | 继承基类 |
|------|------|------|----------|
| ApiCatalogAdminUI | com.vtc.platformadmin.ui.invocation.ApiCatalogAdminUI | API 目录管理 UI | BaseUI |
| InvocationAdminUI | com.vtc.platformadmin.ui.invocation.InvocationAdminUI | 调用治理管理 UI | BaseUI |

### 5.2 App 层
| 类名 | 路径 | 说明 | 继承基类 |
|------|------|------|----------|
| IApiCatalogAdminAppService | com.vtc.platformadmin.app.service.IApiCatalogAdminAppService | API 目录 App 服务接口 | - |
| ApiCatalogAdminAppServiceImpl | com.vtc.platformadmin.app.service.impl.ApiCatalogAdminAppServiceImpl | API 目录 App 服务实现 | AppServiceImpl<IApiCatalogDomainService, ApiOperationDO, ApiOperationDTO> |
| IInvocationAdminAppService | com.vtc.platformadmin.app.service.IInvocationAdminAppService | 调用治理 App 服务接口 | - |
| InvocationAdminAppServiceImpl | com.vtc.platformadmin.app.service.impl.InvocationAdminAppServiceImpl | 调用治理 App 服务实现 | AppServiceImpl<IInvocationDomainService, ApiInvocationDO, InvocationDTO> |
| ApiOperationAppConvertor | com.vtc.platformadmin.app.convert.ApiOperationAppConvertor | ApiOperation DTO 转换器 | @Component 注册到 ConvertHelper |

### 5.3 Domain 层
| 类名 | 路径 | 说明 | 继承基类 |
|------|------|------|----------|
| ApiOperationDO | com.vtc.platformadmin.domain.invocation.model.entity.ApiOperationDO | API 操作实体 | BaseDO，@Component @Scope("prototype") |
| IApiCatalogDomainService | com.vtc.platformadmin.domain.invocation.service.business.IApiCatalogDomainService | API 目录领域服务接口 | - |
| ApiCatalogDomainServiceImpl | com.vtc.platformadmin.domain.invocation.service.business.impl.ApiCatalogDomainServiceImpl | API 目录领域服务实现 | DomainServiceImpl<IApiOperationRepository, ApiOperationDO> |
| IApiOperationRepository | com.vtc.platformadmin.domain.invocation.repository.IApiOperationRepository | API 操作仓库接口 | IDatabaseRepository<ApiOperationDO> |
| ApiOperationDomainConvertor | com.vtc.platformadmin.domain.invocation.model.convert.ApiOperationDomainConvertor | ApiOperation DO-PO 转换器 | @Component 注册到 ConvertHelper |

### 5.4 Infra 层
| 类名 | 路径 | 说明 | 继承基类 |
|------|------|------|----------|
| ApiOperationPO | com.vtc.platformadmin.infra.dao.po.ApiOperationPO | API 操作 PO | BasePO |
| ApiOperationMapper | com.vtc.platformadmin.infra.dao.ApiOperationMapper | API 操作 Mapper | IBaseMapper<ApiOperationPO> |
| ApiOperationRepositoryImpl | com.vtc.platformadmin.infra.repository.ApiOperationRepositoryImpl | API 操作仓库实现 | DatabaseRepositoryImpl<ApiOperationMapper, ApiOperationDO, ApiOperationPO> |

---

## 6. 迁移文件清单表

| 源文件路径（open-api-service） | 目标文件路径（platform-admin） | 改动说明 |
|----------------------------------|----------------------------------|----------|
| src/main/java/com/vtc/openapi/domain/open/model/entity/ApiOperationDO.java | src/main/java/com/vtc/platformadmin/domain/invocation/model/entity/ApiOperationDO.java | 改包名，添加 @Component @Scope("prototype") |
| src/main/java/com/vtc/openapi/domain/open/repository/IApiOperationRepository.java | src/main/java/com/vtc/platformadmin/domain/invocation/repository/IApiOperationRepository.java | 改包名，继承 IDatabaseRepository<ApiOperationDO> |
| src/main/java/com/vtc/openapi/domain/open/service/business/IApiCatalogDomainService.java | src/main/java/com/vtc/platformadmin/domain/invocation/service/business/IApiCatalogDomainService.java | 改包名 |
| src/main/java/com/vtc/openapi/domain/open/service/business/impl/ApiCatalogDomainServiceImpl.java | src/main/java/com/vtc/platformadmin/domain/invocation/service/business/impl/ApiCatalogDomainServiceImpl.java | 改包名，继承 DomainServiceImpl<IApiOperationRepository, ApiOperationDO> |
| src/main/java/com/vtc/openapi/infra/dao/po/ApiOperationPO.java | src/main/java/com/vtc/platformadmin/infra/dao/po/ApiOperationPO.java | 改包名 |
| src/main/java/com/vtc/openapi/infra/dao/ApiOperationMapper.java | src/main/java/com/vtc/platformadmin/infra/dao/ApiOperationMapper.java | 改包名 |
| src/main/java/com/vtc/openapi/infra/repository/ApiOperationRepositoryImpl.java | src/main/java/com/vtc/platformadmin/infra/repository/ApiOperationRepositoryImpl.java | 改包名，继承 DatabaseRepositoryImpl<ApiOperationMapper, ApiOperationDO, ApiOperationPO> |
| src/main/java/com/vtc/openapi/domain/open/model/convert/ApiOperationDomainConvertor.java | src/main/java/com/vtc/platformadmin/domain/invocation/model/convert/ApiOperationDomainConvertor.java | 改包名，@Component 注册到 ConvertHelper |
| src/main/java/com/vtc/openapi/app/service/IApiCatalogAdminAppService.java | src/main/java/com/vtc/platformadmin/app/service/IApiCatalogAdminAppService.java | 改包名 |
| src/main/java/com/vtc/openapi/app/service/impl/ApiCatalogAdminAppServiceImpl.java | src/main/java/com/vtc/platformadmin/app/service/impl/ApiCatalogAdminAppServiceImpl.java | 改包名，继承 AppServiceImpl<IApiCatalogDomainService, ApiOperationDO, ApiOperationDTO> |
| src/main/java/com/vtc/openapi/app/convert/ApiOperationAppConvertor.java | src/main/java/com/vtc/platformadmin/app/convert/ApiOperationAppConvertor.java | 改包名，@Component 注册到 ConvertHelper |
| src/main/java/com/vtc/openapi/ui/admin/ApiCatalogAdminUI.java | src/main/java/com/vtc/platformadmin/ui/invocation/ApiCatalogAdminUI.java | 改包名，调整注入的服务类 |
| src/main/java/com/vtc/openapi/ui/admin/InvocationAdminUI.java | src/main/java/com/vtc/platformadmin/ui/invocation/InvocationAdminUI.java | 改包名，调整注入的服务类，去掉 export/artifact 相关接口（不在 M2 范围） |
| src/main/java/com/vtc/openapi/ui/dto/admin/ApiOperationDTO.java | src/main/java/com/vtc/platformadmin/ui/invocation/dto/ApiOperationDTO.java | 改包名 |
| src/main/java/com/vtc/openapi/ui/dto/admin/ApiOperationPageDto.java | src/main/java/com/vtc/platformadmin/ui/invocation/dto/ApiOperationPageDto.java | 改包名 |
| src/main/java/com/vtc/openapi/ui/dto/admin/InvocationDetailDTO.java | src/main/java/com/vtc/platformadmin/ui/invocation/dto/InvocationDetailDTO.java | 改包名 |
| src/main/java/com/vtc/openapi/ui/dto/admin/InvocationRequestBodyDTO.java | src/main/java/com/vtc/platformadmin/ui/invocation/dto/InvocationRequestBodyDTO.java | 改包名 |
| src/main/java/com/vtc/openapi/ui/dto/admin/InvocationResponseBodyDTO.java | src/main/java/com/vtc/platformadmin/ui/invocation/dto/InvocationResponseBodyDTO.java | 改包名 |
| src/main/java/com/vtc/openapi/ui/dto/admin/PartnerQuotaDTO.java | src/main/java/com/vtc/platformadmin/ui/invocation/dto/PartnerQuotaDTO.java | 改包名 |
| src/main/java/com/vtc/openapi/ui/dto/admin/PartnerQuotaPageDto.java | src/main/java/com/vtc/platformadmin/ui/invocation/dto/PartnerQuotaPageDto.java | 改包名 |
| src/main/java/com/vtc/openapi/domain/open/model/query/ApiOperationAdminQuery.java | src/main/java/com/vtc/platformadmin/domain/invocation/model/query/ApiOperationAdminQuery.java | 改包名 |
| src/main/java/com/vtc/openapi/domain/open/model/result/InvocationDailyTrendStat.java | src/main/java/com/vtc/platformadmin/domain/invocation/model/result/InvocationDailyTrendStat.java | 改包名 |
| src/main/java/com/vtc/openapi/domain/open/model/result/InvocationErrorCodeStat.java | src/main/java/com/vtc/platformadmin/domain/invocation/model/result/InvocationErrorCodeStat.java | 改包名 |
| src/main/java/com/vtc/openapi/domain/open/model/result/PartnerInvocationStatsResult.java | src/main/java/com/vtc/platformadmin/domain/invocation/model/result/PartnerInvocationStatsResult.java | 改包名 |
| src/main/java/com/vtc/openapi/domain/open/model/result/PartnerQuotaStatResult.java | src/main/java/com/vtc/platformadmin/domain/invocation/model/result/PartnerQuotaStatResult.java | 改包名 |
| src/main/java/com/vtc/openapi/app/service/IInvocationAdminAppService.java | src/main/java/com/vtc/platformadmin/app/service/IInvocationAdminAppService.java | 改包名（新增，当前 platform-admin 只有 IApiInvocationAppService） |
| src/main/java/com/vtc/openapi/app/service/impl/InvocationAdminAppServiceImpl.java | src/main/java/com/vtc/platformadmin/app/service/impl/InvocationAdminAppServiceImpl.java | 改包名（新增） |

---

## 7. 接口契约

### 7.1 API 目录查询
| 项 | 内容 |
|----|------|
| 路径 | GET /internal/admin/api-operations |
| 方法 | GET |
| 入参 | requiredCapability/capabilityCode, status, openapiTag/tag, domain, operationId, keyword, page, size |
| 出参 | ApiResponse<ApiOperationPageDto> |

### 7.2 调用记录详情查询
| 项 | 内容 |
|----|------|
| 路径 | GET /internal/admin/invocations/{invocationId} |
| 方法 | GET |
| 入参 | invocationId（path variable） |
| 出参 | ApiResponse<InvocationDetailDTO> |

### 7.3 调用记录请求报文查询
| 项 | 内容 |
|----|------|
| 路径 | GET /internal/admin/invocations/{invocationId}/request-body |
| 方法 | GET |
| 入参 | invocationId（path variable） |
| 出参 | ApiResponse<InvocationRequestBodyDTO> |

### 7.4 调用记录响应报文查询
| 项 | 内容 |
|----|------|
| 路径 | GET /internal/admin/invocations/{invocationId}/response-body |
| 方法 | GET |
| 入参 | invocationId（path variable） |
| 出参 | ApiResponse<InvocationResponseBodyDTO> |

### 7.5 Partner 配额与统计查询
| 项 | 内容 |
|----|------|
| 路径 | GET /internal/admin/quotas |
| 方法 | GET |
| 入参 | partnerId, partnerName, status, startedFrom, startedTo, page, size |
| 出参 | ApiResponse<PartnerQuotaPageDto> |

---

## 8. 数据表与 Liquibase

### 8.1 数据表
- api_operation：共享 open-api 库，不重复建表
- api_invocation：共享 open-api 库，已在使用

### 8.2 Liquibase
无需新增 Liquibase 变更，所有表已存在。

---

## 9. 与 EventBus 集成点
无新增 EventBus 集成点，M0 已完成调用记录事件链路接入。

---

## 10. 验收标准

| 编号 | 验收描述 |
|------|----------|
| AC-1 | API 目录分页查询接口可用，返回正确数据 |
| AC-2 | 调用记录详情查询接口可用，返回正确数据 |
| AC-3 | 调用记录请求报文查询接口可用，返回正确数据 |
| AC-4 | 调用记录响应报文查询接口可用，返回正确数据 |
| AC-5 | Partner 配额与统计查询接口可用，返回正确数据 |
| AC-6 | 所有代码遵循 DDD 四层架构，符合 spore-base-ddd 规范 |
| AC-7 | platform-admin mvn test 全绿 |
| AC-8 | API 路径与契约与 open-api-service 完全一致 |

---

## 11. multi-agent 拆分建议

| Agent 编号 | 负责内容 | 依赖 |
|------------|----------|------|
| Agent M2-1 | 迁移 Domain 层代码：ApiOperationDO、IApiOperationRepository、IApiCatalogDomainService 及 impl、ApiOperationDomainConvertor、query/result 类 | - |
| Agent M2-2 | 迁移 Infra 层代码：ApiOperationPO、ApiOperationMapper、ApiOperationRepositoryImpl | Agent M2-1 |
| Agent M2-3 | 迁移 App 层代码：IApiCatalogAdminAppService、ApiCatalogAdminAppServiceImpl、ApiOperationAppConvertor、IInvocationAdminAppService、InvocationAdminAppServiceImpl | Agent M2-1 |
| Agent M2-4 | 迁移 UI 层代码：ApiCatalogAdminUI、InvocationAdminUI、相关 DTO 类 | Agent M2-3 |
| Agent M2-5 | 全量验证：运行 mvn test，检查接口可用性 | Agent M2-1, M2-2, M2-3, M2-4 |

---

## 12. 风险与遗留

### 12.1 风险
- 共享 open-api 库，两边同时读写同一表：迁移后 open-api-service 对应接口应逐步转壳或下线（收口阶段）
- 缺少 export/artifact 相关接口：不在 M2 范围，后续根据需要决定是否迁移

### 12.2 遗留
- export/artifact 相关接口（/internal/admin/exports/{exportId}/download、/internal/admin/artifacts/{artifactId}/download）：不在 M2 范围，暂不迁移
- Webhook 投递闭环：属于 M3 范围，不在 M2 范围
