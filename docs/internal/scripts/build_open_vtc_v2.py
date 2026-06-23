# -*- coding: utf-8 -*-
# ASCII-ONLY source. All CJK via \uXXXX in string literals.
# Generates: open-api-vtc-prd-v2.html  +  open-api-vtc-pass-prototype-v2.html
from pathlib import Path

OUTDIR = Path(__file__).resolve().parent.parent / "prototypes"
OUTDIR.mkdir(parents=True, exist_ok=True)

# ---------- helpers ---------------------------------------------------------
def make_html(title_u, nav_groups, sections_fn):
    """Build a complete HTML page."""
    P = []
    def a(*x):
        for v in x: P.append(v)

    CSS = (
        ":root{--p:#1890ff;--s:#52c41a;--w:#faad14;--e:#ff4d4f"
        ";--t:rgba(0,0,0,.85);--ts:rgba(0,0,0,.45);--bg:#f0f2f5;--c:#fff;--sb:#001529}"
        "*{box-sizing:border-box;margin:0;padding:0}"
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif"
        ";font-size:14px;color:var(--t);background:var(--bg);line-height:1.6}"
        ".app{display:flex;min-height:100vh}"
        ".side{width:256px;background:var(--sb);color:#fff;flex-shrink:0;position:sticky;top:0;height:100vh;overflow-y:auto}"
        ".logo{padding:16px 20px;font-size:15px;font-weight:700;border-bottom:1px solid rgba(255,255,255,.1);line-height:1.4}"
        ".logo small{display:block;font-size:11px;font-weight:400;opacity:.5;margin-top:2px}"
        ".ng{padding:14px 0 4px}.nt{padding:3px 20px;font-size:10px;color:rgba(255,255,255,.3);letter-spacing:.5px}"
        ".ni{display:block;padding:7px 20px 7px 32px;color:rgba(255,255,255,.6);font-size:13px;cursor:pointer;text-decoration:none;border-left:3px solid transparent}"
        ".ni:hover{color:#fff;background:rgba(255,255,255,.06)}"
        ".ni.active{color:#fff;background:rgba(24,144,255,.15);border-left-color:var(--p)}"
        ".main{flex:1;overflow:auto;min-width:0}"
        ".topbar{height:52px;background:var(--c);border-bottom:1px solid #f0f0f0;display:flex;align-items:center;padding:0 28px;position:sticky;top:0;z-index:99;gap:12px;box-shadow:0 1px 4px rgba(0,0,0,.06)}"
        ".ct{padding:28px;max-width:1140px}"
        ".sec{display:none}.sec.active{display:block}"
        ".card{background:var(--c);border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.06);margin-bottom:24px;border:1px solid #f0f0f0}"
        ".ch{padding:16px 24px;border-bottom:1px solid #f0f0f0;font-weight:600;font-size:14px;display:flex;align-items:center;gap:10px;justify-content:space-between}"
        ".cb{padding:20px 24px}"
        "table{width:100%;border-collapse:collapse}"
        "th,td{padding:10px 14px;border-bottom:1px solid #f0f0f0;vertical-align:top;font-size:13px}"
        "th{background:#fafafa;font-weight:600;white-space:nowrap;color:var(--ts)}"
        "td code{font-size:11px;background:#f5f5f5;padding:1px 6px;border-radius:3px;font-family:Consolas,monospace;color:#c7254e}"
        ".bdg{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:600;border:1px solid;line-height:1.8}"
        ".b0{background:#e6f7ff;border-color:#91d5ff;color:#0958d9}"
        ".b1{background:#f6ffed;border-color:#b7eb8f;color:#389e0d}"
        ".b2{background:#fff7e6;border-color:#ffd591;color:#d46b08}"
        ".b3{background:#f9f0ff;border-color:#d3adf7;color:#531dab}"
        ".b4{background:#fff2f0;border-color:#ffccc7;color:#cf1322}"
        ".b5{background:#fafafa;border-color:#d9d9d9;color:#595959}"
        ".al{padding:12px 18px;border-radius:6px;margin-bottom:18px;font-size:13px;line-height:1.7;border-left:4px solid}"
        ".ai{background:#e6f7ff;border-color:var(--p);color:#0050b3}"
        ".aw{background:#fffbe6;border-color:var(--w);color:#874d00}"
        ".ae{background:#fff2f0;border-color:var(--e);color:#a8071a}"
        ".as{background:#f6ffed;border-color:var(--s);color:#135200}"
        ".fc{background:#1e1e2e;color:#cdd6f4;border-radius:6px;padding:18px 22px;font-family:Consolas,monospace;font-size:12px;line-height:1.9;white-space:pre;overflow-x:auto;margin-bottom:16px}"
        ".grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}"
        ".grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}"
        ".grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}"
        ".kpi{background:var(--c);border:1px solid #f0f0f0;border-radius:6px;padding:18px}"
        ".kpi .n{font-size:30px;font-weight:700;margin-bottom:4px;line-height:1}"
        ".kpi .l{font-size:12px;color:var(--ts)}"
        ".tl{border-left:3px solid #e8e8e8;padding-left:22px;margin-left:10px}"
        ".tli{margin-bottom:18px;position:relative}"
        ".tli::before{content:'';width:12px;height:12px;border-radius:50%;background:var(--p);position:absolute;left:-30px;top:3px}"
        ".tli.done::before{background:var(--s)}.tli.pend::before{background:#d9d9d9}"
        ".tl-h{font-weight:600;margin-bottom:4px;font-size:13px}"
        ".tl-d{color:var(--ts);font-size:12px;line-height:1.7}"
        ".steps{display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin:12px 0}"
        ".step{padding:8px 14px;background:#e6f7ff;border:1px solid #91d5ff;border-radius:6px;font-size:12px;text-align:center;min-width:80px;line-height:1.4}"
        ".sarr{padding:0 4px;color:#91d5ff;font-size:18px}"
        ".sm{background:#fafafa;border:1px solid #e8e8e8;border-radius:4px;padding:14px 18px;font-family:Consolas,monospace;font-size:12px;line-height:1.8;white-space:pre}"
        "h3{font-size:14px;font-weight:600;margin:22px 0 10px;color:var(--t);padding-bottom:6px;border-bottom:1px solid #f0f0f0}"
        "h4{font-size:13px;font-weight:600;margin:14px 0 8px;color:var(--ts)}"
        ".sep{height:1px;background:#f0f0f0;margin:18px 0}"
        ".tag-w0{background:#e6f7ff;color:#0958d9;border:1px solid #91d5ff;font-size:10px;padding:1px 6px;border-radius:3px}"
        ".tag-w1{background:#f6ffed;color:#389e0d;border:1px solid #b7eb8f;font-size:10px;padding:1px 6px;border-radius:3px}"
        ".tag-done{background:#f6ffed;color:#389e0d;border:1px solid #b7eb8f;font-size:10px;padding:1px 6px;border-radius:3px}"
        ".tab-bar{display:flex;border-bottom:1px solid #f0f0f0;background:var(--c);flex-wrap:wrap}"
        ".tab{padding:12px 18px;cursor:pointer;border-bottom:2px solid transparent;font-size:13px;color:var(--ts)}"
        ".tab.active{color:var(--p);border-bottom-color:var(--p);font-weight:600}"
        ".tp{display:none;padding:20px 24px}.tp.active{display:block}"
        ".kv{display:flex;margin-bottom:10px;font-size:13px}"
        ".kv .k{width:130px;color:var(--ts);flex-shrink:0}"
        ".dual{display:grid;grid-template-columns:1fr 1fr;gap:16px}"
        ".scard{border:1px solid #f0f0f0;border-radius:6px;padding:16px}"
        ".scard h4{margin:0 0 12px;font-size:13px;font-weight:600}"
        ".progress-bar{background:#f0f0f0;border-radius:4px;height:8px;margin:8px 0}"
        ".progress-fill{height:8px;border-radius:4px;background:var(--p)}"
        ".merge-v{display:flex;align-items:center;justify-content:center;gap:16px;padding:24px;flex-wrap:wrap}"
        ".mbox{border:2px solid #91d5ff;background:#e6f7ff;padding:16px 28px;text-align:center;border-radius:6px;min-width:100px}"
        ".mbox.result{border-color:#b7eb8f;background:#f6ffed}"
        ".search-row{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap}"
        ".inp{border:1px solid #d9d9d9;border-radius:4px;padding:6px 10px;font-size:13px;outline:none}"
        ".btn{border:1px solid #d9d9d9;border-radius:4px;padding:6px 12px;font-size:13px;cursor:pointer;background:#fff}"
        ".btn-p{background:var(--p);color:#fff;border-color:var(--p)}"
        ".btn-s{background:var(--s);color:#fff;border-color:var(--s)}"
        ".seq-table{font-family:Consolas,monospace;font-size:11px}"
        ".err{color:var(--e)}"
        ".ok{color:var(--s)}"
        ".warn{color:var(--w)}"
        "tr:hover td{background:#fafeff}"
        ".drawer-mask{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);z-index:200}"
        ".drawer-mask.open{display:block}"
        ".drawer{position:fixed;top:0;right:-520px;width:520px;height:100%;background:#fff;z-index:201;transition:right .3s;overflow-y:auto;box-shadow:-4px 0 20px rgba(0,0,0,.15)}"
        ".drawer.open{right:0}"
        ".drawer-head{padding:16px 24px;border-bottom:1px solid #f0f0f0;font-weight:600;display:flex;justify-content:space-between;align-items:center}"
        ".drawer-body{padding:20px 24px}"
        ".close-btn{cursor:pointer;font-size:18px;color:var(--ts);background:none;border:none}"
    )

    a('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"/>')
    a('<meta name="viewport" content="width=device-width,initial-scale=1"/>')
    a('<title>', title_u, '</title>')
    a('<style>', CSS, '</style></head><body><div class="app">')

    # sidebar
    first_sid = nav_groups[0][1][0][0]
    a('<aside class="side"><div class="logo">', title_u, '</div>')
    for grp_lbl, items in nav_groups:
        a('<div class="ng"><div class="nt">', grp_lbl, '</div>')
        for sid, lbl in items:
            act = ' active' if sid == first_sid else ''
            a('<a class="ni', act, '" data-sec="', sid, '">', lbl, '</a>')
        a('</div>')
    a('</aside>')

    # main
    a('<div class="main">')
    a('<div class="topbar"><span style="font-weight:600;font-size:15px">', title_u, '</span>')
    a('<span class="bdg b0">v2.0</span>')
    a('<span class="bdg b2">2026-06-16</span>')
    a('</div><div class="ct">')

    sections_fn(a)

    a('</div></div></div>')
    a('<script>')
    a('(function(){')
    a('var items=document.querySelectorAll(".ni[data-sec]");')
    a('var secs=document.querySelectorAll(".sec");')
    a('function show(id){')
    a('secs.forEach(function(s){s.classList.remove("active")});')
    a('items.forEach(function(i){i.classList.remove("active")});')
    a('var s=document.getElementById("sec-"+id);if(s)s.classList.add("active");')
    a('var n=document.querySelector(".ni[data-sec=\'"+id+"\']");if(n)n.classList.add("active");')
    a('}')
    a('items.forEach(function(i){i.addEventListener("click",function(){show(i.dataset.sec)})});')
    # tab switching
    a('document.querySelectorAll(".tab-bar").forEach(function(bar){')
    a('bar.querySelectorAll(".tab").forEach(function(tab){')
    a('tab.addEventListener("click",function(){')
    a('bar.querySelectorAll(".tab").forEach(function(t){t.classList.remove("active")});')
    a('tab.classList.add("active");')
    a('var panel=document.getElementById("tp-"+tab.dataset.tab);')
    a('if(panel){')
    a('panel.parentElement.querySelectorAll(".tp").forEach(function(p){p.classList.remove("active")});')
    a('panel.classList.add("active");}')
    a('});});});')
    # drawer
    a('window.openDrawer=function(id){document.getElementById(id).classList.add("open");document.getElementById(id+"-mask").classList.add("open")};')
    a('window.closeDrawer=function(id){document.getElementById(id).classList.remove("open");document.getElementById(id+"-mask").classList.remove("open")};')
    a('})();')
    a('</script></body></html>')

    return "".join(P)


# ---------- reusable helpers ------------------------------------------------
def tbl(heads, rows, extra_class=""):
    s = '<table class="' + extra_class + '"><tr>' + ''.join('<th>' + h + '</th>' for h in heads) + '</tr>'
    for r in rows:
        s += '<tr>' + ''.join('<td>' + str(c) + '</td>' for c in r) + '</tr>'
    return s + '</table>'

def card(a_fn, title, body, badge=""):
    badge_html = (' <span class="tag-w0">' + badge + '</span>') if badge else ""
    a_fn('<div class="card"><div class="ch">', title, badge_html, '</div><div class="cb">', body, '</div></div>')

def al(t, c):
    return '<div class="al a' + t + '">' + c + '</div>'

def bdg(cls, text):
    return '<span class="bdg ' + cls + '">' + text + '</span>'

def fc(code):
    return '<div class="fc">' + code + '</div>'

def sm(code):
    return '<div class="sm">' + code + '</div>'

def sec_open(a_fn, sid, active=False):
    a_fn('<div id="sec-', sid, '" class="sec', ' active' if active else '', '">')

def sec_close(a_fn):
    a_fn('</div>')

def tab_bar(a_fn, bar_id, tabs, sec_prefix):
    a_fn('<div class="tab-bar" id="', bar_id, '">')
    for i, (tid, tlbl) in enumerate(tabs):
        act = ' active' if i == 0 else ''
        a_fn('<div class="tab', act, '" data-tab="', sec_prefix, '-', tid, '">', tlbl, '</div>')
    a_fn('</div>')
    for i, (tid, _) in enumerate(tabs):
        a_fn('<div id="tp-', sec_prefix, '-', tid, '" class="tp', ' active' if i == 0 else '', '">')

def tp_close(a_fn):
    a_fn('</div>')

def drawer(a_fn, did, title, body):
    a_fn('<div class="drawer-mask" id="', did, '-mask" onclick="closeDrawer(\'', did, '\')"></div>')
    a_fn('<div class="drawer" id="', did, '">')
    a_fn('<div class="drawer-head"><span>', title, '</span><button class="close-btn" onclick="closeDrawer(\'', did, '\')">&times;</button></div>')
    a_fn('<div class="drawer-body">', body, '</div>')
    a_fn('</div>')


# ============================================================================
# PRD v2
# ============================================================================
def build_prd():

    NAV = [
        ('\u4ea7\u54c1\u603b\u89c8', [
            ('exec',    '\u6982\u8981\u4e0e\u53cd\u5c65'),
            ('terms',   '\u672f\u8bed\u8868'),
            ('asis',    'AS-IS vs TO-BE'),
            ('goals',   '\u4ea7\u54c1\u76ee\u6807'),
        ]),
        ('\u4e1a\u52a1\u89c4\u5219', [
            ('bizrule',  'SOC_DUAL \u89c4\u5219'),
            ('statemach','\u72b6\u6001\u673a'),
            ('sequence', '\u7aef\u5230\u7aef\u65f6\u5e8f'),
            ('merge',    '\u5e76\u96c6\u7b97\u6cd5'),
        ]),
        ('\u6280\u672f\u8bbe\u8ba1', [
            ('service',  '\u670d\u52a1\u804c\u8d23\u77e9\u9635'),
            ('api_ext',  '\u5bf9\u5916 API \u8be6\u8868'),
            ('api_int',  '\u5185\u90e8 API \u5916\u5305'),
            ('apijson',  'API JSON \u793a\u4f8b'),
            ('kafka',    'Kafka \u4e8b\u4ef6'),
            ('webhook',  'Webhook \u89c4\u683c'),
        ]),
        ('\u6570\u636e\u6a21\u578b', [
            ('er',       'ER \u6982\u89c8'),
            ('fields',   '\u5b57\u6bb5\u8be6\u8868'),
            ('enums',    '\u679a\u4e3e\u8868'),
        ]),
        ('\u5f00\u53d1\u8ba1\u5212', [
            ('nfr',      '\u975e\u529f\u80fd\u9700\u6c42'),
            ('risks',    '\u98ce\u9669\u767b\u8bb0'),
            ('roadmap',  'Wave \u8def\u7ebf\u56fe'),
            ('accept',   '\u9a8c\u6536\u6807\u51c6'),
        ]),
    ]

    def sections(a):
        # -----------------------------------------------------------------------
        # EXEC
        # -----------------------------------------------------------------------
        sec_open(a, 'exec', True)
        card(a, '\u6587\u6863\u5143\u4fe1\u606f', tbl(
            ['\u5c5e\u6027', '\u5185\u5bb9'],
            [
                ['\u540d\u79f0', 'OPEN \u7f16\u6392\u4efb\u52a1 \u00b7 SOC \u53cc\u626b\u5168\u94fe\u8def \u2014 \u4ea7\u54c1\u9700\u6c42\u6587\u6863 v2.0'],
                ['\u72b6\u6001', '<span class="bdg b2">Draft</span>'],
                ['\u65e5\u671f', '2026-06-17'],
                ['\u9002\u7528\u670d\u52a1', 'open-api-service \u00b7 vul-pass \u00b7 vuln-task-center'],
                ['\u529f\u80fd\u7f16\u53f7', 'OPEN-VTC-W0 ~ W4'],
                ['\u8bfb\u8005', '\u540e\u7aef\u5f00\u53d1\u3001\u8054\u8c03\u5de5\u7a0b\u5e08\u3001\u4ea7\u54c1\u7ecf\u7406\u3001\u8fd0\u7ef4'],
            ]))

        card(a, '\u6838\u5fc3\u95ee\u9898\u4e0e\u76ee\u6807',
            al('w', '<strong>\u6838\u5fc3\u75db\u70b9\uff1a</strong>'
               'open-api-service \u5f53\u524d\u901a\u8fc7\u4f2a\u9020 <code>orderId</code> \u8c03\u7528 '
               '<code>POST /vul-scan-task/dispatch</code>\uff0c'
               '\u5bfc\u81f4\uff1a\u2460\u7b2c\u4e09\u65b9\u6570\u636e\u6df7\u5165\u8003\u6838\u5de5\u5355\u8868\uff1b'
               '\u2461 SOC \u63a5\u5165\u65b9\u53cc\u626b\u9700\u6c42\u65e0\u6cd5\u5b9e\u73b0\uff1b'
               '\u2462 Webhook \u56de\u8c03\u4eff Mock\uff1b'
               '\u2463 \u5e73\u53f0\u65e0\u6cd5\u533a\u5206 OPEN/METRIC/ASSESS \u6570\u636e\u6765\u6e90\u3002') +
            tbl(['\u95ee\u9898', '\u5f71\u54cd', '\u89e3\u51b3\u65b9\u5f0f', 'Wave'],
                [
                    ['\u5047 orderId \u6ce1\u6c13\u8003\u6838\u5de5\u5355', '\u8003\u6838\u6743\u76ca\u53d7\u635f / \u5ba1\u8ba1\u5931\u8d25',
                     'open-api \u8c03\u5185\u90e8\u63a5\u53e3 <code>/internal/open/v1/tasks</code>', 'W1c'],
                    ['SOC \u53cc\u626b\u627f\u8bfa\u65e0\u6cd5\u5151\u73b0', 'Partner \u4fe1\u4efb\u4e22\u5931',
                     'vul-pass SOC_DUAL \u8def\u7531\u521b\u5efa 2x survey', 'W1a/b'],
                    ['\u6570\u636e\u6765\u6e90\u4e0d\u6e05', '\u5e38\u6001\u5316\u4e0a\u62a5\u51fa\u9519',
                     'biz_line \u679a\u4e3e\u5168\u9762\u6807\u8bc6', 'W0 \u2713'],
                    ['\u771f\u5b9e Webhook \u7f3a\u5931', 'Partner \u96c6\u6210\u65e0\u6cd5\u81ea\u52a8\u5316',
                     'open-api WebhookDispatcher + vul-pass notify', 'W1c'],
                    ['\u5e76\u96c6\u903b\u8f91\u7f3a\u5931', '\u6f0f\u6d1e\u6f0f\u62a5/\u91cd\u590d',
                     'vul-pass MergeService + dedupKey', 'W1b'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # TERMS
        # -----------------------------------------------------------------------
        sec_open(a, 'terms')
        card(a, '\u672f\u8bed\u8868 / Glossary', tbl(
            ['\u672f\u8bed', '\u5b9a\u4e49', '\u5bf9\u5e94\u5b57\u6bb5'],
            [
                ['Partner', '\u5df2\u5b8c\u6210\u5f00\u901a\u7684\u7b2c\u4e09\u65b9\u7cfb\u7edf\uff08SOC\u3001SIEM\u3001ITSM\u7b49\uff09', 'partner_id'],
                ['SOC_DUAL', '\u53cc\u626b\u7b56\u7565\uff1a\u5c06\u76f8\u540c\u76ee\u6807\u540c\u65f6\u4e0b\u53d1 Nessus + \u7eff\u76df RSAS', 'scan_policy'],
                ['passTaskId', 'vul-pass \u5185\u90e8\u7f16\u6392\u4efb\u52a1\u4e3b\u952e', 'vul_scan_task.id'],
                ['platformTaskId (extTaskId)', 'open-api-service \u4fa7\u751f\u6210\u7684\u4efb\u52a1\u6807\u8bc6\uff0c\u5bf9 Partner \u66b4\u9732', 'open_task.id'],
                ['survey / subTaskId', 'task-center \u6216 vul-pass \u5185\u7684\u5b50\u4efb\u52a1', 'vul_scan_task_sub.id'],
                ['dedupKey', '\u5e76\u96c6\u53bb\u91cd\u952e\uff1a\u8d44\u4ea7IP+\u7aef\u53e3+\u534f\u8bae+\u670d\u52a1+vulId', '\u5185\u90e8\u8ba1\u7b97\u5b57\u6bb5'],
                ['rela_oper', '\u8fd0\u8425\u8f68\uff1a\u771f\u5b9e\u8f68\u8ff9\uff0c\u5199\u5165\u65b9 OPEN/METRIC/PROD', 'vul_inst_log_rela_oper'],
                ['rela_report', '\u4e0a\u62a5\u8f68\uff1a\u90e8\u4fa7\u5408\u89c4\u8f68\u8ff9\uff0c\u5199\u5165\u65b9 ASSESS', 'vul_inst_log_rela_report'],
                ['biz_line', '\u4e1a\u52a1\u7ebf\u679a\u4e3e\uff1aOPEN/METRIC/ASSESS/PROD', 'vul_scan_task.biz_line'],
                ['MergeService', 'vul-pass \u5e76\u96c6\u670d\u52a1\uff1a\u53cc\u626b\u7ed3\u679c dedup \u540e\u5199\u5165 inst', '\u65b0\u5efa\u7c7b'],
                ['OpenTaskOrchestrator', 'vul-pass \u7f16\u6392\u5668\uff1a\u63a5\u6536 Feign \u8c03\u7528\uff0c\u521b\u5efa task + sub', '\u65b0\u5efa\u7c7b'],
                ['WebhookDispatcher', 'open-api \u56de\u8c03\u5206\u53d1\u5668\uff1a\u6307\u6570\u91cd\u8bd5\u3001\u7b7e\u540d', '\u65b0\u5efa\u7c7b'],
                ['SvmpEngineAdapterImpl', 'open-api \u5f15\u64ce\u9002\u914d\u5668\uff1a\u76ee\u524d\u8c03 dispatch\uff0c\u6539\u9020\u540e\u8c03\u5185\u90e8 API', '\u73b0\u6709\u7c7b'],
            ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # AS-IS vs TO-BE
        # -----------------------------------------------------------------------
        sec_open(a, 'asis')
        card(a, 'AS-IS vs TO-BE \u5bf9\u6bd4',
            tbl(['\u7ef4\u5ea6', 'AS-IS (\u73b0\u72b6)', 'TO-BE (\u76ee\u6807)', '\u5f71\u54cd'],
                [
                    ['\u4efb\u52a1\u521b\u5efa\u5165\u53e3',
                     'open-api \u4f2a\u9020 orderId \u8c03 dispatch',
                     'open-api \u8c03 <code>POST /internal/open/v1/tasks</code>',
                     '\u5408\u89c4\u9694\u79bb'],
                    ['\u626b\u63cf\u7b56\u7565',
                     '\u5355\u626b\uff0c\u65e0\u7b56\u7565\u6982\u5ff5',
                     'ScanPolicyEnum\uff1aSOC_DUAL / SINGLE_LM / SINGLE_NES',
                     '\u4e1a\u52a1\u627f\u8bfa'],
                    ['\u53cc\u626b\u652f\u6301',
                     '\u65e0\uff0c\u624b\u52a8\u5de5\u5355\u5408\u5e76',
                     'SOC_DUAL \u81ea\u52a8 2x survey + \u5e76\u96c6\u5165\u5e93',
                     '\u6548\u7387\u63d0\u5347'],
                    ['\u5e76\u96c6\u903b\u8f91',
                     '\u65e0',
                     'MergeService\uff1adedupKey \u53bb\u91cd + \u5b57\u6bb5\u5408\u5e76',
                     '\u6f0f\u6d1e\u5b8c\u6574\u6027'],
                    ['Webhook \u56de\u8c03',
                     'Mock \u56de\u8c03\uff0cPartner \u4e0d\u53ef\u4f18',
                     'WebhookDispatcher + \u6307\u6570\u91cd\u8bd5 + HMAC \u7b7e\u540d',
                     'Partner \u96c6\u6210\u6709\u6548'],
                    ['\u6570\u636e\u6765\u6e90\u6807\u8bc6',
                     '\u65e0 biz_line\uff0cOPEN/ASSESS \u5171\u7528\u8868',
                     'biz_line \u5fc5\u8bbe + \u53cc\u8f68\u5b58\u50a8\u9694\u79bb',
                     '\u4e0a\u62a5\u5ba1\u8ba1\u5408\u89c4'],
                    ['\u6f0f\u6d1e\u5b9e\u4f8b\u72b6\u6001\u673a',
                     '\u53ef\u64cd\u4f5c\u4f46\u65e0 Partner \u4fa7\u5c65\u5386',
                     '\u53cc\u8f68 rela_oper + rela_report \u5b8c\u6574\u8bb0\u5f55',
                     '\u5168\u751f\u547d\u5468\u671f\u53ef\u5ba1'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # GOALS
        # -----------------------------------------------------------------------
        sec_open(a, 'goals')
        a('<div class="grid4">')
        for num, lbl in [('3', 'BizLine \u5168\u652f\u6301'), ('100%', 'SOC_DUAL \u5b9e\u73b0\u7387'), ('0', '\u5047 orderId \u6cc4\u6f0f'), ('&lt;5s', 'Webhook P95')]:
            a('<div class="kpi"><div class="n">', num, '</div><div class="l">', lbl, '</div></div>')
        a('</div>')
        card(a, 'OKR \u8be6\u8868',
            tbl(['OKR ID', '\u76ee\u6807', '\u5f20\u53e3\u8bf4\u660e', '\u53ef\u91cf\u5316\u6307\u6807', 'Wave', '\u8d1f\u8d23\u65b9'],
                [
                    ['O1', '\u5207\u65ad\u5047 orderId', 'SvmpEngineAdapterImpl \u6539\u8c03\u5185\u90e8\u63a5\u53e3',
                     'open-api \u4e0d\u518d\u8c03 /vul-scan-task/dispatch', 'W1c', 'open-api \u540e\u7aef'],
                    ['O2', 'SOC \u53cc\u626b\u5151\u73b0', 'SOC_DUAL \u81ea\u52a8\u521b\u5efa Nessus+\u7eff\u76df \u4e24\u4e2a survey',
                     '\u5168\u91cf SOC Partner 100% \u8d70 SOC_DUAL', 'W1a+W1b', 'vul-pass+vtc \u540e\u7aef'],
                    ['O3', '\u5e76\u96c6\u5165\u5e93\u51c6\u786e', 'MergeService dedup + \u5b57\u6bb5\u5408\u5e76',
                     'dedup \u91cd\u590d\u7387 &lt;1%\uff0c\u6f0f\u62a5\u7387 &lt;0.5%', 'W1b', 'vul-pass \u540e\u7aef'],
                    ['O4', '\u771f\u5b9e Webhook', 'WebhookDispatcher \u6307\u6570\u91cd\u8bd5\uff0cHMAC \u7b7e\u540d',
                     'Webhook \u6295\u9012\u6210\u529f\u7387 &ge;99%', 'W1c', 'open-api \u540e\u7aef'],
                    ['O5', '\u6570\u636e\u6e90\u6e05\u6670', 'biz_line \u5fc5\u9879 + \u53cc\u8f68\u9694\u79bb',
                     'biz_line \u8986\u76d6\u7387 100%', 'W0 \u2713', 'vul-pass \u540e\u7aef'],
                    ['O6', '\u5b9e\u4f8b\u5168\u751f\u547d\u5468\u671f', 'verify/remediate/verify-fix \u5199 rela_oper',
                     'Partner \u6240\u6709\u5199\u64cd\u4f5c\u5747\u8bb0\u5165\u8fd0\u8425\u8f68', 'W2', 'vul-pass \u540e\u7aef'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # BIZ RULES
        # -----------------------------------------------------------------------
        sec_open(a, 'bizrule')
        card(a, 'SOC_DUAL \u4e1a\u52a1\u89c4\u5219',
            al('w', '<strong>SOC \u5f3a\u5236\u5f69\u626f\uff1a</strong>\u6bcf\u4e2a SOC Partner \u7684 <code>scanPolicy</code> \u5fc5\u987b\u4e3a <code>SOC_DUAL</code>\uff0c'
               '\u521b\u5efa\u4efb\u52a1\u65f6\u5982\u672a\u4f20\u6216\u4f20\u5176\u4ed6\u503c\uff0c\u5e73\u53f0\u5f3a\u5236\u8986\u5199\u4e3a SOC_DUAL\u3002') +
            tbl(['\u89c4\u5219\u7f16\u53f7', '\u89c4\u5219', '\u5b9e\u73b0\u4f4d\u7f6e'],
                [
                    ['BR-01', 'SOC Partner \u5fc5\u987b\u7ed1\u5b9a SOC_DUAL\uff0c\u5f3a\u5236\u4e0d\u53ef\u6539\u4e3a SINGLE', 'OpenTaskOrchestrator.validate()'],
                    ['BR-02', '\u5355\u6b21\u4efb\u52a1\u76ee\u6807 IP \u4e0a\u9650 1000 \u4e2a\uff0c\u8d85\u51fa 422', 'open-api \u8bf7\u6c42\u6821\u9a8c'],
                    ['BR-03', 'Nessus \u548c\u7eff\u76df \u5e94\u4f7f\u7528\u76f8\u540c\u626b\u63cf\u76ee\u6807\uff0c\u8054\u7c7b\u626b\u63cf\u6a21\u677f', 'OpenTaskOrchestrator.createSubTasks()'],
                    ['BR-04', '\u53cc survey \u5747\u5b8c\u6210\uff1a\u5468\u671f\u548c\u72b6\u6001\u5747\u6ee1\u8db3\uff0c\u624d\u89e6\u53d1 MergeService', 'vul-pass Kafka Listener'],
                    ['BR-05', '\u5176\u4e2d\u4e00\u4e2a survey FAILED\uff1a\u7236\u4efb\u52a1\u7f6e PARTIAL_FAILED\uff0c\u53ea\u5e76\u96c6\u6210\u529f\u7684\u4e00\u65b9', 'MergeService.merge()'],
                    ['BR-06', 'dedupKey \u51b2\u7a81\u65f6\uff1a\u4fdd\u7559\u4e24\u65b9\u4e2d\u4e25\u91cd\u7b49\u7ea7\u66f4\u9ad8\u8005\uff0c\u5176\u4f59\u5b57\u6bb5\u53d6\u5e76\u96c6', 'MergeService.dedup()'],
                    ['BR-07', 'Webhook \u56de\u8c03\u65f6\u673a\uff1a MergeService \u5199\u5165 rela_oper \u5b8c\u6210 \u540e\u624d notify', 'vul-pass notify Feign'],
                    ['BR-08', '\u6bcf\u4e2a Partner \u6570\u636e\u6c90\u6c90\u5c42\u9694\u79bb\uff0c\u4e0d\u540c Partner \u53ef\u4e0d\u80fd\u5171\u4eab\u5b9e\u4f8b\u6216\u4efb\u52a1', 'open-api Domain \u5c42'],
                    ['BR-09', 'verify-fix \u5355\u5382\u5546\u5168\u91cf\u590d\u626b\uff1b\u4ec5\u76ee\u6807 vulInfoID \u5224\u5b9a 6/7/10', 'VerifyFixOrchestrator + VerifyFixRecycleHandler'],
                ]))
        card(a, '\u4e09\u5927\u4e1a\u52a1\u53d1\u8d77\u65b9\u5bf9\u6bd4',
            tbl(['\u7ef4\u5ea6', 'OPEN (SOC)', 'METRIC (\u6307\u6807)', 'ASSESS (\u8003\u6838)'],
                [
                    ['\u5165\u53e3', 'REST API /api/open/v1', 'Feign \u5185\u90e8\u8c03\u7528', '\u90e8\u4fa7\u5de5\u5355 dispatch()'],
                    ['biz_line', 'OPEN', 'METRIC', 'ASSESS'],
                    ['scan_policy', 'SOC_DUAL (\u5f3a\u5236)', '\u6307\u5b9a\u6a21\u677f', '\u5382\u5546\u7531\u5de5\u5355\u786e\u5b9a'],
                    ['\u5199\u5165\u8f68\u9053', 'rela_oper (\u8fd0\u8425\u8f68)', 'rela_oper', 'rela_report (\u4e0a\u62a5\u8f68)'],
                    ['Webhook', '\u6709\uff0c\u771f\u5b9e\u56de\u8c03', '\u65e0', '\u65e0\uff0c\u5185\u90e8\u9a71\u52a8'],
                    ['orderId', '\u65e0\uff08\u5207\u65ad\uff09', '\u65e0', '\u6709\uff08\u8003\u6838\u5de5\u5355\u5fc5\u987b\uff09'],
                    ['\u5e76\u96c6\u4eba\u5de5', 'MergeService \u81ea\u52a8', 'N/A', 'N/A'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # STATE MACHINES
        # -----------------------------------------------------------------------
        sec_open(a, 'statemach')
        card(a, 'open_task \u4efb\u52a1\u72b6\u6001\u673a',
            tbl(['\u72b6\u6001', '\u8bf4\u660e', '\u524d\u7f6e\u72b6\u6001', '\u8f6c\u79fb\u89e6\u53d1'],
                [
                    ['PENDING', '\u5df2\u63a5\u6536\uff0c\u5c1a\u672a\u4e0b\u53d1 survey', '-', 'open-api \u63a5\u53d7 POST \u8bf7\u6c42'],
                    ['RUNNING', 'vul-pass \u5df2\u521b\u5efa\u5e76\u4e0b\u53d1', 'PENDING', 'CreateOpenTaskResponse.ACCEPTED'],
                    ['PARTIAL_FAILED', '\u4e00\u4e2a survey \u5931\u8d25\uff0c\u53e6\u4e00\u4e2a\u7ee7\u7eed', 'RUNNING', 'Kafka: open.task.sub.failed (one)'],
                    ['FINISHED', '\u53cc survey \u5747\u5b8c\u6210\uff0c\u5e76\u96c6\u5165\u5e93', 'RUNNING|PARTIAL_FAILED', 'vul-pass notify FINISHED'],
                    ['FAILED', '\u53cc\u65b9\u5747\u5931\u8d25\u6216\u6d41\u7a0b\u5f02\u5e38', 'RUNNING', 'Kafka: open.task.sub.failed (both)'],
                ]) +
            sm(
                'PENDING\n'
                '  |\n'
                '  v (vul-pass ACCEPTED)\n'
                'RUNNING\n'
                '  |            \\\n'
                '  v             v\n'
                'PARTIAL_FAILED  |\n'
                '  |             |\n'
                '  v             v\n'
                'FINISHED <--- (both surveys done)\n'
                'FAILED   <--- (both surveys failed)'
            ))
        card(a, 'vul_scan_task_sub \u5b50\u4efb\u52a1\u72b6\u6001\u673a',
            tbl(['\u72b6\u6001', '\u8bf4\u660e', '\u626b\u63cf\u5668\u5bf9\u5e94'],
                [
                    ['PENDING', '\u5c1a\u672a\u4e0b\u53d1\u5230 task-center', '-'],
                    ['DISPATCHED', '\u5df2\u4e0b\u53d1\uff0c\u7b49\u5f85\u5f15\u64ce\u54cd\u5e94', 'task-center \u6536\u5230\u8bf7\u6c42'],
                    ['RUNNING', '\u5f15\u64ce\u6b63\u5728\u6267\u884c', 'Nessus/LM RUNNING'],
                    ['FINISHED', '\u5f15\u64ce\u5b8c\u6210\uff0c\u7ed3\u679c\u5df2\u53ef\u8bfb\u53d6', 'Nessus/LM FINISHED'],
                    ['FAILED', '\u5f15\u64ce\u5931\u8d25\u6216\u8d85\u65f6', 'Nessus/LM ERROR'],
                    ['TIMEOUT', '\u8d85\u65f6\u65e0\u54cd\u5e94', '\u5e73\u53f0\u76d1\u63a7\u89e6\u53d1'],
                ]))
        card(a, '\u5e76\u96c6\u95e8\u7981 (Merge Gate)',
            al('i', '\u4e24\u4e2a sub \u5747\u5b8c\u6210\u540e\uff0c\u624d\u89e6\u53d1 MergeService\u3002\u8f6c\u6362\u8868\u5982\u4e0b\uff1a') +
            tbl(['Nessus', '\u7eff\u76df', '\u7236\u4efb\u52a1\u72b6\u6001', '\u52a8\u4f5c'],
                [
                    ['FINISHED', 'FINISHED', 'RUNNING \u2192 FINISHED', 'MergeService.merge()'],
                    ['FINISHED', 'FAILED', 'RUNNING \u2192 PARTIAL_FAILED', 'MergeService.mergeSingle(Nessus)'],
                    ['FAILED', 'FINISHED', 'RUNNING \u2192 PARTIAL_FAILED', 'MergeService.mergeSingle(LM)'],
                    ['FAILED', 'FAILED', 'RUNNING \u2192 FAILED', '\u4e0d\u8fdb\u884c\u5e76\u96c6\uff0c\u76f4\u63a5 notify FAILED'],
                    ['TIMEOUT', '\u4e3b\u52a8\u8fbe\u5230', 'RUNNING \u2192 PARTIAL_FAILED', '\u8d85\u65f6\u626b\u63cf\u5668 FAILED \u5904\u7406'],
                ]))
        card(a, 'VulInfoStat \u6f0f\u6d1e\u5b9e\u4f8b\u72b6\u6001\u673a',
            tbl(['code', 'VulStateEnum', '\u5c40\u9648', 'Partner \u53ef\u64cd\u4f5c'],
                [
                    ['1', 'INITIAL_DISCOVERY', '\u521d\u59cb\u53d1\u73b0', 'verify / remediate'],
                    ['2', 'VALIDATED_TRUE', '\u5df2\u9a8c\u8bc1\u6709\u6548', 'remediate'],
                    ['3', 'VALIDATED_FALSE', '\u5df2\u9a8c\u8bc1\u8bef\u62a5 (\u7ec8\u6001)', '\u65e0'],
                    ['5', 'FIXED', '\u5df2\u4fee\u590d', 'verify-fix'],
                    ['6', 'VERIFIED_FIXED', '\u6838\u9a8c\u4fee\u590d (\u7ec8\u6001)', '\u65e0'],
                    ['7', 'VERIFIED_UNFIXED', '\u6838\u9a8c\u672a\u4fee\u590d', 'remediate / verify-fix'],
                    ['9', 'FIX_FAILED', '\u4fee\u590d\u5931\u8d25/\u5907\u6848', '\u4e0d\u53ef\u518d\u64cd\u4f5c'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # SEQUENCE
        # -----------------------------------------------------------------------
        sec_open(a, 'sequence')
        card(a, '\u521b\u5efa SOC_DUAL \u4efb\u52a1 \u2014 \u7aef\u5230\u7aef\u65f6\u5e8f',
            tbl(['\u6b65\u9aa4', '\u53d1\u8d77\u65b9', '\u8c03\u7528\u65b9', '\u52a8\u4f5c', '\u4e3b\u8981\u5b57\u6bb5'],
                [
                    ['1', 'Partner', 'partner-gateway', 'POST /api/open/v1/tasks/vul', 'Authorization: Bearer {token}'],
                    ['2', 'partner-gateway', 'open-api-service', '\u9c13\u6743\u6821\u9a8c + \u6ce8\u5165 X-Partner-Id', '\u80fd\u529b\u7801 TASK_CREATE \u6821\u9a8c'],
                    ['3', 'open-api', 'open-api DB', '\u5199\u5165 open_task (PENDING)', 'scan_policy=SOC_DUAL'],
                    ['4', 'open-api', 'vul-pass Feign', 'POST /internal/open/v1/tasks', 'CreateOpenTaskRequest (partnerId, extTaskId, targets, policy)'],
                    ['5', 'vul-pass', 'vul-pass DB', '\u5199\u5165 vul_scan_task (biz_line=OPEN)', 'partner_id, scan_policy'],
                    ['6', 'vul-pass OpenTaskOrchestrator', 'vuln-task-center', 'POST survey (Nessus) + POST survey (\u7eff\u76df)', 'scan_template_id, target hosts'],
                    ['7', 'vul-pass', 'vul-pass DB', '\u5199\u5165 vul_scan_task_sub x2', 'scanner_vendor=NESSUS/LM, external_survey_id'],
                    ['8', 'vul-pass', 'open-api Feign', 'CreateOpenTaskResponse', 'passTaskId, subTasks[]'],
                    ['9', 'open-api', 'open-api DB', '\u66f4\u65b0 open_task (RUNNING, passTaskId)', ''],
                    ['10', 'open-api', 'Partner', 'HTTP 200: {taskId, status: "ACCEPTED"}', ''],
                ]) +
            al('i', '\u6b65\u9aa4 4~9 \u5728\u540c\u4e00 HTTP \u8bf7\u6c42\u5185\u540c\u6b65\u5b8c\u6210\uff1b\u5982 vul-pass \u8d85\u65f6\uff0c open-api \u8fd4\u56de 503\u3002'))
        card(a, '\u53cc\u626b\u5b8c\u6210 \u2192 \u5e76\u96c6 \u2192 Webhook \u65f6\u5e8f',
            tbl(['\u6b65\u9aa4', '\u53d1\u8d77\u65b9', '\u8c03\u7528\u65b9', '\u52a8\u4f5c'],
                [
                    ['A1', 'Nessus', 'vuln-task-center', '\u626b\u63cf\u5b8c\u6210\u56de\u8c03'],
                    ['A2', 'vuln-task-center', 'Kafka', 'topic: open.task.sub.finished {subTaskId, vendor=NESSUS, vulns=[]}'],
                    ['A3', '\u7eff\u76df RSAS', 'vuln-task-center', '\u626b\u63cf\u5b8c\u6210\u56de\u8c03'],
                    ['A4', 'vuln-task-center', 'Kafka', 'topic: open.task.sub.finished {subTaskId, vendor=LM, vulns=[]}'],
                    ['A5', 'vul-pass MergeGateListener', 'vul-pass DB', '\u66f4\u65b0 vul_scan_task_sub.status=FINISHED'],
                    ['A6', 'MergeGateListener', '\u5185\u90e8\u68c0\u67e5', '\u68c0\u67e5\u53cc sub \u662f\u5426\u5747\u5b8c\u6210'],
                    ['A7', 'vul-pass MergeService', 'vul-pass DB', 'dedup \u5e76\u96c6 \u2192 \u5199\u5165 vul_archive_inst (data_origin=OPEN)'],
                    ['A8', 'MergeService', 'vul-pass DB', '\u5199\u5165 vul_inst_log_rela_oper \u8fd0\u8425\u8f68'],
                    ['A9', 'vul-pass', 'open-api Feign', 'POST /internal/open/v1/tasks/{passTaskId}/notify'],
                    ['A10', 'open-api WebhookDispatcher', 'open-api DB', '\u66f4\u65b0 open_task.status=FINISHED'],
                    ['A11', 'WebhookDispatcher', 'Partner callbackUrl', 'POST TASK_COMPLETED {taskId, mergedCount, vulCount}'],
                ]))
        card(a, '\u4fee\u590d\u6838\u9a8c verify-fix \u65f6\u5e8f (\u00a75.5)',
            al('i', 'Partner \u4e3b\u52a8\u53d1\u8d77\uff1b\u590d\u7528\u6700\u8fd1 <code>scanner_vendor</code> \u5355 survey <strong>\u5168\u91cf\u626b\u63cf</strong>\uff1b\u56de\u6536\u540e\u4ec5\u5224\u5b9a\u76ee\u6807 <code>vulInfoID</code>\u3002') +
            tbl(['\u6b65\u9aa4', '\u53d1\u8d77\u65b9', '\u52a8\u4f5c'],
                [
                    ['V1', 'Partner', 'POST /instances/{vulInfoID}/verify-fix (stat=5)'],
                    ['V2', 'open-api', 'Feign verify-fix internal API'],
                    ['V3', 'vul-pass', '\u89e3\u6790 vulInfoID -> assetIp + \u6700\u8fd1 scanner_vendor'],
                    ['V4', 'vul-pass', '\u521b\u5efa tsk_scn=VERIFY_FIX, scan_policy=SINGLE'],
                    ['V5', 'vuln-task-center', '\u5168\u91cf survey\uff08\u4e0d\u6307\u5b9a\u4ea7\u54c1\u6f0f\u6d1e\uff09'],
                    ['V6', 'vul-pass', '\u5168\u91cf recycle\uff1b\u4ec5\u76ee\u6807\u6f0f\u6d1e: \u672a\u68c0\u51fa->6, \u4ecd\u68c0\u51fa->7'],
                    ['V7', 'open-api', 'INSTANCE_VERIFY_FIX_COMPLETED + EXPORT_READY(VERIFY_FIX_SCAN)'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # MERGE ALGORITHM
        # -----------------------------------------------------------------------
        sec_open(a, 'merge')
        card(a, '\u5e76\u96c6\u7b97\u6cd5\u8be6\u8bf4',
            al('i', '<strong>dedupKey \u516c\u5f0f\uff1a</strong> <code>sha256(assetIp + ":" + port + ":" + protocol + ":" + service + ":" + vulId)</code>') +
            tbl(['\u6b65\u9aa4', '\u64cd\u4f5c', '\u5b9e\u73b0\u7c7b'],
                [
                    ['1', '\u6536\u5230\u53cc\u65b9\u7ed3\u679c\u5217\u8868 (Nessus vulns[] + LM vulns[])', 'MergeService.merge()'],
                    ['2', '\u5bf9\u6bcf\u4e2a\u6f0f\u6d1e\u8ba1\u7b97 dedupKey', 'VulnDeduplicator.computeKey()'],
                    ['3', '\u6309 dedupKey \u5efa\u7acb HashMap', 'VulnDeduplicator.buildMap()'],
                    ['4', '\u9047\u5230\u51b2\u7a81\uff1a\u6bd4\u8f83\u4e24\u65b9 severity\uff0c\u4fdd\u7559\u4e25\u91cd\u7b49\u7ea7\u66f4\u9ad8\u8005', 'MergeConflictResolver.resolve()'],
                    ['5', '\u975e\u51b2\u7a81\u5b57\u6bb5\uff1a\u53d6\u5e76\u96c6\uff08\u5982 fixLnk \u53d6\u4e24\u8005\u90fd\u6709\u5c31\u62fc\u63a5\uff09', 'MergeConflictResolver.mergeFields()'],
                    ['6', '\u5e76\u96c6\u7ed3\u679c\u5199\u5165 vul_archive_inst (data_origin=OPEN)', 'VulArchiveInstRepository.batchUpsert()'],
                    ['7', '\u5199\u5165 vul_inst_log_rela_oper (biz_line=OPEN, \u53cc\u8f68)', 'RelaOperRepository.batchInsert()'],
                ]) +
            tbl(['\u5b57\u6bb5\u51b2\u7a81\u89c4\u5219', '\u89c4\u5219\u8bf4\u660e'],
                [
                    ['severity / riskLevel', '\u4fdd\u7559\u66f4\u9ad8\u8005'],
                    ['cvssScore', '\u4fdd\u7559\u8f83\u9ad8\u8005'],
                    ['remedDesc / fixLnk', '\u4e24\u65b9\u5747\u6709\u5219\u62fc\u63a5\uff0c\u4ec5\u4e00\u65b9\u6709\u5219\u4fdd\u7559'],
                    ['vulInstCpe / vulInstVer', '\u53d6 Nessus \u7ed3\u679c\u4f18\u5148'],
                    ['scannerVendors', '\u8bb0\u5f55\u4e24\u65b9\u626b\u63cf\u5668 [NESSUS, LM]'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # SERVICE RESPONSIBILITY
        # -----------------------------------------------------------------------
        sec_open(a, 'service')
        card(a, '\u670d\u52a1\u804c\u8d23\u77e9\u9635',
            tbl(['\u670d\u52a1', '\u7c7b/\u6a21\u5757', '\u804c\u8d23', 'Wave'],
                [
                    ['open-api-service', 'SvmpEngineAdapterImpl (\u6539\u9020)', '\u5c06 Partner POST /tasks/vul \u6620\u5c04\u4e3a /internal/open/v1/tasks Feign \u8c03\u7528\uff0c\u5207\u65ad\u5047 orderId', 'W1c'],
                    ['open-api-service', 'WebhookDispatcher (\u65b0\u5efa)', '\u63a5\u53d7 vul-pass notify\uff0c\u6307\u6570\u91cd\u8bd5\u5e7f\u64ad TASK_COMPLETED\uff0c HMAC \u7b7e\u540d', 'W1c'],
                    ['open-api-service', 'OpenApiPartnerFilter', 'partner_id \u9694\u79bb\u6821\u9a8c\uff0c X-Partner-Id \u6ce8\u5165', '\u5df2\u6709'],
                    ['vul-pass', 'OpenTaskOrchestrator (\u65b0\u5efa)', '\u63a5\u6536 Feign \u8bf7\u6c42\uff0c\u521b\u5efa vul_scan_task + 2x vul_scan_task_sub\uff0c\u8c03 task-center', 'W1b'],
                    ['vul-pass', 'MergeService (\u65b0\u5efa)', '\u53d7 Kafka \u4e8b\u4ef6\u9a71\u52a8\uff0c dedup \u5e76\u96c6 \u2192 vul_archive_inst + rela_oper', 'W1b'],
                    ['vul-pass', 'MergeGateListener (\u65b0\u5efa)', '\u76d1\u542c open.task.sub.finished\uff0c\u68c0\u67e5\u4e24\u4e2a sub \u5747\u5b8c\u6210\u540e\u89e6\u53d1 Merge', 'W1b'],
                    ['vul-pass', 'OpenTaskInternalController (\u65b0\u5efa)', '\u63d0\u4f9b /internal/open/v1/tasks GET/POST/notify', 'W1b'],
                    ['vuln-task-center', 'ScanPolicyRouter (\u65b0\u5efa)', '\u6839\u636e scan_policy \u88c1\u5b9a\u626b\u63cf\u5668\u7ec4\u5408\uff0c SOC_DUAL \u8f93\u51fa [NESSUS, LM]', 'W1a'],
                    ['vuln-task-center', 'ScannerAdapter-NESSUS', '\u5bf9\u63a5 Nessus REST API\uff0c\u521b\u5efa/\u67e5\u8be2\u626b\u63cf\u4efb\u52a1', '\u5df2\u6709'],
                    ['vuln-task-center', 'ScannerAdapter-LM', '\u5bf9\u63a5\u7eff\u76df RSAS API V6\uff0c\u521b\u5efa/\u67e5\u8be2\u626b\u63cf\u4efb\u52a1', '\u5df2\u6709'],
                    ['vul-pass', 'VerifyFixOrchestrator (\u65b0\u5efa)', 'verify-fix: \u89e3\u6790 vulInfoID/assetIp/scanner_vendor \u2192 SINGLE \u5168\u91cf\u4e0b\u53d1', 'W3'],
                    ['vul-pass', 'VerifyFixRecycleHandler (\u65b0\u5efa)', '\u5168\u91cf\u56de\u6536\uff1b\u4ec5\u76ee\u6807 vulInfoID \u5224\u5b9a 6/7/10', 'W3'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # API EXT
        # -----------------------------------------------------------------------
        sec_open(a, 'api_ext')
        card(a, '\u5bf9\u5916 API \u5b57\u6bb5\u6620\u5c04\u8be6\u8868 (POST /api/open/v1/tasks/vul)',
            al('i', 'Partner \u8bf7\u6c42\u5b57\u6bb5 \u2192 open-api DTO \u2192 \u5185\u90e8 Feign \u8bf7\u6c42\u5b57\u6bb5\u5168\u8def\u5c55\u5f00\u3002') +
            tbl(['\u4e2d\u6587\u8bed\u4e49', 'Partner \u8bf7\u6c42\u5b57\u6bb5', '\u7c7b\u578b/\u7ea6\u675f', 'open-api DTO \u5b57\u6bb5', 'Feign \u8bf7\u6c42\u5b57\u6bb5', '\u5907\u6ce8'],
                [
                    ['\u4efb\u52a1\u540d\u79f0', 'taskName', 'string, \u5fc5\u586b, max 128', 'taskName', 'taskName', ''],
                    ['\u6f0f\u6d1e\u7c7b\u578b', 'vulnType', 'int: 1=\u7cfb\u7edf 2=Web 3=\u5f31\u53e3\u4ee4', 'vulnType', 'vulnType', '\u51b3\u5b9a\u626b\u63cf\u6a21\u677f'],
                    ['\u626b\u63cf\u76ee\u6807', 'targets.hosts', 'string, \u9017\u53f7\u6216\u5206\u53f7\u5206\u9694, \u6700\u591a 1000 IP', 'targets.hosts', 'targets.hosts', ''],
                    ['\u8ba4\u8bc1\u4fe1\u606f', 'targets.auth[]', 'array, \u53ef\u9009', 'targets.auth', 'targets.auth', '\u5c31\u4f20 task-center'],
                    ['\u626b\u63cf\u7b56\u7565', 'scanPolicy', 'string, SOC \u5fc5\u987b SOC_DUAL', 'scanPolicy', 'scanPolicy', '\u5f3a\u5236\u8986\u5199'],
                    ['\u56de\u8c03\u5730\u5740', 'callbackUrl', 'string, \u53ef\u9009', 'callbackUrl', '\u5b58 open_task.callback_url', '\u5b58\u5728 open-api \u4fa7'],
                    ['\u5904\u7f6e\u65b9\u5f0f', 'srcMethod', 'int, \u53ef\u9009', 'srcMethod', 'srcMethod', '\u7ee7\u627f\u81f3\u5b9e\u4f8b'],
                    ['\u626b\u63cf\u6a21\u677f', 'file.\u6a21\u677f\u7f16\u53f7', 'int, \u53ef\u9009', '\u9ed8\u8ba4\u6a21\u677f', 'scanTemplateId', 'vulnType \u6620\u5c04'],
                ]))
        card(a, '\u5bf9\u5916 API \u8fd4\u56de\u5b57\u6bb5 (createTask Response)',
            tbl(['\u5b57\u6bb5', '\u7c7b\u578b', '\u8bf4\u660e'],
                [
                    ['taskId', 'string', 'open-api \u4fa7\u4efb\u52a1\u6807\u8bc6\uff0c\u5bf9 Partner \u66b4\u9732\uff0c\u4e0d\u6697\u793a vul-pass \u5185\u90e8 ID'],
                    ['status', 'string', 'ACCEPTED | REJECTED'],
                    ['message', 'string', '\u9519\u8bef\u8bf4\u660e\uff08REJECTED \u65f6\uff09'],
                    ['createdAt', 'ISO8601', '\u521b\u5efa\u65f6\u95f4'],
                ]))
        card(a, '\u5b9e\u4f8b\u57df\u5199\u63a5\u53e3\u6620\u5c04',
            al('i', '\u6838\u5fc3\u673a\u5236\uff1avul-pass PUT \u5355\u627f\u63a5\u53e3\uff0c\u5199\u64cd\u4f5c\u5fc5\u987b\u5148 GET \u5f97\u5230\u5185\u90e8 id\uff0c\u518d\u62baPUT\u3002') +
            tbl(['Partner \u8def\u5f84', 'open-api operationId', 'vul-pass \u63a5\u53e3', '\u4e3b\u8981\u8868\u5199\u5b57\u6bb5'],
                [
                    ['POST .../verify', 'verifyInstance', 'GET page \u53d6 id \u2192 PUT /vul-scan-task-sub-system', 'vulInfoStat=2 (\u6709\u6548) \u6216 3 (\u8bef\u62a5)'],
                    ['POST .../remediate', 'remediateInstance', '\u540c\u4e0a', 'vulInfoStat=5, method, remedDesc'],
                    ['POST .../verify-fix', 'verifyFixInstance', 'POST /internal/open/v1/instances/{id}/verify-fix', '\u53d7\u7406 stat=5\uff1b\u5f02\u6b65\u5168\u91cf\u590d\u626b\u540e 6/7/10'],
                    ['\u6279\u91cf verify', 'verifyInstanceBatch', 'Domain \u5c42\u5faa\u73af\u5355\u6761', '\u8fd4\u56de success/failed \u6c47\u603b'],
                    ['\u6279\u91cf remediate', 'remediateInstanceBatch', '\u540c\u4e0a', '\u540c\u4e0a'],
                    ['\u6279\u91cf verify-fix', 'verifyFixInstanceBatch', '\u540c\u4e0a', '\u540c\u4e0a'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # API INT (internal API contract)
        # -----------------------------------------------------------------------
        sec_open(a, 'api_int')
        card(a, 'Internal API \u5916\u5305 \u2014 \u5b8c\u6574\u8def\u5f84\u4e0e\u5b57\u6bb5',
            tbl(['\u65b9\u6cd5', '\u8def\u5f84', '\u8bf7\u6c42\u5173\u952e\u5b57\u6bb5', '\u54cd\u5e94\u5173\u952e\u5b57\u6bb5', 'Wave'],
                [
                    ['POST', '/internal/open/v1/tasks',
                     'partnerId, platformTaskId, extTaskId, taskName, vulnType, targets{hosts,auth[]}, scanPolicy, scanTemplateId, reportTemplateId, srcMethod, callbackUrl',
                     'passTaskId(Long), status(ACCEPTED|REJECTED), subTasks[]{subTaskId, scannerVendor, externalSurveyId}, message',
                     'W1b'],
                    ['GET', '/internal/open/v1/tasks/{passTaskId}',
                     'passTaskId (path)',
                     'passTaskId, status(PENDING|RUNNING|FINISHED|FAILED|PARTIAL_FAILED), progress(0-100), subTasks[]{subTaskId, scannerVendor, status, progress}, finishedAt',
                     'W1b'],
                    ['POST', '/internal/open/v1/tasks/{passTaskId}/notify',
                     'passTaskId (path), status(FINISHED|FAILED|PARTIAL_FAILED), platformTaskId, summary{totalInstances, verifiedValid, falsePositive}, errorMessage',
                     'code, msg',
                     'W1c'],
                ]) +
            al('w', '/internal/** \u8def\u7531\u5728 partner-gateway \u5c42 401 \u62e6\u622a\uff0c\u4ec5\u5185\u7f51 Feign \u53ef\u8bbf\u3002'))
        sec_close(a)

        # -----------------------------------------------------------------------
        # API JSON EXAMPLES
        # -----------------------------------------------------------------------
        sec_open(a, 'apijson')
        card(a, 'POST /api/open/v1/tasks/vul \u8bf7\u6c42\u793a\u4f8b',
            fc(
                '// Partner \u53d1\u8d77\n'
                'POST /api/open/v1/tasks/vul HTTP/1.1\n'
                'Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...\n'
                'Content-Type: application/json\n\n'
                '{\n'
                '  "taskName": "2026Q2-\u6838\u5fc3\u4e1a\u52a1\u6392\u67e5",\n'
                '  "vulnType": 1,\n'
                '  "targets": {\n'
                '    "hosts": "10.10.1.2,10.10.1.3,10.10.1.4",\n'
                '    "auth": [{"ip":"10.10.1.2","protocol":"ssh","port":22,"username":"admin","password":"xxx"}]\n'
                '  },\n'
                '  "scanPolicy": "SOC_DUAL",\n'
                '  "callbackUrl": "https://soc.example.com/hooks/vuln",\n'
                '  "srcMethod": 1\n'
                '}'))
        card(a, 'POST /internal/open/v1/tasks \u8bf7\u6c42\u793a\u4f8b (Feign)',
            fc(
                '// open-api \u8f6c\u53d1\u7ed9 vul-pass\n'
                '{\n'
                '  "partnerId": "SOC-CLIENT-A",\n'
                '  "platformTaskId": "TASK-7f3a2b1c",\n'
                '  "extTaskId": "ext-20260616-001",\n'
                '  "taskName": "2026Q2-\u6838\u5fc3\u4e1a\u52a1\u6392\u67e5",\n'
                '  "vulnType": 1,\n'
                '  "targets": { "hosts": "10.10.1.2,10.10.1.3,10.10.1.4" },\n'
                '  "scanPolicy": "SOC_DUAL",\n'
                '  "scanTemplateId": 101,\n'
                '  "callbackUrl": "https://soc.example.com/hooks/vuln"\n'
                '}'))
        card(a, '\u521b\u5efa\u4efb\u52a1\u54cd\u5e94 \u4e0e Webhook \u8d1f\u8f7d',
            fc(
                '// POST /internal/open/v1/tasks \u54cd\u5e94\n'
                '{\n'
                '  "passTaskId": 10086001,\n'
                '  "status": "ACCEPTED",\n'
                '  "subTasks": [\n'
                '    {"subTaskId": 2001, "scannerVendor": "NESSUS", "externalSurveyId": "SV-NES-001"},\n'
                '    {"subTaskId": 2002, "scannerVendor": "LM",     "externalSurveyId": "SV-LM-002"}\n'
                '  ]\n'
                '}\n\n'
                '// TASK_COMPLETED Webhook \u8d1f\u8f7d\n'
                'POST https://soc.example.com/hooks/vuln\n'
                'X-ESMP-Signature: sha256=abc123...\n'
                'Content-Type: application/json\n\n'
                '{\n'
                '  "eventType": "TASK_COMPLETED",\n'
                '  "taskId": "TASK-7f3a2b1c",\n'
                '  "mergedCount": 51,\n'
                '  "vulCount": {"nessus": 42, "lm": 38},\n'
                '  "status": "FINISHED",\n'
                '  "finishedAt": "2026-06-16T20:30:00Z"\n'
                '}'))
        sec_close(a)

        # -----------------------------------------------------------------------
        # KAFKA
        # -----------------------------------------------------------------------
        sec_open(a, 'kafka')
        card(a, 'Kafka Topic \u8bbe\u8ba1',
            tbl(['Topic', '\u751f\u4ea7\u8005', '\u6d88\u8d39\u8005', 'key', 'payload \u4e3b\u8981\u5b57\u6bb5'],
                [
                    ['open.task.sub.finished', 'vuln-task-center', 'vul-pass MergeGateListener',
                     'passTaskId', '{passTaskId, subTaskId, vendor, status, vulns[]}'],
                    ['open.task.sub.failed', 'vuln-task-center', 'vul-pass MergeGateListener',
                     'passTaskId', '{passTaskId, subTaskId, vendor, errorCode, errorMsg}'],
                    ['open.task.merge.ready', 'vul-pass MergeGateListener', 'vul-pass MergeService',
                     'passTaskId', '{passTaskId, readySubs[], failedSubs[]}'],
                ]) +
            al('i', 'consumer group \u5efamen\u8bae\uff1a<code>open-task-merge-group</code>\uff0c\u5206\u533a\u6570 3\uff0c\u5e02\u5ea6 earliest\u3002'))
        sec_close(a)

        # -----------------------------------------------------------------------
        # WEBHOOK
        # -----------------------------------------------------------------------
        sec_open(a, 'webhook')
        card(a, 'Webhook \u89c4\u683c\u8be6\u8868',
            tbl(['\u9879\u76ee', '\u5185\u5bb9'],
                [
                    ['\u5730\u5740\u7c7b\u578b', 'Partner \u63d0\u4f9b\u7684 HTTPS callbackUrl'],
                    ['\u91cd\u8bd5\u7b56\u7565', '\u6307\u6570\u9000\u907f: 1s / 5s / 30s / 120s / 600s\uff0c\u5171 5 \u6b21\uff1b\u5168\u90e8\u5931\u8d25\u8fdb\u6b7b\u4fe1\u961f\u5217'],
                    ['\u7b7e\u540d\u65b9\u5f0f', 'X-ESMP-Signature: sha256={HMAC-SHA256(body, partnerSecret)}'],
                    ['\u8bf7\u6c42\u65b9\u6cd5', 'POST application/json'],
                    ['\u8d85\u65f6', '\u5355\u6b21\u8bf7\u6c42 10s'],
                    ['\u5e42\u7b49\u6027', '\u91cd\u8bd5\u65f6 eventType+taskId \u5c31\u662f\u5e42\u7b49\u952e\uff0cPartner \u5e94\u81ea\u884c\u53bb\u91cd'],
                ]) +
            tbl(['eventType', '\u89e6\u53d1\u65f6\u673a', '\u5173\u952e payload \u5b57\u6bb5'],
                [
                    ['TASK_COMPLETED', '\u5e76\u96c6\u5165\u5e93\u5b8c\u6210', 'taskId, mergedCount, vulCount{nessus,lm}, status, finishedAt'],
                    ['TASK_FAILED', '\u4efb\u52a1\u5f02\u5e38\u7ec8\u6b62', 'taskId, errorCode, errorMsg'],
                    ['PARTIAL_FAILED', '\u5176\u4e2d\u4e00\u626b\u63cf\u5668\u5931\u8d25', 'taskId, failedVendor, mergedCount'],
                    ['EXPORT_READY', 'TaskExport \u5c31\u7eea', 'taskId, downloadUrl, format, expiresAt'],
                    ['INSTANCE_UPDATED', '\u5b9e\u4f8b\u72b6\u6001\u53d8\u66f4', 'taskId, vulInfoId, oldStat, newStat'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # ER
        # -----------------------------------------------------------------------
        sec_open(a, 'er')
        card(a, 'ER \u6982\u89c8 (Wave 0 \u5df2\u5b9e\u73b0)',
            sm(
                'open_task\n'
                '  id (BIGINT PK)                -- platformTaskId\n'
                '  partner_id   VARCHAR(64)\n'
                '  scan_policy  VARCHAR(20)       -- SOC_DUAL default\n'
                '  pass_task_id BIGINT            -- FK -> vul_scan_task.id (Wave 1b \u540e\u586b\u5199)\n'
                '  callback_url VARCHAR(512)\n'
                '  status       VARCHAR(20)       -- PENDING/RUNNING/FINISHED/FAILED\n'
                '  external_task_id VARCHAR(64)\n'
                '  create_time  DATETIME\n\n'
                'vul_scan_task  (biz_line \u6269\u5c55)\n'
                '  id (BIGINT PK)                -- passTaskId\n'
                '  biz_line     VARCHAR(20)       -- OPEN/METRIC/ASSESS/PROD [NEW]\n'
                '  data_origin  VARCHAR(20)       -- [NEW]\n'
                '  scan_policy  VARCHAR(20)       -- [NEW]\n'
                '  partner_id   VARCHAR(64)       -- [NEW]\n'
                '  external_task_id VARCHAR(64)   -- [NEW]\n'
                '  order_id     BIGINT NULL       -- ASSESS \u65f6\u53ef\u586b\n\n'
                'vul_scan_task_sub  (scanner_vendor \u6269\u5c55)\n'
                '  id (BIGINT PK)                -- subTaskId\n'
                '  scan_task_id BIGINT            -- FK -> vul_scan_task.id\n'
                '  scanner_vendor VARCHAR(20)     -- NESSUS/LM/AH [NEW]\n'
                '  external_survey_id VARCHAR(64) -- task-center \u5185\u90e8 id [NEW]\n'
                '  order_id     BIGINT NULL\n\n'
                'vul_archive_inst\n'
                '  id (BIGINT PK)                -- vulInfoId\n'
                '  data_origin  VARCHAR(20)       -- OPEN/METRIC/... [NEW]\n'
                '  reportable_flag TINYINT        -- \u662f\u5426\u8fdb\u4e0a\u62a5\u8f68 [NEW]\n\n'
                'vul_inst_log_rela_oper  [NEW TABLE]\n'
                '  id (BIGINT PK)\n'
                '  vul_info_id  VARCHAR(64)       -- FK -> vul_archive_inst\n'
                '  data_origin  VARCHAR(20)\n'
                '  biz_line     VARCHAR(20)\n'
                '  partner_id   VARCHAR(64)\n'
                '  action_type  VARCHAR(20)\n'
                '  action_time  DATETIME\n'
                '  operator     VARCHAR(64)\n\n'
                'vul_inst_log_rela_report  (\u73b0\u6709\u8868\u540d \u4e0a\u62a5\u8f68)\n'
                '  id, vul_info_id, synthesized, log_ids, ...'
            ))
        sec_close(a)

        # -----------------------------------------------------------------------
        # FIELDS
        # -----------------------------------------------------------------------
        sec_open(a, 'fields')
        card(a, 'Wave 0 \u5df2\u53d1\u5e03\u6269\u5c55\u5b57\u6bb5\u8be6\u8868',
            tbl(['\u8868', '\u5b57\u6bb5', '\u7c7b\u578b', '\u9ed8\u8ba4\u5024', '\u975e\u7a7a', '\u8bf4\u660e'],
                [
                    ['vul_scan_task', 'biz_line', 'VARCHAR(20)', '-', 'N', 'OPEN/METRIC/ASSESS/PROD'],
                    ['vul_scan_task', 'data_origin', 'VARCHAR(20)', '-', 'N', '\u6570\u636e\u6765\u6e90'],
                    ['vul_scan_task', 'scan_policy', 'VARCHAR(20)', 'SOC_DUAL', 'N', '\u626b\u63cf\u7b56\u7565'],
                    ['vul_scan_task', 'partner_id', 'VARCHAR(64)', 'NULL', 'N', 'OPEN \u5fc5\u8bbe\uff0c\u5176\u4ed6 NULL'],
                    ['vul_scan_task', 'external_task_id', 'VARCHAR(64)', 'NULL', 'N', 'Partner \u5c42 taskId'],
                    ['vul_scan_task', 'tsk_scn', 'VARCHAR(20)', '\u5df2\u6709', 'N', '\u573a\u666f\u533a\u5206'],
                    ['vul_scan_task_sub', 'scanner_vendor', 'VARCHAR(20)', '-', 'N', 'NESSUS/LM/AH\u2026'],
                    ['vul_scan_task_sub', 'external_survey_id', 'VARCHAR(64)', 'NULL', 'N', 'task-center \u5185\u90e8 survey id'],
                    ['vul_archive_inst', 'data_origin', 'VARCHAR(20)', '-', 'N', '\u5b9e\u4f8b\u6765\u6e90'],
                    ['vul_archive_inst', 'reportable_flag', 'TINYINT(1)', '0', 'N', '\u662f\u5426\u8fdb\u4e0a\u62a5\u8f68'],
                    ['open_task', 'pass_task_id', 'BIGINT', 'NULL', 'N', 'Wave1b \u540e\u586b\u5199'],
                    ['open_task', 'scan_policy', 'VARCHAR(20)', 'SOC_DUAL', 'N', '\u7b56\u7565'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # ENUMS
        # -----------------------------------------------------------------------
        sec_open(a, 'enums')
        card(a, '\u679a\u4e3e\u8868',
            tbl(['\u679a\u4e3e', '\u53d6\u503c', '\u8bf4\u660e'],
                [
                    ['BizLineEnum', 'OPEN / METRIC / ASSESS / PROD', '\u4e1a\u52a1\u7ebf\uff0c\u6240\u6709\u65b0\u5efa\u4efb\u52a1\u5fc5\u5199'],
                    ['ScanPolicyEnum', 'SOC_DUAL (default) / SINGLE_LM / SINGLE_NES / CUSTOM', 'SOC \u5fc5\u987b SOC_DUAL'],
                    ['ScannerVendorEnum', 'NESSUS / LM / AH / QM / TRX / AZ / JTL', '\u5339\u914d task-center \u5382\u5546'],
                    ['DataOriginEnum', 'OPEN / METRIC / ASSESS / PROD / IMPORT', '\u5199 vul_archive_inst'],
                    ['LedgerStatusEnum', 'PENDING / WRITING / DONE / FAILED', '\u53f0\u8d26\u5199\u5165\u72b6\u6001'],
                    ['VulInfoStatEnum', '1/2/3/5/6/7/9/10', '\u5b9e\u4f8b\u751f\u547d\u5468\u671f\uff0c\u89c1\u72b6\u6001\u673a\u8868'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # NFR
        # -----------------------------------------------------------------------
        sec_open(a, 'nfr')
        card(a, '\u6027\u80fd\u4e0e\u53ef\u9760\u6027 SLA',
            tbl(['\u6307\u6807', '\u8981\u6c42', '\u6d4b\u91cf\u65b9\u5f0f'],
                [
                    ['\u4efb\u52a1\u521b\u5efa\u54cd\u5e94', 'P99 &lt; 2s', 'open-api \u8868\u5c42 traceId \u65f6\u957f'],
                    ['Webhook \u5ef6\u8fdf', 'P95 &lt; 5s (\u5e76\u96c6\u5b8c\u6210\u5230\u56de\u8c03)', 'Kafka offset \u5230 HTTP \u65f6\u957f'],
                    ['\u5e76\u96c6\u5165\u5e93', '\u53cc survey \u5168\u5b8c\u6210\u540e 30s \u5185', 'MergeService \u5904\u7406\u5ef6\u8fdf'],
                    ['\u5e76\u53d1\u4efb\u52a1', '\u5355 vul-pass \u5b9e\u4f8b &ge; 500 \u5e76\u53d1 SOC_DUAL \u4efb\u52a1', '\u538b\u6d4b'],
                    ['dedup \u51c6\u786e\u7387', '\u91cd\u590d\u7387 &lt; 1%\uff0c\u6f0f\u62a5\u7387 &lt; 0.5%', '\u7070\u5ea6\u53cc\u5199\u9a8c\u8bc1'],
                    ['Webhook \u6210\u529f\u7387', '&ge; 99% (\u542b 5 \u6b21\u91cd\u8bd5)', '\u76d1\u63a7\u9762\u677f\u6307\u6807'],
                ]))
        card(a, '\u53ef\u89c2\u6d4b\u6027 (Observability)',
            tbl(['\u9879\u76ee', '\u5185\u5bb9'],
                [
                    ['Metrics', 'open_task_created_total, webhook_delivery_total{status}, merge_latency_ms, dedup_conflict_total'],
                    ['Logs', '\u6bcf\u6b65\u8bb0\u5f55 traceId + passTaskId + partnerId\uff0cJSON \u683c\u5f0f'],
                    ['Tracing', 'Feign \u548c Kafka \u5185\u90e8\u4f20\u64ad X-B3-TraceId'],
                    ['\u8fd0\u8425\u5e94\u6025', 'Webhook \u91cd\u8bd5\u8d85\u8fc7 3 \u6b21\u544a\u8b66\uff0c\u4efb\u52a1 FAILED \u9875\u9762\u8fdb\u884c\u624b\u52a8\u91cd\u5c04'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # RISKS
        # -----------------------------------------------------------------------
        sec_open(a, 'risks')
        card(a, '\u98ce\u9669\u767b\u8bb0',
            tbl(['ID', '\u98ce\u9669', '\u7b49\u7ea7', '\u53d1\u751f\u6982\u7387', '\u5e94\u5bf9\u7b56\u7565'],
                [
                    ['R-01', 'task-center \u5f02\u5e38\u5bfc\u81f4\u53cc\u626b\u4e0d\u5168',
                     '<span class="bdg b4">\u9ad8</span>', '\u4e2d',
                     '\u8d85\u65f6\u5c06 sub \u7f6e TIMEOUT\uff0c\u89e6\u53d1 PARTIAL_FAILED \u6d41\u7a0b\uff1b\u8fd0\u8425\u548c\u5f71\u544a\u8b66'],
                    ['R-02', 'dedup \u89c4\u5219\u4e0d\u5b8c\u5584\u5bfc\u81f4\u6f0f\u62a5',
                     '<span class="bdg b4">\u9ad8</span>', '\u4e2d',
                     '\u7070\u5ea6\u6d4b\u8bd5 10% \u6d41\u91cf + \u53cc\u5199\u6a21\u5f0f\u6bd4\u5bf9'],
                    ['R-03', 'Webhook Partner \u7aef 502 \u6301\u7eed\u5931\u8d25',
                     '<span class="bdg b2">\u4e2d</span>', '\u4f4e',
                     '5 \u6b21\u91cd\u8bd5 + \u6b7b\u4fe1\u961f\u5217 + \u8fd0\u8425\u624b\u52a8\u91cd\u5c04'],
                    ['R-04', 'ASSESS \u5b58\u91cf\u6570\u636e biz_line \u8bef\u6807',
                     '<span class="bdg b2">\u4e2d</span>', '\u4e2d',
                     '\u5b58\u91cf\u8fc1\u79fb\u811a\u672c + \u56de\u6eda\u65b9\u6848\u5347\u7ea7\u524d\u51c6\u5907'],
                    ['R-05', 'Nessus + \u7eff\u76df \u5e76\u53d1\u8d85\u51fa task-center \u5bb9\u91cf',
                     '<span class="bdg b1">\u4f4e</span>', '\u4f4e',
                     'Partner \u5355\u4efb\u52a1\u76ee\u6807 IP &le; 1000\uff0c\u8d85\u51fa 422\uff1b\u961f\u5217\u9650\u6d41'],
                    ['R-06', 'open-api \u5185\u90e8 Feign \u8c03\u7528 vul-pass \u8d85\u65f6',
                     '<span class="bdg b2">\u4e2d</span>', '\u4f4e',
                     'Feign \u8d85\u65f6 3s\uff0c\u5f02\u6b65\u5907\u7528\u65b9\u6848\uff08Kafka \u8865\u5fa1\uff09'],
                ]))
        sec_close(a)

        # -----------------------------------------------------------------------
        # ROADMAP
        # -----------------------------------------------------------------------
        sec_open(a, 'roadmap')
        card(a, 'Wave \u8def\u7ebf\u56fe\u4e0e\u4ea4\u4ed8\u7269',
            '<div class="tl">'
            '<div class="tli done"><div class="tl-h">Wave 0 <span class="bdg b1">\u5df2\u5b8c\u6210</span></div>'
            '<div class="tl-d">\u4ea4\u4ed8\u7269\uff1aLiquibase groovy changeset (vul_scan_task + sub + inst + rela_oper)\u3001'
            '\u679a\u4e3e\u7c7b (BizLineEnum/ScanPolicyEnum/ScannerVendorEnum)\u3001DO/PO/DTO \u955c\u50cf\u3001'
            'Internal API \u5916\u5305 YAML\u3001PRD v1 + \u539f\u578b v1</div></div>'

            '<div class="tli"><div class="tl-h"><span class="bdg b2">Wave 1a</span> vuln-task-center \u53cc\u626b\u652f\u6301</div>'
            '<div class="tl-d">\u5c71\u5c71: ScanPolicyRouter.route(SOC_DUAL) \u8f93\u51fa [NESSUS, LM]\uff1b'
            '\u5c71\u5c71: Kafka \u8fd4\u56de open.task.sub.finished \u4e8b\u4ef6\uff1b'
            '\u9a8c\u6536: 5min \u5185 2 \u4e2a survey \u5747 RUNNING</div></div>'

            '<div class="tli"><div class="tl-h"><span class="bdg b2">Wave 1b</span> vul-pass \u7f16\u6392\u5185\u6838</div>'
            '<div class="tl-d">\u5c71\u5c71: OpenTaskInternalController + OpenTaskOrchestrator\uff1b'
            'MergeGateListener + MergeService + VulnDeduplicator\uff1b'
            '\u5c71\u5c71: vul_archive_inst \u5e76\u96c6\u5165\u5e93 + rela_oper \u5199\u5165\uff1b'
            '\u9a8c\u6536: \u5e76\u96c6\u6b63\u786e\u6027\u5355\u6d4b + \u5e76\u53d1\u538b\u6d4b</div></div>'

            '<div class="tli"><div class="tl-h"><span class="bdg b2">Wave 1c</span> open-api \u6539\u9020\u4e0e Webhook</div>'
            '<div class="tl-d">\u5c71\u5c71: SvmpEngineAdapterImpl \u5207\u65ad\u5047 orderId\uff1b'
            'WebhookDispatcher (\u6307\u6570\u91cd\u8bd5 + HMAC \u7b7e\u540d)\uff1b'
            '\u5c71\u5c71: /internal/notify \u63a5\u53e3\u5b9e\u73b0\uff1b'
            '\u9a8c\u6536: Partner \u771f\u5b9e\u6536\u5230 TASK_COMPLETED + \u7b7e\u540d\u9a8c\u8bc1</div></div>'

            '<div class="tli pend"><div class="tl-h"><span class="bdg b5">Wave 2</span> \u5b9e\u4f8b\u751f\u547d\u5468\u671f + \u5916\u53d1</div>'
            '<div class="tl-d">verify/remediate/verify-fix \u5199\u8fd0\u8425\u8f68\uff1b'
            'TaskExport XML/JSON \u5916\u53d1\uff1b\u62a5\u544a\u4ea7\u7269\u4e0b\u8f7d</div></div>'

            '<div class="tli pend"><div class="tl-h"><span class="bdg b5">Wave 3</span> METRIC \u8fc1\u79fb</div>'
            '<div class="tl-d">vuln-model \u6307\u6807\u4efb\u52a1\u5168\u91cf\u8fc1\u79fb\u5230 vul-pass METRIC \u8f68</div></div>'

            '<div class="tli pend"><div class="tl-h"><span class="bdg b5">Wave 4</span> \u8fd0\u8425\u5de5\u4f5c\u53f0</div>'
            '<div class="tl-d">\u524d\u7aef\u7ba1\u7406\u9875\u9762\uff1a\u4efb\u52a1\u5217\u8868\u3001\u53cc\u626b\u76d1\u63a7\u3001Webhook \u65e5\u5fd7\u3001\u5bf9\u8d26\u5f02\u5e38</div></div>'
            '</div>')
        sec_close(a)

        # -----------------------------------------------------------------------
        # ACCEPTANCE
        # -----------------------------------------------------------------------
        sec_open(a, 'accept')
        card(a, 'Wave 1 \u9a8c\u6536\u6807\u51c6\u8be6\u8868',
            tbl(['ID', '\u9a8c\u6536\u573a\u666f', '\u524d\u7f6e\u6761\u4ef6', '\u9884\u671f\u7ed3\u679c', '\u9a8c\u8bc1\u65b9\u5f0f'],
                [
                    ['AC-01', '\u521b\u5efa SOC_DUAL \u4efb\u52a1', 'SOC-CLIENT-A \u53d1\u8d77 POST /tasks/vul',
                     'HTTP 200\uff0c\u8fd4\u56de taskId + ACCEPTED\uff0c5min \u5185 Nessus + \u7eff\u76df survey \u5747 RUNNING',
                     'E2E \u8054\u8c03\u6d4b\u8bd5'],
                    ['AC-02', '\u53cc\u626b\u5e76\u96c6\u6b63\u786e\u6027', '\u4e24\u4e2a survey \u5747 FINISHED',
                     'vul_archive_inst \u5b9e\u4f8b\u6570 = \u5e76\u96c6\u540e\u552f\u4e00\u5bb9\uff0cdata_origin=OPEN\uff0cdedup key \u65e0\u91cd\u590d',
                     'DB \u67e5\u8be2\u9a8c\u8bc1'],
                    ['AC-03', 'TASK_COMPLETED Webhook', '\u5e76\u96c6\u5165\u5e93\u5b8c\u6210',
                     'callbackUrl \u6536\u5230 POST\uff0c payload \u5305\u542b mergedCount\uff0c\u7b7e\u540d\u9a8c\u8bc1\u901a\u8fc7',
                     'Partner Mock \u670d\u52a1\u622a\u5305'],
                    ['AC-04', '\u8fd0\u8425\u8f68\u5199\u5165', '\u5e76\u96c6\u5165\u5e93\u5b8c\u6210',
                     'vul_inst_log_rela_oper \u5305\u542b\u8be5\u4efb\u52a1\u5168\u90e8\u5b9e\u4f8b\uff0cbiz_line=OPEN',
                     'DB \u67e5\u8be2'],
                    ['AC-05', 'biz_line \u9694\u79bb', 'OPEN + ASSESS \u5e76\u5b58\u4efb\u52a1',
                     'OPEN \u4efb\u52a1\u4e0d\u5199 rela_report\uff0cASSESS \u4efb\u52a1\u4e0d\u5199 rela_oper',
                     'DB \u4ea4\u53c9\u67e5\u8be2'],
                    ['AC-06', '\u5207\u65ad\u5047 orderId', '\u5168\u91cf\u56de\u5f52\u6d4b\u8bd5',
                     'open-api \u65e5\u5fd7\u4e2d\u65e0 /vul-scan-task/dispatch \u8c03\u7528',
                     '\u65e5\u5fd7\u7ba1\u7406\u641c\u7d22'],
                    ['AC-07', 'Webhook \u6307\u6570\u91cd\u8bd5', 'Partner \u7aef\u6301\u7eed 502',
                     '\u81ea\u52a8\u6309 1/5/30/120/600s \u91cd\u8bd5\uff0c5 \u6b21\u540e\u8fdb\u6b7b\u4fe1\u961f\u5217',
                     '\u6a21\u62df Partner \u7aef\u9519\u8bef\u6d4b\u8bd5'],
                    ['AC-08', 'SOC_DUAL \u5f3a\u5236\u8986\u5199', 'SOC Partner \u4f20\u5165 SINGLE',
                     'vul-pass \u5f3a\u5236\u7f6e\u4e3a SOC_DUAL\uff0c\u4e24\u4e2a survey \u5e94\u5339\u914d\u521b\u5efa',
                     'E2E \u6d4b\u8bd5\u9a8c\u8bc1'],
                    ['AC-09', 'PARTIAL_FAILED \u573a\u666f', 'Nessus survey \u4eba\u4e3a\u5931\u8d25',
                     '\u7236\u4efb\u52a1 PARTIAL_FAILED\uff0c\u7eff\u76df\u7ed3\u679c\u4ecd\u5165\u5e93\uff0cWebhook \u63a8\u9001 PARTIAL_FAILED',
                     '\u6545\u969c\u6ce8\u5165\u6d4b\u8bd5'],
                    ['AC-10', 'Partner \u6570\u636e\u9694\u79bb', '\u4e24\u4e2a Partner A / B \u5e76\u5b58',
                     'Partner A \u65e0\u6cd5\u67e5\u8be2 Partner B \u7684\u4efb\u52a1\u6216\u5b9e\u4f8b',
                     'API \u8de8 Partner \u8bf7\u6c42\u6d4b\u8bd5'],
                ]))
        sec_close(a)

    return make_html(
        '\u5f00\u653e API \u7f16\u6392 \u00b7 SOC \u53cc\u626b\u5168\u94fe\u8def PRD v2',
        NAV,
        sections
    )


# ============================================================================
# main
# ============================================================================
if __name__ == "__main__":
    prd_html = build_prd()
    prd_out = OUTDIR / "open-api-vtc-prd-v2.html"
    prd_out.write_text(prd_html, encoding="utf-8")
    print("PRD v2 OK:", prd_out, "bytes", len(prd_html.encode("utf-8")))
