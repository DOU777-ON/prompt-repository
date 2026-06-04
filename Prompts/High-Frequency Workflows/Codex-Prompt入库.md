---
title: Codex-Prompt入库
category: high-frequency
status: favorite
version: v1.4
tags:
  - codex
  - prompt-intake
  - prompt-repository
created: 2026-06-04
updated: 2026-06-04
role: Prompt工程师
level: L5
source: internal
---

# Codex-Prompt入库

## 使用经验

- 适合在一次 Codex 任务结束后，把好用提示词沉淀为资产。
- 如果用户没有指定目录，按自动分类规则选择目录；只有信息不足或未经验证时才进入测试。
- 如果用户明确说“已经验证过”，可保存为 scenario + validated。
- 入库前应先读取或参考当前 README、Prompt_Template 和自动分类保存规则，确保 Codex 使用的是最新版库规则。
- 如果 Obsidian 库规则刚被修改，必须同步更新 Codex 相关高频工作流后再保存新 Prompt。
- 普通 Prompt 入库时只保留 YAML、使用经验和优化记录；角色卡继续使用角色卡模板。
- 用户只说“优化入库”时，优先优化已有入库工作流或分类规则，不新建重复 Prompt。
- 入库或迁移完成后必须运行 `scripts/update_index.ps1`，让 README 索引和桌面小卡片同步刷新。
- 如果变更应长期保留，提交并推送到 GitHub；只忽略 Obsidian 本地 UI 配置等未明确要求同步的文件。
- 桌面小卡片双击提示词时只复制提示词正文，因此入库时应把真正可复用的 Prompt 放在 `## Prompt 正文` 下。

## 优化记录

| 版本 | 日期 | 优化内容 |
|---|---|---|
| v1.0 | 2026-06-04 | 初始版本 |
| v1.1 | 2026-06-04 | 增加自动分类、去重和保存位置判断规则 |
| v1.2 | 2026-06-04 | 按新版 Prompt_Template 精简，仅保留使用经验和优化记录 |
| v1.3 | 2026-06-04 | 增加 Obsidian 与 Codex 同步更新要求 |
| v1.4 | 2026-06-04 | 增加入库后更新索引、触发桌面卡片、GitHub 同步和 Prompt 正文复制规则 |
