# 网络安全漏洞管理平台 · 对外集成设计

本仓库存放漏洞管理平台与外部系统对接的设计文档（草稿）。

## OpenAPI

| 文件 | 说明 |
|------|------|
| [openapi/v1/openapi.yaml](./openapi/v1/openapi.yaml) | 开放平台 API **3.1**（V2.2.2：部侧字段 `vulInfoID`/`vulInfoStat`/`lvRsn`） |

本地预览（需安装 [Swagger UI](https://github.com/swagger-api/swagger-ui) 或 Redoc）：

```bash
npx @redocly/cli preview-docs openapi/v1/openapi.yaml
```

## 文档索引

| 文档 | 版本 | 说明 |
|------|------|------|
| [漏洞管理平台对外集成能力设计方案-V2.0.md](./漏洞管理平台对外集成能力设计方案-V2.0.md) | **V2.2（当前）** | 通用集成 + 部侧工单；**修复/备案并列处置**（§3.5） |
| [基础电信企业安全漏洞管理平台接口示例2025-V2.2.docx](./基础电信企业安全漏洞管理平台接口示例2025-V2.2.docx) | V2.2 | 部侧接口示例原文（**接口3 说明**为工单入站设计依据） |
| [SVMP对外接口联动方案-V1.1-对齐工信部2025.md](./SVMP对外接口联动方案-V1.1-对齐工信部2025.md) | V1.1 | SOC ↔ SVMP 专项方案，已归档为附录参考 |

## 演进说明

- **V1.x**：点对点 SOC-SVMP 接入层设计（`/api/soc/*`）
- **V2.2**：处置阶段 **修复（→5）与备案（→9）并列**；`archiveExtension.provincialFields` 预留省侧扩展
- **V2.0/V2.1**：开放平台 API + 部侧接口3/4 工单入站（MIIT-2025）
