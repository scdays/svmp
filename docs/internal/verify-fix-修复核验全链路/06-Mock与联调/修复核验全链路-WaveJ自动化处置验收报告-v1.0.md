# 修复核验全链路 — Wave J 主任务自动化处置验收报告

> 版本：v1.0 · 日期：2026-07-16 · 对应 PRD v1.4.9 §7.6 / US-09

## 交付摘要

| Wave | 内容 | 状态 |
|------|------|------|
| J-0 | PRD §7.6 / US-09 / API 清单 / 修订记录 v1.4.9 | 完成 |
| J-1 | `VerifyFixAutoDisposeOrchestrator` + UI API + 单测 | 完成 |
| J-2 | 主任务「自动化处置」+ 在线一键 + 进度轮询 | 完成 |
| J-3 | 离线有序批量导入（槽位锁定） | 完成 |
| J-4 | `wave`/`depend_gate_id` 落库；spawn 存活 IP 过滤 | 完成 |

## 后端接口

| 方法 | 路径 |
|------|------|
| POST | `/vul-pass/vul-scan-task/auto-dispose/preview` |
| POST | `/vul-pass/vul-scan-task/auto-dispose` |
| GET | `/vul-pass/vul-scan-task/auto-dispose/{runId}` |
| POST | `/vul-pass/vul-scan-task/auto-dispose/{runId}/pause` |
| POST | `/vul-pass/vul-scan-task/auto-dispose/{runId}/resume` |
| POST | `/vul-pass/vul-scan-task/auto-dispose/{runId}/notify` |

## 单测

- `VerifyFixAutoDisposeOrchestratorTest`：wave 解析、processOrder、needsUpload、mode — **通过**

## 手工验收建议

1. 仅连通性工单：打开自动化处置 → 离线上传连通性报告 → 完成且无空跑修复核验。
2. 1050 + sequential：连通性完成后出现修复核验槽位；在线模式对 `upload=0` 类型可一键。
3. 子任务卡片展示 `dependGateId`；分页返回 `wave`。
4. 暂停/继续与单条「去处置」可并存兜底。

## 说明

- 进程内 run 状态（重启丢失）；生产可再落表增强。
- 连通性默认 reportType=34 需上传，前端会自动切到 `offline-batch`。
