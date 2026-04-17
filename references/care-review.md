---
name: care-review
description: "CARE 回顾整理：分析多维表格记录，生成飞书回顾文档。触发场景：回顾一下、整理一下、周回顾、看看这周做了什么、查看记录、有多少待办、整理记录。"
---

# CARE Review — 回顾整理

## 前置

读取 `~/.care-assistant/config.json` 获取 `base_token`、`table_id`、`article_table_id`、`user_open_id`、`folder_token`。

lark-cli 需要代理：`https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897`。

## 查看模式

用户说"查看记录"、"有多少待办"时：

```bash
lark-cli base +record-list --base-token <base_token> --table-id <table_id> --limit 200
```

按用户关心的维度（标签/完成状态/时间）汇总展示。不需要生成文档，直接回复即可。

## 回顾模式

用户说"回顾"、"整理"、"周回顾"时，生成飞书回顾文档。

### 1. 读取记录

```bash
lark-cli base +record-list --base-token <base_token> --table-id <table_id> --limit 200
```

同时读文章表。默认最近 7 天，用户可指定范围。

### 2. 分析

- 待办：检查完成状态，标注已过期/进行中/已完成
- 灵感：按主题分组，点评进展和下一步
- 标签分布：发现关注方向

### 3. 生成飞书文档

```bash
lark-cli docs +create \
  --title "CARE 周回顾：MM.DD - MM.DD" \
  --folder-token <folder_token> \
  --markdown "<content>"
```

文档结构：

```
## 概览
新增记录 N 条（待办 X / 灵感 Y / 其他 Z）、新增文章 P 篇

## 待办跟进
表格：待办 | 截止日期 | 状态 | 关联

## 灵感回顾
按主题分组，每条附点评

## 方向观察
标签分布分析

## 下期建议
2-3 条可执行建议
```

### 4. 整理动作（用户说"整理"时额外执行）

- 标签不准的更新（`+record-upsert` 只改标签）
- 待办未设截止日期的，推断或标记
- 过期待办更新为"进行中"

### 5. 汇报

```
回顾文档已生成：{doc_url}
- 本期 N 条记录，X 条待办已完成，Y 条灵感待行动
- 过期待办 Z 条，建议关注
```
