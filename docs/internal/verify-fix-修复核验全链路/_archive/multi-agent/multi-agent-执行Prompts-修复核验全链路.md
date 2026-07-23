# Multi-Agent 执行 Prompts

> **自动生成**：`2026-07-14` · 源文件 [`features/vulpass-verify-fix-p0.yaml`](./vulpass-verify-fix-p0.yaml)  
> **功能**：修复核验全链路（vul-pass）P0–P2（`VULPASS-VERIFYFIX-P0` / P0-P2）  
> **工作流**：[prd-to-multi-agent-工作流](../../../08-工具与指南/prd-to-multi-agent-工作流.md)  
> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py

---

## 0. 功能概览

| 项 | 值 |
|----|-----|
| 功能 ID | `VULPASS-VERIFYFIX-P0` |
| 名称 | 修复核验全链路（vul-pass）P0–P2 |
| 阶段 | P0-P2 |
| PRD | `svmp/docs/internal/04-子PRD与规格/修复核验全链路-vul-pass-PRD.md` |

---

## 1. 全局必读

- .cursor/skills/esmp-rd-standards/SKILL.md
- .cursor/skills/esmp-backend-dev/SKILL.md
- .cursor/skills/esmp-frontend-dev/SKILL.md
- .cursor/rules/java-hard-ban.mdc
- .cursor/rules/backend-layer-boundary-strict.mdc
- .cursor/rules/backend-ddd-layers.mdc
- .cursor/rules/backend-naming.mdc
- .cursor/rules/test-required-strict.mdc
- .cursor/rules/security-hard-ban.mdc
- svmp/docs/internal/04-子PRD与规格/修复核验全链路-vul-pass-PRD.md

---

## 2. 交付门禁（Integration 核对）

- 工单34/1063仅 stat=5 且 src_method∈105x 进入编排
- preDispatch 返回 plan+confirmToken；未 confirm 调用 dispatch 被拒绝
- 确认后每条 subTask 写 opCode=9；回收后写 opCode=10 且 onlineAddr 覆盖负责 IP
- 混合105x 预览正确；1053 alive=false→stat=6；1050 alive不一致→stat=10
- NSFOCUS_XML_III 与 PLATFORM_VUL_INST_XLSX_V2 均可判定
- Feature flag 关闭走 legacy；mvn compile / lint 通过

---

## 3. Agent 索引

| Prompt | Agent | 依赖 |
|--------|-------|------|
| **B1** | Backend-P0-DDL-Merger-Ledger | — |
| **B2** | Backend-P1-Planner-Confirm | B1 |
| **F1** | Frontend-P1-PlanPreview | B2 |
| **B3** | Backend-P2-Slicer-Verdict | B2 |
| **F2** | Frontend-P2-OfflineDispose | B3 |
| **R1** | Integration-Review | B3, F2 |

---

## 4. 各 Agent Prompt

## Prompt B1 — Backend-P0-DDL-Merger-Ledger

**负责人**：业务后端  

**工程**：`project_backend/svmp/vul-pass`

**可改路径**

- project_backend/svmp/vul-pass/src/main/resources/db/**
- project_backend/svmp/vul-pass/src/main/java/com/vtc/security/infra/**
- project_backend/svmp/vul-pass/src/main/java/com/vtc/security/domain/pass/**
- project_backend/svmp/vul-pass/src/main/java/com/vtc/security/ui/dto/**
- project_backend/svmp/vul-pass/src/test/**

**禁止路径**

- project_frontend/**
- project_backend/svmp/open-api-service/**
- project_backend/svmp/partner-gateway/**

**必读**

- svmp/docs/internal/04-子PRD与规格/修复核验全链路-vul-pass-PRD.md
- .cursor/skills/esmp-rd-standards/SKILL.md
- .cursor/skills/esmp-backend-dev/SKILL.md

**必须交付**

- Liquibase changeset：vul_scan_task_sub 新增 src_method/verify_src_method/expect_alive/actual_alive/alive_consistent/scanner_source/confirm_token
- Liquibase：vul_scan_task 新增 confirm_token（若尚无）
- TskTypeEnum（10–15）
- OnlineAddrMerger + VerifyResultActionService/TaskResultActionService 接入
- 核验实例 src_method 校验（1050–1053 + fixLnk/defDev）
- astUnitNum 拆分后每条 subTask 保障 opCode=9/10 成对可写
- Nacos/配置 compliance.ledger-online-addr-merge-enabled 等 feature flag
- 单测：OnlineAddrMerger、flag 关闭走 legacy

**验证**

- mvn -pl project_backend/svmp/vul-pass -am compile -q（或模块内 compile）
- 相关单测通过

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent B1 · 修复核验 P0（DDL + OnlineAddrMerger + 台账）负责人。

【工程】project_backend/svmp/vul-pass，分支 feature/fix-ledger-log-records
【禁止】改 open-api-service、前端、无关服务；禁止重写 IssueVerify/VerifyResult 骨架。

【目标·PRD §5.4/§6.7/§8/§14.5 P0】
1. Liquibase groovy 追加字段（对齐现有 vul_scan_task_sub.groovy / vul_scan_task.groovy 风格，changeset id 不重复）
2. PO/DO/DTO 同步新字段；新增 TskTypeEnum
3. 实现 OnlineAddrMerger（合并 portList + 实例 IP），接入 TaskResultActionService 与 VerifyResultActionService；flag 关则走原 onlineAddrFileLoc
4. 核验加载实例校验：stat=5 且 src_method∈1050–1053；1050 需 fixLnk；1051/1052 需 defDev
5. 在现有 astUnitHandle 拆分路径上，确保每个 subTask 均可成对写 9/10（合规保障，不改成策略展开——策略是 P1）
6. 配置项见 PRD §8.2；UTF-8 无 BOM；补单测

【纠偏】tsk_model：0=在线、1=离线；核验默认 1。
【交付】改动清单 + 编译/测试结果说明
```

---

## Prompt B2 — Backend-P1-Planner-Confirm

**负责人**：业务后端  

**工程**：`project_backend/svmp/vul-pass`

**可改路径**

- project_backend/svmp/vul-pass/src/main/java/com/vtc/security/**
- project_backend/svmp/vul-pass/src/test/**
- project_backend/svmp/vul-pass/src/main/resources/**

**禁止路径**

- project_frontend/**
- project_backend/svmp/open-api-service/**

**必读**

- svmp/docs/internal/04-子PRD与规格/修复核验全链路-vul-pass-PRD.md

**必须交付**

- VerifyFixStrategyResolver / DispatchPlanner / EngDeviceMatcher / LastScannerResolver
- VulScanTaskStatEnum 扩展 PREVIEW(4)/WAITING_IMPORT(5)
- preDispatch 返回 VerifyFixDispatchPlan + confirmToken；dispatch 校验 token

**验证**

- mvn compile + Planner/Confirm 相关单测

**依赖**：Prompt B1  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
（请在 YAML 中填写 prompt 字段）
```

---

## Prompt F1 — Frontend-P1-PlanPreview

**负责人**：前端  

**工程**：`project_frontend/asset/asset-newleak-manage`

**可改路径**

- project_frontend/asset/asset-newleak-manage/**

**禁止路径**

- project_backend/**
- project_frontend/asset/asset-openplatform-manage/**

**必读**

- svmp/docs/internal/04-子PRD与规格/修复核验全链路-vul-pass-PRD.md
- .cursor/skills/esmp-frontend-dev/SKILL.md

**必须交付**

- VerifyFixPlanPreview.vue；BaseInfo/AddTaskDrawer/SafeSourceDriver 改造
- API plan/confirmToken；确认态禁改 engHash

**验证**

- npm run lint（或项目既有 lint）

**依赖**：Prompt B2  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
（请在 YAML 中填写 prompt 字段）
```

---

## Prompt B3 — Backend-P2-Slicer-Verdict

**负责人**：业务后端  

**工程**：`project_backend/svmp/vul-pass`

**可改路径**

- project_backend/svmp/vul-pass/**

**禁止路径**

- project_frontend/**
- project_backend/svmp/open-api-service/**

**必须交付**

- ScanResultStageSlicer / VerifyFixVerdictService / AliveConsistencyChecker
- recycle 增强与 submit 回传

**验证**

- 判定单测 TC-01~07

**依赖**：Prompt B2  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
（请在 YAML 中填写 prompt 字段）
```

---

## Prompt F2 — Frontend-P2-OfflineDispose

**负责人**：前端  

**工程**：`project_frontend/asset/asset-newleak-manage`

**可改路径**

- project_frontend/asset/asset-newleak-manage/**

**禁止路径**

- project_backend/**

**必须交付**

- ProMethodDrawer reportType 默认 3/10；submit 接线

**验证**

- lint

**依赖**：Prompt B3  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
（请在 YAML 中填写 prompt 字段）
```

---

## Prompt R1 — Integration-Review

**负责人**：审查  

**工程**：`project_backend/svmp/vul-pass`、`project_frontend/asset/asset-newleak-manage`

**必读**

- .cursor/skills/esmp-code-review-strict/SKILL.md
- .cursor/skills/esmp-rd-standards/checklist.md

**必须交付**

- 对照 PRD §9 通过/阻塞清单

**验证**

- compile + lint + 验收勾选

**依赖**：Prompt B3, Prompt F2  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
（请在 YAML 中填写 prompt 字段）
```

---

## 5. 并行执行建议

```text
Wave 1（可并行）: H, D, F
Wave 2（可并行）: I（依赖 H）, E（依赖 F）
Wave 3: G（依赖 I + D + F + E）
Wave 4（P1）: J（依赖 G）
```
