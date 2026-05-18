# 网络安全漏洞管理平台 · 对外集成设计

本仓库存放漏洞管理平台与外部系统对接的设计文档（草稿）。

## OpenAPI

| 文件 | 说明 |
|------|------|
| [openapi/v1/openapi.yaml](./openapi/v1/openapi.yaml) | 开放平台 API **3.1**（V2.2.9：含 `verify-fix` / `verify-fix:batch`） |

本地预览（需安装 [Swagger UI](https://github.com/swagger-api/swagger-ui) 或 Redoc）：

```bash
npx @redocly/cli preview-docs openapi/v1/openapi.yaml
```

## 文档索引

| 文档 | 版本 | 说明 |
|------|------|------|
| [漏洞管理平台对外集成能力设计方案-V2.0.md](./漏洞管理平台对外集成能力设计方案-V2.0.md) | **V2.2.9（当前）** | 含 **§5.9 修复核验** `verify-fix`；修复/备案并列（§3.5） |
| [基础电信企业安全漏洞管理平台接口示例2025-V2.2.docx](./基础电信企业安全漏洞管理平台接口示例2025-V2.2.docx) | V2.2 | 部侧接口示例原文（**接口3 说明**为工单入站设计依据） |

## 演进说明

- **V2.2**：处置阶段 **修复（→5）与备案（→9）并列**；`provincialFields` 预留省侧扩展
- **V2.0/V2.1**：开放平台 API + 部侧接口3/4 工单入站（MIIT-2025）
- 第三方仅通过 **`/api/open/v1/*`** 接入；扫描/处置由平台内部对接 SVMP（§6.3），无单独定制 API 路径
