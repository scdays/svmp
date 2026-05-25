#!/usr/bin/env py -3
"""Restructure open-api-service to vul-pass layout: app, domain, infra, ui only."""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] / "project_backend" / "svmp" / "open-api-service" / "src" / "main" / "java" / "com" / "vtc" / "openapi"

MOVES = [
    ("common/OpenApiException.java", "domain/open/OpenApiException.java"),
    ("common/OpenApiConstants.java", "domain/open/OpenApiConstants.java"),
    ("common/PartnerContext.java", "domain/partner/context/PartnerContext.java"),
    ("domain/partner/PartnerConstants.java", "domain/partner/model/PartnerConstants.java"),
    ("governance/InvocationContext.java", "domain/open/model/InvocationContext.java"),
    ("governance/OpenApiOperations.java", "domain/open/OpenApiOperations.java"),
    ("governance/ApiCatalogService.java", "domain/open/service/business/impl/ApiCatalogDomainServiceImpl.java"),
    ("governance/InvocationService.java", "domain/open/service/business/impl/InvocationDomainServiceImpl.java"),
    ("pipeline/InvocationPipeline.java", "app/open/InvocationPipeline.java"),
    ("pipeline/OpenOperationHandler.java", "app/open/OpenOperationHandler.java"),
    ("handler/TaskHandler.java", "domain/task/service/business/impl/OpenTaskDomainServiceImpl.java"),
    ("service/impl/TaskServiceImpl.java", "app/service/impl/OpenTaskAppServiceImpl.java"),
    ("web/dto/ApiResponse.java", "ui/dto/ApiResponse.java"),
    ("web/dto/task/CreateTaskRequest.java", "ui/dto/open/task/CreateTaskRequest.java"),
    ("web/dto/task/CreateTaskResponse.java", "ui/dto/open/task/CreateTaskResponse.java"),
    ("web/dto/task/TaskListPageDto.java", "ui/dto/open/task/TaskListPageDto.java"),
    ("web/dto/task/TaskProgressDto.java", "ui/dto/open/task/TaskProgressDto.java"),
    ("web/dto/task/TaskSummaryDto.java", "ui/dto/open/task/TaskSummaryDto.java"),
    ("web/InternalAdminAuthFilter.java", "infra/filter/InternalAdminAuthFilter.java"),
    ("web/PartnerContextFilter.java", "infra/filter/PartnerContextFilter.java"),
    ("web/RequestIdFilter.java", "infra/filter/RequestIdFilter.java"),
    ("web/OpenApiExceptionHandler.java", "infra/filter/OpenApiExceptionHandler.java"),
    ("web/HealthController.java", "ui/HealthUI.java"),
    ("adapter/SvmpEngineAdapter.java", "infra/adapter/SvmpEngineAdapter.java"),
    ("adapter/SvmpEngineAdapterImpl.java", "infra/adapter/SvmpEngineAdapterImpl.java"),
    ("adapter/dto/SvmpTaskCreateRequest.java", "infra/adapter/dto/SvmpTaskCreateRequest.java"),
    ("adapter/dto/SvmpTaskCreateResult.java", "infra/adapter/dto/SvmpTaskCreateResult.java"),
    ("adapter/dto/SvmpTaskProgressResult.java", "infra/adapter/dto/SvmpTaskProgressResult.java"),
]

PACKAGE_MAP = {
    "com.vtc.openapi.common.OpenApiException": "com.vtc.openapi.domain.open.OpenApiException",
    "com.vtc.openapi.common.OpenApiConstants": "com.vtc.openapi.domain.open.OpenApiConstants",
    "com.vtc.openapi.common.PartnerContext": "com.vtc.openapi.domain.partner.context.PartnerContext",
    "com.vtc.openapi.domain.partner.PartnerConstants": "com.vtc.openapi.domain.partner.model.PartnerConstants",
    "com.vtc.openapi.governance.InvocationContext": "com.vtc.openapi.domain.open.model.InvocationContext",
    "com.vtc.openapi.governance.OpenApiOperations": "com.vtc.openapi.domain.open.OpenApiOperations",
    "com.vtc.openapi.governance.ApiCatalogService": "com.vtc.openapi.domain.open.service.business.IApiCatalogDomainService",
    "com.vtc.openapi.governance.InvocationService": "com.vtc.openapi.domain.open.service.business.IInvocationDomainService",
    "com.vtc.openapi.pipeline.InvocationPipeline": "com.vtc.openapi.app.open.InvocationPipeline",
    "com.vtc.openapi.pipeline.OpenOperationHandler": "com.vtc.openapi.app.open.OpenOperationHandler",
    "com.vtc.openapi.handler.TaskHandler": "com.vtc.openapi.domain.task.service.business.IOpenTaskDomainService",
    "com.vtc.openapi.service.TaskService": "com.vtc.openapi.app.service.IOpenTaskAppService",
    "com.vtc.openapi.service.impl.TaskServiceImpl": "com.vtc.openapi.app.service.impl.OpenTaskAppServiceImpl",
    "com.vtc.openapi.web.dto.ApiResponse": "com.vtc.openapi.ui.dto.ApiResponse",
    "com.vtc.openapi.web.dto.task.": "com.vtc.openapi.ui.dto.open.task.",
    "com.vtc.openapi.web.InternalAdminAuthFilter": "com.vtc.openapi.infra.filter.InternalAdminAuthFilter",
    "com.vtc.openapi.web.PartnerContextFilter": "com.vtc.openapi.infra.filter.PartnerContextFilter",
    "com.vtc.openapi.web.RequestIdFilter": "com.vtc.openapi.infra.filter.RequestIdFilter",
    "com.vtc.openapi.web.OpenApiExceptionHandler": "com.vtc.openapi.infra.filter.OpenApiExceptionHandler",
    "com.vtc.openapi.web.HealthController": "com.vtc.openapi.ui.HealthUI",
    "com.vtc.openapi.adapter.": "com.vtc.openapi.infra.adapter.",
}

CLASS_RENAMES = {
    "ApiCatalogService": "ApiCatalogDomainServiceImpl",
    "InvocationService": "InvocationDomainServiceImpl",
    "TaskHandler": "OpenTaskDomainServiceImpl",
    "TaskServiceImpl": "OpenTaskAppServiceImpl",
    "HealthController": "HealthUI",
}

FILE_PACKAGE = {
    "domain/open/OpenApiException.java": "com.vtc.openapi.domain.open",
    "domain/open/OpenApiConstants.java": "com.vtc.openapi.domain.open",
    "domain/partner/context/PartnerContext.java": "com.vtc.openapi.domain.partner.context",
    "domain/partner/model/PartnerConstants.java": "com.vtc.openapi.domain.partner.model",
    "domain/open/model/InvocationContext.java": "com.vtc.openapi.domain.open.model",
    "domain/open/OpenApiOperations.java": "com.vtc.openapi.domain.open",
    "domain/open/service/business/impl/ApiCatalogDomainServiceImpl.java": "com.vtc.openapi.domain.open.service.business.impl",
    "domain/open/service/business/impl/InvocationDomainServiceImpl.java": "com.vtc.openapi.domain.open.service.business.impl",
    "app/open/InvocationPipeline.java": "com.vtc.openapi.app.open",
    "app/open/OpenOperationHandler.java": "com.vtc.openapi.app.open",
    "domain/task/service/business/impl/OpenTaskDomainServiceImpl.java": "com.vtc.openapi.domain.task.service.business.impl",
    "app/service/impl/OpenTaskAppServiceImpl.java": "com.vtc.openapi.app.service.impl",
    "ui/dto/ApiResponse.java": "com.vtc.openapi.ui.dto",
    "ui/dto/open/task/CreateTaskRequest.java": "com.vtc.openapi.ui.dto.open.task",
    "ui/dto/open/task/CreateTaskResponse.java": "com.vtc.openapi.ui.dto.open.task",
    "ui/dto/open/task/TaskListPageDto.java": "com.vtc.openapi.ui.dto.open.task",
    "ui/dto/open/task/TaskProgressDto.java": "com.vtc.openapi.ui.dto.open.task",
    "ui/dto/open/task/TaskSummaryDto.java": "com.vtc.openapi.ui.dto.open.task",
    "infra/filter/InternalAdminAuthFilter.java": "com.vtc.openapi.infra.filter",
    "infra/filter/PartnerContextFilter.java": "com.vtc.openapi.infra.filter",
    "infra/filter/RequestIdFilter.java": "com.vtc.openapi.infra.filter",
    "infra/filter/OpenApiExceptionHandler.java": "com.vtc.openapi.infra.filter",
    "ui/HealthUI.java": "com.vtc.openapi.ui",
    "infra/adapter/SvmpEngineAdapter.java": "com.vtc.openapi.infra.adapter",
    "infra/adapter/SvmpEngineAdapterImpl.java": "com.vtc.openapi.infra.adapter",
    "infra/adapter/dto/SvmpTaskCreateRequest.java": "com.vtc.openapi.infra.adapter.dto",
    "infra/adapter/dto/SvmpTaskCreateResult.java": "com.vtc.openapi.infra.adapter.dto",
    "infra/adapter/dto/SvmpTaskProgressResult.java": "com.vtc.openapi.infra.adapter.dto",
}


def move_files():
    for src_rel, dst_rel in MOVES:
        src = ROOT / src_rel.replace("/", "\\") if False else ROOT / src_rel
        dst = ROOT / dst_rel
        if not src.exists():
            print(f"SKIP missing {src_rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst.unlink()
        shutil.move(str(src), str(dst))
        print(f"MOVE {src_rel} -> {dst_rel}")


def fix_package_in_file(path: Path, pkg: str):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^package\s+[\w.]+;", f"package {pkg};", text, count=1, flags=re.MULTILINE)
    path.write_text(text, encoding="utf-8")


def apply_renames(content: str) -> str:
    for old, new in sorted(PACKAGE_MAP.items(), key=lambda x: -len(x[0])):
        content = content.replace(old, new)
    for old, new in CLASS_RENAMES.items():
        # class declaration rename in moved files only handled separately
        pass
    return content


def rewrite_all_java():
    test_root = ROOT.parents[2] / "test" / "java" / "com" / "vtc" / "openapi"
    dirs = [ROOT, test_root] if test_root.exists() else [ROOT]
    for base in dirs:
        for path in base.rglob("*.java"):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(ROOT)).replace("\\", "/") if path.is_relative_to(ROOT) else None
            if rel and rel in FILE_PACKAGE:
                text = re.sub(r"^package\s+[\w.]+;", f"package {FILE_PACKAGE[rel]};", text, count=1, flags=re.MULTILINE)
            new_text = apply_renames(text)
            # class renames in impl files
            if "ApiCatalogDomainServiceImpl" in str(path):
                new_text = new_text.replace("class ApiCatalogService", "class ApiCatalogDomainServiceImpl")
                new_text = new_text.replace("public ApiCatalogService(", "public ApiCatalogDomainServiceImpl(")
            if "InvocationDomainServiceImpl" in str(path):
                new_text = new_text.replace("class InvocationService", "class InvocationDomainServiceImpl")
                new_text = new_text.replace("public InvocationService(", "public InvocationDomainServiceImpl(")
            if "OpenTaskDomainServiceImpl" in str(path):
                new_text = new_text.replace("class TaskHandler", "class OpenTaskDomainServiceImpl")
                new_text = new_text.replace("public TaskHandler(", "public OpenTaskDomainServiceImpl(")
            if "OpenTaskAppServiceImpl" in str(path):
                new_text = new_text.replace("class TaskServiceImpl", "class OpenTaskAppServiceImpl")
                new_text = new_text.replace("implements TaskService, IOpenTaskAppService", "implements IOpenTaskAppService")
                new_text = new_text.replace("private final TaskHandler taskHandler", "private final IOpenTaskDomainService openTaskDomainService")
                new_text = new_text.replace("TaskHandler taskHandler", "IOpenTaskDomainService openTaskDomainService")
                new_text = new_text.replace("this.taskHandler = taskHandler", "this.openTaskDomainService = openTaskDomainService")
                new_text = new_text.replace("taskHandler.create", "openTaskDomainService.create")
                new_text = new_text.replace("taskHandler.get", "openTaskDomainService.get")
                new_text = new_text.replace("taskHandler.list", "openTaskDomainService.list")
                new_text = re.sub(r"import com\.vtc\.openapi\.service\.TaskService;\n", "", new_text)
            if path.name == "HealthUI.java":
                new_text = new_text.replace("class HealthController", "class HealthUI")
            if new_text != text:
                path.write_text(new_text, encoding="utf-8")


def remove_empty_dirs():
    for pkg in ["common", "governance", "pipeline", "handler", "adapter", "service", "web"]:
        p = ROOT / pkg
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            print(f"REMOVE dir {pkg}/")


def main():
    move_files()
    rewrite_all_java()
    remove_empty_dirs()
    print("Done.")


if __name__ == "__main__":
    main()
