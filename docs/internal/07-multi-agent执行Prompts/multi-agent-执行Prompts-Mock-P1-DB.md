# Multi-Agent 执行 Prompts

> **自动生成**：`2026-06-15` · 源文件 [`features/op-mock-p1-db.yaml`](./features/op-mock-p1-db.yaml)  
> **功能**：Mock 实例 MySQL 落库（方案一）（`OP-MOCK-P1-DB` / P1）  
> **工作流**：[prd-to-multi-agent-工作流](./prd-to-multi-agent-工作流.md)  
> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py

---

## 0. 功能概览

| 项 | 值 |
|----|-----|
| 功能 ID | `OP-MOCK-P1-DB` |
| 名称 | Mock 实例 MySQL 落库（方案一） |
| 阶段 | P1 |
| 落地方案 | `svmp/docs/internal/引擎对接与Mock模式方案.md` |
| PRD | `svmp/docs/internal/open-api-mock-instance-db-PRD.md` |

---

## 1. 全局必读

- .cursor/skills/esmp-rd-standards/SKILL.md
- svmp/docs/internal/open-api-mock-instance-db-PRD.md
- svmp/docs/internal/引擎对接与Mock模式方案.md
- project_backend/svmp/open-api-service/src/main/resources/mock/engine/README.md
- .cursor/skills/esmp-backend-dev/SKILL.md
- .cursor/rules/open-api-service-ddd.mdc

---

## 2. 交付门禁（Integration 核对）

- scanTemplateId=1001 type=1 任务 FINISHED 后 open_vuln_instance 约 500 条且 task_id 正确
- 经 open-api-service 的 POST /instances/search 与 fixture 字段一致
- PUT 处置操作后 GET vulInfoStat 保持库表值
- scanTemplateId=1002/1003 与 type=3 任务命中对应 bundle 条数
- 重启后 GET 任务进度仍为 FINISHED 而非 mock engine task not found
- 同一 taskId 重复 ingest 幂等无 UK 冲突
- auto-ingest-instances-on-finish=false 时不落库、仍可读 fixture
- powershell verify-open-api-ddd.ps1 -Compile 通过

---

## 3. Agent 索引

| Prompt | Agent | 依赖 |
|--------|-------|------|
| **M1** | Backend-Mock-Instance-DDL | — |
| **M2** | Backend-Mock-Instance-Ingest | M1 |
| **M3** | Backend-Mock-Instance-Gateway | M2 |
| **M4** | Integration-Mock-Instance-DB | M1, M2, M3 |

---

## 4. 各 Agent Prompt

## Prompt M1 — Backend-Mock-Instance-DDL

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/src/main/resources/db/**
- open-api-service/**/infra/dao/**

**禁止路径**

- project_frontend/**
- partner-gateway/**
- vul-pass/**

**必读**

- svmp/docs/internal/open-api-mock-instance-db-PRD.md
- open-api-service/src/main/resources/db/mysql/open_vuln_instance.groovy

**必须交付**

- Liquibase changeset 扩展 open_vuln_instance（task_id/ext_task_id/ingest 字段）
- OpenVulnInstancePO + Mapper + XML（如需）
- open_task 可选 ingest 字段 changeset

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent M1 · Mock 实例 DDL 与持久化层负责人。

【只改】open-api-service 下 db/mysql、groovy changeset、infra/dao/po/mapper。
【禁止】改前端、partner-gateway、vul-pass。

【目标】按 PRD §4.1 扩展 open_vuln_instance，实现 PO/Mapper。
【约束】UTF-8 无 BOM；changeset id 不重复；字段命名与 open_task 风格一致。

【交付】changeset 列表 + 新字段说明 + 编译通过
```

---

## Prompt M2 — Backend-Mock-Instance-Ingest

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/domain/instance/**
- open-api-service/**/domain/task/**
- open-api-service/**/infra/repository/**
- open-api-service/**/infra/adapter/mock/**

**禁止路径**

- project_frontend/**
- partner-gateway/**

**必读**

- svmp/docs/internal/open-api-mock-instance-db-PRD.md
- open-api-service/src/main/java/com/vtc/openapi/infra/adapter/mock/MockFixtureResolver.java

**必须交付**

- InstanceIngestDomainService（幂等批量插入）
- mergeEngineProgress 首次 FINISHED 触发 ingest
- 实现 auto-ingest-instances-on-finish 配置
- 批量 insert + 幂等（同 task_id 不重复行）
- vul_info_id 生成策略（含 taskId 前缀避免 UK 冲突）

**验证**

- 单元测试或集成测试：mock FINISHED 后有库表记录
- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt M1  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent M2 · Mock 实例 ingest 域服务负责人。

【依赖】M1 DDL/Mapper 已经就绪。
【目标】任务 FINISHED 时从 MockFixtureResolver 取 bundle 并写入 open_vuln_instance。
【约束】仅 adapter-mode=mock；禁止向日志输出敏感字段。

【交付】改动清单 + ingest 流程说明 + 测试/手工验证步骤
```

---

## Prompt M3 — Backend-Mock-Instance-Gateway

**负责人**：业务后端  

**工程**：`project_backend/svmp/open-api-service`

**可改路径**

- open-api-service/**/instance/**
- open-api-service/**/infra/adapter/VulnInstanceGatewayMockImpl.java
- open-api-service/**/infra/adapter/SvmpEngineAdapterMockImpl.java
- open-api-service/**/infra/repository/**

**禁止路径**

- project_frontend/**
- partner-gateway/**

**必读**

- svmp/docs/internal/open-api-mock-instance-db-PRD.md
- svmp/docs/external/网络安全漏洞管理平台 · API 接口文档V1.0.4.md

**必须交付**

- VulnInstanceGatewayMockImpl 读/写改走 DB，移除 mockStateOverrides
- search 按 partner + taskId/extTaskId 分页
- updateInstance 更新 vul_info_stat + snapshot_json
- SvmpEngineAdapterMockImpl getTaskProgress 无内存状态时读 open_task

**验证**

- powershell -File svmp/docs/internal/scripts/verify-open-api-ddd.ps1 -Compile

**依赖**：Prompt M2  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent M3 · Mock 实例网关读写库负责人。

【依赖】M2 ingest 已可写库数据。
【目标】Mock 模式下实例 API 全部走 open_vuln_instance，重启数据不丢。
【禁止】改动 vul-pass Feign 适配（adapter-mode=vul-pass 路径保持原样）。

【交付】改动清单 + AC-02/AC-03 验证说明
```

---

## Prompt M4 — Integration-Mock-Instance-DB

**负责人**：联调验收  

**可改路径**

- svmp/docs/internal/**
- open-api-service/src/main/resources/mock/**

**必读**

- svmp/docs/internal/open-api-mock-instance-db-PRD.md
- open-api-service/src/main/resources/mock/engine/README.md

**必须交付**

- 联调手册-Mock-Instance-DB.md（对照 PRD AC 与验收表）
- acceptance 勾选结果

**验证**

- acceptance 列表全部通过

**依赖**：Prompt M1, Prompt M2, Prompt M3  

### 执行 Prompt（复制到 Cursor Agent）

```markdown
你是 Agent M4 · OP-MOCK-P1-DB 联调验收负责人。

【依赖】M1/M2/M3 已完成。
【任务】编写联调手册：mock profile 启动 → 创建 1001/1002/1003 任务 → 等 FINISHED → search → verify → 重启 → 再查。
【输出】通过项 / 阻塞项 / 修改建议。
```

---

## 5. 并行执行建议

```text
Wave 1（可并行）: H, D, F
Wave 2（可并行）: I（依赖 H）, E（依赖 F）
Wave 3: G（依赖 I + D + F + E）
Wave 4（P1）: J（依赖 G）
```
