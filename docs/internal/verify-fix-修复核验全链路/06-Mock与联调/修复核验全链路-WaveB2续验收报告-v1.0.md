# 修复核验全链路 — Wave B2 续验收报告 v1.0

> **对应计划**：`修复核验全链路-开发计划-v1.3.md` · Wave B2 续  
> **对应 PRD**：`修复核验全链路-vul-pass-PRD.md` v1.4.4 · §10 / §17.6 TC-09/11/13/14  
> **执行日期**：2026-07-16  
> **分支**：`feature/fix-ledger-log-records`（vul-pass）

---

## 1. 验收结论

| 维度 | 结论 | 说明 |
|------|------|------|
| **后端单元/回归** | **通过** | `mvn test` 全绿 |
| **TC-09 confirmToken** | **通过（单测）** | blank / null / 无效拒绝；有效 token 返回 plan |
| **TC-11 台账 1060+1028** | **通过（单测）** | Gate `procMethod=1060` + `verifySrcMethod=1028`；`initLog.logType=1060`；rela 优先写 verifySrcMethod |
| **TC-13 存活派生落库** | **通过（单测）** | 有存活 IP → SCAN `saveBatch` + `WAITING_VERIFY_SCAN` |
| **TC-14 台账 9+10 成对** | **通过（单测）** | CREATE→`issueVerifyTaskActionService`；RESULT→`verifyResultActionService` |
| **离线完整报告 E2E** | **仍待环境** | 样例报告一次性导入写完整 Gate+Scan 9/10 字段，需联调样例 |

**Wave B2 续总评**：**自动化缺口已关单**；全链路 E2E（真实/样例报告）仍可在 F-W2 续或联调环境并行补齐。

---

## 2. 本 Wave 交付物

### 2.1 单测

| 测试类 | 方法 | 映射 TC |
|--------|------|---------|
| `VulScanTaskAppServiceRequireConfirmTokenTest` | blank / null / unknown / valid | **TC-09** |
| `VulScanTaskSubDomainServiceVerifyLedgerTest` | Gate 1060+1028；initLog；arrangeActions 9/10；ensurePair | **TC-11 / TC-14** |
| `VulScanTaskSubDomainServiceGateCascadeTest` | `trySpawn_aliveIp_spawnsScanAndPersists`（Proxy stub `saveBatch`） | **TC-13** |

### 2.2 生产代码微调

| 变更 | 文件 | 说明 |
|------|------|------|
| rela `srcMethod` 优先 `verifySrcMethod` | `VulScanTaskSubDomainServiceImpl#writeVulInstLedger`（两处） | 对齐 PRD「外壳 1060、内层 1028/1022…」；无 verifySrcMethod 时回落 procMethod |

---

## 3. 执行记录

```bash
cd project_backend/svmp/vul-pass
mvn test "-Dtest=VulScanTaskAppServiceRequireConfirmTokenTest,VulScanTaskSubDomainServiceVerifyLedgerTest,VulScanTaskSubDomainServiceGateCascadeTest"
# exit 0

mvn test
# exit 0
```

---

## 4. 遗留

| 项 | 说明 |
|----|------|
| TC-14 全链路 E2E | 离线完整报告导入 → Gate+Scan 各自完整 opCode 9+10；需样例报告 |
| F-W2 续 | 真实工单对照 PRD §7.5.7 checklist |
| §18.5 `prc_vul_num` | 产品确认口径 |
| Review | 建议 `esmp-code-review-strict` |

---

## 5. 结论

Wave B2 续 **自动化验收通过**，可进入 F-W2 续 / Review。未 commit（待用户指令）。
