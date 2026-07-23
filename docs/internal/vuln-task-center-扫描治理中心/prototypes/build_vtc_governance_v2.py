# -*- coding: utf-8 -*-

"""Build vuln-task-center governance prototype v2 (UTF-8)."""

from pathlib import Path



ROOT = Path(__file__).parent

OPEN = ROOT / "open-platform-admin-prototype.html"

OUT = ROOT / "vuln-task-center-governance-prototype.html"





def css_block():

    text = OPEN.read_text(encoding="utf-8")

    start = text.index("<style>")

    end = text.index("</style>") + len("</style>")

    extra = """

    .dev-done { background: #f6ffed; color: #389e0d; border: 1px solid #b7eb8f; }

    .dev-todo { background: #fff7e6; color: #d46b08; border: 1px solid #ffd591; }

    .dev-skip { background: #fafafa; color: rgba(0,0,0,.45); border: 1px solid #d9d9d9; }

    .story-flow { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 12px 0; font-size: 13px; }

    .story-step { padding: 6px 12px; border: 1px solid #91d5ff; background: #e6f7ff; border-radius: 2px; cursor: pointer; }

    .story-step:hover { border-color: var(--primary); }

    .story-arrow { color: var(--text-secondary); }

    .diff-table td.diff-add { background: #f6ffed; }

    .diff-table td.diff-del { background: #fff2f0; }

    .three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }

    @media (max-width: 960px) { .three-col { grid-template-columns: 1fr; } }

    .col-box { border: 1px solid #f0f0f0; border-radius: 2px; padding: 12px; font-size: 13px; }

    .col-box h4 { font-size: 13px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 500; }

    .excluded-list { margin-top: 12px; font-size: 12px; color: var(--text-secondary); }

    .excluded-list li { margin-bottom: 4px; }

    """

    return text[start:end].replace("</style>", extra + "\n  </style>")





SIDEBAR = """

  <aside class="sidebar">

    <div class="sidebar-logo">扫描治理中心<br><small style="font-weight:400;font-size:11px;opacity:.65">vuln-task-center</small></div>

    <nav>

      <div class="menu-group"><div class="menu-group-title">总览</div>

        <div class="menu-item active" data-view="overview">功能总览 / 站点地图</div>

        <div class="menu-item" data-view="story-s2">端到端 · 工单下发 S2</div>

        <div class="menu-item" data-view="story-s3">端到端 · 对账恢复 S3</div>

        <div class="menu-item" data-view="story-s5">端到端 · 漂移操控 S5</div>

      </div>

      <div class="menu-group"><div class="menu-group-title">P0 · 设备治理</div>

        <div class="menu-item" data-view="node-list">扫描节点 <span class="phase p0">P0</span></div>

        <div class="menu-item" data-view="node-create">新增 / 编辑节点</div>

        <div class="menu-item" data-view="node-detail">节点详情 / 指标</div>

        <div class="menu-item" data-view="classify-list">厂商 / 版本</div>

        <div class="menu-item" data-view="scanner-list">逻辑扫描器</div>

        <div class="menu-item" data-view="scene-list">业务场景</div>

        <div class="menu-item" data-view="capability-catalog">能力目录 LM</div>

      </div>

      <div class="menu-group"><div class="menu-group-title">P0 · 对账</div>

        <div class="menu-item" data-view="reconcile-list">任务对账 <span class="phase p0">P0</span></div>

        <div class="menu-item" data-view="reconcile-diff">差异详情 / diff</div>

      </div>

      <div class="menu-group"><div class="menu-group-title">P0/P1 · 任务</div>

        <div class="menu-item" data-view="scan-task-list">扫描计划</div>

        <div class="menu-item" data-view="survey-list">计划实例 survey</div>

        <div class="menu-item" data-view="subtask-list">子任务 sub_task</div>

        <div class="menu-item" data-view="preview-scanners">下发前预览</div>

        <div class="menu-item" data-view="queue-monitor">队列监控</div>

      </div>

      <div class="menu-group"><div class="menu-group-title">P1 · 观测</div>

        <div class="menu-item" data-view="dashboard">扫描器仪表盘</div>

        <div class="menu-item" data-view="alert-rules">告警规则</div>

      </div>

      <div class="menu-group"><div class="menu-group-title">P2 · 模板与预检</div>

        <div class="menu-item" data-view="template-sync">模板 / 字典同步</div>

        <div class="menu-item" data-view="weakpwd-sync">弱口令字典</div>

        <div class="menu-item" data-view="auth-precheck">登录凭据预检</div>

      </div>

    </nav>

  </aside>

"""



TOPBAR = """

    <header class="topbar">

      <small>扫描治理中心 v2 · PRD P0–P2 · 绿盟 LM · 默认配置 1A/2A</small>

      <div style="display:flex;gap:8px">

        <button class="btn" type="button" onclick="showView('story-s3')">模拟对账 S3</button>

        <button class="btn btn-primary" type="button" onclick="openSubTaskDrawer('ST-20260614-002')">子任务抽屉 S5</button>

      </div>

    </header>

"""



BANNER = """

      <div class="mock-banner">

        <strong>原型 v2</strong>：独立治理中心菜单（1A）· PRD 全量 P0–P2 · 仅绿盟 LM 深描 ·

        必画故事 S2 工单下发 / S3 对账 MISSING / S5 DRIFT 操控。

        Mock 服务 <code>vuln-task-center:18087</code>，执行真相源 <code>scan_sub_task</code>。

      </div>

"""



VIEWS = """

      <section id="view-overview" class="view active">

        <div class="breadcrumb">扫描治理 / 功能总览</div>

        <div class="legend">

          <span class="dev-done">已实现（代码锚点存在）</span>

          <span class="dev-todo">待开发（PRD 目标）</span>

          <span class="dev-skip">P3+ 暂不画</span>

          <span class="phase p0">P0</span><span class="phase p1">P1</span><span class="phase p2">P2</span>

        </div>

        <div class="stat-row">

          <div class="stat-card"><div class="label">注册节点</div><div class="value">12</div><div class="helper">healthy 9 · offline 1</div></div>

          <div class="stat-card"><div class="label">执行中子任务</div><div class="value">47</div><div class="helper">scan_sub_task 真相源</div></div>

          <div class="stat-card"><div class="label">对账差异</div><div class="value" style="color:var(--error)">5</div><div class="helper">ORPHAN 2 · DRIFT 2 · MISSING 1</div></div>

          <div class="stat-card"><div class="label">队列积压</div><div class="value">23</div><div class="helper">send 8 · wait 15</div></div>

        </div>

        <div class="sitemap-grid">

          <div class="sitemap-card" onclick="showView('node-list')"><h3>设备治理 <span class="phase p0">P0</span></h3><ul><li>扫描节点 Registry + Metrics</li><li>能力目录 LM Profile</li><li>逻辑扫描器 / 场景</li></ul></div>

          <div class="sitemap-card" onclick="showView('reconcile-list')"><h3>任务对账 <span class="phase p0">P0</span></h3><ul><li>平台 vs active_list</li><li>MATCHED / ORPHAN / MISSING / DRIFT</li></ul></div>

          <div class="sitemap-card" onclick="showView('survey-list')"><h3>调度编排 <span class="phase p0">P0</span></h3><ul><li>dispatch-detail 三栏参数</li><li>sync-status / pause / resume</li></ul></div>

          <div class="sitemap-card" onclick="showView('story-s2')"><h3>端到端故事</h3><ul><li>S2 vul-pass 下发 → 子任务</li><li>S3 超时对账 MISSING</li><li>S5 DRIFT → sync/pause/resume</li></ul></div>

        </div>

      </section>



      <section id="view-story-s2" class="view">

        <div class="breadcrumb"><a onclick="showView('overview')">总览</a> / 故事 S2 · 工单下发</div>

        <div class="card"><div class="card-title">S2：vul-pass 创建扫描 → VTC 路由 → 子任务执行</div>

        <div class="card-body">

          <div class="story-flow">

            <span class="story-step" onclick="toast('vul-pass VulScanTaskUi.create')">1. vul-pass 工单</span>

            <span class="story-arrow">→</span>

            <span class="story-step" onclick="showView('preview-scanners')">2. preview-scanners</span>

            <span class="story-arrow">→</span>

            <span class="story-step" onclick="toast('QueueAppServiceImpl 选节点')">3. Router 选节点</span>

            <span class="story-arrow">→</span>

            <span class="story-step" onclick="toast('ScannerAdapter-LM task.create')">4. Adapter 下发</span>

            <span class="story-arrow">→</span>

            <span class="story-step" onclick="openSubTaskDrawer('ST-20260614-001')">5. scan_sub_task</span>

          </div>

          <pre class="code-block">POST /vuln-task-center/v1/scan/task/preview-scanners

POST /vuln-task-center/v1/scan/task  → surveyId

GET  /v1/scan/task/{surveyId}/dispatch-detail

现有 MsgSendLM 逐步替换为 ScannerAdapter-LM（P0 目标）</pre>

        </div></div>

      </section>



      <section id="view-story-s3" class="view">

        <div class="breadcrumb"><a onclick="showView('overview')">总览</a> / 故事 S3 · 对账恢复</div>

        <div class="card"><div class="card-title">S3：定时对账发现 MISSING → 重试下发</div>

        <div class="card-body">

          <div class="story-flow">

            <span class="story-step">1. Cron reconcile</span><span class="story-arrow">→</span>

            <span class="story-step" onclick="showView('reconcile-list')">2. active_list 对比</span><span class="story-arrow">→</span>

            <span class="story-step" onclick="showView('reconcile-diff')">3. MISSING 详情</span><span class="story-arrow">→</span>

            <span class="story-step" onclick="toast('POST retry')">4. 重试下发</span>

          </div>

          <table><thead><tr><th>sub_task</th><th>平台状态</th><th>设备 task_id</th><th>结论</th></tr></thead>

          <tbody><tr><td>ST-MISS-001</td><td>执行中</td><td>—</td><td><span class="tag tag-orange">MISSING</span> 超时 15min 未出现在 active_list</td></tr></tbody></table>

        </div></div>

      </section>



      <section id="view-story-s5" class="view">

        <div class="breadcrumb"><a onclick="showView('overview')">总览</a> / 故事 S5 · 漂移操控</div>

        <div class="card"><div class="card-title">S5：DRIFT 检测 → sync-status → pause / resume</div>

        <div class="card-body">

          <div class="story-flow">

            <span class="story-step" onclick="showView('reconcile-list')">1. DRIFT 行</span><span class="story-arrow">→</span>

            <span class="story-step" onclick="openSubTaskDrawer('ST-20260614-002')">2. 子任务抽屉</span><span class="story-arrow">→</span>

            <span class="story-step" onclick="toast('POST sync-status')">3. sync-status</span><span class="story-arrow">→</span>

            <span class="story-step" onclick="toast('POST pause/resume')">4. 人工 pause/resume</span>

          </div>

          <div class="kv-row"><div class="k">平台进度</div><div class="v">45% · 执行中</div></div>

          <div class="kv-row"><div class="k">设备进度</div><div class="v">60% · 已暂停（管理员在 RSAS 控制台暂停）</div></div>

        </div></div>

      </section>



      <section id="view-node-list" class="view">

        <div class="breadcrumb"><a onclick="showView('overview')">总览</a> / 扫描节点</div>

        <div class="card"><div class="card-body"><div class="search-row">

          <div class="form-item"><label>厂商</label><select><option selected>绿盟 LM</option></select></div>

          <div class="form-item"><label>健康状态</label><select><option>全部</option><option>healthy</option><option>offline</option></select></div>

          <div class="form-item"><label>&nbsp;</label><button class="btn btn-primary">查询</button></div>

        </div></div></div>

        <div class="card"><div class="card-title"><span>扫描节点 <span class="api-path">GET /v1/scan/node</span> <span class="dev-done">部分实现</span></span>

          <button class="btn btn-primary" onclick="showView('node-create')">新增节点</button></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>名称</th><th>厂商</th><th>URL</th><th>健康</th><th>负载</th><th>能力</th><th>探活</th><th>操作</th></tr></thead>

          <tbody>

            <tr><td><a class="btn-link" onclick="showView('node-detail')">绿盟-北京-01</a></td><td>绿盟</td><td><code>https://10.65.6.156</code></td>

              <td><span class="tag tag-green">healthy</span></td><td>3/10</td><td>14/14</td><td>10:32:01</td>

              <td><button class="btn-link" onclick="toast('POST probe')">探活</button>

                  <button class="btn-link" onclick="showView('node-create')">编辑</button></td></tr>

            <tr><td>绿盟-上海-02</td><td>绿盟</td><td><code>https://10.65.6.157</code></td>

              <td><span class="tag tag-orange">degraded</span></td><td>9/10</td><td>12/14</td><td>10:28:44</td><td><button class="btn-link">探活</button></td></tr>

            <tr><td>绿盟-省中心</td><td>绿盟</td><td><code>https://10.20.1.88</code></td>

              <td><span class="tag tag-red">offline</span></td><td>—</td><td>6/14</td><td>08:15:00</td><td><button class="btn-link">探活</button></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-node-create" class="view">

        <div class="breadcrumb"><a onclick="showView('node-list')">扫描节点</a> / 新增 / 编辑</div>

        <div class="card"><div class="card-title">节点表单 <span class="api-path">POST /v1/scan/node</span> <span class="dev-todo">待开发</span></div>

        <div class="card-body"><div class="form-grid">

          <div class="form-item"><label class="required">节点名称</label><input value="绿盟-北京-01" /></div>

          <div class="form-item"><label class="required">厂商版本</label><select><option>绿盟 RSAS V6.0.8</option></select></div>

          <div class="form-item full"><label class="required">设备 URL</label><input value="https://10.65.6.156" style="width:100%" /></div>

          <div class="form-item"><label class="required">API 用户名</label><input value="api_user" /></div>

          <div class="form-item"><label class="required">API 密码</label><input type="password" value="******" /></div>

          <div class="form-item"><label>最大并发任务</label><input type="number" value="10" /></div>

          <div class="form-item"><label>所属组织</label><select><option>省公司/信安部</option></select></div>

          <div class="form-item full"><label>备注</label><input value="生产 RSAS，定时 syn_type 同步" style="width:100%" /></div>

        </div>

        <div style="margin-top:16px"><button class="btn btn-primary" onclick="toast('保存成功');showView('node-list')">保存</button>

          <button class="btn" onclick="showView('node-list')">取消</button></div></div></div>

      </section>



      <section id="view-node-detail" class="view">

        <div class="breadcrumb"><a onclick="showView('node-list')">扫描节点</a> / 绿盟-北京-01</div>

        <div class="detail-page-grid">

          <div class="detail-sidebar"><div class="card"><div class="card-title">节点概览</div><div class="card-body">

            <div class="kv-row"><div class="k">RSAS 版本</div><div class="v">V6.0R04F00SP05</div></div>

            <div class="kv-row"><div class="k">漏洞库版本</div><div class="v">V6.0R02F01.2103</div></div>

            <div class="kv-row"><div class="k">health</div><div class="v"><span class="tag tag-green">healthy</span></div></div>

            <div class="kv-row"><div class="k">Adapter</div><div class="v"><code>ScannerAdapter-LM</code></div></div>

            <button class="btn btn-primary" style="margin-top:8px;width:100%" onclick="toast('GET metrics 刷新')">刷新指标</button>

            <button class="btn" style="margin-top:8px;width:100%" onclick="showView('template-sync')">模板同步</button>

          </div></div></div>

          <div>

            <div class="card"><div class="card-title">实时指标 <span class="api-path">GET /v1/scanner/node/{id}/metrics</span></div>

            <div class="card-body"><div class="stat-row">

              <div class="stat-card"><div class="label">CPU</div><div class="value">12%</div></div>

              <div class="stat-card"><div class="label">内存</div><div class="value">36%</div></div>

              <div class="stat-card"><div class="label">磁盘</div><div class="value">23%</div></div>

              <div class="stat-card"><div class="label">活跃任务</div><div class="value">3</div></div>

            </div><div class="chart-placeholder">system.status 趋势（P1）</div></div></div>

            <div class="card"><div class="card-title">节点能力（14/14） <span class="dev-todo">Capability Registry</span></div>

            <div class="card-body"><div class="checkbox-grid">

              <div class="checkbox-item"><input type="checkbox" checked disabled /> task.create</div>

              <div class="checkbox-item"><input type="checkbox" checked disabled /> task.active_list</div>

              <div class="checkbox-item"><input type="checkbox" checked disabled /> system.status</div>

              <div class="checkbox-item"><input type="checkbox" checked disabled /> task.pause</div>

              <div class="checkbox-item"><input type="checkbox" checked disabled /> task.resume</div>

              <div class="checkbox-item"><input type="checkbox" checked disabled /> template.baseline.list</div>

            </div></div></div>

          </div>

        </div>

      </section>



      <section id="view-classify-list" class="view">

        <div class="breadcrumb">设备治理 / 厂商版本</div>

        <div class="card"><div class="card-title"><span>厂商 / 版本 <span class="api-path">GET /v1/scanner/classify</span></span>

          <button class="btn btn-primary">新增版本</button></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>厂商</th><th>产品</th><th>版本</th><th>Adapter</th><th>能力 Profile</th><th>节点数</th></tr></thead>

          <tbody>

            <tr><td>绿盟</td><td>RSAS</td><td>V6.0.8</td><td><code>ScannerAdapter-LM</code></td><td>14 capabilities</td><td>12</td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-scanner-list" class="view">

        <div class="breadcrumb">设备治理 / 逻辑扫描器</div>

        <div class="card"><div class="card-title"><span>逻辑扫描器 <span class="api-path">GET /v1/scanner</span></span>

          <button class="btn btn-primary">新增扫描器</button></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>名称</th><th>绑定节点</th><th>组织</th><th>扫描范围</th><th>场景</th><th>状态</th><th>操作</th></tr></thead>

          <tbody>

            <tr><td>省公司-漏洞扫描-A</td><td>绿盟-北京-01</td><td>省公司/信安部</td><td>10.65.0.0/16</td><td>漏洞扫描</td>

              <td><span class="tag tag-green">正常</span></td><td><button class="btn-link">编辑</button></td></tr>

            <tr><td>地市-基线扫描</td><td>绿盟-上海-02</td><td>地市</td><td>暴露面资产</td><td>基线核查</td>

              <td><span class="tag tag-orange">节点 degraded</span></td><td><button class="btn-link">编辑</button></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-scene-list" class="view">

        <div class="breadcrumb">设备治理 / 业务场景</div>

        <div class="card"><div class="card-title">场景配置 <span class="api-path">GET /v1/scanner/scene</span> <span class="dev-todo">待开发</span></div>

        <div class="card-body"><table>

          <thead><tr><th>场景码</th><th>名称</th><th>任务类型</th><th>默认模板</th><th>路由策略</th></tr></thead>

          <tbody>

            <tr><td><code>vuln_scan</code></td><td>漏洞扫描</td><td>host_scan</td><td>端口扫描</td><td>负载最低 + 范围匹配</td></tr>

            <tr><td><code>baseline</code></td><td>基线核查</td><td>baseline_scan</td><td>Windows 配置规范</td><td>能力匹配</td></tr>

            <tr><td><code>weakpwd</code></td><td>弱口令</td><td>pwd_scan</td><td>SSH默认用户</td><td>负载最低</td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-capability-catalog" class="view">

        <div class="breadcrumb">设备治理 / 能力目录 LM</div>

        <div class="card"><div class="card-body">

          <div class="filter-chips" id="capFilters">

            <span class="filter-chip active" data-cap="all">全部</span>

            <span class="filter-chip" data-cap="task">任务</span>

            <span class="filter-chip" data-cap="template">模板</span>

            <span class="filter-chip" data-cap="system">系统</span>

          </div>

        </div></div>

        <div class="card"><div class="card-title">绿盟 RSAS V6.0.8 Profile <span class="api-path">GET /v1/scanner/capability/catalog</span></div>

        <div class="card-body" style="padding-top:0"><table id="capTable">

          <thead><tr><th>capability_code</th><th>RSAS API</th><th>必选</th><th>syn_type</th><th>状态</th></tr></thead>

          <tbody>

            <tr data-cap="task"><td><code>task.create</code></td><td>POST /api/task/create</td><td>是</td><td>—</td><td><span class="dev-done">Adapter</span></td></tr>

            <tr data-cap="task"><td><code>task.active_list</code></td><td>GET /api/task/active_list</td><td>是</td><td>active_list</td><td><span class="dev-done">VulnTaskListenerLM</span></td></tr>

            <tr data-cap="system"><td><code>system.status</code></td><td>GET /api/system/status</td><td>是</td><td>sys_status</td><td><span class="dev-done">已实现</span></td></tr>

            <tr data-cap="task"><td><code>task.pause</code></td><td>POST /api/task/pause/{id}</td><td>否</td><td>task_pause</td><td><span class="dev-todo">P0</span></td></tr>

            <tr data-cap="task"><td><code>task.resume</code></td><td>POST /api/task/resume/{id}</td><td>否</td><td>—</td><td><span class="dev-todo">P0</span></td></tr>

            <tr data-cap="template"><td><code>template.baseline.list</code></td><td>GET /api/template/baseline/list</td><td>否</td><td>syn_baseline_data</td><td><span class="dev-done">SynVulnData</span></td></tr>

            <tr data-cap="template"><td><code>template.sysvuln.list</code></td><td>GET /api/template/sysvuln/list</td><td>否</td><td>syn_sysvuln_data</td><td><span class="dev-done">SynVulnData</span></td></tr>

            <tr data-cap="template"><td><code>userpwd.list</code></td><td>GET /api/userpwd/list</td><td>否</td><td>syn_userpwd_data</td><td><span class="dev-done">SynVulnData</span></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-reconcile-list" class="view">

        <div class="breadcrumb">调度编排 / 任务对账</div>

        <div class="stat-row">

          <div class="stat-card"><div class="label">MATCHED</div><div class="value" style="color:var(--success)">42</div></div>

          <div class="stat-card"><div class="label">ORPHAN</div><div class="value" style="color:var(--error)">2</div></div>

          <div class="stat-card"><div class="label">MISSING</div><div class="value" style="color:var(--warning)">1</div></div>

          <div class="stat-card"><div class="label">DRIFT</div><div class="value" style="color:var(--primary)">2</div></div>

        </div>

        <div class="card"><div class="card-body"><div class="search-row">

          <div class="form-item"><label>节点</label><select><option>绿盟-北京-01</option><option>全部</option></select></div>

          <div class="form-item"><label>差异类型</label><select><option>全部</option><option>ORPHAN</option><option>MISSING</option><option>DRIFT</option></select></div>

          <div class="form-item"><label>&nbsp;</label><button class="btn btn-primary" onclick="toast('POST /v1/reconcile/tasks/trigger')">立即对账</button></div>

        </div>

        <p class="helper">平台 scan_sub_task ? 设备 GET /api/task/active_list · Cron 默认 5min</p></div></div>

        <div class="card"><div class="card-title">对账结果 <span class="api-path">GET /v1/reconcile/tasks</span> <span class="dev-todo">P0 新增</span></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>类型</th><th>节点</th><th>sub_task</th><th>task_id</th><th>任务名</th><th>平台状态</th><th>设备状态</th><th>操作</th></tr></thead>

          <tbody>

            <tr><td><span class="tag tag-red">ORPHAN</span></td><td>绿盟-北京-01</td><td>—</td><td>882</td><td>admin_手工扫描</td><td>—</td><td>扫描中</td>

              <td><button class="btn-link" onclick="openModal('orphan')">处理</button></td></tr>

            <tr><td><span class="tag tag-orange">MISSING</span></td><td>绿盟-北京-01</td><td>ST-MISS-001</td><td>—</td><td>工单-102-漏洞排查</td><td>执行中</td><td>—</td>

              <td><button class="btn-link" onclick="showView('reconcile-diff')">详情</button>

                  <button class="btn-link" onclick="toast('POST retry')">重试</button></td></tr>

            <tr><td><span class="tag tag-blue">DRIFT</span></td><td>绿盟-北京-01</td><td>ST-20260614-002</td><td>875</td><td>月扫-195.0/24</td><td>执行中 45%</td><td>暂停 60%</td>

              <td><button class="btn-link" onclick="openSubTaskDrawer('ST-20260614-002')">操控 S5</button></td></tr>

            <tr><td><span class="tag tag-green">MATCHED</span></td><td>绿盟-北京-01</td><td>ST-003</td><td>870</td><td>例行扫描</td><td>已完成</td><td>完成</td><td>—</td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-reconcile-diff" class="view">

        <div class="breadcrumb"><a onclick="showView('reconcile-list')">任务对账</a> / 差异详情 ST-MISS-001</div>

        <div class="card"><div class="card-title">MISSING · diff 详情 <span class="api-path">GET /v1/reconcile/tasks/{id}</span></div>

        <div class="card-body">

          <table class="diff-table"><thead><tr><th>字段</th><th>平台 scan_sub_task</th><th>设备 active_list</th></tr></thead>

          <tbody>

            <tr><td>task_id / plan_id</td><td class="diff-add">—（未回填）</td><td class="diff-del">无匹配项</td></tr>

            <tr><td>status</td><td class="diff-add">RUNNING</td><td class="diff-del">—</td></tr>

            <tr><td>progress</td><td>12%</td><td>—</td></tr>

            <tr><td>last_dispatch_at</td><td>2026-06-14 10:05:00</td><td>—</td></tr>

            <tr><td>reconcile_at</td><td colspan="2">2026-06-14 10:20:00 · 结论 MISSING（超时 15min）</td></tr>

          </tbody></table>

          <div style="margin-top:16px"><button class="btn btn-primary" onclick="toast('retry 下发')">重试下发</button>

            <button class="btn" onclick="toast('标记失败')">标记失败</button></div>

        </div></div>

      </section>



      <section id="view-scan-task-list" class="view">

        <div class="breadcrumb">任务 / 扫描计划</div>

        <div class="card"><div class="card-title"><span>扫描计划 <span class="api-path">GET /v1/scan/plan</span></span>

          <button class="btn btn-primary">新建计划</button></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>计划 ID</th><th>名称</th><th>场景</th><th>Cron</th><th>目标范围</th><th>状态</th><th>操作</th></tr></thead>

          <tbody>

            <tr><td><code>PLAN-001</code></td><td>月度漏洞扫描</td><td>漏洞扫描</td><td>0 0 2 1 * ?</td><td>10.65.0.0/16</td>

              <td><span class="tag tag-green">启用</span></td><td><button class="btn-link">编辑</button><button class="btn-link">立即执行</button></td></tr>

            <tr><td><code>PLAN-002</code></td><td>基线季度核查</td><td>基线核查</td><td>0 0 3 1 1,4,7,10 ?</td><td>核心系统</td>

              <td><span class="tag tag-default">停用</span></td><td><button class="btn-link">编辑</button></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-survey-list" class="view">

        <div class="breadcrumb">任务 / 计划实例</div>

        <div class="card"><div class="card-title">计划实例 survey <span class="api-path">GET /v1/scan/task</span> <span class="dev-done">部分</span></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>surveyId</th><th>计划/工单</th><th>场景</th><th>子任务数</th><th>进度</th><th>对账</th><th>操作</th></tr></thead>

          <tbody>

            <tr><td><code>SUR-77821</code></td><td>工单-102-漏洞排查</td><td>漏洞扫描</td><td>3</td>

              <td><div class="progress-bar"><span style="width:45%"></span></div></td>

              <td><span class="tag tag-orange">1 MISSING</span></td>

              <td><button class="btn-link" onclick="openDispatchDrawer('SUR-77821')">下发详情</button>

                  <button class="btn-link" onclick="showView('subtask-list')">子任务</button></td></tr>

            <tr><td><code>SUR-77805</code></td><td>月度漏洞扫描</td><td>漏洞扫描</td><td>5</td>

              <td><div class="progress-bar"><span style="width:78%"></span></div></td>

              <td><span class="tag tag-green">全部 MATCHED</span></td>

              <td><button class="btn-link" onclick="openDispatchDrawer('SUR-77805')">下发详情</button></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-subtask-list" class="view">

        <div class="breadcrumb">任务 / 子任务</div>

        <div class="card"><div class="card-body"><div class="search-row">

          <div class="form-item"><label>surveyId</label><input placeholder="SUR-77821" /></div>

          <div class="form-item"><label>状态</label><select><option>全部</option><option>执行中</option><option>DRIFT</option></select></div>

          <div class="form-item"><label>&nbsp;</label><button class="btn btn-primary">查询</button></div>

        </div></div></div>

        <div class="card"><div class="card-title">子任务 scan_sub_task <span class="api-path">GET /v1/scan/sub-task</span></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>sub_task_id</th><th>surveyId</th><th>节点</th><th>plan_id</th><th>进度</th><th>状态</th><th>对账</th><th>操作</th></tr></thead>

          <tbody>

            <tr><td><code>ST-20260614-001</code></td><td>SUR-77821</td><td>绿盟-北京-01</td><td>874</td><td>100%</td>

              <td><span class="tag tag-green">已完成</span></td><td>MATCHED</td>

              <td><button class="btn-link" onclick="openSubTaskDrawer('ST-20260614-001')">详情</button></td></tr>

            <tr><td><code>ST-20260614-002</code></td><td>SUR-77821</td><td>绿盟-北京-01</td><td>875</td><td>45%</td>

              <td><span class="tag tag-blue">执行中</span></td><td><span class="tag tag-blue">DRIFT</span></td>

              <td><button class="btn-link" onclick="openSubTaskDrawer('ST-20260614-002')">操控</button></td></tr>

            <tr><td><code>ST-MISS-001</code></td><td>SUR-77821</td><td>绿盟-北京-01</td><td>—</td><td>12%</td>

              <td><span class="tag tag-orange">执行中</span></td><td><span class="tag tag-orange">MISSING</span></td>

              <td><button class="btn-link" onclick="showView('reconcile-diff')">对账</button></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-preview-scanners" class="view">

        <div class="breadcrumb">任务 / 下发前预览</div>

        <div class="card"><div class="card-title"><span class="api-path">POST /v1/scan/task/preview-scanners</span> <span class="dev-done">QueueAppServiceImpl</span></div>

        <div class="card-body"><div class="form-grid">

          <div class="form-item"><label>业务场景</label><select id="previewScene"><option value="vuln">漏洞扫描</option><option value="baseline">基线核查</option></select></div>

          <div class="form-item"><label>扫描 IP / 范围</label><input id="previewIp" value="10.65.195.0/24" /></div>

          <div class="form-item"><label>组织</label><select><option>省公司/信安部</option></select></div>

          <div class="form-item"><label>&nbsp;</label><button class="btn btn-primary" onclick="runPreview()">预览候选扫描器</button></div>

        </div>

        <div id="previewResult" class="hidden" style="margin-top:20px">

          <h4 style="margin-bottom:12px">候选扫描器（按得分排序）</h4>

          <div class="node-card selected" style="margin-bottom:8px"><h4 style="display:flex;justify-content:space-between">绿盟-北京-01 <span class="score-badge">92</span></h4>

            <p style="font-size:13px;color:var(--text-secondary)">负载 3/10 · 能力匹配 · 范围匹配 · 组织匹配</p></div>

          <div class="node-card" style="margin-bottom:8px;opacity:.7"><h4 style="display:flex;justify-content:space-between">绿盟-上海-02 <span style="color:var(--warning)">58</span></h4>

            <p style="font-size:13px;color:var(--text-secondary)">负载 9/10 · 能力匹配 · 范围匹配</p></div>

          <ul class="excluded-list"><strong>排除原因 excludedReasons：</strong>

            <li>绿盟-省中心 — offline，health_status=offline</li>

            <li>绿盟-测试-03 — 扫描范围 10.66.0.0/16 不匹配目标 10.65.195.0/24</li>

            <li>绿盟-上海-02 — 负载 9/10 超过阈值（仍列候选但降权）</li>

          </ul>

        </div></div></div>

      </section>



      <section id="view-queue-monitor" class="view">

        <div class="breadcrumb">任务 / 队列监控</div>

        <div class="stat-row">

          <div class="stat-card"><div class="label">sendQueue</div><div class="value">8</div><div class="helper">待下发</div></div>

          <div class="stat-card"><div class="label">waitQueue</div><div class="value">15</div><div class="helper">节点满载等待</div></div>

          <div class="stat-card"><div class="label">executeQueue</div><div class="value">47</div><div class="helper">已下发执行中</div></div>

          <div class="stat-card"><div class="label">死信 / 异常</div><div class="value" style="color:var(--error)">3</div></div>

        </div>

        <div class="card"><div class="card-title">队列三分 Tab</div>

        <div class="card-body" style="padding-top:0">

          <div class="tabs" id="queueTabs">

            <div class="tab active" data-qtab="send">sendQueue (8)</div>

            <div class="tab" data-qtab="wait">waitQueue (15)</div>

            <div class="tab" data-qtab="execute">executeQueue (47)</div>

          </div>

          <div id="qtab-send" class="tab-panel active"><table>

            <thead><tr><th>surveyId</th><th>子任务</th><th>目标节点</th><th>入队时间</th><th>重试</th></tr></thead>

            <tbody><tr><td>SUR-77822</td><td>ST-pending-01</td><td>绿盟-北京-01</td><td>10:31:02</td><td>0</td></tr></tbody></table></div>

          <div id="qtab-wait" class="tab-panel"><table>

            <thead><tr><th>surveyId</th><th>原因</th><th>等待节点</th><th>等待时长</th></tr></thead>

            <tbody><tr><td>SUR-77810</td><td>节点并发已满 10/10</td><td>绿盟-上海-02</td><td>3m 12s</td></tr></tbody></table></div>

          <div id="qtab-execute" class="tab-panel"><table>

            <thead><tr><th>sub_task</th><th>plan_id</th><th>节点</th><th>进度</th><th>状态</th></tr></thead>

            <tbody><tr><td>ST-20260614-002</td><td>875</td><td>绿盟-北京-01</td><td>45%</td><td>DRIFT</td></tr></tbody></table></div>

        </div></div>

      </section>



      <section id="view-dashboard" class="view">

        <div class="breadcrumb">观测 / 扫描器仪表盘</div>

        <div class="stat-row">

          <div class="stat-card"><div class="label">在线节点</div><div class="value">11/12</div></div>

          <div class="stat-card"><div class="label">平均 CPU</div><div class="value">18%</div></div>

          <div class="stat-card"><div class="label">活跃子任务</div><div class="value">47</div></div>

          <div class="stat-card"><div class="label">凭证过期</div><div class="value" style="color:var(--warning)">2</div></div>

        </div>

        <div class="card"><div class="card-body"><div class="chart-placeholder">GET /v1/scanner/dashboard · 集群负载 / 对账差异趋势 / 队列水位</div></div></div>

      </section>



      <section id="view-alert-rules" class="view">

        <div class="breadcrumb">观测 / 告警规则</div>

        <div class="card"><div class="card-title"><span>告警规则</span><button class="btn btn-primary">新增规则</button></div>

        <div class="card-body" style="padding-top:0"><table>

          <thead><tr><th>规则名</th><th>条件</th><th>级别</th><th>通知</th><th>状态</th></tr></thead>

          <tbody>

            <tr><td>节点离线</td><td>offline 持续 &gt; 5min</td><td><span class="tag tag-red">严重</span></td><td>钉钉 + 邮件</td><td>启用</td></tr>

            <tr><td>负载过高</td><td>current/max &gt; 90%</td><td><span class="tag tag-orange">警告</span></td><td>钉钉</td><td>启用</td></tr>

            <tr><td>对账 ORPHAN</td><td>ORPHAN &gt; 0</td><td><span class="tag tag-blue">提示</span></td><td>站内信</td><td>启用</td></tr>

            <tr><td>MISSING 超时</td><td>MISSING &gt; 30min 未处理</td><td><span class="tag tag-red">严重</span></td><td>钉钉</td><td><span class="dev-todo">P1</span></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-template-sync" class="view">

        <div class="breadcrumb">P2 / 模板同步</div>

        <div class="card"><div class="card-title"><span>模板同步</span>

          <button class="btn btn-primary" onclick="toast('POST templates/sync')">全量同步</button></div>

        <div class="card-body"><div class="search-row">

          <div class="form-item"><label>节点</label><select><option>绿盟-北京-01</option></select></div>

          <div class="form-item"><label>模板类型</label><select><option>全部</option><option>sysvuln</option><option>baseline</option></select></div>

        </div>

        <table style="margin-top:12px"><thead><tr><th>类型</th><th>ID/uuid</th><th>名称</th><th>本地版本</th><th>设备版本</th><th>diff</th><th>同步时间</th></tr></thead>

          <tbody>

            <tr><td>sysvuln</td><td>10</td><td>端口扫描</td><td>v3</td><td>v3</td><td><span class="tag tag-green">一致</span></td><td>2026-06-14 00:45</td></tr>

            <tr><td>baseline</td><td>66c221be-…</td><td>Windows 配置规范</td><td>v2</td><td>v1</td><td><button class="btn-link" onclick="openModal('templateDiff')">查看 diff</button></td><td>2026-06-13</td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-weakpwd-sync" class="view">

        <div class="breadcrumb">P2 / 弱口令字典</div>

        <div class="card"><div class="card-title">弱口令字典 <span class="api-path">syn_userpwd_data</span></div>

        <div class="card-body"><table>

          <thead><tr><th>字典 ID</th><th>名称</th><th>条目数</th><th>同步状态</th><th>操作</th></tr></thead>

          <tbody>

            <tr><td>188</td><td>SSH默认用户</td><td>1,204</td><td><span class="tag tag-green">已同步</span></td><td><button class="btn-link">同步</button></td></tr>

            <tr><td>189</td><td>数据库弱口令</td><td>856</td><td><span class="tag tag-orange">待同步</span></td><td><button class="btn-link">同步</button></td></tr>

          </tbody></table></div></div>

      </section>



      <section id="view-auth-precheck" class="view">

        <div class="breadcrumb">P2 / 登录凭据预检</div>

        <div class="card"><div class="card-title">凭据预检 <span class="api-path">POST /v1/scanner/auth/precheck</span> <span class="dev-todo">P2</span></div>

        <div class="card-body"><div class="form-grid">

          <div class="form-item"><label>目标 IP</label><input value="10.65.195.204" /></div>

          <div class="form-item"><label>协议</label><select><option>SSH</option><option>RDP</option><option>SNMP</option></select></div>

          <div class="form-item"><label>用户名</label><input value="root" /></div>

          <div class="form-item"><label>密码</label><input type="password" value="******" /></div>

          <div class="form-item"><label>端口</label><input value="22" /></div>

          <div class="form-item"><label>&nbsp;</label><button class="btn btn-primary" onclick="toast('预检成功 · 耗时 1.2s')">执行预检</button></div>

        </div>

        <div class="timeline" style="margin-top:20px">

          <div class="timeline-item"><div class="t">10:32:01</div>连接 10.65.195.204:22</div>

          <div class="timeline-item"><div class="t">10:32:02</div>SSH 握手成功</div>

          <div class="timeline-item"><div class="t">10:32:02</div>凭据验证通过</div>

        </div></div></div>

      </section>



      <div class="page-note">vuln-task-center 扫描治理中心 · PRD V0.1 · 原型 v2 · 2026-06-14 · 默认配置 1A/2A/S2+S3+S5/LM</div>

"""



DRAWERS = """

<div id="drawerSubTask" class="drawer-overlay" onclick="if(event.target===this)closeAllDrawers()">

  <div class="drawer drawer-full" onclick="event.stopPropagation()">

    <div class="drawer-header"><span id="stDrawerTitle">子任务详情</span><button class="btn-link" onclick="closeAllDrawers()">关闭</button></div>

    <div class="drawer-body">

      <div class="drawer-tabs" id="stDrawerTabs">

        <div class="drawer-tab active" data-st-panel="info">基本信息</div>

        <div class="drawer-tab" data-st-panel="params">下发参数</div>

        <div class="drawer-tab" data-st-panel="reconcile">对账 / 操控</div>

        <div class="drawer-tab" data-st-panel="timeline">时间线</div>

      </div>

      <div id="st-panel-info" class="drawer-panel active">

        <div class="kv-row"><div class="k">sub_task_id</div><div class="v" id="st-id">ST-20260614-002</div></div>

        <div class="kv-row"><div class="k">surveyId</div><div class="v">SUR-77821</div></div>

        <div class="kv-row"><div class="k">plan_id (RSAS)</div><div class="v"><code>875</code></div></div>

        <div class="kv-row"><div class="k">节点</div><div class="v">绿盟-北京-01</div></div>

        <div class="kv-row"><div class="k">平台进度</div><div class="v">45% · 执行中</div></div>

        <div class="kv-row"><div class="k">设备进度</div><div class="v">60% · 已暂停</div></div>

        <div class="kv-row"><div class="k">对账</div><div class="v"><span class="tag tag-blue">DRIFT</span></div></div>

      </div>

      <div id="st-panel-params" class="drawer-panel">

        <pre class="code-block" id="st-params-json">{

  "taskType": "vuln_scan",

  "scanIp": "10.65.196.0/24",

  "templateId": 10,

  "templateName": "端口扫描",

  "credentials": "*** masked ***"

}</pre>

        <p class="helper">GET /v1/scan/task/{surveyId}/dispatch-detail · 子任务维度参数</p>

      </div>

      <div id="st-panel-reconcile" class="drawer-panel">

        <p style="margin-bottom:12px">S5：检测到 DRIFT，可同步设备状态或人工 pause/resume</p>

        <button class="btn btn-primary" onclick="toast('POST /v1/scan/sub-task/{id}/sync-status')">sync-status 同步</button>

        <button class="btn" onclick="toast('POST pause plan_id=875')">pause 暂停</button>

        <button class="btn" onclick="toast('POST resume plan_id=875')">resume 恢复</button>

        <button class="btn" onclick="toast('POST retry')">retry 重试</button>

      </div>

      <div id="st-panel-timeline" class="drawer-panel">

        <div class="timeline">

          <div class="timeline-item"><div class="t">10:05:00</div>创建 sub_task，入 sendQueue</div>

          <div class="timeline-item"><div class="t">10:05:02</div>Adapter task.create → plan_id=875</div>

          <div class="timeline-item"><div class="t">10:15:00</div>对账 MATCHED</div>

          <div class="timeline-item warn"><div class="t">10:25:00</div>对账 DRIFT：设备已暂停</div>

        </div>

      </div>

    </div>

    <div class="drawer-footer">

      <button class="btn btn-danger" onclick="toast('cancel 取消任务')">取消任务</button>

      <button class="btn" onclick="closeAllDrawers()">关闭</button>

    </div>

  </div>

</div>



<div id="drawerDispatch" class="drawer-overlay" onclick="if(event.target===this)closeAllDrawers()">

  <div class="drawer drawer-full" onclick="event.stopPropagation()">

    <div class="drawer-header"><span id="dispatchTitle">下发详情</span><button class="btn-link" onclick="closeAllDrawers()">关闭</button></div>

    <div class="drawer-body">

      <p class="helper" style="margin-bottom:12px"><span class="api-path">GET /v1/scan/task/{surveyId}/dispatch-detail</span> · 三栏：平台请求 / 路由结果 / 子任务聚合</p>

      <div class="three-col">

        <div class="col-box"><h4>① 平台请求参数</h4>

          <pre class="code-block" style="max-height:200px">{

  "workOrderId": "WO-102",

  "scene": "vuln_scan",

  "targets": ["10.65.195.0/24","10.65.196.0/24","10.65.197.0/24"],

  "orgId": "ORG-001"

}</pre></div>

        <div class="col-box"><h4>② 路由 / 预览结果</h4>

          <ul style="font-size:12px;line-height:1.8;padding-left:16px">

            <li>10.65.195.0/24 → 绿盟-北京-01 (92分)</li>

            <li>10.65.196.0/24 → 绿盟-北京-01 (88分)</li>

            <li>10.65.197.0/24 → 绿盟-上海-02 (71分)</li>

          </ul>

          <p class="helper">preview-scanners + getNodeScannerMap</p></div>

        <div class="col-box"><h4>③ 子任务聚合</h4>

          <table style="font-size:12px"><tr><td>ST-001</td><td>100%</td><td>MATCHED</td></tr>

          <tr><td>ST-002</td><td>45%</td><td><span class="tag tag-blue">DRIFT</span></td></tr>

          <tr><td>ST-MISS</td><td>12%</td><td><span class="tag tag-orange">MISSING</span></td></tr></table>

          <p style="margin-top:8px">综合进度 45% · matched 1 / missing 1 / drift 1</p></div>

      </div>

    </div>

    <div class="drawer-footer">

      <button class="btn" onclick="showView('reconcile-list');closeAllDrawers()">打开对账</button>

      <button class="btn btn-primary" onclick="showView('subtask-list');closeAllDrawers()">子任务列表</button>

    </div>

  </div>

</div>



<div id="modalOrphan" class="modal-overlay" onclick="if(event.target===this)closeAllModals()">

  <div class="modal" onclick="event.stopPropagation()">

    <div class="modal-header">处理 ORPHAN 任务 <button class="btn-link" onclick="closeAllModals()">×</button></div>

    <div class="modal-body">

      <p style="margin-bottom:12px">设备 task_id=882 在 active_list 中存在，但平台无对应 scan_sub_task</p>

      <div class="form-item"><label>处理方式</label>

        <select><option>IGNORE 忽略（记录审计）</option><option>STOP 终止设备任务</option><option>ADOPT 纳管（创建 sub_task）</option></select>

      </div>

      <p class="helper"><span class="api-path">POST /v1/reconcile/tasks/orphan/handle</span></p>

    </div>

    <div class="modal-footer"><button class="btn" onclick="closeAllModals()">取消</button>

      <button class="btn btn-primary" onclick="toast('ORPHAN 已处理');closeAllModals()">确认</button></div>

  </div>

</div>



<div id="modalTemplateDiff" class="modal-overlay" onclick="if(event.target===this)closeAllModals()">

  <div class="modal" onclick="event.stopPropagation()">

    <div class="modal-header">模板 diff · Windows 配置规范 <button class="btn-link" onclick="closeAllModals()">×</button></div>

    <div class="modal-body"><table class="diff-table">

      <thead><tr><th>检查项</th><th>本地 v2</th><th>设备 v1</th></tr></thead>

      <tbody>

        <tr><td>密码复杂度策略</td><td class="diff-add">新增检查项 #128</td><td class="diff-del">不存在</td></tr>

        <tr><td>账户锁定阈值</td><td>5 次</td><td>5 次</td></tr>

      </tbody></table></div>

    <div class="modal-footer"><button class="btn btn-primary" onclick="toast('同步模板');closeAllModals()">同步到设备</button></div>

  </div>

</div>



<div id="toast" class="toast"></div>

"""



SCRIPT = """

<script>

(function(){

  function showView(name){

    document.querySelectorAll('.view').forEach(function(el){

      el.classList.toggle('active', el.id === 'view-' + name);

    });

    document.querySelectorAll('.menu-item[data-view]').forEach(function(item){

      item.classList.toggle('active', item.dataset.view === name);

    });

    window.scrollTo(0,0);

  }

  function showToast(msg){

    var t=document.getElementById('toast');

    t.textContent=msg; t.classList.add('show');

    clearTimeout(showToast._tm);

    showToast._tm=setTimeout(function(){t.classList.remove('show');},2600);

  }

  function closeAllDrawers(){ document.querySelectorAll('.drawer-overlay').forEach(function(d){d.classList.remove('show');}); }

  function closeAllModals(){ document.querySelectorAll('.modal-overlay').forEach(function(m){m.classList.remove('show');}); }

  function openSubTaskDrawer(id){

    document.getElementById('st-id').textContent=id;

    document.getElementById('stDrawerTitle').textContent='子任务详情 · '+id;

    document.getElementById('drawerSubTask').classList.add('show');

  }

  function openDispatchDrawer(surveyId){

    document.getElementById('dispatchTitle').textContent='下发详情 · '+surveyId;

    document.getElementById('drawerDispatch').classList.add('show');

  }

  function openModal(name){

    var map={orphan:'modalOrphan',templateDiff:'modalTemplateDiff'};

    var el=document.getElementById(map[name]||name);

    if(el) el.classList.add('show');

  }

  function runPreview(){ document.getElementById('previewResult').classList.remove('hidden'); showToast('preview-scanners 完成'); }



  document.querySelectorAll('.menu-item[data-view]').forEach(function(item){

    item.addEventListener('click',function(){ showView(item.dataset.view); });

  });

  document.getElementById('stDrawerTabs').addEventListener('click',function(e){

    var tab=e.target.closest('.drawer-tab[data-st-panel]');

    if(!tab) return;

    document.querySelectorAll('#stDrawerTabs .drawer-tab').forEach(function(t){t.classList.remove('active');});

    document.querySelectorAll('[id^="st-panel-"]').forEach(function(p){p.classList.remove('active');});

    tab.classList.add('active');

    document.getElementById('st-panel-'+tab.dataset.stPanel).classList.add('active');

  });

  document.getElementById('queueTabs').addEventListener('click',function(e){

    var tab=e.target.closest('.tab[data-qtab]');

    if(!tab) return;

    document.querySelectorAll('#queueTabs .tab').forEach(function(t){t.classList.remove('active');});

    document.querySelectorAll('[id^="qtab-"]').forEach(function(p){p.classList.remove('active');});

    tab.classList.add('active');

    document.getElementById('qtab-'+tab.dataset.qtab).classList.add('active');

  });

  document.getElementById('capFilters').addEventListener('click',function(e){

    var chip=e.target.closest('[data-cap]');

    if(!chip) return;

    var cap=chip.dataset.cap;

    document.querySelectorAll('#capFilters .filter-chip').forEach(function(c){c.classList.toggle('active',c===chip);});

    document.querySelectorAll('#capTable tbody tr').forEach(function(row){

      row.style.display=(cap==='all'||row.dataset.cap===cap)?'':'none';

    });

  });



  window.showView=showView; window.toast=showToast;

  window.openSubTaskDrawer=openSubTaskDrawer; window.openDispatchDrawer=openDispatchDrawer;

  window.openModal=openModal; window.closeAllDrawers=closeAllDrawers; window.closeAllModals=closeAllModals;

  window.runPreview=runPreview;

})();

</script>

</body>

</html>

"""





def build():

    html = (

        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'

        '  <meta charset="UTF-8" />\n'

        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'

        '  <title>扫描治理中心 · 全功能原型 v2（VTC-GOV PRD）</title>\n'

        + css_block()

        + "\n</head>\n<body>\n<div class=\"app-shell\">\n"

        + SIDEBAR

        + '  <div class="main-area">\n'

        + TOPBAR

        + '    <main class="content">\n'

        + BANNER

        + VIEWS

        + "    </main>\n  </div>\n</div>\n"

        + DRAWERS

        + SCRIPT

    )

    OUT.write_text(html, encoding="utf-8")

    text = OUT.read_text(encoding="utf-8")

    assert "扫描治理中心" in text

    assert "view-story-s2" in text

    assert "view-queue-monitor" in text

    print("OK", OUT, len(text), "chars")





if __name__ == "__main__":

    build()

