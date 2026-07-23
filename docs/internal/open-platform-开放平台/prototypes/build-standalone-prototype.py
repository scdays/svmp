#!/usr/bin/env py -3
"""
Build ONE file: open-platform-admin-prototype.html

- 接口规范：内嵌 docs/external/开放平台API接口规范-V1.0.1.html
- Swagger UI：由 open-platform-swagger-ui.template.html + vendor + openapi.yaml 生成，
  写入 open-platform-swagger-ui.html 后整体嵌入管理原型（iframe srcdoc）
"""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROTOTYPES = Path(__file__).resolve().parent
ADMIN_TEMPLATE = PROTOTYPES / "open-platform-admin-prototype.template.html"
SWAGGER_TEMPLATE = PROTOTYPES / "open-platform-swagger-ui.template.html"
OUTPUT = PROTOTYPES / "open-platform-admin-prototype.html"
SWAGGER_OUTPUT = PROTOTYPES / "open-platform-swagger-ui.html"
VENDOR = PROTOTYPES / "vendor"
SPEC_HTML = ROOT / "docs" / "external" / "开放平台API接口规范-V1.0.1.html"
OPENAPI_YAML = ROOT / "openapi" / "v1" / "openapi.yaml"

EMBED_BEGIN = "<!-- embedded-docs:BEGIN -->"
EMBED_END = "<!-- embedded-docs:END -->"

SWAGGER_VERSION = "5.11.0"
JSYAML_VERSION = "4.1.0"
VENDOR_FILES = {
    "swagger-ui.css": f"https://unpkg.com/swagger-ui-dist@{SWAGGER_VERSION}/swagger-ui.css",
    "swagger-ui-bundle.js": f"https://unpkg.com/swagger-ui-dist@{SWAGGER_VERSION}/swagger-ui-bundle.js",
    "swagger-ui-standalone-preset.js": f"https://unpkg.com/swagger-ui-dist@{SWAGGER_VERSION}/swagger-ui-standalone-preset.js",
    "js-yaml.min.js": f"https://cdn.jsdelivr.net/npm/js-yaml@{JSYAML_VERSION}/dist/js-yaml.min.js",
}


def strip_embeds(text: str) -> str:
    while EMBED_BEGIN in text:
        start = text.index(EMBED_BEGIN)
        end = text.index(EMBED_END, start) + len(EMBED_END)
        text = text[:start] + text[end:]
    return text


def strip_cdn(text: str) -> str:
    text = re.sub(
        r'\s*<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist[^"]*" />\s*',
        "\n",
        text,
    )
    text = re.sub(
        r'<script src="https://[^"]+js-yaml[^"]+"></script>\s*',
        "",
        text,
    )
    text = re.sub(
        r'<script src="https://unpkg.com/swagger-ui-dist[^"]+"></script>\s*',
        "",
        text,
    )
    return text


def escape_script_js(js: str) -> str:
    return js.replace("</script>", "<\\/script>")


def escape_cdata(content: str) -> str:
    return content.replace("]]>", "]]]]><![CDATA[>")


def ensure_vendor() -> None:
    VENDOR.mkdir(exist_ok=True)
    for name, url in VENDOR_FILES.items():
        path = VENDOR / name
        if path.exists() and path.stat().st_size > 0:
            continue
        print(f"Downloading {name} ...")
        urllib.request.urlretrieve(url, path)


def build_swagger_html(yaml: str) -> str:
    """Render open-platform-swagger-ui.html from template + offline vendor assets."""
    tpl = SWAGGER_TEMPLATE.read_text(encoding="utf-8")
    css = (VENDOR / "swagger-ui.css").read_text(encoding="utf-8")
    jsyaml = (VENDOR / "js-yaml.min.js").read_text(encoding="utf-8")
    bundle = (VENDOR / "swagger-ui-bundle.js").read_text(encoding="utf-8")
    preset = (VENDOR / "swagger-ui-standalone-preset.js").read_text(encoding="utf-8")

    html = tpl.replace("<!-- INLINE_SWAGGER_CSS -->", f"<style>{css}</style>")
    html = html.replace(
        "<!-- INLINE_JSYAML -->",
        f"<script>{escape_script_js(jsyaml)}</script>",
    )
    html = html.replace(
        "<!-- INLINE_SWAGGER_BUNDLE -->",
        f"<script>{escape_script_js(bundle)}</script>",
    )
    html = html.replace(
        "<!-- INLINE_SWAGGER_PRESET -->",
        f"<script>{escape_script_js(preset)}</script>",
    )
    html = html.replace("<!-- INLINE_OPENAPI_YAML -->", escape_cdata(yaml))
    return html


def build_embed_block(spec: str, swagger_html: str, yaml: str) -> str:
    return (
        f"{EMBED_BEGIN}\n"
        f'<script type="text/html" id="embed-spec-doc"><![CDATA[\n{escape_cdata(spec)}\n]]></script>\n'
        f'<script type="text/html" id="embed-swagger-doc"><![CDATA[\n{escape_cdata(swagger_html)}\n]]></script>\n'
        f'<script type="text/plain" id="embed-openapi-yaml"><![CDATA[\n{escape_cdata(yaml)}\n]]></script>\n'
        f"{EMBED_END}\n"
    )


def main() -> None:
    if not ADMIN_TEMPLATE.exists():
        raise SystemExit(f"Missing {ADMIN_TEMPLATE}")
    if not SWAGGER_TEMPLATE.exists():
        raise SystemExit(f"Missing {SWAGGER_TEMPLATE}")

    ensure_vendor()

    yaml = OPENAPI_YAML.read_text(encoding="utf-8")
    spec = SPEC_HTML.read_text(encoding="utf-8")
    swagger_html = build_swagger_html(yaml)

    # Intermediate: same content as embedded in admin tab (for diff / standalone preview)
    SWAGGER_OUTPUT.write_text(swagger_html, encoding="utf-8")
    print(f"Wrote {SWAGGER_OUTPUT.name} ({SWAGGER_OUTPUT.stat().st_size / 1024:.0f} KB)")

    text = strip_embeds(strip_cdn(ADMIN_TEMPLATE.read_text(encoding="utf-8")))
    embed = build_embed_block(spec, swagger_html, yaml)
    anchor = "<script>\n  function showView"
    if anchor not in text:
        raise SystemExit("main script anchor not found")
    text = text.replace(anchor, embed + anchor, 1)

    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUTPUT.name} ({OUTPUT.stat().st_size / (1024 * 1024):.2f} MB) — 最终只需打开此文件")


if __name__ == "__main__":
    main()
