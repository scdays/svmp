# 修复核验全链路 — Wave I 处置类型自动分配与 1028 解析 开发计划 v1.0

> **状态**：已执行完成（见 Wave I 验收报告 v1.0）  
> **日期**：2026-07-16  
> **前置**：Wave G/H 已合入；业务场景=`ctxCode=3`；工单来源=`source`（0企业/1部侧，任务表不存）；1028 方案 A

---

## 1. 目标

1. 后端统一 **处置类型（reportType）自动分配策略**，任务预览/下发时每个子任务带好默认 `suggestedReportType` 并落库。  
2. 新增 **1028 连通性检测** 专用 `VulReportTypeEnum` 码 + `ConnectivityCheckParser`。  
3. 前端处置弹窗与预览对齐后端策略，去掉仅靠前端 `checkData` 猜默认值的分叉。

## 2. 验收标准

- [ ] `VulReportTypeEnum` 新增连通性检测码（建议 **34**），`hidden=1`，绑定 `ConnectivityCheckParser`
- [ ] `ConnectivityCheckParser` 能解析/处理主机存活+端口结果（对齐 recycle 所需 `portList` / alive 语义）
- [ ] 手段 ∈ {1020,1022,1023,1024,1027} 默认 reportType 规则：
  - `source==0`（企业本地工单）→ **3** 常态化 XLSX  
  - `source==1`（部侧）且 `ctxCode==3`（行业漏洞专项排查）→ **3**  
  - `source==1` 且其它 ctxCode → **10** 绿盟 XML V1.2  
- [ ] 预览/下发能拿到外层工单 `source`（任务表本身不存，需入参或按 orderId 回查）
- [ ] 手段 **1028** → 固定新码 **34**（不走 3/10）
- [ ] 预览 plan group 含 `suggestedReportType` / name；下发写入子任务 `reportType`
- [ ] 前端处置：优先用子任务已有 `reportType`；无则调同一策略（或读后端字段）
- [ ] 单测覆盖映射表 + 1028 枚举/Parser 注册；相关 lint 通过

## 3. 不改什么

- 不改 Wave H 主/子状态码  
- 不改 v2 sequential/parallel、wave 子任务类型  
- 不做 lifecycle 快照表  
- 不改 open-api-service（除非必须暴露新枚举给字典接口——若字典走 vul-pass 枚举反射则自动带上）

---

## 4. 策略定稿（用户确认）

### 4.0 工单来源字段

| 概念 | 字段位置 | 值 | 说明 |
|------|----------|----|------|
| 指令来源 | **外层工单/任务列表 `source`**（非 vul_scan_task） | **0** | 企业本地工单 |
| 指令来源 | 同上 | **1** | 部侧工单 |
| 业务场景 | 任务 **`ctxCode`** | **3** | 行业漏洞专项排查 |

> `vul_scan_task` **未存 source**。策略入参必须从外层工单透传，或按 `orderId` 回查（如系统漏洞处置工单）。  
> **禁止**用 `ctxCode==2` 表示企业（现网 ProMethodDrawer 误判，本 Wave 修正）。

代码依据：`VulnDisposeOrderDTO` / `VulnCommonBaseDTO`：`指令来源（0-企业本地工单，1-部侧工单）`；前端 `SysVulnOrder` 列表同义。

### 4.1 扫描类手段默认 reportType

适用：`verifySrcMethod` / `procMethod` ∈ **1020, 1022, 1023, 1024, 1027**

| 条件 | 默认 reportType | 说明 |
|------|-----------------|------|
| `source == 0` | **3** | 企业 → 常态化 XLSX |
| `source == 1` 且 `ctxCode == 3` | **3** | 部侧 + 行业漏洞专项排查 → 常态化 XLSX |
| `source == 1` 且其它 ctxCode | **10** | 部侧其它 → 绿盟 XML V1.2 |
| `source` 缺失 | **10** | 保守兜底 |

```text
if source == 0:
  return 3
if source == 1 and ctxCode == 3:
  return 3
return 10
```

### 4.2 连通性检测 1028（方案 A）

| 项 | 定稿 |
|----|------|
| 新码 | **34**（建议名：连通性检测V1.0） |
| Parser | `ConnectivityCheckParser` |
| 默认分配 | 凡手段=1028 → **固定 34**（不依赖 source/ctxCode） |
| upload | 建议 `1` |
| hidden | `1` |

### 4.3 其它手段（沿用现网，本 Wave 可迁到策略类）

| 手段 | 默认 |
|------|------|
| 1021 POC | 23 |
| 1026 交叉扫描 | 21 |
| 1040 EXP | 22 |
| 1050～1053 修复 | 31 |
| 1060/1061 修复核验外壳 | 32 |
| 1080 关联分析 | 51 |

---

## 5. 任务矩阵

| Wave | Agent | 改什么 | 交付物 |
|------|-------|--------|--------|
| **I-0** | 文档 | PRD 策略章节；本计划定稿 | svmp |
| **I-1** | 后端 | `ReportTypeAssignStrategy`（入参含 source+ctxCode）；枚举 34；`ConnectivityCheckParser`；预览/下发透传 source 并写入 reportType | Java + 单测 |
| **I-2** | 前端 | 预览带 source；展示建议处置类型；`ProMethodDrawer` 优先子任务 reportType；去掉 ctxCode==2 误判 | Vue + lint |
| **I-3** | QA | 映射单测 + 回归 | 验收报告 |

**预计并行**：I-0 后 I-1∥I-2 骨架；I-3 收尾。

---

## 6. 分支与规范

| 项 | 约定 |
|----|------|
| 分支 | `feature/fix-ledger-log-records` |
| Skills | `esmp-backend-dev`、`esmp-frontend-dev`、`esmp-rd-standards` |
| Rules | `java-hard-ban`、`backend-layer-boundary-strict`、`test-required-strict`、`security-hard-ban` |
| Commit | `[ADD]`/`[IMP]`；未要求不 push |

---

## 7. 风险

| 风险 | 缓解 |
|------|------|
| 新码 34 冲突 | Grep 确认；冲突顺延 |
| Parser 与绿盟端口解析重复 | 复用 Abstract 公共抽取 |
| 任务无 source | 预览/下发强制透传；后端可按 orderId 回查工单作兜底 |
| 前端仍用 ctxCode==2 | I-2 删除该误判，改为 source |
| source 缺失 | 默认 10；可配置 |

---

## 8. 默认决策（同意执行且不另说明）

1. 新码 **34**；冲突则顺延。  
2. `source==0 → 3`；`source==1 && ctxCode==3 → 3`；其它扫描类 → **10**；**1028 → 34**。  
3. 预览入参透传外层工单 `source`；策略禁止 `ctxCode==2` 判断企业。  
4. 用户处置时可改选。  
5. 未要求不 commit / push。

---

请确认计划；回复 **同意执行** 后开工。  
若 `source` 缺失时兜底不要用 10，请注明。
