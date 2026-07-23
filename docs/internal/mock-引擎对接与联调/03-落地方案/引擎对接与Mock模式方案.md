# 引擎对接与 Mock 模式方案

> **背景**：vul-pass 对开放 API 的实例/外发接口**尚未开发**；下周需对接入方做 §5 REST 联调。  
> **策略**：先**冻结对接契约**（Gateway 接口 + 映射表），通过 **`adapter-mode=mock`** 支撑全链路联调；生产扫描原始结果到位后，**热替换 fixture**，再切 **`vul-pass`** 做真机验证。  
> **关联**：[映射表](../../open-platform-开放平台/05-接口契约/Open%20API与vul-pass内部接口映射表.md) · [执行面落地方案](../../open-platform-开放平台/03-落地方案/开放平台对外REST执行面-分期落地方案.md) · [Mock 实例落库 PRD](../04-子PRD与规格/open-api-mock-instance-db-PRD.md)（OP-MOCK-P1-DB） · [**半人工联调配置指南**](../06-Mock与联调/open-api-mock-manual-配置指南.md)

---

## 1. 目标与原则

| 目标 | 说明 |
|------|------|
| 不阻塞 Partner 联调 | Partner 只调 `/api/open/v1/*`，**不感知** mock / vul-pass |
| 契约先行 | Domain 只依赖 `IScanEngineGateway` / `IVulnInstanceGateway`（待建），Infra 可切换 |
| 数据可替换 | Mock 数据来自 **JSON fixture**，生产原始结果导入后**无需改代码** |
| 一键切换 | `open-api.engine.adapter-mode: mock \| vul-pass`（Nacos / profile） |

**禁止**：在 Domain / UI 层写 `if (mock)`；切换仅在 `infra/adapter` + Spring Bean 配置。

---

## 2. 分层与切换点

```text
OpenInstanceUI / OpenTaskUI
  → InvocationPipeline
  → Domain（状态机、Partner 隔离、open_vuln_instance）
  → Gateway 接口（Domain 定义）
       ├─ mock   → SvmpEngineAdapterMockImpl + MockEngineFixtureLoader
       └─ vul-pass → SvmpEngineAdapterImpl + Feign
```

| Gateway | 职责 | mock | vul-pass |
|---------|------|:----:|:--------:|
| `IScanEngineGateway` | 任务创建/进度 | ✅ 已实现切换 | ✅ 已有 |
| `IVulnInstanceGateway` | 实例读/写（P1） | ✅ 同期实现 | 待 vul-pass 就绪后 |
| `IExportGateway`（P2） | 外发读 | fixture 文件 | 引擎 + 本地表 |

---

## 3. 配置项

```yaml
open-api:
  engine:
    # mock：联调/演示；vul-pass：生产或 vul-pass 就绪后
    adapter-mode: mock
    mock:
      # classpath:mock/engine 或 file:/data/open-api-mock（生产样本外挂目录）
      data-dir: classpath:mock/engine
      default-bundle: default
      # 任务创建后多少秒模拟 FINISHED（便于测 Webhook / 实例入库）
      task-finish-delay-seconds: 5
      # P1：任务 FINISHED 后是否把 fixture 实例写入 open_vuln_instance
      auto-ingest-instances-on-finish: true
  svmp:
    # adapter-mode=vul-pass 时生效
    engine-service-name: vul-pass
    dispatch:
      order-id: "1-31-xxxxxxxxxxxxxxxxxxx"
```

**联调环境启动**：

```powershell
# 方式 A：profile
spring.profiles.active=mock

# 方式 B：环境变量
OPEN_API_ENGINE_ADAPTER_MODE=mock
```

本地默认 `application.yml` 仍为 `vul-pass`（`matchIfMissing`）；联调机使用 `application-mock.yml`。

---

## 4. Mock 数据目录约定

```text
open-api-service/src/main/resources/mock/engine/   # 或外挂 data-dir
├── README.md
└── bundles/
    ├── default/                    # 无生产数据前的占位样本
    │   ├── manifest.json           # bundle 元数据
    │   └── instances.json          # 实例列表（Partner §5.2 字段子集）
    └── prod-sample-001/            # 生产导入包（数据到位后新增）
        ├── manifest.json
        ├── instances.json          # 由原始结果转换
        └── exports/                # P2：TaskExport xml/json
            └── task-export.json
```

### 4.1 `manifest.json`

```json
{
  "bundleId": "prod-sample-001",
  "description": "某生产任务扫描结果（2026-05-xx 导出）",
  "match": {
    "extTaskIdPrefix": "PARTNER-A-",
    "taskNameContains": "联调"
  },
  "instanceCount": 42,
  "importedAt": "2026-05-25"
}
```

### 4.2 `instances.json`（内部 fixture 格式）

与 [openapi §5.2 items[]](../../../external/网络安全漏洞管理平台%20·%20API%20接口文档V1.0.4.md) **字段对齐**，另加 `_mock` 仅供调试（不返回 Partner）：

```json
{
  "instances": [
    {
      "vulInfoID": "VI-MOCK-0001",
      "vulID": "VUL-2025-0001",
      "vulInfoStat": 1,
      "vulName": "示例 SQL 注入",
      "vulLevel": 3,
      "vulNetAddr": "10.0.0.1",
      "vulPort": 443,
      "transferTime": "1716192000",
      "vulnDisposalId": "DISP-MOCK-0001"
    }
  ]
}
```

**bundle 选择规则**（Mock 引擎）：

1. 若 `manifest.match.extTaskIdPrefix` 命中当前任务 → 用该 bundle  
2. 否则用 `open-api.engine.mock.default-bundle`（默认 `default`）  
3. 生产包到位后：新增 `bundles/prod-sample-001/`，**不重启**可支持外挂 `file:` 目录热加载（见 §6）

---

## 5. 各域 Mock 行为

### 5.1 任务（P0，已实现切换）

| 操作 | mock 行为 |
|------|-----------|
| `createTask` | 返回 `engineTaskId=MOCK-ENG-{id}`，不调用 Feign |
| `getTaskProgress` | 前 N 秒 `RUNNING/50` → 之后 `FINISHED/100` |
| Webhook | 任务 `FINISHED` 后照常触发 `TASK_COMPLETED`（与 vul-pass 一致） |

### 5.2 实例（P1，与 Open API 同期开发）

| 操作 | mock 行为 |
|------|-----------|
| 任务 FINISHED + `auto-ingest-instances-on-finish` | 从选中 bundle 复制实例到 `open_vuln_instance`（绑定 taskId/partnerId） |
| `searchInstances` / `getInstance` | 读 `open_vuln_instance`（与 vul-pass 模式相同路径） |
| `verify` / `remediate` / `verify-fix` | **仅更新本地表 + 状态机**，不调 vul-pass；可选模拟 `verify-fix` 异步复扫（延迟改 stat） |
| `:batch` | 循环单条逻辑 |

Partner 侧契约、错误码、幂等与 vul-pass 模式**完全一致**。

### 5.3 外发（P2）

| 操作 | mock 行为 |
|------|-----------|
| 任务/核验完成 | 从 `bundles/*/exports/` 注册 `open_export` |
| `GET /exports/*` | 读本地表 + fixture 文件流 |

---

## 6. 生产原始结果 → Mock fixture（数据到位后）

**输入**（你方从生产获取，预计几天后）：扫描任务原始 XML/JSON、子系统漏洞列表、处置字段等。

**步骤**（一次性脚本，不进 Partner 路径）：

```text
1. 脱敏：去掉内网 IP/账号等（或映射到 10.x 段）
2. 运行转换脚本（待建）：svmp/docs/internal/scripts/import-prod-scan-to-mock-bundle.py
   输入：raw/scan-result.xml + raw/sub-system-page.json
   输出：mock/engine/bundles/prod-sample-001/instances.json
3. 联调环境 data-dir 指向含新 bundle 的目录
4. adapter-mode 保持 mock，Partner 重跑 createTask → 实例查询即可看到真实形态数据
5. vul-pass 接口就绪后：adapter-mode=vul-pass，同批数据做回归对比
```

**验收**：fixture 中 `vulInfoID` 与生产一致**非必须**；Partner 只认平台分配的 ID。重点是 **字段形态、状态机路径、外发结构** 与 §5 一致。

---

## 7. 与 vul-pass 真对接的衔接（后续）

| 阶段 | adapter-mode | 说明 |
|------|--------------|------|
| **联调周** | `mock` | Partner curl + Webhook；运营看 invocation 日志 |
| **vul-pass α** | `vul-pass` + 部分 mock 实例写 | 读走 vul-pass，写仍 mock（可扩展 `hybrid`，暂不实现） |
| **全量** | `vul-pass` | 映射表 §3 全部 ✅ 后切换 |

映射表 [§6 决策记录](../../open-platform-开放平台/05-接口契约/Open%20API与vul-pass内部接口映射表.md) 在 vul-pass 开发并行填写；**不阻塞** mock 联调。

---

## 8. 联调检查清单（mock 模式）

- [ ] `spring.profiles.active=mock` 或 `adapter-mode=mock`
- [ ] 日志出现 `Engine adapter mode: MOCK`（启动 banner）
- [ ] `POST /tasks/vul` → `GET /tasks/{id}` 在 delay 后 `FINISHED`
- [ ] `POST /instances/search` 能返回 fixture 实例（P1 实现后）
- [ ] 完整走 verify → remediate → verify-fix，stat 与 §5 一致
- [ ] Webhook / `webhook_delivery_log` 有记录
- [ ] 生产 bundle 导入后重跑上述用例，**仅数据量变**，接口行为不变

---

## 9. 变更日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-05-21 | 初版：mock 切换、fixture 约定、生产数据导入路径 |
| 1.1 | 2026-06-13 | 关联 OP-MOCK-P1-DB：任务 FINISHED 后实例写入 `open_vuln_instance`，见 [PRD](../04-子PRD与规格/open-api-mock-instance-db-PRD.md) |
