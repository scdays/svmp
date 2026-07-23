# -*- coding: utf-8 -*-
"""One-shot generator: embed VTC governance HTML into build_vtc_governance_proto.py"""
from pathlib import Path

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ɨ���������� �� ȫ����ԭ�� v1��VTC-GOV PRD��</title>
  <style>
    :root {
      --primary: #1890ff; --success: #52c41a; --warning: #faad14; --error: #ff4d4f;
      --text: rgba(0,0,0,.85); --text-secondary: rgba(0,0,0,.45);
      --border: #d9d9d9; --bg: #f0f2f5; --card: #fff; --sidebar: #001529;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 14px; color: var(--text); background: var(--bg); }
    .app-shell { display: flex; min-height: 100vh; }
    .sidebar { width: 240px; background: var(--sidebar); color: #fff; flex-shrink: 0; overflow-y: auto; }
    .sidebar-logo { height: 64px; display: flex; align-items: center; padding: 0 20px; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,.1); }
    .menu-group { padding: 12px 0 4px; }
    .menu-group-title { padding: 4px 20px; font-size: 11px; color: rgba(255,255,255,.35); letter-spacing: .5px; }
    .menu-item { padding: 8px 20px 8px 36px; color: rgba(255,255,255,.65); cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: space-between; }
    .menu-item:hover { color: #fff; background: rgba(255,255,255,.05); }
    .menu-item.active { background: var(--primary); color: #fff; }
    .main-area { flex: 1; display: flex; flex-direction: column; min-width: 0; }
    .topbar { height: 48px; background: var(--card); border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
    .topbar small { color: var(--text-secondary); }
    .content { padding: 16px; flex: 1; overflow: auto; }
    .view { display: none; } .view.active { display: block; }
    .phase { font-size: 10px; padding: 1px 6px; border-radius: 2px; font-weight: 500; }
    .p0 { background: #e6f7ff; color: #0958d9; border: 1px solid #91d5ff; }
    .p1 { background: #f6ffed; color: #389e0d; border: 1px solid #b7eb8f; }
    .p2 { background: #fff7e6; color: #d46b08; border: 1px solid #ffd591; }
    .p3 { background: #f9f0ff; color: #531dab; border: 1px solid #d3adf7; }
    .p4 { background: #fff1f0; color: #a8071a; border: 1px solid #ffa39e; }
    .alert { padding: 8px 15px; border-radius: 2px; margin-bottom: 16px; display: flex; gap: 8px; }
    .alert-info { background: #e6f7ff; border: 1px solid #91d5ff; color: #0958d9; }
    .hidden { display: none !important; }
    .breadcrumb { margin-bottom: 16px; color: var(--text-secondary); }
    .breadcrumb a { color: var(--primary); text-decoration: none; cursor: pointer; }
    .card { background: var(--card); border-radius: 2px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.03); }
    .card-title { padding: 14px 20px; border-bottom: 1px solid #f0f0f0; font-weight: 500; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
    .card-body { padding: 16px 20px; }
    .btn { height: 32px; padding: 0 15px; border: 1px solid var(--border); background: #fff; border-radius: 2px; cursor: pointer; font-size: 14px; }
    .btn-primary { background: var(--primary); border-color: var(--primary); color: #fff; }
    .btn-danger { background: var(--error); border-color: var(--error); color: #fff; }
    .btn-link { border: none; background: none; color: var(--primary); cursor: pointer; padding: 0 4px; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
    .search-row { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; }
    .form-item label { display: block; color: var(--text-secondary); margin-bottom: 4px; font-size: 13px; }
    .form-item input, .form-item select, .form-item textarea { height: 32px; padding: 0 11px; border: 1px solid var(--border); border-radius: 2px; min-width: 160px; font-size: 14px; }
    .form-item textarea { height: auto; padding: 8px 11px; min-height: 80px; width: 100%; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #f0f0f0; }
    th { background: #fafafa; font-weight: 500; }
    tr:hover td { background: #fafafa; }
    .tag { display: inline-block; padding: 0 7px; font-size: 12px; border-radius: 2px; line-height: 20px; border: 1px solid; }
    .tag-green { background: #f6ffed; border-color: #b7eb8f; color: #389e0d; }
    .tag-red { background: #fff2f0; border-color: #ffccc7; color: #cf1322; }
    .tag-blue { background: #e6f7ff; border-color: #91d5ff; color: #0958d9; }
    .tag-default { background: #fafafa; border-color: #d9d9d9; }
    .tag-orange { background: #fff7e6; border-color: #ffd591; color: #d46b08; }
    .tag-purple { background: #f9f0ff; border-color: #d3adf7; color: #531dab; }
    .tabs { display: flex; border-bottom: 1px solid #f0f0f0; flex-wrap: wrap; }
    .tab { padding: 10px 18px; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }
    .tab.active { color: var(--primary); border-bottom-color: var(--primary); }
    .tab-panel { display: none; padding: 20px; } .tab-panel.active { display: block; }
    .stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
    .stat-card { background: #fafafa; border: 1px solid #f0f0f0; border-radius: 2px; padding: 14px; }
    .stat-card .label { color: var(--text-secondary); font-size: 12px; }
    .stat-card .value { font-size: 22px; font-weight: 500; margin-top: 4px; }
    .chart-placeholder { height: 200px; background: linear-gradient(180deg,#fafafa,#f0f0f0); border: 1px dashed var(--border); border-radius: 2px; display: flex; align-items: center; justify-content: center; color: var(--text-secondary); margin-top: 12px; }
    .sitemap-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .sitemap-card { border: 1px solid #f0f0f0; border-radius: 2px; padding: 16px; cursor: pointer; transition: box-shadow .2s; }
    .sitemap-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,.08); }
    .sitemap-card h3 { font-size: 15px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .sitemap-card ul { margin-left: 16px; color: var(--text-secondary); font-size: 13px; line-height: 1.8; }
    .detail-header { padding: 16px 20px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    .detail-title { font-size: 18px; font-weight: 500; }
    .detail-meta { color: var(--text-secondary); font-size: 13px; margin-top: 4px; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px 24px; max-width: 900px; }
    .form-grid .full { grid-column: 1 / -1; }
    .helper { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
    .action-btn { color: var(--primary); cursor: pointer; margin-right: 10px; }
    .pagination { display: flex; justify-content: flex-end; align-items: center; gap: 8px; padding-top: 12px; color: var(--text-secondary); }
    .drawer-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: none; z-index: 1000; }
    .drawer-overlay.show { display: block; }
    .drawer { position: fixed; top: 0; right: 0; width: 520px; max-width: 90vw; height: 100vh; background: #fff; box-shadow: -2px 0 8px rgba(0,0,0,.15); display: flex; flex-direction: column; transform: translateX(100%); transition: transform .3s; z-index: 1001; }
    .drawer-overlay.show .drawer { transform: translateX(0); }
    .drawer-header { padding: 16px 20px; border-bottom: 1px solid #f0f0f0; font-weight: 500; display: flex; justify-content: space-between; align-items: center; }
    .drawer-body { padding: 20px; overflow: auto; flex: 1; }
    .drawer-footer { padding: 12px 20px; border-top: 1px solid #f0f0f0; text-align: right; display: flex; gap: 8px; justify-content: flex-end; }
    .kv-row { display: flex; margin-bottom: 10px; font-size: 13px; }
    .kv-row .k { width: 130px; color: var(--text-secondary); flex-shrink: 0; }
    .kv-row .v { flex: 1; word-break: break-all; }
    .kv-row .v code { background: #f5f5f5; padding: 2px 6px; border-radius: 2px; font-size: 12px; }
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: none; align-items: center; justify-content: center; z-index: 1002; padding: 24px; }
    .modal-overlay.show { display: flex; }
    .modal { background: #fff; border-radius: 2px; width: 100%; max-width: 640px; max-height: 90vh; overflow: auto; }
    .modal-header { padding: 14px 20px; border-bottom: 1px solid #f0f0f0; font-weight: 500; display: flex; justify-content: space-between; }
    .modal-body { padding: 20px; }
    .modal-footer { padding: 12px 20px; border-top: 1px solid #f0f0f0; text-align: right; display: flex; gap: 8px; justify-content: flex-end; }
    .api-path { font-family: Consolas, monospace; font-size: 12px; color: #531dab; }
    .filter-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
    .filter-chip { padding: 4px 12px; border: 1px solid var(--border); border-radius: 2px; cursor: pointer; font-size: 13px; background: #fff; }
    .filter-chip.active { border-color: var(--primary); color: var(--primary); background: #e6f7ff; }
    .legend { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; align-items: center; }
    .legend span { font-size: 12px; padding: 2px 8px; border-radius: 2px; }
    .dev-done { background: #f6ffed; color: #389e0d; border: 1px solid #b7eb8f; }
    .dev-todo { background: #fff7e6; color: #d46b08; border: 1px solid #ffd591; }
    .mock-banner { background: #fffbe6; border: 1px solid #ffe58f; padding: 10px 15px; border-radius: 2px; margin-bottom: 16px; font-size: 13px; }
    .drawer-wide { width: 720px; }
    .drawer-full { width: min(920px, 92vw); }
    .drawer-tabs { display: flex; border-bottom: 1px solid #f0f0f0; margin: -4px 0 16px; flex-wrap: wrap; }
    .drawer-tab { padding: 8px 14px; cursor: pointer; font-size: 13px; border-bottom: 2px solid transparent; margin-bottom: -1px; }
    .drawer-tab.active { color: var(--primary); border-bottom-color: var(--primary); }
    .drawer-panel { display: none; } .drawer-panel.active { display: block; }
    pre.code-block { background: #fafafa; border: 1px solid #f0f0f0; padding: 12px; border-radius: 2px; font-size: 12px; overflow: auto; max-height: 320px; white-space: pre-wrap; word-break: break-all; }
    .toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,.75); color: #fff; padding: 10px 20px; border-radius: 4px; font-size: 13px; z-index: 2000; opacity: 0; transition: opacity .25s; pointer-events: none; }
    .toast.show { opacity: 1; }
    .vendor-badge { font-size: 11px; padding: 0 6px; border-radius: 2px; background: #f5f5f5; border: 1px solid #e8e8e8; }
    .page-note { text-align: center; padding: 20px; color: var(--text-secondary); font-size: 12px; border-top: 1px dashed var(--border); margin-top: 20px; }
    @media (max-width: 960px) { .sitemap-grid, .stat-row { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<div class="app-shell">
  <aside class="sidebar">
    <div class="sidebar-logo">ɨ����������</div>
    <nav>
      <div class="menu-group">
        <div class="menu-group-title">����</div>
        <div class="menu-item active" data-view="overview">�������� / վ���ͼ</div>
      </div>
      <div class="menu-group">
        <div class="menu-group-title">P0 �� �豸������</div>
        <div class="menu-item" data-view="node-list">ɨ��ڵ��б�</div>
        <div class="menu-item" data-view="node-detail">�ڵ�����</div>
        <div class="menu-item" data-view="capability-catalog">����Ŀ¼</div>
        <div class="menu-item" data-view="scanner-list">����ע���</div>
      </div>
      <div class="menu-group">
        <div class="menu-group-title">P0 �� ��������</div>
        <div class="menu-item" data-view="reconcile">������� <span class="phase p0">P0</span></div>
      </div>
      <div class="menu-group">
        <div class="menu-group-title">P0-P1 �� �������</div>
        <div class="menu-item" data-view="survey-list">Survey �����б�</div>
        <div class="menu-item" data-view="preview-scanners">�·�ǰ�ڵ�Ԥ��</div>
        <div class="menu-item" data-view="queue">���й۲�</div>
      </div>
      <div class="menu-group">
        <div class="menu-group-title">P1-P2 �� ��Ӫ</div>
        <div class="menu-item" data-view="dashboard">��Ⱥ����</div>
        <div class="menu-item" data-view="template-sync">ģ��ͬ��</div>
        <div class="menu-item" data-view="auth-precheck">ƾ֤Ԥ��</div>
      </div>
      <div class="menu-group">
        <div class="menu-group-title">P3-P4 �� �߼�</div>
        <div class="menu-item" data-view="metrics-history">ָ����ʷ</div>
        <div class="menu-item" data-view="alert-rules">�澯����</div>
        <div class="menu-item" data-view="openapi-bridge">����ƽ̨�Ž�</div>
      </div>
    </nav>
  </aside>

  <div class="main-area">
    <header class="topbar">
      <small>vuln-task-center �� port 18087 �� HTML ԭ�� v1 �� VTC-GOV-P0~P4</small>
      <div>
        <button class="btn" type="button" onclick="openDispatchDrawer('SUR-20260614-001')">�·����� Drawer</button>
        <button class="btn btn-primary" type="button" onclick="openSubtaskDrawer('sub-001')">������ Drawer</button>
      </div>
    </header>

    <main class="content">
      <div class="alert alert-info">
        <span>?</span>
        <div>��ԭ�Ͷ��� PRD <strong>VTC-GOV-P0~P4</strong>����ʽ���뿪��ƽ̨����ԭ�ͣ�Ant Design ɫ�� / ���� / Drawer / Modal / Toast����P0 �ɽ� REST + Postman ���ա�</div>
      </div>

      <!-- �������� -->
      <section id="view-overview" class="view active">
        <div class="breadcrumb">ɨ���������� / ��������</div>
        <div class="card">
          <div class="card-title">ɨ���������� �� ȫ����վ���ͼ</div>
          <div class="card-body">
            <p style="margin-bottom:12px;color:var(--text-secondary);">΢���� <code>vuln-task-center</code> �� �ӡ������·�ͨ�����ݽ�Ϊ��ɨ����Դ�������ġ���</p>
            <div class="legend">
              <span class="phase dev-done">P0 ����</span>
              <span class="phase dev-todo">P1-P2 ��ǿ</span>
              <span class="phase p3">P3 �۲�</span>
              <span class="phase p4">P4 ����</span>
            </div>
            <div class="mock-banner"><strong>����״̬</strong>��MATCHED / ORPHAN / MISSING / DRIFT �� �������� <code>scan_sub_task</code> ΪΨһִ��̬����Դ��</div>
            <div class="sitemap-grid">
              <div class="sitemap-card" onclick="showView('node-list')">
                <h3><span class="phase p0">P0</span> �豸����</h3>
                <ul>
                  <li>�ڵ��б� �� GET /v1/scan/node����ǿ health_status��</li>
                  <li>�ڵ����� �� metrics / capabilities</li>
                  <li>����Ŀ¼ �� GET /v1/scanner/capability/catalog</li>
                  <li>����ע�� �� GET /v1/scanner</li>
                </ul>
              </div>
              <div class="sitemap-card" onclick="showView('reconcile')">
                <h3><span class="phase p0">P0</span> �������</h3>
                <ul>
                  <li>���˽�� �� GET /v1/reconcile/tasks</li>
                  <li>�������� �� POST /v1/reconcile/tasks/trigger</li>
                  <li>���챨�� �� GET /v1/reconcile/tasks/diff</li>
                  <li>�¶����� �� POST .../orphan/handle</li>
                </ul>
              </div>
              <div class="sitemap-card" onclick="showView('survey-list')">
                <h3><span class="phase p0">P0</span> ����׷��</h3>
                <ul>
                  <li>Survey �б� + ���������</li>
                  <li>�·����� �� GET .../dispatch-detail</li>
                  <li>ͬ��״̬ �� POST .../sync-status</li>
                </ul>
              </div>
              <div class="sitemap-card" onclick="showView('preview-scanners')">
                <h3><span class="phase p1">P1</span> �·�ǰԤ��</h3>
                <ul>
                  <li>POST /v1/scan/task/preview-scanners</li>
                  <li>�� taskType + IP + template + load ����</li>
                </ul>
              </div>
              <div class="sitemap-card" onclick="showView('dashboard')">
                <h3><span class="phase p1">P1</span> ��Ⱥ����</h3>
                <ul>
                  <li>GET /v1/scanner/dashboard</li>
                  <li>�ڵ㸺�� / ���������� / �����ֲ�</li>
                </ul>
              </div>
              <div class="sitemap-card" onclick="showView('template-sync')">
                <h3><span class="phase p2">P2</span> ģ��ͬ��</h3>
                <ul>
                  <li>GET/POST .../templates �� sync</li>
                  <li>sysvuln / webvuln / baseline</li>
                </ul>
              </div>
              <div class="sitemap-card" onclick="showView('auth-precheck')">
                <h3><span class="phase p2">P2</span> ƾ֤Ԥ��</h3>
                <ul>
                  <li>auth.login_verify �·�ǰУ��</li>
                </ul>
              </div>
              <div class="sitemap-card" onclick="showView('openapi-bridge')">
                <h3><span class="phase p4">P4</span> ����ƽ̨�Ž�</h3>
                <ul>
                  <li>open-api-service ·�� + preview-scanners</li>
                  <li>Partner ����״̬�ۺ� sub_task</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- �ڵ��б� -->
      <section id="view-node-list" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ɨ��ڵ� <span class="phase p0">P0</span></div>
        <div class="card"><div class="card-body">
          <div class="search-row">
            <div class="form-item"><label>�ڵ� ID</label><input placeholder="nodeId" /></div>
            <div class="form-item"><label>����</label><select><option>ȫ��</option><option>LM</option><option>AH</option><option>QM</option></select></div>
            <div class="form-item"><label>����״̬</label><select><option>ȫ��</option><option>healthy</option><option>degraded</option><option>offline</option></select></div>
            <button class="btn btn-primary" type="button">��ѯ</button>
          </div>
        </div></div>
        <div class="card"><div class="card-body">
          <div class="toolbar"><span class="api-path">GET /v1/scan/node</span><span class="helper">��ǿ�ֶΣ�health_status �� supported_capabilities �� last_heartbeat_at</span></div>
          <table>
            <thead><tr><th>nodeId</th><th>����</th><th>����</th><th>health_status</th><th>������</th><th>�������</th><th>����</th></tr></thead>
            <tbody>
              <tr>
                <td><a class="btn-link" onclick="showView('node-detail')">node-lm-01</a></td>
                <td>���� RSAS ���ڵ�</td><td><span class="vendor-badge">LM</span></td>
                <td><span class="tag tag-green">healthy</span></td><td>12</td><td>2026-06-14 10:02:11</td>
                <td><span class="action-btn" onclick="showView('node-detail')">����</span><span class="action-btn" onclick="showToast('�Ѵ��� POST .../health/check')">̽��</span></td>
              </tr>
              <tr>
                <td>node-ah-02</td><td>����ɨ����</td><td><span class="vendor-badge">AH</span></td>
                <td><span class="tag tag-orange">degraded</span></td><td>8</td><td>2026-06-14 09:58:00</td>
                <td><span class="action-btn" onclick="showView('node-detail')">����</span></td>
              </tr>
              <tr>
                <td>node-qm-03</td><td>���� VScanner</td><td><span class="vendor-badge">QM</span></td>
                <td><span class="tag tag-red">offline</span></td><td>6</td><td>2026-06-13 22:10:00</td>
                <td><span class="action-btn" onclick="showView('node-detail')">����</span></td>
              </tr>
            </tbody>
          </table>
          <div class="pagination"><span>�� 3 ��</span></div>
        </div></div>
      </section>

      <!-- �ڵ����� -->
      <section id="view-node-detail" class="view">
        <div class="breadcrumb"><a onclick="showView('node-list')">ɨ��ڵ�</a> / node-lm-01 <span class="phase p0">P0</span></div>
        <div class="card">
          <div class="detail-header">
            <div>
              <div class="detail-title">���� RSAS ���ڵ� <span class="tag tag-green">healthy</span></div>
              <div class="detail-meta">node-lm-01 �� LM �� vendor_device_hash: a3f2��9c01 �� ������� 10:02:11</div>
            </div>
            <div>
              <button class="btn" type="button" onclick="showToast('POST /v1/scanner/node/node-lm-01/health/check')">����̽��</button>
              <button class="btn btn-primary" type="button" onclick="showView('capability-catalog')">����Ŀ¼</button>
            </div>
          </div>
          <div class="tabs" id="nodeTabs">
            <div class="tab active" data-tab="metrics"><span class="phase p1">P1</span> ʵʱָ��</div>
            <div class="tab" data-tab="caps"><span class="phase p0">P0</span> �ڵ�����</div>
            <div class="tab" data-tab="templates"><span class="phase p2">P2</span> ģ��</div>
          </div>
          <div id="ntab-metrics" class="tab-panel active">
            <span class="api-path">GET /v1/scanner/node/node-lm-01/metrics</span>
            <div class="stat-row" style="margin-top:12px;">
              <div class="stat-card"><div class="label">CPU</div><div class="value">23%</div></div>
              <div class="stat-card"><div class="label">Memory</div><div class="value">61%</div></div>
              <div class="stat-card"><div class="label">Disk</div><div class="value">48%</div></div>
              <div class="stat-card"><div class="label">task_running</div><div class="value">3</div></div>
            </div>
            <div class="helper">������Դ��LM system.status �ֶ�ӳ��</div>
          </div>
          <div id="ntab-caps" class="tab-panel">
            <span class="api-path">GET /v1/scanner/node/node-lm-01/capabilities</span>
            <table style="margin-top:12px;">
              <thead><tr><th>capability_code</th><th>RSAS API</th><th>required</th><th>verified_at</th></tr></thead>
              <tbody>
                <tr><td>task.create</td><td>POST /api/task/create</td><td>��</td><td>2026-06-10</td></tr>
                <tr><td>task.active_list</td><td>GET /api/task/active_list</td><td>��</td><td>2026-06-10</td></tr>
                <tr><td>system.status</td><td>GET /api/system/status</td><td>��</td><td>2026-06-10</td></tr>
                <tr><td>auth.login_verify</td><td>POST /api/auth/login_verify</td><td>��</td><td>��</td></tr>
              </tbody>
            </table>
            <button class="btn" style="margin-top:12px;" type="button" onclick="showToast('POST .../capabilities/verify')">��֤����������</button>
          </div>
          <div id="ntab-templates" class="tab-panel">
            <span class="api-path">GET /v1/scanner/node/node-lm-01/templates?type=sysvuln</span>
            <table style="margin-top:12px;">
              <thead><tr><th>vendor_template_id</th><th>����</th><th>content_hash</th><th>synced_at</th></tr></thead>
              <tbody>
                <tr><td>tpl-1001</td><td>ȫ��ϵͳ©��ģ��</td><td>sha256:ab12��</td><td>2026-06-12</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ����Ŀ¼ -->
      <section id="view-capability-catalog" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ����Ŀ¼ <span class="phase p0">P0</span></div>
        <div class="card"><div class="card-body">
          <div class="toolbar"><span class="api-path">GET /v1/scanner/capability/catalog</span></div>
          <div class="filter-chips" id="capVendorFilter">
            <span class="filter-chip active" data-vendor="all">ȫ������</span>
            <span class="filter-chip" data-vendor="LM">LM</span>
            <span class="filter-chip" data-vendor="AH">AH</span>
            <span class="filter-chip" data-vendor="QM">QM</span>
          </div>
          <table>
            <thead><tr><th>vendor_code</th><th>capability_code</th><th>http_method</th><th>path_template</th><th>required</th><th>min_firmware</th></tr></thead>
            <tbody>
              <tr data-vendor="LM"><td>LM</td><td>task.create</td><td>POST</td><td>/api/task/create</td><td>��</td><td>6.0.8</td></tr>
              <tr data-vendor="LM"><td>LM</td><td>task.pause</td><td>POST</td><td>/api/task/pause/{id}</td><td>��</td><td>6.0.8</td></tr>
              <tr data-vendor="LM"><td>LM</td><td>template.sysvuln.list</td><td>GET</td><td>/api/template/sysvuln/list</td><td>��</td><td>6.0.8</td></tr>
              <tr data-vendor="AH"><td>AH</td><td>task.create</td><td>POST</td><td>/scan/task</td><td>��</td><td>��</td></tr>
            </tbody>
          </table>
        </div></div>
      </section>

      <!-- ����ע��� -->
      <section id="view-scanner-list" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ����ע��� <span class="phase p0">P0</span></div>
        <div class="card"><div class="card-body">
          <div class="toolbar"><span class="api-path">GET /v1/scanner</span><span class="helper">ScannerAdapter ���ע�� �� �³���ʵ�� infra/adapter/scanner/{vendor}/</span></div>
          <table>
            <thead><tr><th>vendor_code</th><th>��ʾ��</th><th>Adapter ��</th><th>�ڵ���</th><th>��ѡ����</th><th>״̬</th></tr></thead>
            <tbody>
              <tr><td>LM</td><td>���� RSAS</td><td>LmScannerAdapter</td><td>2</td><td>task.create, active_list</td><td><span class="tag tag-green">�ѽ���</span></td></tr>
              <tr><td>AH</td><td>����</td><td>AhScannerAdapter</td><td>1</td><td>task.create</td><td><span class="tag tag-orange">��������</span></td></tr>
              <tr><td>QM</td><td>����</td><td>��</td><td>1</td><td>��</td><td><span class="tag tag-default">�滮��</span></td></tr>
            </tbody>
          </table>
        </div></div>
      </section>

      <!-- ���� -->
      <section id="view-reconcile" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ������� <span class="phase p0">P0</span></div>
        <div class="card"><div class="card-body">
          <div class="search-row">
            <div class="form-item"><label>nodeId</label><input placeholder="node-lm-01" /></div>
            <div class="form-item"><label>surveyId</label><input placeholder="SUR-20260614-001" /></div>
            <button class="btn btn-primary" type="button" onclick="showToast('POST /v1/reconcile/tasks/trigger ���ύ')">��������</button>
            <button class="btn" type="button">��ѯ</button>
          </div>
        </div></div>
        <div class="card"><div class="card-body">
          <div class="toolbar">
            <span class="api-path">GET /v1/reconcile/tasks �� GET /v1/reconcile/tasks/diff</span>
            <button class="btn" type="button" onclick="showToast('���� diff ����')">��������</button>
          </div>
          <div class="filter-chips" id="reconcileFilter">
            <span class="filter-chip active" data-diff="all">ȫ��</span>
            <span class="filter-chip" data-diff="MATCHED">MATCHED</span>
            <span class="filter-chip" data-diff="ORPHAN">ORPHAN</span>
            <span class="filter-chip" data-diff="MISSING">MISSING</span>
            <span class="filter-chip" data-diff="DRIFT">DRIFT</span>
          </div>
          <table>
            <thead><tr><th>diff_type</th><th>node_id</th><th>survey_id</th><th>sub_task_id</th><th>vendor_task_id</th><th>platform_state</th><th>vendor_state</th><th>reconcile_at</th><th>����</th></tr></thead>
            <tbody id="reconcileTableBody">
              <tr data-diff="MATCHED"><td><span class="tag tag-green">MATCHED</span></td><td>node-lm-01</td><td>SUR-001</td><td>sub-001</td><td>LM-T-88901</td><td>1 ִ����</td><td>2 ����</td><td>10:00:01</td><td>��</td></tr>
              <tr data-diff="ORPHAN"><td><span class="tag tag-orange">ORPHAN</span></td><td>node-lm-01</td><td>��</td><td>��</td><td>LM-T-99002</td><td>��</td><td>2 ����</td><td>10:00:02</td><td><span class="action-btn" onclick="openOrphanModal('LM-T-99002')">�����¶�</span></td></tr>
              <tr data-diff="MISSING"><td><span class="tag tag-red">MISSING</span></td><td>node-lm-01</td><td>SUR-002</td><td>sub-002</td><td>��</td><td>1 ִ����</td><td>��</td><td>10:00:03</td><td><span class="action-btn" onclick="showToast('���� retry ����ʧ��')">retry</span></td></tr>
              <tr data-diff="DRIFT"><td><span class="tag tag-purple">DRIFT</span></td><td>node-lm-01</td><td>SUR-003</td><td>sub-003</td><td>LM-T-77003</td><td>2 �����</td><td>2 ����</td><td>10:00:04</td><td><span class="action-btn" onclick="showToast('POST .../sync-status')">sync-status</span></td></tr>
            </tbody>
          </table>
        </div></div>
      </section>

      <!-- Survey �б� -->
      <section id="view-survey-list" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / Survey ���� <span class="phase p0">P0</span></div>
        <div class="card"><div class="card-body">
          <div class="search-row">
            <div class="form-item"><label>surveyId</label><input placeholder="SUR-20260614-001" /></div>
            <div class="form-item"><label>״̬</label><select><option>ȫ��</option><option>ִ����</option><option>�����</option></select></div>
            <button class="btn btn-primary" type="button">��ѯ</button>
          </div>
        </div></div>
        <div class="card"><div class="card-body">
          <div class="toolbar">
            <span class="api-path">GET /v1/scan/task/{surveyId}/sub-tasks/summary �� GET .../dispatch-detail</span>
            <button class="btn btn-primary" type="button" onclick="openDispatchDrawer('SUR-20260614-001')">�·�����</button>
          </div>
          <table>
            <thead><tr><th>surveyId</th><th>��������</th><th>��������</th><th>ִ����</th><th>�����</th><th>����</th><th>����</th></tr></thead>
            <tbody>
              <tr>
                <td>SUR-20260614-001</td><td>6����������ɨ��</td><td>4</td><td>2</td><td>1</td>
                <td><span class="tag tag-green">MATCHED��2</span> <span class="tag tag-purple">DRIFT��1</span></td>
                <td>
                  <span class="action-btn" onclick="openDispatchDrawer('SUR-20260614-001')">�·�����</span>
                  <span class="action-btn" onclick="openSubtaskDrawer('sub-001')">������</span>
                  <span class="action-btn" onclick="showView('reconcile')">����</span>
                </td>
              </tr>
              <tr>
                <td>SUR-20260613-008</td><td>Web ©��ר��</td><td>2</td><td>0</td><td>2</td>
                <td><span class="tag tag-green">MATCHED��2</span></td>
                <td><span class="action-btn" onclick="openDispatchDrawer('SUR-20260613-008')">�·�����</span></td>
              </tr>
            </tbody>
          </table>
          <div class="helper" style="margin-top:12px;">������ state��0 δ��ʼ �� 1 ִ���� �� 2 ����� �� 3 ʧ�� �� 4 ��ͣ</div>
        </div></div>
      </section>

      <!-- Ԥ��ɨ��ڵ� -->
      <section id="view-preview-scanners" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / �·�ǰ�ڵ�Ԥ�� <span class="phase p1">P1</span></div>
        <div class="card">
          <div class="card-title">Ԥ������ɨ��ڵ� <span class="api-path">POST /v1/scan/task/preview-scanners</span></div>
          <div class="card-body">
            <div class="form-grid">
              <div class="form-item"><label>taskType</label><select><option>host_vuln</option><option>web_vuln</option><option>baseline</option></select></div>
              <div class="form-item"><label>target IP ��</label><input placeholder="10.0.0.0/24" value="192.168.1.0/24" /></div>
              <div class="form-item"><label>templateId</label><input placeholder="tpl-1001" value="tpl-1001" /></div>
              <div class="form-item"><label>requiredCapabilities</label><input placeholder="task.create,system.status" value="task.create" /></div>
            </div>
            <button class="btn btn-primary" style="margin-top:16px;" type="button" onclick="showPreviewResult()">Ԥ���ڵ�</button>
            <div id="previewResult" class="hidden" style="margin-top:16px;">
              <table>
                <thead><tr><th>nodeId</th><th>score</th><th>load</th><th>capabilities</th><th>excludedReasons</th></tr></thead>
                <tbody>
                  <tr><td>node-lm-01</td><td>92</td><td>��</td><td>12/12</td><td>��</td></tr>
                  <tr><td>node-ah-02</td><td>��</td><td>��</td><td>��</td><td>��֧�� web_vuln</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- ���� -->
      <section id="view-queue" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ���й۲� <span class="phase p1">P1</span></div>
        <div class="card"><div class="card-body">
          <div class="toolbar"><span class="api-path">GET /v1/queue �� GET /v1/scan/sub/task</span><span class="helper">չʾ�� reconcile ������ send / wait / execute ����</span></div>
          <div class="stat-row">
            <div class="stat-card"><div class="label">send ������</div><div class="value">5</div></div>
            <div class="stat-card"><div class="label">wait �ȴ�</div><div class="value">12</div></div>
            <div class="stat-card"><div class="label">execute ִ��</div><div class="value">3</div></div>
            <div class="stat-card"><div class="label">reconcile ������</div><div class="value">2</div></div>
          </div>
          <table>
            <thead><tr><th>queue</th><th>sub_task_id</th><th>nodeId</th><th>reconcile_status</th><th>���ʱ��</th></tr></thead>
            <tbody>
              <tr><td>send</td><td>sub-004</td><td>node-lm-01</td><td>��</td><td>10:05:01</td></tr>
              <tr><td>wait</td><td>sub-005</td><td>node-lm-01</td><td>MATCHED</td><td>10:04:55</td></tr>
              <tr><td>execute</td><td>sub-001</td><td>node-lm-01</td><td>DRIFT</td><td>09:50:00</td></tr>
            </tbody>
          </table>
        </div></div>
      </section>

      <!-- ���� -->
      <section id="view-dashboard" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ��Ⱥ���� <span class="phase p1">P1</span></div>
        <div class="card"><div class="card-body">
          <span class="api-path">GET /v1/scanner/dashboard</span>
          <div class="stat-row" style="margin-top:12px;">
            <div class="stat-card"><div class="label">�ڵ�����</div><div class="value">4</div></div>
            <div class="stat-card"><div class="label">healthy</div><div class="value">2</div></div>
            <div class="stat-card"><div class="label">����������</div><div class="value">7</div></div>
            <div class="stat-card"><div class="label">ORPHAN ������</div><div class="value">1</div></div>
          </div>
          <div class="chart-placeholder">�ڵ㸺�طֲ� / ��������ռ�ȣ�ECharts��</div>
        </div></div>
      </section>

      <!-- ģ��ͬ�� -->
      <section id="view-template-sync" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ģ��ͬ�� <span class="phase p2">P2</span></div>
        <div class="card">
          <div class="card-title">ģ��ͬ�� <span class="api-path">POST /v1/scanner/node/{nodeId}/templates/sync</span></div>
          <div class="card-body">
            <div class="form-grid">
              <div class="form-item"><label>nodeId</label><select><option>node-lm-01</option><option>node-ah-02</option></select></div>
              <div class="form-item"><label>template_type</label><select><option>sysvuln</option><option>webvuln</option><option>baseline</option></select></div>
            </div>
            <button class="btn btn-primary" style="margin-top:16px;" type="button" onclick="showToast('ģ��ͬ���������ύ')">����ͬ��</button>
            <div class="helper" style="margin-top:12px;">ͬ���� preview-scanners ��У�� template_id ��Ч��</div>
          </div>
        </div>
      </section>

      <!-- ƾ֤Ԥ�� -->
      <section id="view-auth-precheck" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ƾ֤Ԥ�� <span class="phase p2">P2</span></div>
        <div class="card">
          <div class="card-title">�·�ǰƾ֤Ԥ�� <span class="helper">capability: auth.login_verify</span></div>
          <div class="card-body">
            <div class="form-grid">
              <div class="form-item"><label>nodeId</label><select><option>node-lm-01</option></select></div>
              <div class="form-item"><label>user_account</label><input value="scan_admin" /></div>
              <div class="form-item full"><label>password</label><input type="password" value="********" /><div class="helper">�����ֶβ������� dispatch-detail ���ģ�������</div></div>
            </div>
            <button class="btn btn-primary" style="margin-top:16px;" type="button" onclick="showToast('POST /api/auth/login_verify �� Ԥ��ͨ��')">ִ��Ԥ��</button>
          </div>
        </div>
      </section>

      <!-- ָ����ʷ -->
      <section id="view-metrics-history" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ָ����ʷ <span class="phase p3">P3</span></div>
        <div class="card"><div class="card-body">
          <span class="api-path">GET /v1/scanner/node/{nodeId}/metrics/history</span>
          <div class="search-row" style="margin-top:12px;">
            <div class="form-item"><label>nodeId</label><select><option>node-lm-01</option></select></div>
            <div class="form-item"><label>ʱ�䷶Χ</label><input type="date" /></div>
            <button class="btn btn-primary" type="button">��ѯ</button>
          </div>
          <div class="chart-placeholder">CPU / Memory / Disk ��ʷ���� �� Prometheus ָ�걩¶</div>
        </div></div>
      </section>

      <!-- �澯���� -->
      <section id="view-alert-rules" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / �澯���� <span class="phase p3">P3</span></div>
        <div class="card"><div class="card-body">
          <div class="toolbar"><button class="btn btn-primary" type="button">�� �½�����</button></div>
          <table>
            <thead><tr><th>������</th><th>����</th><th>��ֵ</th><th>֪ͨ</th><th>״̬</th></tr></thead>
            <tbody>
              <tr><td>�ڵ�����</td><td>health_status = offline</td><td>���� 5min</td><td>�ʼ� + ����</td><td><span class="tag tag-green">����</span></td></tr>
              <tr><td>ORPHAN �ѻ�</td><td>reconcile ORPHAN count</td><td>&gt; 10</td><td>����</td><td><span class="tag tag-green">����</span></td></tr>
              <tr><td>metrics ��ʱ</td><td>metrics API P99</td><td>&gt; 3s</td><td>Prometheus Alert</td><td><span class="tag tag-default">����</span></td></tr>
            </tbody>
          </table>
        </div></div>
      </section>

      <!-- ����ƽ̨�Ž� -->
      <section id="view-openapi-bridge" class="view">
        <div class="breadcrumb"><a onclick="showView('overview')">ɨ����������</a> / ����ƽ̨�Ž� <span class="phase p4">P4</span></div>
        <div class="card">
          <div class="card-title">open-api-service �Խ� <span class="phase p4">VTC-GOV-P4</span></div>
          <div class="card-body">
            <p style="margin-bottom:12px;color:var(--text-secondary);">Partner �� open-api-service �·�ɨ������ʱ��·���� vuln-task-center �� preview-scanners �� sub_task ״̬�ۺϡ�</p>
            <div class="kv-row"><span class="k">�·�·��</span><span class="v">open-api �� vuln-task-center /v1/scan/task/preview-scanners</span></div>
            <div class="kv-row"><span class="k">״̬��ѯ</span><span class="v">Partner GET task �� �ۺ� sub-tasks/summary</span></div>
            <div class="kv-row"><span class="k">��ѡ</span><span class="v">�ڵ��׺Ͳ��� �� Partner �� preview ����</span></div>
            <button class="btn btn-primary" style="margin-top:12px;" type="button" onclick="showToast('�Ž����ñ��棨ԭ�ͣ�')">�����Ž�����</button>
          </div>
        </div>
      </section>

      <div class="page-note">vuln-task-center ɨ����������ԭ�� �� PRD VTC-GOV-P0~P4 �� 2026-06-14</div>
    </main>
  </div>
</div>

<!-- ������ Drawer -->
<div class="drawer-overlay" id="subtaskDrawer">
  <div class="drawer drawer-wide">
    <div class="drawer-header"><span>����������</span><button class="btn-link" type="button" onclick="closeDrawer('subtaskDrawer')">?</button></div>
    <div class="drawer-body">
      <div class="kv-row"><span class="k">sub_task_id</span><span class="v"><code id="st-id">sub-001</code></span></div>
      <div class="kv-row"><span class="k">surveyId</span><span class="v">SUR-20260614-001</span></div>
      <div class="kv-row"><span class="k">nodeId</span><span class="v">node-lm-01</span></div>
      <div class="kv-row"><span class="k">state</span><span class="v"><span class="tag tag-blue">1 ִ����</span></span></div>
      <div class="kv-row"><span class="k">plan_id</span><span class="v">LM-T-88901</span></div>
      <div class="kv-row"><span class="k">reconcile</span><span class="v"><span class="tag tag-green">MATCHED</span></span></div>
      <div class="drawer-tabs" id="subtaskDrawerTabs">
        <div class="drawer-tab active" data-st-panel="ops">����</div>
        <div class="drawer-tab" data-st-panel="payload">sendParamsInfo</div>
      </div>
      <div id="st-panel-ops" class="drawer-panel active">
        <div style="display:flex;flex-wrap:wrap;gap:8px;">
          <button class="btn" type="button" onclick="showToast('POST .../pause')">��ͣ</button>
          <button class="btn" type="button" onclick="showToast('POST .../resume')">�ָ�</button>
          <button class="btn" type="button" onclick="showToast('POST .../retry')">�����·�</button>
          <button class="btn btn-danger" type="button" onclick="showToast('POST .../cancel')">ȡ��</button>
          <button class="btn btn-primary" type="button" onclick="showToast('POST .../sync-status')">sync-status</button>
        </div>
        <p class="helper" style="margin-top:12px;">P1��pause / resume / retry / cancel �� P0��sync-status</p>
      </div>
      <div id="st-panel-payload" class="drawer-panel">
        <pre class="code-block" id="st-payload">{
  "classify_task_name": "6������ɨ��-������1",
  "target": "192.168.1.10",
  "template_id": "tpl-1001",
  "reconcile_status": "MATCHED"
}</pre>
      </div>
    </div>
    <div class="drawer-footer">
      <button class="btn" type="button" onclick="closeDrawer('subtaskDrawer')">�ر�</button>
    </div>
  </div>
</div>

<!-- �·����� Drawer -->
<div class="drawer-overlay" id="dispatchDrawer">
  <div class="drawer drawer-full">
    <div class="drawer-header"><span>�·����� �� <span id="dispatch-survey-id">SUR-20260614-001</span></span><button class="btn-link" type="button" onclick="closeDrawer('dispatchDrawer')">?</button></div>
    <div class="drawer-body">
      <span class="api-path">GET /v1/scan/task/{surveyId}/dispatch-detail</span>
      <div class="drawer-tabs" id="dispatchDrawerTabs" style="margin-top:12px;">
        <div class="drawer-tab active" data-dp-panel="platform">platformParams</div>
        <div class="drawer-tab" data-dp-panel="adapter">adapterParams</div>
        <div class="drawer-tab" data-dp-panel="subs">subTasks</div>
      </div>
      <div id="dp-panel-platform" class="drawer-panel active">
        <pre class="code-block">{
  "surveyId": "SUR-20260614-001",
  "taskName": "6����������ɨ��",
  "taskType": "host_vuln",
  "targets": ["192.168.1.0/24"],
  "templateId": "tpl-1001"
}</pre>
      </div>
      <div id="dp-panel-adapter" class="drawer-panel">
        <pre class="code-block">{
  "vendor": "LM",
  "nodeId": "node-lm-01",
  "adapter": "LmScannerAdapter",
  "requiredCapabilities": ["task.create", "system.status"]
}</pre>
      </div>
      <div id="dp-panel-subs" class="drawer-panel">
        <table>
          <thead><tr><th>sub_task_id</th><th>target</th><th>state</th><th>nodeId</th><th>����</th></tr></thead>
          <tbody>
            <tr><td>sub-001</td><td>192.168.1.10</td><td>ִ����</td><td>node-lm-01</td><td><span class="action-btn" onclick="openSubtaskDrawer('sub-001')">����</span></td></tr>
            <tr><td>sub-002</td><td>192.168.1.11</td><td>�����</td><td>node-lm-01</td><td><span class="action-btn" onclick="openSubtaskDrawer('sub-002')">����</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="drawer-footer">
      <button class="btn" type="button" onclick="closeDrawer('dispatchDrawer')">�ر�</button>
    </div>
  </div>
</div>

<!-- �¶����� Modal -->
<div class="modal-overlay" id="orphanModal">
  <div class="modal">
    <div class="modal-header"><span>�����¶����� ORPHAN</span><button class="btn-link" type="button" onclick="closeOrphanModal()">?</button></div>
    <div class="modal-body">
      <span class="api-path">POST /v1/reconcile/tasks/orphan/handle</span>
      <div class="kv-row" style="margin-top:12px;"><span class="k">vendor_task_id</span><span class="v"><code id="orphan-vendor-id">LM-T-99002</code></span></div>
      <div class="kv-row"><span class="k">node_id</span><span class="v">node-lm-01</span></div>
      <p class="helper" style="margin:12px 0;">�豸�С�ƽ̨�� �� ѡ����������</p>
      <div class="form-item">
        <label>handled_action</label>
        <select id="orphanAction">
          <option value="IGNORE">IGNORE �� ���Բ���¼</option>
          <option value="STOP">STOP �� Զ��ֹͣ�豸����</option>
          <option value="ADOPT">ADOPT �� �ɹ�Ϊƽ̨ sub_task</option>
        </select>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn" type="button" onclick="closeOrphanModal()">ȡ��</button>
      <button class="btn btn-primary" type="button" onclick="submitOrphan()">�ύ</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
  function showView(name) {
    document.querySelectorAll('.view').forEach(function (el) {
      el.classList.toggle('active', el.id === 'view-' + name);
    });
    document.querySelectorAll('.menu-item[data-view]').forEach(function (item) {
      item.classList.toggle('active', item.dataset.view === name);
    });
    window.scrollTo(0, 0);
  }
  document.querySelectorAll('.menu-item[data-view]').forEach(function (item) {
    item.addEventListener('click', function () { showView(item.dataset.view); });
  });

  document.getElementById('nodeTabs').addEventListener('click', function (e) {
    var tab = e.target.closest('.tab[data-tab]');
    if (!tab) return;
    document.querySelectorAll('#nodeTabs .tab').forEach(function (t) { t.classList.remove('active'); });
    document.querySelectorAll('[id^="ntab-"]').forEach(function (p) { p.classList.remove('active'); });
    tab.classList.add('active');
    document.getElementById('ntab-' + tab.dataset.tab).classList.add('active');
  });

  document.getElementById('reconcileFilter').addEventListener('click', function (e) {
    var chip = e.target.closest('[data-diff]');
    if (!chip) return;
    var diff = chip.dataset.diff;
    document.querySelectorAll('#reconcileFilter .filter-chip').forEach(function (c) {
      c.classList.toggle('active', c === chip);
    });
    document.querySelectorAll('#reconcileTableBody tr').forEach(function (row) {
      row.style.display = (diff === 'all' || row.dataset.diff === diff) ? '' : 'none';
    });
  });

  document.getElementById('capVendorFilter').addEventListener('click', function (e) {
    var chip = e.target.closest('[data-vendor]');
    if (!chip) return;
    var vendor = chip.dataset.vendor;
    document.querySelectorAll('#capVendorFilter .filter-chip').forEach(function (c) {
      c.classList.toggle('active', c === chip);
    });
    document.querySelectorAll('#view-capability-catalog tbody tr').forEach(function (row) {
      row.style.display = (vendor === 'all' || row.dataset.vendor === vendor) ? '' : 'none';
    });
  });

  function openDrawer(id) { document.getElementById(id).classList.add('show'); }
  function closeDrawer(id) { document.getElementById(id).classList.remove('show'); }

  function openSubtaskDrawer(id) {
    document.getElementById('st-id').textContent = id;
    openDrawer('subtaskDrawer');
  }
  function openDispatchDrawer(surveyId) {
    document.getElementById('dispatch-survey-id').textContent = surveyId;
    openDrawer('dispatchDrawer');
  }

  document.getElementById('subtaskDrawerTabs').addEventListener('click', function (e) {
    var tab = e.target.closest('.drawer-tab[data-st-panel]');
    if (!tab) return;
    document.querySelectorAll('#subtaskDrawerTabs .drawer-tab').forEach(function (t) { t.classList.remove('active'); });
    document.querySelectorAll('[id^="st-panel-"]').forEach(function (p) { p.classList.remove('active'); });
    tab.classList.add('active');
    document.getElementById('st-panel-' + tab.dataset.stPanel).classList.add('active');
  });

  document.getElementById('dispatchDrawerTabs').addEventListener('click', function (e) {
    var tab = e.target.closest('.drawer-tab[data-dp-panel]');
    if (!tab) return;
    document.querySelectorAll('#dispatchDrawerTabs .drawer-tab').forEach(function (t) { t.classList.remove('active'); });
    document.querySelectorAll('[id^="dp-panel-"]').forEach(function (p) { p.classList.remove('active'); });
    tab.classList.add('active');
    document.getElementById('dp-panel-' + tab.dataset.dpPanel).classList.add('active');
  });

  function openOrphanModal(vendorTaskId) {
    document.getElementById('orphan-vendor-id').textContent = vendorTaskId;
    document.getElementById('orphanModal').classList.add('show');
  }
  function closeOrphanModal() { document.getElementById('orphanModal').classList.remove('show'); }
  function submitOrphan() {
    var action = document.getElementById('orphanAction').value;
    closeOrphanModal();
    showToast('orphan/handle �� ' + action + ' ���ύ');
  }

  function showPreviewResult() {
    document.getElementById('previewResult').classList.remove('hidden');
    showToast('preview-scanners ���� 1 �����ýڵ�');
  }

  var toastTimer;
  function showToast(msg) {
    var el = document.getElementById('toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, 2200);
  }

  ['subtaskDrawer', 'dispatchDrawer'].forEach(function (id) {
    document.getElementById(id).addEventListener('click', function (e) {
      if (e.target === e.currentTarget) closeDrawer(id);
    });
  });
  document.getElementById('orphanModal').addEventListener('click', function (e) {
    if (e.target === e.currentTarget) closeOrphanModal();
  });
</script>
</body>
</html>'''

BUILD = Path(__file__).with_name('build_vtc_governance_proto.py')
content = '''# -*- coding: utf-8 -*-
"""Generate vuln-task-center governance prototype with correct UTF-8."""
from pathlib import Path

OUT = Path(__file__).with_name("vuln-task-center-governance-prototype.html")
HTML = """''' + HTML.replace('\\', '\\\\').replace('"""', '\\"\\"\\"') + '''"""
OUT.write_text(HTML, encoding="utf-8")
print("written:", OUT, "bytes:", OUT.stat().st_size)
'''
BUILD.write_text(content, encoding='utf-8')
print('Updated', BUILD, 'size', BUILD.stat().st_size)
