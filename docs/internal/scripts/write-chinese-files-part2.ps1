$utf8Bom = [System.Text.UTF8Encoding]::new($true)
$base = "d:\application\solo\3.0\project_backend\svmp\open-api-service\src\main\java\com\vtc\openapi"

# --- OpenInstanceAppServiceImpl ---
$f = "$base\app\service\impl\OpenInstanceAppServiceImpl.java"
$c = @"
package com.vtc.openapi.app.service.impl;

import com.vtc.openapi.app.open.InvocationPipeline;
import com.vtc.openapi.app.service.IOpenInstanceAppService;
import com.vtc.openapi.domain.instance.model.command.RemediateInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.VerifyFixInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.VerifyInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;
import com.vtc.openapi.domain.instance.model.result.InstanceStateResult;
import com.vtc.openapi.domain.instance.service.business.IInstanceDomainService;
import com.vtc.openapi.domain.open.OpenApiConstants;
import com.vtc.openapi.domain.open.OpenApiException;
import com.vtc.openapi.domain.open.OpenApiOperations;
import com.vtc.openapi.domain.partner.context.PartnerContext;
import com.vtc.openapi.ui.dto.ApiResponse;
import com.vtc.openapi.ui.dto.open.instance.InstanceBatchFailedItem;
import com.vtc.openapi.ui.dto.open.instance.InstanceBatchOperationRequest;
import com.vtc.openapi.ui.dto.open.instance.InstanceBatchOperationRequest.BatchItem;
import com.vtc.openapi.ui.dto.open.instance.InstanceBatchOperationResponse;
import com.vtc.openapi.ui.dto.open.instance.InstanceDetailDto;
import com.vtc.openapi.ui.dto.open.instance.InstanceDto;
import com.vtc.openapi.ui.dto.open.instance.InstanceOperationResponse;
import com.vtc.openapi.ui.dto.open.instance.InstanceSearchRequest;
import com.vtc.openapi.ui.dto.open.instance.InstanceSearchResponse;
import com.vtc.openapi.ui.dto.open.instance.RemediateInstanceRequest;
import com.vtc.openapi.ui.dto.open.instance.VerifyFixInstanceRequest;
import com.vtc.openapi.ui.dto.open.instance.VerifyInstanceRequest;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 实例应用服务：DTO 转换 + InvocationPipeline 编排 + 批量聚合。
 */
@Service
public class OpenInstanceAppServiceImpl implements IOpenInstanceAppService {

    /** 批量操作最大条数 */
    private static final int MAX_BATCH_SIZE = 100;

    private final InvocationPipeline invocationPipeline;
    private final IInstanceDomainService instanceDomainService;

    public OpenInstanceAppServiceImpl(InvocationPipeline invocationPipeline,
                                      IInstanceDomainService instanceDomainService) {
        this.invocationPipeline = invocationPipeline;
        this.instanceDomainService = instanceDomainService;
    }

    // ===================== 读接口 =====================

    @Override
    public ApiResponse<InstanceSearchResponse> searchInstances(InstanceSearchRequest request) {
        if (request == null) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "请求体不能为空");
        }
        if (request.getPage() == null || request.getPage() < 1) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "page 必须为正整数");
        }
        if (request.getSize() == null || request.getSize() < 1) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "size 必须为正整数");
        }

        return invocationPipeline.invoke(OpenApiOperations.SEARCH_INSTANCES, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            SearchInstanceCommand command = toCommand(request);
            InstancePageResult result = instanceDomainService.search(partnerId, command);
            return toSearchResponse(result);
        });
    }

    @Override
    public ApiResponse<InstanceDetailDto> getInstance(String vulInfoId) {
        if (vulInfoId == null || vulInfoId.trim().isEmpty()) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "vulInfoID 不能为空");
        }

        return invocationPipeline.invoke(OpenApiOperations.GET_INSTANCE, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            InstanceItemResult result = instanceDomainService.getByVulInfoId(partnerId, vulInfoId);
            if (result == null) {
                throw new OpenApiException(OpenApiConstants.CODE_CROSS_PARTNER,
                        "实例不存在或无权访问");
            }
            return toDetailDto(result);
        });
    }

    // ===================== 写接口（单条） =====================

    @Override
    public ApiResponse<InstanceOperationResponse> verifyInstance(String vulInfoId, VerifyInstanceRequest request) {
        if (vulInfoId == null || vulInfoId.trim().isEmpty()) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "vulInfoID 不能为空");
        }
        if (request == null || request.getVerifyResult() == null || request.getVerifyResult().trim().isEmpty()) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "verifyResult 不能为空");
        }

        return invocationPipeline.invoke(OpenApiOperations.VERIFY_INSTANCE, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            VerifyInstanceCommand command = new VerifyInstanceCommand();
            command.setVulInfoId(vulInfoId);
            command.setVerifyResult(request.getVerifyResult());
            InstanceStateResult result = instanceDomainService.verify(partnerId, command);
            return toOperationResponse(result);
        });
    }

    @Override
    public ApiResponse<InstanceOperationResponse> remediateInstance(String vulInfoId, RemediateInstanceRequest request) {
        if (vulInfoId == null || vulInfoId.trim().isEmpty()) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "vulInfoID 不能为空");
        }

        return invocationPipeline.invoke(OpenApiOperations.REMEDIATE_INSTANCE, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            RemediateInstanceCommand command = new RemediateInstanceCommand();
            command.setVulInfoId(vulInfoId);
            if (request != null) {
                command.setSrcMethod(request.getSrcMethod());
                command.setRemedDesc(request.getRemedDesc());
                command.setFixLnk(request.getFixLnk());
            }
            InstanceStateResult result = instanceDomainService.remediate(partnerId, command);
            return toOperationResponse(result);
        });
    }

    @Override
    public ApiResponse<InstanceOperationResponse> verifyFixInstance(String vulInfoId, VerifyFixInstanceRequest request) {
        if (vulInfoId == null || vulInfoId.trim().isEmpty()) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "vulInfoID 不能为空");
        }
        if (request == null || request.getVerifyResult() == null || request.getVerifyResult().trim().isEmpty()) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "verifyResult 不能为空");
        }

        return invocationPipeline.invoke(OpenApiOperations.VERIFY_FIX_INSTANCE, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            VerifyFixInstanceCommand command = new VerifyFixInstanceCommand();
            command.setVulInfoId(vulInfoId);
            command.setVerifyResult(request.getVerifyResult());
            InstanceStateResult result = instanceDomainService.verifyFix(partnerId, command);
            return toOperationResponse(result);
        });
    }

    // ===================== 写接口（批量） =====================

    @Override
    public ApiResponse<InstanceBatchOperationResponse> verifyInstanceBatch(InstanceBatchOperationRequest request) {
        validateBatchRequest(request);
        return invocationPipeline.invoke(OpenApiOperations.VERIFY_INSTANCE_BATCH, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            return executeBatch(partnerId, request.getItems(), (pid, item) -> {
                VerifyInstanceCommand cmd = new VerifyInstanceCommand();
                cmd.setVulInfoId(item.getVulInfoID());
                cmd.setVerifyResult(item.getVerifyResult());
                return instanceDomainService.verify(pid, cmd);
            });
        });
    }

    @Override
    public ApiResponse<InstanceBatchOperationResponse> remediateInstanceBatch(InstanceBatchOperationRequest request) {
        validateBatchRequest(request);
        return invocationPipeline.invoke(OpenApiOperations.REMEDIATE_INSTANCE_BATCH, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            return executeBatch(partnerId, request.getItems(), (pid, item) -> {
                RemediateInstanceCommand cmd = new RemediateInstanceCommand();
                cmd.setVulInfoId(item.getVulInfoID());
                cmd.setSrcMethod(item.getSrcMethod());
                cmd.setRemedDesc(item.getRemedDesc());
                cmd.setFixLnk(item.getFixLnk());
                return instanceDomainService.remediate(pid, cmd);
            });
        });
    }

    @Override
    public ApiResponse<InstanceBatchOperationResponse> verifyFixInstanceBatch(InstanceBatchOperationRequest request) {
        validateBatchRequest(request);
        return invocationPipeline.invoke(OpenApiOperations.VERIFY_FIX_INSTANCE_BATCH, ctx -> {
            String partnerId = PartnerContext.requirePartnerId();
            return executeBatch(partnerId, request.getItems(), (pid, item) -> {
                VerifyFixInstanceCommand cmd = new VerifyFixInstanceCommand();
                cmd.setVulInfoId(item.getVulInfoID());
                cmd.setVerifyResult(item.getVerifyResult());
                return instanceDomainService.verifyFix(pid, cmd);
            });
        });
    }

    // ===================== 私有方法 =====================

    private void validateBatchRequest(InstanceBatchOperationRequest request) {
        if (request == null || request.getItems() == null || request.getItems().isEmpty()) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR, "items 不能为空");
        }
        if (request.getItems().size() > MAX_BATCH_SIZE) {
            throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR,
                    "批量操作最多 " + MAX_BATCH_SIZE + " 条");
        }
    }

    @FunctionalInterface
    private interface BatchSingleHandler {
        InstanceStateResult execute(String partnerId, BatchItem item) throws OpenApiException;
    }

    /** 循环执行单条操作，聚合 success[] + failed[] */
    private InstanceBatchOperationResponse executeBatch(String partnerId,
                                                         List<BatchItem> items,
                                                         BatchSingleHandler handler) {
        List<InstanceOperationResponse> successList = new ArrayList<>();
        List<InstanceBatchFailedItem> failedList = new ArrayList<>();

        for (BatchItem item : items) {
            try {
                InstanceStateResult result = handler.execute(partnerId, item);
                successList.add(toOperationResponse(result));
            } catch (OpenApiException ex) {
                InstanceBatchFailedItem failed = new InstanceBatchFailedItem();
                failed.setVulInfoID(item.getVulInfoID());
                failed.setErrorCode(ex.getCode());
                failed.setErrorMessage(ex.getMessage());
                failedList.add(failed);
            }
        }

        InstanceBatchOperationResponse resp = new InstanceBatchOperationResponse();
        resp.setSuccess(successList);
        resp.setFailed(failedList);
        return resp;
    }

    private SearchInstanceCommand toCommand(InstanceSearchRequest request) {
        SearchInstanceCommand cmd = new SearchInstanceCommand();
        cmd.setTaskId(request.getTaskId());
        cmd.setExtTaskId(request.getExtTaskId());
        cmd.setVulInfoStatList(request.getVulInfoStatList());
        cmd.setVulLevelList(request.getVulLevelList());
        cmd.setVulNetAddr(request.getVulNetAddr());
        cmd.setAssetName(request.getAssetName());
        cmd.setVulName(request.getVulName());
        cmd.setOrgVulId(request.getOrgVulId());
        cmd.setVulId(request.getVulId());
        cmd.setIsAccess(request.getIsAccess());
        cmd.setUnitType(request.getUnitType());
        cmd.setPage(request.getPage());
        cmd.setSize(request.getSize());
        return cmd;
    }

    private InstanceSearchResponse toSearchResponse(InstancePageResult result) {
        InstanceSearchResponse resp = new InstanceSearchResponse();
        resp.setPage(result.getPage());
        resp.setSize(result.getSize());
        resp.setTotal(result.getTotal());
        if (result.getItems() != null) {
            resp.setItems(result.getItems().stream()
                    .map(this::toInstanceDto)
                    .collect(Collectors.toList()));
        }
        return resp;
    }

    private InstanceDto toInstanceDto(InstanceItemResult r) {
        InstanceDto dto = new InstanceDto();
        dto.setVulInfoID(r.getVulInfoId());
        dto.setVulID(r.getVulId());
        dto.setVulInfoStat(r.getVulInfoStat());
        dto.setLvRsn(r.getLvRsn());
        dto.setVulName(r.getVulName());
        dto.setVulLevel(r.getVulLevel());
        dto.setOrgVulId(r.getOrgVulId());
        dto.setVulNetAddr(r.getVulNetAddr());
        dto.setVulPort(r.getVulPort());
        dto.setVulSvc(r.getVulSvc());
        dto.setIsAccess(r.getIsAccess());
        dto.setTransferTime(r.getTransferTime());
        dto.setVulnDisposalId(r.getVulnDisposalId());
        dto.setExtVulnRef(r.getExtVulnRef());
        return dto;
    }

    private InstanceDetailDto toDetailDto(InstanceItemResult r) {
        InstanceDetailDto dto = new InstanceDetailDto();
        dto.setVulInfoID(r.getVulInfoId());
        dto.setVulID(r.getVulId());
        dto.setVulInfoStat(r.getVulInfoStat());
        dto.setLvRsn(r.getLvRsn());
        dto.setVulName(r.getVulName());
        dto.setVulLevel(r.getVulLevel());
        dto.setOrgVulId(r.getOrgVulId());
        dto.setVulNetAddr(r.getVulNetAddr());
        dto.setVulPort(r.getVulPort());
        dto.setVulSvc(r.getVulSvc());
        dto.setIsAccess(r.getIsAccess());
        dto.setTransferTime(r.getTransferTime());
        dto.setVulnDisposalId(r.getVulnDisposalId());
        dto.setVulAddrType(r.getVulAddrType());
        dto.setAssetID(r.getAssetId());
        dto.setAssetName(r.getAssetName());
        dto.setVulInstCpe(r.getVulInstCpe());
        dto.setVulInstVendor(r.getVulInstVendor());
        dto.setVulInstClass(r.getVulInstClass());
        dto.setVulInstName(r.getVulInstName());
        dto.setVulInstVer(r.getVulInstVer());
        dto.setRemedDesc(r.getRemedDesc());
        dto.setFixLnk(r.getFixLnk());
        dto.setRemedTime(r.getRemedTime());
        dto.setSrcMethod(r.getMethod());
        dto.setVulTransProto(r.getVulTransProto());
        dto.setExtVulnRef(r.getExtVulnRef());
        return dto;
    }

    private InstanceOperationResponse toOperationResponse(InstanceStateResult result) {
        InstanceOperationResponse resp = new InstanceOperationResponse();
        resp.setVulInfoID(result.getVulInfoId());
        resp.setPreviousStatus(result.getPreviousStat());
        resp.setCurrentStatus(result.getCurrentStat());
        return resp;
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: OpenInstanceAppServiceImpl"

# --- InstanceDomainServiceImpl ---
$f = "$base\domain\instance\service\business\impl\InstanceDomainServiceImpl.java"
$c = @"
package com.vtc.openapi.domain.instance.service.business.impl;

import com.vtc.openapi.domain.instance.model.command.RemediateInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.VerifyFixInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.VerifyInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;
import com.vtc.openapi.domain.instance.model.result.InstanceStateResult;
import com.vtc.openapi.domain.instance.repository.IInstanceRepository;
import com.vtc.openapi.domain.instance.service.business.IInstanceDomainService;
import com.vtc.openapi.domain.open.OpenApiConstants;
import com.vtc.openapi.domain.open.OpenApiException;
import com.vtc.openapi.domain.webhook.model.WebhookEvent;
import com.vtc.openapi.domain.webhook.model.WebhookEventType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * 实例领域服务：状态机校验 + 写操作 + Webhook 事件发布。
 */
@Service
public class InstanceDomainServiceImpl implements IInstanceDomainService {

    private static final Logger log = LoggerFactory.getLogger(InstanceDomainServiceImpl.class);

    /** verify 允许的前置状态：潜在预警(0)、初始发现(1) */
    private static final Set<Integer> VERIFY_ALLOWED_STATES = new HashSet<>(Arrays.asList(0, 1));
    /** remediate 允许的前置状态：已验证有效(2)、核验未修复(7) */
    private static final Set<Integer> REMEDIATE_ALLOWED_STATES = new HashSet<>(Arrays.asList(2, 7));
    /** verify-fix 允许的前置状态：已修复(5) */
    private static final Set<Integer> VERIFY_FIX_ALLOWED_STATES = new HashSet<>(5);

    private static final int STAT_VALIDATED_TRUE = 2;
    private static final int STAT_VALIDATED_FALSE = 3;
    private static final int STAT_FIXED = 5;
    private static final int STAT_VERIFIED_FIXED = 6;
    private static final int STAT_VERIFIED_UNFIXED = 7;

    private static final String VERIFY_RESULT_VALID = "VALID";
    private static final String VERIFY_RESULT_FALSE_POSITIVE = "FALSE_POSITIVE";
    private static final String VERIFY_FIX_RESULT_CONFIRMED = "FIX_CONFIRMED";
    private static final String VERIFY_FIX_RESULT_FAILED = "FIX_FAILED";

    private final IInstanceRepository instanceRepository;
    private final ApplicationEventPublisher eventPublisher;

    public InstanceDomainServiceImpl(IInstanceRepository instanceRepository,
                                     ApplicationEventPublisher eventPublisher) {
        this.instanceRepository = instanceRepository;
        this.eventPublisher = eventPublisher;
    }

    @Override
    public InstancePageResult search(String partnerId, SearchInstanceCommand command) {
        return instanceRepository.searchInstances(partnerId, command);
    }

    @Override
    public InstanceItemResult getByVulInfoId(String partnerId, String vulInfoId) {
        InstanceItemResult result = instanceRepository.findByVulInfoId(partnerId, vulInfoId);
        if (result == null) {
            return null;
        }
        return result;
    }

    @Override
    public InstanceStateResult verify(String partnerId, VerifyInstanceCommand command) {
        InstanceItemResult current = requireInstance(partnerId, command.getVulInfoId());
        int currentStat = requireStat(current);

        if (!VERIFY_ALLOWED_STATES.contains(currentStat)) {
            if (currentStat == STAT_VALIDATED_TRUE || currentStat == STAT_VALIDATED_FALSE) {
                throw new OpenApiException(OpenApiConstants.CODE_DUPLICATE_OP,
                        "实例已验证");
            }
            throw new OpenApiException(OpenApiConstants.CODE_STATE_INVALID,
                    "实例当前状态不允许验证，当前状态: " + currentStat);
        }

        int targetStat = resolveVerifyTarget(command.getVerifyResult());
        return executeStateChange(partnerId, current, targetStat, null, null);
    }

    @Override
    public InstanceStateResult remediate(String partnerId, RemediateInstanceCommand command) {
        InstanceItemResult current = requireInstance(partnerId, command.getVulInfoId());
        int currentStat = requireStat(current);

        if (!REMEDIATE_ALLOWED_STATES.contains(currentStat)) {
            if (currentStat == STAT_FIXED) {
                throw new OpenApiException(OpenApiConstants.CODE_DUPLICATE_OP,
                        "实例已修复");
            }
            throw new OpenApiException(OpenApiConstants.CODE_STATE_INVALID,
                    "实例当前状态不允许修复，当前状态: " + currentStat);
        }

        return executeStateChange(partnerId, current, STAT_FIXED, command.getSrcMethod(), command.getRemedDesc());
    }

    @Override
    public InstanceStateResult verifyFix(String partnerId, VerifyFixInstanceCommand command) {
        InstanceItemResult current = requireInstance(partnerId, command.getVulInfoId());
        int currentStat = requireStat(current);

        if (!VERIFY_FIX_ALLOWED_STATES.contains(currentStat)) {
            if (currentStat == STAT_VERIFIED_FIXED || currentStat == STAT_VERIFIED_UNFIXED) {
                throw new OpenApiException(OpenApiConstants.CODE_DUPLICATE_OP,
                        "实例已核验");
            }
            throw new OpenApiException(OpenApiConstants.CODE_STATE_INVALID,
                    "实例当前状态不允许核验修复，当前状态: " + currentStat);
        }

        int targetStat = resolveVerifyFixTarget(command.getVerifyResult());
        return executeStateChange(partnerId, current, targetStat, null, null);
    }

    /** 校验实例存在且归属 Partner */
    private InstanceItemResult requireInstance(String partnerId, String vulInfoId) {
        InstanceItemResult current = instanceRepository.findByVulInfoId(partnerId, vulInfoId);
        if (current == null) {
            throw new OpenApiException(OpenApiConstants.CODE_CROSS_PARTNER,
                    "实例不存在或无权访问");
        }
        return current;
    }

    private int requireStat(InstanceItemResult item) {
        if (item.getVulInfoStat() == null) {
            throw new OpenApiException(OpenApiConstants.CODE_STATE_INVALID,
                    "实例状态未知");
        }
        return item.getVulInfoStat();
    }

    private int resolveVerifyTarget(String verifyResult) {
        if (VERIFY_RESULT_VALID.equals(verifyResult)) {
            return STAT_VALIDATED_TRUE;
        }
        if (VERIFY_RESULT_FALSE_POSITIVE.equals(verifyResult)) {
            return STAT_VALIDATED_FALSE;
        }
        throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR,
                "无效的 verifyResult，期望 VALID 或 FALSE_POSITIVE");
    }

    private int resolveVerifyFixTarget(String verifyResult) {
        if (VERIFY_FIX_RESULT_CONFIRMED.equals(verifyResult)) {
            return STAT_VERIFIED_FIXED;
        }
        if (VERIFY_FIX_RESULT_FAILED.equals(verifyResult)) {
            return STAT_VERIFIED_UNFIXED;
        }
        throw new OpenApiException(OpenApiConstants.CODE_PARAM_ERROR,
                "无效的 verifyResult，期望 FIX_CONFIRMED 或 FIX_FAILED");
    }

    /** 执行状态变更并发布 Webhook 事件 */
    private InstanceStateResult executeStateChange(String partnerId, InstanceItemResult current,
                                                    int targetStat, String srcMethod, String remedDesc) {
        int previousStat = current.getVulInfoStat();
        instanceRepository.updateInstanceState(current.getId(), targetStat, srcMethod, remedDesc);

        InstanceStateResult result = new InstanceStateResult();
        result.setVulInfoId(current.getVulInfoId());
        result.setPreviousStat(previousStat);
        result.setCurrentStat(targetStat);

        publishStatusChangedEvent(partnerId, current.getVulInfoId(), previousStat, targetStat);
        return result;
    }

    /** 发布实例状态变更事件（供 Webhook 投递） */
    private void publishStatusChangedEvent(String partnerId, String vulInfoId,
                                            int previousStat, int currentStat) {
        try {
            Map<String, Object> data = new HashMap<>();
            data.put("vulInfoID", vulInfoId);
            data.put("previousStatus", previousStat);
            data.put("currentStatus", currentStat);
            WebhookEvent event = new WebhookEvent(
                    WebhookEventType.INSTANCE_STATUS_CHANGED, null, null, partnerId, data);
            eventPublisher.publishEvent(event);
        } catch (Exception ex) {
            log.warn("发布实例状态变更事件失败: partnerId={} vulInfoId={}", partnerId, vulInfoId, ex);
        }
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceDomainServiceImpl"

Write-Host "`n=== Part 2 done ==="
