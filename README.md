# 网络安全漏洞管理平台 · 对外集成设计

本仓库存放漏洞管理平台与外部系统对接的设计文档、OpenAPI 契约与外发模板。

## 仓库结构

```text
.
├── README.md
├── docs/
│   ├── external/          # 第三方：开放平台 API 接口规范
│   ├── internal/          # 内部：集成能力设计方案
│   └── standards/         # 部侧 2025 规范原文（docx）
├── openapi/v1/            # OpenAPI 3.1 机器可读契约
├── templates/             # 数据外发模板、字段目录、引擎样本
│   ├── yaml/
│   ├── catalogs/
│   ├── engine/
│   └── schemas/
└── tools/                 # 字段解析与模板生成脚本
```

## 第三方接口文档

| 文件 | 说明 |
|------|------|
| [**docs/external/开放平台API接口规范.md**](./docs/external/开放平台API接口规范.md) | **提供给第三方的标准接口文档** |
| [docs/external/第三方开放平台接口文档.md](./docs/external/第三方开放平台接口文档.md) | 旧标题跳转页 |

## OpenAPI

| 文件 | 说明 |
|------|------|
| [openapi/v1/openapi.yaml](./openapi/v1/openapi.yaml) | 开放平台 API **1.0.0**（OpenAPI 3.1） |

本地预览 OpenAPI（任选其一）：

**方式 A · 生成 HTML（推荐，适配 Redocly CLI 2.x）**

Redocly CLI **2.x 已移除** `preview-docs`，请改用 `build-docs` 生成静态页后用浏览器打开：

```bash
node -v
npx @redocly/cli build-docs openapi/v1/openapi.yaml -o openapi/v1/api-docs.html
```

Windows CMD 生成后打开：

```cmd
start openapi\v1\api-docs.html
```

**方式 B · 在线 Swagger Editor（无需 Node）**

https://editor.swagger.io → **File → Import file** → 选择 `openapi/v1/openapi.yaml`

**方式 C · Docker Swagger UI**

```bash
docker run --rm -p 8080:8080 -e SWAGGER_JSON=/spec/openapi.yaml -v "%CD%/openapi/v1:/spec" swaggerapi/swagger-ui
```

**方式 D · 旧版实时预览（可选）**

若必须使用已废弃的 `preview-docs`，可固定 CLI 1.x：

```bash
npx @redocly/cli@1.34.4 preview-docs openapi/v1/openapi.yaml
```

环境要求：**Node.js ≥ 20.19**（或 22.x LTS）。若出现 `Unexpected token '??='`，请先升级 Node。

## 工具脚本

解析《数据外发字段说明》并生成模板：

```bash
python3 tools/parse_export_fields_html.py templates/engine/数据外发字段说明.html -o templates --write-drafts
python3 tools/build_export_xml_phases.py templates/catalogs/field-catalog.json -o templates
```

## 文档索引

| 路径 | 说明 |
|------|------|
| [docs/README.md](./docs/README.md) | 文档总索引 |
| [docs/internal/漏洞管理平台对外集成能力设计方案-V2.0.md](./docs/internal/漏洞管理平台对外集成能力设计方案-V2.0.md) | 内部设计（V2.3.3） |
| [templates/](./templates/) | 外发模板 YAML、字段目录、引擎 XML 样本 |
| [docs/standards/](./docs/standards/) | 部侧规范 docx |

## 演进说明

- **V2.2**：处置阶段修复（→5）与备案（→9）并列
- 第三方仅通过 **`/api/open/v1/*`** 接入；扫描/处置由平台内部对接 SVMP，无单独定制 API 路径
