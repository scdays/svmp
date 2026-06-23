# -*- coding: utf-8 -*-
# ASCII-only source: all CJK chars as \uXXXX string literals
from pathlib import Path

PARTS = []
def a(*chunks):
    for c in chunks:
        PARTS.append(c)

# ---- CSS (no CJK needed) ---------------------------------------------------
CSS = (
    ":root{--primary:#1890ff;--success:#52c41a;--warning:#faad14;--error:#ff4d4f"
    ";--text:rgba(0,0,0,.85);--secondary:rgba(0,0,0,.45);--border:#d9d9d9"
    ";--bg:#f5f5f5;--card:#fff;--sidebar:#001529}"
    "*{box-sizing:border-box;margin:0;padding:0}"
    "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif"
    ";font-size:14px;color:var(--text);background:var(--bg);line-height:1.6}"
    ".app{display:flex;min-height:100vh}"
    ".side{width:240px;background:var(--sidebar);color:#fff;flex-shrink:0;position:sticky;top:0;height:100vh;overflow-y:auto}"
    ".logo{padding:18px 20px;font-size:15px;font-weight:600;border-bottom:1px solid rgba(255,255,255,.1);line-height:1.4}"
    ".logo small{display:block;font-size:11px;font-weight:400;opacity:.6;margin-top:2px}"
    ".nav-group{padding:12px 0 4px}"
    ".nav-group-title{padding:4px 20px;font-size:10px;color:rgba(255,255,255,.35)}"
    ".nav-item{display:block;padding:8px 20px 8px 28px;color:rgba(255,255,255,.65);font-size:13px;text-decoration:none;cursor:pointer}"
    ".nav-item:hover{color:#fff;background:rgba(255,255,255,.07)}"
    ".nav-item.active{color:#fff;background:var(--primary)}"
    ".main{flex:1;overflow:auto}"
    ".topbar{height:48px;background:#fff;border-bottom:1px solid #f0f0f0;display:flex;align-items:center;padding:0 24px;position:sticky;top:0;z-index:10;gap:12px}"
    ".topbar-title{font-weight:500}"
    ".badge{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:500;border:1px solid}"
    ".badge-blue{background:#e6f7ff;border-color:#91d5ff;color:#0958d9}"
    ".badge-green{background:#f6ffed;border-color:#b7eb8f;color:#389e0d}"
    ".badge-orange{background:#fff7e6;border-color:#ffd591;color:#d46b08}"
    ".badge-purple{background:#f9f0ff;border-color:#d3adf7;color:#531dab}"
    ".badge-red{background:#fff2f0;border-color:#ffccc7;color:#cf1322}"
    ".badge-gray{background:#fafafa;border-color:#d9d9d9;color:#666}"
    ".content{padding:24px;max-width:1080px}"
    ".section{display:none}.section.active{display:block}"
    ".card{background:#fff;border-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,.04);margin-bottom:20px}"
    ".card-head{padding:14px 20px;border-bottom:1px solid #f0f0f0;font-weight:500;font-size:14px;display:flex;align-items:center;gap:8px}"
    ".card-body{padding:16px 20px}"
    "table{width:100%;border-collapse:collapse}"
    "th,td{padding:10px 14px;border-bottom:1px solid #f0f0f0;vertical-align:top}"
    "th{background:#fafafa;font-weight:500;white-space:nowrap}"
    "td code{font-size:12px;background:#f5f5f5;padding:1px 5px;border-radius:3px}"
    ".alert{padding:12px 16px;border-radius:4px;margin-bottom:16px;font-size:13px;line-height:1.7}"
    ".alert-info{background:#e6f7ff;border:1px solid #91d5ff;color:#0958d9}"
    ".alert-warn{background:#fffbe6;border:1px solid #ffe58f;color:#ad6800}"
    ".tl{border-left:3px solid #e8e8e8;padding-left:20px;margin-left:8px}"
    ".tl-item{margin-bottom:16px;position:relative}"
    ".tl-item::before{content:'';width:11px;height:11px;border-radius:50%;background:var(--primary);position:absolute;left:-27px;top:4px;border:2px solid #fff}"
    ".tl-item.done::before{background:var(--success)}"
    ".tl-item.pending::before{background:#d9d9d9}"
    ".tl-label{font-weight:500;margin-bottom:4px}"
    ".tl-desc{color:var(--secondary);font-size:13px}"
    ".feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}"
    ".feat-card{border:1px solid #f0f0f0;border-radius:4px;padding:16px;background:#fafafa}"
    ".feat-card h4{margin-bottom:6px;font-size:13px}"
    ".feat-card p{font-size:12px;color:var(--secondary);line-height:1.6}"
    ".arch{background:#f8f8f8;border:1px dashed #d9d9d9;border-radius:4px;padding:20px;font-family:Consolas,monospace;font-size:12px;line-height:1.8;white-space:pre}"
    ".flow-steps{display:flex;align-items:center;flex-wrap:wrap;gap:0;margin:16px 0}"
    ".flow-step{padding:10px 16px;background:#e6f7ff;border:1px solid #91d5ff;border-radius:4px;font-size:12px;text-align:center;min-width:90px}"
    ".flow-arrow{padding:0 8px;color:#91d5ff;font-size:18px}"
    ".stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}"
    ".stat{background:#fff;border:1px solid #f0f0f0;border-radius:4px;padding:16px}"
    ".stat .num{font-size:28px;font-weight:500;margin-bottom:4px}"
    ".stat .lbl{font-size:12px;color:var(--secondary)}"
    ".risk-high{color:#cf1322;font-weight:500}.risk-mid{color:#d46b08}.risk-low{color:#389e0d}"
)

# ---- helpers ---------------------------------------------------------------
def card(title, body):
    a('<div class="card"><div class="card-head">', title, '</div><div class="card-body">', body, '</div></div>')

def tbl(heads, rows):
    s = '<table><tr>' + ''.join('<th>' + h + '</th>' for h in heads) + '</tr>'
    for r in rows:
        s += '<tr>' + ''.join('<td>' + str(c) + '</td>' for c in r) + '</tr>'
    return s + '</table>'

def al(t, c):
    return '<div class="alert alert-' + t + '">' + c + '</div>'

def sec_open(sid, active=False):
    a('<div id="sec-', sid, '" class="section', ' active' if active else '', '">')

def sec_close():
    a('</div>')

# ---- document head ---------------------------------------------------------
a('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"/>')
a('<meta name="viewport" content="width=device-width,initial-scale=1"/>')
a('<title>\u5f00\u653e API \u00b7 SOC \u53cc\u626b PRD v1</title>')
a('<style>', CSS, '</style></head><body><div class="app">')

# ---- sidebar ---------------------------------------------------------------
a('<aside class="side">')
a('<div class="logo">\u6f0f\u6d1e\u7ba1\u7406\u5e73\u53f0<small>OPEN \u7f16\u6392 \u00b7 SOC \u53cc\u626b PRD v1</small></div>')

NAV = [
    ('\u4ea7\u54c1\u6587\u6863', [
        ('overview', '\u6982\u8ff0\u4e0e\u80cc\u666f'),
        ('goals',    '\u4ea7\u54c1\u76ee\u6807'),
        ('arch',     '\u67b6\u6784\u603b\u89c8'),
        ('users',    '\u7528\u6237\u4e0e\u89d2\u8272'),
    ]),
    ('\u9700\u6c42\u8be6\u60c5', [
        ('features', '\u529f\u80fd\u8bbe\u8ba1'),
        ('api',      'API \u5185\u90e8\u63a5\u53e3'),
        ('data',     '\u6570\u636e\u6a21\u578b'),
        ('stories',  '\u7528\u6237\u6545\u4e8b'),
    ]),
    ('\u8d28\u91cf\u4e0e\u98ce\u9669', [
        ('nfr',        '\u975e\u529f\u80fd\u9700\u6c42'),
        ('risks',      '\u98ce\u9669\u4e0e\u7ea6\u675f'),
        ('roadmap',    '\u4ea7\u54c1\u8def\u7ebf\u56fe'),
        ('acceptance', '\u9a8c\u6536\u6807\u51c6'),
    ]),
]

for grp_label, items in NAV:
    a('<div class="nav-group"><div class="nav-group-title">', grp_label, '</div>')
    for sid, lbl in items:
        act = ' active' if sid == 'overview' else ''
        a('<a class="nav-item', act, '" data-sec="', sid, '">', lbl, '</a>')
    a('</div>')

a('</aside>')

# ---- main area -------------------------------------------------------------
a('<div class="main">')
a('<div class="topbar"><span class="topbar-title">')
a('\u5f00\u653e API \u7f16\u6392\u4efb\u52a1 \u00b7 SOC \u53cc\u626b\u5168\u94fe\u8def PRD')
a('</span>')
a('<span class="badge badge-blue">v1.0</span>')
a('<span class="badge badge-orange">Draft</span>')
a('<span style="margin-left:auto;font-size:12px">2026-06-16</span>')
a('</div><div class="content">')

# ===========================================================================
# SECTION: overview
# ===========================================================================
sec_open('overview', True)
card('\u6587\u6863\u5143\u4fe1\u606f', tbl(
    ['\u5c5e\u6027', '\u5185\u5bb9'],
    [
        ['\u6587\u6863\u540d\u79f0', 'OPEN \u7f16\u6392\u4efb\u52a1 \u00b7 SOC \u53cc\u626b\u5168\u94fe\u8def \u2014 PRD'],
        ['\u7248\u672c', 'v1.0 Draft'],
        ['\u65e5\u671f', '2026-06-16'],
        ['\u9002\u7528\u8303\u56f4', 'open-api-service \u00b7 vul-pass \u00b7 vuln-task-center'],
        ['\u529f\u80fd\u7f16\u53f7', 'OPEN-VTC-W0 ~ W4'],
    ]))
card('\u80cc\u666f\u4e0e\u95ee\u9898',
    al('warn', '<strong>\u5f53\u524d\u75db\u70b9\uff1a</strong>'
       'open-api-service \u901a\u8fc7\u4f2a\u9020 <code>orderId</code> \u8c03\u7528 '
       '<code>POST /vul-scan-task/dispatch</code>\uff0c\u5bfc\u81f4\u6570\u636e\u6e90\u4e0d\u6e05\u3001'
       '\u53cc\u626b\u65e0\u6cd5\u5b9e\u73b0\u3001Webhook \u4f2a\u9020\u3002') +
    tbl(
        ['\u95ee\u9898', '\u8868\u73b0', '\u5f71\u54cd'],
        [
            ['\u5047 orderId \u6ce1\u6c13 \u8003\u6838', '\u5171\u7528\u8003\u6838\u6570\u636e\u8868', '\u8003\u6838\u6743\u76ca\u53d7\u635f'],
            ['SOC \u53cc\u626b\u65e0\u6cd5\u5b9e\u73b0', '\u4ec5\u652f\u6301\u5355\u626b', '\u4e1a\u52a1\u627f\u8bfa\u5931\u4fe1'],
            ['\u6570\u636e\u6765\u6e90\u4e0d\u6e05', 'OPEN/METRIC/ASSESS \u6df7\u7528', '\u4e0a\u62a5\u5408\u89c4\u5931\u8d25'],
            ['\u771f\u5b9e Webhook \u7f3a\u5931', '\u56de\u8c03 Mock', 'Partner \u4fe1\u4efb\u964d\u4f4e'],
        ]))
card('\u4e09\u5927\u53d1\u8d77\u65b9',
    '<div class="feat-grid">'
    '<div class="feat-card"><h4><span class="badge badge-purple">OPEN</span> SOC Partner</h4>'
    '<p>REST API \u521b\u5efa\u53cc\u626b\u4efb\u52a1\uff0c\u5fc5\u987b SOC_DUAL\uff1a'
    'Nessus + \u7eff\u76df \u5e76\u96c6\u540e Webhook\u3002</p></div>'
    '<div class="feat-card"><h4><span class="badge badge-orange">METRIC</span> \u6307\u6807\u4efb\u52a1</h4>'
    '<p>vuln-model \u5e38\u6001\u5316\u4efb\u52a1\u8fc1\u79fb vul-pass\uff0cbiz_line=METRIC\u3002</p></div>'
    '<div class="feat-card"><h4><span class="badge badge-blue">ASSESS</span> \u90e8\u4fa7\u8003\u6838</h4>'
    '<p>\u5de5\u5355\u9a71\u52a8\uff0c\u5199\u4e0a\u62a5\u8f68 rela_report\u3002</p></div>'
    '</div>')
sec_close()

# ===========================================================================
# SECTION: goals
# ===========================================================================
sec_open('goals')
card('\u4ea7\u54c1\u76ee\u6807 OKR',
    '<div class="stat-row">'
    '<div class="stat"><div class="num">3</div><div class="lbl">\u53d1\u8d77\u65b9\u5168\u652f\u6301</div></div>'
    '<div class="stat"><div class="num">100%</div><div class="lbl">SOC_DUAL \u5b9e\u73b0\u7387</div></div>'
    '<div class="stat"><div class="num">0</div><div class="lbl">\u5047 orderId \u6cc4\u6f0f</div></div>'
    '<div class="stat"><div class="num">&lt;5s</div><div class="lbl">Webhook P95 \u5ef6\u8fdf</div></div>'
    '</div>' +
    tbl(
        ['OKR', '\u76ee\u6807', '\u53ef\u91cf\u5316\u6307\u6807', 'Wave'],
        [
            ['O1', '\u5207\u65ad\u5047 orderId', 'open-api \u4e0d\u518d\u8c03 /vul-scan-task/dispatch', 'W1'],
            ['O2', 'SOC \u53cc\u626b\u627f\u8bfa\u5151\u73b0', 'SOC Partner 100% \u8d70 SOC_DUAL', 'W1'],
            ['O3', '\u5e76\u96c6\u81ea\u52a8\u5165\u5e93', 'dedup \u91cd\u590d\u7387 &lt;1%', 'W2'],
            ['O4', '\u771f\u5b9e Webhook', '\u6210\u529f\u7387 &ge;99%', 'W2'],
            ['O5', '\u6570\u636e\u6765\u6e90\u6e05\u6670', 'biz_line \u8986\u76d6 100%', 'W0 \u2713'],
        ]))
sec_close()

# ===========================================================================
# SECTION: arch
# ===========================================================================
sec_open('arch')
card('\u76ee\u6807\u67b6\u6784\uff08Wave 1+\uff09',
    '<div class="arch">'
    'Partner (SOC)\n'
    '  | POST /api/open/v1/tasks/vul\n'
    '  v\nopen-api-service\n'
    '  | POST /internal/open/v1/tasks (Feign)\n'
    '  v\nvul-pass  OpenTaskOrchestrator\n'
    '  +- biz_line=OPEN, scan_policy=SOC_DUAL\n'
    '  |  +- vul_scan_task_sub x2 (Nessus + \u7eff\u76df)\n'
    '  v  Kafka\nvuln-task-center\n'
    '  +- Nessus RSAS\n'
    '  +- \u7eff\u76df LM RSAS\n'
    '  v  \u53cc survey \u5b8c\u6210 -> Kafka\n'
    'vul-pass  MergeService\n'
    '  +- dedup \u5e76\u96c6 -> vul_archive_inst (data_origin=OPEN)\n'
    '  +- \u8fd0\u8425\u8f68 vul_inst_log_rela_oper\n'
    '  v  Feign notify\n'
    'open-api  WebhookDispatcher\n'
    '  +- TASK_COMPLETED -> Partner callbackUrl'
    '</div>' +
    al('info', '\u5173\u952e\u5207\u65ad\uff1aopen-api \u4e0d\u518d\u8c03 '
       '<code>POST /vul-scan-task/dispatch</code>\uff0c'
       '\u65b0\u5185\u90e8\u63a5\u53e3 <code>POST /internal/open/v1/tasks</code> '
       '\u5b9e\u73b0\u4efb\u52a1\u6e90\u9694\u79bb\u3002'))
card('\u53cc\u8f68\u5b58\u50a8\u6a21\u578b',
    '<div class="arch">'
    'vul_archive_inst  (\u5168\u5e73\u53f0\u5171\u7528\u4e3b\u6863)\n'
    '  data_origin: OPEN | METRIC | ASSESS | PROD | IMPORT\n\n'
    'vul_inst_log_rela_oper  (\u8fd0\u8425\u8f68 - \u771f\u5b9e\u8f68\u8ff9)\n'
    '  \u5199\u5165\u65b9: OPEN / METRIC / PROD\n\n'
    'vul_inst_log_rela_report  (\u4e0a\u62a5\u8f68 - \u90e8\u4fa7\u5408\u89c4)\n'
    '  \u5199\u5165\u65b9: ASSESS\n'
    '  log_id_lst \u5b8c\u6574\u5c55\u73b0'
    '</div>')
sec_close()

# ===========================================================================
# SECTION: users
# ===========================================================================
sec_open('users')
card('\u76f4\u63a5\u7528\u6237\u4e0e\u89d2\u8272',
    tbl(
        ['\u89d2\u8272', '\u4e3b\u8981\u8bc9\u6c42', '\u6280\u672f\u63a5\u53e3'],
        [
            ['SOC Partner', '\u521b\u5efa\u53cc\u626b\u4efb\u52a1\u3001\u67e5\u8be2\u8fdb\u5ea6\u3001Webhook', 'REST /api/open/v1'],
            ['METRIC \u7cfb\u7edf', '\u5e38\u6001\u5316\u4efb\u52a1\u8fc1\u79fb', 'Feign/Kafka'],
            ['\u8fd0\u8425\u7ba1\u7406\u5458', '\u67e5\u770b\u72b6\u6001\u3001\u91cd\u8bd5 Webhook', '\u7ba1\u7406\u9875\u9762'],
            ['\u90e8\u4fa7\u8003\u6838', '\u5de5\u5355\u9a71\u52a8\u4e0a\u62a5\u8f68', 'vul-pass \u5185\u90e8'],
        ]))
card('Partner \u63a5\u5165\u8981\u4ef6',
    tbl(
        ['\u914d\u7f6e\u9879', '\u5185\u5bb9'],
        [
            ['<code>partnerId</code>', '\u8fd0\u8425\u5206\u914d\u7684\u552f\u4e00\u6807\u8bc6'],
            ['<code>clientId/clientSecret</code>', 'OAuth 2.0 Client Credentials'],
            ['<code>scanPolicy</code>', 'SOC \u63a5\u5165\u65b9\u5fc5\u987b\u4e3a SOC_DUAL'],
            ['<code>callbackUrl</code>', 'Partner \u63d0\u4f9b Webhook \u5730\u5740'],
            ['\u80fd\u529b\u7801', '\u8fd0\u8425\u5f00\u901a: TASK_CREATE / WEBHOOK'],
        ]))
sec_close()

# ===========================================================================
# SECTION: features
# ===========================================================================
sec_open('features')
card('P0 \u5fc5\u987b\u529f\u80fd',
    tbl(
        ['ID', '\u529f\u80fd', '\u670d\u52a1', '\u8bf4\u660e'],
        [
            ['F-01', '\u5185\u90e8\u4efb\u52a1\u521b\u5efa API', 'vul-pass', '<code>POST /internal/open/v1/tasks</code>'],
            ['F-02', 'SOC_DUAL \u53cc survey \u4e0b\u53d1', 'vul-pass \u2192 vtc', '\u540c\u65f6\u521b\u5efa Nessus + \u7eff\u76df 2\u4e2a survey'],
            ['F-03', '\u5e76\u96c6 merge \u5165\u5e93', 'vul-pass MergeService', 'dedup \u5e76\u96c6 \u2192 vul_archive_inst'],
            ['F-04', '\u771f\u5b9e Webhook', 'open-api', 'TASK_COMPLETED\uff0c5\u6b21\u6307\u6570\u91cd\u8bd5'],
            ['F-05', '\u4efb\u52a1\u67e5\u8be2', 'open-api \u2192 vul-pass', '<code>GET /internal/open/v1/tasks/{id}</code>'],
            ['F-06', 'biz_line \u5168\u9762\u6807\u8bc6', 'vul-pass', '\u65b0\u5efa\u4efb\u52a1\u5fc5\u5199 biz_line'],
        ]))
card('SOC_DUAL \u53cc\u626b\u6d41\u7a0b\u793a\u610f',
    '<div class="flow-steps">'
    '<div class="flow-step">Partner<br>POST /tasks/vul</div>'
    '<div class="flow-arrow">-&gt;</div>'
    '<div class="flow-step">open-api<br>\u9c13\u6743\u6821\u9a8c</div>'
    '<div class="flow-arrow">-&gt;</div>'
    '<div class="flow-step">vul-pass<br>\u521b\u5efa\u4efb\u52a1</div>'
    '<div class="flow-arrow">-&gt;</div>'
    '<div class="flow-step">task-center<br>Nessus</div>'
    '<div class="flow-arrow">+</div>'
    '<div class="flow-step">task-center<br>\u7eff\u76df</div>'
    '</div>'
    '<div class="flow-steps">'
    '<div class="flow-step">\u5f02\u6b65\u626b\u63cf</div>'
    '<div class="flow-arrow">-&gt;</div>'
    '<div class="flow-step">Kafka<br>\u53cc\u7ed3\u679c</div>'
    '<div class="flow-arrow">-&gt;</div>'
    '<div class="flow-step">dedup<br>\u5e76\u96c6</div>'
    '<div class="flow-arrow">-&gt;</div>'
    '<div class="flow-step">rela_oper<br>\u5165\u5e93</div>'
    '<div class="flow-arrow">-&gt;</div>'
    '<div class="flow-step">Webhook<br>COMPLETED</div>'
    '</div>' +
    al('info', 'dedupKey = \u8d44\u4ea7 IP + \u7aef\u53e3 + \u534f\u8bae + \u670d\u52a1 + vulId'))
sec_close()

# ===========================================================================
# SECTION: api
# ===========================================================================
sec_open('api')
card('\u5bf9\u5916 API\uff08Partner \u8c03\u7528\uff09',
    tbl(
        ['\u65b9\u6cd5', '\u8def\u5f84', '\u8bf4\u660e'],
        [
            ['POST', '/api/open/v1/tasks/vul', '\u521b\u5efa\u6392\u67e5\u4efb\u52a1\uff0c\u8fd4\u56de taskId'],
            ['GET',  '/api/open/v1/tasks/{taskId}', '\u4efb\u52a1\u8fdb\u5ea6\u4e0e\u72b6\u6001'],
            ['POST', '/api/open/v1/instances/{id}/verify', '\u9a8c\u8bc1\u8bef\u62a5'],
            ['POST', '/api/open/v1/instances/{id}/remediate', '\u5904\u7f6e\uff08\u4fee\u590d/\u5907\u6848\uff09'],
            ['POST', '/api/open/v1/instances/{id}/verify-fix', '\u4fee\u590d\u6838\u9a8c\u590d\u626b'],
        ]))
card('\u5185\u90e8 API\uff08Feign\uff09',
    tbl(
        ['\u65b9\u6cd5', '\u8def\u5f84', '\u8bf4\u660e', 'Wave'],
        [
            ['POST', '/internal/open/v1/tasks', '\u521b\u5efa OPEN \u4efb\u52a1', 'W1b'],
            ['GET',  '/internal/open/v1/tasks/{id}', '\u67e5\u8be2\u8fdb\u5ea6', 'W1b'],
            ['POST', '/internal/open/v1/tasks/{id}/notify', 'Webhook \u56de\u8c03\u89e6\u53d1', 'W1c'],
        ]))
card('Webhook \u4e8b\u4ef6\u7c7b\u578b',
    tbl(
        ['eventType', '\u89e6\u53d1\u65f6\u673a', '\u5173\u952e\u5b57\u6bb5'],
        [
            ['TASK_COMPLETED', '\u5e76\u96c6\u5165\u5e93\u5b8c\u6210', 'taskId, mergedCount'],
            ['TASK_FAILED',    '\u4efb\u52a1\u5f02\u5e38\u7ec8\u6b62', 'taskId, reason'],
            ['EXPORT_READY',   'TaskExport \u5c31\u7eea', 'downloadUrl, format'],
            ['INSTANCE_UPDATED', '\u5b9e\u4f8b\u72b6\u6001\u53d8\u66f4', 'vulInfoId, vulInfoStat'],
        ]))
sec_close()

# ===========================================================================
# SECTION: data
# ===========================================================================
sec_open('data')
card('\u65b0\u589e/\u6269\u5c55\u5b57\u6bb5\uff08Wave 0 \u5df2\u53d1\u5e03\uff09',
    tbl(
        ['\u8868', '\u5b57\u6bb5', '\u8bf4\u660e', '\u72b6\u6001'],
        [
            ['vul_scan_task', 'biz_line / data_origin / scan_policy / partner_id / external_task_id', '\u4efb\u52a1\u6765\u6e90\u6807\u8bc6', '\u5df2\u53d1\u5e03'],
            ['vul_scan_task_sub', 'external_survey_id / scanner_vendor', '\u5b50\u4efb\u52a1\u6807\u8bc6', '\u5df2\u53d1\u5e03'],
            ['vul_archive_inst', 'data_origin / reportable_flag', '\u5b9e\u4f8b\u6765\u6e90', '\u5df2\u53d1\u5e03'],
            ['open_task', 'pass_task_id / scan_policy', '\u5173\u8054 vul-pass\uff0c\u9ed8\u8ba4 SOC_DUAL', '\u5df2\u53d1\u5e03'],
            ['vul_inst_log_rela_oper', '\u65b0\u8868', '\u8fd0\u8425\u8f68', '\u5df2\u53d1\u5e03'],
        ]))
card('\u679a\u4e3e\u8868',
    tbl(
        ['\u679a\u4e3e', '\u53d6\u5024'],
        [
            ['BizLineEnum', 'OPEN / METRIC / ASSESS / PROD'],
            ['ScanPolicyEnum', 'SOC_DUAL(default) / SINGLE_LM / SINGLE_NES / CUSTOM'],
            ['ScannerVendorEnum', 'NESSUS / LM / AH / QM / TRX'],
            ['DataOriginEnum', 'OPEN / METRIC / ASSESS / PROD / IMPORT'],
            ['LedgerStatusEnum', 'PENDING / WRITING / DONE / FAILED'],
        ]))
sec_close()

# ===========================================================================
# SECTION: stories
# ===========================================================================
sec_open('stories')
card('\u7528\u6237\u6545\u4e8b',
    tbl(
        ['ID', '\u89d2\u8272', '\u6211\u5e0c\u671b\u2026', '\u9a8c\u6536\u6807\u51c6', '\u4f18\u5148\u7ea7'],
        [
            ['US-01', 'SOC \u8fd0\u8425', '\u521b\u5efa\u53cc\u626b\u4efb\u52a1', '5min \u5185 Nessus+\u7eff\u76df survey RUNNING', '<span class="badge badge-red">P0</span>'],
            ['US-02', 'SOC \u8fd0\u8425', 'Webhook TASK_COMPLETED', '\u5305\u542b mergedCount', '<span class="badge badge-red">P0</span>'],
            ['US-03', '\u8fd0\u8425\u7ba1\u7406\u5458', '\u67e5\u770b\u53cc\u626b\u8fdb\u5ea6', '\u9875\u9762\u5c55\u793a\u53cc survey \u72b6\u6001', '<span class="badge badge-orange">P1</span>'],
            ['US-04', '\u8fd0\u8425\u7ba1\u7406\u5458', '\u624b\u52a8\u91cd\u8bd5 Webhook', '\u6295\u9012\u6210\u529f', '<span class="badge badge-orange">P1</span>'],
            ['US-05', 'METRIC \u7cfb\u7edf', '\u5e38\u6001\u5316\u4efb\u52a1\u8fc1\u79fb', 'biz_line=METRIC \u72ec\u7acb\u5efa\u8868', '<span class="badge badge-orange">P1</span>'],
        ]))
sec_close()

# ===========================================================================
# SECTION: nfr
# ===========================================================================
sec_open('nfr')
card('\u6027\u80fd\u4e0e\u53ef\u9760\u6027',
    tbl(
        ['\u6307\u6807', '\u8981\u6c42'],
        [
            ['\u4efb\u52a1\u521b\u5efa\u54cd\u5e94', '&lt;2s P99'],
            ['Webhook \u5ef6\u8fdf', '&lt;5s P95'],
            ['\u5e76\u96c6\u5165\u5e93', '\u53cc survey \u5168\u5b8c\u6210\u540e 30s \u5185'],
            ['Webhook \u91cd\u8bd5', '\u6307\u6570\u9000\u907f 5\u6b21 (1/5/30/120/600s)'],
            ['\u5e76\u53d1\u4efb\u52a1', '\u5355\u5b9e\u4f8b &ge; 500 \u5e76\u53d1\u6392\u67e5'],
        ]))
card('\u5b89\u5168\u6027',
    tbl(
        ['\u9879\u76ee', '\u8981\u6c42'],
        [
            ['API \u9c13\u6743', 'OAuth 2.0 Client Credentials + Bearer Token'],
            ['Partner \u6570\u636e\u9694\u79bb', 'partner_id \u5fc5\u987b\u9694\u79bb\uff0c\u7981\u6b62\u8de8 Partner \u67e5\u8be2'],
            ['/internal/* \u8def\u7531', '\u4ec5\u5185\u7f51\u53ef\u8bbf\uff0c\u5bf9\u5916\u7f51\u5173\u62e6\u622a'],
        ]))
sec_close()

# ===========================================================================
# SECTION: risks
# ===========================================================================
sec_open('risks')
card('\u98ce\u9669\u767b\u8bb0',
    tbl(
        ['ID', '\u98ce\u9669', '\u7b49\u7ea7', '\u5e94\u5bf9\u7b56\u7565'],
        [
            ['R-01', 'task-center \u5f02\u5e38\u5bfc\u81f4\u53cc\u626b\u4e0d\u5168', '<span class="risk-high">\u9ad8</span>', '\u8d85\u65f6\u91cd\u8bd5 + \u5355\u626b fallback'],
            ['R-02', 'dedup \u89c4\u5219\u4e0d\u5b8c\u5584\u5bfc\u81f4\u6f0f\u62a5', '<span class="risk-high">\u9ad8</span>', '\u7070\u5ea6\u6d4b\u8bd5 10% \u6d41\u91cf'],
            ['R-03', 'Webhook Partner 502 \u6301\u7eed\u5931\u8d25', '<span class="risk-mid">\u4e2d</span>', '5\u6b21\u91cd\u8bd5 + \u624b\u52a8\u91cd\u5c04'],
            ['R-04', 'ASSESS \u8bef\u6807 biz_line', '<span class="risk-mid">\u4e2d</span>', '\u5b58\u91cf\u8fc1\u79fb\u811a\u672c + \u56de\u6eda'],
        ]))
card('\u5f00\u53d1\u7ea6\u675f',
    tbl(
        ['\u7ea6\u675f\u9879', '\u5185\u5bb9'],
        [
            ['\u65b0\u5efa\u5fae\u670d\u52a1', '\u7981\u6b62\uff0c\u5168\u90e8\u5c55\u5165\u5df2\u6709\u4e09\u4e2a\u670d\u52a1'],
            ['\u76f4\u8fde\u626b\u63cf\u5668', 'Partner \u4e0d\u76f4\u8fde\u626b\u63cf\u5668\uff0c\u5fc5\u987b\u7ecf\u7531\u5e73\u53f0 API'],
            ['Liquibase', '\u6240\u6709 Schema \u53d8\u66f4\u5fc5\u987b\u7ecf\u7531 Liquibase changeset'],
        ]))
sec_close()

# ===========================================================================
# SECTION: roadmap
# ===========================================================================
sec_open('roadmap')
card('\u5f00\u53d1 Wave \u8def\u7ebf\u56fe',
    '<div class="tl">'

    '<div class="tl-item done">'
    '<div class="tl-label">Wave 0 <span class="badge badge-green">\u5df2\u5b8c\u6210</span></div>'
    '<div class="tl-desc">Liquibase Schema + \u679a\u4e3e + DO/PO/DTO + Internal API \u6587\u6863 + \u539f\u578b v1</div>'
    '</div>'

    '<div class="tl-item">'
    '<div class="tl-label"><span class="badge badge-orange">Wave 1a</span> vuln-task-center \u53cc\u626b\u652f\u6301</div>'
    '<div class="tl-desc">ScanPolicyRouter\uff0cSOC_DUAL \u521b\u5efa 2x survey\uff0c\u53cc\u5b8c\u6210 Kafka \u4e8b\u4ef6</div>'
    '</div>'

    '<div class="tl-item">'
    '<div class="tl-label"><span class="badge badge-orange">Wave 1b</span> vul-pass OpenTaskOrchestrator</div>'
    '<div class="tl-desc">POST /internal/open/v1/tasks \u5b9e\u73b0\uff0cKafka \u76d1\u542c\u5e76\u96c6 \u2192 MergeService</div>'
    '</div>'

    '<div class="tl-item">'
    '<div class="tl-label"><span class="badge badge-orange">Wave 1c</span> open-api \u6539\u9020</div>'
    '<div class="tl-desc">SvmpEngineAdapterImpl \u6539\u8c03\u5185\u90e8 API\uff0c\u5207\u65ad\u5047 orderId\uff0cWebhook \u5b9e\u94fe\u8def</div>'
    '</div>'

    '<div class="tl-item pending">'
    '<div class="tl-label"><span class="badge badge-gray">Wave 2</span> \u5b9e\u4f8b\u751f\u547d\u5468\u671f + \u5916\u53d1</div>'
    '<div class="tl-desc">verify/remediate/verify-fix \u5199\u8fd0\u8425\u8f68\uff0cTaskExport\uff0c\u62a5\u544a\u4e0b\u8f7d</div>'
    '</div>'

    '<div class="tl-item pending">'
    '<div class="tl-label"><span class="badge badge-gray">Wave 3~4</span> METRIC \u8fc1\u79fb + \u8fd0\u8425\u5de5\u4f5c\u53f0</div>'
    '<div class="tl-desc">vuln-model \u5168\u91cf\u8fc1\u79fb\uff0c\u524d\u7aef\u7ba1\u7406\u9875\u9762</div>'
    '</div>'

    '</div>')
sec_close()

# ===========================================================================
# SECTION: acceptance
# ===========================================================================
sec_open('acceptance')
card('Wave 1 \u9a8c\u6536\u6e05\u5355',
    tbl(
        ['ID', '\u573a\u666f', '\u9884\u671f\u7ed3\u679c'],
        [
            ['AC-01', '\u521b\u5efa SOC_DUAL \u4efb\u52a1', 'Nessus + \u7eff\u76df survey \u5747 RUNNING'],
            ['AC-02', '\u53cc\u626b\u5e76\u96c6', 'vul_archive_inst data_origin=OPEN\uff0c\u5b9e\u4f8b\u552f\u4e00'],
            ['AC-03', 'Webhook \u56de\u8c03', 'callbackUrl \u6536\u5230 TASK_COMPLETED + mergedCount'],
            ['AC-04', '\u8fd0\u8425\u8f68\u5199\u5165', 'rela_oper \u5305\u542b\u8be5\u4efb\u52a1\u5168\u90e8\u5b9e\u4f8b'],
            ['AC-05', 'biz_line \u9694\u79bb', 'OPEN \u4e0d\u5199 rela_report\uff0cASSESS \u4e0d\u5199 rela_oper'],
            ['AC-06', '\u5207\u65ad\u5047 orderId', 'open-api \u4e0d\u518d\u8c03 /vul-scan-task/dispatch'],
        ]))
card('\u5173\u8054\u6587\u6863',
    tbl(
        ['\u6587\u6863', '\u8def\u5f84'],
        [
            ['\u5bf9\u5916 API \u6587\u6863', 'svmp/docs/external/\u7f51\u7edc\u5b89\u5168\u6f0f\u6d1e\u7ba1\u7406\u5e73\u53f0 API \u63a5\u53e3\u6587\u6863.md'],
            ['Internal API \u5916\u5305', 'svmp/docs/internal/open-api-vtc-pass-internal-api.yaml'],
            ['\u9875\u9762\u539f\u578b', 'svmp/docs/internal/prototypes/open-api-vtc-pass-prototype-v1.html'],
            ['\u53cc\u8f68\u5b58\u50a8\u65b9\u6848', 'svmp/docs/internal/\u6f0f\u6d1e\u5b9e\u4f8b\u4e0e\u751f\u547d\u5468\u671f\u53cc\u8f68\u5b58\u50a8-\u843d\u5730\u65b9\u6848.md'],
        ]))
sec_close()

# ---- footer + JS -----------------------------------------------------------
a('<p style="text-align:center;padding:20px;font-size:12px">')
a('PRD v1.0 \u00b7 OPEN \u7f16\u6392 \u00b7 SOC \u53cc\u626b\u5168\u94fe\u8def \u00b7 2026-06-16 \u00b7 SVMP')
a('</p>')
a('</div></div></div>')

JS = (
    '<script>(function(){'
    'var items=document.querySelectorAll(".nav-item[data-sec]");'
    'var secs=document.querySelectorAll(".section");'
    'function show(id){'
    'secs.forEach(function(s){s.classList.remove("active")});'
    'items.forEach(function(i){i.classList.remove("active")});'
    'var s=document.getElementById("sec-"+id);if(s)s.classList.add("active");'
    "var n=document.querySelector('.nav-item[data-sec=\"'+id+'\"]');if(n)n.classList.add(\"active\")"
    '}'
    'items.forEach(function(i){i.addEventListener("click",function(){show(i.dataset.sec)})});'
    '})();</script>'
)
a(JS)
a('</body></html>')

# ---- write output ----------------------------------------------------------
TARGET = Path(__file__).resolve().parent.parent / "prototypes" / "open-api-vtc-prd-v1.html"

if __name__ == "__main__":
    html = "".join(PARTS)
    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("OK:", TARGET, "bytes", len(html.encode("utf-8")))
