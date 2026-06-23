# -*- coding: utf-8 -*-
"""Patch SOC PRD docs for section 5.5 verify-fix full-chain."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _find_md(*hints: str, exclude: tuple = ()) -> Path:
    for f in ROOT.iterdir():
        if f.suffix != ".md":
            continue
        if any(x in f.name for x in exclude):
            continue
        if all(h in f.name for h in hints):
            return f
    raise FileNotFoundError(hints)


def read_soc_md(name_part: str) -> str:
    if name_part == "SOC对接全链路-PRD":
        f = _find_md("SOC", "PRD.md", exclude=("v2", "代码", "修正"))
    elif "v2修订" in name_part:
        f = _find_md("SOC", "v2", "修订")
    elif "代码分析" in name_part:
        f = _find_md("SOC", "代码分析")
    else:
        f = next(p for p in ROOT.glob("*.md") if name_part in p.name)
    raw = f.read_bytes()
    for enc in ("gbk", "gb18030", "utf-8", "utf-8-sig"):
        try:
            text = raw.decode(enc)
            if "## 九、" in text or "verify-fix" in text or "修订摘要" in text:
                return text
        except UnicodeDecodeError:
            continue
    return raw.decode("gb18030", errors="replace")


def write_soc_md(name_part: str, text: str) -> None:
    if name_part == "SOC对接全链路-PRD":
        f = _find_md("SOC", "PRD.md", exclude=("v2", "代码", "修正"))
    elif "v2修订" in name_part:
        f = _find_md("SOC", "v2", "修订")
    elif "代码分析" in name_part:
        f = _find_md("SOC", "代码分析")
    else:
        f = next(p for p in ROOT.glob("*.md") if name_part in p.name)
    f.write_text(text, encoding="utf-8")
    print("wrote", f.name, len(text))


VERIFY_FIX_SECTION = """
### 8.4 修复核验（verify-fix）编排链路

> 对应开放平台 API **§5.5 漏洞实例 · 修复核验**。由 **Partner 主动发起**；平台异步复扫后判定终态并外发。

#### 8.4.1 业务语义

| 项 | 说明 |
|----|------|
| 触发方 | Partner 调用 `POST /instances/{vulInfoID}/verify-fix` 或批量接口 |
| 前置状态 | `vulInfoStat = 5`（已修复） |
| 受理响应 | 同步返回 `verifyFixStatus=PENDING/RUNNING`、`verifyFixJobId`；**受理期间状态保持 5** |
| 终态 | 6 核验修复 / 7 核验未修复 / 10 核验失败 |
| 与 verify 区分 | verify 确认漏洞真假（前置 0/1）；verify-fix 确认**修复是否生效**（前置 5） |

#### 8.4.2 端到端时序

```text
Partner
  | POST /api/open/v1/instances/{vulInfoID}/verify-fix  (Idempotency-Key)
  v
open-api-service
  | 能力码 INSTANCE_VERIFY_FIX + 幂等 24h
  | Feign -> vul-pass internal verify-fix
  v
vul-pass OpenInstanceAppService
  1. 校验 vulInfoStat=5
  2. 按 vulInfoID 加载 vul_archive_inst（系统漏洞实例档案）
  3. 从实例/系统漏洞库提取影响资产 IP（assetIp）、端口、协议 -> 扫描 targets[]
  4. 查询该实例最近一次扫描 sub：vul_scan_task_sub ORDER BY finish_time DESC
     -> 读取 scanner_vendor（NESSUS / LM / AH ...）
  5. 创建修复核验扫描任务（biz_line=OPEN, tsk_scn=VERIFY_FIX, scan_policy=SINGLE）
  6. 调用 vuln-task-center 下发 **单厂商全量扫描**（不复用 SOC_DUAL 双扫）
  7. 写 verify_fix_job 关联（verifyFixJobId 关联 passTaskId/subId 与 vulInfoID）
  8. 同步返回受理结果给 open-api -> Partner
  v
vuln-task-center
  | 全量主机/系统漏洞扫描（**不支持指定产品漏洞 ID 下发**）
  v
扫描完成 -> Kafka dr_vul_scan_task_status
  v
vul-pass VerifyFixRecycleHandler
  1. handlerReport 解析全量结果
  2. **仅关注** verify-fix 请求中的目标 vulInfoID（及对应 vulId/dedupKey）
  3. 判定：
     - 结果中**未再检出**该漏洞 -> transition -> vulInfoStat=6（核验修复）
     - **仍检出** -> vulInfoStat=7（核验未修复）
     - 引擎失败/超时 -> vulInfoStat=10（核验失败）
  4. appendOperRela + writeVulInstLedger
  5. notify open-api
  v
open-api
  | EXPORT_READY（exportStage=VERIFY_FIX_SCAN）
  | Webhook INSTANCE_VERIFY_FIX_COMPLETED
  v
Partner 轮询外发或接收 Webhook
```

#### 8.4.3 扫描下发约束

| 约束 | 说明 |
|------|------|
| 扫描器选择 | 默认使用该漏洞实例**最近一次排查/扫描**使用的扫描器（`vul_scan_task_sub.scanner_vendor`） |
| 扫描范围 | 对实例影响资产 IP 做**全量扫描**；task-center **不支持**按产品漏洞 ID 定点下发 |
| 结果过滤 | 回收结果为全量；状态判定**仅匹配**本次 verify-fix 的 `vulInfoID`（及 vulId） |
| SOC_DUAL | 修复核验为**单 survey 复扫**，不触发双扫并集合并 |
| procMethod | 建议 `1060`（修复核验自适应扫描）；阶段 `PHASE_VERIFICATION` / `scan_phase=3` |

#### 8.4.4 数据落库

| 表/字段 | 用途 |
|---------|------|
| `vul_scan_task.tsk_scn` | `VERIFY_FIX` 区分排查/验证/修复核验任务 |
| `vul_scan_task.scan_policy` | 固定 `SINGLE` |
| `vul_scan_task_sub.scanner_vendor` | 复扫厂商 |
| `vul_scan_task_sub.scan_phase` | `3` = 修复核验阶段 |
| `open_verify_fix_job`（建议新增） | verifyFixJobId、partnerId、vulInfoID、passTaskId、status |
| `vul_inst_log_rela_oper` | 核验动作写运营轨 |

#### 8.4.5 外发与回调

| 事件 | 时机 | exportStage |
|------|------|-------------|
| `INSTANCE_VERIFY_FIX_COMPLETED` | 复扫完成且状态已更新 | - |
| `EXPORT_READY` | 外发组装完成 | `VERIFY_FIX_SCAN` |

外发须含 `targets[]`、`liveProbeResults[]`、`portScanResults[]`、`vulnerabilities[]`（§5.6.3）。

#### 8.4.6 验收要点（W3）

- [ ] Partner 对 stat=5 实例发起 verify-fix，同步收到 `verifyFixStatus=RUNNING`
- [ ] vul-pass 从系统漏洞库正确解析影响资产 IP
- [ ] 复扫使用最近一次 `scanner_vendor`，且为单 survey 全量扫描
- [ ] 全量结果回收后，仅目标 vulInfoID 参与 6/7/10 判定
- [ ] 完成后收到 `INSTANCE_VERIFY_FIX_COMPLETED` + `EXPORT_READY(VERIFY_FIX_SCAN)`
"""

V2_APPENDIX = """
## 十一、修复核验（verify-fix）编排修订（v2.1）

> **状态**：正式纳入 PRD 正文 §8.4。
> **依据**：`external/网络安全漏洞管理平台 · API 接口文档.md` §5.5、§6.4、§7（VERIFY_FIX_SCAN）

### 11.1 修订摘要

| # | 修订项 | 影响范围 | 优先级 |
|---|--------|----------|--------|
| 7 | 补齐修复核验全链路：Partner 发起 -> 解析 vulInfoID -> 资产 IP -> 最近扫描器 -> task-center 全量复扫 -> 过滤判定 6/7/10 | open-api / vul-pass / vuln-task-center / W3 | P0 |

### 11.2 与 autoVerify 双阶段的关系

- **排查 + 验证**（autoVerify）：仍走双阶段 + 可选 SOC_DUAL 并集。
- **修复核验**：独立异步链路，**单扫描器全量复扫**，不参与 UNION/INTERSECT 合并。

### 11.3 扫描下发要点

1. 从 `vulInfoID` 加载系统漏洞实例，取影响资产 IP 作为 targets。
2. 查询 `vul_scan_task_sub` 最近完成记录取 `scanner_vendor`。
3. task-center 下发**全量扫描**（不支持指定产品漏洞）。
4. 回收时 handler 仅对目标 `vulInfoID` 做存在性判定。

### 11.4 修订记录补充

| 版本 | 日期 | 说明 |
|------|------|------|
| v2.1 | 2026-06-17 | 纳入 §5.5 修复核验编排、外发 VERIFY_FIX_SCAN、W3 验收 |
"""

CODE_ANALYSIS = """
## 九、修复核验（verify-fix）实现要点（v1.2 补充）

### 9.1 当前 open-api 现状

| 模块 | 现状 | W3 目标 |
|------|------|---------|
| InstanceDomainServiceImpl | Mock 本地改 stat + 延迟触发 VERIFY_FIX_SCAN | Feign vul-pass，不再本地改终态 |
| MockInstanceScanFollowUpService | 定时模拟外发 | 由 vul-pass notify 驱动真实回收 |
| ExportAssemblyDomainServiceImpl | 已支持 VERIFY_FIX_SCAN 组装 | 对接 vul-pass 真实扫描结果 |

### 9.2 vul-pass 待建能力

| 组件 | 职责 |
|------|------|
| `VerifyFixOrchestrator` | 解析 vulInfoID -> 资产 IP + scanner_vendor -> 创建 SINGLE 扫描任务 |
| `VerifyFixRecycleHandler` | 全量 recycle，仅匹配目标 vulInfoID 判定 6/7/10 |
| `OpenInstanceUi` verify-fix | internal API，受理返回 verifyFixJobId |

### 9.3 与部侧考核 recycle 复用

- 复用 `handlerReport` / `handlerVulProcess` / `transition` 框架。
- `procMethod=1060`，OPEN 专用 `scan_phase=3`。
- **不**走 `MergeService`（单 survey）。
"""

DUAL_STAGE = """
## 七、修复核验阶段（verify-fix）- OPEN 专用

> 与 §3 双阶段「排查 + 验证」并列，为实例生命周期**第三条扫描链路**。

### 7.1 定位

| 维度 | 排查+验证（autoVerify） | 修复核验（verify-fix） |
|------|-------------------------|----------------------|
| 触发 | 创建任务 / autoVerify 自动衔接 | Partner POST verify-fix |
| 扫描器 | 可双扫（SOC UNION / 部侧 INTERSECT） | **单厂商**（最近一次 scanner_vendor） |
| 扫描类型 | 排查 + 交叉验证 | **全量复扫**（不支持指定产品漏洞） |
| 结果处理 | 并集/交集合并入库 | 全量回收，**仅过滤目标 vulInfoID** 改状态 |
| 状态 | 1 -> 2/3 | 5 -> 6/7/10 |

### 7.2 流程

```text
Partner verify-fix (vulInfoStat=5)
  -> vul-pass 解析 vulInfoID
  -> 系统漏洞库取 assetIp
  -> 最近 sub.scanner_vendor
  -> task-center 全量 survey
  -> recycle 全量结果
  -> 仅目标漏洞：未检出->6，仍检出->7，失败->10
  -> Webhook + VERIFY_FIX_SCAN 外发
```
"""


def patch_prd_main():
    text = read_soc_md("SOC对接全链路-PRD")
    text = text.replace("\r\n", "\n")
    if "### 8.4 修复核验" in text:
        print("PRD main: already has 8.4")
    else:
        marker = "\n---\n\n## 九、"
        pos = text.find(marker)
        if pos < 0:
            raise SystemExit("PRD main: section 9 marker not found")
        text = text[:pos] + "\n" + VERIFY_FIX_SECTION + text[pos:]
    if "US-O06" not in text:
        text = text.replace(
            "| US-O05 | SOC 接入方 | 查询任务进度时看到双扫子任务状态 | 知道哪侧还在跑 | W1 |",
            "| US-O05 | SOC 接入方 | 查询任务进度时看到双扫子任务状态 | 知道哪侧还在跑 | W1 |\n"
            "| US-O06 | SOC 接入方 | 对已修复实例发起修复核验，平台按最近扫描器全量复扫并判定 6/7 | 闭环修复效果确认 | W3 |",
        )
    if "verify-fix 全量复扫误伤" not in text:
        text = text.replace(
            "| verify-fix 复扫扫描器选择错误 | 记录 `scanner_vendor` 于 sub 表，复扫时查询 |",
            "| verify-fix 复扫扫描器选择错误 | 记录 `scanner_vendor` 于 sub 表，复扫时查询 |\n"
            "| verify-fix 全量复扫误伤/耗时 | 单 IP 全量模板 + 结果仅过滤目标 vulInfoID 做状态判定 |",
        )
    if "EXPORT_READY exportStage=VERIFY_FIX_SCAN" not in text:
        text = text.replace(
            "- [ ] 幂等键生效",
            "- [ ] 幂等键生效\n"
            "- [ ] verify-fix：从 vul_archive_inst 解析资产 IP，按最近 scanner_vendor 单 survey 全量下发\n"
            "- [ ] verify-fix：回收全量结果后仅匹配目标 vulInfoID -> 6/7/10\n"
            "- [ ] verify-fix：EXPORT_READY exportStage=VERIFY_FIX_SCAN + INSTANCE_VERIFY_FIX_COMPLETED",
        )
    write_soc_md("SOC对接全链路-PRD", text)


def patch_v2_appendix():
    text = read_soc_md("SOC对接全链路-PRD-v2修订附录")
    if "## 十一、修复核验" not in text:
        text = text.replace(
            "| §5.5 verify-fix 接口 | 不变 |",
            "| §5.5 verify-fix 接口 | **v2.1 补充编排链路**（§8.4 / 附录十一） |",
        )
        if "| v2.1 |" not in text:
            text = text.replace(
                "| v2 | 2026-06-17 |",
                "| v2.1 | 2026-06-17 | 纳入 §5.5 修复核验全链路编排（单厂商全量复扫、结果过滤判定） |\n| v2 | 2026-06-17 |",
            )
        text = text.rstrip() + "\n" + V2_APPENDIX
    write_soc_md("SOC对接全链路-PRD-v2修订附录", text)


def patch_code_analysis():
    text = read_soc_md("SOC对接全链路-PRD-代码分析修正")
    if "## 九、修复核验" not in text:
        text = text.rstrip() + "\n" + CODE_ANALYSIS
    write_soc_md("SOC对接全链路-PRD-代码分析修正", text)


def patch_dual_stage():
    path = ROOT / "双阶段交叉扫描方案-SOC并集与部侧交集统一.md"
    if not path.exists():
        for f in ROOT.iterdir():
            if "双阶段" in f.name and f.suffix == ".md":
                path = f
                break
    text = path.read_text(encoding="gbk")
    if "## 七、修复核验阶段" not in text:
        text = text.rstrip() + "\n" + DUAL_STAGE
    path.write_text(text, encoding="utf-8")
    print("wrote", path.name)


def patch_multi_agent():
    path = ROOT / "multi-agent-执行Prompts-SOC-LINK.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    old = """3. verify-fix 异步复扫
   - 查询实例最近一次扫描器: vul_scan_task_sub.scanner_vendor
   - 调 task-center 下发复扫任务
   - Kafka 消费完成后 transition → 6/7/10"""
    new = """3. verify-fix 异步复扫（§5.5 全链路）
   - Partner 发起；校验前置 stat=5；同步返回 verifyFixJobId，受理期间保持 5
   - 按 vulInfoID 加载 vul_archive_inst，从系统漏洞库取影响资产 IP -> targets
   - 查询实例最近一次扫描 sub.scanner_vendor（单厂商，非 SOC_DUAL）
   - 调 task-center 下发**全量扫描**（不支持指定产品漏洞 ID）
   - Kafka 回收全量结果；**仅匹配** verify-fix 目标 vulInfoID 判定：
     未再检出->6（核验修复），仍检出->7（核验未修复），失败/超时->10
   - notify open-api -> INSTANCE_VERIFY_FIX_COMPLETED + EXPORT_READY(VERIFY_FIX_SCAN)"""
    if old in text:
        text = text.replace(old, new)
    text = text.replace(
        "- [ ] verify-fix 异步复扫完成",
        "- [ ] verify-fix：资产 IP 与 scanner_vendor 解析正确\n"
        "- [ ] verify-fix：task-center 全量复扫（非双扫、非指定产品漏洞）\n"
        "- [ ] verify-fix：仅目标 vulInfoID 参与 6/7/10 判定\n"
        "- [ ] verify-fix：VERIFY_FIX_SCAN 外发 + INSTANCE_VERIFY_FIX_COMPLETED",
    )
    path.write_text(text, encoding="utf-8")
    print("wrote multi-agent prompts")


def patch_task_matrix():
    path = ROOT / "features" / "soc-link-task-matrix.yaml"
    text = path.read_text(encoding="utf-8", errors="replace")
    replacements = [
        (
            "- verify-fix 异步复扫: 调 task-center 下发",
            "- verify-fix: 解析 vulInfoID->资产 IP + 最近 scanner_vendor -> task-center 全量复扫（不支持指定产品漏洞）",
        ),
        (
            "- verify-fix: 5 -> 6/7/10",
            "- verify-fix: 5 -> 全量回收后仅过滤目标 vulInfoID -> 6/7/10",
        ),
    ]
    for a, b in replacements:
        if a in text:
            text = text.replace(a, b)
    path.write_text(text, encoding="utf-8")
    print("wrote task matrix")


if __name__ == "__main__":
    patch_prd_main()
    patch_v2_appendix()
    patch_code_analysis()
    patch_dual_stage()
    patch_multi_agent()
    patch_task_matrix()
    print("done")
