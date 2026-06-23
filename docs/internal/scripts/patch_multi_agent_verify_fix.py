# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "multi-agent-执行Prompts-SOC-LINK.md"
text = p.read_bytes().decode("utf-8", errors="replace")

start = text.find("3. verify-fix")
end = text.find("### open-api", start)
if start < 0 or end < 0:
    raise SystemExit("block not found")

new_block = """3. verify-fix 异步复扫（§5.5 全链路）
   - Partner 发起；同步返回 verifyFixJobId，受理期间保持 stat=5
   - 按 vulInfoID 加载 vul_archive_inst，从系统漏洞库取影响资产 IP -> targets
   - 查询实例最近一次扫描 sub.scanner_vendor（单厂商，非 SOC_DUAL）
   - 调 task-center 下发**全量扫描**（不支持指定产品漏洞 ID）
   - Kafka 回收全量结果；**仅匹配** verify-fix 目标 vulInfoID 判定：
     未再检出->6（核验修复），仍检出->7（核验未修复），失败/超时->10
   - notify open-api -> INSTANCE_VERIFY_FIX_COMPLETED + EXPORT_READY(VERIFY_FIX_SCAN)

"""

text = text[:start] + new_block + text[end:]

text = text.replace(
    "- verify-fix: 前置 5 → 6/7/10",
    "- verify-fix: 前置 5 -> 解析资产 IP + 最近 scanner_vendor -> 全量复扫 -> 过滤判定 -> 6/7/10",
)

old_accept = "- [ ] verify-fix 异步复扫完成"
new_accept = """- [ ] verify-fix：资产 IP 与 scanner_vendor 解析正确
- [ ] verify-fix：task-center 全量复扫（非双扫、非指定产品漏洞）
- [ ] verify-fix：仅目标 vulInfoID 参与 6/7/10 判定
- [ ] verify-fix：VERIFY_FIX_SCAN 外发 + INSTANCE_VERIFY_FIX_COMPLETED"""

if old_accept in text:
    text = text.replace(old_accept, new_accept)
elif "VERIFY_FIX_SCAN" not in text:
    text = text.replace(
        "- [ ] 幂等键生效",
        new_accept + "\n- [ ] 幂等键生效",
        1,
    )

p.write_text(text, encoding="utf-8")
print("patched", p.name)
