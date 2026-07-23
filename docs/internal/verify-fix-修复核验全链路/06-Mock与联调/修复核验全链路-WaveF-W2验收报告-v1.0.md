# 修复核验全链路 — Wave F-W2 验收报告 v1.0

> **对应计划**：`修复核验全链路-开发计划-v1.3.md` · Wave F-W2  
> **对应 PRD**：`修复核验全链路-vul-pass-PRD.md` v1.4.2 · §7.5  
> **原型**：`修复核验-任务详情工作台-原型.html`  
> **执行日期**：2026-07-16  
> **工程**：`asset-newleak-manage` · 分支 `feature/fix-ledger-log-records`

---

## 1. 验收结论

| 维度 | 结论 | 说明 |
|------|------|------|
| **§7.5 信息架构落地** | **通过（代码）** | 列表行内摘要 + 任务全页四标签 + 子任务卡片/全页 + 结果摘要双 Tab + 去处置 |
| **前端 lint** | **通过** | TaskDrawer 及新增/改动组件无报错 |
| **手工联调 UI** | **待环境** | 需真实工单数据验证展开/全页切换与接口字段 |
| **路由** | **符合约束** | 未新建独立路由，在 `TaskDrawer.vue` 内扩展 |

**Wave F-W2 总评**：**§7.5 Vue 落地完成，自动化静态检查通过**；建议联调环境走一轮对照原型 checklist。

---

## 2. 交付物

### 2.1 新增组件

| 文件 | 职责 |
|------|------|
| `TaskDetails/MainTaskSummary.vue` | 主任务摘要（字段网格 + 核验状态机 + 快捷入口） |
| `TaskDetails/SubTaskCardList.vue` | 纵向子任务卡片 + 操作（含去处置） |
| `TaskDetails/ResultSummaryPanel.vue` | 任务结果 \| 台账日志 双 Tab |
| `TaskDetails/SubTaskWorkbench.vue` | 子任务全页（四 Tab / 结果入口仅两 Tab） |

### 2.2 改造组件

| 文件 | 改动 |
|------|------|
| `TaskDrawer.vue` | `viewMode=list\|workbench`；行点击行内摘要；全页四标签；挂载 ProMethodDrawer 子任务处置 |
| `TaskInfoDrawer.vue` | `embedded`：嵌入工作台时用 div 壳 |
| `SearchTask.vue` | 同上 `embedded` |
| `ProMethodDrawer.vue` | Wave B 已默认 reportType=32（本 Wave 复用） |

---

## 3. §7.5 对照

| 规格项 | 实现 |
|--------|------|
| 点击主任务行 → 行内嵌入摘要 | `expandedRowRender` + `MainTaskSummary` + `customRow`/`expandedRowKeys` |
| 操作列详情/结果/台账 → 任务全页 | `openWorkbench` 切对应 Tab |
| 四标签：概览/子任务/下发详情/结果摘要 | `workbenchTab` |
| 子任务纵向卡片 + 去处置 | `SubTaskCardList`；`tskStat=1`/跳过不展示去处置 |
| 子任务全页无右栏 | `SubTaskWorkbench` |
| 结果/台账入口仅两 Tab | `resultOnly=true` |
| 去处置 → ProMethodDrawer `taskType=subTask` | TaskDrawer 直挂 |

---

## 4. 验证命令

```bash
cd project_frontend/asset/asset-newleak-manage
npm run lint:nofix -- --no-error-on-unmatched-pattern \
  src/views/VulnManagePlat/components/TaskDetails/TaskDrawer.vue \
  src/views/VulnManagePlat/components/TaskDetails/MainTaskSummary.vue \
  src/views/VulnManagePlat/components/TaskDetails/SubTaskCardList.vue \
  src/views/VulnManagePlat/components/TaskDetails/ResultSummaryPanel.vue \
  src/views/VulnManagePlat/components/TaskDetails/SubTaskWorkbench.vue \
  src/views/VulnManagePlat/components/TaskDetails/TaskInfoDrawer.vue \
  src/views/VulnManagePlat/components/TaskDetails/SearchTask/SearchTask.vue
# DONE  No lint errors found!
```

---

## 5. 待联调 / 已知限制

| 项 | 说明 |
|----|------|
| 子任务 `wave`/`strategyClass`/`dependGateId` | 后端有 `wave`/`verifySrcMethod`；缺省字段卡片静默不展示 |
| 概览审计时间线 | 调 `getLogInfoPage` 取前 10 条；字段名随接口适配 |
| 下发详情「系统漏洞范围」 | 嵌入 TaskInfoDrawer 全量四内页，略重于原型「节选」 |
| pageMode 二级路由 | 工作台内优先内嵌；旧 `emitPageNavigate` 兜底仍保留 |
| §18.5 `prc_vul_num` 文案 | 卡片已展示 `prcVulNum`，口径待产品确认 |

---

## 6. 工作台 UI 定稿（改造事项摘要）

F-W2 界面以 **PRD §7.5.7** 为唯一定稿依据，摘要如下（完整表见 PRD）：

| 改造面 | 定稿要点 |
|--------|----------|
| 主任务列表 | 去掉「处置方式 / 工单业务阶段」列；行点摘要、操作进全页 |
| 主任务摘要 | Tag 全文 + 悬浮「属性：值」；指标密排；confirmToken 同行且尽量少折行 |
| 数值样式 | 短值蓝字常规字重；token/hash 深灰 `#595959` 常规字重；无浅蓝底框 |
| 核验状态机 | 1060/1061 展示；完成步不闪、当前/未完成可闪 |
| 下发详情 | 仅范围明细，不与摘要重复 KV |
| 子任务卡片 | ID 边框盒；处置方式 + 核验手段分色；**不展示阶段**；engHash 同行 |
| 进度 | 0/1 → 未执行/已完成 |

实现文件：`TaskDrawer.vue`、`MainTaskSummary.vue`、`SubTaskCardList.vue` 等。改版请跑 §7.5.7 §7 自检 + lint。

---

## 7. 签核

| 角色 | 结论 | 日期 |
|------|------|------|
| F-W2 代码落地 | **通过** | 2026-07-16 |
| lint | **通过** | 2026-07-16 |
| 工作台 UI 定稿（§6 / PRD §7.5.7） | **已入库** | 2026-07-16 |
| 端到端联调 | **待环境** | — |
