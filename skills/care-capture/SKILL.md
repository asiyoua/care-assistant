---
name: care-capture
description: "CARE 随手记：把用户的话直接写入飞书多维表格。只要用户说了包含时间+动作的句子（如'明天10点开会'、'下午三点有个会'、'周五之前交报告'），或者表达了要记事、待办、灵感的意图，就必须触发此 skill 直接写入表格，不要只是回复确认或问用户要做什么。触发词：记录、待办、灵感、记一下、随手记、帮我记、开会、开会、会议、出差、提交、完成、复习、准备、去、做。只要句子结构是'时间+事件'或'要做某事'，就触发。不涉及网络访问。"
---

# CARE Capture — 随手记

读取 `~/.care-assistant/config.json` 获取 `base_token`、`table_id`、`user_open_id`。

lark-cli 需要代理：`https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897`。

## 你的任务

用户说了任何值得记录的话，你直接写入表格。不要问用户"需要我做什么"，不要只是确认收到，直接执行以下流程。

## 提取

- **title**：内容摘要（超50字精简）
- **tags**：类型标签，从待办/灵感/其他中选择一个
- **content**：完整内容
- **due_date**：截止日期（仅待办，无法判断时问用户）

时间推断：今天下午3点 → 今天日期，明天 → 明天，后天 → 后天，无具体时间 → 当天。

## 去重

```bash
# 使用 bot API 读取已有记录（按字段名，不依赖顺序）
lark-cli api GET --as bot "/open-apis/bitable/v1/apps/<base_token>/tables/<table_id>/records?limit=200" | jq '.data.items[].fields'
```

核心含义相同则跳过。

## 写入

```bash
lark-cli base +record-upsert \
  --base-token <base_token> \
  --table-id <table_id> \
  --json '{
    "title": "<title>",
    "source": "终端",
    "tags": ["<tag1>","<tag2>"],
    "content": "<content>",
    "created_date": "<YYYY-MM-DD>",
    "due_date": "<YYYY-MM-DD 或 \"\">",
    "status": "未完成",
    "related_doc": ""
  }'
```

## 待办 → 飞书任务

```bash
lark-cli task +create --summary "<title>" --due "<date>" --assignee "<user_open_id>"
```

## 回复

`已记录 [标签]：标题内容`
