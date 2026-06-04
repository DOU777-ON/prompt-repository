---
title: Codex-自动分类保存规则
category: high-frequency
status: favorite
version: v1.4
tags:
  - codex
  - auto-classification
  - prompt-intake
  - prompt-repository
created: 2026-06-04
updated: 2026-06-04
role: Prompt工程师
level: L5
source: internal
---

# Codex-自动分类保存规则

## 使用经验

- 暂无。
- 保存或更新 Prompt 时，应以当前 Obsidian 库中的 README、模板和高频工作流为准。
- 如果用户修改了目录名称、模板结构、分类规则或生命周期规则，Codex 必须同步更新相关入库和调用提示词。
- 高频工作流统一保存到 `Prompts/High-Frequency Workflows`。
- 普通 Prompt 文件遵循当前 `Prompt_Template.md`，必须包含 YAML、标题、`## Prompt 正文`、`## 使用经验`、`## 优化记录`。
- 入库前先查重；发现高度相似内容时更新原文件，不创建同义重复文件。
- 入库后运行 `scripts/update_index.ps1`，更新 README 索引。
- 可直接被调用的提示词正文应放在 `## Prompt 正文` 下，便于检索和复用。
- 没有完整 Prompt 正文的内容只能作为 `draft` 放入测试区；专业场景默认只允许 `testing` 或 `validated`。
- `draft` 是想法、片段或未完成文本；`testing` 是可执行但未验证；`validated` 是至少用过一次并记录经验；`favorite` 是高频稳定资产或规则工作流。

## 优化记录

| 版本 | 日期 | 优化内容 |
|---|---|---|
| v1.0 | 2026-06-04 | 初始版本 |
| v1.1 | 2026-06-04 | 按新版 Prompt_Template 精简，仅保留使用经验和优化记录 |
| v1.2 | 2026-06-04 | 增加 Obsidian 与 Codex 同步更新规则 |
| v1.3 | 2026-06-04 | 增加入库查重、索引刷新和 Prompt 正文提取规则 |
| v1.4 | 2026-06-04 | 统一 Prompt 正文结构和质量门槛 |
