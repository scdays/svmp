#!/usr/bin/env py -3
"""
从任务拆分矩阵 YAML 生成 multi-agent-执行Prompts.md

用法:
  py -3 svmp/docs/internal/scripts/generate-multi-agent-prompts.py
  py -3 svmp/docs/internal/scripts/generate-multi-agent-prompts.py features/open-platform-admin-p0.yaml
  py -3 svmp/docs/internal/scripts/generate-multi-agent-prompts.py features/*.yaml --out multi-agent-执行Prompts.md
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("需要 PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

INTERNAL = Path(__file__).resolve().parent.parent
DEFAULT_YAML = INTERNAL / "features" / "open-platform-admin-p0.yaml"
DEFAULT_OUT = INTERNAL / "multi-agent-执行Prompts.md"


def bullet(items: list[str] | None, prefix: str = "- ") -> str:
    if not items:
        return "_（无）_\n"
    return "\n".join(f"{prefix}{x}" for x in items) + "\n"


def render_agent(agent: dict) -> str:
    aid = agent.get("id", "?")
    name = agent.get("name", "Agent")
    lines = [
        f"## Prompt {aid} — {name}",
        "",
    ]
    if agent.get("owner"):
        lines.append(f"**负责人**：{agent['owner']}  ")
    if agent.get("phase_note"):
        lines.append(f"**阶段说明**：{agent['phase_note']}  ")
    lines.append("")

    meta = []
    if agent.get("repos"):
        meta.append("**工程**：" + "、".join(f"`{r}`" for r in agent["repos"]))
    if meta:
        lines.extend(meta)
        lines.append("")

    if agent.get("allow_paths"):
        lines.append("**可改路径**")
        lines.append("")
        lines.append(bullet(agent["allow_paths"]))
    if agent.get("deny_paths"):
        lines.append("**禁止路径**")
        lines.append("")
        lines.append(bullet(agent["deny_paths"]))
    if agent.get("reads"):
        lines.append("**必读**")
        lines.append("")
        lines.append(bullet(agent["reads"]))
    if agent.get("delivers"):
        lines.append("**必须交付**")
        lines.append("")
        lines.append(bullet(agent["delivers"]))
    if agent.get("verify"):
        lines.append("**验证**")
        lines.append("")
        lines.append(bullet(agent["verify"]))
    if agent.get("depends_on"):
        deps = ", ".join(f"Prompt {d}" for d in agent["depends_on"])
        lines.append(f"**依赖**：{deps}  ")
        lines.append("")

    lines.append("### 执行 Prompt（复制到 Cursor Agent）")
    lines.append("")
    lines.append("```markdown")
    lines.append(agent.get("prompt", "（请在 YAML 中填写 prompt 字段）").rstrip())
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def render_doc(data: dict, source) -> str:
    feat = data.get("feature", {})
    fid = feat.get("id", "UNKNOWN")
    fname = feat.get("name", "")
    phase = feat.get("phase", "")
    source_posix = source.as_posix() if hasattr(source, "as_posix") else str(source)

    parts = [
        "# Multi-Agent 执行 Prompts",
        "",
        f"> **自动生成**：`{date.today().isoformat()}` · 源文件 [`{source_posix}`](./{source_posix})  ",
        f"> **功能**：{fname}（`{fid}` / {phase}）  ",
        "> **工作流**：[prd-to-multi-agent-工作流](./prd-to-multi-agent-工作流.md)  ",
        "> **勿手工改本文件核心 Prompt 段落** — 改 YAML 后重新运行 generate-multi-agent-prompts.py",
        "",
        "---",
        "",
        "## 0. 功能概览",
        "",
        f"| 项 | 值 |",
        f"|----|-----|",
        f"| 功能 ID | `{fid}` |",
        f"| 名称 | {fname} |",
        f"| 阶段 | {phase} |",
    ]
    if feat.get("landing_plan"):
        parts.append(f"| 落地方案 | `{feat['landing_plan']}` |")
    if feat.get("page_design"):
        parts.append(f"| 页面设计 | `{feat['page_design']}` |")
    if feat.get("prd"):
        parts.append(f"| PRD | `{feat['prd']}` |")
    parts.extend(["", "---", ""])

    if data.get("shared_reads"):
        parts.append("## 1. 全局必读")
        parts.append("")
        parts.append(bullet(data["shared_reads"]))
        parts.append("---")
        parts.append("")

    if data.get("acceptance"):
        parts.append("## 2. 交付门禁（Integration 核对）")
        parts.append("")
        parts.append(bullet(data["acceptance"]))
        parts.append("---")
        parts.append("")

    parts.append("## 3. Agent 索引")
    parts.append("")
    parts.append("| Prompt | Agent | 依赖 |")
    parts.append("|--------|-------|------|")
    for agent in data.get("agents", []):
        deps = ", ".join(agent.get("depends_on") or []) or "—"
        parts.append(f"| **{agent.get('id')}** | {agent.get('name')} | {deps} |")
    parts.extend(["", "---", ""])

    parts.append("## 4. 各 Agent Prompt")
    parts.append("")
    for agent in data.get("agents", []):
        parts.append(render_agent(agent))
        parts.append("---")
        parts.append("")

    parts.append("## 5. 并行执行建议")
    parts.append("")
    parts.append("```text")
    parts.append("Wave 1（可并行）: H, D, F")
    parts.append("Wave 2（可并行）: I（依赖 H）, E（依赖 F）")
    parts.append("Wave 3: G（依赖 I + D + F + E）")
    parts.append("Wave 4（P1）: J（依赖 G）")
    parts.append("```")
    parts.append("")

    return "\n".join(parts)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate multi-agent prompts from YAML")
    parser.add_argument(
        "yaml",
        nargs="?",
        default=str(DEFAULT_YAML),
        help="Task matrix YAML path",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output markdown path",
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml)
    if not yaml_path.is_absolute():
        candidate = INTERNAL / yaml_path
        if candidate.exists():
            yaml_path = candidate
        elif (INTERNAL / "features" / yaml_path.name).exists():
            yaml_path = INTERNAL / "features" / yaml_path.name
        else:
            raise SystemExit(f"YAML not found: {args.yaml}")
    if not yaml_path.exists():
        raise SystemExit(f"YAML not found: {yaml_path}")

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = INTERNAL / args.out

    data = load_yaml(yaml_path)
    try:
        rel_source = yaml_path.relative_to(INTERNAL)
    except ValueError:
        rel_source = yaml_path.name
    doc = render_doc(data, rel_source)
    out_path.write_text(doc, encoding="utf-8")
    print(f"Wrote {out_path} ({len(data.get('agents', []))} agents)")


if __name__ == "__main__":
    main()
