# open-gateway 改造开发计划

> 版本：v1.0  日期：2026-06-19
> 依据：[open-gateway合并与平台业务解耦改造方案.md](open-gateway合并与平台业务解耦改造方案.md)
> 团队假设：1-2 名后端 + 1 名前端（串行为主，前端可穿插并行）
> 粒度：任务卡级（每卡含产出物 / 依赖 / 验收点 / 预估人日）

---

## 0. 总览

### 0.1 阶段甘特（关键路径）

```
Phase 0 契约冻结+注册表定义      [1周]  ████
Phase 1 网关合并                  [2周]      ████████
Phase 2 注册表改造                [2周]            ████████
Phase 3 业务下沉(依赖vul-pass就绪)[3-4周]                  ████████████
Phase 4 mock纯桩+切流             [1-2周]                              ██████
                                   │
前端 F0(契约对齐) ────────► F1(网关合并验证) ──► F2(注册表下发) ──────────► F3(临时点清理)
```

后端关键路径：Phase 0 → 1 → 2 → 3 → 4 串行（人少，不宜强行并行）。
前端穿插：F0 随 Phase 0、F1 随 Phase 1、F2 随 Phase 2、F3 随 Phase 4。

### 0.2 角色定义

| 角色 | 职责 | 人数 |
|---|---|---|
| BE-Gateway | open-gateway 网关层、注册表、管理面通用壳、切流 | 1 |
| BE-Biz | vul-pass 业务下沉、注册项接入、mock 桩维护 | 1（可与 BE-Gateway 同一人轮换） |
| FE | asset-openplatform-manage 前端 | 1 |

### 0.3 总估时

约 9-11 周（后端 7-9 周 + 前端穿插 4-5 卡）。Phase 3 依赖 vul-pass W1-W4 真实编排就绪，若 vul-pass 未就绪则 Phase 3 顺延。

---

## Phase 0 —— 契约冻结与注册表定义（1 周）

> 目标：冻结 Partner 对外契约作为共同基准；定义注册表接口契约；定义切流配置。纯设计+契约，不改业务代码。

### P0-1 冻结 Partner 对外契约（BE-Gateway + BE-Biz，2d）
- **产出**：`05-接口契约/open-api-partner-contract-v1.yaml`（OpenAPI），覆盖 `/api/open/v1/tasks/vul`、`/instances/search|get`、`/instances/{id}/verify|remediate|verify-fix`、`:batch`、`/tasks/{id}/exports`、`/exports/{id}(/download)`、`/oauth/token`。
- **要点**：明确**只含对外契约形状，不含内部业务字段**（`scan_phase`/`verify_merge_strategy`/`auto_verify` 不进响应）。状态机语义在响应里只体现为 `vulInfoStat` 终态值。
- **依赖**：无。
- **验收**：契约 yaml 通过 lint；mock 桩与 vul-pass 均以此为唯一基准。

### P0-2 定义注册表接口契约（BE-Gateway，2d）
- **产出**：四套注册接口的 OpenAPI + 存储选型决策（建议 Redis 缓存 + DB 持久化 `business_registry`）：
  - `POST /internal/registry/capabilities`（能力码：code/path/method）
  - `POST /internal/registry/webhook-events`（事件：code/payloadSchemaRef）
  - `POST /internal/registry/case-types`（案件类型：code/primaryResourceType/workspaceHandler）
  - `POST /internal/registry/routes`（路由：routePrefix/target/adapterMode 约束）
  - 配套 `GET /internal/admin/registry/*`（前端拉取用，挂管理面鉴权）
- **依赖**：无。
- **验收**：四接口契约评审通过；存储选型落定。

### P0-3 定义切流配置与灰度策略（BE-Gateway，1d）
- **产出**：`open-gateway.adapter-mode`（mock/vul-pass）配置项规格；灰度按 partner_id 维度的切流方案（部分 partner 走 mock、部分走 vul-pass）。
- **依赖**：P0-2。
- **验收**：配置项与灰度规则文档化，进入 Phase 1 实现依据。

### 前端 F0-1 契约对齐（FE，2d，与 P0-1 并行）
- **产出**：核对 `src/api/openPlatform/openPartnerApi.js` 现有调用与冻结契约一致；列出偏差清单。
- **依赖**：P0-1（契约初稿）。
- **验收**：偏差清单归档，为后续 F2 铺垫。

---

## Phase 1 —— 网关合并（2 周）

> 目标：partner-gateway + open-api-service 网关层物理合并为 open-gateway，监听隔离、三套鉴权链、配置合并。**不迁业务表**，open-api-service 暂时既当网关又当业务承载，保持测试期稳定。

### P1-1 合并工程骨架（BE-Gateway，3d）
- **产出**：新建 open-gateway 工程（或在 open-api-service 基础上吸收 partner-gateway 能力），合并依赖、配置、启动类。统一服务名 `open-gateway`，端口 35770。
- **依赖**：Phase 0 完成。
- **验收**：open-gateway 可启动，原 partner-gateway 的 Token 校验/限流/能力码拦截逻辑迁入并能跑通。

### P1-2 监听隔离与三套鉴权链（BE-Gateway，3d）
- **产出**：
  - 公网端口绑定 `/oauth/token`、`/api/open/v1/**`；内网绑定 `/internal/admin/**`、`/internal/health`、`/internal/dev/webhook/receive`（或同端口+内网段）。
  - 过滤器链按路径分流：Partner API（Bearer+X-Partner-Id）、管理面（X-Internal-Admin-Key）、无鉴权。
- **依赖**：P1-1。
- **验收**：三入口鉴权各按预期放行/拦截；`open-gateway.admin.api-key` 生效；未配 Admin Key 时管理面 401。

### P1-3 契约路由与 adapter-mode 开关（BE-Gateway，2d）
- **产出**：`/api/open/v1/**` 按 `adapter-mode` 路由——`mock` 转发到 open-api-service 桩（此阶段 open-api-service 仍是业务承载，先转发到自身业务实现）、`vul-pass` 转发到 vul-pass。路由暂用配置硬编码，Phase 2 改注册表驱动。
- **依赖**：P1-2。
- **验收**：切换 `adapter-mode` 配置，`/api/open/v1/**` 命中不同后端；健康检查通过。

### P1-4 配置合并与部署链调整（BE-Gateway，2d）
- **产出**：合并两服务配置项（admin key、adapter-mode、限流、Token 缓存、file-sharing 等）为一份；CI/CD（Choerodon）调整：open-gateway 单服务构建部署，partner-gateway 镜像停止构建。
- **依赖**：P1-3。
- **验收**：open-gateway 单服务部署成功；旧 partner-gateway 下线（保留回滚镜像）。

### 前端 F1-1 网关合并验证（FE，2d，与 P1-4 并行）
- **产出**：`vue.config.js` / `.env*` 反代配置简化（双通道 baseURL 不变，后端合一透明）；冒烟验证双通道（`openApiRequest`/`openPartnerRequest`）仍通。
- **依赖**：P1-4。
- **验收**：Partner 管理/调用记录/E2E 接入测试页冒烟通过。

> **Phase 1 回滚**：若鉴权/路由回归，回退双服务部署（partner-gateway 镜像仍在）。

---

## Phase 2 —— 注册表改造（2 周）

> 目标：平台层能力码/Webhook事件/案件类型从硬编码枚举改为注册表驱动；vul-pass 启动注册漏洞业务项；前端枚举改注册表下发。**先在 mock 模式验证**。

### P2-1 注册表存储与接口实现（BE-Gateway，3d）
- **产出**：`business_registry` 相关表/Redis 结构；四套 `POST /internal/registry/*` 接口实现（服务间鉴权）；`GET /internal/admin/registry/*` 查询接口。
- **依赖**：P0-2、Phase 1。
- **验收**：curl 注册一条 capability，`GET` 能查回；重复注册幂等。

### P2-2 网关拦截改注册表驱动（BE-Gateway，3d）
- **产出**：能力码拦截从硬编码枚举改为查注册表（路径+方法→capability→Partner 是否开通→40301）；契约路由从 P1-3 配置硬编码改为查 routes 注册表（含 adapter-mode 覆盖）；Webhook 投递的事件类型校验改查注册表。
- **依赖**：P2-1。
- **验收**：删掉平台层硬编码能力码枚举后，注册的能力仍能正确拦截；`adapter-mode=mock` 仍按 routes 表路由。

### P2-3 运营案件壳去业务字段（BE-Gateway，2d）
- **产出**：`open_operation_case` 壳去除漏洞专属字段；case_type 改为查注册表（不持枚举值）；工作台 payload 按 `workspaceHandler` 路由聚合（转发到业务服务 handler）。
- **依赖**：P2-1。
- **验收**：案件壳无漏洞字段；按注册的 case_type 能找到对应 workspaceHandler 并聚合 payload。

### P2-4 vul-pass 注册接入（BE-Biz，2d）
- **产出**：vul-pass 启动时向 open-gateway 注册漏洞业务的 capability（INSTANCE_VERIFY 等）、event（TASK_COMPLETED 等）、case-type（TASK_SCAN/VERIFY_FIX 等）、route（/api/open/v1/tasks,/instances → vul-pass）。
- **依赖**：P2-1。
- **验收**：vul-pass 启动后 `GET /internal/admin/registry/*` 能查到漏洞业务全套注册项；mock 模式下端到端拦截/投递/案件渲染正常。

### 前端 F2-1 枚举改注册表下发（FE，3d，与 P2-2/P2-4 并行）
- **产出**：新增 `/internal/admin/registry/*` 拉取；`OPERATION_CASE_TYPES`/`CAPABILITIES`/`WEBHOOK_EVENT_TYPES` 从 `src/constants/openPlatformDisplay/enums.js` 硬编码改为注册表下发 + 前端内置兜底（接口空值时 fallback）；案件工作台多态面板按注册 case_type 渲染。
- **依赖**：P2-1（接口可用）。
- **验收**：注册表下发后枚举标签正确；接口失败时兜底枚举生效（不空白）。

> **Phase 2 回滚**：注册表异常时，前端 fallback 兜底枚举；后端回退硬编码枚举（保留 git 历史）。
> **Phase 2 验收硬指标**：换一个非漏洞业务注册新 capability/event/case-type/route，open-gateway 零代码改动即可完成拦截/投递/案件渲染/路由（对应方案 §9.3）。

---

## Phase 3 —— 业务下沉（3-4 周，依赖 vul-pass W1-W4 就绪）

> 目标：漏洞表/编排/契约实现/业务 Admin 迁 vul-pass；OAuth 签发迁认证服务。**双写过渡**，对账通过后切流。此阶段 open-api-service 仍以"网关+业务承载"身份运行。

### P3-1 vuln-business 模块搭建（BE-Biz，3d）
- **产出**：在 vul-pass 内建 vuln-business 模块（或包），承接 `open_task`/`open_vuln_instance`/`open_verify_fix_job`/`open_export` 的 PO/DO/Mapper；建表 DDL（从 open-api-service 迁移）。
- **依赖**：vul-pass W1-W4 真实编排就绪（autoVerify/UNION/INTERSECT/scan_phase/transition/双轨）。**若未就绪，本 Phase 整体顺延。**
- **验收**：vul-pass 侧表结构就绪，单元读写通过。

### P3-2 契约实现下沉（BE-Biz，4d）
- **产出**：`/api/open/v1/tasks/vul`、`/instances/*` 真实实现迁入 vul-pass，对接 vul-pass 编排内核（沿用实例域两硬约束：vulInfoID≠id、写前查 page 换 id；统一 PUT `/vul-scan-task-sub-system`）。
- **依赖**：P3-1。
- **验收**：vul-pass 侧实现通过契约 P0-1 yaml 比对，响应形状与 mock 桩一致（内部字段不暴露）。

### P3-3 业务 Admin 下沉（BE-Biz，3d）
- **产出**：`/internal/admin/open-tasks`、`/open-vuln-instances`、`/verify-fix` 迁 vul-pass；open-gateway 仅留通用 Admin 壳（partners/invocations/webhook-deliveries/quotas/operation-cases 壳/api-operations）。
- **依赖**：P3-2。
- **验收**：前端管理页调相应 admin 接口仍正常；open-gateway 代码库无业务 admin。

### P3-4 OAuth 签发迁认证服务（BE-Gateway，2d）
- **产出**：`/oauth/token` 签发逻辑迁认证服务；open-gateway 仅校验（查 Redis `partner:token:{sha256}` 或 introspect）。
- **依赖**：Phase 1。
- **验收**：Partner 换 token 流程正常；网关不再持签发逻辑。

### P3-5 双写过渡与对账（BE-Biz + BE-Gateway，4d）
- **产出**：open-api-service 与 vul-pass 并行写（双写）`open_task` 等表；对账任务比对两侧一致性；不一致告警。
- **依赖**：P3-2、P3-3。
- **验收**：连续 N 天双写对账零差异；可切流。

> **Phase 3 回滚**：双写不一致时回退单写 open-api-service，保留业务承载。

---

## Phase 4 —— mock 纯桩化与切流（1-2 周）

> 目标：open-api-service 剥离真实逻辑退化为纯契约桩；灰度切流 mock→vul-pass；前端临时点清理。

### P4-1 open-api-service 纯桩化（BE-Biz，3d）
- **产出**：剥离真实 Feign 编排、真实业务表、`/internal/admin` 治理面、OAuth 签发、半人工 XML 导入（mockTask/mockVerifyFix）；只保留 Partner 契约 mock 实现（按 vulInfoStat 状态机返假数据 1→2→5→6/7、误报 1→3、批量共享 verifyFixJobId）；mock 用内存或独立 mock 表；调用记录落地。
- **依赖**：Phase 3 双写对账通过。
- **验收**：open-api-service 无真实编排、无内部业务字段暴露（对应方案 §5.3）；契约形状与 P0-1 一致。

### P4-2 灰度切流与对比回归（BE-Gateway + BE-Biz，3d）
- **产出**：按 partner_id 灰度把 `adapter-mode` 从 mock 切到 vul-pass；同输入比对 mock 与 vul-pass 输出差异；修复差异。
- **依赖**：P4-1。
- **验收**：灰度 partner 端到端通过；Partner 无感（对应方案 §9.5）。

### P4-3 桩服务下线/备用（BE-Gateway，1d）
- **产出**：全量切 vul-pass 后，open-api-service 桩停止接收流量，保留备用镜像。
- **依赖**：P4-2 全量通过。
- **验收**：线上无流量命中桩；可随时拉起备用（对应方案 §9.6）。

### 前端 F3-1 临时点清理（FE，3d，与 P4 并行）
- **产出**：
  - 移除 `src/api/openPlatform/mockTask.js`、`mockVerifyFix.js` 半人工导入（真实复扫回调已就绪）；
  - 收敛两个同名 `listVerifyFixJobs` 到 `verifyFix.js`；
  - 评估删除 `src/views/openPlatform/OpenSocOrchestration.vue`（已被 redirect 替代）；
  - `src/api/openPlatform/quota.js` N+1 聚合 → 后端补 stats 聚合接口后简化（依赖 BE-Gateway 补 `/internal/admin/partners/stats/aggregate`）。
- **依赖**：P4-2（真实链路就绪）。
- **验收**：前端无 mock 半人工残留；lint 通过；`verify-utf8` 校验通过；冒烟全页正常。

---

## 1. 关键路径与依赖图

```
P0-1 ─┬─► P1-1 ─► P1-2 ─► P1-3 ─► P1-4 ─► P2-1 ─┬─► P2-2 ─► P2-3
P0-2 ─┤                                         ├─► P2-4
P0-3 ─┘                                         │
                                                │   (Phase 3 依赖 vul-pass W1-W4 就绪)
                                                └─► P3-1 ─► P3-2 ─► P3-3 ─► P3-5 ─► P4-1 ─► P4-2 ─► P4-3
                                                     P3-4(可并行) ─┘
前端: F0-1(P0) ─► F1-1(P1) ─► F2-1(P2) ─────────────────────────────────► F3-1(P4)
```

后端关键路径：P0 → P1 → P2 → P3（受 vul-pass 就绪阻塞）→ P4。
P3-4（OAuth 迁移）与 P3-1~P3-3 可并行（若 2 名后端）。

---

## 2. 验收里程碑

| 里程碑 | 对应方案 §9 | 完成标志 |
|---|---|---|
| M1 网关合并 | §9.1 | Phase 1 结束：公网/内网监听隔离、三套鉴权链、前端双通道无感 |
| M2 注册表驱动 | §9.3 | Phase 2 结束：换业务零代码改动即可拦截/投递/渲染/路由 |
| M3 平台零业务语义 | §9.2 | Phase 3 结束：open-gateway 无 `scan_policy`/`auto_verify`/`vulInfoStat`/`scan_phase`、无 `open_task` 等业务表 |
| M4 业务下沉 | §9.4 | Phase 3 结束：漏洞表/编排/契约/业务 Admin 全在 vul-pass |
| M5 mock 纯桩+可下线 | §9.5/§9.6 | Phase 4 结束：桩只返契约形状、adapter-mode 可切换、切流后 Partner 无感、桩可下线 |

---

## 3. 风险跟踪（沿用方案 §8，细化触发点）

| 风险 | 触发点 | 缓解/回滚 |
|---|---|---|
| 网关合并鉴权/路由回归 | Phase 1 | P1 先合网关不迁业务；回退双服务部署 |
| 业务表迁移数据不一致 | Phase 3 | P3-5 双写+对账；不一致回退单写 |
| 注册表拦截/投递异常 | Phase 2 | 先 mock 模式验证；前端 fallback 兜底；回退硬编码 |
| mock 桩暴露内部字段成事实契约 | Phase 4 | §5.3 约束 + code review；剔除内部字段 |
| 切流后 Partner 感知差异 | Phase 4 | P4-2 灰度+对比回归；切回 mock |
| vul-pass W1-W4 未就绪阻塞 Phase 3 | Phase 3 起点 | Phase 3 整体顺延；Phase 1-2 先行不阻塞 |

---

## 4. 备注

- **测试期稳定优先**：Phase 1-2 可先行且不影响现有测试版本运行；Phase 3-4 在 vul-pass 就绪后推进，不必一次性推完。
- **前端双通道 baseURL 全程不变**：后端合并对前端透明，前端改造集中在枚举下发与临时点清理。
- **不删除原则**：过程产物（旧 partner-gateway 镜像、硬编码枚举 git 历史、open-api-service 业务承载分支）保留至对应里程碑验收通过后再清理。
- **编码护栏**：前端修改生成产物类 Vue 文件（报文模态、webhook secret UI）仍走 `scripts/` 生成脚本，不动 `verify-utf8` 链。
