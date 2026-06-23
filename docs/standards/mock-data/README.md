# 绿盟 Aurora 扫描报告 Mock 数据源

本目录存放**绿盟远程安全评估系统**导出的 Aurora XML，用于生成 `open-api-service` 的 mock 实例 fixture。

## 文件说明

| 文件 | 类型 | 说明 |
|------|------|------|
| `report_by_vul.xml` | **模板** | 漏洞扫描结果结构示例（少量 target/vuln，适合联调） |
| `report_by_pwd.xml` | **模板** | 弱口令扫描结构示例（含 `password_results`） |
| `漏洞扫描结果1166.xml` | **实样** | 任务 1166 完整漏洞扫描结果（体积大） |
| `弱口令扫描结果1053.xml` | **实样** | 任务 1053 完整弱口令扫描结果（体积大） |

XML 根节点为 `<aurora>`，与 vul-pass 中 `NsfocusXmlParserV4` / `NsfocusXmlParserV2` 解析格式一致。

## 生成 open-api mock bundle

在 `svmp/docs/internal/scripts/` 下执行：

```powershell
cd d:\application\solo\3.0\svmp\docs\internal\scripts

# 漏洞扫描模板 → 小 bundle（联调推荐）
py -3 import-nsfocus-xml-to-mock-bundle.py `
  --xml ../../standards/mock-data/report_by_vul.xml `
  --bundle-id nsfocus-vul-template `
  --out ../../../project_backend/svmp/open-api-service/src/main/resources/mock/engine/bundles/nsfocus-vul-template

# 弱口令模板 → 小 bundle
py -3 import-nsfocus-xml-to-mock-bundle.py `
  --xml ../../standards/mock-data/report_by_pwd.xml `
  --bundle-id nsfocus-pwd-template `
  --out ../../../project_backend/svmp/open-api-service/src/main/resources/mock/engine/bundles/nsfocus-pwd-template

# 大文件实样（限制条数，避免 mock 过大）
py -3 import-nsfocus-xml-to-mock-bundle.py `
  --xml ../../standards/mock-data/漏洞扫描结果1166.xml `
  --bundle-id prod-vul-1166 --limit 100 `
  --out ../../../project_backend/svmp/open-api-service/src/main/resources/mock/engine/bundles/prod-vul-1166
```

输出目录结构：

```
bundles/<bundle-id>/
├── instances.json   # MockEngineFixtureLoader 加载
├── manifest.json    # 元数据 + match 规则
└── source.xml       # 原始 XML 备份
```

## 使用生成的 mock 数据

1. 启动 `open-api-service` 时启用 mock：

   ```yaml
   spring.profiles.active: mock
   # 或 open-api.engine.adapter-mode: mock
   ```

2. 可选：指定默认 bundle

   ```yaml
   open-api:
     engine:
       mock:
         default-bundle: nsfocus-vul-template
   ```

3. 创建任务时 `taskName` 包含 XML 内任务名片段，或配置 `match.extTaskIdPrefix`，即可命中对应 bundle。

详见：`svmp/docs/internal/引擎对接与Mock模式方案.md`
