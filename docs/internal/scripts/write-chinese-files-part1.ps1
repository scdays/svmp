$utf8Bom = [System.Text.UTF8Encoding]::new($true)
$base = "d:\application\solo\3.0\project_backend\svmp\open-api-service\src\main\java\com\vtc\openapi"

# --- WebhookEventType ---
$f = "$base\domain\webhook\model\WebhookEventType.java"
$c = @"
package com.vtc.openapi.domain.webhook.model;

/**
 * Webhook 事件类型常量。
 */
public final class WebhookEventType {

    /** 任务完成 */
    public static final String TASK_COMPLETED = "TASK_COMPLETED";
    /** 实例状态变更 */
    public static final String INSTANCE_STATUS_CHANGED = "INSTANCE_STATUS_CHANGED";
    /** 外发就绪（P2 暂不实现） */
    public static final String EXPORT_READY = "EXPORT_READY";

    private WebhookEventType() {
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: WebhookEventType"

# --- WebhookEvent ---
$f = "$base\domain\webhook\model\WebhookEvent.java"
$c = @"
package com.vtc.openapi.domain.webhook.model;

import java.util.Map;

/**
 * Webhook 出站事件载荷。
 */
public class WebhookEvent {

    private String eventType;
    private String eventId;
    private String timestamp;
    private String partnerId;
    private Map<String, Object> data;

    public WebhookEvent() {
    }

    public WebhookEvent(String eventType, String eventId, String timestamp,
                        String partnerId, Map<String, Object> data) {
        this.eventType = eventType;
        this.eventId = eventId;
        this.timestamp = timestamp;
        this.partnerId = partnerId;
        this.data = data;
    }

    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public String getEventId() { return eventId; }
    public void setEventId(String eventId) { this.eventId = eventId; }
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    public String getPartnerId() { return partnerId; }
    public void setPartnerId(String partnerId) { this.partnerId = partnerId; }
    public Map<String, Object> getData() { return data; }
    public void setData(Map<String, Object> data) { this.data = data; }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: WebhookEvent"

# --- IWebhookDomainService ---
$f = "$base\domain\webhook\service\business\IWebhookDomainService.java"
$c = @"
package com.vtc.openapi.domain.webhook.service.business;

import com.vtc.openapi.domain.webhook.model.WebhookEvent;

/**
 * Webhook 出站投递领域服务。
 */
public interface IWebhookDomainService {

    /**
     * 异步投递 Webhook 事件到 Partner 的 callbackUrl。
     * 投递失败不影响调用方。
     */
    void deliver(WebhookEvent event);
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: IWebhookDomainService"

# --- WebhookDomainServiceImpl ---
$f = "$base\domain\webhook\service\business\impl\WebhookDomainServiceImpl.java"
$c = @"
package com.vtc.openapi.domain.webhook.service.business.impl;

import com.alibaba.fastjson.JSON;
import com.vtc.openapi.domain.partner.repository.IPartnerRepository;
import com.vtc.openapi.domain.webhook.model.WebhookEvent;
import com.vtc.openapi.domain.webhook.service.business.IWebhookDomainService;
import com.vtc.openapi.infra.adapter.WebhookDeliveryAdapter;
import com.vtc.openapi.infra.dao.WebhookDeliveryLogMapper;
import com.vtc.openapi.infra.dao.po.WebhookDeliveryLogPO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Date;

/**
 * Webhook 出站投递实现。
 * 异步发送 HTTP POST 到 Partner callbackUrl，失败重试最多 3 次（指数退避）。
 */
@Service
public class WebhookDomainServiceImpl implements IWebhookDomainService {

    private static final Logger log = LoggerFactory.getLogger(WebhookDomainServiceImpl.class);
    private static final DateTimeFormatter ISO_FMT =
            DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'").withZone(ZoneId.of("UTC"));

    private static final int MAX_RETRIES = 3;
    private static final long[] BACKOFF_MS = {1000L, 2000L, 4000L};

    private final IPartnerRepository partnerRepository;
    private final WebhookDeliveryAdapter deliveryAdapter;
    private final WebhookDeliveryLogMapper deliveryLogMapper;

    public WebhookDomainServiceImpl(IPartnerRepository partnerRepository,
                                    WebhookDeliveryAdapter deliveryAdapter,
                                    WebhookDeliveryLogMapper deliveryLogMapper) {
        this.partnerRepository = partnerRepository;
        this.deliveryAdapter = deliveryAdapter;
        this.deliveryLogMapper = deliveryLogMapper;
    }

    @Override
    @Async
    public void deliver(WebhookEvent event) {
        if (event == null || event.getPartnerId() == null) {
            return;
        }

        String callbackUrl = partnerRepository.findCallbackUrl(event.getPartnerId());
        if (!StringUtils.hasText(callbackUrl)) {
            log.debug("Partner {} 未配置 callbackUrl，跳过 Webhook 投递", event.getPartnerId());
            return;
        }

        if (event.getEventId() == null) {
            event.setEventId("evt-" + java.util.UUID.randomUUID().toString().replace("-", ""));
        }
        if (event.getTimestamp() == null) {
            event.setTimestamp(ISO_FMT.format(Instant.now()));
        }

        String payloadJson = JSON.toJSONString(event);

        for (int attempt = 0; attempt <= MAX_RETRIES; attempt++) {
            WebhookDeliveryLogPO logEntry = createLogEntry(event, callbackUrl, payloadJson, attempt);

            try {
                int httpStatus = deliveryAdapter.post(callbackUrl, payloadJson);
                logEntry.setHttpStatus(httpStatus);
                logEntry.setStatus(httpStatus >= 200 && httpStatus < 300 ? "SUCCESS" : "FAILED");
            } catch (Exception ex) {
                log.warn("Webhook 投递失败: partnerId={} eventType={} 第{}次尝试",
                        event.getPartnerId(), event.getEventType(), attempt, ex);
                logEntry.setHttpStatus(-1);
                logEntry.setStatus("FAILED");
            }

            deliveryLogMapper.insert(logEntry);

            if ("SUCCESS".equals(logEntry.getStatus())) {
                return;
            }

            if (attempt < MAX_RETRIES) {
                try {
                    Thread.sleep(BACKOFF_MS[Math.min(attempt, BACKOFF_MS.length - 1)]);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }

        log.warn("Webhook 投递耗尽重试次数: partnerId={} eventType={}",
                event.getPartnerId(), event.getEventType());
    }

    private WebhookDeliveryLogPO createLogEntry(WebhookEvent event, String callbackUrl,
                                                 String payloadJson, int attempt) {
        WebhookDeliveryLogPO po = new WebhookDeliveryLogPO();
        po.setPartnerId(event.getPartnerId());
        po.setEventType(event.getEventType());
        po.setPayloadJson(payloadJson);
        po.setCallbackUrl(callbackUrl);
        po.setRetryCount(attempt);
        po.setStatus("PENDING");
        po.setCreatedAt(new Date());
        return po;
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: WebhookDomainServiceImpl"

# --- WebhookDeliveryAdapter ---
$f = "$base\infra\adapter\WebhookDeliveryAdapter.java"
$c = @"
package com.vtc.openapi.infra.adapter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

/**
 * Webhook 出站 HTTP 投递适配器，POST JSON 到目标 URL。
 */
@Component
public class WebhookDeliveryAdapter {

    private static final Logger log = LoggerFactory.getLogger(WebhookDeliveryAdapter.class);

    private final RestTemplate restTemplate;

    public WebhookDeliveryAdapter() {
        this.restTemplate = new RestTemplate();
    }

    /**
     * POST JSON 到目标 URL，返回 HTTP 状态码。
     */
    public int post(String url, String jsonPayload) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(jsonPayload, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            return response.getStatusCodeValue();
        } catch (Exception ex) {
            log.warn("Webhook POST 失败: url={}", url, ex);
            throw new RuntimeException("Webhook 投递 HTTP 错误", ex);
        }
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: WebhookDeliveryAdapter"

# --- OpenInstanceUI ---
$f = "$base\ui\open\OpenInstanceUI.java"
$c = @"
package com.vtc.openapi.ui.open;

import com.vtc.openapi.app.service.IOpenInstanceAppService;
import com.vtc.openapi.domain.open.OpenApiConstants;
import com.vtc.openapi.ui.dto.ApiResponse;
import com.vtc.openapi.ui.dto.open.instance.InstanceBatchOperationRequest;
import com.vtc.openapi.ui.dto.open.instance.InstanceBatchOperationResponse;
import com.vtc.openapi.ui.dto.open.instance.InstanceDetailDto;
import com.vtc.openapi.ui.dto.open.instance.InstanceOperationResponse;
import com.vtc.openapi.ui.dto.open.instance.InstanceSearchRequest;
import com.vtc.openapi.ui.dto.open.instance.InstanceSearchResponse;
import com.vtc.openapi.ui.dto.open.instance.RemediateInstanceRequest;
import com.vtc.openapi.ui.dto.open.instance.VerifyFixInstanceRequest;
import com.vtc.openapi.ui.dto.open.instance.VerifyInstanceRequest;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 开放平台实例 REST（/api/open/v1instances）。P1 OP-OPENAPI-P1。
 */
@RestController
@RequestMapping(OpenApiConstants.API_PREFIX)
@Api(tags = "开放平台 - 实例")
public class OpenInstanceUI {

    private final IOpenInstanceAppService openInstanceAppService;

    public OpenInstanceUI(IOpenInstanceAppService openInstanceAppService) {
        this.openInstanceAppService = openInstanceAppService;
    }

    @ApiOperation(value = "搜索实例", notes = "POST /instances/search - INSTANCE_READ")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @PostMapping("/instances/search")
    public ApiResponse<InstanceSearchResponse> searchInstances(@RequestBody InstanceSearchRequest request) {
        return openInstanceAppService.searchInstances(request);
    }

    @ApiOperation(value = "查询实例详情", notes = "GET /instances/{vulInfoID} - INSTANCE_READ")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @GetMapping("/instances/{vulInfoID}")
    public ApiResponse<InstanceDetailDto> getInstance(@PathVariable("vulInfoID") String vulInfoId) {
        return openInstanceAppService.getInstance(vulInfoId);
    }

    @ApiOperation(value = "验证实例", notes = "POST /instances/{vulInfoID}/verify - INSTANCE_VERIFY")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @PostMapping("/instances/{vulInfoID}/verify")
    public ApiResponse<InstanceOperationResponse> verifyInstance(
            @PathVariable("vulInfoID") String vulInfoId,
            @RequestBody VerifyInstanceRequest request) {
        return openInstanceAppService.verifyInstance(vulInfoId, request);
    }

    @ApiOperation(value = "修复实例", notes = "POST /instances/{vulInfoID}/remediate - INSTANCE_REMEDIATE")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @PostMapping("/instances/{vulInfoID}/remediate")
    public ApiResponse<InstanceOperationResponse> remediateInstance(
            @PathVariable("vulInfoID") String vulInfoId,
            @RequestBody(required = false) RemediateInstanceRequest request) {
        return openInstanceAppService.remediateInstance(vulInfoId, request);
    }

    @ApiOperation(value = "核验修复", notes = "POST /instances/{vulInfoID}/verify-fix - INSTANCE_VERIFY_FIX")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @PostMapping("/instances/{vulInfoID}/verify-fix")
    public ApiResponse<InstanceOperationResponse> verifyFixInstance(
            @PathVariable("vulInfoID") String vulInfoId,
            @RequestBody VerifyFixInstanceRequest request) {
        return openInstanceAppService.verifyFixInstance(vulInfoId, request);
    }

    // ===================== 批量接口 =====================

    @ApiOperation(value = "批量验证实例", notes = "POST /instances/verify:batch - INSTANCE_VERIFY")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @PostMapping("/instances/verify:batch")
    public ApiResponse<InstanceBatchOperationResponse> verifyInstanceBatch(
            @RequestBody InstanceBatchOperationRequest request) {
        return openInstanceAppService.verifyInstanceBatch(request);
    }

    @ApiOperation(value = "批量修复实例", notes = "POST /instances/remediate:batch - INSTANCE_REMEDIATE")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @PostMapping("/instances/remediate:batch")
    public ApiResponse<InstanceBatchOperationResponse> remediateInstanceBatch(
            @RequestBody InstanceBatchOperationRequest request) {
        return openInstanceAppService.remediateInstanceBatch(request);
    }

    @ApiOperation(value = "批量核验修复", notes = "POST /instances/verify-fix:batch - INSTANCE_VERIFY_FIX")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "X-Partner-Id", value = "Partner ID", required = true,
                    paramType = "header", dataType = "string"),
            @ApiImplicitParam(name = "X-Request-Id", value = "请求追踪 ID", paramType = "header", dataType = "string")
    })
    @PostMapping("/instances/verify-fix:batch")
    public ApiResponse<InstanceBatchOperationResponse> verifyFixInstanceBatch(
            @RequestBody InstanceBatchOperationRequest request) {
        return openInstanceAppService.verifyFixInstanceBatch(request);
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: OpenInstanceUI"

Write-Host "`n=== Domain + Infra + UI done ==="
