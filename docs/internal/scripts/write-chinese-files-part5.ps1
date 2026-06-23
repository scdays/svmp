$utf8Bom = [System.Text.UTF8Encoding]::new($true)
$base = "d:\application\solo\3.0\project_backend\svmp\open-api-service\src\main\java\com\vtc\openapi"

# --- IInstanceDomainService ---
$f = "$base\domain\instance\service\business\IInstanceDomainService.java"
$c = @"
package com.vtc.openapi.domain.instance.service.business;

import com.vtc.openapi.domain.instance.model.command.RemediateInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.VerifyFixInstanceCommand;
import com.vtc.openapi.domain.instance.model.command.VerifyInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;
import com.vtc.openapi.domain.instance.model.result.InstanceStateResult;

/**
 * 实例领域服务接口：搜索、详情、验证、修复、核验修复。
 */
public interface IInstanceDomainService {

    /** 搜索实例 */
    InstancePageResult search(String partnerId, SearchInstanceCommand command);

    /** 按 vulInfoId 查询实例 */
    InstanceItemResult getByVulInfoId(String partnerId, String vulInfoId);

    /** 验证实例 */
    InstanceStateResult verify(String partnerId, VerifyInstanceCommand command);

    /** 修复实例 */
    InstanceStateResult remediate(String partnerId, RemediateInstanceCommand command);

    /** 核验修复 */
    InstanceStateResult verifyFix(String partnerId, VerifyFixInstanceCommand command);
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: IInstanceDomainService"

# --- IInstanceRepository ---
$f = "$base\domain\instance\repository\IInstanceRepository.java"
$c = @"
package com.vtc.openapi.domain.instance.repository;

import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;

/**
 * 实例仓储接口。
 */
public interface IInstanceRepository {

    /** 分页搜索实例 */
    InstancePageResult searchInstances(String partnerId, SearchInstanceCommand command);

    /** 按 vulInfoId 查找实例（含 Partner 隔离） */
    InstanceItemResult findByVulInfoId(String partnerId, String vulInfoId);

    /** 更新实例状态 */
    void updateInstanceState(Long id, Integer targetStat, String srcMethod, String remedDesc);
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: IInstanceRepository"

# --- InstanceRepositoryImpl ---
$f = "$base\infra\repository\InstanceRepositoryImpl.java"
$c = @"
package com.vtc.openapi.infra.repository;

import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;
import com.vtc.openapi.domain.instance.repository.IInstanceRepository;
import com.vtc.openapi.infra.gateway.IVulnInstanceGateway;
import org.springframework.stereotype.Repository;

/**
 * 实例仓储实现：委托 IVulnInstanceGateway 与引擎交互。
 */
@Repository
public class InstanceRepositoryImpl implements IInstanceRepository {

    private final IVulnInstanceGateway vulnInstanceGateway;

    public InstanceRepositoryImpl(IVulnInstanceGateway vulnInstanceGateway) {
        this.vulnInstanceGateway = vulnInstanceGateway;
    }

    @Override
    public InstancePageResult searchInstances(String partnerId, SearchInstanceCommand command) {
        return vulnInstanceGateway.searchInstances(partnerId, command);
    }

    @Override
    public InstanceItemResult findByVulInfoId(String partnerId, String vulInfoId) {
        return vulnInstanceGateway.getInstance(partnerId, vulInfoId);
    }

    @Override
    public void updateInstanceState(Long id, Integer targetStat, String srcMethod, String remedDesc) {
        vulnInstanceGateway.updateInstance(id, targetStat, srcMethod, remedDesc);
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceRepositoryImpl"

# --- IVulnInstanceGateway ---
$f = "$base\infra\gateway\IVulnInstanceGateway.java"
$c = @"
package com.vtc.openapi.infra.gateway;

import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;

/**
 * 漏洞实例引擎网关接口（infra 层）。
 */
public interface IVulnInstanceGateway {

    /** 分页搜索实例 */
    InstancePageResult searchInstances(String partnerId, SearchInstanceCommand command);

    /** 按 vulInfoId 获取实例 */
    InstanceItemResult getInstance(String partnerId, String vulInfoId);

    /** 更新实例状态 */
    void updateInstance(Long id, Integer targetStat, String srcMethod, String remedDesc);
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: IVulnInstanceGateway"

# --- VulnInstanceGatewayImpl ---
$f = "$base\infra\gateway\impl\VulnInstanceGatewayImpl.java"
$c = @"
package com.vtc.openapi.infra.gateway.impl;

import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;
import com.vtc.openapi.infra.gateway.IVulnInstanceGateway;
import com.vtc.openapi.infra.feign.IVulPassInstanceFeign;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * 引擎网关真实实现：通过 Feign 调用 vul-pass。
 * 仅在 mock=false 时激活。
 */
@Component
@ConditionalOnProperty(name = "open-api.mock.enabled", havingValue = "false", matchIfMissing = true)
public class VulnInstanceGatewayImpl implements IVulnInstanceGateway {

    private static final Logger log = LoggerFactory.getLogger(VulnInstanceGatewayImpl.class);

    private final IVulPassInstanceFeign vulPassInstanceFeign;

    public VulnInstanceGatewayImpl(IVulPassInstanceFeign vulPassInstanceFeign) {
        this.vulPassInstanceFeign = vulPassInstanceFeign;
    }

    @Override
    public InstancePageResult searchInstances(String partnerId, SearchInstanceCommand command) {
        log.debug("调用 vul-pass 搜索实例: partnerId={}", partnerId);
        return vulPassInstanceFeign.searchInstances(partnerId, command);
    }

    @Override
    public InstanceItemResult getInstance(String partnerId, String vulInfoId) {
        log.debug("调用 vul-pass 获取实例: partnerId={} vulInfoId={}", partnerId, vulInfoId);
        return vulPassInstanceFeign.getInstance(partnerId, vulInfoId);
    }

    @Override
    public void updateInstance(Long id, Integer targetStat, String srcMethod, String remedDesc) {
        log.debug("调用 vul-pass 更新实例状态: id={} targetStat={}", id, targetStat);
        vulPassInstanceFeign.updateInstance(id, targetStat, srcMethod, remedDesc);
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: VulnInstanceGatewayImpl"

# --- VulnInstanceGatewayMockImpl ---
$f = "$base\infra\gateway\impl\VulnInstanceGatewayMockImpl.java"
$c = @"
package com.vtc.openapi.infra.gateway.impl;

import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;
import com.vtc.openapi.infra.gateway.IVulnInstanceGateway;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 引擎网关 Mock 实现：本地内存存储，不依赖 vul-pass。
 * 在 open-api.mock.enabled=true 时激活。
 */
@Component
@ConditionalOnProperty(name = "open-api.mock.enabled", havingValue = "true")
public class VulnInstanceGatewayMockImpl implements IVulnInstanceGateway {

    private static final Logger log = LoggerFactory.getLogger(VulnInstanceGatewayMockImpl.class);
    private static final AtomicLong ID_SEQ = new AtomicLong(1L);

    private final ConcurrentHashMap<String, InstanceItemResult> store = new ConcurrentHashMap<>();

    @Override
    public InstancePageResult searchInstances(String partnerId, SearchInstanceCommand command) {
        log.info("[Mock] 搜索实例: partnerId={}", partnerId);

        List<InstanceItemResult> all = new ArrayList<>();
        if (store.isEmpty()) {
            all.add(createSample(partnerId, "mock-vul-001"));
            all.add(createSample(partnerId, "mock-vul-002"));
        } else {
            all.addAll(store.values());
        }

        int page = command.getPage() != null ? command.getPage() : 1;
        int size = command.getSize() != null ? command.getSize() : 20;
        int from = (page - 1) * size;
        int to = Math.min(from + size, all.size());

        InstancePageResult result = new InstancePageResult();
        result.setPage(page);
        result.setSize(size);
        result.setTotal((long) all.size());
        result.setItems(all.subList(Math.min(from, all.size()), to));
        return result;
    }

    @Override
    public InstanceItemResult getInstance(String partnerId, String vulInfoId) {
        log.info("[Mock] 获取实例: partnerId={} vulInfoId={}", partnerId, vulInfoId);
        InstanceItemResult item = store.get(vulInfoId);
        if (item == null) {
            item = createSample(partnerId, vulInfoId);
            store.put(vulInfoId, item);
        }
        return item;
    }

    @Override
    public void updateInstance(Long id, Integer targetStat, String srcMethod, String remedDesc) {
        log.info("[Mock] 更新实例状态: id={} targetStat={}", id, targetStat);
        for (InstanceItemResult item : store.values()) {
            if (item.getId() != null && item.getId().equals(id)) {
                item.setVulInfoStat(targetStat);
                item.setMethod(srcMethod);
                item.setRemedDesc(remedDesc);
                return;
            }
        }
    }

    private InstanceItemResult createSample(String partnerId, String vulInfoId) {
        InstanceItemResult item = new InstanceItemResult();
        item.setId(String.valueOf(ID_SEQ.getAndIncrement()));
        item.setVulInfoId(vulInfoId);
        item.setVulId("CVE-2024-0001");
        item.setVulInfoStat(1);
        item.setVulName("模拟漏洞");
        item.setVulLevel("high");
        item.setVulNetAddr("192.168.1." + (ID_SEQ.get() % 254 + 1));
        item.setAssetName("模拟资产");
        return item;
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: VulnInstanceGatewayMockImpl"

# --- IVulPassInstanceFeign ---
$f = "$base\infra\feign\IVulPassInstanceFeign.java"
$c = @"
package com.vtc.openapi.infra.feign;

import com.vtc.openapi.domain.instance.model.command.SearchInstanceCommand;
import com.vtc.openapi.domain.instance.model.result.InstanceItemResult;
import com.vtc.openapi.domain.instance.model.result.InstancePageResult;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;

/**
 * vul-pass 引擎实例接口 Feign 客户端。
 */
@FeignClient(name = "vul-pass", contextId = "instanceFeign")
public interface IVulPassInstanceFeign {

    @PostMapping("/api/v1/instances/search")
    InstancePageResult searchInstances(@RequestHeader("X-Partner-Id") String partnerId,
                                       @RequestBody SearchInstanceCommand command);

    @GetMapping("/api/v1/instances/{vulInfoId}")
    InstanceItemResult getInstance(@RequestHeader("X-Partner-Id") String partnerId,
                                   @PathVariable("vulInfoId") String vulInfoId);

    @PostMapping("/api/v1/instances/{id}/state")
    void updateInstance(@PathVariable("id") Long id,
                        @RequestBody Integer targetStat,
                        @RequestBody String srcMethod,
                        @RequestBody String remedDesc);
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: IVulPassInstanceFeign"

Write-Host "`n=== Part 5 Domain/Infra done ==="
