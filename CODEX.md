# CODEX

Codex 使用本仓库时，先读取本文件和 `Prompts/README.md`。本仓库是全局 Prompt Repository，默认路径：

```text
C:\Users\ROG\Documents\Prompt Repository
```

## 定位规则

- 在任意项目中收到保存、检索、调用 Prompt、角色卡或高频工作流请求时，优先使用本仓库。
- 如果当前项目也有本地 `Prompts` 目录，除非用户明确要求使用项目本地库，否则仍使用本全局库。
- 保存前必须先用 `rg` 或 `scripts/search_prompts.ps1` 检查相似 Prompt，优先更新现有文件，避免重复创建。

## 分类规则

- 普通 Prompt 使用 `Prompts/📄 模板/Prompt_Template.md`。
- 收藏或书签式 Prompt 保存到 `Prompts/Favorites`，使用 `Prompts/Favorites/收藏-模板.md`。
- 角色卡使用 `Prompts/📄 模板/Role_Template.md`，保存到 `Prompts/🧩 角色卡`。
- 未验证 Prompt 保存到 `Prompts/🧪 测试`。
- 已验证场景 Prompt 保存到 `Prompts/📚 专业场景`。
- 高频工作流保存到 `Prompts/High-Frequency Workflows`。

## Frontmatter

每个 Prompt 文件使用 Markdown + YAML frontmatter：

```yaml
---
title: ""
category: lab
status: draft
version: v1.0
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
role: ""
level: ""
source: internal
---
```

## 索引和同步

- 保存、更新、迁移 Prompt 后运行 `scripts/update_index.ps1`。
- 检索 Prompt 时可运行 `scripts/search_prompts.ps1 -Query "关键词"`，也可传 `-Tag`、`-Status`、`-Category`。
- GitHub 同步使用 `scripts/sync_github.ps1`；首次同步需要传入 `-RemoteUrl`。
- GitHub 仓库建议设为 private。

## 常用指令

```text
请按照 Prompt Repository 工作，优先读取 CODEX.md 和 Prompts/README.md。
```

```text
请将下面这个提示词加入 Prompt 库。你先判断分类，然后自动整理 YAML、使用经验和优化记录，保存到最合适的位置，并更新索引。
```
