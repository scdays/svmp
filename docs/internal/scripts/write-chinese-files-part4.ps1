$utf8Bom = [System.Text.UTF8Encoding]::new($true)
$base = "d:\application\solo\3.0\project_backend\svmp\open-api-service\src\main\java\com\vtc\openapi"

# --- VerifyInstanceCommand ---
$f = "$base\domain\instance\model\command\VerifyInstanceCommand.java"
$c = @"
package com.vtc.openapi.domain.instance.model.command;

import lombok.Data;

/**
 * 验证实例命令。
 */
@Data
public class VerifyInstanceCommand {
    private String vulInfoId;
    private String verifyResult;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: VerifyInstanceCommand"

# --- RemediateInstanceCommand ---
$f = "$base\domain\instance\model\command\RemediateInstanceCommand.java"
$c = @"
package com.vtc.openapi.domain.instance.model.command;

import lombok.Data;

/**
 * 修复实例命令。
 */
@Data
public class RemediateInstanceCommand {
    private String vulInfoId;
    private String srcMethod;
    private String remedDesc;
    private String fixLnk;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: RemediateInstanceCommand"

# --- VerifyFixInstanceCommand ---
$f = "$base\domain\instance\model\command\VerifyFixInstanceCommand.java"
$c = @"
package com.vtc.openapi.domain.instance.model.command;

import lombok.Data;

/**
 * 核验修复命令。
 */
@Data
public class VerifyFixInstanceCommand {
    private String vulInfoId;
    private String verifyResult;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: VerifyFixInstanceCommand"

# --- SearchInstanceCommand ---
$f = "$base\domain\instance\model\command\SearchInstanceCommand.java"
$c = @"
package com.vtc.openapi.domain.instance.model.command;

import java.util.List;
import lombok.Data;

/**
 * 实例搜索命令。
 */
@Data
public class SearchInstanceCommand {
    private String taskId;
    private String extTaskId;
    private List<Integer> vulInfoStatList;
    private List<String> vulLevelList;
    private String vulNetAddr;
    private String assetName;
    private String vulName;
    private String orgVulId;
    private String vulId;
    private Boolean isAccess;
    private String unitType;
    private Integer page;
    private Integer size;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: SearchInstanceCommand"

# --- InstancePageResult ---
$f = "$base\domain\instance\model\result\InstancePageResult.java"
$c = @"
package com.vtc.openapi.domain.instance.model.result;

import java.util.List;
import lombok.Data;

/**
 * 实例分页结果。
 */
@Data
public class InstancePageResult {
    private Integer page;
    private Integer size;
    private Long total;
    private List<InstanceItemResult> items;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstancePageResult"

# --- InstanceItemResult ---
$f = "$base\domain\instance\model\result\InstanceItemResult.java"
$c = @"
package com.vtc.openapi.domain.instance.model.result;

import lombok.Data;

/**
 * 实例单条查询结果（领域层内部通用）。
 */
@Data
public class InstanceItemResult {
    private String id;
    private String vulInfoId;
    private String vulId;
    private Integer vulInfoStat;
    private String lvRsn;
    private String vulName;
    private String vulLevel;
    private String orgVulId;
    private String vulNetAddr;
    private String vulPort;
    private String vulSvc;
    private Boolean isAccess;
    private String transferTime;
    private String vulnDisposalId;
    private String vulAddrType;
    private String assetId;
    private String assetName;
    private String vulInstCpe;
    private String vulInstVendor;
    private String vulInstClass;
    private String vulInstName;
    private String vulInstVer;
    private String remedDesc;
    private String fixLnk;
    private String remedTime;
    private String method;
    private String vulTransProto;
    private String extVulnRef;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceItemResult"

# --- InstanceStateResult ---
$f = "$base\domain\instance\model\result\InstanceStateResult.java"
$c = @"
package com.vtc.openapi.domain.instance.model.result;

import lombok.Data;

/**
 * 实例状态变更结果。
 */
@Data
public class InstanceStateResult {
    private String vulInfoId;
    private Integer previousStat;
    private Integer currentStat;
}
"@
[System.IO.File]::WriteAllText($f, $c, $utf8Bom)
Write-Host "OK: InstanceStateResult"

Write-Host "`n=== Part 4 Command/Result done ==="
