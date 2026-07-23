# 修复核验全链路 — Wave A 联调验收报告 v1.0

> **对应计划**：`修复核验全链路-开发计划-v1.3.md` · Wave A  
> **对应 PRD**：`修复核验全链路-vul-pass-PRD.md` v1.4.2  
> **执行日期**：2026-07-16  
> **分支**：`feature/fix-ledger-log-records`（vul-pass + asset-newleak-manage）

---

## 1. 验收结论

| 维度 | 结论 | 说明 |
|------|------|------|
| **后端单元/回归（§19）** | **通过** | `mvn test` 全绿；门闸编排 + §18 修复单测全部通过 |
| **前端静态检查** | **通过** | `TaskDrawer.vue`、`VerifyFixPlanPreview.vue` lint 无报错 |
| **TC 用例（自动化映射）** | **部分通过** | TC-01～08、TC-12～14 有单测覆盖；TC-09～11 仅局部单测，缺 HTTP/台账 E2E |
| **端到端联调（工单→下发→回收→台账）** | **待补** | 需联调环境 + 样例工单/报告；本 Wave 未接入真实 DB/Kafka |

**Wave A 总评**：**自动化回归门禁通过，可进入 Wave B**；端到端联调项列入 §4 阻塞/待办，不阻塞 B1/B3 开发，但 **Wave B 合入前须补测 TC-09～11、TC-14 运行时链路**。

---

## 2. 执行记录

### 2.1 后端（vul-pass）

```bash
cd project_backend/svmp/vul-pass
mvn test   # exit 0
```

**§19 专项回归（PRD 明示）**：

| 测试类 | 方法 | 结果 |
|--------|------|------|
| `VulScanTaskSubDomainServiceSetTaskTest` | `setTask_preservesWaitingVerifyGate` | ✅ |
| 〃 | `setTask_defaultsToWaitingForNonGate` | ✅ |
| 〃 | `filterAssetsByIps_setsAstNumPerIp` | ✅ |
| 〃 | `syntheticAssetsFromIps_setsAstNumOne` | ✅ |
| 〃 | `buildSubTasksFromVerifyFixPlan_gateSubTaskFieldsComplete` | ✅ |

**修复核验域单测**：

| 测试类 | 用例数 | 结果 |
|--------|--------|------|
| `VerifyFixDispatchPlannerTest` | 11 | ✅ |
| `VerifyFixVerdictServiceTest` | 6 | ✅ |
| `VerifyFixInstanceValidatorTest` | 6 | ✅ |
| `OnlineAddrMergerTest` | 4 | ✅ |

### 2.2 前端（asset-newleak-manage）

```bash
cd project_frontend/asset/asset-newleak-manage
npm run lint:nofix -- --no-error-on-unmatched-pattern \
  src/views/VulnManagePlat/components/TaskDetails/TaskDrawer.vue \
  src/views/VulnManagePlat/components/TaskSend/VerifyFixPlanPreview.vue
# DONE  No lint errors found!
```

### 2.3 交互原型（非 Wave A 门禁，已确认）

- `修复核验-任务详情工作台-原型.html` — PRD §7.5 已定稿，Vue 落地归 Wave F-W2

---

## 3. TC 用例对照（PRD §10 / §17.6）

| 用例 | 场景 | 自动化覆盖 | 结果 | 备注 |
|------|------|------------|------|------|
| TC-01 | 仅 1050 全存活，astUnitNum=-1 | `plan_only1050_astUnitUnlimited_onePhysical` | ✅ | v1.4：1 Gate + 1 SCAN 占位 = 2 |
| TC-02 | 1050+1051 全存活 | `plan_1050_and_1051_twoPhysical` | ✅ | 1 Gate + 2 SCAN = 3 |
| TC-03 | 混合四 src_method | `plan_mixedFourSrc_merge1052_1053_threePhysical` | ✅ | v1.4：1 Gate + 2 SCAN = 3（1052/1053 无二次 Scan） |
| TC-04 | astUnitNum 切 IP 批 | `plan_astUnitNum_splitsByIpBatch` | ✅ | Gate/Scan 分批计数正确 |
| TC-05 | 1053 不可达 | `tc05_1053_unreachable_pass` | ✅ | vulInfoStat=**6**（核验修复） |
| TC-06 | 1052 端口仍 open | `tc06_1052_portStillOpen_notFixed` | ✅ | vulInfoStat=**7**（核验未修复） |
| TC-07 | 1050 不存活 | `tc07b_1050_aliveInconsistent_abnormal` | ✅ | vulInfoStat=**10** |
| TC-08 | 1050 存活且未再检出 | `tc07_1050_aliveOk_notDetected_pass` | ✅ | vulInfoStat=**6** |
| TC-09 | 无 confirmToken 下发 | `confirmToken_store`（存储层） | ⚠️ | 缺 `dispatch` HTTP 集成测 |
| TC-10 | 排查 onlineAddr 覆盖 | `OnlineAddrMergerTest` | ⚠️ | 缺 recycle 后台账 SQL 验收 |
| TC-11 | logType=1060 + 内层 1028 | — | ❌ | **无单测/联调用例** |
| TC-12 | Gate 后 1050/1051 全不存活 | `plan_v14_only_1052_1053_gate_only`（部分） | ⚠️ | 预览层通过；**缺 recycle 后 trySpawnScan 不派生** 集成测 |
| TC-13 | Gate 后部分存活生成 Scan | `plan_v14_cascade_gate_and_scan_placeholders` | ⚠️ | 预览占位通过；**缺运行时派生** |
| TC-14 | 离线完整报告 9+10 | — | ❌ | 归 **Wave B** recycle 闭环 |

**§18 缺陷回归**：§18.1～§18.3 均有对应单测（见 §2.1）；§18.4 前端状态码已合入，lint 通过。

---

## 4. 阻塞 / 待办清单

| 优先级 | 项 | 负责 Wave | 建议动作 |
|--------|-----|-----------|----------|
| P1 | TC-11 台账外壳 1060 + 内层 1028 | B2 | 补 `IssueVerifyTaskActionService` / recycle 集成测或联调脚本 |
| P1 | TC-09 dispatch 无 token 拒绝 | B1 | 补 `VulScanTaskAppServiceImpl` 或 Ui 层 MockMvc 测 |
| P2 | Gate 回收 → Scan 动态派生（TC-12/13 运行时） | B1 | 补 `trySpawnScanSubTasksAfterGate` 集成测（mock recycle） |
| P2 | TC-10 onlineAddr SQL 验收 | B2 | 联调环境 + 靶标工单 |
| P2 | TC-14 离线报告双波 9+10 | B | Wave B 主交付 |
| P3 | §18.5 `prc_vul_num` 口径 | 产品 | 确认后单独立项 |

---

## 5. Gate→Scan 级联（设计 vs 实测）

| 检查点 | 设计（PRD §17） | 单测验证 |
|--------|-----------------|----------|
| dispatch 仅落 Gate 波 | §17.3.2 | ✅ `buildSubTasksFromVerifyFixPlan_gateSubTaskFieldsComplete` |
| 主任务 WAITING_VERIFY_GATE | §17.2.1 | ✅ `setTask_preservesWaitingVerifyGate` |
| 预览含 SCAN 占位 | §17.5 | ✅ `plan_v14_cascade_*` |
| recycle 后派生 Scan | §17.3.3 | ⚠️ **待 Wave B 集成测** |

---

## 6. 下一步建议

1. **立即启动 Wave B1**：Verdict + recycle 字段写全；同步补 TC-09/11/14 自动化。
2. **Wave F-W2 可与 B3 并行**：任务详情工作台 Vue 落地（§7.5）。
3. **联调环境就绪后**：按 §4 P2 项做一轮手工 E2E（工单 34 → preDispatch → confirm → 导入 XML/XLSX → 台账查询）。

---

## 7. 签核

| 角色 | 结论 | 日期 |
|------|------|------|
| 自动化回归 | **通过** | 2026-07-16 |
| 端到端联调 | **待环境补测** | — |
| Wave B 启动 | **建议批准** | 2026-07-16 |
