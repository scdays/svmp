# 修复核验全链路 — Wave B 联调验收报告 v1.0

> **对应计划**：`修复核验全链路-开发计划-v1.3.md` · Wave B  
> **对应 PRD**：`修复核验全链路-vul-pass-PRD.md` v1.4.2  
> **执行日期**：2026-07-16  
> **分支**：`feature/fix-ledger-log-records`（vul-pass + asset-newleak-manage）

---

## 1. 验收结论

| 维度 | 结论 | 说明 |
|------|------|------|
| **后端单元/回归** | **通过** | `mvn test` 全绿；新增 Gate 级联 + `prc_*` 回填单测 |
| **前端静态检查（B3）** | **通过** | `ProMethodDrawer.vue` lint 无报错 |
| **TC 用例（自动化映射）** | **部分通过** | TC-05～08 维持绿；TC-12 单测补强；TC-09/11/14 仍缺运行时/E2E |
| **离线 recycle → Verdict → 台账闭环** | **代码就绪，E2E 待补** | `recycle` 已串联级联派生 + 分层判定 + 台账写入；缺样例报告联调 |
| **F-W2 工作台 Vue** | **未启动** | 归下一 Wave，原型 §7.5 已定稿 |

**Wave B 总评**：**B1/B3 自动化增量验收通过，可并行启动 F-W2**；TC-09/11/14 及 Gate→Scan **有存活 IP 派生落库**路径须在联调环境或补 Mock 集成测后关单。

---

## 2. 本 Wave 交付物

### 2.1 后端（B1）

| 交付 | 文件 | 说明 |
|------|------|------|
| 回收后 `prc_vul_num` / `prc_ast_num` 回填 | `VulScanTaskSubDomainServiceImpl#refreshSubTaskProcessCounts` | 绑定实例后 `prcVulNum=实例数`；`prcAstNum` 兜底 `astNum` |
| recycle 路径接线 | 同上 `#recycle`（两处 `bindTaskVulInstList` 之后） | 与子任务卡片「实际处置数」展示对齐（§18.5 口径仍待产品确认） |
| Gate→Scan 级联单测 | `VulScanTaskSubDomainServiceGateCascadeTest` | 5 用例，见 §3 |

**既有能力（Wave B 依赖，本 Wave 未改逻辑）**：

- `trySpawnScanSubTasksAfterGate`：Gate 全终态 → 按存活 IP 派生 SCAN 子任务
- `applyVerifyFixVerdict`：分层判定 vulInfoStat 6/7/10
- `writeLedger` / `writeVulInstLedger`：台账 9+10 骨架

### 2.2 前端（B3）

| 交付 | 文件 | 说明 |
|------|------|------|
| 核验处置默认报告类型 | `ProMethodDrawer.vue` | `procMethod` 1060/1061 且 `tskPhase` 3/4 时默认 **reportType=32**（漏洞核验修复 V1.0）；用户仍可改选 3/10 |

---

## 3. 执行记录

### 3.1 后端（vul-pass）

```bash
cd project_backend/svmp/vul-pass
mvn test   # exit 0

# Wave B 增量专项
mvn test -Dtest=VulScanTaskSubDomainServiceGateCascadeTest,\
VulScanTaskSubDomainServiceSetTaskTest,\
VerifyFixDispatchPlannerTest,\
VerifyFixVerdictServiceTest
# exit 0
```

**新增/补强单测**：

| 测试类 | 方法 | 结果 | 映射 TC |
|--------|------|------|---------|
| `VulScanTaskSubDomainServiceGateCascadeTest` | `trySpawn_notWaitingVerifyGate_returnsFalse` | ✅ | 级联 guard |
| 〃 | `trySpawn_gateNotAllTerminal_returnsFalse` | ✅ | Gate 未终态不派生 |
| 〃 | `trySpawn_noAliveIp_marksVerifyDone` | ✅ | **TC-12** |
| 〃 | `trySpawn_noScanGroups_marksVerifyDone` | ✅ | 仅 Gate 无 Scan 占位 |
| 〃 | `refreshSubTaskProcessCounts_setsPrcVulNumFromInstList` | ✅ | §18 计数回填 |

### 3.2 前端（asset-newleak-manage）

```bash
cd project_frontend/asset/asset-newleak-manage
npm run lint:nofix -- --no-error-on-unmatched-pattern \
  src/views/VulnManagePlat/components/TaskDetails/ProMethodDrawer.vue
# DONE  No lint errors found!
```

---

## 4. TC 用例对照（相对 Wave A 变化）

| 用例 | 场景 | Wave A | Wave B | 备注 |
|------|------|--------|--------|------|
| TC-05～08 | 分层判定 6/7/10 | ✅ | ✅ | `VerifyFixVerdictServiceTest` |
| TC-09 | 无 confirmToken 下发拒绝 | ⚠️ | ⚠️ | 仅 `confirmToken_store` 存储层 |
| TC-10 | onlineAddr 覆盖 | ⚠️ | ⚠️ | 缺 recycle 后台账 SQL |
| TC-11 | logType=1060 + 内层 1028 | ❌ | ❌ | 待 B2 集成测或联调脚本 |
| TC-12 | Gate 后全不存活 | ⚠️ | **✅（单测）** | `trySpawn_noAliveIp_marksVerifyDone` |
| TC-13 | Gate 后部分存活派生 Scan | ⚠️ | ⚠️ | 预览占位 ✅；**有存活 IP + saveBatch 未测** |
| TC-14 | 离线完整报告 9+10 双波 | ❌ | ⚠️ | 逻辑在 recycle 链；**缺样例 XML/XLSX E2E** |

---

## 5. 阻塞 / 待办清单

| 优先级 | 项 | 建议动作 | 目标 Wave |
|--------|-----|----------|-----------|
| P1 | TC-11 台账 1060+1028 | 补 recycle 集成测或联调 SQL 断言 | B2 续 |
| P1 | TC-14 离线双波 9+10 | 准备样例 reportType 3/10/32 报告 + 手工/E2E | B2 续 |
| P2 | TC-09 dispatch HTTP | MockMvc 测无 token 400/拒绝 | B2 续 |
| P2 | TC-13 存活 IP 派生落库 | Mockito 化 `saveBatch` 或联调演示 | B2 续 |
| P2 | TC-10 onlineAddr | 联调环境靶标工单 | 环境就绪后 |
| P3 | §18.5 `prc_vul_num` 产品口径 | 确认后更新 PRD + 前端列文案 | 产品 |
| — | **F-W2 TaskDrawer §7.5** | 对照 HTML 原型落地 Vue | **建议立即并行** |

---

## 6. 离线闭环链路（设计 vs 本 Wave 验证）

```text
导入报告 (reportType 3/10/32)
  → recycle 解析 + 实例绑定
  → refreshSubTaskProcessCounts（本 Wave 新增）
  → trySpawnScanSubTasksAfterGate（Gate 波）
       ├─ 无存活 / 无 Scan 组 → WAITING_VERIFY_DONE
       └─ 有存活 → 派生 SCAN 子任务 → 等待二次 recycle
  → applyVerifyFixVerdict（Scan 或单波）
  → writeLedger + writeVulInstLedger（9+10）
  → refreshTaskStatus / refreshOrderStatus
```

| 检查点 | 单测 | 运行时/E2E |
|--------|------|------------|
| Verdict 6/7/10 | ✅ | 待样例报告 |
| Gate 无存活 → 完成态 | ✅ | 待联调 |
| Gate 有存活 → 派生 Scan | ⚠️ 未测 saveBatch | 待联调 |
| prc_vul_num 回填 | ✅ | 待 UI 展示（F-W2） |
| 台账 9+10 成对 | — | **TC-14 待补** |
| ProMethodDrawer 默认 32 | lint ✅ | 待手工导入验证 |

---

## 7. 下一步建议

1. **启动 F-W2**：按 PRD §7.5 + HTML 原型扩展 `TaskDrawer.vue`（可与 B2 续项并行）。
2. **B2 续**：补 TC-09/11/13/14 集成测或联调脚本；有环境后跑一轮工单 34 全链路。
3. **产品确认** §18.5 `prc_vul_num` 展示口径后再定子任务卡片列文案。

---

## 8. 签核

| 角色 | 结论 | 日期 |
|------|------|------|
| Wave B 自动化增量 | **通过** | 2026-07-16 |
| Wave B 端到端闭环 | **待补测** | — |
| F-W2 启动 | **建议批准** | 2026-07-16 |
