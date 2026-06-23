### 4.3 能力代码映射（Scanner Capability Profile）

能力注册表以 **vendor_code + capability_code** 唯一标识；各厂商 API 路径不同，但对上层暴露统一 capability 语义。
P0 种子数据：**LM**；P1 扩展：**AH**（安恒明鉴 DAS-RAS V5.0）。

#### 4.3.1 绿盟 RSAS V6.0.8（vendor_code=LM）

| capability_code | RSAS API | 平台 syn_type（现有） | 阶段 |
|-----------------|----------|----------------------|------|
| task.create | POST /api/task/create | taskCreate | P0 |
| task.status | GET /api/task/status/{id} | — | P0 |
| task.active_list | GET /api/task/active_list | active_list | P0 |
| task.list | GET /api/task/list | — | P1 |
| task.pause | POST /api/task/pause/{id} | task_pause | P0 |
| task.resume | POST /api/task/resume/{id} | task_resume | P0 |
| task.stop | POST /api/task/stop/{id} | — | P1 |
| task.delete | POST /api/task/delete/{id} | task_delete | P1 |
| system.status | GET /api/system/status | sys_status | P0 |
| template.sysvuln.list | GET /api/template/sysvuln/list | syn_sysvuln_data | P2 |
| template.baseline.list | GET /api/template/baseline/list | syn_baseline_data | P2 |
| userpwd.list | GET /api/userpwd/list | syn_pwd_data | P2 |
| report.task | GET /api/report/task/{id} | — | P2 |
| auth.login_verify | POST /api/auth/login_verify | — | P2 |

参考：svmp/docs/standards/_extracted/lm-api-v608.txt

#### 4.3.2 安恒明鉴 DAS-RAS V5.0（vendor_code=AH）

**协议**：HTTPS · Base {ip}:{port}/api/normal/* · UTF-8  
**认证**：GET /api/normal/token?userName=&userCode=（userCode=密码 MD5，见 MsgSendAH.queryToken）  
**模块 module**（附录1；下发/对账必带）：

| module | 扫描类型 | 平台 taskType（MsgSendAH） |
|--------|----------|---------------------------|
| 0 | 网站 webscan | web |
| 1 | 数据库 dbscan | — |
| 5 | 基线 baseline | base_line_scan |
| 8 | 主机 hostscan | vuln / weak_password_scan |

| capability_code | DAS-RAS API | 说明 | 阶段 |
|-----------------|-------------|------|------|
| auth.token | GET /api/normal/token | Token 认证 | P1 |
| engine.list | GET /api/normal/getEngines | 引擎列表 | P1 |
| engine.list.v5 | GET /api/normal/getEngines/v5 | V5 引擎 state 600–603 | P1 |
| task.create | POST /api/normal/task/create | 创建，返回 taskId | P1 |
| task.create.from_asset | POST /api/normal/task/createFromExistAsset | 从资产创建 | P2 |
| task.start | POST /api/normal/task/start | **创建后需 start 才执行** | P1 |
| task.suspend | POST /api/normal/task/suspend | 暂停 | P1 |
| task.resume | POST /api/normal/task/start | 暂停后恢复（手册无独立 resume，与 start 联调确认） | P1 |
| task.stop | POST /api/normal/task/stop | 停止 | P1 |
| task.delete | POST /api/normal/task/delete | 删除 | P1 |
| task.progress | POST /api/normal/task/progress | 进度 0–100 | P1 |
| task.status | GET /api/normal/task/getTaskStatus | state + progress | P1 |
| task.list | GET /api/normal/task/list | 任务列表 | P1 |
| task.list.v2 | GET /api/normal/task/list/V2 | 按 state/时间筛选（**对账源** ） | P1 |
| task.result | GET /api/normal/task/result | 扫描结果 | P2 |
| policy.get | GET /api/normal/policy/get | 策略 | P2 |
| policy.templates | GET /api/normal/policy/getPolicyTemplates | 策略模板 | P2 |
| system.version | GET /api/normal/system/version | 版本 | P1 |
| system.resource | GET /api/normal/system/resouceuasge | CPU/内存 metrics | P1 |
| dict.list | GET /api/normal/dict/list | 弱口令字典 | P2 |
| asset.check_connection | POST /api/normal/asset/checkConnection | 连通性预检 | P2 |
| report.generate | GET /api/normal/task/doReport | 报表 | P3 |

**明鉴 state（附录2）→ 平台 scan_sub_task.state：**

| AH state | 含义 | 平台 |
|----------|------|------|
| 1 | 等待调度 | 0 |
| 2 | 正在扫描 | 1 |
| 3 | 暂停 | 4 |
| 4 | 停止 | 3 |
| 5 | 结束 | 2 |
| 6 | 异常 | 3 |

**AH 对账**：活跃任务源 `GET /api/normal/task/list/V2`（state∈{1,2,3}）+ getTaskStatus；ORPHAN/MISSING/DRIFT 规则同 4.5。

**现有代码**：MsgSendAH（module 0/5/8、SOAR/tools-scheduler）、VulnTaskListenerAH（vulId 增量同步）。  
P1 目标：AhScannerAdapter 封装 create→start 两阶段 + reconcile。

参考：svmp/docs/standards/扫描器/明鉴漏洞扫描系统API手册V5.0-20230801.docx  
提取：svmp/docs/standards/_extracted/ah-api-v5.txt

#### 4.3.3 跨厂商 capability 对齐

| 统一 capability | LM | AH |
|-------------------|----|----|
| 对账活跃任务 | task.active_list | task.list.v2 |
| 单任务状态 | task.status | task.getTaskStatus |
| 系统负载 | system.status | system.resource |
| 任务创建 | 一步 create | create + start |
| 模板/策略 | template.*.list | policy.get / getPolicyTemplates |
| 凭据预检 | auth.login_verify | asset.checkConnection |
