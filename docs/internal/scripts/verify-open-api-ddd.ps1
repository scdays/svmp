# open-api-service DDD layer verification
# Usage:
#   powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1
#   powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

param(
    [switch]$Compile
)

$ErrorActionPreference = "Stop"

$WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$OpenApiJavaRoot = Join-Path $WorkspaceRoot "project_backend\svmp\open-api-service\src\main\java\com\vtc\openapi"
$OpenApiSrcRoot = Join-Path $WorkspaceRoot "project_backend\svmp\open-api-service\src"
$AllowedTopLevel = @("app", "domain", "infra", "ui")

$ForbiddenPackagePrefixes = @(
    "com.vtc.openapi.common",
    "com.vtc.openapi.web",
    "com.vtc.openapi.governance",
    "com.vtc.openapi.pipeline",
    "com.vtc.openapi.handler",
    "com.vtc.openapi.adapter",
    "com.vtc.openapi.service"
)

$failures = New-Object System.Collections.Generic.List[string]

if (-not (Test-Path $OpenApiJavaRoot)) {
    Write-Host "ERROR: open-api java root not found: $OpenApiJavaRoot" -ForegroundColor Red
    exit 1
}

# 1. Top-level package directories
Get-ChildItem -Path $OpenApiJavaRoot -Directory | ForEach-Object {
    if ($AllowedTopLevel -notcontains $_.Name) {
        [void]$failures.Add("Forbidden top-level dir: com.vtc.openapi.$($_.Name) (allowed: app/domain/infra/ui)")
    }
}

# 2. Forbidden legacy package/import
Get-ChildItem -Path $OpenApiSrcRoot -Recurse -Include *.java | ForEach-Object {
    $lines = Get-Content -Path $_.FullName -Encoding UTF8
    $relative = $_.FullName.Substring($WorkspaceRoot.Length + 1)
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if (-not ($trimmed.StartsWith("package ") -or $trimmed.StartsWith("import "))) {
            continue
        }
        foreach ($prefix in $ForbiddenPackagePrefixes) {
            if ($trimmed.StartsWith("package $prefix.") -or $trimmed -eq "package $prefix;") {
                [void]$failures.Add("${relative}: legacy package $prefix")
            }
            if ($trimmed.StartsWith("import $prefix.") -or $trimmed -eq "import $prefix;") {
                [void]$failures.Add("${relative}: legacy import $prefix")
            }
        }
    }
}

# 3. UI must not inject Mapper/Repository
$uiRoot = Join-Path $OpenApiJavaRoot "ui"
if (Test-Path $uiRoot) {
    Get-ChildItem -Path $uiRoot -Recurse -Include *UI.java | ForEach-Object {
        $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
        $relative = $_.FullName.Substring($WorkspaceRoot.Length + 1)
        if ($content -match "import\s+com\.vtc\.openapi\.infra\.(dao|repository)\.") {
            [void]$failures.Add("${relative}: UI must not inject Mapper/Repository")
        }
        if ($content -match "import\s+com\.vtc\.openapi\.domain\.\w+\.repository\.") {
            [void]$failures.Add("${relative}: UI must not inject Domain Repository")
        }
    }
}

# 4. Optional compile
if ($Compile) {
    $serviceDir = Join-Path $WorkspaceRoot "project_backend\svmp\open-api-service"
    Push-Location $serviceDir
    try {
        & mvn -q compile -DskipTests
        if ($LASTEXITCODE -ne 0) {
            [void]$failures.Add("mvn compile failed (exit $LASTEXITCODE)")
        }
    } finally {
        Pop-Location
    }
}

if ($failures.Count -gt 0) {
    Write-Host "open-api-service DDD verification FAILED ($($failures.Count)):" -ForegroundColor Red
    foreach ($item in $failures) {
        Write-Host "  - $item" -ForegroundColor Red
    }
    exit 1
}

Write-Host "open-api-service DDD verification PASSED" -ForegroundColor Green
if (-not $Compile) {
    Write-Host "Tip: add -Compile to also run mvn compile" -ForegroundColor DarkGray
}
exit 0
