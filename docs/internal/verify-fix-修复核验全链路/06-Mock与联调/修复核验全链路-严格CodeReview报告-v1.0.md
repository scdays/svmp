# 修复核验全链路 — 严格 Code Review 报告 v1.0

> **范围**：Wave B2 续（vul-pass）+ Wave F-W2 / F-W2 续（asset-newleak-manage）  
> **规范**：`esmp-code-review-strict` + `esmp-rd-standards`  
> **日期**：2026-07-16  
> **分支**：`feature/fix-ledger-log-records`

---

## 严格 Code Review 结果

### 阻塞问题

| 文件 | 行号 | 问题 | 原因 | 修复建议 |
|------|-----:|------|------|----------|
| — | — | 无 | — | — |

### 非阻塞建议

| 文件 | 行号 | 建议 | 收益 |
|------|-----:|------|------|
| `VulScanTaskSubDomainServiceImpl.java` | ~687 / ~2110 | `writeVulInstLedger` 两处 `verifySrcMethod` 优先逻辑可抽私有方法 `resolveLedgerSrcMethod`，避免双份注释 | 降低漏改风险 |
| `VulScanTaskSubDomainServiceVerifyLedgerTest.java` | — | 未直接测 `writeVulInstLedger` 写 rela（依赖 `LogInfoReqParamsEvent`）；当前靠 build+initLog+代码审查 | 有样例 stub 时可补一测 |
| `MainTaskSummary.vue` | ~171 `stepClass` | `tskStat` 为 0–3 时五步皆 pending，联调确认后补专用映射 | 核验进行中高亮更准 |
| `SearchTask/*.vue` | 多处 | 追踪子表仍可能有 ellipsis（未纳入本 Wave） | 与 §7.5.7「禁止截断」完全一致 |
| `ResultSummaryPanel.vue` | — | 未展示 opCode 9/10 成对汇总（§7.5.4） | 台账审计可读性 |

### 验收结论

- [x] **可合入**（无阻塞问题；自动化验证通过）
- [ ] 需修复后再验收

### 验证情况

- **已运行**：
  - `project_backend/svmp/vul-pass`：`mvn test` → exit 0
  - `asset-newleak-manage`：TaskDetails 相关 8 文件 `npm run lint:nofix` → 无报错
  - §7.5.7 静态对照（[F-W2 续对照](32c68ac0-6610-45a4-83b2-54565f48dd5e) + 本 Wave polish）
- **未运行**：真实工单浏览器联调、样例报告全链路 E2E
- **失败输出摘要**：无

### 维度摘要（审查覆盖）

| 维度 | 结论 |
|------|------|
| 编译风险 | 通过（`mvn test` / lint） |
| DDD 分层 | B2 改动在 DomainServiceImpl，未跨层 |
| 命名 / GitLab Java 强制 | 未见 `param.equals`、包装类型 `==` 等红线 |
| NPE / 异常 / 日志 | `requireConfirmToken` 用 Assert；单测覆盖拒绝路径 |
| 事务 / 幂等 / 并发 | 未改事务边界；TokenStore 内存 ConcurrentHashMap（既有） |
| 安全 | 无硬编码密钥/IP；前端仍走既有 API |
| SQL / Maven | 未改 Mapper/POM |
| 单测覆盖 | TC-09/11/13/14 单测已补；符合 test-required |
| 可维护性 / 越界 | F-W2 续仅 polish UI；B2 仅 rela srcMethod + 测试 |
| 过度设计 | 无新依赖/抽象层 |

### 合入建议

1. 可按 `[IMP]` / `[FIX]` 分前端、后端两次提交（或一次聚合，按团队习惯）。
2. 合入前仍建议联调环境走一轮 §7.5.7 视觉 checklist。
3. 未要求则不自动 commit / push。
