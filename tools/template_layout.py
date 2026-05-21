"""仓库 templates/ 目录布局（与 tools 输出路径一致）。"""
from __future__ import annotations

from pathlib import Path

TEMPLATE_ROOT = Path("templates")


def paths(root: Path | None = None) -> dict[str, Path]:
    root = root or TEMPLATE_ROOT
    return {
        "root": root,
        "catalogs": root / "catalogs",
        "yaml": root / "yaml",
        "engine": root / "engine",
        "samples": root / "samples",
        "reference": root / "reference",
        "schemas": root / "schemas",
    }


def default_catalog_path() -> Path:
    return paths()["catalogs"] / "field-catalog.json"


def ensure_dirs(root: Path | None = None) -> dict[str, Path]:
    p = paths(root)
    for key in ("catalogs", "yaml", "engine", "samples", "reference", "schemas"):
        p[key].mkdir(parents=True, exist_ok=True)
    return p
