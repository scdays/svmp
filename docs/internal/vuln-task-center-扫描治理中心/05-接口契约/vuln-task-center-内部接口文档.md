# vuln-task-center 内部接口文档

> **版本**：对齐 vuln-task-center `3.6.9` · **日期**：2026-07-27 · **状态**：草稿
> **说明**：参照 `svmp/docs/external/网络安全漏洞管理平台 · API 接口文档.md` 体例编写。覆盖 `04-子PRD与规格/vuln-task-center提供的接口能力.md` 要求的全部 **15 接口 + 1 回调**。已具备的复用现状接口（标注映射），缺失的按实际设计。
> **路径策略**：本文定义**统一规整路径**（目标形态），各接口元信息表标注「现状路径」与「改造」类型（复用/规整/新增），服务端按此对齐逐步迁移。

---

## 5. REST API
<a id="5-rest-api"></a>

> 路径均相对于 vuln-task-center 服务根（默认 port **18087**）。
> 下文「-」表示该项无参数。
> 「改造」列：`复用`（现状路径直接可用，仅规整命名）/ `规整`（基于现状重构路径）/ `新增`（现状缺失，需实现）。

### 5.0 接口一览
<a id="50-接口一览"></a>

| 阶段 | 方法   | 路径                                                  | 说明                     | 改造 |
| ---- | ------ | ----------------------------------------------------- | ------------------------ | ---- |
| 创建 | POST   | `/v1/scan/tasks`                                      | 创建任务（自动调度）     | 复用 |
| 创建 | POST   | `/v1/scan/tasks/draft`                                | 任务下发（仅记录）       | 复用 |
| 创建 | POST   | `/v1/scan/tasks/{taskId}/execute`                     | 任务执行（确认下发）     | 复用 |
| 查询 | GET    | `/v1/scan/tasks/{taskId}`                             | 主任务详情               | 规整 |
| 查询 | GET    | `/v1/scan/tasks/{taskId}/sub-tasks`                   | 子任务列表（分页）       | 规整 |
| 查询 | GET    | `/v1/scan/sub-tasks/{subTaskId}`                      | 子任务详情               | 规整 |
| 查询 | GET    | `/v1/scan/scanners/{scannerId}/tasks`                 | 扫描器任务列表（跨任务） | 新增 |
| 查询 | GET    | `/v1/scan/surveys/{surveyId}/vuln-results`            | 查询漏洞扫描结果（分页） | 规整 |
| 查询 | GET    | `/v1/scan/surveys/{surveyId}/success-ips`             | 查询扫描成功 IP          | 规整 |
| 查询 | GET    | `/v1/scan/surveys/{surveyId}/fail-ips`                | 查询扫描失败 IP          | 规整 |
| 查询 | GET    | `/v1/scan/surveys/{surveyId}/port-details`            | 查询资产端口详情         | 规整 |
| 操控 | POST   | `/v1/scan/tasks/{taskId}/pause`                       | 主任务暂停               | 规整 |
| 操控 | POST   | `/v1/scan/tasks/{taskId}/resume`                      | 主任务启动               | 规整 |
| 操控 | DELETE | `/v1/scan/tasks/{taskId}`                             | 主任务删除（级联子任务） | 规整 |
| 操控 | POST   | `/v1/scan/sub-tasks/{subTaskId}/pause`                | 子任务暂停               | 新增 |
| 操控 | POST   | `/v1/scan/sub-tasks/{subTaskId}/resume`               | 子任务启动               | 新增 |
| 操控 | DELETE | `/v1/scan/sub-tasks/{subTaskId}`                      | 子任务删除               | 规整 |
| 报告 | POST   | `/v1/scan/tasks/{surveyId}/reports/generate`          | 主任务生成报告（全量）   | 规整 |
| 报告 | POST   | `/v1/scan/sub-tasks/{subTaskId}/reports/generate`     | 子任务生成报告           | 规整 |
| 报告 | GET    | `/v1/scan/tasks/{surveyId}/reports/progress`          | 主任务报告进度查询       | 规整 |
| 报告 | GET    | `/v1/scan/sub-tasks/{subTaskId}/reports/progress`     | 子任务报告进度查询       | 新增 |

**任务层级**：`scan_task`（主任务）-> `scan_task_survey`（执行实例，每次调度触发一条）-> `scan_sub_task`（子任务，按扫描节点拆分）。

**回调通知**：子任务列表就绪、子任务状态变更、报告生成结束通过 Kafka 事件主动推送，见 [§6 事件回调](#6-事件回调kafka)。

### 5.0.1 文档体例
<a id="501-文档体例"></a>

各接口按下列块描述：**路径参数** · **查询参数** · **请求头** · **请求体** · **响应 data** · **状态约束** · **示例**。

#### 表格列名约定
<a id="表格列名约定"></a>

| 场景          | 表头                              | 适用章节                        |
| ------------- | --------------------------------- | ------------------------------- |
| 接口元信息    | `项` · `值`                       | 各接口开头（含现状路径/改造）   |
| REST 参数字段 | `参数` · `类型` · `必填` · `说明` | §5 请求体/响应体/查询参数       |
| 简化结构      | `字段` · `类型` · `说明`          | 嵌套对象、状态枚举              |

**必填列取值**：`✓` 必填 · `○` 可选 · `条件` 条件必填。

**统一响应包装**：

| 字段 | 类型   | 说明                                  |
| ---- | ------ | ------------------------------------- |
| code | int    | `200` 成功；非 `200` 失败             |
| msg  | string | 结果描述                              |
| data | object | 业务数据；失败时为 `null`             |

> 文件下载类接口直接返回二进制流（`Content-Type` 由接口指定），不包装。

**通用请求头**：

| 参数         | 类型   | 必填 | 说明                                                        |
| ------------ | ------ | :--: | ----------------------------------------------------------- |
| Content-Type | string |  ✓   | `application/json`（POST/DELETE 带 body）                   |
| _username    | string |  ○   | 调用方标识；服务端按其部门/科室/专业匹配可用扫描器          |

**重要约定**：

| 项           | 约定                                                                                       |
| ------------ | ------------------------------------------------------------------------------------------ |
| 任务键       | 创建返回主任务 `taskId`；操控主任务用 `taskId`，实例用 `surveyId`，子任务用 `subTaskId`   |
| 创建异步     | `POST /tasks` 同步返回 `taskId`；子任务由 mint 调度触发后创建，经 [§6.1.1 SUBTASK_LIST_READY](#611-subtask_list_ready子任务列表回调) 回调或轮询 [§5.2.2](#522-get-v1scantaskstaskidsub-tasks-子任务列表分页) 获取 |
| 三种创建模式 | `POST /tasks`（自动调度）/ `POST /tasks/draft`（仅记录）/ `POST /tasks/{taskId}/execute`（确认下发） |
| 回调地址     | `appHost` / `path` 由服务端覆盖写入，客户端勿传                                            |
| 四类客户端   | 创建接口通过 `clientType` 标识来源，影响扫描器分配策略，见 [§5.1.1](#511-post-v1scantasks-创建任务自动调度) |

**任务状态枚举**：

| 字段            | 所属     | 值 -> 含义                                                       |
| --------------- | -------- | ---------------------------------------------------------------- |
| `taskState`     | 主任务   | `0`未开始 / `1`启动 / `2`暂停 / `3`完成                          |
| `state`(survey) | 执行实例 | `0`未开始 / `1`执行中 / `2`已完成 / `3`失败 / `4`暂停 / `5`重启  |
| `state`(subTask)| 子任务   | `0`未开始 / `1`执行中 / `2`已完成 / `3`失败 / `4`暂停            |
| `state`(report) | 报告     | `0`未开始 / `1`生成中 / `2`已完成 / `3`失败 / `4`可下载          |

> 📌 现状报告状态为 `0/1/2下载中/3已完成/4上传完成/5异常`（仅 LM），本文规整为通用 5 态；WP2 将统一枚举包装兼容。

**任务类型 `taskType`**：`vuln_scan` / `weak_password_scan` / `base_line_scan` / `port_scan` / `asset_find_scan`（服务端兼容短名）。

**厂商 `classifyId`**：`1`=LM / `2`=AH / `3`=QM / `4`=TRX / `7`=Nessus / `8`=AZ / `9`=JTL。

**四类客户端 `clientType`**：

| 值              | 客户端         | 默认扫描器分配策略                         |
| --------------- | -------------- | ------------------------------------------ |
| `SCAN_MANAGE`   | 扫描任务管理   | 负载均衡（`AUTO_BALANCE`）                 |
| `OPS_METRIC`    | 运营指标任务   | 负载均衡；复扫可指定节点                   |
| `DEPT_WORKORDER`| 部侧专项工单   | 指定扫描器 hash / 节点 ID（`SPECIFY_NODE`）|
| `OPEN_PLATFORM` | 开放平台       | 指定厂商（`SPECIFY_VENDOR`）+ 负载均衡     |

### 5.0.2 状态码码表
<a id="502-状态码码表"></a>

除文件下载外，接口在 HTTP 200 时用业务码 `code` 区分成败：`200` 成功，非 `200` 失败。失败时 `data` 为 `null`，`msg` 描述原因。**级联操作**（主任务暂停/启动/删除）部分子任务失败时，主接口仍返回 `code=200`，各子任务结果在 `data.subTaskResults[]` 的 `success` 与 `code` 中体现。

| code  | 名称           | 说明                       | 典型场景                       |
| ----- | -------------- | -------------------------- | ------------------------------ |
| 200   | 成功           | 请求处理成功               | -                              |
| 40001 | 参数错误       | 请求参数缺失/非法          | 必填字段缺失、格式错误        |
| 40002 | 状态不允许     | 当前状态不允许该操作       | 已完成暂停、失败恢复          |
| 40003 | 资源不存在     | taskId/subTaskId 不存在    | 查询/操控不存在任务            |
| 40004 | 任务类型非法   | taskType 不支持            | execute 接口非 vuln            |
| 40005 | 扫描器不可达   | 节点离线/认证失败          | 操控/下发时扫描器不可用        |
| 40006 | 无可用扫描器   | 负载均衡无可用节点         | 全部节点满载/不可用            |
| 40007 | 报告生成失败   | 报告生成异常               | 扫描器报告接口异常             |
| 40008 | 重复提交       | 幂等冲突                   | 重复创建                       |
| 40009 | 权限不足       | 无权操作该任务             | 跨用户操作                     |
| 50000 | 服务异常       | 服务端内部错误             | 未捕获异常                     |
| 50001 | 调度服务异常   | mint 调度服务不可用        | mint 不可达                    |
| 50002 | 下发失败       | 扫描器下发失败             | mint.add 失败                  |

---

### 5.1 任务创建
<a id="51-任务创建"></a>

#### 5.1.1 `POST /v1/scan/tasks` - 创建任务（自动调度）
<a id="511-post-v1scantasks-创建任务自动调度"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 创建主任务并立即注册到 mint 调度，到点自动下发扫描器。适用于扫描任务管理、开放平台（指定厂商）    |
| 现状路径 | `POST /v1/scan/task/add`                                                                          |
| 改造     | 复用（路径规整）                                                                                   |

**路径参数**：- · **查询参数**：-

**请求体**（`ScanTaskDTO`，关键字段）：

| 参数         | 类型     | 必填 | 说明                                                                 |
| ------------ | -------- | :--: | -------------------------------------------------------------------- |
| clientType   | string   |  ✓   | 客户端类型，见 [5.0.1](#四类客户端-clienttype)；决定分配策略         |
| taskName     | string   |  ✓   | 计划名称                                                             |
| taskType     | string   |  ✓   | 计划类型，见 [5.0.1](#任务类型-tasktype)                             |
| classifyId   | string   |  ✓   | 厂商 ID；`OPEN_PLATFORM` 必填（指定厂商）                            |
| inputIp      | string   | 条件 | 手动输入 IP（逗号分隔）；与 `selectIp` / `fileIp` 三选一             |
| selectIp     | string   | 条件 | 选择资产 IP（逗号分隔）                                              |
| fileIp       | string   | 条件 | 上传文件 IP                                                          |
| scannerId    | string   |  ○   | 指定扫描器；`DEPT_WORKORDER` 可传节点 ID（服务端 fallback）         |
| nodeHash     | string   |  ○   | 扫描器安全资源 hash；`DEPT_WORKORDER` 指定设备（**新增字段**）      |
| sceneId      | string   |  ○   | 场景 ID（影响分配）                                                  |
| executeType  | string   |  ✓   | `1`=定期 `2`=周期；空默认 `1`                                        |
| executeCron  | string   | 条件 | 周期 cron；`executeType=2` 时必填                                    |
| startTime    | datetime |  ✓   | 计划开始时间                                                         |
| endTime      | datetime |  ✓   | 计划结束时间                                                         |
| createUser   | string   |  ✓   | 责任人                                                               |
| flag         | string   |  ○   | 标识：`1`修复核验 `2`暴露面 `5`漏洞验证 `7`指标任务                  |
| scanPort     | string   |  ○   | 端口策略（LM）：`standard`/`fast`/`user`/`allports`                  |
| templateId   | string   |  ○   | 漏洞模板（`0`=自动匹配）/ 弱口令字典 ID                              |

> 完整 LM 专属字段（tcpScanMode/udpScan/scanDepth 等）见 `ScanTaskDTO.java`。`appHost`/`path` 由服务端覆盖，勿传。

**响应 data**：

| 参数      | 类型     | 必填 | 说明                                   |
| --------- | -------- | :--: | -------------------------------------- |
| taskId    | string   |  ✓   | 主任务 ID（后续查询/操控均用此字段）   |
| taskState | string   |  ✓   | 主任务状态，创建后为 `0`未开始         |
| sTime     | datetime |  ✓   | 开始时间                               |
| eTime     | datetime |  ○   | 结束时间                               |
| taskType  | string   |  ✓   | 任务类型（回显）                       |

**状态约束**：`taskType` 非法 -> 失败；`mintClient.add` 下发失败 -> 回滚删除已建计划；子任务非同步创建，需等 [§6.1.1](#611-subtask_list_ready子任务列表回调) 回调或轮询 [§5.2.2](#522-get-v1scantaskstaskidsub-tasks-子任务列表分页)。

**请求示例**

```http
POST /v1/scan/tasks HTTP/1.1
Content-Type: application/json
_username: zhangsan

{
  "clientType": "SCAN_MANAGE",
  "taskName": "每日漏洞扫描",
  "taskType": "vuln_scan",
  "classifyId": "1",
  "inputIp": "10.0.0.1,10.0.0.2",
  "executeType": "1",
  "startTime": "2026-07-27 00:00:00",
  "endTime": "2026-07-28 00:00:00",
  "createUser": "zhangsan",
  "scanPort": "standard"
}
```

**响应示例（成功）**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "123456",
    "taskState": "0",
    "sTime": "2026-07-27 00:00:00",
    "eTime": "2026-07-28 00:00:00",
    "taskType": "vuln_scan"
  }
}
```

---

#### 5.1.2 `POST /v1/scan/tasks/draft` - 任务下发（仅记录）
<a id="512-post-v1scantaslksdraft-任务下发仅记录"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 仅创建主任务记录，**不下发调度**。用于运营指标任务「管理员分发」阶段（`clientType=OPS_METRIC`）   |
| 现状路径 | `POST /v1/scan/task/add/first/half`（批量 `/batch/add/first/half`，Excel `/batch/add/first/half/excel`） |
| 改造     | 复用（路径规整）                                                                                   |

**请求体**（仅需以下字段，其余服务端强制覆盖）：

| 参数       | 类型   | 必填 | 说明                       |
| ---------- | ------ | :--: | -------------------------- |
| clientType | string |  ✓   | 固定 `OPS_METRIC`          |
| taskName   | string |  ✓   | 计划名称                   |
| createUser | string |  ✓   | 责任人                     |
| remarks    | string |  ✓   | 备注                       |

> 服务端强制：`taskType=vuln`、`taskState=0`、`executeType=1`、`builtInTask=0`、`flag=7`，**不调 mint**。

**响应 data**：

| 参数      | 类型   | 必填 | 说明                            |
| --------- | ------ | :--: | ------------------------------- |
| taskId    | string |  ✓   | 草稿记录 ID（**执行接口必传**） |
| taskState | string |  ✓   | `0`未开始                       |

**状态约束**：本接口不触发扫描器下发；需后续调用 [§5.1.3](#513-post-v1scantaskstaskidexecute-任务执行确认下发) 补全参数并下发。

**请求示例**

```http
POST /v1/scan/tasks/draft HTTP/1.1
Content-Type: application/json

{
  "clientType": "OPS_METRIC",
  "taskName": "2026Q2-运营指标扫描",
  "createUser": "admin",
  "remarks": "指标任务-待确认"
}
```

---

#### 5.1.3 `POST /v1/scan/tasks/{taskId}/execute` - 任务执行（确认下发）
<a id="513-post-v1scantaskstaskidexecute-任务执行确认下发"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 对草稿记录补全扫描参数并下发。用于运营指标任务「安全员确认执行」阶段。仅限 `vuln` 计划。服务端先删草稿再重建并下发 |
| 现状路径 | `POST /v1/scan/task/add/second/half`                                                              |
| 改造     | 复用（路径规整）                                                                                   |

**路径参数**：

| 参数   | 类型   | 必填 | 说明            |
| ------ | ------ | :--: | --------------- |
| taskId | string |  ✓   | 草稿记录 ID     |

**请求体**（完整扫描参数）：

| 参数        | 类型     | 必填 | 说明                                                          |
| ----------- | -------- | :--: | ------------------------------------------------------------- |
| clientType  | string   |  ✓   | 固定 `OPS_METRIC`                                             |
| inputIp     | string   |  ✓   | 扫描目标 IP（逗号分隔）                                       |
| classifyId  | string   |  ✓   | 厂商 ID                                                       |
| startTime   | datetime |  ✓   | 开始时间                                                      |
| endTime     | datetime |  ○   | 结束时间                                                      |
| createUser  | string   |  ✓   | 责任人                                                        |
| 其他扫描参数 | -        |  ○   | 同 [§5.1.1](#511-post-v1scantasks-创建任务自动调度)           |

> 服务端强制 `flag=7`；`taskType` 限 `vuln`。

**响应 data**：

| 参数      | 类型   | 必填 | 说明                                   |
| --------- | ------ | :--: | -------------------------------------- |
| taskId    | string |  ✓   | 重建后的主任务 ID（可能与草稿不同）    |
| taskState | string |  ✓   | `0`未开始（待 mint 调度触发）          |

**状态约束**：实现为「删除重建」，客户端应在成功后再依赖返回的 `taskId`；`taskType` 非 `vuln` -> 失败。

**请求示例**

```http
POST /v1/scan/tasks/123450/execute HTTP/1.1
Content-Type: application/json

{
  "clientType": "OPS_METRIC",
  "inputIp": "10.0.0.1,10.0.0.2",
  "classifyId": "1",
  "startTime": "2026-07-27 00:00:00",
  "endTime": "2026-07-28 00:00:00",
  "createUser": "zhangsan"
}
```

---

### 5.2 任务查询
<a id="52-任务查询"></a>

#### 5.2.1 `GET /v1/scan/tasks/{taskId}` - 主任务详情
<a id="521-get-v1scantaskstaskid-主任务详情"></a>

| 项       | 值                                          |
| -------- | ------------------------------------------- |
| 说明     | 按主任务 ID 查询基础信息                    |
| 现状路径 | `GET /v1/scan/task/vulnScan/basicInfo/{taskId}` |
| 改造     | 规整（统一返回 `Result` 包装）              |

**路径参数**：

| 参数   | 类型   | 必填 | 说明      |
| ------ | ------ | :--: | --------- |
| taskId | string |  ✓   | 主任务 ID |

**响应 data**（主任务信息 + 历史执行实例列表）：

| 参数       | 类型     | 必填 | 说明                                  |
| ---------- | -------- | :--: | ------------------------------------- |
| taskId     | string   |  ✓   | 主任务 ID                             |
| taskName   | string   |  ✓   | 计划名称                              |
| taskType   | string   |  ✓   | 计划类型                              |
| taskState  | string   |  ✓   | 主任务状态，见 [5.0.1](#任务状态枚举) |
| scanIp     | string   |  ○   | 扫描 IP                               |
| createUser | string   |  ✓   | 责任人                                |
| sTime      | datetime |  ○   | 开始时间                              |
| eTime      | datetime |  ○   | 结束时间                              |
| surveyList | array    |  ✓   | 历史任务执行实例列表，见下表          |

**`surveyList[]` 元素**（`ScanTaskSurveyDTO`）：

| 参数           | 类型     | 必填 | 说明                                       |
| -------------- | -------- | :--: | ------------------------------------------ |
| id             | string   |  ✓   | 执行实例 ID（surveyId）                    |
| taskId         | string   |  ✓   | 主任务 ID                                  |
| state          | string   |  ✓   | 实例状态，见 [5.0.1](#任务状态枚举)        |
| executeTime    | datetime |  ○   | 本次执行时间                               |
| endTime        | datetime |  ○   | 本次结束时间                               |
| scanIpTotal    | string   |  ○   | 扫描 IP 总数                               |
| scanIpCount    | string   |  ○   | 已扫描 IP 数                               |
| process        | string   |  ○   | 执行进度                                   |
| downloadReport | string   |  ○   | 报告状态：`0`未点击/`1`已点击/成功后为路径 |

**请求示例**

```http
GET /v1/scan/tasks/123456 HTTP/1.1
```

**响应示例（成功）**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "123456",
    "taskName": "每日漏洞扫描",
    "taskType": "vuln_scan",
    "taskState": "1",
    "scanIp": "10.0.0.1,10.0.0.2",
    "createUser": "zhangsan",
    "sTime": "2026-07-27 00:00:00",
    "eTime": "2026-07-28 00:00:00"
  }
}
```

---

#### 5.2.2 `GET /v1/scan/tasks/{taskId}/sub-tasks` - 子任务列表（分页）
<a id="522-get-v1scantaskstaskidsub-tasks-子任务列表分页"></a>

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 说明     | 按主任务查询子任务列表。子任务列表回调（[§6.1.1](#611-subtask_list_ready子任务列表回调)）未送达时用本接口轮询 |
| 现状路径 | `GET /v1/scan/sub/task/page`（按 taskId 过滤）              |
| 改造     | 规整                                                         |

**路径参数**：

| 参数   | 类型   | 必填 | 说明      |
| ------ | ------ | :--: | --------- |
| taskId | string |  ✓   | 主任务 ID |

**查询参数**：

| 参数     | 类型   | 必填 | 说明           |
| -------- | ------ | :--: | -------------- |
| pageNum  | int    |  ✓   | 页码           |
| pageSize | int    |  ✓   | 每页条数       |
| surveyId | string |  ○   | 执行实例 ID    |
| nodeId   | string |  ○   | 扫描节点 ID    |
| state    | string |  ○   | 子任务状态     |

**响应 data**：`PageInfo<ScanSubTaskDTO>`，`list` 元素见 [§5.2.3](#523-get-v1scansub-taskssubtaskid-子任务详情)。

---

#### 5.2.3 `GET /v1/scan/sub-tasks/{subTaskId}` - 子任务详情
<a id="523-get-v1scansub-taskssubtaskid-子任务详情"></a>

| 项       | 值                                          |
| -------- | ------------------------------------------- |
| 说明     | 按子任务 ID 查询                            |
| 现状路径 | `GET /v1/scan/sub/task/findById/{key}`      |
| 改造     | 规整                                        |

**路径参数**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| subTaskId | string |  ✓   | 子任务 ID  |

**响应 data**（`ScanSubTaskDTO`）：

| 参数        | 类型     | 必填 | 说明                                              |
| ----------- | -------- | :--: | ------------------------------------------------- |
| id          | string   |  ✓   | 子任务 ID                                         |
| taskId      | string   |  ✓   | 主任务 ID                                         |
| surveyId    | string   |  ✓   | 执行实例 ID                                       |
| nodeId      | string   |  ✓   | 扫描节点 ID                                       |
| scannerId   | string   |  ✓   | 扫描器 ID                                         |
| planId      | string   |  ✓   | 扫描器侧任务 ID                                   |
| ips         | string   |  ✓   | 扫描资产 IP                                       |
| progress    | string   |  ✓   | 进度                                              |
| state       | string   |  ✓   | 子任务状态，见 [5.0.1](#任务状态枚举)             |
| createTime  | datetime |  ✓   | 创建时间                                          |
| endTime     | datetime |  ○   | 结束时间                                          |
| discrption  | string   |  ○   | 描述（失败原因）                                  |

**请求示例**

```http
GET /v1/scan/sub-tasks/654321 HTTP/1.1
```

**响应示例（成功）**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": "654321",
    "taskId": "123456",
    "surveyId": "100001",
    "nodeId": "10",
    "scannerId": "lm-scanner-01",
    "planId": "lm-plan-001",
    "ips": "10.0.0.1",
    "progress": "100",
    "state": "2",
    "createTime": "2026-07-27 08:00:00",
    "endTime": "2026-07-27 10:30:00"
  }
}
```

---

#### 5.2.4 `GET /v1/scan/scanners/{scannerId}/tasks` - 扫描器任务列表（跨任务）
<a id="524-get-v1scanscannersscanneridtasks-扫描器任务列表跨任务"></a>

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 说明     | 按扫描器（节点）维度查询其全部任务，跨主任务/实例。现状仅按 `surveyId+nodeId` 查，本接口为新增 |
| 现状路径 | 无（现状 `GET /v1/scan/task/vulnScan/scanNodeList/{surveyId}/{nodeId}` 仅按实例） |
| 改造     | 新增                                                         |

**路径参数**：

| 参数       | 类型   | 必填 | 说明                          |
| ---------- | ------ | :--: | ----------------------------- |
| scannerId  | string |  ✓   | 扫描器 ID（或节点 ID）        |

**查询参数**：

| 参数     | 类型   | 必填 | 说明                       |
| -------- | ------ | :--: | -------------------------- |
| pageNum  | int    |  ✓   | 页码                       |
| pageSize | int    |  ✓   | 每页条数                   |
| state    | string |  ○   | 子任务状态过滤             |
| fromTime | datetime | ○  | 开始时间起                 |
| toTime   | datetime | ○  | 开始时间止                 |

**响应 data**：`PageInfo<Map>`，元素字段：

| 参数        | 类型     | 必填 | 说明                       |
| ----------- | -------- | :--: | -------------------------- |
| subTaskId   | string   |  ✓   | 子任务 ID                  |
| taskId      | string   |  ✓   | 主任务 ID                  |
| taskName    | string   |  ✓   | 主任务名称                 |
| surveyId    | string   |  ✓   | 执行实例 ID                |
| planId      | string   |  ✓   | 扫描器侧任务 ID            |
| state       | string   |  ✓   | 子任务状态                 |
| progress    | string   |  ✓   | 进度                       |
| createTime  | datetime |  ✓   | 创建时间                   |
| endTime     | datetime |  ○   | 结束时间                   |

---

#### 5.2.5 `GET /v1/scan/surveys/{surveyId}/vuln-results` - 查询漏洞扫描结果
<a id="525-get-v1scansurveyssurveyidvuln-results-查询漏洞扫描结果"></a>

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 说明     | 按执行实例查询漏洞扫描结果（分页，每页 50 条），含漏洞库详情 |
| 现状路径 | `GET /event/scan/task/survey/query/vulnScanResult`           |
| 改造     | 规整                                                         |

**路径参数**：

| 参数     | 类型   | 必填 | 说明         |
| -------- | ------ | :--: | ------------ |
| surveyId | string |  ✓   | 执行实例 ID  |

**查询参数**：

| 参数    | 类型 | 必填 | 说明                         |
| ------- | ---- | :--: | ---------------------------- |
| current | int  |  ✓   | 页码，从 1 开始；每页 50 条  |

**响应 data**（`Map`）：

| 参数               | 类型  | 必填 | 说明                       |
| ------------------ | ----- | :--: | -------------------------- |
| total              | long  |  ✓   | 总记录数                   |
| currentPage        | long  |  ✓   | 当前页码                   |
| pageSize           | long  |  ✓   | 每页条数（固定 50）        |
| pages              | long  |  ✓   | 总页数                     |
| vulnScanResultList | array |  ✓   | 漏洞扫描结果列表，见下表   |
| vulnDatabaseList   | array |  ✓   | 漏洞库详情列表             |

**`vulnScanResultList[]` 元素**：

| 参数           | 类型   | 必填 | 说明                                  |
| -------------- | ------ | :--: | ------------------------------------- |
| taskId         | string |  ✓   | 主任务 ID                             |
| surveyId       | string |  ✓   | 执行实例 ID                           |
| nodeId         | string |  ✓   | 扫描节点 ID                           |
| scannerId      | string |  ✓   | 扫描器 ID                             |
| ip             | string |  ✓   | 资产 IP                               |
| port           | string |  ✓   | 端口                                  |
| protocol       | string |  ✓   | 协议                                  |
| service        | string |  ○   | 服务                                  |
| serviceVersion | string |  ○   | 服务版本                              |
| cve            | string |  ○   | CVE 编号                              |
| classify       | string |  ✓   | 厂商（LM/AH/QM 等）                   |
| planId         | string |  ✓   | 扫描器计划 ID                         |
| vulId          | string |  ✓   | 厂商漏洞 ID                           |
| vulnName       | string |  ✓   | 漏洞名称                              |
| level          | string |  ✓   | 漏洞等级 urgent/high/medium/low/info  |

---

#### 5.2.6 `GET /v1/scan/surveys/{surveyId}/success-ips` - 查询扫描成功 IP
<a id="526-get-v1scansurveyssurveyidsuccess-ips-查询扫描成功-ip"></a>

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 说明     | 查询执行实例下扫描成功的 IP 集合（已去重）。数据源 ES `vuln_scan_node_execute`，`state=finish` |
| 现状路径 | `GET /event/scan/task/survey/query/success/ips`              |
| 改造     | 规整                                                         |

**路径参数**：

| 参数     | 类型   | 必填 | 说明         |
| -------- | ------ | :--: | ------------ |
| surveyId | string |  ✓   | 执行实例 ID  |

**响应 data**：`string[]`，扫描成功 IP 集合（已去重）。

**响应示例（成功）**

```json
{
  "code": 200,
  "msg": "success",
  "data": ["1.1.1.1", "2.2.2.2", "172.16.4.195"]
}
```

---

#### 5.2.7 `GET /v1/scan/surveys/{surveyId}/fail-ips` - 查询扫描失败 IP
<a id="527-get-v1scansurveyssurveyidfail-ips-查询扫描失败-ip"></a>

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 说明     | 查询执行实例下扫描失败的 IP 集合（已去重）。数据源 ES `vuln_scan_node_execute`，`state=fail` |
| 现状路径 | `GET /event/scan/task/survey/query/fail/ips`                 |
| 改造     | 规整                                                         |

**路径参数**：

| 参数     | 类型   | 必填 | 说明         |
| -------- | ------ | :--: | ------------ |
| surveyId | string |  ✓   | 执行实例 ID  |

**响应 data**：`string[]`，扫描失败 IP 集合（已去重）。

---

#### 5.2.8 `GET /v1/scan/surveys/{surveyId}/port-details` - 查询资产端口详情
<a id="528-get-v1scansurveyssurveyidport-details-查询资产端口详情"></a>

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 说明     | 按执行实例查询资产端口扫描详情。适用于端口发现任务（`taskType=port`） |
| 现状路径 | `GET /event/scan/task/survey/query/ip/port`                  |
| 改造     | 规整                                                         |

**路径参数**：

| 参数     | 类型   | 必填 | 说明         |
| -------- | ------ | :--: | ------------ |
| surveyId | string |  ✓   | 执行实例 ID  |

**响应 data**：`array`，每条为单个资产的端口扫描结果。

**元素字段**：

| 参数          | 类型   | 必填 | 说明             |
| ------------- | ------ | :--: | ---------------- |
| taskId        | string |  ✓   | 主任务 ID        |
| surveyId      | string |  ✓   | 执行实例 ID      |
| nodeId        | string |  ✓   | 扫描节点 ID      |
| scannerId     | string |  ✓   | 扫描器 ID        |
| planId        | string |  ✓   | 扫描器计划 ID    |
| ip            | string |  ✓   | 资产 IP          |
| osName        | string |  ○   | 操作系统名称     |
| osVersion     | string |  ○   | 操作系统版本     |
| portInfoArray | array  |  ○   | 端口信息，见下表 |
| appInfoArray  | array  |  ○   | 软件信息，见下表 |

**`portInfoArray[]` 元素**：`port`/`banner`/`protocol`/`service`/`state`
**`appInfoArray[]` 元素**：`appName`/`appVersion`

---

### 5.3 任务操控
<a id="53-任务操控"></a>

#### 5.3.1 `POST /v1/scan/tasks/{taskId}/pause` - 主任务暂停
<a id="531-post-v1scantaskstaskidpause-主任务暂停"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 暂停主任务：停 mint 调度 + `taskState=2`。批量入口 `POST /v1/scan/tasks:batch-pause`             |
| 现状路径 | `GET /v1/scan/task/pause/{key}`（批量 `/batch/pause`；实例级 `/classify/pause/{taskId}/{surveyId}`） |
| 改造     | 规整（`GET`->`POST`，符合 RESTful 操控语义）                                                      |

**路径参数**：

| 参数   | 类型   | 必填 | 说明      |
| ------ | ------ | :--: | --------- |
| taskId | string |  ✓   | 主任务 ID |

**请求体**：

| 参数     | 类型   | 必填 | 说明             |
| -------- | ------ | :--: | ---------------- |
| operator | string |  ○   | 操作人           |
| reason   | string |  ○   | 暂停原因         |

**响应 data**：

| 参数           | 类型     | 必填 | 说明                                                |
| -------------- | -------- | :--: | --------------------------------------------------- |
| taskId         | string   |  ✓   | 主任务 ID                                           |
| taskState      | string   |  ✓   | `2`暂停                                             |
| operator       | string   |  ○   | 操作人                                              |
| operateTime    | datetime |  ✓   | 操作时间                                            |
| message        | string   |  ✓   | 整体消息（成功/失败内容）                           |
| subTaskResults | array    |  ✓   | 级联子任务/扫描器操作结果，见下表                   |

**`subTaskResults[]` 元素**：

| 参数      | 类型   | 必填 | 说明                                      |
| --------- | ------ | :--: | ----------------------------------------- |
| subTaskId | string |  ✓   | 子任务 ID                                 |
| nodeId    | string |  ✓   | 扫描节点 ID                               |
| scannerId | string |  ✓   | 扫描器 ID                                 |
| operate   | string |  ✓   | 操作：`pause`                             |
| success   | bool   |  ✓   | 该子任务操作是否成功                      |
| code      | string |  ○   | 失败时状态码，见 [5.0.2](#502-状态码码表) |
| message   | string |  ✓   | 该子任务消息（成功/失败内容）             |

**状态约束**：级联到扫描器下发 `task_pause`。计划级暂停现状无前置状态校验（🔵 规划补校验）；实例级 `classifyPause` 校验 `survey.state=1`。已 `FINISHED`/`FAILED` -> **40002**。部分子任务失败时主接口仍 `200`，详见 `subTaskResults`。

**响应示例（成功，部分子任务失败）**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "123456",
    "taskState": "2",
    "operator": "zhangsan",
    "operateTime": "2026-07-27 09:00:00",
    "message": "主任务已暂停，2个子任务成功，1个失败",
    "subTaskResults": [
      { "subTaskId": "654321", "nodeId": "10", "scannerId": "lm-01", "operate": "pause", "success": true, "message": "扫描器暂停指令已下发" },
      { "subTaskId": "654322", "nodeId": "11", "scannerId": "lm-02", "operate": "pause", "success": true, "message": "扫描器暂停指令已下发" },
      { "subTaskId": "654323", "nodeId": "12", "scannerId": "lm-03", "operate": "pause", "success": false, "code": "40005", "message": "扫描器不可达" }
    ]
  }
}
```

**请求示例**

```http
POST /v1/scan/tasks/123456/pause HTTP/1.1
Content-Type: application/json

{ "operator": "zhangsan", "reason": "业务侧要求临时暂停" }
```

---

#### 5.3.2 `POST /v1/scan/tasks/{taskId}/resume` - 主任务启动
<a id="532-post-v1scantaskstaskidresume-主任务启动"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 启动主任务：恢复 mint 调度 + `taskState=1`。批量入口 `POST /v1/scan/tasks:batch-resume`          |
| 现状路径 | `GET /v1/scan/task/resume/{key}`                                                                  |
| 改造     | 规整                                                                                              |

**路径参数**：

| 参数   | 类型   | 必填 | 说明      |
| ------ | ------ | :--: | --------- |
| taskId | string |  ✓   | 主任务 ID |

**请求体**：

| 参数     | 类型   | 必填 | 说明     |
| -------- | ------ | :--: | -------- |
| operator | string |  ○   | 操作人   |

**响应 data**：

| 参数           | 类型     | 必填 | 说明                                                |
| -------------- | -------- | :--: | --------------------------------------------------- |
| taskId         | string   |  ✓   | 主任务 ID                                           |
| taskState      | string   |  ✓   | `1`启动                                             |
| operator       | string   |  ○   | 操作人                                              |
| operateTime    | datetime |  ✓   | 操作时间                                            |
| message        | string   |  ✓   | 整体消息（成功/失败内容）                           |
| subTaskResults | array    |  ✓   | 级联子任务/扫描器操作结果，结构同 [§5.3.1](#531-post-v1scantaskstaskidpause-主任务暂停) |

**`subTaskResults[]` 元素**：`operate` 为 `resume`，其余字段同 [§5.3.1](#531-post-v1scantaskstaskidpause-主任务暂停)。

**状态约束**：级联到扫描器下发 `task_resume`。实例级 `classifyResume` 校验 `survey.state=4`；非暂停态 -> **40002**。部分子任务失败时主接口仍 `200`，详见 `subTaskResults`。

---

#### 5.3.3 `DELETE /v1/scan/tasks/{taskId}` - 主任务删除
<a id="533-delete-v1scantaskstaskid-主任务删除"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 删除主任务：删 mint 调度 + 级联删除全部子任务（含 ES/队列）。批量入口 `POST /v1/scan/tasks:batch-delete` |
| 现状路径 | `POST /v1/scan/task/delete`（body `ids[]`）                                                       |
| 改造     | 规整                                                                                              |

**路径参数**：

| 参数   | 类型   | 必填 | 说明      |
| ------ | ------ | :--: | --------- |
| taskId | string |  ✓   | 主任务 ID |

**请求体**：

| 参数      | 类型   | 必填 | 说明   |
| --------- | ------ | :--: | ------ |
| _username | string |  ✓   | 操作人 |

**响应 data**：

| 参数           | 类型     | 必填 | 说明                                                |
| -------------- | -------- | :--: | --------------------------------------------------- |
| taskId         | string   |  ✓   | 主任务 ID                                           |
| operator       | string   |  ○   | 操作人                                              |
| operateTime    | datetime |  ✓   | 操作时间                                            |
| message        | string   |  ✓   | 整体消息（成功/失败内容）                           |
| subTaskResults | array    |  ✓   | 级联子任务/扫描器操作结果，结构同 [§5.3.1](#531-post-v1scantaskstaskidpause-主任务暂停) |

**`subTaskResults[]` 元素**：`operate` 为 `delete`（删除扫描器侧任务 + ES/队列），其余字段同 [§5.3.1](#531-post-v1scantaskstaskidpause-主任务暂停)。

**状态约束**：级联删除 mint 调度 + 全部子任务（含 ES/队列信息）+ 扫描器侧任务。任务不存在 -> **40003**。部分子任务扫描器侧删除失败时主接口仍 `200`，详见 `subTaskResults`。

**请求示例**

```http
DELETE /v1/scan/tasks/123456 HTTP/1.1
Content-Type: application/json

{ "_username": "zhangsan" }
```

---

#### 5.3.4 `POST /v1/scan/sub-tasks/{subTaskId}/pause` - 子任务暂停
<a id="534-post-v1scansub-taskssubtaskidpause-子任务暂停"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 暂停单个子任务。现状仅支持实例级 `classifyPause`（按 `surveyId` 批量），本接口下沉到单子任务粒度 |
| 现状路径 | 无                                                                                                |
| 改造     | 新增                                                                                              |

**路径参数**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| subTaskId | string |  ✓   | 子任务 ID  |

**请求体**：

| 参数     | 类型   | 必填 | 说明   |
| -------- | ------ | :--: | ------ |
| operator | string |  ○   | 操作人 |

**响应 data**：

| 参数          | 类型     | 必填 | 说明                                                |
| ------------- | -------- | :--: | --------------------------------------------------- |
| subTaskId     | string   |  ✓   | 子任务 ID                                           |
| state         | string   |  ✓   | `4`暂停                                             |
| operator      | string   |  ○   | 操作人                                              |
| operateTime   | datetime |  ✓   | 操作时间                                            |
| message       | string   |  ✓   | 整体消息（成功/失败内容）                           |
| scannerResult | object   |  ✓   | 扫描器侧操作结果，见下表                            |

**`scannerResult` 对象**：

| 参数      | 类型   | 必填 | 说明                                      |
| --------- | ------ | :--: | ----------------------------------------- |
| nodeId    | string |  ✓   | 扫描节点 ID                               |
| scannerId | string |  ✓   | 扫描器 ID                                 |
| operate   | string |  ✓   | 操作：`pause`                             |
| success   | bool   |  ✓   | 扫描器侧操作是否成功                      |
| code      | string |  ○   | 失败时状态码，见 [5.0.2](#502-状态码码表) |
| message   | string |  ✓   | 扫描器侧消息（成功/失败内容）             |

**状态约束**：级联到扫描器下发 `task_pause`。仅 `state=1`（执行中）可暂停；已 `2`/`3` -> **40002**。扫描器侧失败 -> **40005**，`scannerResult.success=false`。

---

#### 5.3.5 `POST /v1/scan/sub-tasks/{subTaskId}/resume` - 子任务启动
<a id="535-post-v1scansub-taskssubtaskidresume-子任务启动"></a>

| 项       | 值           |
| -------- | ------------ |
| 说明     | 启动单个子任务 |
| 现状路径 | 无           |
| 改造     | 新增         |

**路径参数**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| subTaskId | string |  ✓   | 子任务 ID  |

**响应 data**：

| 参数          | 类型     | 必填 | 说明                                                |
| ------------- | -------- | :--: | --------------------------------------------------- |
| subTaskId     | string   |  ✓   | 子任务 ID                                           |
| state         | string   |  ✓   | `1`执行中                                           |
| operator      | string   |  ○   | 操作人                                              |
| operateTime   | datetime |  ✓   | 操作时间                                            |
| message       | string   |  ✓   | 整体消息（成功/失败内容）                           |
| scannerResult | object   |  ✓   | 扫描器侧操作结果，结构同 [§5.3.4](#534-post-v1scansub-taskssubtaskidpause-子任务暂停) |

**`scannerResult` 对象**：`operate` 为 `resume`，其余字段同 [§5.3.4](#534-post-v1scansub-taskssubtaskidpause-子任务暂停)。

**状态约束**：级联到扫描器下发 `task_resume`。仅 `state=4`（暂停）可启动；非暂停态 -> **40002**。扫描器侧失败 -> **40005**，`scannerResult.success=false`。

---

#### 5.3.6 `DELETE /v1/scan/sub-tasks/{subTaskId}` - 子任务删除
<a id="536-delete-v1scansub-taskssubtaskid-子任务删除"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 删除单个子任务。⚠️ 现状 Java 方法名误写为 `pause`，实为删除，**以路径 `/delete` 为准**，本规整路径用 `DELETE` |
| 现状路径 | `GET /v1/scan/sub/task/delete/{key}`                                                              |
| 改造     | 规整                                                                                              |

**路径参数**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| subTaskId | string |  ✓   | 子任务 ID  |

**响应 data**：

| 参数          | 类型     | 必填 | 说明                                                |
| ------------- | -------- | :--: | --------------------------------------------------- |
| subTaskId     | string   |  ✓   | 子任务 ID                                           |
| operator      | string   |  ○   | 操作人                                              |
| operateTime   | datetime |  ✓   | 操作时间                                            |
| message       | string   |  ✓   | 整体消息（成功/失败内容）                           |
| scannerResult | object   |  ✓   | 扫描器侧操作结果（删除扫描器侧任务），结构同 [§5.3.4](#534-post-v1scansub-taskssubtaskidpause-子任务暂停) |

**`scannerResult` 对象**：`operate` 为 `delete`，其余字段同 [§5.3.4](#534-post-v1scansub-taskssubtaskidpause-子任务暂停)。

**状态约束**：级联删除扫描器侧任务 + ES/队列。子任务不存在 -> **40003**；扫描器侧删除失败 -> **40005**，`scannerResult.success=false`。

---

### 5.4 报告
<a id="54-报告"></a>

> 现状报告能力仅 LM；本节定义**通用多厂商**路径（去 `lm` 绑定），服务端按 `classifyId` 路由 `ReportGenerateStrategy`。现状 LM 专用接口（`/domnload/report/lm/*`）保留为兼容。

#### 5.4.1 `POST /v1/scan/tasks/{surveyId}/reports/generate` - 主任务生成报告（全量）
<a id="541-post-v1scantasksurveyidreportsgenerate-主任务生成报告全量"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 生成执行实例下全部子任务的扫描器原始报告。异步生成，完成后经 [§6.1.3 REPORT_COMPLETED](#613-report_completed主任务报告生成结束) 回调 |
| 现状路径 | `POST /v1/scan/task/vulnScan/domnload/report/lm/all`（仅 LM）                                    |
| 改造     | 规整（去 LM 绑定，通用多厂商）                                                                    |

**路径参数**：

| 参数     | 类型   | 必填 | 说明         |
| -------- | ------ | :--: | ------------ |
| surveyId | string |  ✓   | 执行实例 ID  |

**请求体**：

| 参数              | 类型     | 必填 | 说明                                          |
| ----------------- | -------- | :--: | --------------------------------------------- |
| reportTemplateCode | string  |  ○   | 报告模板码；缺省按厂商默认                    |
| format            | string   |  ○   | 格式：`html`/`pdf`/`xlsx`/`xml`               |
| subTaskIds        | string[] |  ○   | 指定子任务；缺省为全部子任务                  |

**响应 data**：

| 参数        | 类型   | 必填 | 说明                          |
| ----------- | ------ | :--: | ----------------------------- |
| surveyId    | string |  ✓   | 执行实例 ID                   |
| reportJobId | string |  ✓   | 报告任务 ID（查进度用）       |
| status      | string |  ✓   | `queued`/`generating`         |

**状态约束**：仅 `survey.state=2`（已完成）可生成；生成结束经 [§6.1.3](#613-report_completed主任务报告生成结束) 回调，或轮询 [§5.4.3](#543-get-v1scantasksurveyidreportsprogress-主任务报告进度查询)。

**请求示例**

```http
POST /v1/scan/tasks/100001/reports/generate HTTP/1.1
Content-Type: application/json

{ "format": "pdf" }
```

**响应示例（成功）**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "surveyId": "100001",
    "reportJobId": "RPT-20260727-001",
    "status": "queued"
  }
}
```

---

#### 5.4.2 `POST /v1/scan/sub-tasks/{subTaskId}/reports/generate` - 子任务生成报告
<a id="542-post-v1scansub-taskssubtaskidreportsgenerate-子任务生成报告"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 生成单个子任务的扫描器原始报告。完成后经 [§6.1.4 SUBTASK_REPORT_READY](#614-subtask_report_ready子任务报告生成结束) 回调 |
| 现状路径 | `POST /v1/scan/task/vulnScan/domnload/report/lm/id`（仅 LM）                                    |
| 改造     | 规整                                                                                              |

**路径参数**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| subTaskId | string |  ✓   | 子任务 ID  |

**请求体**：

| 参数              | 类型   | 必填 | 说明                            |
| ----------------- | ------ | :--: | ------------------------------- |
| reportTemplateCode | string |  ○  | 报告模板码                      |
| format            | string |  ○   | 格式：`html`/`pdf`/`xlsx`/`xml` |

**响应 data**：

| 参数        | 类型   | 必填 | 说明                |
| ----------- | ------ | :--: | ------------------- |
| subTaskId   | string |  ✓   | 子任务 ID           |
| reportJobId | string |  ✓   | 报告任务 ID         |
| status      | string |  ✓   | `queued`/`generating` |

---

#### 5.4.3 `GET /v1/scan/tasks/{surveyId}/reports` - 主任务报告查询
<a id="543-get-v1scantasksurveyidreportsprogress-主任务报告查询"></a>

| 项       | 值                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------- |
| 说明     | 查询执行实例下各子任务报告生成进度/状态。[§6.1.3](#613-report_completed主任务报告生成结束) 回调阻断时轮询兜底 |
| 现状路径 | `GET /v1/scan/task/vulnScan/query/domnload/report/{surveyId}`                                    |
| 改造     | 规整                                                                                              |

**路径参数**：

| 参数     | 类型   | 必填 | 说明         |
| -------- | ------ | :--: | ------------ |
| surveyId | string |  ✓   | 执行实例 ID  |

**响应 data**：`List<Map>`，元素字段：

| 参数        | 类型   | 必填 | 说明                                                      |
| ----------- | ------ | :--: | --------------------------------------------------------- |
| surveyId    | string |  ✓   | 执行实例 ID                                               |
| subTaskId   | string |  ✓   | 子任务 ID                                                 |
| nodeId      | string |  ✓   | 扫描节点 ID                                               |
| planId      | string |  ✓   | 扫描器计划 ID                                             |
| state       | string |  ✓   | 报告状态，见 [5.0.1](#任务状态枚举)；`4`可下载            |
| progress    | string |  ✓   | 进度                                                      |
| downloadUrl | string |  ○   | `state=4` 时的下载路径                                    |
| errorMsg    | string |  ○   | `state=3` 时的失败信息                                    |

**请求示例**

```http
GET /v1/scan/tasks/100001/reports/progress HTTP/1.1
```

**响应示例（成功）**

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "surveyId": "100001",
      "subTaskId": "654321",
      "nodeId": "10",
      "planId": "lm-plan-001",
      "state": "4",
      "progress": "100",
      "downloadUrl": "/ftp/report/lm-plan-001.html",
      "errorMsg": ""
    }
  ]
}
```

---

#### 5.4.4 `GET /v1/scan/sub-tasks/{subTaskId}/reports/progress` - 子任务报告进度查询
<a id="544-get-v1scansub-taskssubtaskidreportsprogress-子任务报告进度查询"></a>

| 项       | 值                                                           |
| -------- | ------------------------------------------------------------ |
| 说明     | 按子任务 ID 直查报告进度。现状入参为 `surveyId` 需客户端匹配，本接口为新增 `subTaskId` 维度 |
| 现状路径 | 无（复用主任务进度接口，入参 surveyId）                      |
| 改造     | 新增                                                         |

**路径参数**：

| 参数      | 类型   | 必填 | 说明       |
| --------- | ------ | :--: | ---------- |
| subTaskId | string |  ✓   | 子任务 ID  |

**响应 data**：

| 参数        | 类型   | 必填 | 说明                          |
| ----------- | ------ | :--: | ----------------------------- |
| subTaskId   | string |  ✓   | 子任务 ID                     |
| state       | string |  ✓   | 报告状态                      |
| progress    | string |  ✓   | 进度                          |
| downloadUrl | string |  ○   | 下载路径                      |
| errorMsg    | string |  ○   | 失败信息                      |

---

## 6. 事件回调（Kafka）
<a id="6-事件回调kafka"></a>

vuln-task-center 在特定异步事件发生时，向 Kafka topic 发布事件；客户端按 `clientType` / `passTaskId` 订阅并过滤。

| 项           | 约定                                                                 |
| ------------ | -------------------------------------------------------------------- |
| 触发时机     | 子任务列表就绪、子任务状态变更、报告生成结束（见 §6.1）              |
| 与 REST 关系 | 客户端主动调用 REST **不会**触发回调；回调为服务端**单向推送**       |
| 替代方式     | 回调未送达时可轮询 [§5.2.2](#522-get-v1scantaskstaskidsub-tasks-子任务列表分页) / [§5.4.3](#543-get-v1scantasksurveyidreportsprogress-主任务报告进度查询) |
| 幂等         | 以 `eventId` 去重                                                    |

### 6.0 通道与公共事件体
<a id="60-通道与公共事件体"></a>

| 事件                 | topic                          | 现状                                                                 |
| -------------------- | ------------------------------ | -------------------------------------------------------------------- |
| 主任务开始执行       | `vtc_task_started`             | 🔵 新增                                                              |
| 子任务列表就绪       | `vtc_subtask_list_notify`      | 🔵 新增（现状无）                                                    |
| 子任务状态变更       | `dr_vul_scan_task_status`      | ✅ 复用现状 topic（`SUB_TASK_STATUS_CHANGED`）                       |
| 主任务结束           | `vtc_task_completed`           | 🔵 新增                                                              |
| 主任务报告生成结束   | `dr_vul_scan_report_status`    | 🟡 复用现状 topic（`REPORT_JOB_COMPLETED`），payload 增强            |
| 子任务报告生成结束   | `vtc_subtask_report_ready`     | 🔵 新增                                                              |

**公共事件体**：

| 字段        | 类型     | 必填 | 说明                                    |
| ----------- | -------- | :--: | --------------------------------------- |
| eventId     | string   |  ✓   | 事件唯一 ID（幂等处理）                 |
| eventType   | string   |  ✓   | 事件类型，见 §6.1                       |
| occurredAt  | datetime |  ✓   | 事件发生时间                            |
| clientType  | string   |  ✓   | 客户端类型，见 [5.0.1](#四类客户端-clienttype)（路由过滤） |
| passTaskId  | string   |  ○   | 客户端任务键（客户端按此过滤）          |
| taskId      | string   |  ✓   | 主任务 ID                               |
| payload     | object   |  ✓   | 随事件类型变化                          |

### 6.1 事件类型与 payload
<a id="61-事件类型与-payload"></a>

| eventType                | 说明                         | 对应文档接口 |
| ------------------------ | ---------------------------- | ------------ |
| `TASK_STARTED`           | 主任务开始执行               | -            |
| `SUBTASK_LIST_READY`     | 子任务列表就绪（创建后异步） | 接口 1.5     |
| `SUBTASK_STATUS_CHANGED` | 子任务状态变更               | -            |
| `TASK_COMPLETED`         | 主任务结束                   | -            |
| `REPORT_COMPLETED`       | 主任务报告生成结束           | 接口 7       |
| `SUBTASK_REPORT_READY`   | 子任务报告生成结束           | 接口 14      |

#### 6.1.1 `SUBTASK_LIST_READY`（子任务列表回调）
<a id="611-subtask_list_ready子任务列表回调"></a>

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 说明 | mint 调度触发 `executeScanTask` 拆分子任务后推送。客户端据此获知子任务清单（含扫描节点 IP/厂商），无需轮询 |

**payload**：

| 参数        | 类型   | 必填 | 说明                                  |
| ----------- | ------ | :--: | ------------------------------------- |
| surveyId    | string |  ✓   | 执行实例 ID                           |
| subTasks    | array  |  ✓   | 子任务列表                            |

**`subTasks[]` 元素**：

| 参数       | 类型     | 必填 | 说明        |
| ---------- | -------- | :--: | ----------- |
| subTaskId  | string   |  ✓   | 子任务 ID   |
| state      | string   |  ✓   | 子任务状态  |
| startTime  | datetime |  ○   | 开始时间    |
| endTime    | datetime |  ○   | 结束时间    |
| scanNodeIp | string   |  ✓   | 扫描节点 IP |
| nodeId     | string   |  ✓   | 扫描节点 ID |
| vendor     | string   |  ✓   | 扫描器厂商  |

**示例**

```json
{
  "eventId": "evt-20260727-0001",
  "eventType": "SUBTASK_LIST_READY",
  "occurredAt": "2026-07-27T08:00:05Z",
  "clientType": "SCAN_MANAGE",
  "passTaskId": "EXT-TASK-001",
  "taskId": "123456",
  "payload": {
    "surveyId": "100001",
    "subTasks": [
      {
        "subTaskId": "654321",
        "state": "0",
        "startTime": "2026-07-27 08:00:00",
        "scanNodeIp": "10.0.0.10",
        "nodeId": "10",
        "vendor": "LM"
      },
      {
        "subTaskId": "654322",
        "state": "0",
        "startTime": "2026-07-27 08:00:00",
        "scanNodeIp": "10.0.0.11",
        "nodeId": "10",
        "vendor": "LM"
      }
    ]
  }
}
```

#### 6.1.2 `SUBTASK_STATUS_CHANGED`（子任务状态变更）
<a id="612-subtask_status_changed子任务状态变更"></a>

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 说明 | 子任务状态/进度变更时推送。复用现状 topic `dr_vul_scan_task_status` |

**payload**（对齐现状 `ab-contract.yaml`）：

| 参数          | 类型   | 必填 | 说明                                          |
| ------------- | ------ | :--: | --------------------------------------------- |
| surveyId      | string |  ✓   | 执行实例 ID                                   |
| subTaskId     | string |  ✓   | 子任务 ID                                     |
| vendor        | string |  ✓   | 厂商                                          |
| status        | enum   |  ✓   | `FINISHED` / `FAILED` / `RUNNING`             |
| progress      | int    |  ✓   | 0–100                                         |
| passSubTaskId | string |  ○   | 客户端子任务键                                |
| scanPhase     | int    |  ○   | 1排查/2验证/3修复核验                         |
| finishedAt    | datetime | ○  | 结束时间                                      |
| errorMessage  | string |  ○   | 失败原因                                      |

#### 6.1.3 `REPORT_COMPLETED`（主任务报告生成结束）
<a id="613-report_completed主任务报告生成结束"></a>

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 说明 | 主任务下全部子任务报告生成结束时推送。复用现状 topic `dr_vul_scan_report_status`，payload 增强 |

**payload**：

| 参数            | 类型   | 必填 | 说明                                              |
| --------------- | ------ | :--: | ------------------------------------------------- |
| surveyId        | string |  ✓   | 执行实例 ID                                       |
| reportJobId     | string |  ✓   | 报告任务 ID                                       |
| status          | enum   |  ✓   | `ready` / `failed`                                |
| subTaskReports  | array  |  ✓   | 子任务报告列表                                    |

**`subTaskReports[]` 元素**：

| 参数        | 类型   | 必填 | 说明                |
| ----------- | ------ | :--: | ------------------- |
| subTaskId   | string |  ✓   | 子任务 ID           |
| downloadUrl | string |  ○   | 报告下载路径       |
| errorMsg    | string |  ○   | 失败原因            |

**示例**

```json
{
  "eventId": "evt-20260727-0002",
  "eventType": "REPORT_COMPLETED",
  "occurredAt": "2026-07-27T10:35:00Z",
  "clientType": "SCAN_MANAGE",
  "passTaskId": "EXT-TASK-001",
  "taskId": "123456",
  "payload": {
    "surveyId": "100001",
    "reportJobId": "RPT-20260727-001",
    "status": "ready",
    "subTaskReports": [
      { "subTaskId": "654321", "downloadUrl": "/ftp/report/lm-plan-001.html" },
      { "subTaskId": "654322", "downloadUrl": "/ftp/report/lm-plan-002.html" }
    ]
  }
}
```

#### 6.1.4 `SUBTASK_REPORT_READY`（子任务报告生成结束）
<a id="614-subtask_report_ready子任务报告生成结束"></a>

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 说明 | 单个子任务报告生成结束时推送。topic `vtc_subtask_report_ready`，🔵 新增 |

**payload**：

| 参数        | 类型   | 必填 | 说明                          |
| ----------- | ------ | :--: | ----------------------------- |
| subTaskId   | string |  ✓   | 子任务 ID                     |
| reportJobId | string |  ✓   | 报告任务 ID                   |
| status      | enum   |  ✓   | `ready` / `failed`            |
| progress    | int    |  ✓   | 0–100                         |
| downloadUrl | string |  ○   | `ready` 时下载路径            |
| errorMsg    | string |  ○   | `failed` 时失败原因           |

**示例**

```json
{
  "eventId": "evt-20260727-0003",
  "eventType": "SUBTASK_REPORT_READY",
  "occurredAt": "2026-07-27T10:30:00Z",
  "clientType": "SCAN_MANAGE",
  "passTaskId": "EXT-TASK-001",
  "taskId": "123456",
  "payload": {
    "subTaskId": "654321",
    "reportJobId": "RPT-20260727-001",
    "status": "ready",
    "progress": 100,
    "downloadUrl": "/ftp/report/lm-plan-001.html"
  }
}
```

#### 6.1.5 `TASK_STARTED`（主任务开始执行通知）
<a id="615-task_started主任务开始执行通知"></a>

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 说明 | mint 调度回调 `executeScanTask`，创建执行实例 survey 并拆分子任务后推送。客户端据此获知任务**真正开始执行**（区别于创建时的"已接收"），携带 `surveyId`/`taskId`/开始时间 |

**payload**：

| 参数         | 类型     | 必填 | 说明                |
| ------------ | -------- | :--: | ------------------- |
| taskId       | string   |  ✓   | 主任务 ID           |
| surveyId     | string   |  ✓   | 执行实例 ID         |
| startTime    | datetime |  ✓   | 开始执行时间        |
| taskType     | string   |  ✓   | 任务类型            |
| scanIpTotal  | string   |  ○   | 扫描 IP 总数        |
| subTaskCount | int      |  ○   | 拆分子任务数        |

**示例**

```json
{
  "eventId": "evt-20260727-0000",
  "eventType": "TASK_STARTED",
  "occurredAt": "2026-07-27T08:00:00Z",
  "clientType": "SCAN_MANAGE",
  "passTaskId": "EXT-TASK-001",
  "taskId": "123456",
  "payload": {
    "taskId": "123456",
    "surveyId": "100001",
    "startTime": "2026-07-27 08:00:00",
    "taskType": "vuln_scan",
    "scanIpTotal": "2",
    "subTaskCount": 2
  }
}
```

#### 6.1.6 `TASK_COMPLETED`（主任务结束通知）
<a id="616-task_completed主任务结束通知"></a>

| 项   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| 说明 | 主任务执行实例 survey 结束时推送（全部子任务完成或失败）。客户端据此获知任务结束及扫描统计 |

**payload**：

| 参数           | 类型     | 必填 | 说明                              |
| -------------- | -------- | :--: | --------------------------------- |
| taskId         | string   |  ✓   | 主任务 ID                         |
| surveyId       | string   |  ✓   | 执行实例 ID                       |
| endTime        | datetime |  ✓   | 结束时间                          |
| status         | enum     |  ✓   | `FINISHED` / `FAILED`             |
| scanIpTotal    | string   |  ○   | 扫描 IP 总数                      |
| scanIpSuccess  | string   |  ○   | 扫描成功 IP 数                    |
| scanIpFail     | string   |  ○   | 扫描失败 IP 数                    |
| vulnCount      | string   |  ○   | 漏洞数量                          |
| duration       | string   |  ○   | 耗时                              |
| errorMessage   | string   |  ○   | `FAILED` 时失败原因               |

**示例**

```json
{
  "eventId": "evt-20260727-0009",
  "eventType": "TASK_COMPLETED",
  "occurredAt": "2026-07-27T10:30:00Z",
  "clientType": "SCAN_MANAGE",
  "passTaskId": "EXT-TASK-001",
  "taskId": "123456",
  "payload": {
    "taskId": "123456",
    "surveyId": "100001",
    "endTime": "2026-07-27 10:30:00",
    "status": "FINISHED",
    "scanIpTotal": "2",
    "scanIpSuccess": "2",
    "scanIpFail": "0",
    "vulnCount": "15",
    "duration": "2h30m"
  }
}
```

---

## 7. 接口编排使用场景
<a id="7-接口编排使用场景"></a>

> 以下场景结合 §5 REST 接口与 §6 Kafka 事件编排，说明四类客户端的典型调用链路。**服务端时序**描述 vuln-task-center 内部事件流转；**客户端时序**描述客户端动作。

### 7.1 开放平台
<a id="71-开放平台"></a>

**服务端时序**：

```
创建任务(§5.1.1, clientType=OPEN_PLATFORM, 指定厂商 classifyId)
   └─> 响应任务结果（同步返回 taskId）
        └─> 主任务开始执行通知（§6.1.5 TASK_STARTED，含 surveyId/startTime）
             └─> 子任务列表回调（§6.1.1 SUBTASK_LIST_READY，含子任务清单/扫描节点IP/厂商）
                  └─> 子任务状态变更（§6.1.2 SUBTASK_STATUS_CHANGED，执行中多次推送）
                       └─> 主任务结束通知（§6.1.6 TASK_COMPLETED，含扫描统计）
                            └─>【自动化】主任务生成报告（§5.4.1，全量子任务原始报告）
                                 └─> 主任务报告生成结束通知（§6.1.3 REPORT_COMPLETED，含子任务报告路径）
```

**客户端时序**：

```
接收 TASK_COMPLETED(§6.1.6)
   ├─> 拉取扫描任务结果：
   │    ├─ 查询漏洞扫描结果（§5.2.5）      -- 漏洞详情 + 漏洞库
   │    ├─ 查询资产端口详情（§5.2.8）      -- 端口任务（taskType=port）
   │    ├─ 查询扫描成功 IP（§5.2.6）
   │    └─ 查询扫描失败 IP（§5.2.7）
   │
   └─> 接收 REPORT_COMPLETED(§6.1.3)       -- 报告生成结束通知
        └─> 查询报告进度（§5.4.3）/ 按 downloadUrl 下载报告
```

**说明**：

- 开放平台创建任务时 `clientType=OPEN_PLATFORM` 并指定厂商 `classifyId`，服务端在该厂商可用节点中负载均衡分配扫描器。
- **主任务报告自动化**：主任务结束（`TASK_COMPLETED`）后，服务端**自动触发**主任务生成报告（§5.4.1，生成全部子任务的扫描器原始报告），完成后经 `REPORT_COMPLETED`（§6.1.3）通知客户端，客户端按 `subTaskReports[].downloadUrl` 下载；回调阻断时轮询 §5.4.3。
- **子任务生成报告（§5.4.2）用于查漏补缺**：当某子任务报告缺失或生成失败时，客户端可对单个子任务手动补生成（传入 `subTaskId`），完成后经 `SUBTASK_REPORT_READY`（§6.1.4）通知。非自动化流程，按需调用。
- 结果以 `TASK_COMPLETED` 为拉取触发点（回调阻断时可轮询 §5.2.5-§5.2.8）。现状开放平台入口为 `POST /event/scan/task/outside/soc/scan`（`outsideSocScan`，传 `taskId`/`scannerType`），规整后统一到 §5.1.1。

---

### 7.2 扫描任务管理（vuln-task-center 自身业务能力）
<a id="72-扫描任务管理vuln-task-center-自身业务能力"></a>

**服务端时序**：

```
创建任务(§5.1.1, clientType=SCAN_MANAGE, 负载均衡)
   └─> TASK_STARTED(§6.1.5) ─> SUBTASK_LIST_READY(§6.1.1)
        └─> SUBTASK_STATUS_CHANGED(§6.1.2，多次) ─> TASK_COMPLETED(§6.1.6)
```

**客户端时序**：

```
创建任务(§5.1.1) ─> 查询主任务详情(§5.2.1，含 surveyList 历史实例)
   │
   ├─ 运行中查询：子任务列表(§5.2.2) / 子任务详情(§5.2.3) / 扫描器任务列表(§5.2.4)
   │
   ├─ 操控（级联子任务 + 扫描器）：
   │   ├─ 主任务暂停(§5.3.1) / 启动(§5.3.2) / 删除(§5.3.3)
   │   └─ 子任务暂停(§5.3.4) / 启动(§5.3.5) / 删除(§5.3.6)
   │
   ├─ 报告：生成报告(§5.4.1) ─> 接收 REPORT_COMPLETED(§6.1.3)
   │        └─ 查询进度(§5.4.3) / 子任务报告进度(§5.4.4) / 下载
   │
   └─ 结果拉取：漏洞结果(§5.2.5) / 端口详情(§5.2.8) / 成功IP(§5.2.6) / 失败IP(§5.2.7)
```

**说明**：扫描任务管理是 vuln-task-center 自身业务能力，覆盖任务全生命周期。操控接口返回 `subTaskResults`/`scannerResult` 级联结果，部分失败时主接口仍 `200`。报告生成异步，完成后 `REPORT_COMPLETED` 回调。

---

### 7.3 运营指标任务
<a id="73-运营指标任务"></a>

**服务端时序**：

```
① 管理员分发：创建草稿(§5.1.2, clientType=OPS_METRIC)   -- 仅记录，不下发扫描器
② 安全员确认执行：执行(§5.1.3)                          -- 删草稿重建 + mint 下发
   └─> TASK_STARTED(§6.1.5) ─> SUBTASK_LIST_READY(§6.1.1)
        └─> SUBTASK_STATUS_CHANGED(§6.1.2) ─> TASK_COMPLETED(§6.1.6)
```

**客户端时序**：

```
管理员：创建草稿(§5.1.2)          -- 返回草稿 taskId，任务 state=0
   │
安全员：确认执行(§5.1.3，带草稿 taskId + 扫描参数)
   │
   └─> 接收 TASK_COMPLETED(§6.1.6)
        └─> 拉取漏洞扫描结果(§5.2.5) ─> 回写 vuln-model（经 vmId 关联统计）
```

**说明**：运营指标任务采用两阶段（分发/执行）模式，`flag=7` 标识。`vmId` 记录与 vuln-model 的对应关系，结果回写 vuln-model 统计。指标任务跳过「未知资产禁止」校验。

---

### 7.4 部侧专项工单
<a id="74-部侧专项工单"></a>

**服务端时序**：

```
① 接收部侧工单/任务（Kafka 入站，orderType+orderSubType 区分）
② 派发扫描任务：创建任务(§5.1.1, clientType=DEPT_WORKORDER, 指定扫描器 hash/节点 ID)
   └─> TASK_STARTED(§6.1.5) ─> SUBTASK_LIST_READY(§6.1.1)
        └─> SUBTASK_STATUS_CHANGED(§6.1.2) ─> TASK_COMPLETED(§6.1.6)
```

**客户端时序**：

```
接收部侧工单 ─> 派发扫描(distribute，clientType=DEPT_WORKORDER，nodeHash 指定扫描器)
   │
   └─> 接收 TASK_COMPLETED(§6.1.6)
        └─> 拉取结果：漏洞结果(§5.2.5) / 端口详情(§5.2.8) / 成功IP(§5.2.6) / 失败IP(§5.2.7)
             └─> 回传部侧（Kafka：工单回传 TOPICS_INTER_WORKORDER_PRODUCER / 任务回传 TOPICS_INTER_TASK_PRODUCER）
```

**说明**：部侧工单通过 `orderSubType` 区分（1/3 工单请求，101-105 任务）。派发扫描时 `clientType=DEPT_WORKORDER`，用 `nodeHash`/`scannerId` 指定扫描器。扫描完成拉取结果后回传部侧，`distributeStat` 流转 0未派发 -> 1已派发 -> 4已回传。

> ⚠️ 现状部侧入站 Kafka 消费链路（`WorkbenchConsumer`）未启用，实际消费方需确认；出站回传链路已启用。

---

## 文档要求接口覆盖对照

| 文档接口 | 本文档章节 | 改造 |
| -------- | ---------- | ---- |
| 1.1 任务下发（仅记录） | §5.1.2 | 复用 |
| 1.2 任务执行（确认下发） | §5.1.3 | 复用 |
| 1.3 任务创建（自动调度） | §5.1.1 | 复用 |
| 1.4 四类客户端区分 | §5.1.1（`clientType`） | 新增字段 |
| 1.5 子任务列表回调通知 | §6.1.1 | 新增 |
| 2 主任务详情查询 | §5.2.1 | 规整 |
| 3 子任务列表查询 | §5.2.2 | 规整 |
| 4 主任务暂停/启动 | §5.3.1 / §5.3.2 | 规整 |
| 5 主任务删除 | §5.3.3 | 规整 |
| 6 主任务生成报告 | §5.4.1 | 规整（通用化） |
| 7 主任务报告生成结束通知 | §6.1.3 | 复用+增强 |
| 8 查询主任务报告进度 | §5.4.3 | 规整 |
| 9 查询扫描器任务列表 | §5.2.4 | 新增 |
| 10 子任务详情查询 | §5.2.3 | 规整 |
| 11 子任务暂停/启动 | §5.3.4 / §5.3.5 | 新增 |
| 12 子任务删除 | §5.3.6 | 规整 |
| 13 子任务生成报告 | §5.4.2 | 规整（通用化） |
| 14 子任务报告生成结束通知 | §6.1.4 | 新增 |
| 15 查询子任务报告进度 | §5.4.4 | 新增 |

> **其余章节**（1 概述 / 2 接入准备 / 3 鉴权 / 4 通用约定 / 附录）暂未输出，待后续补充。
