# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(r"d:\application\solo\3.0\svmp\docs\internal")
OUT = ROOT / "vuln-task-center-\u626b\u63cf\u6cbb\u7406\u4e2d\u5fc3-PRD.md"
SECTION_43 = ROOT / "_ah_section_43.md"

section_43 = SECTION_43.read_text(encoding="utf-8")
section_43 = section_43.replace(
    "活跃任务源 \task/list/V2", "活跃任务源 `GET /api/normal/task/list/V2`"
).replace(
    "task.resume | POST /api/normal/task/suspend | 文档与 suspend 同路径，联调确认",
    "task.resume | POST /api/normal/task/start | 暂停后恢复（手册无独立 resume，与 start 联调确认）",
)

exec(open(ROOT / "_prd_body.py", encoding="utf-8").read())
