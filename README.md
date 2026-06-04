# Prompt Repository

全局 Prompt Repository。用于在 Obsidian 中浏览，在 Codex 中跨项目检索、调用、保存和同步 Prompt。

## 使用

1. 用 Obsidian 打开本目录作为 vault。
2. 在任意 Codex 项目中，按 Prompt Repository 工作时优先使用本仓库。
3. Codex 读取 `CODEX.md` 和 `Prompts/README.md` 后再保存或调用 Prompt。
4. Prompt 资产统一放在 `Prompts` 目录。

## 结构

```text
.
├─ README.md
├─ CODEX.md
├─ .gitignore
├─ Prompts
└─ scripts
```

## 常用命令

```powershell
.\scripts\update_index.ps1
.\scripts\search_prompts.ps1 -Query "关键词"
.\scripts\search_prompts.ps1 -Tag "codex"
.\scripts\sync_github.ps1
```

首次 GitHub 同步时先提供 remote：

```powershell
.\scripts\sync_github.ps1 -RemoteUrl "https://github.com/<user>/<private-repo>.git"
```

## 维护规则

- 新 Prompt 先放 `Prompts/🧪 测试`。
- 临时收藏或书签式 Prompt 放 `Prompts/Favorites`。
- 稳定后迁移到 `Prompts/📚 专业场景`。
- 角色卡放 `Prompts/🧩 角色卡`。
- 高频工作流放 `Prompts/High-Frequency Workflows`。
- 改目录、模板或规则时，同步更新 `CODEX.md` 和 `Prompts/README.md`。
- 保存或迁移 Prompt 后运行 `scripts/update_index.ps1`。
