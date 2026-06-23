# PRD → Multi-Agent 自动化开发工作流

> **目标**：把产品需求（PRD）转成**可并行执行**的 Agent Prompt，避免「整份 PRD 丢给一个 Agent」导致的边界冲突与返工。
>
> **产物链**：`PRD` → `任务拆分矩阵 YAML` → `multi-agent-执行Prompts.md` → 各 Cursor Agent 会话

---

## 1. 为什么不直接用 PRD

| 问题 | 说明 |
|------|------|
| PRD 偏「做什么」 | Agent 需要「改哪个 repo、禁止改什么、怎么验收」 |
| 全栈单 Agent | 易改 clover-front / gateway / 后端同一 diff，冲突大 |
| 验收模糊 | 「体验更好」无法自动验证 |

因此增加中间层：**任务拆分矩阵** — 把 PRD 翻译成工程边界 + 依赖 + Prompt。

---

## 2. 流程总览

```text
┌─────────────┐    ┌──────────────────┐    ┌─────────────────────────┐    ┌──────────────┐
│ 1. PRD      │───▶│ 2. 任务拆分矩阵   │───▶│ 3. generate 脚本         │───▶│ 4. 执行 Agent │
│ (产品输入)   │    │ (features/*.yaml) │    │ → multi-agent-Prompts.md │    │ (Cursor 并行) │
└─────────────┘    └──────────────────┘    └─────────────────────────┘    └──────────────┘
       │                     │                          │
       ▼                     ▼                          ▼
  PRD-模板.md          落地方案 / 页面设计          复制 Prompt X 到新会话
  .trae/specs/         OpenAPI / 原型 HTML           按 Wave 并行
```

### 阶段门禁

| 阶段 | 门禁 | 产出 |
|------|------|------|
| **PRD 评审** | 成功标准可衡量、不做边界清晰、页面/API 清单含 P0/P1 | `PRD-模板.md` 或 `.trae/specs/*/spec.md` |
| **拆分评审** | 每个 Agent 只有一个主 repo、deny_paths 完整、depends_on 无环 | `features/{id}.yaml` |
| **Prompt 生成** | 脚本跑通、Prompt 含交付与验证 | `multi-agent-执行Prompts.md` |
| **开发** | 一次只开一个 Agent 对应 Prompt | 各工程 PR / diff |
| **Integration** | acceptance 列表全绿 | 联调报告 |

---

## 3. 任务拆分矩阵字段说明

文件位置：`svmp/docs/internal/features/{feature-id}.yaml`  
模板：`templates/任务拆分矩阵-模板.yaml`  
示例：`features/open-platform-admin-p0.yaml`

| 字段 | 必填 | 说明 |
|------|:----:|------|
| `feature.id` | ✓ | 功能编号，如 `OP-ADMIN-P0` |
| `feature.landing_plan` | ✓ | 落地方案 markdown 路径 |
| `shared_reads` | ✓ | 所有 Agent 共读的文档 |
| `acceptance` | ✓ | Integration Agent 端到端门禁 |
| `agents[].id` | ✓ | Prompt 字母/编号（I、D、F、E、G…） |
| `agents[].allow_paths` | ✓ | 允许修改的路径 glob |
| `agents[].deny_paths` | ✓ | **禁止**修改的路径（防越界） |
| `agents[].reads` | ✓ | 该 Agent 必读 |
| `agents[].delivers` | ✓ | 交付物清单 |
| `agents[].verify` | ✓ | 验证命令或步骤 |
| `agents[].depends_on` | ○ | 依赖的其他 Prompt ID |
| `agents[].prompt` | ✓ | 复制到 Cursor 的完整 Prompt 正文 |

### Agent 切分原则

1. **按工程切**：一个 Agent 默认只改一个主 repo（Integration / Doc 除外）
2. **按阶段切**：P0 与 P1 分文件或分 `phase_note`
3. **显式禁止**：`deny_paths` 比 `allow_paths` 更重要（防改 clover-front 等）
4. **可并行**：无依赖的 Agent 同一 Wave 开多个 Cursor 会话

---

## 4. 从 PRD 填矩阵 — 对照表

填 PRD 时，用下表映射到 YAML：

| PRD 章节 | 映射到 YAML |
|----------|-------------|
| §1 成功标准 | `acceptance` + 各 Agent `verify` |
| §1.4 不做边界 | 各 Agent `deny_paths` + prompt 内【禁止】 |
| §3.2 页面/API 清单 | 按 repo 分到 Frontend / Backend Agent `delivers` |
| §4 技术约束 | `feature.landing_plan` + `shared_reads` |
| §5 验收标准 | `acceptance`（与 Integration Agent 对齐） |

**已有落地方案时**：可跳过完整 PRD，直接从落地方案 + 页面设计生成 YAML（开放平台 P0 即此路径）。

---

## 5. 生成 Prompt 文档

```bash
# 默认：open-platform-admin-p0.yaml → multi-agent-执行Prompts.md
py -3 svmp/docs/internal/scripts/generate-multi-agent-prompts.py

# 指定功能
py -3 svmp/docs/internal/scripts/generate-multi-agent-prompts.py features/open-platform-admin-p0.yaml
```

修改 YAML 后**重新运行脚本**；`multi-agent-执行Prompts.md` 顶部的自动生成标记会更新。

---

## 6. 执行 Multi-Agent（Cursor）

### 6.1 打开会话

1. 打开 `multi-agent-执行Prompts.md`
2. 找到对应 **Prompt X** 的「执行 Prompt」代码块
3. **新建 Cursor Agent 会话**，整段粘贴
4. 可选：附加 Skill（如 `esmp-backend-dev`、`esmp-frontend-dev`）

### 6.2 推荐并行 Wave（开放平台 P0）

```text
Wave 1: Prompt H（文档）+ D（Backend-Admin）+ F（Backend-OpenAPI）  ← 并行
Wave 2: Prompt I（前端，依赖 H）+ E（网关，依赖 F）                 ← 并行
Wave 3: Prompt G（Integration，依赖 I+D+F+E）                       ← 串行
Wave 4: Prompt J（P1，依赖 G）                                      ← 下一阶段
```

### 6.3 Integration Agent 职责

- 不改功能代码（除非开独立 fix 任务）
- 核对 `acceptance` 与落地方案 §9.2 评审表
- 输出联调报告：通过项 / 阻塞项 / 指派

---

## 7. 与 PM-AI 工作流的关系

| PM-AI 阶段 | 本工作流对应 |
|------------|--------------|
| 需求澄清 / 产品方案 | 写 PRD（`PRD-模板.md`） |
| 产品原型 | HTML 原型 / 页面设计 |
| 交付开发 | 任务拆分 YAML → Multi-Agent Prompt → 编码 |
| 交付门禁 | Integration + acceptance |

PRD 是**可选上游**；若已有「完整落地方案 + 页面设计」，可直接从步骤 2（拆分矩阵）开始。

---

## 8. 新功能快速开始

```text
1. 复制 templates/PRD-模板.md → 填写 / 或使用 .trae/specs/{feature}/spec.md
2. 复制 templates/任务拆分矩阵-模板.yaml → features/{feature-id}.yaml
3. 按 PRD 填 agents、allow/deny、delivers、prompt
4. py -3 svmp/docs/internal/scripts/generate-multi-agent-prompts.py features/{feature-id}.yaml
5. 按 Wave 在 Cursor 中执行各 Prompt
6. Prompt G 联调通过后标记 PRD/落地方案「已交付」
```

---

## 9. 相关文件

| 文件 | 作用 |
|------|------|
| [templates/PRD-模板.md](./templates/PRD-模板.md) | PRD 输入模板 |
| [templates/任务拆分矩阵-模板.yaml](./templates/任务拆分矩阵-模板.yaml) | 拆分矩阵空模板 |
| [features/open-platform-admin-p0.yaml](./features/open-platform-admin-p0.yaml) | 开放平台 P0 示例 |
| [multi-agent-执行Prompts.md](./multi-agent-执行Prompts.md) | 生成的 Agent Prompt（执行用） |
| [开放平台集成管理-完整落地方案.md](./开放平台集成管理-完整落地方案.md) | 业务落地方案 |
| `.cursor/skills/prd-to-multi-agent/SKILL.md` | Cursor Skill：引导本流程 |
