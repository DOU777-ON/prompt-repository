# Prompts

Prompt 资产目录。本文件包含分类规则和自动索引。

## 目录

```text
Prompts
├─ Favorites
├─ High-Frequency Workflows
├─ 🧩 角色卡
├─ 📚 专业场景
├─ 🧪 测试
├─ 📄 模板
└─ README.md
```

## 规则

- 普通 Prompt：使用 `📄 模板/Prompt_Template.md`。
- 收藏 Prompt：使用 `Favorites/收藏-模板.md`。
- 角色卡：使用 `📄 模板/Role_Template.md`。
- 临时收藏：放 `Favorites`。
- 新 Prompt：先放 `🧪 测试`。
- 已验证场景：放 `📚 专业场景`。
- 高频工作流：放 `High-Frequency Workflows`。

普通 Prompt 结构：

```text
YAML frontmatter
# 标题
## 使用经验
## 优化记录
```

## 自动索引

由 `scripts/update_index.ps1` 维护。不要手动编辑标记之间的内容。

<!-- BEGIN_AUTO_INDEX -->
### .

| Title | Status | Tags | Updated | Path |
|---|---|---|---|---|
| Codex-自动分类保存规则 | favorite | codex, auto-classification, prompt-intake, prompt-repository | 2026-06-04 | [Codex-自动分类保存规则.md](Codex-自动分类保存规则.md) |

### High-Frequency Workflows

| Title | Status | Tags | Updated | Path |
|---|---|---|---|---|
| Codex-Prompt入库 | favorite | codex, prompt-intake, prompt-repository | 2026-06-04 | [High-Frequency Workflows/Codex-Prompt入库.md](High-Frequency Workflows/Codex-Prompt入库.md) |
| Codex-从库调用Prompt | favorite | codex, prompt-retrieval, prompt-repository | 2026-06-04 | [High-Frequency Workflows/Codex-从库调用Prompt.md](High-Frequency Workflows/Codex-从库调用Prompt.md) |
| Codex-调用相关角色卡 | favorite | codex, role-card, prompt-repository, high-frequency | 2026-06-04 | [High-Frequency Workflows/Codex-调用相关角色卡.md](High-Frequency Workflows/Codex-调用相关角色卡.md) |
| Workflow-High-Frequency-Task-Handling | favorite | workflow, high-frequency, task-execution, codex | 2026-06-04 | [High-Frequency Workflows/Workflow-High-Frequency-Task-Handling.md](High-Frequency Workflows/Workflow-High-Frequency-Task-Handling.md) |

### 📚 专业场景

| Title | Status | Tags | Updated | Path |
|---|---|---|---|---|
| 总图 | draft | prompt, 总图, 待补充 | 2026-06-04 | [📚 专业场景/总图.md](📚 专业场景/总图.md) |

### 🧩 角色卡

| Title | Status | Tags | Updated | Path |
|---|---|---|---|---|
| 角色卡-Prompt工程师 | validated | role-card, prompt-engineering, ai-repository | 2026-06-04 | [🧩 角色卡/角色卡-Prompt工程师.md](🧩 角色卡/角色卡-Prompt工程师.md) |
| 角色卡-电力工程设计师 | validated | role-card, power-engineering, electrical-design, engineering | 2026-06-04 | [🧩 角色卡/角色卡-电力工程设计师.md](🧩 角色卡/角色卡-电力工程设计师.md) |
| 角色卡-康复医生 | validated | role-card, rehabilitation, medicine, clinical-support | 2026-06-04 | [🧩 角色卡/角色卡-康复医生.md](🧩 角色卡/角色卡-康复医生.md) |

### 🧪 测试

| Title | Status | Tags | Updated | Path |
|---|---|---|---|---|
| 产品-MVP设计 | testing | mvp, product, strategy, lab | 2026-06-04 | [🧪 测试/产品-MVP设计.md](🧪 测试/产品-MVP设计.md) |
| 结构化-YAML生成 | testing | yaml, structured-output, metadata, lab | 2026-06-04 | [🧪 测试/结构化-YAML生成.md](🧪 测试/结构化-YAML生成.md) |
| 设计-工作流拆解 | testing | workflow, process-design, task-planning, lab | 2026-06-04 | [🧪 测试/设计-工作流拆解.md](🧪 测试/设计-工作流拆解.md) |
<!-- END_AUTO_INDEX -->

