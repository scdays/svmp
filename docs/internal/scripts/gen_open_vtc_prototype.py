# -*- coding: utf-8 -*-
from pathlib import Path

def t(*codes):
    return "".join(chr(c) for c in codes)

def u(s):
    return s.encode("utf-8").decode("unicode_escape") if "\\u" in s else s

PARTS = []

def add(*chunks):
    for c in chunks:
        PARTS.append(c)

# Build HTML in chunks (ASCII + unicode_escape strings)
add(
    "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n",
    "  <meta charset=\"UTF-8\" />\n",
    "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n",
    "  <title>OPEN \u7f16\u6392\u4efb\u52a1 \u00b7 SOC \u53cc\u626b\u5168\u94fe\u8def\u539f\u578b v1</title>\n",
    "  <style>",
    ":root{--primary:#1890ff;--success:#52c41a;--warning:#faad14;--error:#ff4d4f;--text:rgba(0,0,0,.85);--text-secondary:rgba(0,0,0,.45);--border:#d9d9d9;--bg:#f0f2f5;--card:#fff;--sidebar:#001529}",
    "*{box-sizing:border-box;margin:0;padding:0}",
    "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;font-size:14px;color:var(--text);background:var(--bg)}",
    ".app-shell{display:flex;min-height:100vh}.sidebar{width:248px;background:var(--sidebar);color:#fff}",
    ".sidebar-logo{height:64px;display:flex;align-items:center;padding:0 20px;font-weight:600;font-size:14px;border-bottom:1px solid rgba(255,255,255,.1);line-height:1.4}",
    ".menu-group{padding:12px 0 4px}.menu-group-title{padding:4px 20px;font-size:11px;color:rgba(255,255,255,.35)}",
    ".menu-item{padding:8px 20px 8px 36px;color:rgba(255,255,255,.65);cursor:pointer;font-size:13px;display:flex;justify-content:space-between}",
    ".menu-item:hover{color:#fff;background:rgba(255,255,255,.05)}.menu-item.active{background:var(--primary);color:#fff}",
    ".main-area{flex:1;display:flex;flex-direction:column}.topbar{height:48px;background:var(--card);border-bottom:1px solid #f0f0f0;display:flex;align-items:center;padding:0 20px}",
    ".content{padding:16px;flex:1;overflow:auto}.view{display:none}.view.active{display:block}",
    ".wave{font-size:10px;padding:1px 6px;border-radius:2px;border:1px solid}.w0{background:#e6f7ff;color:#0958d9;border-color:#91d5ff}.w1{background:#f6ffed;color:#389e0d;border-color:#b7eb8f}",
    ".alert{padding:10px 15px;border-radius:2px;margin-bottom:16px;font-size:13px;line-height:1.6}.alert-info{background:#e6f7ff;border:1px solid #91d5ff;color:#0958d9}.alert-warn{background:#fffbe6;border:1px solid #ffe58f;color:#ad6800}",
    ".card{background:var(--card);border-radius:2px;margin-bottom:16px;box-shadow:0 1px 2px rgba(0,0,0,.03)}.card-title{padding:14px 20px;border-bottom:1px solid #f0f0f0;font-weight:500}",
    ".card-body{padding:16px 20px}.tag{display:inline-block;padding:0 7px;font-size:12px;border-radius:2px;line-height:20px;border:1px solid}",
    ".tag-green{background:#f6ffed;border-color:#b7eb8f;color:#389e0d}.tag-blue{background:#e6f7ff;border-color:#91d5ff;color:#0958d9}",
    ".tag-orange{background:#fff7e6;border-color:#ffd591;color:#d46b08}.tag-purple{background:#f9f0ff;border-color:#d3adf7;color:#531dab}.tag-red{background:#fff2f0;border-color:#ffccc7;color:#cf1322}",
    ".stat-row{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px}.stat-card{background:#fafafa;border:1px solid #f0f0f0;padding:14px;cursor:pointer}",
    ".stat-card .label{color:var(--text-secondary);font-size:12px}.stat-card .value{font-size:22px;font-weight:500;margin-top:4px}",
    ".tabs{display:flex;border-bottom:1px solid #f0f0f0;background:var(--card)}.tab{padding:12px 18px;cursor:pointer;border-bottom:2px solid transparent}.tab.active{color:var(--primary);border-bottom-color:var(--primary)}",
    ".tab-panel{display:none;padding:20px;background:var(--card)}.tab-panel.active{display:block}",
    ".workspace-header{padding:16px 20px;background:var(--card);box-shadow:0 1px 2px rgba(0,0,0,.03)}.workspace-title{font-size:18px;font-weight:500}",
    ".workspace-meta{color:var(--text-secondary);font-size:13px;margin-top:6px;line-height:1.7}",
    ".dual-scan{display:grid;grid-template-columns:1fr 1fr;gap:16px}.scan-node{border:1px solid #f0f0f0;padding:16px}",
    ".merge-visual{display:flex;align-items:center;justify-content:center;gap:12px;padding:20px;flex-wrap:wrap}.merge-box{border:2px solid #91d5ff;background:#e6f7ff;padding:16px 24px;text-align:center;min-width:120px}",
    ".timeline{border-left:2px solid #e8e8e8;padding-left:20px;margin-left:8px}.timeline-item{margin-bottom:14px;position:relative;padding-left:4px}",
    ".timeline-item::before{content:'';width:10px;height:10px;background:var(--primary);border-radius:50%;position:absolute;left:-26px;top:4px}.timeline-item.done::before{background:var(--success)}",
    ".flow-diagram{background:#fafafa;border:1px dashed var(--border);padding:20px;font-family:Consolas,monospace;font-size:12px;white-space:pre}",
    "table{width:100%;border-collapse:collapse}th,td{padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:left}th{background:#fafafa}",
    ".breadcrumb{margin-bottom:16px;color:var(--text-secondary)}.breadcrumb a{color:var(--primary);cursor:pointer}",
    ".btn-link{border:none;background:none;color:var(--primary);cursor:pointer}.page-note{text-align:center;padding:16px;color:var(--text-secondary);font-size:12px}",
    ".api-path{font-family:Consolas,monospace;font-size:12px;color:#531dab}.kv-row{display:flex;margin-bottom:8px;font-size:13px}.kv-row .k{width:120px;color:var(--text-secondary)}",
    "  </style>\n</head>\n<body>\n<div class=\"app-shell\">\n",
    "  <aside class=\"sidebar\"><div class=\"sidebar-logo\">\u6f0f\u6d1e\u7ba1\u7406\u5e73\u53f0<br><small style=\"font-weight:400;opacity:.7\">OPEN \u7f16\u6392 \u00b7 SOC \u53cc\u626b</small></div>\n",
    "    <div class=\"menu-group\"><div class=\"menu-group-title\">\u8fd0\u8425\u5de5\u4f5c\u53f0</div>\n",
    "      <div class=\"menu-item active\" data-view=\"dashboard\">\u5de5\u4f5c\u53f0 <span class=\"wave w0\">W0</span></div>\n",
    "      <div class=\"menu-item\" data-view=\"task-list\">OPEN \u7f16\u6392\u4efb\u52a1 <span class=\"wave w1\">W1</span></div>\n",
    "      <div class=\"menu-item\" data-view=\"task-workspace\">\u4efb\u52a1\u5b9e\u4f8b\u5de5\u4f5c\u53f0 <span class=\"wave w1\">W1</span></div></div>\n",
    "    <div class=\"menu-group\"><div class=\"menu-group-title\">\u5f00\u653e\u5e73\u53f0</div>\n",
    "      <div class=\"menu-item\" data-view=\"partner-policy\">Partner \u626b\u63cf\u7b56\u7565</div>\n",
    "      <div class=\"menu-item\" data-view=\"webhook-log\">Webhook \u6295\u9012\u65e5\u5fd7</div></div>\n",
    "    <div class=\"menu-group\"><div class=\"menu-group-title\">\u626b\u63cf\u6cbb\u7406</div>\n",
    "      <div class=\"menu-item\" data-view=\"vtc-link\">task-center \u5b50\u4efb\u52a1</div></div>\n",
    "    <div class=\"menu-group\"><div class=\"menu-group-title\">\u53c2\u8003</div>\n",
    "      <div class=\"menu-item\" data-view=\"architecture\">\u5168\u94fe\u8def\u67b6\u6784</div>\n",
    "      <div class=\"menu-item\" data-view=\"api-map\">Internal API \u6620\u5c04</div></div>\n",
    "  </aside>\n  <div class=\"main-area\"><header class=\"topbar\"><div>OPEN \u7f16\u6392\u4efb\u52a1\u539f\u578b <span class=\"wave w0\">Wave 0</span></div></header>\n",
    "    <main class=\"content\">\n",
    "      <section id=\"view-dashboard\" class=\"view active\">\n",
    "        <div class=\"alert alert-info\"><strong>SOC \u63a5\u5165\u7ea6\u675f\uff1a</strong>\u6bcf\u6b21 Partner \u521b\u5efa\u6392\u67e5\u4efb\u52a1\uff0c\u5e73\u53f0\u5c06\u76f8\u540c\u76ee\u6807\u5206\u522b\u4e0b\u53d1\u81f3 <strong>Nessus</strong> \u4e0e <strong>\u7eff\u76df RSAS</strong>\uff0c\u5b8c\u6210\u540e\u5bf9\u7cfb\u7edf\u6f0f\u6d1e\u53d6<strong>\u5e76\u96c6</strong>\u5165\u5e93\uff0c\u518d Webhook \u56de\u8c03 Partner\u3002</div>\n",
    "        <div class=\"stat-row\">\n",
    "          <div class=\"stat-card\" onclick=\"showView('task-list')\"><div class=\"label\">\u4eca\u65e5 OPEN \u4efb\u52a1</div><div class=\"value\">12</div></div>\n",
    "          <div class=\"stat-card\"><div class=\"label\">SOC \u53cc\u626b\u8fdb\u884c\u4e2d</div><div class=\"value\" style=\"color:var(--primary)\">5</div></div>\n",
    "          <div class=\"stat-card\"><div class=\"label\">\u7b49\u5f85\u5e76\u96c6\u5165\u5e93</div><div class=\"value\" style=\"color:var(--warning)\">2</div></div>\n",
    "          <div class=\"stat-card\" onclick=\"showView('webhook-log')\"><div class=\"label\">Webhook \u5f85\u91cd\u8bd5</div><div class=\"value\" style=\"color:var(--error)\">1</div></div>\n",
    "          <div class=\"stat-card\"><div class=\"label\">\u5b50\u4efb\u52a1\u5bf9\u8d26\u5f02\u5e38</div><div class=\"value\">0</div></div></div>\n",
    "        <div class=\"card\"><div class=\"card-title\">\u5f85\u529e\u4e8b\u9879</div><div class=\"card-body\" style=\"padding:0\"><table><thead><tr><th>\u7c7b\u578b</th><th>\u4efb\u52a1</th><th>Partner</th><th>\u72b6\u6001</th></tr></thead><tbody>\n",
    "          <tr><td><span class=\"tag tag-purple\">\u53cc\u626b</span></td><td><a class=\"btn-link\" onclick=\"showView('task-workspace')\">TASK-7f3a2b1c</a></td><td>SOC-CLIENT-A</td><td><span class=\"tag tag-orange\">\u7eff\u76df 100% \u00b7 Nessus 78%</span></td></tr>\n",
    "          <tr><td><span class=\"tag tag-blue\">\u56de\u8c03</span></td><td>TASK-a1b2 Webhook 502</td><td>SOC-CLIENT-A</td><td><span class=\"tag tag-red\">\u91cd\u8bd5 3/5</span></td></tr>\n",
    "        </tbody></table></div></div></section>\n",
    "      <section id=\"view-task-list\" class=\"view\"><div class=\"breadcrumb\"><a onclick=\"showView('dashboard')\">\u5de5\u4f5c\u53f0</a> / OPEN \u7f16\u6392\u4efb\u52a1</div>\n",
    "        <div class=\"card\"><div class=\"card-title\">OPEN \u7f16\u6392\u4efb\u52a1\u5217\u8868</div><div class=\"card-body\"><table><thead><tr><th>taskId</th><th>Partner</th><th>\u4efb\u52a1\u540d</th><th>\u7b56\u7565</th><th>\u8fdb\u5ea6</th><th>\u72b6\u6001</th><th>\u64cd\u4f5c</th></tr></thead><tbody>\n",
    "          <tr><td><code>TASK-7f3a2b1c</code></td><td>SOC-CLIENT-A</td><td>2026Q2-\u6838\u5fc3\u4e1a\u52a1\u6392\u67e5</td><td><span class=\"tag tag-purple\">SOC_DUAL</span></td><td>78%</td><td><span class=\"tag tag-blue\">RUNNING</span></td><td><button class=\"btn-link\" onclick=\"showView('task-workspace')\">\u5de5\u4f5c\u53f0</button></td></tr>\n",
    "        </tbody></table></div></div></section>\n",
    "      <section id=\"view-task-workspace\" class=\"view\">\n",
    "        <div class=\"workspace-header\"><div class=\"workspace-title\">2026Q2-\u6838\u5fc3\u4e1a\u52a1\u6392\u67e5 <span class=\"tag tag-blue\">RUNNING</span> <span class=\"tag tag-purple\">SOC_DUAL</span></div>\n",
    "          <div class=\"workspace-meta\">taskId <code>TASK-7f3a2b1c</code> &middot; passTaskId <code>10086001</code> &middot; Partner <code>SOC-CLIENT-A</code> &middot; \u76ee\u6807 <code>10.10.1.2,10.10.1.3</code></div></div>\n",
    "        <div class=\"tabs\" id=\"workspace-tabs\">\n",
    "          <div class=\"tab active\" data-tab=\"overview\">\u6982\u89c8</div><div class=\"tab\" data-tab=\"subtasks\">\u5b50\u4efb\u52a1\uff08\u53cc\u626b\uff09</div><div class=\"tab\" data-tab=\"merge\">\u7ed3\u679c\u5e76\u96c6</div>\n",
    "          <div class=\"tab\" data-tab=\"lifecycle\">\u6f0f\u6d1e\u751f\u547d\u5468\u671f</div><div class=\"tab\" data-tab=\"report\">\u62a5\u544a\u4ea7\u7269</div><div class=\"tab\" data-tab=\"callback\">Partner \u56de\u8c03</div></div>\n",
    "        <div id=\"tab-overview\" class=\"tab-panel active\"><div class=\"alert alert-warn\">\u7236\u4efb\u52a1 FINISHED \u6761\u4ef6\uff1aNessus \u4e0e\u7eff\u76df\u5b50\u4efb\u52a1\u5747\u5b8c\u6210\u3002</div>\n",
    "          <div class=\"timeline\"><div class=\"timeline-item done\">POST /api/open/v1/tasks/vul</div><div class=\"timeline-item done\">vul-pass \u521b\u5efa SOC_DUAL \u7f16\u6392</div>\n",
    "          <div class=\"timeline-item done\">task-center \u4e0b\u53d1 2 \u4e2a survey</div><div class=\"timeline-item\">\u7eff\u76df FINISHED \u00b7 Nessus RUNNING</div>\n",
    "          <div class=\"timeline-item\" style=\"opacity:.5\">\u5e76\u96c6 \u2192 oper \u8f68 \u2192 Webhook</div></div></div>\n",
    "        <div id=\"tab-subtasks\" class=\"tab-panel\"><div class=\"dual-scan\">\n",
    "          <div class=\"scan-node\"><h4>NESSUS</h4><div class=\"kv-row\"><span class=\"k\">surveyId</span><span>SV-NES-001</span></div><div class=\"kv-row\"><span class=\"k\">\u8fdb\u5ea6</span><span>78% RUNNING</span></div><div class=\"kv-row\"><span class=\"k\">\u6f0f\u6d1e</span><span>42\uff08\u672a\u5e76\u96c6\uff09</span></div></div>\n",
    "          <div class=\"scan-node\"><h4>\u7eff\u76df LM</h4><div class=\"kv-row\"><span class=\"k\">surveyId</span><span>SV-LM-002</span></div><div class=\"kv-row\"><span class=\"k\">\u8fdb\u5ea6</span><span>100% FINISHED</span></div><div class=\"kv-row\"><span class=\"k\">\u6f0f\u6d1e</span><span>38\uff08\u672a\u5e76\u96c6\uff09</span></div></div></div></div>\n",
    "        <div id=\"tab-merge\" class=\"tab-panel\"><div class=\"merge-visual\"><div class=\"merge-box\">Nessus<br>42</div><div>+</div><div class=\"merge-box\">\u7eff\u76df<br>38</div><div>&rarr;</div><div class=\"merge-box\" style=\"border-color:#b7eb8f;background:#f6ffed\">\u5e76\u96c6<br>51</div></div>\n",
    "          <p style=\"margin-top:12px;color:var(--text-secondary);font-size:13px\">dedupKey = \u8d44\u4ea7 + \u7aef\u53e3 + \u534f\u8bae + \u670d\u52a1 + vulId</p></div>\n",
    "        <div id=\"tab-lifecycle\" class=\"tab-panel\"><div class=\"alert alert-info\">OPEN \u5199\u5165 <code>vul_inst_log_rela_oper</code>\uff0c<code>data_origin=OPEN</code></div><p>\u4efb\u52a1\u672a\u5b8c\u6210\uff0c\u5b9e\u4f8b\u5c1a\u672a\u5165\u5e93\uff08Wave 1b\uff09</p></div>\n",
    "        <div id=\"tab-report\" class=\"tab-panel\"><table><thead><tr><th>\u4ea7\u7269</th><th>\u6765\u6e90</th><th>\u72b6\u6001</th></tr></thead><tbody>\n",
    "          <tr><td>\u7eff\u76df\u539f\u59cb XML</td><td>LM</td><td><span class=\"tag tag-green\">\u53ef\u4e0b\u8f7d</span></td></tr>\n",
    "          <tr><td>Nessus \u62a5\u544a</td><td>NESSUS</td><td><span class=\"tag tag-orange\">\u626b\u63cf\u4e2d</span></td></tr></tbody></table></div>\n",
    "        <div id=\"tab-callback\" class=\"tab-panel\"><div class=\"kv-row\"><span class=\"k\">\u4e8b\u4ef6</span><span>TASK_COMPLETED\uff08\u5f85\u89e6\u53d1\uff09</span></div><div class=\"kv-row\"><span class=\"k\">URL</span><span><code>https://soc.example.com/hooks/vuln</code></span></div></div>\n",
    "      </section>\n",
    "      <section id=\"view-partner-policy\" class=\"view\"><div class=\"card\"><div class=\"card-title\">Partner \u626b\u63cf\u7b56\u7565</div><div class=\"card-body\"><table><thead><tr><th>partnerId</th><th>scanPolicy</th><th>\u5f3a\u5236\u53cc\u626b</th><th>\u8bf4\u660e</th></tr></thead><tbody>\n",
    "        <tr><td>SOC-CLIENT-A</td><td><span class=\"tag tag-purple\">SOC_DUAL</span></td><td>\u662f</td><td>SOC \u63a5\u5165\uff1aNessus + \u7eff\u76df</td></tr></tbody></table></div></div></section>\n",
    "      <section id=\"view-webhook-log\" class=\"view\"><div class=\"card\"><div class=\"card-title\">Webhook \u6295\u9012\u65e5\u5fd7</div><div class=\"card-body\"><table><thead><tr><th>ID</th><th>eventType</th><th>HTTP</th><th>\u91cd\u8bd5</th></tr></thead><tbody>\n",
    "        <tr><td>wh-001</td><td>TASK_COMPLETED</td><td><span class=\"tag tag-red\">502</span></td><td>3</td></tr></tbody></table></div></div></section>\n",
    "      <section id=\"view-vtc-link\" class=\"view\"><div class=\"card\"><div class=\"card-title\">task-center \u5b50\u4efb\u52a1</div><div class=\"card-body\"><table><thead><tr><th>surveyId</th><th>\u5382\u5546</th><th>\u76ee\u6807</th><th>\u72b6\u6001</th></tr></thead><tbody>\n",
    "        <tr><td>SV-NES-001</td><td>Nessus</td><td>10.10.1.2,10.10.1.3</td><td><span class=\"tag tag-blue\">RUNNING</span></td></tr>\n",
    "        <tr><td>SV-LM-002</td><td>\u7eff\u76df</td><td>10.10.1.2,10.10.1.3</td><td><span class=\"tag tag-green\">FINISHED</span></td></tr></tbody></table></div></div></section>\n",
    "      <section id=\"view-architecture\" class=\"view\"><div class=\"card\"><div class=\"card-title\">\u5168\u94fe\u8def\u67b6\u6784</div><div class=\"card-body\"><div class=\"flow-diagram\">Partner (SOC)\n  | POST /api/open/v1/tasks/vul\n  v\nopen-api-service -> POST /internal/open/v1/tasks\n  v\nvul-pass (biz_line=OPEN, scan_policy=SOC_DUAL)\n  | 2 x vul_scan_task_sub\n  v\nvuln-task-center -> Nessus + \u7eff\u76df\n  | \u5e76\u96c6 -> inst + rela_oper\n  v\nopen-api Webhook TASK_COMPLETED</div></div></div></section>\n",
    "      <section id=\"view-api-map\" class=\"view\"><div class=\"card\"><div class=\"card-title\">Internal API \u6620\u5c04</div><div class=\"card-body\"><table><thead><tr><th>Partner API</th><th>vul-pass internal</th><th>task-center</th></tr></thead><tbody>\n",
    "        <tr><td class=\"api-path\">POST /tasks/vul</td><td class=\"api-path\">POST /internal/open/v1/tasks</td><td>first/half + second/half x2</td></tr>\n",
    "        <tr><td class=\"api-path\">GET /tasks/{id}</td><td class=\"api-path\">GET /internal/open/v1/tasks/{id}</td><td>survey/query</td></tr>\n",
    "        <tr><td>Webhook</td><td class=\"api-path\">POST .../notify</td><td>-</td></tr></tbody></table></div></div></section>\n",
    "      <p class=\"page-note\">\u539f\u578b v1 \u00b7 2026-06-16 \u00b7 \u6d4f\u89c8\u5668\u76f4\u63a5\u6253\u5f00 \u00b7 open-api-vtc-pass-\u843d\u5730\u65b9\u6848.md</p>\n",
    "    </main></div></div>\n<script>\nfunction showView(id){document.querySelectorAll('.view').forEach(function(v){v.classList.remove('active');});document.querySelectorAll('.menu-item').forEach(function(m){m.classList.remove('active');});var e=document.getElementById('view-'+id);if(e)e.classList.add('active');var m=document.querySelector('.menu-item[data-view=\"'+id+'\"]');if(m)m.classList.add('active');}\ndocument.querySelectorAll('.menu-item[data-view]').forEach(function(i){i.onclick=function(){showView(i.dataset.view);};});\ndocument.querySelectorAll('#workspace-tabs .tab').forEach(function(tab){tab.onclick=function(){document.querySelectorAll('#workspace-tabs .tab').forEach(function(t){t.classList.remove('active');});document.querySelectorAll('[id^=tab-]').forEach(function(p){p.classList.remove('active');});tab.classList.add('active');var p=document.getElementById('tab-'+tab.dataset.tab);if(p)p.classList.add('active');};});\n</script>\n</body>\n</html>\n",
)

TARGET = Path(__file__).resolve().parent.parent / "prototypes" / "open-api-vtc-pass-prototype-v1.html"

if __name__ == "__main__":
    html = "".join(PARTS)
    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("OK:", TARGET, "bytes", len(html.encode("utf-8")))
