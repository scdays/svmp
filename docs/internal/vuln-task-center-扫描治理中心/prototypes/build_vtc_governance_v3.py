# -*- coding: utf-8 -*-
"""Build vuln-task-center governance prototype v3 (UTF-8)."""

from pathlib import Path

ROOT = Path(__file__).parent
CSS_SRC = ROOT / "v3-chunk-head.css"
OUT = ROOT / "vuln-task-center-governance-prototype-v3.html"

EXTRA_CSS = """
    .diff-table td.diff-add { background: #f6ffed; }
    .diff-table td.diff-del { background: #fff2f0; }
    .checkbox-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
    .checkbox-item { display: flex; align-items: center; gap: 6px; padding: 6px 10px; border: 1px solid #f0f0f0; border-radius: 2px; font-size: 13px; }
    .node-card { border: 1px solid #f0f0f0; border-radius: 2px; padding: 12px 16px; cursor: pointer; }
    .node-card.selected { border-color: var(--primary); background: #e6f7ff; }
    .score-badge { background: var(--success); color: #fff; padding: 2px 8px; border-radius: 2px; font-size: 12px; }
    .helper { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
    .required::before { content: "* "; color: var(--error); }
    .sitemap-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .sitemap-card { border: 1px solid #f0f0f0; border-radius: 2px; padding: 16px; cursor: pointer; transition: box-shadow .2s; }
    .sitemap-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,.08); }
    .sitemap-card h3 { font-size: 15px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .sitemap-card ul { margin-left: 16px; color: var(--text-secondary); font-size: 13px; line-height: 1.8; }
    .detail-sidebar .card-body { padding: 12px 16px; }
    .quick-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .matrix-cell { min-width: 100px; }
    .matrix-progress { font-size: 11px; color: var(--text-secondary); margin-top: 4px; }
"""


def read_head():
    text = CSS_SRC.read_text(encoding="utf-8")
    if "<title>" in text:
        start = text.index("<title>") + len("<title>")
        end = text.index("</title>")
        text = text[:start] + "ɨ���������� �� ȫ����ԭ�� v3���������ģ�" + text[end:]
    text = text.replace("</style>", EXTRA_CSS + "\n  </style>", 1)
    return text


def report_matrix_html():
    subtasks = [
        ("ST-20260614-001", "874", "10.65.195.0/24", "�����", "tag-green", "MATCHED"),
        ("ST-20260614-002", "875", "10.65.196.0/24", "ִ����", "tag-blue", "DRIFT"),
        ("ST-MISS-001", "��", "10.65.197.0/24", "ִ����", "tag-orange", "MISSING"),
    ]
    templates = [
        ("vuln_summary", "©�����ܱ���", "LM", "report_type=1"),
        ("host_detail", "����©����ϸ", "LM", "report_type=2"),
        ("baseline_rpt", "���ߺ˲鱨��", "AH", "report_type=3"),
        ("weakpwd_rpt", "�������", "LM", "report_type=4"),
    ]
    header = "<tr><th>������ \\ ����ģ��</th>"
    for _, tname, vendor, _ in templates:
        header += f"<th>{tname}<br><small style='font-weight:400;color:var(--text-secondary)'>{vendor}</small></th>"
    header += "</tr>"
    rows = []
    for st_id, plan, target, status, tag_cls, recon in subtasks:
        row = f"<tr><td><strong>{st_id}</strong><br><small>plan={plan} �� {target}</small><br><span class='tag {tag_cls}'>{status}</span> �� {recon}</td>"
        for tcode, tname, vendor, rtype in templates:
            cell_id = f"cell-{st_id}-{tcode}"
            if st_id == "ST-20260614-001" and tcode == "vuln_summary":
                row += f"""<td class="matrix-cell"><span class="tag tag-green">������</span>
                  <div class="matrix-progress">2026-06-14 10:18</div>
                  <button class="btn-link" onclick="toast('���� report_job RJ-001')">����</button></td>"""
            elif st_id == "ST-20260614-002" and tcode == "host_detail":
                row += f"""<td class="matrix-cell"><span class="tag tag-orange">������</span>
                  <div class="progress-bar" style="margin:6px 0"><span id="{cell_id}" style="width:62%"></span></div>
                  <div class="matrix-progress">LM generate_report 62%</div></td>"""
            elif st_id == "ST-MISS-001":
                row += f"""<td class="matrix-cell"><span class="tag tag-default">�ȴ�ɨ��</span>
                  <button class="btn-link" disabled style="opacity:.45">����</button></td>"""
            elif tcode == "baseline_rpt" and vendor == "AH":
                row += f"""<td class="matrix-cell"><span class="tag tag-red">ʧ��</span>
                  <div class="matrix-progress">AH ģ��δ��</div>
                  <button class="btn-link" onclick="openReportGenerateModal('{st_id}','{tcode}')">����</button></td>"""
            else:
                row += f"""<td class="matrix-cell"><span class="tag tag-default">δ����</span>
                  <button class="btn-link" onclick="openReportGenerateModal('{st_id}','{tcode}')">����</button></td>"""
        row += "</tr>"
        rows.append(row)
    return header + "\n" + "\n".join(rows)


def capability_rows(vendor):
    caps = [
        ("task.create", "POST /api/task/create", "��", "��", "dev-done", "Adapter"),
        ("task.active_list", "GET /api/task/active_list", "��", "active_list", "dev-done", "VulnTaskListener"),
        ("task.pause", "POST /api/task/pause/{id}", "��", "task_pause", "dev-todo", "P0"),
        ("task.resume", "POST /api/task/resume/{id}", "��", "��", "dev-todo", "P0"),
        ("system.status", "GET /api/system/status", "��", "sys_status", "dev-done", "Metrics"),
        ("report.generate", "POST /api/report/generate", "��", "��", "dev-todo", "P1"),
        ("template.sysvuln.list", "GET /api/template/sysvuln/list", "��", "syn_sysvuln", "dev-done", "SynVulnData"),
        ("template.baseline.list", "GET /api/template/baseline/list", "��", "syn_baseline", "dev-done", "SynVulnData"),
    ] if vendor == "LM" else [
        ("scan.host", "POST /ah/scan/host", "��", "��", "dev-todo", "AH Adapter"),
        ("scan.web", "POST /ah/scan/web", "��", "��", "dev-todo", "P1"),
        ("report.export", "GET /ah/report/{id}/export", "��", "��", "dev-todo", "P1"),
        ("asset.sync", "POST /ah/asset/sync", "��", "asset_sync", "dev-skip", "P2"),
    ]
    rows = []
    for code, api, req, syn, cls, note in caps:
        rows.append(
            f"<tr data-vendor='{vendor}'><td><code>{code}</code></td><td>{api}</td>"
            f"<td>{req}</td><td>{syn}</td><td><span class='{cls}'>{note}</span></td></tr>"
        )
    return "\n".join(rows)


def sidebar():
    return """
  <aside class="sidebar">
    <div class="sidebar-logo">ɨ����������<br><small style="font-weight:400;font-size:11px;opacity:.65">vuln-task-center v3</small></div>
    <nav>
      <div class="menu-group"><div class="menu-group-title">����̨</div>
        <div class="menu-item active" data-view="workbench">��������̨ <span class="phase p0">P0</span></div>
      </div>
      <div class="menu-group"><div class="menu-group-title">ɨ������</div>
        <div class="menu-item" data-view="survey-list">�ƻ�ʵ�� survey <span class="phase p0">P0</span></div>
        <div class="menu-item" data-view="survey-workspace">ʵ������̨ <span class="phase p0">����</span></div>
        <div class="menu-item" data-view="scan-wizard">�½�ɨ���� <span class="phase p0">P0</span></div>
      </div>
      <div class="menu-group"><div class="menu-group-title">��Դ����</div>
        <div class="menu-item" data-view="node-list">ɨ��ڵ� <span class="phase p0">P0</span></div>
        <div class="menu-item" data-view="node-form">���� / �༭�ڵ�</div>
        <div class="menu-item" data-view="node-detail">�ڵ�����</div>
        <div class="menu-item" data-view="scanner-list">�߼�ɨ����</div>
        <div class="menu-item" data-view="scene-list">ҵ�񳡾�</div>
        <div class="menu-item" data-view="capability-catalog">����Ŀ¼ <span class="phase p1">P1</span></div>
        <div class="menu-item" data-view="templates">ģ���ֵ� <span class="phase p2">P2</span></div>
      </div>
      <div class="menu-group"><div class="menu-group-title">��������</div>
        <div class="menu-item" data-view="report-jobs">�������� <span class="phase p1">P1</span></div>
        <div class="menu-item" data-view="report-templates">ģ��ӳ��</div>
        <div class="menu-item" data-view="report-exports">������¼</div>
      </div>
      <div class="menu-group"><div class="menu-group-title">��������</div>
        <div class="menu-item" data-view="reconcile-list">������� <span class="phase p0">P0</span></div>
        <div class="menu-item" data-view="reconcile-diff">��������</div>
        <div class="menu-item" data-view="queue">���м��</div>
        <div class="menu-item" data-view="dashboard">ɨ�����Ǳ��� <span class="phase p1">P1</span></div>
        <div class="menu-item" data-view="alert-rules">�澯����</div>
      </div>
    </nav>
  </aside>
"""


def topbar():
    return """
    <header class="topbar">
      <small>ɨ���������� v3 �� PRD v0.3 �� survey ʵ������̨Ϊ���� �� Mock vuln-task-center:18087</small>
      <div style="display:flex;gap:8px">
        <button class="btn" type="button" onclick="showView('reconcile-list')">��������</button>
        <button class="btn" type="button" onclick="openWorkspace('SUR-77821')">�� SUR-77821</button>
        <button class="btn btn-primary" type="button" onclick="showView('scan-wizard')">�½�ɨ��</button>
      </div>
    </header>
"""


def banner():
    return """
      <div class="mock-banner">
        <strong>ԭ�� v3</strong>���� <code>SUR-77821</code> ʵ������̨Ϊ���� �� 6 Tab ȫ�������� ��
        ���� sub_task��ģ����� �� S2/S3/S5 ���¿�Ƭ�ڹ���̨ ��
        ��ע <span class="dev-done">dev-done</span> / <span class="dev-todo">dev-todo</span> �� API ·����
      </div>
"""


def view_workbench():
    return """
      <section id="view-workbench" class="view active">
        <div class="breadcrumb">����̨ / ��������̨</div>
        <div class="legend">
          <span class="dev-done">dev-done ��ʵ��</span>
          <span class="dev-todo">dev-todo ������</span>
          <span class="phase p0">P0</span><span class="phase p1">P1</span><span class="phase p2">P2</span>
        </div>
        <div class="stat-row">
          <div class="stat-card" onclick="showView('survey-list')"><div class="label">ִ����ʵ��</div><div class="value">18</div><div class="sub">survey ������</div></div>
          <div class="stat-card" onclick="showView('reconcile-list')"><div class="label">���˲���</div><div class="value" style="color:var(--error)">5</div><div class="sub">ORPHAN 2 �� MISSING 1 �� DRIFT 2</div></div>
          <div class="stat-card" onclick="showView('report-jobs')"><div class="label">����ʧ��</div><div class="value" style="color:var(--warning)">3</div><div class="sub">report_job FAILED</div></div>
          <div class="stat-card" onclick="showView('node-list')"><div class="label">offline �ڵ�</div><div class="value" style="color:var(--error)">1</div><div class="sub">����-ʡ����</div></div>
          <div class="stat-card" onclick="showView('queue')"><div class="label">���л�ѹ</div><div class="value">23</div><div class="sub">send 8 �� wait 15</div></div>
        </div>
        <div class="card">
          <div class="card-title">�������� <span class="api-path">GET /v1/governance/todos</span> <span class="dev-todo">P0</span></div>
          <div class="card-body" style="padding:0">
            <div class="todo-list">
              <div class="todo-item" onclick="showView('reconcile-diff')"><span><span class="tag tag-orange">MISSING</span> ST-MISS-001 �� ����-102 �� ��ʱ 15min δ������ active_list</span><span class="btn-link">���� ��</span></div>
              <div class="todo-item" onclick="openModal('orphan')"><span><span class="tag tag-red">ORPHAN</span> task_id=882 �� ����-����-01 �� �豸������ƽ̨�޼�¼</span><span class="btn-link">���� ��</span></div>
              <div class="todo-item" onclick="showView('report-jobs')"><span><span class="tag tag-red">���� failed</span> RJ-20260614-003 �� baseline_rpt �� AH ģ��δ��</span><span class="btn-link">���� ��</span></div>
              <div class="todo-item" onclick="showView('node-detail')"><span><span class="tag tag-red">offline</span> ����-ʡ���� �� ̽��ʧ�� 08:15:00</span><span class="btn-link">�鿴 ��</span></div>
              <div class="todo-item" onclick="showView('queue')"><span><span class="tag tag-blue">����</span> waitQueue 15 �� �� ����-�Ϻ�-02 ��������</span><span class="btn-link">��� ��</span></div>
            </div>
          </div>
        </div>
        <div class="story-cards">
          <div class="story-card" onclick="openWorkspace('SUR-77821')"><strong>S2 �� �����·�</strong>vul-pass ���� �� preview-scanners �� Router ѡ�ڵ� �� Adapter �·� �� scan_sub_task</div>
          <div class="story-card" onclick="showView('reconcile-list')"><strong>S3 �� ���˻ָ�</strong>Cron reconcile �� active_list �Ա� �� MISSING ���� �� POST retry �����·�</div>
          <div class="story-card" onclick="openSubTaskDrawer('ST-20260614-002')"><strong>S5 �� Ư�Ʋٿ�</strong>DRIFT ��� �� sync-status �� pause / resume �˹���Ԥ</div>
        </div>
        <div class="card">
          <div class="card-title">��ݲ���</div>
          <div class="card-body">
            <div class="quick-actions">
              <button class="btn btn-primary" onclick="showView('scan-wizard')">�½�ɨ��</button>
              <button class="btn" onclick="showView('reconcile-list')">��������</button>
              <button class="btn" onclick="toast('POST /v1/reconcile/tasks/trigger')">���� reconcile</button>
              <button class="btn" onclick="showView('report-jobs')">��������</button>
              <button class="btn" onclick="showView('node-list')">�ڵ����</button>
              <button class="btn" onclick="openWorkspace('SUR-77821')">��ʵ������̨</button>
            </div>
          </div>
        </div>
        <div class="sitemap-grid">
          <div class="sitemap-card" onclick="showView('survey-workspace')"><h3>ʵ������̨ <span class="phase p0">����</span></h3><ul><li>6 Tab ȫ��������</li><li>������� generate/download</li><li>SUR-77821 Mock ��������</li></ul></div>
          <div class="sitemap-card" onclick="showView('capability-catalog')"><h3>����Ŀ¼ LM/AH</h3><ul><li>���� Profile �л�</li><li>Capability Registry</li><li>syn_type ӳ��</li></ul></div>
          <div class="sitemap-card" onclick="showView('report-jobs')"><h3>��������</h3><ul><li>report_job ȫƽ̨</li><li>ģ�� code �� LM report_type</li><li>����Ͷ����ʷ</li></ul></div>
          <div class="sitemap-card" onclick="showView('dashboard')"><h3>�����۲�</h3><ul><li>��Ⱥ��������</li><li>����ˮλ</li><li>�澯����</li></ul></div>
        </div>
      </section>
"""


def view_survey_list():
    return """
      <section id="view-survey-list" class="view">
        <div class="breadcrumb"><a onclick="showView('workbench')">����̨</a> / ɨ������ / �ƻ�ʵ��</div>
        <div class="card"><div class="card-body"><div class="search-row">
          <div class="form-item"><label>surveyId / ����</label><input placeholder="SUR-77821" /></div>
          <div class="form-item"><label>����</label><select><option>ȫ��</option><option>©��ɨ��</option><option>���ߺ˲�</option><option>������</option></select></div>
          <div class="form-item"><label>״̬</label><select><option>ȫ��</option><option>ִ����</option><option>�����</option><option>ʧ��</option></select></div>
          <div class="form-item"><label>����</label><select><option>ȫ��</option><option>�в���</option><option>ȫ�� MATCHED</option></select></div>
          <div class="form-item"><label>&nbsp;</label><button class="btn btn-primary">��ѯ</button><button class="btn">����</button></div>
        </div></div></div>
        <div class="card">
          <div class="card-title"><span>�ƻ�ʵ�� survey <span class="api-path">GET /v1/scan/task</span> <span class="dev-done">����</span></span>
            <button class="btn btn-primary" onclick="showView('scan-wizard')">�½�ɨ��</button></div>
          <div class="card-body" style="padding-top:0">
            <table>
              <thead><tr><th>surveyId</th><th>�ƻ�/����</th><th>����</th><th>������</th><th>����</th><th>����</th><th>����</th><th>����ʱ��</th><th>����</th></tr></thead>
              <tbody>
                <tr><td><code>SUR-77821</code></td><td>����-102-©���Ų�</td><td>©��ɨ��</td><td>3</td>
                  <td><div class="progress-bar"><span style="width:45%"></span></div><small>45%</small></td>
                  <td><span class="tag tag-orange">1 MISSING</span> <span class="tag tag-blue">1 DRIFT</span></td>
                  <td><span class="tag tag-green">1/12</span> <span class="tag tag-red">1 failed</span></td>
                  <td>2026-06-14 10:00</td>
                  <td><button class="btn-link" onclick="openWorkspace('SUR-77821')">���빤��̨</button>
                      <button class="btn-link" onclick="openSubTaskDrawer('ST-20260614-002')">������</button></td></tr>
                <tr><td><code>SUR-77805</code></td><td>�¶�©��ɨ��</td><td>©��ɨ��</td><td>5</td>
                  <td><div class="progress-bar"><span style="width:78%"></span></div><small>78%</small></td>
                  <td><span class="tag tag-green">ȫ�� MATCHED</span></td>
                  <td><span class="tag tag-green">8/20</span></td>
                  <td>2026-06-13 02:00</td>
                  <td><button class="btn-link" onclick="openWorkspace('SUR-77805')">���빤��̨</button></td></tr>
                <tr><td><code>SUR-77790</code></td><td>���߼��Ⱥ˲�</td><td>���ߺ˲�</td><td>2</td>
                  <td><div class="progress-bar"><span style="width:100%"></span></div><small>100%</small></td>
                  <td><span class="tag tag-green">MATCHED</span></td>
                  <td><span class="tag tag-green">4/4</span></td>
                  <td>2026-06-10 03:00</td>
                  <td><button class="btn-link" onclick="openWorkspace('SUR-77790')">���빤��̨</button></td></tr>
                <tr><td><code>SUR-77788</code></td><td>������ר��</td><td>������</td><td>1</td>
                  <td><div class="progress-bar"><span style="width:12%"></span></div><small>12%</small></td>
                  <td><span class="tag tag-default">��</span></td>
                  <td><span class="tag tag-default">0/3</span></td>
                  <td>2026-06-14 09:30</td>
                  <td><button class="btn-link" onclick="openWorkspace('SUR-77788')">���빤��̨</button></td></tr>
              </tbody>
            </table>
            <div class="pagination"><span>�� 128 ��</span><button class="btn">��һҳ</button><span>1 / 13</span><button class="btn">��һҳ</button></div>
          </div>
        </div>
      </section>
"""


def view_survey_workspace():
    matrix = report_matrix_html()
    return f"""
      <section id="view-survey-workspace" class="view">
        <div class="breadcrumb"><a onclick="showView('workbench')">����̨</a> / <a onclick="showView('survey-list')">�ƻ�ʵ��</a> / ʵ������̨</div>
        <div class="workspace-header">
          <div>
            <div class="workspace-title" id="ws-title">SUR-77821 �� ����-102-©���Ų�</div>
            <div class="workspace-meta">������©��ɨ�� �� ������ 3 �� �ۺϽ��� 45% �� ���� 2026-06-14 10:00 �� workOrderId WO-102</div>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn" onclick="toast('POST pause survey')">��ͣʵ��</button>
            <button class="btn" onclick="toast('POST sync-status')">sync-status</button>
            <button class="btn btn-primary" onclick="switchWsTab('report')">��������</button>
            <button class="btn" onclick="showView('survey-list')">�����б�</button>
          </div>
        </div>
        <div class="stat-row">
          <div class="stat-card"><div class="label">������</div><div class="value">3</div><div class="sub">1 ��� �� 2 ִ����</div></div>
          <div class="stat-card"><div class="label">����</div><div class="value" style="color:var(--warning)">2</div><div class="sub">MISSING 1 �� DRIFT 1</div></div>
          <div class="stat-card"><div class="label">����</div><div class="value">1/12</div><div class="sub">1 ������ �� 1 ʧ��</div></div>
          <div class="stat-card"><div class="label">©����</div><div class="value">847</div><div class="sub">��Σ 23 �� ��Σ 156</div></div>
          <div class="stat-card"><div class="label">�ڵ�</div><div class="value">2</div><div class="sub">����-01 �� �Ϻ�-02</div></div>
        </div>
        <div class="card">
          <div class="tabs" id="wsTabs">
            <div class="tab active" data-wstab="overview">����</div>
            <div class="tab" data-wstab="subtasks">������</div>
            <div class="tab" data-wstab="dispatch">�·�����</div>
            <div class="tab" data-wstab="reconcile">����</div>
            <div class="tab" data-wstab="result">���ժҪ</div>
            <div class="tab" data-wstab="report">����</div>
          </div>
          <div class="card-body">
            <div id="wstab-overview" class="tab-panel active">
              <div class="detail-grid">
                <div>
                  <div class="kv-row"><div class="k">surveyId</div><div class="v"><code>SUR-77821</code></div></div>
                  <div class="kv-row"><div class="k">����</div><div class="v">WO-102-©���Ų�</div></div>
                  <div class="kv-row"><div class="k">����</div><div class="v">vuln_scan �� ©��ɨ��</div></div>
                  <div class="kv-row"><div class="k">��֯</div><div class="v">ʡ��˾/�Ű���</div></div>
                  <div class="kv-row"><div class="k">״̬</div><div class="v"><span class="tag tag-blue">ִ����</span></div></div>
                  <div class="kv-row"><div class="k">API</div><div class="v"><span class="api-path">GET /v1/scan/task/SUR-77821</span></div></div>
                </div>
                <div>
                  <h4 style="margin-bottom:12px;font-weight:500">Ŀ�귶Χ</h4>
                  <pre class="code-block">10.65.195.0/24  �� ����-����-01  (ST-20260614-001 �����)
10.65.196.0/24  �� ����-����-01  (ST-20260614-002 DRIFT 45%)
10.65.197.0/24  �� ����-�Ϻ�-02  (ST-MISS-001 MISSING 12%)</pre>
                  <div class="timeline" style="margin-top:16px">
                    <div class="timeline-item"><div class="t">10:00:00</div>vul-pass ���� survey SUR-77821</div>
                    <div class="timeline-item"><div class="t">10:00:05</div>preview-scanners ·����ɣ����� 3 ��������</div>
                    <div class="timeline-item"><div class="t">10:05:00</div>Adapter task.create �·� plan_id 874/875</div>
                    <div class="timeline-item warn"><div class="t">10:20:00</div>���� MISSING��ST-MISS-001 ��ʱδ������ active_list</div>
                    <div class="timeline-item warn"><div class="t">10:25:00</div>���� DRIFT��ST-20260614-002 �豸����ͣ</div>
                  </div>
                </div>
              </div>
            </div>
            <div id="wstab-subtasks" class="tab-panel">
              <div class="toolbar"><span><span class="api-path">GET /v1/scan/sub-task?surveyId=SUR-77821</span></span>
                <button class="btn btn-primary" onclick="toast('POST retry-all')">��������</button></div>
              <table>
                <thead><tr><th>sub_task_id</th><th>�ڵ�</th><th>Ŀ��</th><th>plan_id</th><th>����</th><th>״̬</th><th>����</th><th>����</th></tr></thead>
                <tbody>
                  <tr><td><code>ST-20260614-001</code></td><td>����-����-01</td><td>10.65.195.0/24</td><td>874</td><td>100%</td>
                    <td><span class="tag tag-green">�����</span></td><td>MATCHED</td>
                    <td><button class="btn-link" onclick="openSubTaskDrawer('ST-20260614-001')">����</button></td></tr>
                  <tr><td><code>ST-20260614-002</code></td><td>����-����-01</td><td>10.65.196.0/24</td><td>875</td><td>45%</td>
                    <td><span class="tag tag-blue">ִ����</span></td><td><span class="tag tag-blue">DRIFT</span></td>
                    <td><button class="btn-link" onclick="openSubTaskDrawer('ST-20260614-002')">�ٿ� S5</button></td></tr>
                  <tr><td><code>ST-MISS-001</code></td><td>����-�Ϻ�-02</td><td>10.65.197.0/24</td><td>��</td><td>12%</td>
                    <td><span class="tag tag-orange">ִ����</span></td><td><span class="tag tag-orange">MISSING</span></td>
                    <td><button class="btn-link" onclick="toast('POST retry')">����</button>
                        <button class="btn-link" onclick="showView('reconcile-diff')">����</button></td></tr>
                </tbody>
              </table>
            </div>
            <div id="wstab-dispatch" class="tab-panel">
              <p class="helper" style="margin-bottom:12px"><span class="api-path">GET /v1/scan/task/SUR-77821/dispatch-detail</span> �� ������ƽ̨���� / ·�ɽ�� / ������ۺ�</p>
              <div class="three-col">
                <div class="col-box"><h4>�� ƽ̨�������</h4>
                  <pre class="code-block">{{
  "workOrderId": "WO-102",
  "scene": "vuln_scan",
  "targets": ["10.65.195.0/24","10.65.196.0/24","10.65.197.0/24"],
  "orgId": "ORG-001",
  "templateId": 10,
  "templateName": "�˿�ɨ��"
}}</pre></div>
                <div class="col-box"><h4>�� ·�� / preview-scanners</h4>
                  <ul style="font-size:12px;line-height:1.8;padding-left:16px">
                    <li>10.65.195.0/24 �� ����-����-01 (92��)</li>
                    <li>10.65.196.0/24 �� ����-����-01 (88��)</li>
                    <li>10.65.197.0/24 �� ����-�Ϻ�-02 (71��)</li>
                  </ul>
                  <p class="helper">QueueAppServiceImpl.getNodeScannerMap</p></div>
                <div class="col-box"><h4>�� ������ۺ�</h4>
                  <table style="font-size:12px"><tr><td>ST-001</td><td>100%</td><td>MATCHED</td></tr>
                  <tr><td>ST-002</td><td>45%</td><td><span class="tag tag-blue">DRIFT</span></td></tr>
                  <tr><td>ST-MISS</td><td>12%</td><td><span class="tag tag-orange">MISSING</span></td></tr></table>
                  <p style="margin-top:8px">�ۺ� 45% �� matched 1 / missing 1 / drift 1</p></div>
              </div>
            </div>
            <div id="wstab-reconcile" class="tab-panel">
              <div class="toolbar"><span>ʵ��ά�ȶ��˿��� �� Cron 5min</span>
                <button class="btn btn-primary" onclick="toast('POST /v1/reconcile/tasks/trigger')">��������</button></div>
              <table>
                <thead><tr><th>����</th><th>sub_task</th><th>task_id</th><th>ƽ̨</th><th>�豸</th><th>����</th></tr></thead>
                <tbody>
                  <tr><td><span class="tag tag-green">MATCHED</span></td><td>ST-20260614-001</td><td>874</td><td>�����</td><td>���</td><td>��</td></tr>
                  <tr><td><span class="tag tag-blue">DRIFT</span></td><td>ST-20260614-002</td><td>875</td><td>ִ���� 45%</td><td>��ͣ 60%</td>
                    <td><button class="btn-link" onclick="openSubTaskDrawer('ST-20260614-002')">sync/pause</button></td></tr>
                  <tr><td><span class="tag tag-orange">MISSING</span></td><td>ST-MISS-001</td><td>��</td><td>ִ���� 12%</td><td>��</td>
                    <td><button class="btn-link" onclick="showView('reconcile-diff')">����</button>
                        <button class="btn-link" onclick="toast('retry')">����</button></td></tr>
                </tbody>
              </table>
            </div>
            <div id="wstab-result" class="tab-panel">
              <div class="stat-row">
                <div class="stat-card"><div class="label">©������</div><div class="value">847</div></div>
                <div class="stat-card"><div class="label">��Σ</div><div class="value" style="color:var(--error)">23</div></div>
                <div class="stat-card"><div class="label">��Σ</div><div class="value" style="color:var(--warning)">156</div></div>
                <div class="stat-card"><div class="label">��Σ</div><div class="value">668</div></div>
                <div class="stat-card"><div class="label">������</div><div class="value">512</div></div>
              </div>
              <div class="chart-placeholder">©���ֲ� TOP10 �� ��������ۺ� �� GET /v1/scan/task/SUR-77821/result-summary</div>
              <table style="margin-top:16px">
                <thead><tr><th>������</th><th>Ŀ��</th><th>����</th><th>��Σ</th><th>��Σ</th><th>��Σ</th><th>״̬</th></tr></thead>
                <tbody>
                  <tr><td>ST-20260614-001</td><td>10.65.195.0/24</td><td>256</td><td>12</td><td>89</td><td>412</td><td><span class="tag tag-green">�����</span></td></tr>
                  <tr><td>ST-20260614-002</td><td>10.65.196.0/24</td><td>156</td><td>8</td><td>45</td><td>198</td><td><span class="tag tag-blue">�������</span></td></tr>
                  <tr><td>ST-MISS-001</td><td>10.65.197.0/24</td><td>��</td><td>��</td><td>��</td><td>��</td><td><span class="tag tag-orange">�ȴ����</span></td></tr>
                </tbody>
              </table>
            </div>
            <div id="wstab-report" class="tab-panel">
              <div class="toolbar">
                <span>������� �� ��=sub_task �� ��=����ģ�� <span class="api-path">POST /v1/report/generate</span> <span class="dev-todo">P1</span></span>
                <button class="btn btn-primary" onclick="openReportGenerateModal('ST-20260614-002','vuln_summary')">��������</button>
              </div>
              <table class="report-matrix">
                <thead>{matrix}</thead>
                <tbody></tbody>
              </table>
              <p class="helper" style="margin-top:12px">Mock��LM generate_report �� progress ��ѯ �� download �� ʧ�ܿ� retry �� AH ģ�����Ȱ� report-templates</p>
              <h4 style="margin:16px 0 8px;font-weight:500">��� report_job</h4>
              <table>
                <thead><tr><th>job_id</th><th>sub_task</th><th>ģ��</th><th>״̬</th><th>����</th><th>����</th></tr></thead>
                <tbody>
                  <tr><td>RJ-001</td><td>ST-20260614-001</td><td>©�����ܱ���</td><td><span class="tag tag-green">SUCCESS</span></td><td>100%</td>
                    <td><button class="btn-link" onclick="toast('���� PDF')">����</button></td></tr>
                  <tr><td>RJ-002</td><td>ST-20260614-002</td><td>����©����ϸ</td><td><span class="tag tag-orange">RUNNING</span></td><td>62%</td>
                    <td><button class="btn-link" onclick="mockReportProgress('RJ-002')">ˢ��</button></td></tr>
                  <tr><td>RJ-003</td><td>ST-20260614-002</td><td>���ߺ˲鱨��</td><td><span class="tag tag-red">FAILED</span></td><td>��</td>
                    <td><button class="btn-link" onclick="openReportGenerateModal('ST-20260614-002','baseline_rpt')">����</button></td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
"""


def view_scan_wizard():
    return """
      <section id="view-scan-wizard" class="view">
        <div class="breadcrumb"><a onclick="showView('workbench')">����̨</a> / ɨ������ / �½�ɨ����</div>
        <div class="card">
          <div class="card-title">�½�ɨ�� �� 4 ���� <span class="api-path">POST /v1/scan/task</span> <span class="dev-done">QueueAppServiceImpl</span></div>
          <div class="card-body">
            <div class="wizard-steps" id="wizardSteps">
              <div class="wizard-step active" data-wstep="1">�� ����</div>
              <div class="wizard-step" data-wstep="2">�� Ŀ��</div>
              <div class="wizard-step" data-wstep="3">�� preview-scanners</div>
              <div class="wizard-step" data-wstep="4">�� ȷ���·�</div>
            </div>
            <div id="wstep-1" class="wizard-panel active">
              <div class="form-grid">
                <div class="form-item"><label class="required">ҵ�񳡾�</label>
                  <select id="wizScene"><option value="vuln_scan">©��ɨ�� vuln_scan</option><option value="baseline">���ߺ˲� baseline</option><option value="weakpwd">������ weakpwd</option></select></div>
                <div class="form-item"><label class="required">ɨ��ģ��</label>
                  <select><option>�˿�ɨ�� (sysvuln id=10)</option><option>ȫ�˿�ɨ��</option><option>Windows ���ù淶</option></select></div>
                <div class="form-item"><label>������</label><input placeholder="WO-xxx����ѡ��" value="WO-103" /></div>
                <div class="form-item"><label>��֯</label><select><option>ʡ��˾/�Ű���</option><option>����/���粿</option></select></div>
                <div class="form-item full"><label>��ע</label><textarea>����©��ɨ�� �� ���� vul-pass ����</textarea></div>
              </div>
            </div>
            <div id="wstep-2" class="wizard-panel">
              <div class="form-grid">
                <div class="form-item full"><label class="required">ɨ��Ŀ�� IP / ����</label>
                  <textarea id="wizTargets" style="width:100%;min-height:120px">10.65.195.0/24
10.65.196.0/24
10.65.197.0/24</textarea>
                  <p class="helper">ÿ��һ��Ŀ�֧꣬�� CIDR �� ��� 50 ��</p></div>
                <div class="form-item"><label>ƾ����</label><select><option>Ĭ�� SSH ƾ��</option><option>SNMP v2c</option></select></div>
                <div class="form-item"><label>ɨ�����</label><select><option>��׼</option><option>���</option><option>����</option></select></div>
              </div>
            </div>
            <div id="wstep-3" class="wizard-panel">
              <p class="helper" style="margin-bottom:12px"><span class="api-path">POST /v1/scan/task/preview-scanners</span> �� ���÷������ѡɨ����</p>
              <button class="btn btn-primary" onclick="runWizardPreview()" style="margin-bottom:16px">Ԥ����ѡɨ����</button>
              <div id="wizPreviewResult" class="hidden">
                <div class="node-card selected" style="margin-bottom:8px"><h4 style="display:flex;justify-content:space-between;font-size:14px">����-����-01 <span class="score-badge">92</span></h4>
                  <p style="font-size:13px;color:var(--text-secondary)">10.65.195.0/24 + 196.0/24 �� ���� 3/10 �� ����ƥ��</p></div>
                <div class="node-card" style="margin-bottom:8px"><h4 style="display:flex;justify-content:space-between;font-size:14px">����-�Ϻ�-02 <span style="color:var(--warning)">71</span></h4>
                  <p style="font-size:13px;color:var(--text-secondary)">10.65.197.0/24 �� ���� 9/10 �� ��Χƥ��</p></div>
                <ul style="font-size:12px;color:var(--text-secondary);margin-top:12px;padding-left:20px;line-height:1.8">
                  <li>����-ʡ���� �� excluded��offline</li>
                  <li>����-����-03 �� excluded��ɨ�跶Χ��ƥ��</li>
                </ul>
              </div>
            </div>
            <div id="wstep-4" class="wizard-panel">
              <h4 style="margin-bottom:12px;font-weight:500">ȷ���·�</h4>
              <div class="kv-row"><div class="k">����</div><div class="v">©��ɨ�� �� �˿�ɨ��</div></div>
              <div class="kv-row"><div class="k">Ŀ��</div><div class="v">3 ������ �� Ԥ�� 3 ��������</div></div>
              <div class="kv-row"><div class="k">·��</div><div class="v">����-����-01 (2) �� ����-�Ϻ�-02 (1)</div></div>
              <div class="kv-row"><div class="k">API</div><div class="v"><span class="api-path">POST /v1/scan/task</span> �� surveyId</div></div>
              <pre class="code-block" style="margin-top:12px">{
  "scene": "vuln_scan",
  "targets": ["10.65.195.0/24","10.65.196.0/24","10.65.197.0/24"],
  "templateId": 10,
  "orgId": "ORG-001"
}</pre>
            </div>
            <div style="margin-top:24px;display:flex;justify-content:space-between">
              <button class="btn" id="wizPrevBtn" onclick="wizardPrev()" disabled>��һ��</button>
              <div style="display:flex;gap:8px">
                <button class="btn" onclick="showView('survey-list')">ȡ��</button>
                <button class="btn btn-primary" id="wizNextBtn" onclick="wizardNext()">��һ��</button>
              </div>
            </div>
          </div>
        </div>
      </section>
"""
