# -*- coding: utf-8 -*-
# ASCII-ONLY source. All CJK via \uXXXX in string literals.
# DEPRECATED: Canonical UI prototype is prototypes/open-api-vtc-pass-prototype-v2.html
# (hand-maintained, dual-phase + verify-fix W3). Do not run this script unless
# intentionally regenerating the old simplified layout.
# Generates: open-api-vtc-pass-prototype-v2.html
from pathlib import Path

OUTDIR = Path(__file__).resolve().parent.parent / "prototypes"
OUTDIR.mkdir(parents=True, exist_ok=True)

CSS = (
    ":root{--p:#1890ff;--s:#52c41a;--w:#faad14;--e:#ff4d4f"
    ";--t:rgba(0,0,0,.85);--ts:rgba(0,0,0,.45);--bg:#f0f2f5;--c:#fff;--sb:#001529}"
    "*{box-sizing:border-box;margin:0;padding:0}"
    "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif"
    ";font-size:14px;color:var(--t);background:var(--bg);line-height:1.6}"
    ".app{display:flex;min-height:100vh}"
    ".side{width:240px;background:var(--sb);color:#fff;flex-shrink:0;position:sticky;top:0;height:100vh;overflow-y:auto}"
    ".logo{padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.1);}"
    ".logo-t{font-size:14px;font-weight:700;}"
    ".logo-s{font-size:10px;opacity:.5;display:block;margin-top:2px}"
    ".ng{padding:12px 0 2px}.nt{padding:2px 16px;font-size:10px;color:rgba(255,255,255,.3);letter-spacing:.5px}"
    ".ni{display:block;padding:7px 16px 7px 28px;color:rgba(255,255,255,.65);font-size:12px;cursor:pointer;text-decoration:none;border-left:3px solid transparent;transition:all .15s}"
    ".ni:hover{color:#fff;background:rgba(255,255,255,.06)}"
    ".ni.active{color:#fff;background:rgba(24,144,255,.15);border-left-color:var(--p)}"
    ".main{flex:1;overflow:auto;min-width:0}"
    ".topbar{height:50px;background:var(--c);border-bottom:1px solid #f0f0f0;display:flex;align-items:center;padding:0 24px;position:sticky;top:0;z-index:99;gap:10px;box-shadow:0 1px 4px rgba(0,0,0,.06)}"
    ".ct{padding:24px;max-width:1200px}"
    ".sec{display:none}.sec.active{display:block}"
    ".card{background:var(--c);border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.06);margin-bottom:20px;border:1px solid #f0f0f0}"
    ".ch{padding:14px 20px;border-bottom:1px solid #f0f0f0;font-weight:600;font-size:13px;display:flex;align-items:center;gap:8px;justify-content:space-between}"
    ".cb{padding:18px 20px}"
    "table{width:100%;border-collapse:collapse}"
    "th,td{padding:9px 12px;border-bottom:1px solid #f0f0f0;vertical-align:middle;font-size:12px}"
    "th{background:#fafafa;font-weight:600;white-space:nowrap;color:var(--ts)}"
    "tr:hover td{background:#fafeff}"
    ".bdg{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;font-weight:600;border:1px solid;line-height:1.8}"
    ".b0{background:#e6f7ff;border-color:#91d5ff;color:#0958d9}"
    ".b1{background:#f6ffed;border-color:#b7eb8f;color:#389e0d}"
    ".b2{background:#fff7e6;border-color:#ffd591;color:#d46b08}"
    ".b3{background:#f9f0ff;border-color:#d3adf7;color:#531dab}"
    ".b4{background:#fff2f0;border-color:#ffccc7;color:#cf1322}"
    ".b5{background:#fafafa;border-color:#d9d9d9;color:#595959}"
    ".b6{background:#fff0f6;border-color:#ffadd2;color:#c41d7f}"
    ".al{padding:10px 16px;border-radius:6px;margin-bottom:14px;font-size:12px;line-height:1.7;border-left:4px solid}"
    ".ai{background:#e6f7ff;border-color:var(--p);color:#0050b3}"
    ".aw{background:#fffbe6;border-color:var(--w);color:#874d00}"
    ".ae{background:#fff2f0;border-color:var(--e);color:#a8071a}"
    ".as{background:#f6ffed;border-color:var(--s);color:#135200}"
    ".grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}"
    ".grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}"
    ".grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}"
    ".stat-card{background:var(--c);border:1px solid #f0f0f0;border-radius:6px;padding:16px 20px;}"
    ".stat-n{font-size:28px;font-weight:700;line-height:1;margin-bottom:4px}"
    ".stat-l{font-size:11px;color:var(--ts)}"
    ".stat-t{font-size:11px;margin-top:6px}"
    ".tab-bar{display:flex;border-bottom:2px solid #f0f0f0;flex-wrap:wrap}"
    ".tab{padding:10px 16px;cursor:pointer;border-bottom:2px solid transparent;font-size:12px;color:var(--ts);margin-bottom:-2px;transition:all .15s}"
    ".tab.active{color:var(--p);border-bottom-color:var(--p);font-weight:600}"
    ".tp{display:none;padding:18px 20px}.tp.active{display:block}"
    ".search-bar{background:#fafafa;border:1px solid #e8e8e8;border-radius:6px;padding:14px 16px;margin-bottom:16px;display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end}"
    ".field{display:flex;flex-direction:column;gap:4px}"
    ".field label{font-size:11px;color:var(--ts)}"
    ".inp{border:1px solid #d9d9d9;border-radius:4px;padding:5px 9px;font-size:12px;outline:none;background:#fff;min-width:120px}"
    ".inp:focus{border-color:var(--p)}"
    ".sel{border:1px solid #d9d9d9;border-radius:4px;padding:5px 9px;font-size:12px;outline:none;background:#fff;min-width:100px}"
    ".btn{border:1px solid #d9d9d9;border-radius:4px;padding:5px 12px;font-size:12px;cursor:pointer;background:#fff;transition:all .15s}"
    ".btn:hover{border-color:var(--p);color:var(--p)}"
    ".btn-p{background:var(--p);color:#fff;border-color:var(--p)}"
    ".btn-p:hover{background:#096dd9;border-color:#096dd9;color:#fff}"
    ".btn-s{background:var(--s);color:#fff;border-color:var(--s)}"
    ".btn-w{background:#fff;color:var(--w);border-color:var(--w)}"
    ".btn-e{background:#fff;color:var(--e);border-color:var(--e)}"
    ".btn-sm{padding:3px 8px;font-size:11px;border-radius:3px}"
    ".btn-link{background:none;border:none;color:var(--p);cursor:pointer;font-size:12px;padding:0}"
    ".page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}"
    ".page-title{font-size:16px;font-weight:600}"
    ".pagination{display:flex;gap:4px;align-items:center;justify-content:flex-end;padding:12px 0}"
    ".pg{width:28px;height:28px;display:flex;align-items:center;justify-content:center;border:1px solid #d9d9d9;border-radius:4px;font-size:12px;cursor:pointer}"
    ".pg.active{background:var(--p);color:#fff;border-color:var(--p)}"
    ".progress-wrap{display:flex;align-items:center;gap:8px}"
    ".progress-bar{flex:1;background:#f0f0f0;border-radius:3px;height:6px}"
    ".progress-fill{height:6px;border-radius:3px;background:var(--p)}"
    ".progress-text{font-size:11px;color:var(--ts);white-space:nowrap}"
    ".dual-panel{display:grid;grid-template-columns:240px 1fr;gap:16px}"
    ".tree-panel{border:1px solid #f0f0f0;border-radius:6px;overflow:hidden}"
    ".tree-head{padding:10px 14px;background:#fafafa;font-size:12px;font-weight:600;border-bottom:1px solid #f0f0f0}"
    ".tree-item{padding:7px 14px 7px 28px;font-size:12px;cursor:pointer;border-bottom:1px solid #f5f5f5}"
    ".tree-item:hover{background:#e6f7ff;color:var(--p)}"
    ".tree-item.active{background:#e6f7ff;color:var(--p);font-weight:600}"
    ".detail-panel{border:1px solid #f0f0f0;border-radius:6px;background:#fff}"
    ".detail-head{padding:12px 16px;border-bottom:1px solid #f0f0f0;font-weight:600;font-size:13px;display:flex;align-items:center;justify-content:space-between}"
    ".detail-body{padding:16px}"
    ".kv-row{display:grid;grid-template-columns:120px 1fr;gap:8px;padding:6px 0;border-bottom:1px solid #f5f5f5;font-size:12px}"
    ".kv-label{color:var(--ts)}"
    ".sub-task-row{display:flex;align-items:center;gap:12px;padding:10px 12px;border:1px solid #f0f0f0;border-radius:4px;margin-bottom:8px;background:#fafffe}"
    ".vendor-icon{width:28px;height:28px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;flex-shrink:0}"
    ".v-nes{background:#e6f7ff;color:#0958d9}"
    ".v-lm{background:#f6ffed;color:#389e0d}"
    ".drawer-mask{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);z-index:200}"
    ".drawer-mask.open{display:block}"
    ".drawer{position:fixed;top:0;right:-540px;width:540px;height:100%;background:#fff;z-index:201;transition:right .28s;overflow-y:auto;box-shadow:-4px 0 20px rgba(0,0,0,.15)}"
    ".drawer.open{right:0}"
    ".drawer-head{padding:14px 20px;border-bottom:1px solid #f0f0f0;font-weight:600;font-size:13px;display:flex;justify-content:space-between;align-items:center}"
    ".drawer-body{padding:16px 20px}"
    ".modal-mask{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);z-index:300;justify-content:center;align-items:center}"
    ".modal-mask.open{display:flex}"
    ".modal{background:#fff;border-radius:8px;width:520px;max-height:80vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.15)}"
    ".modal-head{padding:14px 20px;border-bottom:1px solid #f0f0f0;font-weight:600;font-size:13px;display:flex;justify-content:space-between;align-items:center}"
    ".modal-body{padding:20px}"
    ".modal-foot{padding:12px 20px;border-top:1px solid #f0f0f0;display:flex;justify-content:flex-end;gap:8px}"
    ".form-item{margin-bottom:16px}"
    ".form-label{font-size:12px;color:var(--ts);margin-bottom:4px;display:block}"
    ".form-label .req{color:var(--e)}"
    ".form-inp{width:100%;border:1px solid #d9d9d9;border-radius:4px;padding:6px 10px;font-size:12px;outline:none}"
    ".form-inp:focus{border-color:var(--p)}"
    ".form-sel{width:100%;border:1px solid #d9d9d9;border-radius:4px;padding:6px 10px;font-size:12px;outline:none}"
    ".target-textarea{width:100%;border:1px solid #d9d9d9;border-radius:4px;padding:8px 10px;font-size:12px;font-family:Consolas,monospace;height:80px;resize:vertical;outline:none}"
    ".target-textarea:focus{border-color:var(--p)}"
    ".step-dots{display:flex;gap:6px;align-items:center;padding:16px 0}"
    ".step-dot{width:8px;height:8px;border-radius:50%;background:#d9d9d9}"
    ".step-dot.active{background:var(--p);width:24px;border-radius:4px}"
    ".step-dot.done{background:var(--s)}"
    ".tag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:10px}"
    ".timeline{padding:12px 0}"
    ".tl-item{display:flex;gap:12px;margin-bottom:12px}"
    ".tl-dot{width:8px;height:8px;border-radius:50%;background:var(--p);flex-shrink:0;margin-top:5px}"
    ".tl-dot.ok{background:var(--s)}"
    ".tl-dot.fail{background:var(--e)}"
    ".tl-content{flex:1;font-size:12px}"
    ".tl-time{color:var(--ts);font-size:11px}"
    ".webhook-row{border:1px solid #f0f0f0;border-radius:4px;margin-bottom:8px}"
    ".webhook-head{padding:8px 12px;display:flex;align-items:center;gap:8px;cursor:pointer;font-size:12px}"
    ".webhook-body{padding:10px 12px;border-top:1px solid #f5f5f5;font-size:11px;font-family:Consolas,monospace;background:#fafafa;display:none;white-space:pre}"
    ".webhook-row.open .webhook-body{display:block}"
    ".empty-hint{text-align:center;padding:40px;color:var(--ts);font-size:13px}"
    ".divider{height:1px;background:#f0f0f0;margin:14px 0}"
    ".fc{background:#1e1e2e;color:#cdd6f4;border-radius:4px;padding:12px 16px;font-family:Consolas,monospace;font-size:11px;line-height:1.8;white-space:pre;overflow-x:auto}"
    ".close-btn{cursor:pointer;font-size:18px;color:var(--ts);background:none;border:none;line-height:1}"
    "code{font-size:11px;background:#f5f5f5;padding:1px 5px;border-radius:3px;font-family:Consolas,monospace;color:#c7254e}"
    ".risk-h{color:var(--e);font-weight:600}"
    ".risk-m{color:var(--w)}"
    ".risk-l{color:var(--s)}"
    ".filter-tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}"
    ".filter-tag{padding:3px 10px;border-radius:12px;font-size:11px;cursor:pointer;border:1px solid transparent}"
    ".filter-tag.active{background:var(--p);color:#fff;border-color:var(--p)}"
    ".filter-tag:not(.active){background:#f5f5f5;color:var(--ts);border-color:#e8e8e8}"
    ".split-view{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#f0f0f0;border:1px solid #f0f0f0;border-radius:6px;overflow:hidden}"
    ".split-pane{background:#fff;padding:16px}"
    ".split-pane h4{font-size:12px;font-weight:600;margin-bottom:10px;color:var(--ts)}"
    ".merge-arrow{display:flex;align-items:center;justify-content:center;font-size:18px;color:#91d5ff;padding:0 8px}"
    ".badge-vendor{font-size:10px;padding:1px 5px;border-radius:3px;font-weight:700}"
    ".nes-v{background:#e6f7ff;color:#0958d9}"
    ".lm-v{background:#f6ffed;color:#389e0d}"
    ".merge-v{background:#f9f0ff;color:#531dab}"
    "h3{font-size:13px;font-weight:600;margin:16px 0 8px;padding-bottom:5px;border-bottom:1px solid #f0f0f0}"
    "h3:first-child{margin-top:0}"
)

JS = (
    "(function(){"
    "var items=document.querySelectorAll('.ni[data-sec]');"
    "var secs=document.querySelectorAll('.sec');"
    "function show(id){"
    "secs.forEach(function(s){s.classList.remove('active')});"
    "items.forEach(function(i){i.classList.remove('active')});"
    "var s=document.getElementById('sec-'+id);if(s)s.classList.add('active');"
    "var n=document.querySelector('.ni[data-sec=\"'+id+'\"]');if(n)n.classList.add('active');}"
    "items.forEach(function(i){i.addEventListener('click',function(){show(i.dataset.sec)})});"
    "document.querySelectorAll('.tab-bar').forEach(function(bar){"
    "bar.querySelectorAll('.tab').forEach(function(tab){"
    "tab.addEventListener('click',function(){"
    "bar.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active')});"
    "tab.classList.add('active');"
    "var pid=tab.dataset.tab;"
    "tab.closest('.card,.cb').querySelectorAll('.tp').forEach(function(p){p.classList.remove('active')});"
    "var panel=document.getElementById('tp-'+pid);"
    "if(panel)panel.classList.add('active');});});});"
    "window.openDrawer=function(id){document.getElementById(id).classList.add('open');var m=document.getElementById(id+'-mask');if(m)m.classList.add('open')};"
    "window.closeDrawer=function(id){document.getElementById(id).classList.remove('open');var m=document.getElementById(id+'-mask');if(m)m.classList.remove('open')};"
    "window.openModal=function(id){document.getElementById(id).classList.add('open')};"
    "window.closeModal=function(id){document.getElementById(id).classList.remove('open')};"
    "document.querySelectorAll('.webhook-head').forEach(function(h){"
    "h.addEventListener('click',function(){h.parentElement.classList.toggle('open')});});"
    "document.querySelectorAll('.tree-item').forEach(function(it){"
    "it.addEventListener('click',function(){"
    "document.querySelectorAll('.tree-item').forEach(function(x){x.classList.remove('active')});"
    "it.classList.add('active');"
    "var tid=it.dataset.detail;"
    "if(tid){"
    "document.querySelectorAll('.detail-content').forEach(function(d){d.style.display='none'});"
    "var det=document.getElementById('det-'+tid);if(det)det.style.display='block';}});});"
    "})();"
)

def html_page(title_u, nav_groups, body_fn):
    P = []
    def a(*x):
        for v in x: P.append(v)
    first_sid = nav_groups[0][1][0][0]
    a('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"/>')
    a('<meta name="viewport" content="width=device-width,initial-scale=1"/>')
    a('<title>', title_u, '</title><style>', CSS, '</style></head><body><div class="app">')
    a('<aside class="side"><div class="logo"><span class="logo-t">', title_u, '</span>')
    a('<small class="logo-s">v2.0 \u539f\u578b</small></div>')
    for grp_lbl, items in nav_groups:
        a('<div class="ng"><div class="nt">', grp_lbl, '</div>')
        for sid, lbl in items:
            act = ' active' if sid == first_sid else ''
            a('<a class="ni', act, '" data-sec="', sid, '">', lbl, '</a>')
        a('</div>')
    a('</aside><div class="main">')
    a('<div class="topbar">')
    a('<span style="font-weight:600;font-size:14px">', title_u, '</span>')
    a('<span class="bdg b0">v2.0</span>')
    a('<span class="bdg b2">2026-06-17</span>')
    a('<span style="flex:1"></span>')
    a('<button class="btn btn-p btn-sm" onclick="openModal(\'modal-create\')">+ \u521b\u5efa\u626b\u63cf\u4efb\u52a1</button>')
    a('</div><div class="ct">')
    body_fn(a)
    a('</div></div></div>')
    a('<script>', JS, '</script></body></html>')
    return "".join(P)


# ============= helpers =============
def bdg(cls, t): return '<span class="bdg %s">%s</span>' % (cls, t)
def al(t, c): return '<div class="al a%s">%s</div>' % (t, c)
def tbl(heads, rows):
    s = '<table><tr>' + ''.join('<th>' + h + '</th>' for h in heads) + '</tr>'
    for r in rows: s += '<tr>' + ''.join('<td>' + str(c) + '</td>' for c in r) + '</tr>'
    return s + '</table>'

def card_open(a, title, extra=''):
    a('<div class="card"><div class="ch"><span>', title, '</span>', extra, '</div><div class="cb">')
def card_close(a):
    a('</div></div>')

def create_task_modal(a):
    """Create Task Modal"""
    a('<div class="modal-mask" id="modal-create"><div class="modal">')
    a('<div class="modal-head"><span>\u521b\u5efa\u626b\u63cf\u4efb\u52a1</span>')
    a('<button class="close-btn" onclick="closeModal(\'modal-create\')">&times;</button></div>')
    a('<div class="modal-body">')
    # step dots
    a('<div class="step-dots" id="step-dots">')
    for cls in ['done', 'active', '', '']:
        a('<div class="step-dot ', cls, '"></div>')
    a('</div>')
    # step 1
    a('<div id="modal-step-1" style="display:block">')
    a('<h3>\u57fa\u672c\u4fe1\u606f</h3>')
    a('<div class="form-item"><label class="form-label"><span class="req">*</span> \u4efb\u52a1\u540d\u79f0</label>')
    a('<input class="form-inp" placeholder="\u5982\uff1a2026Q2-SOC\u6838\u5fc3\u7cfb\u7edf\u6392\u67e5"/></div>')
    a('<div class="form-item"><label class="form-label"><span class="req">*</span> \u6f0f\u6d1e\u7c7b\u578b</label>')
    a('<select class="form-sel"><option>\u7cfb\u7edf\u6f0f\u6d1e</option><option>Web\u6f0f\u6d1e</option><option>\u5f31\u53e3\u4ee4</option></select></div>')
    a('<div class="form-item"><label class="form-label">\u626b\u63cf\u7b56\u7565 <span class="bdg b0" style="font-size:10px">SOC \u5f3a\u5236</span></label>')
    a('<select class="form-sel" disabled><option>SOC_DUAL (Nessus + \u7eff\u76df)</option></select></div>')
    a('<div class="form-item"><label class="form-label">\u56de\u8c03\u5730\u5740 (Webhook)</label>')
    a('<input class="form-inp" placeholder="https://your-soc.example.com/hooks/vuln"/></div>')
    a('</div>')
    # step 2
    a('<div id="modal-step-2" style="display:none">')
    a('<h3>\u626b\u63cf\u76ee\u6807</h3>')
    a(al('i', '\u652f\u6301\u8f93\u5165 IP / CIDR\uff0c\u591a\u4e2a\u7528\u9017\u53f7\u6216\u6362\u884c\u5206\u9694\uff0c\u6700\u591a 1000 \u4e2a\u5730\u5740\u3002'))
    a('<div class="form-item"><label class="form-label"><span class="req">*</span> \u76ee\u6807\u5730\u5740</label>')
    a('<textarea class="target-textarea" placeholder="10.10.1.2\n10.10.1.3\n192.168.0.0/24"></textarea></div>')
    a('<div class="form-item"><label class="form-label">\u8ba4\u8bc1\u4fe1\u606f (\u53ef\u9009)</label>')
    a('<input class="form-inp" placeholder="\u5982\uff1a admin/*** @ 22 SSH"/></div>')
    a('</div>')
    # step 3
    a('<div id="modal-step-3" style="display:none">')
    a('<h3>\u786e\u8ba4\u63d0\u4ea4</h3>')
    a('<div class="card" style="border-color:#d9d9d9">')
    a('<div class="cb">')
    for k, v in [('\u4efb\u52a1\u540d\u79f0', '2026Q2-SOC\u6838\u5fc3\u7cfb\u7edf\u6392\u67e5'),
                 ('\u6f0f\u6d1e\u7c7b\u578b', '\u7cfb\u7edf\u6f0f\u6d1e'),
                 ('\u626b\u63cf\u7b56\u7565', 'SOC_DUAL'),
                 ('\u76ee\u6807 IP \u6570', '3 \u4e2a'),
                 ('\u56de\u8c03\u5730\u5740', 'https://soc.example.com/hooks/vuln')]:
        a('<div class="kv-row"><span class="kv-label">', k, '</span><span>', v, '</span></div>')
    a('</div></div>')
    a(al('w', '\u63d0\u4ea4\u540e\u5c06\u540c\u65f6\u4e0b\u53d1 Nessus \u548c\u7eff\u76df RSAS \u53cc\u626b\uff0c\u5e76\u96c6\u5b8c\u6210\u540e\u81ea\u52a8\u56de\u8c03\u60a8\u7684 Webhook \u5730\u5740\u3002'))
    a('</div>')
    a('</div>')
    a('<div class="modal-foot">')
    a('<button class="btn" onclick="closeModal(\'modal-create\')">\u53d6\u6d88</button>')
    a('<button class="btn btn-p">\u63d0\u4ea4\u4efb\u52a1</button>')
    a('</div></div></div>')


def build_prototype():
    NAV = [
        ('\u4efb\u52a1\u7ba1\u7406', [
            ('tasklist', '\u4efb\u52a1\u5217\u8868'),
            ('taskdetail', '\u4efb\u52a1\u8be6\u60c5'),
            ('taskcreate', '\u521b\u5efa\u5411\u5bfc'),
        ]),
        ('\u6f0f\u6d1e\u5b9e\u4f8b', [
            ('instlist', '\u5b9e\u4f8b\u5217\u8868'),
            ('instlife', '\u5b9e\u4f8b\u751f\u547d\u5468\u671f'),
            ('verifyfix', '\u4fee\u590d\u6838\u9a8c\u94fe\u8def'),
            ('instbatch', '\u6279\u91cf\u64cd\u4f5c'),
        ]),
        ('\u53cc\u626b\u76d1\u63a7', [
            ('mergeview', '\u5e76\u96c6\u89c2\u6d4b'),
            ('subtask', '\u5b50\u4efb\u52a1\u72b6\u6001'),
        ]),
        ('\u5e73\u53f0\u8fd0\u8425', [
            ('webhook', 'Webhook \u65e5\u5fd7'),
            ('partner', 'Partner \u7ba1\u7406'),
            ('export', '\u6570\u636e\u5916\u53d1'),
        ]),
    ]

    def body(a):
        # ---- Modal: create task
        create_task_modal(a)

        # ===============================================================
        # 1. TASK LIST
        # ===============================================================
        a('<div id="sec-tasklist" class="sec active">')
        # stats
        a('<div class="grid4" style="margin-bottom:20px">')
        for num, lbl, cls in [('28', '\u5168\u90e8\u4efb\u52a1', ''), ('6', 'RUNNING', 'b0'), ('1', 'PARTIAL_FAILED', 'b2'), ('21', 'FINISHED', 'b1')]:
            a('<div class="stat-card"><div class="stat-n">', num, '</div>')
            a('<div class="stat-l">', bdg(cls, lbl) if cls else lbl, '</div></div>')
        a('</div>')

        # search
        a('<div class="card"><div class="ch"><span>\u4efb\u52a1\u5217\u8868</span>')
        a('<div style="display:flex;gap:8px">')
        a('<button class="btn btn-p btn-sm" onclick="openModal(\'modal-create\')">+ \u521b\u5efa</button>')
        a('<button class="btn btn-sm">CSV \u5bfc\u51fa</button>')
        a('</div></div>')
        a('<div style="padding:14px 20px 0">')
        a('<div class="search-bar">')
        for lbl, ph, w in [('\u4efb\u52a1\u540d\u79f0', '\u8f93\u5165\u540d\u79f0', 150), ('\u626b\u63cf\u7b56\u7565', '', 120), ('\u72b6\u6001', '', 110), ('\u65f6\u95f4\u8303\u56f4', '\u5f00\u59cb\u65f6\u95f4', 130)]:
            a('<div class="field"><label>', lbl, '</label>')
            if ph:
                a('<input class="inp" style="width:', str(w), 'px" placeholder="', ph, '"/>')
            else:
                a('<select class="sel" style="width:', str(w), 'px"><option>\u5168\u90e8</option></select>')
            a('</div>')
        a('<div class="field"><label>&nbsp;</label>')
        a('<div style="display:flex;gap:6px"><button class="btn btn-p">\u67e5\u8be2</button><button class="btn">\u91cd\u7f6e</button></div>')
        a('</div></div>')
        a('</div>')
        a('<div class="cb">')
        a(tbl(
            ['\u4efb\u52a1\u540d\u79f0', '\u626b\u63cf\u7b56\u7565', '\u76ee\u6807 IP', '\u72b6\u6001', '\u5e76\u96c6\u5b9e\u4f8b', '\u526f\u4efb\u52a1', '\u521b\u5efa\u65f6\u95f4', '\u64cd\u4f5c'],
            [
                ['<a class="btn-link" onclick="document.querySelector(\'.ni[data-sec=taskdetail]\').click()">2026Q2-SOC\u6838\u5fc3\u7cfb\u7edf</a>',
                 bdg('b3', 'SOC_DUAL'), '3', bdg('b0', 'RUNNING'),
                 '<div class="progress-wrap"><div class="progress-bar"><div class="progress-fill" style="width:55%"></div></div><span class="progress-text">55%</span></div>',
                 '<span class="bdg b0">NES</span> <span class="bdg b1">LM</span>', '2026-06-16 14:30', '<button class="btn btn-sm">\u67e5\u770b</button>'],
                ['SOC-\u76d1\u63a7\u8282\u70b9\u51fa\u53e3',
                 bdg('b3', 'SOC_DUAL'), '120', bdg('b2', 'PARTIAL_FAIL'),
                 '<div class="progress-wrap"><div class="progress-bar"><div class="progress-fill" style="width:80%;background:#faad14"></div></div><span class="progress-text">80%</span></div>',
                 '<span class="bdg b0">NES</span> <span class="bdg b4">LM\u5931\u8d25</span>', '2026-06-15 09:00', '<button class="btn btn-sm">\u67e5\u770b</button>'],
                ['2026Q1-\u5168\u91cf\u6392\u67e5',
                 bdg('b3', 'SOC_DUAL'), '512', bdg('b1', 'FINISHED'),
                 '182', '<span class="bdg b0">NES</span> <span class="bdg b1">LM</span>',
                 '2026-06-10 08:00', '<button class="btn btn-sm">\u67e5\u770b</button>'],
                ['\u6d4b\u8bd5-\u5f31\u53e3\u4ee4\u6e05\u67e5',
                 bdg('b5', 'SINGLE_NES'), '10', bdg('b5', 'PENDING'),
                 '-', '<span class="bdg b0">NES</span>',
                 '2026-06-16 20:00', '<button class="btn btn-sm">\u67e5\u770b</button>'],
            ]))
        a('<div class="pagination">')
        a('<span style="color:var(--ts);font-size:12px">\u5171 28 \u6761</span>')
        a('<div style="flex:1"></div>')
        for pg in ['&lt;', '1', '2', '3', '...', '4', '&gt;']:
            cls = ' active' if pg == '1' else ''
            a('<div class="pg', cls, '">', pg, '</div>')
        a('</div>')
        a('</div></div></div>')

        # ===============================================================
        # 2. TASK DETAIL
        # ===============================================================
        a('<div id="sec-taskdetail" class="sec">')
        a('<div class="page-header">')
        a('<div style="display:flex;align-items:center;gap:10px">')
        a('<button class="btn" onclick="document.querySelector(\'.ni[data-sec=tasklist]\').click()">&larr; \u8fd4\u56de</button>')
        a('<span class="page-title">2026Q2-SOC\u6838\u5fc3\u7cfb\u7edf\u6392\u67e5</span>')
        a(bdg('b0', 'RUNNING'))
        a('</div>')
        a('<div style="display:flex;gap:8px">')
        a('<button class="btn">\u5237\u65b0</button>')
        a('<button class="btn btn-e btn-sm">\u7ec8\u6b62\u4efb\u52a1</button>')
        a('</div></div>')

        # overview kv
        a('<div class="grid2" style="margin-bottom:20px">')
        a('<div class="card"><div class="ch">\u4efb\u52a1\u4fe1\u606f</div><div class="cb">')
        for k, v in [('\u4efb\u52a1 ID', '<code>TASK-7f3a2b1c</code>'),
                     ('passTaskId', '<code>10086001</code>'),
                     ('\u626b\u63cf\u7b56\u7565', bdg('b3', 'SOC_DUAL')),
                     ('\u6f0f\u6d1e\u7c7b\u578b', '\u7cfb\u7edf\u6f0f\u6d1e'),
                     ('\u76ee\u6807 IP \u6570', '3'),
                     ('biz_line', bdg('b0', 'OPEN')),
                     ('\u521b\u5efa\u65f6\u95f4', '2026-06-16 14:30:00'),
                     ('\u56de\u8c03\u5730\u5740', '<code>https://soc.example.com/hooks/vuln</code>')]:
            a('<div class="kv-row"><span class="kv-label">', k, '</span><span>', v, '</span></div>')
        a('</div></div>')

        a('<div class="card"><div class="ch">\u6574\u4f53\u8fdb\u5ea6</div><div class="cb">')
        a('<div style="margin-bottom:18px">')
        a('<div style="font-size:12px;margin-bottom:6px;color:var(--ts)">\u603b\u8fdb\u5ea6</div>')
        a('<div class="progress-wrap"><div class="progress-bar" style="height:10px"><div class="progress-fill" style="width:55%;height:10px"></div></div>')
        a('<span class="progress-text">55%</span></div>')
        a('</div>')
        a('<div style="margin-bottom:10px;font-size:12px;font-weight:600">\u53cc\u626b\u8fdb\u5ea6</div>')
        # sub tasks
        for vendor_cls, vendor_lbl, vendor_pct, vendor_stat, survey_id in [
            ('v-nes', 'NES', 70, bdg('b0', 'RUNNING'), 'SV-NES-001'),
            ('v-lm',  'LM',  40, bdg('b0', 'RUNNING'), 'SV-LM-002'),
        ]:
            a('<div class="sub-task-row">')
            a('<div class="vendor-icon ', vendor_cls, '">', vendor_lbl, '</div>')
            a('<div style="flex:1">')
            a('<div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:12px">')
            a('<span>', vendor_lbl, ' Scanner &nbsp;', vendor_stat, '</span>')
            a('<span style="color:var(--ts);font-size:11px">survey: <code>', survey_id, '</code></span>')
            a('</div>')
            a('<div class="progress-wrap"><div class="progress-bar"><div class="progress-fill" style="width:', str(vendor_pct), '%;"></div></div>')
            a('<span class="progress-text">', str(vendor_pct), '%</span></div>')
            a('</div></div>')
        a('</div></div>')
        a('</div>')

        # tabs in detail
        a('<div class="card">')
        a('<div class="tab-bar">')
        for i, lbl in enumerate(['\u5b9e\u4f8b\u5217\u8868', 'Webhook \u5386\u53f2', '\u5e76\u96c6\u9884\u89c8', '\u8fd0\u8425\u8f68']):
            a('<div class="tab', ' active' if i == 0 else '', '" data-tab="td-', str(i), '">', lbl, '</div>')
        a('</div>')

        # inst list tab
        a('<div id="tp-td-0" class="tp active">')
        a(tbl(
            ['\u6f0f\u6d1e ID', 'CVE', '\u98ce\u9669\u7b49\u7ea7', '\u5c40\u9668', '\u8d44\u4ea7 IP', '\u626b\u63cf\u5668', '\u5b9e\u4f8b\u72b6\u6001', '\u64cd\u4f5c'],
            [
                ['<code>VI-3001</code>', 'CVE-2021-44228', bdg('b4', '\u9ad8\u5371'), '\u8fdc\u7a0b\u4ee3\u6267\u884c', '10.10.1.2', '<span class="badge-vendor nes-v">NES</span> <span class="badge-vendor lm-v">LM</span>', bdg('b1', '\u5df2\u9a8c\u8bc1'), '<button class="btn btn-sm" onclick="openDrawer(\'drawer-inst\')">...</button>'],
                ['<code>VI-3002</code>', 'CVE-2022-22965', bdg('b4', '\u9ad8\u5371'), '\u8fdc\u7a0b\u4ee3\u6267\u884c', '10.10.1.3', '<span class="badge-vendor nes-v">NES</span>', bdg('b0', '\u521d\u59cb\u53d1\u73b0'), '<button class="btn btn-sm">...</button>'],
                ['<code>VI-3003</code>', 'CVE-2023-34362', bdg('b2', '\u4e2d\u5371'), 'SQL\u6ce8\u5165', '10.10.1.4', '<span class="badge-vendor lm-v">LM</span>', bdg('b0', '\u521d\u59cb\u53d1\u73b0'), '<button class="btn btn-sm">...</button>'],
            ]))
        a('</div>')

        # webhook history tab
        a('<div id="tp-td-1" class="tp">')
        for evt, stat_cls, stat_lbl, t, payload in [
            ('TASK_COMPLETED', 'b1', '\u6210\u529f', '2026-06-16 20:45:00', '{"eventType":"TASK_COMPLETED","taskId":"TASK-7f3a2b1c","mergedCount":51,"status":"FINISHED"}'),
            ('PARTIAL_FAILED', 'b2', '\u6210\u529f', '2026-06-15 16:20:00', '{"eventType":"PARTIAL_FAILED","taskId":"TASK-7f3a2b1c","failedVendor":"LM","mergedCount":32}'),
        ]:
            a('<div class="webhook-row">')
            a('<div class="webhook-head">', bdg(stat_cls, stat_lbl), '&nbsp;<strong>', evt, '</strong>')
            a('<span style="margin-left:auto;font-size:11px;color:var(--ts)">', t, '</span>')
            a('<span style="margin-left:8px">&or;</span></div>')
            a('<div class="webhook-body">', payload, '</div>')
            a('</div>')
        a('</div>')

        # merge preview tab
        a('<div id="tp-td-2" class="tp">')
        a(al('i', '\u5e76\u96c6\u5220\u53bb\u91cd\u590d\u540e\uff0c\u5c55\u793a Nessus + \u7eff\u76df \u5e76\u96c6\u7ed3\u679c\u5bf9\u6bd4\u3002'))
        a('<div class="split-view">')
        a('<div class="split-pane"><h4>\u2460 Nessus \u7ed3\u679c (42 \u6761)</h4>')
        a(tbl(['CVE', '\u98ce\u9669', '\u7aef\u53e3'], [
            ['CVE-2021-44228', bdg('b4', '\u9ad8\u5371'), '8080'],
            ['CVE-2022-22965', bdg('b4', '\u9ad8\u5371'), '443'],
            ['CVE-2023-01234', bdg('b2', '\u4e2d\u5371'), '22'],
        ]))
        a('</div>')
        a('<div class="split-pane"><h4>\u2461 \u7eff\u76df RSAS \u7ed3\u679c (38 \u6761)</h4>')
        a(tbl(['CVE', '\u98ce\u9669', '\u7aef\u53e3'], [
            ['CVE-2021-44228', bdg('b4', '\u9ad8\u5371'), '8080'],
            ['CVE-2023-34362', bdg('b2', '\u4e2d\u5371'), '3306'],
            ['CVE-2022-22965', bdg('b4', '\u9ad8\u5371'), '443'],
        ]))
        a('</div>')
        a('</div>')
        a('<div style="text-align:center;padding:12px;font-size:12px;color:var(--ts)">\u2193 \u5e76\u96c6\u540e (dedupKey \u53bb\u91cd) : <strong>51 \u6761\u5b9e\u4f8b</strong></div>')
        a(tbl(['CVE', '\u98ce\u9669', '\u7aef\u53e3', '\u6765\u6e90'], [
            ['CVE-2021-44228', bdg('b4', '\u9ad8\u5371'), '8080', '<span class="badge-vendor nes-v">NES</span> <span class="badge-vendor lm-v">LM</span>'],
            ['CVE-2022-22965', bdg('b4', '\u9ad8\u5371'), '443', '<span class="badge-vendor nes-v">NES</span> <span class="badge-vendor lm-v">LM</span>'],
            ['CVE-2023-34362', bdg('b2', '\u4e2d\u5371'), '3306', '<span class="badge-vendor lm-v">LM</span>'],
            ['CVE-2023-01234', bdg('b2', '\u4e2d\u5371'), '22', '<span class="badge-vendor nes-v">NES</span>'],
        ]))
        a('</div>')

        # rela_oper tab
        a('<div id="tp-td-3" class="tp">')
        a('<div class="timeline">')
        for dot_cls, time, content in [
            ('ok', '2026-06-16 14:30', '\u521b\u5efa\u4efb\u52a1 (biz_line=OPEN, scan_policy=SOC_DUAL)'),
            ('ok', '2026-06-16 14:30', 'Nessus survey \u5f00\u59cb (SV-NES-001)'),
            ('ok', '2026-06-16 14:30', '\u7eff\u76df survey \u5f00\u59cb (SV-LM-002)'),
            ('', '2026-06-16 14:35', 'Nessus \u5f15\u64ce RUNNING'),
            ('', '2026-06-16 14:36', '\u7eff\u76df\u5f15\u64ce RUNNING'),
        ]:
            a('<div class="tl-item"><div class="tl-dot ', dot_cls, '"></div>')
            a('<div class="tl-content"><div class="tl-time">', time, '</div><div>', content, '</div></div>')
            a('</div>')
        a('</div>')
        a('</div>')
        a('</div>')  # card close
        a('</div>')  # sec close

        # ===============================================================
        # 3. CREATE WIZARD (standalone page)
        # ===============================================================
        a('<div id="sec-taskcreate" class="sec">')
        a('<div class="page-header"><span class="page-title">\u521b\u5efa\u626b\u63cf\u4efb\u52a1</span></div>')
        a('<div style="max-width:600px">')
        a('<div class="card"><div class="ch">\u57fa\u672c\u4fe1\u606f</div><div class="cb">')
        a('<div class="form-item"><label class="form-label"><span class="req">*</span> \u4efb\u52a1\u540d\u79f0</label>')
        a('<input class="form-inp" style="width:100%" placeholder="\u4e0d\u8d85\u8fc7 128 \u5b57\u7b26"/></div>')
        a('<div class="form-item"><label class="form-label"><span class="req">*</span> \u6f0f\u6d1e\u7c7b\u578b</label>')
        a('<select class="form-sel" style="width:100%"><option>\u7cfb\u7edf\u6f0f\u6d1e</option><option>Web\u6f0f\u6d1e</option><option>\u5f31\u53e3\u4ee4</option></select></div>')
        a('<div class="form-item"><label class="form-label">\u626b\u63cf\u7b56\u7565</label>')
        a(al('i', 'SOC \u63a5\u5165\u65b9\u5f3a\u5236\u4f7f\u7528 SOC_DUAL\uff0c\u65e0\u9700\u624b\u52a8\u9009\u62e9\u3002'))
        a('<select class="form-sel" style="width:100%" disabled><option>SOC_DUAL</option></select></div>')
        a('<div class="form-item"><label class="form-label">Webhook \u56de\u8c03\u5730\u5740</label>')
        a('<input class="form-inp" style="width:100%" placeholder="https://soc.example.com/hooks/vuln"/></div>')
        a('</div></div>')
        a('<div class="card"><div class="ch">\u626b\u63cf\u76ee\u6807</div><div class="cb">')
        a('<div class="form-item"><label class="form-label"><span class="req">*</span> \u76ee\u6807 IP / CIDR</label>')
        a('<textarea class="target-textarea" style="width:100%" placeholder="10.10.1.2\n10.10.1.3\n192.168.0.0/24"></textarea>')
        a('<div style="font-size:11px;color:var(--ts);margin-top:4px">\u6700\u591a 1000 \u4e2a\uff0c\u8d85\u51fa\u8fd4\u56de 422</div>')
        a('</div>')
        a('<div class="form-item"><label class="form-label">\u8ba4\u8bc1\u4fe1\u606f (\u53ef\u9009)</label>')
        a('<button class="btn btn-sm">+ \u6dfb\u52a0 SSH/WMI \u8ba4\u8bc1</button>')
        a('</div></div></div>')
        a('<div style="display:flex;gap:8px">')
        a('<button class="btn btn-p">\u63d0\u4ea4\u4efb\u52a1</button>')
        a('<button class="btn">\u53d6\u6d88</button>')
        a('</div></div>')
        a('</div>')

        # ===============================================================
        # 4. INSTANCE LIST
        # ===============================================================
        a('<div id="sec-instlist" class="sec">')
        a('<div class="page-header"><span class="page-title">\u6f0f\u6d1e\u5b9e\u4f8b\u5217\u8868</span>')
        a('<div style="display:flex;gap:8px">')
        a('<button class="btn" onclick="document.querySelector(\'.ni[data-sec=instbatch]\').click()">\u6279\u91cf\u64cd\u4f5c</button>')
        a('<button class="btn">CSV \u5bfc\u51fa</button>')
        a('</div></div>')
        a('<div class="card"><div class="ch">\u5b9e\u4f8b\u641c\u7d22</div><div class="cb">')
        a('<div class="search-bar">')
        for lbl, ph, w in [('\u4efb\u52a1 ID', '', 130), ('\u98ce\u9669\u7b49\u7ea7', '', 110), ('\u5b9e\u4f8b\u72b6\u6001', '', 130), ('\u626b\u63cf\u5668', '', 110), ('CVE/\u6f0f\u6d1e ID', '\u5173\u952e\u8bcd', 150)]:
            a('<div class="field"><label>', lbl, '</label>')
            if ph:
                a('<input class="inp" style="width:', str(w), 'px" placeholder="', ph, '"/>')
            else:
                a('<select class="sel" style="width:', str(w), 'px"><option>\u5168\u90e8</option></select>')
            a('</div>')
        a('<div class="field"><label>&nbsp;</label><div style="display:flex;gap:6px">')
        a('<button class="btn btn-p">\u67e5\u8be2</button><button class="btn">\u91cd\u7f6e</button></div></div>')
        a('</div>')
        a('<div class="filter-tags">')
        for i, tag in enumerate(['\u5168\u90e8 (182)', '\u521d\u59cb\u53d1\u73b0 (89)', '\u5df2\u9a8c\u8bc1 (45)', '\u5df2\u4fee\u590d (30)', '\u9ad8\u5371 (62)']):
            a('<div class="filter-tag', ' active' if i == 0 else '', '">', tag, '</div>')
        a('</div>')
        a(tbl(
            ['', 'CVE', '\u6f0f\u6d1e\u540d\u79f0', '\u98ce\u9669\u7b49\u7ea7', '\u8d44\u4ea7 IP:\u7aef\u53e3', '\u626b\u63cf\u5668', '\u5b9e\u4f8b\u72b6\u6001', 'CVSS', '\u64cd\u4f5c'],
            [
                ['<input type=checkbox>', 'CVE-2021-44228', 'Log4Shell \u8fdc\u7a0b\u4ee3\u6267\u884c', bdg('b4', '\u9ad8\u5371'), '10.10.1.2:8080', '<span class="badge-vendor nes-v">NES</span><span class="badge-vendor lm-v">LM</span>', bdg('b1', '\u5df2\u9a8c\u8bc1'), '10.0',
                 '<button class="btn btn-link" onclick="openDrawer(\'drawer-inst\')">\u8be6\u60c5</button>'],
                ['<input type=checkbox>', 'CVE-2022-22965', 'Spring4Shell', bdg('b4', '\u9ad8\u5371'), '10.10.1.3:443', '<span class="badge-vendor nes-v">NES</span>', bdg('b0', '\u521d\u59cb\u53d1\u73b0'), '9.8',
                 '<button class="btn btn-link">...</button>'],
                ['<input type=checkbox>', 'CVE-2023-34362', 'MOVEit SQL\u6ce8\u5165', bdg('b2', '\u4e2d\u5371'), '10.10.1.4:3306', '<span class="badge-vendor lm-v">LM</span>', bdg('b0', '\u521d\u59cb\u53d1\u73b0'), '6.5',
                 '<button class="btn btn-link">...</button>'],
                ['<input type=checkbox>', 'CVE-2023-01234', 'SSH \u5f31\u5bc6\u7801', bdg('b1', '\u4f4e\u5371'), '10.10.1.2:22', '<span class="badge-vendor nes-v">NES</span>', bdg('b5', '\u9a8c\u8bc1\u8bef\u62a5'), '3.1',
                 '<button class="btn btn-link">...</button>'],
            ]))
        a('<div class="pagination">')
        a('<span style="color:var(--ts);font-size:12px">\u5171 182 \u6761</span><div style="flex:1"></div>')
        for pg in ['&lt;', '1', '2', '3', '...', '19', '&gt;']:
            a('<div class="pg', ' active' if pg == '1' else '', '">', pg, '</div>')
        a('</div></div></div>')
        a('</div>')  # sec

        # Drawer: instance detail
        a('<div class="drawer-mask" id="drawer-inst-mask" onclick="closeDrawer(\'drawer-inst\')"></div>')
        a('<div class="drawer" id="drawer-inst">')
        a('<div class="drawer-head"><span>\u6f0f\u6d1e\u5b9e\u4f8b\u8be6\u60c5</span>')
        a('<button class="close-btn" onclick="closeDrawer(\'drawer-inst\')">&times;</button></div>')
        a('<div class="drawer-body">')
        a('<div class="tab-bar">')
        for i, lbl in enumerate(['\u57fa\u672c\u4fe1\u606f', '\u5b9e\u4f8b\u64cd\u4f5c', '\u5386\u53f2\u8f68\u8ff9']):
            a('<div class="tab', ' active' if i == 0 else '', '" data-tab="di-', str(i), '">', lbl, '</div>')
        a('</div>')
        a('<div id="tp-di-0" class="tp active">')
        for k, v in [('vulInfoId', '<code>VI-3001</code>'), ('CVE', 'CVE-2021-44228'), ('\u6f0f\u6d1e\u540d\u79f0', 'Log4Shell'),
                     ('\u98ce\u9669\u7b49\u7ea7', bdg('b4', '\u9ad8\u5371')), ('CVSS', '10.0'), ('\u8d44\u4ea7 IP', '10.10.1.2'),
                     ('\u7aef\u53e3', '8080'), ('\u534f\u8bae', 'TCP'), ('\u626b\u63cf\u5668', '<span class="badge-vendor nes-v">NES</span> <span class="badge-vendor lm-v">LM</span>'),
                     ('\u5b9e\u4f8b\u72b6\u6001', bdg('b1', '\u5df2\u9a8c\u8bc1')), ('data_origin', '<code>OPEN</code>'), ('biz_line', '<code>OPEN</code>'),
                     ('\u4fee\u590d\u5efa\u8bae', '\u5347\u7ea7 Log4j \u5230 2.17.1+')]:
            a('<div class="kv-row"><span class="kv-label">', k, '</span><span>', v, '</span></div>')
        a('</div>')
        a('<div id="tp-di-1" class="tp">')
        a(al('w', '\u72b6\u6001\u6d41\u8f6c\u4e0d\u53ef\u9006\uff0c\u64cd\u4f5c\u524d\u8bf7\u786e\u8ba4\u3002'))
        a('<div style="display:flex;flex-direction:column;gap:10px">')
        for btn_cls, btn_lbl, rule in [
            ('btn-p', '\u9a8c\u8bc1 (verify)', '\u72b6\u6001: 1 \u2192 2 (\u6709\u6548) | 3 (\u8bef\u62a5)'),
            ('btn btn-s', '\u5907\u6848\u4fee\u590d (remediate)', '\u72b6\u6001: 1|2 \u2192 5'),
            ('btn', '\u6838\u9a8c\u4fee\u590d (verify-fix)', '\u72b6\u6001: 5 \u2192 \u5f02\u6b65\u5168\u91cf\u590d\u626b \u2192 6 (\u6838\u9a8c\u4fee\u590d) | 7 (\u6838\u9a8c\u672a\u4fee\u590d) | 10 (\u5931\u8d25)'),
        ]:
            a('<div style="border:1px solid #f0f0f0;border-radius:4px;padding:12px">')
            a('<div style="font-weight:600;font-size:12px;margin-bottom:6px">', btn_lbl, '</div>')
            a('<div style="font-size:11px;color:var(--ts);margin-bottom:8px">', rule, '</div>')
            a('<button class="btn ', btn_cls, ' btn-sm">', btn_lbl, '</button>')
            a('</div>')
        a('</div></div>')
        a('<div id="tp-di-2" class="tp">')
        a('<div class="timeline">')
        for dot_cls, t, content in [
            ('ok', '2026-06-16 14:32', '\u521d\u59cb\u53d1\u73b0 [INITIAL_DISCOVERY] - Nessus+LM \u5e76\u96c6'),
            ('ok', '2026-06-16 15:00', '\u9a8c\u8bc1 [VALIDATED_TRUE] - operator: admin@soc'),
        ]:
            a('<div class="tl-item"><div class="tl-dot ', dot_cls, '"></div>')
            a('<div class="tl-content"><div class="tl-time">', t, '</div><div style="font-size:12px">', content, '</div></div>')
            a('</div>')
        a('</div></div>')
        a('</div></div>')

        # ===============================================================
        # 5. INSTANCE LIFECYCLE
        # ===============================================================
        a('<div id="sec-instlife" class="sec">')
        a('<div class="page-header"><span class="page-title">\u5b9e\u4f8b\u751f\u547d\u5468\u671f (\u72b6\u6001\u673a\u5c55\u793a)</span></div>')
        a('<div class="card"><div class="cb">')
        a('<div style="display:flex;align-items:flex-start;gap:8px;flex-wrap:wrap">')
        STATES = [
            ('b0', '\u521d\u59cb\u53d1\u73b0\n(INITIAL_DISCOVERY)', '1'),
            ('b1', '\u5df2\u9a8c\u8bc1\u6709\u6548\n(VALIDATED_TRUE)', '2'),
            ('b4', '\u5df2\u9a8c\u8bc1\u8bef\u62a5\n(VALIDATED_FALSE)', '3'),
            ('b1', '\u5df2\u4fee\u590d\n(FIXED)', '5'),
            ('b5', '\u6838\u9a8c\u4fee\u590d\n(VERIFIED_FIXED)', '6'),
            ('b2', '\u6838\u9a8c\u672a\u4fee\u590d\n(VERIFIED_UNFIXED)', '7'),
            ('b5', '\u4fee\u590d\u5907\u6848\n(FIX_FAILED)', '9'),
        ]
        for i, (cls, lbl, code) in enumerate(STATES):
            if i > 0:
                a('<div style="padding-top:20px;color:#91d5ff;font-size:20px">&rarr;</div>')
            a('<div style="border:2px solid;border-radius:6px;padding:10px 14px;text-align:center;font-size:11px;min-width:90px;white-space:pre-line"')
            if cls == 'b0': a(' style="border-color:#91d5ff;background:#e6f7ff"')
            elif cls == 'b1': a(' style="border-color:#b7eb8f;background:#f6ffed"')
            elif cls == 'b4': a(' style="border-color:#ffccc7;background:#fff2f0"')
            elif cls == 'b2': a(' style="border-color:#ffd591;background:#fff7e6"')
            else: a(' style="border-color:#d9d9d9;background:#fafafa"')
            a('>')
            a('<div style="font-size:10px;margin-bottom:4px;color:var(--ts)">', code, '</div>', lbl)
            a('</div>')
        a('</div>')
        a('<div class="divider"></div>')
        a(al('i', '<strong>\u53cc\u8f68\u5199\u5165\u89c4\u5219\uff1a</strong>'
             'Partner \u6240\u6709\u5b9e\u4f8b\u72b6\u6001\u64cd\u4f5c\u5199\u5165 <code>vul_inst_log_rela_oper</code>\uff08\u8fd0\u8425\u8f68\uff09\uff1b'
             'ASSESS \u5de5\u5355\u8fd8\u4e0d\u5199 <code>vul_inst_log_rela_report</code>\uff08\u4e0a\u62a5\u8f68\uff09\u3002'))
        a('</div></div>')
        a('</div>')

        # ===============================================================
        # 5b. VERIFY-FIX CHAIN (??5.5)
        # ===============================================================
        a('<div id="sec-verifyfix" class="sec">')
        a('<div class="page-header"><span class="page-title">\u4fee\u590d\u6838\u9a8c\u94fe\u8def (\u00a75.5 verify-fix)</span></div>')
        a(al('i', 'Partner \u4e3b\u52a8\u53d1\u8d77\uff1b\u5e73\u53f0\u63d0\u53d6 <code>vulInfoID</code> \u2192 \u7cfb\u7edf\u6f0f\u6d1e\u5e93\u8d44\u4ea7 IP \u2192 \u6700\u8fd1 <code>scanner_vendor</code> \u2192 task-center <strong>\u5168\u91cf\u626b\u63cf</strong>\uff08\u4e0d\u652f\u6301\u6307\u5b9a\u4ea7\u54c1\u6f0f\u6d1e\uff09\u2192 \u56de\u6536\u540e\u4ec5\u5224\u5b9a\u76ee\u6807\u6f0f\u6d1e\u72b6\u6001\u3002'))
        a('<div class="card"><div class="ch">\u7aef\u5230\u7aef\u65f6\u5e8f</div><div class="cb">')
        a('<div class="fc">Partner POST /instances/{vulInfoID}/verify-fix  (stat=5)\n'
          '  -> open-api INSTANCE_VERIFY_FIX + \u5e42\u7b49\n'
          '  -> vul-pass: vul_archive_inst.assetIp + \u6700\u8fd1 sub.scanner_vendor\n'
          '  -> vuln-task-center: SINGLE \u5168\u91cf survey (\u975e SOC_DUAL)\n'
          '  -> Kafka \u56de\u6536\u5168\u91cf\u7ed3\u679c\n'
          '  -> \u4ec5\u5339\u914d\u76ee\u6807 vulInfoID: \u672a\u68c0\u51fa->6 | \u4ecd\u68c0\u51fa->7 | \u5931\u8d25->10\n'
          '  -> Webhook INSTANCE_VERIFY_FIX_COMPLETED + EXPORT_READY(VERIFY_FIX_SCAN)</div>')
        a('</div></div>')
        a('<div class="grid2">')
        a('<div class="card"><div class="ch">\u53d7\u7406\u793a\u4f8b</div><div class="cb">')
        a('<div class="fc">POST /api/open/v1/instances/VI-3001/verify-fix\n{\n  "transferTime": "1747488000",\n  "remark": "\u5b89\u6392\u590d\u626b POC"\n}\n\n'
          'Response:\n{\n  "vulInfoID": "VI-3001",\n  "vulInfoStat": 5,\n'
          '  "verifyFixStatus": "RUNNING",\n  "verifyFixJobId": "VFJ-20260617-001"\n}</div>')
        a('</div></div>')
        a('<div class="card"><div class="ch">\u626b\u63cf\u4e0b\u53d1\u53c2\u6570</div><div class="cb">')
        a(tbl(['\u5b57\u6bb5', '\u6765\u6e90', '\u8bf4\u660e'], [
            ['targets.hosts', 'vul_archive_inst.assetIp', '\u5f71\u54cd\u8d44\u4ea7 IP'],
            ['scanner_vendor', 'vul_scan_task_sub \u6700\u8fd1\u4e00\u6b21', 'NESSUS / LM / AH'],
            ['scan_policy', '\u56fa\u5b9a', 'SINGLE\uff08\u975e\u53cc\u626b\uff09'],
            ['tsk_scn', '\u56fa\u5b9a', 'VERIFY_FIX'],
            ['vul_filter', '\u4e0d\u4f20', 'task-center \u5168\u91cf\u626b\u63cf'],
        ]))
        a('</div></div>')
        a('</div>')
        a('<div class="card"><div class="ch">\u6838\u9a8c\u4efb\u52a1\u76d1\u63a7</div><div class="cb">')
        a(tbl(['verifyFixJobId', 'vulInfoID', '\u8d44\u4ea7 IP', '\u626b\u63cf\u5668', '\u72b6\u6001', '\u7ed3\u679c'],
            [
                ['<code>VFJ-20260617-001</code>', 'VI-3001', '10.10.1.2', '<span class="badge-vendor nes-v">NESSUS</span>',
                 bdg('b0', 'RUNNING'), '-'],
                ['<code>VFJ-20260616-088</code>', 'VI-2888', '10.10.1.5', '<span class="badge-vendor lm-v">LM</span>',
                 bdg('b1', 'FINISHED'), bdg('b1', '\u6838\u9a8c\u4fee\u590d (6)')],
                ['<code>VFJ-20260616-077</code>', 'VI-2777', '10.10.1.8', '<span class="badge-vendor nes-v">NESSUS</span>',
                 bdg('b1', 'FINISHED'), bdg('b2', '\u6838\u9a8c\u672a\u4fee\u590d (7)')],
            ]))
        a(al('w', '\u5168\u91cf\u626b\u63cf\u7ed3\u679c\u4e2d\u4ec5\u5bf9\u672c\u6b21 <code>vulInfoID</code> \u505a\u5b58\u5728\u6027\u5224\u5b9a\uff1b\u5176\u4f59\u65b0\u53d1\u73b0\u6f0f\u6d1e\u4e0d\u6539\u5199\u5f53\u524d\u5b9e\u4f8b\u72b6\u6001\u3002'))
        a('</div></div>')
        a('</div>')

        # ===============================================================
        # 6. BATCH OPERATION
        # ===============================================================
        a('<div id="sec-instbatch" class="sec">')
        a('<div class="page-header"><span class="page-title">\u6279\u91cf\u64cd\u4f5c</span></div>')
        a('<div class="card"><div class="ch">\u9009\u62e9\u8303\u56f4</div><div class="cb">')
        a('<div class="search-bar">')
        a('<div class="field"><label>\u4efb\u52a1 ID</label><input class="inp" value="TASK-7f3a2b1c"/></div>')
        a('<div class="field"><label>\u98ce\u9669\u7b49\u7ea7</label><select class="sel"><option>\u9ad8\u5371</option></select></div>')
        a('<div class="field"><label>\u5b9e\u4f8b\u72b6\u6001</label><select class="sel"><option>\u521d\u59cb\u53d1\u73b0</option></select></div>')
        a('<div class="field"><label>&nbsp;</label><button class="btn btn-p">\u67e5\u8be2</button></div>')
        a('</div></div></div>')
        a('<div class="card"><div class="ch">\u64cd\u4f5c\u9009\u62e9</div><div class="cb">')
        a('<div class="grid3">')
        for btn_t, btn_desc, btn_cls in [
            ('\u6279\u91cf\u9a8c\u8bc1 (verify)', '\u5c06\u9009\u4e2d\u5b9e\u4f8b\u6807\u8bc1\u4e3a\u9a8c\u8bc1\u72b6\u6001', 'b0'),
            ('\u6279\u91cf\u5907\u6848\u4fee\u590d (remediate)', '\u786e\u8ba4\u5df2\u4fee\u590d\uff0c\u5f85\u6838\u9a8c', 'b1'),
            ('\u6279\u91cf\u6838\u9a8c\u4fee\u590d (verify-fix)', '\u6838\u9a8c\u4fee\u590d\u7ed3\u679c', 'b3'),
        ]:
            a('<div style="border:1px solid #f0f0f0;border-radius:6px;padding:16px">')
            a('<div style="font-weight:600;font-size:13px;margin-bottom:6px">', btn_t, '</div>')
            a('<div style="font-size:12px;color:var(--ts);margin-bottom:12px">', btn_desc, '</div>')
            a('<button class="btn btn-sm ', btn_cls, '">', btn_t, '</button>')
            a('</div>')
        a('</div></div></div>')
        a('<div class="card"><div class="ch">\u5f85\u5904\u7406\u5b9e\u4f8b (\u9009\u4e2d 89 \u6761)</div><div class="cb">')
        a(tbl(['', 'CVE', '\u8d44\u4ea7 IP', '\u72b6\u6001', '\u98ce\u9669'], [
            ['<input type=checkbox checked>', 'CVE-2021-44228', '10.10.1.2', bdg('b0', '\u521d\u59cb\u53d1\u73b0'), bdg('b4', '\u9ad8\u5371')],
            ['<input type=checkbox checked>', 'CVE-2022-22965', '10.10.1.3', bdg('b0', '\u521d\u59cb\u53d1\u73b0'), bdg('b4', '\u9ad8\u5371')],
            ['<input type=checkbox>', 'CVE-2023-34362', '10.10.1.4', bdg('b0', '\u521d\u59cb\u53d1\u73b0'), bdg('b2', '\u4e2d\u5371')],
        ]))
        a('</div></div>')
        a('</div>')

        # ===============================================================
        # 7. MERGE VIEW
        # ===============================================================
        a('<div id="sec-mergeview" class="sec">')
        a('<div class="page-header"><span class="page-title">\u5e76\u96c6\u89c2\u6d4b (SOC_DUAL)</span></div>')
        a('<div class="grid4" style="margin-bottom:20px">')
        for num, lbl, cls in [('42', 'Nessus \u5b9e\u4f8b', 'b0'), ('38', '\u7eff\u76df \u5b9e\u4f8b', 'b1'), ('29', '\u91cd\u53e0\u5b9e\u4f8b', 'b3'), ('51', '\u5e76\u96c6\u7ed3\u679c', 'b5')]:
            a('<div class="stat-card"><div class="stat-n">', num, '</div><div class="stat-l">', bdg(cls, lbl), '</div></div>')
        a('</div>')
        a('<div class="card"><div class="ch">\u5e76\u96c6\u72b6\u6001\u77e9\u9635</div><div class="cb">')
        a(tbl(['dedupKey', 'CVE', '\u8d44\u4ea7 IP:\u7aef\u53e3', 'Nessus', '\u7eff\u76df', '\u5e76\u96c6\u7ed3\u679c', '\u51b2\u7a81\u5904\u7406'],
            [
                ['sha256:a1b2...', 'CVE-2021-44228', '10.10.1.2:8080', bdg('b4', '\u9ad8\u5371 10.0'), bdg('b4', '\u9ad8\u5371 10.0'), bdg('b3', '\u5e76\u96c6'), '\u65e0\u51b2\u7a81'],
                ['sha256:c3d4...', 'CVE-2022-22965', '10.10.1.3:443', bdg('b4', '\u9ad8\u5371 9.8'), bdg('b2', '\u4e2d\u5371 7.5'), bdg('b4', '\u9ad8\u5371 9.8'), '\u4fdd\u7559\u9ad8\u5371'],
                ['sha256:e5f6...', 'CVE-2023-34362', '10.10.1.4:3306', '-', bdg('b2', '\u4e2d\u5371 6.5'), bdg('b1', 'LM \u5355\u65b9'), '\u65e0\u51b2\u7a81'],
            ]))
        a('</div></div>')
        a('<div class="card"><div class="ch">\u5de5\u4f5c\u539f\u7406</div><div class="cb">')
        a('<div style="font-size:12px;line-height:2">')
        a('<strong>dedupKey = sha256( assetIp + ":" + port + ":" + protocol + ":" + service + ":" + vulId )</strong><br/>')
        a('\u51b2\u7a81\u5904\u7406\uff1aseverity/cvssScore \u53d6\u9ad8\u8005\uff0c\u6587\u672c\u5b57\u6bb5\u53d6\u5e76\u96c6\uff0c\u5382\u5546\u5217\u8868\u5c55\u5f00 [NESSUS, LM]<br/>')
        a('\u5b9e\u4f8b\u5199\u5165: <code>vul_archive_inst</code> (data_origin=OPEN) + <code>vul_inst_log_rela_oper</code>')
        a('</div></div></div>')
        a('</div>')

        # ===============================================================
        # 8. SUB TASK STATUS
        # ===============================================================
        a('<div id="sec-subtask" class="sec">')
        a('<div class="page-header"><span class="page-title">\u5b50\u4efb\u52a1\u72b6\u6001 (\u53cc survey)</span></div>')
        a('<div class="card"><div class="cb">')
        a(tbl(['\u4efb\u52a1', '\u5b50\u4efb\u52a1 ID', '\u626b\u63cf\u5668', 'survey ID', '\u72b6\u6001', '\u8fdb\u5ea6', '\u5f00\u59cb\u65f6\u95f4', '\u8d85\u65f6\u65f6\u95f4'],
            [
                ['2026Q2-SOC\u6838\u5fc3', '<code>2001</code>', '<span class="badge-vendor nes-v">NESSUS</span>', 'SV-NES-001', bdg('b0', 'RUNNING'),
                 '<div class="progress-wrap"><div class="progress-bar"><div class="progress-fill" style="width:70%"></div></div><span class="progress-text">70%</span></div>',
                 '14:30', '16:30'],
                ['2026Q2-SOC\u6838\u5fc3', '<code>2002</code>', '<span class="badge-vendor lm-v">LM</span>', 'SV-LM-002', bdg('b0', 'RUNNING'),
                 '<div class="progress-wrap"><div class="progress-bar"><div class="progress-fill" style="width:40%"></div></div><span class="progress-text">40%</span></div>',
                 '14:30', '17:00'],
                ['SOC-\u76d1\u63a7\u8282\u70b9', '<code>1901</code>', '<span class="badge-vendor nes-v">NESSUS</span>', 'SV-NES-090', bdg('b1', 'FINISHED'), '100%', '09:00', '-'],
                ['SOC-\u76d1\u63a7\u8282\u70b9', '<code>1902</code>', '<span class="badge-vendor lm-v">LM</span>', 'SV-LM-091', bdg('b4', 'FAILED'), '\u5931\u8d25', '09:00', '-'],
            ]))
        a('</div></div>')
        a(al('w', 'PARTIAL_FAILED \u573a\u666f\uff1aSOC-\u76d1\u63a7\u8282\u70b9 \u4e2d LM survey \u5931\u8d25\uff0c'
             'Nessus \u7ed3\u679c\u5df2\u5355\u65b9\u5165\u5e93\uff0c\u7236\u4efb\u52a1\u7f6e PARTIAL_FAILED\uff0c'
             'Webhook \u63a8\u9001 PARTIAL_FAILED \u4e8b\u4ef6\u3002'))
        a('</div>')

        # ===============================================================
        # 9. WEBHOOK LOG
        # ===============================================================
        a('<div id="sec-webhook" class="sec">')
        a('<div class="page-header"><span class="page-title">Webhook \u56de\u8c03\u65e5\u5fd7</span>')
        a('<button class="btn btn-sm">+ \u624b\u52a8\u91cd\u5c04</button></div>')
        a('<div class="card"><div class="ch">\u56de\u8c03\u5386\u53f2</div><div class="cb">')
        a(tbl(['\u4efb\u52a1 ID', 'eventType', '\u72b6\u6001', '\u5c1d\u8bd5\u6b21\u6570', '\u6700\u8fd1\u65f6\u95f4', 'HTTP\u7801', '\u64cd\u4f5c'],
            [
                ['TASK-7f3a2b1c', 'TASK_COMPLETED', bdg('b1', '\u6210\u529f'), '1', '2026-06-16 20:45', '200', '<button class="btn btn-link" onclick="document.querySelector(\'.webhook-row\').classList.toggle(\'open\')">\u67e5\u770b\u8d1f\u8f7d</button>'],
                ['TASK-abc00001', 'TASK_COMPLETED', bdg('b4', '\u5168\u90e8\u5931\u8d25'), '5', '2026-06-15 12:30', '502', '<button class="btn btn-link">\u624b\u52a8\u91cd\u5c04</button>'],
                ['TASK-def00002', 'PARTIAL_FAILED', bdg('b2', '\u91cd\u8bd5\u4e2d'), '3', '2026-06-15 16:20', '504', ''],
            ]))
        a('</div></div>')
        a('<div class="card"><div class="ch">\u91cd\u8bd5\u7b56\u7565</div><div class="cb">')
        a('<div style="font-size:12px;line-height:2">')
        a('\u6307\u6570\u9000\u907f: <strong>1s / 5s / 30s / 120s / 600s</strong>\uff0c\u6700\u591a 5 \u6b21\uff1b\u5168\u90e8\u5931\u8d25\u540e\u8fdb\u6b7b\u4fe1\u961f\u5217\u3002<br/>')
        a('\u7b7e\u540d\u65b9\u5f0f: <code>X-ESMP-Signature: sha256=HMAC-SHA256(body, partnerSecret)</code><br/>')
        a('\u8bf7\u6c42\u8d85\u65f6: 10s\uff1b\u5e42\u7b49\u952e: eventType+taskId')
        a('</div></div></div>')
        a('</div>')

        # ===============================================================
        # 10. PARTNER MANAGEMENT
        # ===============================================================
        a('<div id="sec-partner" class="sec">')
        a('<div class="page-header"><span class="page-title">Partner \u7ba1\u7406</span>')
        a('<button class="btn btn-p btn-sm">+ \u5f00\u901a Partner</button></div>')
        a('<div class="card"><div class="cb">')
        a(tbl(['\u540d\u79f0', 'Partner ID', '\u7c7b\u578b', '\u626b\u63cf\u7b56\u7565', 'Webhook', '\u72b6\u6001', '\u64cd\u4f5c'],
            [
                ['SOC-CLIENT-A', '<code>SOC-CLIENT-A</code>', 'SOC', bdg('b3', 'SOC_DUAL'),
                 '\u5df2\u914d\u7f6e', bdg('b1', '\u5df2\u5f00\u901a'), '<button class="btn btn-link">\u7f16\u8f91</button>'],
                ['SIEM-PARTNER-B', '<code>SIEM-B</code>', 'SIEM', bdg('b5', 'SINGLE_NES'),
                 '\u5df2\u914d\u7f6e', bdg('b0', '\u8bd5\u7528\u671f'), '<button class="btn btn-link">\u7f16\u8f91</button>'],
            ]))
        a('</div></div>')
        a('</div>')

        # ===============================================================
        # 11. EXPORT
        # ===============================================================
        a('<div id="sec-export" class="sec">')
        a('<div class="page-header"><span class="page-title">\u6570\u636e\u5916\u53d1</span></div>')
        a('<div class="card"><div class="ch">\u5916\u53d1\u914d\u7f6e</div><div class="cb">')
        a('<div class="form-item"><label class="form-label">\u4efb\u52a1\u9009\u62e9</label>')
        a('<select class="form-sel" style="width:300px"><option>2026Q2-SOC\u6838\u5fc3\u7cfb\u7edf\u6392\u67e5</option></select></div>')
        a('<div class="form-item"><label class="form-label">\u5bfc\u51fa\u683c\u5f0f</label>')
        a('<div style="display:flex;gap:8px">')
        for fmt in ['JSON', 'XML', 'CSV', 'PDF']:
            a('<div style="border:1px solid #d9d9d9;border-radius:4px;padding:6px 14px;cursor:pointer;font-size:12px">', fmt, '</div>')
        a('</div></div>')
        a('<div class="form-item"><label class="form-label">\u7b5b\u9009\u5b57\u6bb5</label>')
        a('<div style="display:flex;flex-wrap:wrap;gap:6px">')
        for f in ['\u6f0f\u6d1e\u4fe1\u606f', '\u8d44\u4ea7\u4fe1\u606f', 'CVE', '\u4fee\u590d\u5efa\u8bae', '\u5b9e\u4f8b\u72b6\u6001', '\u626b\u63cf\u5668\u6765\u6e90']:
            a('<label style="display:flex;align-items:center;gap:4px;font-size:12px"><input type=checkbox checked/>', f, '</label>')
        a('</div></div>')
        a('<button class="btn btn-p">\u751f\u6210\u5916\u53d1\u6587\u4ef6</button>')
        a('</div></div>')
        a('<div class="card"><div class="ch">\u5386\u53f2\u5916\u53d1\u8bb0\u5f55</div><div class="cb">')
        a(tbl(['\u4efb\u52a1', '\u683c\u5f0f', '\u72b6\u6001', '\u521b\u5efa\u65f6\u95f4', '\u64cd\u4f5c'],
            [
                ['2026Q1-\u5168\u91cf\u6392\u67e5', 'JSON', bdg('b1', '\u5c31\u7eea'), '2026-06-10 10:00', '<button class="btn btn-link">\u4e0b\u8f7d</button>'],
                ['2026Q1-\u5168\u91cf\u6392\u67e5', 'XML', bdg('b5', '\u5df2\u8fc7\u671f'), '2026-06-08 08:00', '<button class="btn btn-link" style="color:var(--ts)">\u91cd\u65b0\u751f\u6210</button>'],
            ]))
        a('</div></div>')
        a('</div>')

    return html_page(
        '\u5f00\u653e API \u7f16\u6392 \u00b7 SOC \u53cc\u626b\u8fd0\u8425\u5de5\u4f5c\u53f0',
        NAV,
        body
    )


if __name__ == "__main__":
    html = build_prototype()
    out = OUTDIR / "open-api-vtc-pass-prototype-v2.html"
    out.write_text(html, encoding="utf-8")
    print("Prototype v2 OK:", out, "bytes", len(html.encode("utf-8")))
