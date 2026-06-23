$utf8Bom = [System.Text.UTF8Encoding]::new($true)
$base = "d:\application\solo\3.0\project_backend\svmp\open-api-service\src\main\java\com\vtc\openapi"

# --- InstanceSearchRequest ---
$f = "$base\ui\dto\open\instance\InstanceSearchRequest.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import java.util.List;
import lombok.Data;

/**
 * 实例搜索请求。
 */
@Data
@ApiModel(description = "实例搜索请求")
public class InstanceSearchRequest {

    @ApiModelProperty(value = "任务 ID")
    private String taskId;
    @ApiModelProperty(value = "外部任务 ID")
    private String extTaskId;
    @ApiModelProperty(value = "实例状态列表，如 [0,1,2]")
    private List<Integer> vulInfoStatList;
    @ApiModelProperty(value = "漏洞等级列表，如 [\"high\",\"critical\"]")
    private List<String> vulLevelList;
    @ApiModelProperty(value = "IP/域名")
    private String vulNetAddr;
    @ApiModelProperty(value = "资产名称")
    private String assetName;
    @ApiModelProperty(value = "漏洞名称")
    private String vulName;
    @ApiModelProperty(value = "组织漏洞 ID")
    private String orgVulId;
    @ApiModelProperty(value = "漏洞 ID")
    private String vulId;
    @ApiModelProperty(value = "是否可达（true/false）")
    private Boolean isAccess;
    @ApiModelProperty(value = "单元类型")
    private String unitType;
    @ApiModelProperty(value = "页码，默认 1", required = true)
    private Integer page = 1;
    @ApiModelProperty(value = "每页条数，默认 20", required = true)
    private Integer size = 20;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceSearchRequest"

# --- InstanceSearchResponse ---
$f = "$base\ui\dto\open\instance\InstanceSearchResponse.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import java.util.List;
import lombok.Data;

/**
 * 实例搜索响应。
 */
@Data
@ApiModel(description = "实例搜索响应")
public class InstanceSearchResponse {

    @ApiModelProperty(value = "当前页码")
    private Integer page;
    @ApiModelProperty(value = "每页条数")
    private Integer size;
    @ApiModelProperty(value = "总条数")
    private Long total;
    @ApiModelProperty(value = "实例列表")
    private List<InstanceDto> items;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceSearchResponse"

# --- InstanceDto ---
$f = "$base\ui\dto\open\instance\InstanceDto.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 实例摘要 DTO（列表页用）。
 */
@Data
@ApiModel(description = "实例摘要")
public class InstanceDto {

    @ApiModelProperty(value = "实例唯一 ID")
    private String vulInfoID;
    @ApiModelProperty(value = "漏洞 ID")
    private String vulID;
    @ApiModelProperty(value = "实例状态: 0=潜在预警 1=初始发现 2=已验证有效 3=误报 5=已修复 6=核验已修复 7=核验未修复")
    private Integer vulInfoStat;
    @ApiModelProperty(value = "等级变更原因")
    private String lvRsn;
    @ApiModelProperty(value = "漏洞名称")
    private String vulName;
    @ApiModelProperty(value = "漏洞等级")
    private String vulLevel;
    @ApiModelProperty(value = "组织漏洞 ID")
    private String orgVulId;
    @ApiModelProperty(value = "IP/域名")
    private String vulNetAddr;
    @ApiModelProperty(value = "端口")
    private String vulPort;
    @ApiModelProperty(value = "服务")
    private String vulSvc;
    @ApiModelProperty(value = "是否可达")
    private Boolean isAccess;
    @ApiModelProperty(value = "流转时间")
    private String transferTime;
    @ApiModelProperty(value = "处置 ID")
    private String vulnDisposalId;
    @ApiModelProperty(value = "外部漏洞引用")
    private String extVulnRef;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceDto"

# --- InstanceDetailDto ---
$f = "$base\ui\dto\open\instance\InstanceDetailDto.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 实例详情 DTO。
 */
@Data
@ApiModel(description = "实例详情")
public class InstanceDetailDto {

    @ApiModelProperty(value = "实例唯一 ID")
    private String vulInfoID;
    @ApiModelProperty(value = "漏洞 ID")
    private String vulID;
    @ApiModelProperty(value = "实例状态")
    private Integer vulInfoStat;
    @ApiModelProperty(value = "等级变更原因")
    private String lvRsn;
    @ApiModelProperty(value = "漏洞名称")
    private String vulName;
    @ApiModelProperty(value = "漏洞等级")
    private String vulLevel;
    @ApiModelProperty(value = "组织漏洞 ID")
    private String orgVulId;
    @ApiModelProperty(value = "IP/域名")
    private String vulNetAddr;
    @ApiModelProperty(value = "端口")
    private String vulPort;
    @ApiModelProperty(value = "服务")
    private String vulSvc;
    @ApiModelProperty(value = "是否可达")
    private Boolean isAccess;
    @ApiModelProperty(value = "流转时间")
    private String transferTime;
    @ApiModelProperty(value = "处置 ID")
    private String vulnDisposalId;
    @ApiModelProperty(value = "地址类型")
    private String vulAddrType;
    @ApiModelProperty(value = "资产 ID")
    private String assetID;
    @ApiModelProperty(value = "资产名称")
    private String assetName;
    @ApiModelProperty(value = "组件 CPE")
    private String vulInstCpe;
    @ApiModelProperty(value = "组件厂商")
    private String vulInstVendor;
    @ApiModelProperty(value = "组件分类")
    private String vulInstClass;
    @ApiModelProperty(value = "组件名称")
    private String vulInstName;
    @ApiModelProperty(value = "组件版本")
    private String vulInstVer;
    @ApiModelProperty(value = "修复说明")
    private String remedDesc;
    @ApiModelProperty(value = "修复链接")
    private String fixLnk;
    @ApiModelProperty(value = "修复时间")
    private String remedTime;
    @ApiModelProperty(value = "修复方式")
    private String srcMethod;
    @ApiModelProperty(value = "传输协议")
    private String vulTransProto;
    @ApiModelProperty(value = "外部漏洞引用")
    private String extVulnRef;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceDetailDto"

# --- VerifyInstanceRequest ---
$f = "$base\ui\dto\open\instance\VerifyInstanceRequest.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 验证实例请求。
 */
@Data
@ApiModel(description = "验证实例请求")
public class VerifyInstanceRequest {

    @ApiModelProperty(value = "验证结果: VALID=有效, FALSE_POSITIVE=误报", required = true,
            allowableValues = "VALID,FALSE_POSITIVE")
    private String verifyResult;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: VerifyInstanceRequest"

# --- RemediateInstanceRequest ---
$f = "$base\ui\dto\open\instance\RemediateInstanceRequest.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 修复实例请求。
 */
@Data
@ApiModel(description = "修复实例请求")
public class RemediateInstanceRequest {

    @ApiModelProperty(value = "修复方式")
    private String srcMethod;
    @ApiModelProperty(value = "修复说明")
    private String remedDesc;
    @ApiModelProperty(value = "修复链接")
    private String fixLnk;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: RemediateInstanceRequest"

# --- VerifyFixInstanceRequest ---
$f = "$base\ui\dto\open\instance\VerifyFixInstanceRequest.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 核验修复请求。
 */
@Data
@ApiModel(description = "核验修复请求")
public class VerifyFixInstanceRequest {

    @ApiModelProperty(value = "核验结果: FIX_CONFIRMED=确认已修复, FIX_FAILED=确认未修复", required = true,
            allowableValues = "FIX_CONFIRMED,FIX_FAILED")
    private String verifyResult;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: VerifyFixInstanceRequest"

# --- InstanceOperationResponse ---
$f = "$base\ui\dto\open\instance\InstanceOperationResponse.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 实例写操作响应。
 */
@Data
@ApiModel(description = "实例操作响应")
public class InstanceOperationResponse {

    @ApiModelProperty(value = "实例唯一 ID")
    private String vulInfoID;
    @ApiModelProperty(value = "操作前状态")
    private Integer previousStatus;
    @ApiModelProperty(value = "操作后状态")
    private Integer currentStatus;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceOperationResponse"

# --- InstanceBatchOperationRequest ---
$f = "$base\ui\dto\open\instance\InstanceBatchOperationRequest.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import java.util.List;
import lombok.Data;

/**
 * 实例批量操作请求。
 */
@Data
@ApiModel(description = "实例批量操作请求")
public class InstanceBatchOperationRequest {

    @ApiModelProperty(value = "批量操作条目，最多 100 条", required = true)
    private List<BatchItem> items;

    @Data
    @ApiModel(description = "批量操作单条")
    public static class BatchItem {

        @ApiModelProperty(value = "实例唯一 ID", required = true)
        private String vulInfoID;
        @ApiModelProperty(value = "验证结果（verify / verify-fix 时必填）")
        private String verifyResult;
        @ApiModelProperty(value = "修复方式（remediate 时可选）")
        private String srcMethod;
        @ApiModelProperty(value = "修复说明（remediate 时可选）")
        private String remedDesc;
        @ApiModelProperty(value = "修复链接（remediate 时可选）")
        private String fixLnk;
    }
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceBatchOperationRequest"

# --- InstanceBatchOperationResponse ---
$f = "$base\ui\dto\open\instance\InstanceBatchOperationResponse.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import java.util.List;
import lombok.Data;

/**
 * 实例批量操作响应。
 */
@Data
@ApiModel(description = "实例批量操作响应")
public class InstanceBatchOperationResponse {

    @ApiModelProperty(value = "成功列表")
    private List<InstanceOperationResponse> success;
    @ApiModelProperty(value = "失败列表")
    private List<InstanceBatchFailedItem> failed;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceBatchOperationResponse"

# --- InstanceBatchFailedItem ---
$f = "$base\ui\dto\open\instance\InstanceBatchFailedItem.java"
$c = @"
package com.vtc.openapi.ui.dto.open.instance;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 批量操作失败条目。
 */
@Data
@ApiModel(description = "批量操作失败条目")
public class InstanceBatchFailedItem {

    @ApiModelProperty(value = "实例唯一 ID")
    private String vulInfoID;
    @ApiModelProperty(value = "错误码")
    private String errorCode;
    @ApiModelProperty(value = "错误信息")
    private String errorMessage;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceBatchFailedItem"

Write-Host "`n=== Part 3 DTOs done ==="
