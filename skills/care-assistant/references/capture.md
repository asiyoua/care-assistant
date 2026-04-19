# Capture — 随手记 + 文章收藏

## 判断类型

| 用户输入 | 类型 | 目标表 |
|---------|------|--------|
| 包含链接（http/https） | 文章收藏 | 文章收藏表（`article_table_id`） |
| 其他所有内容 | 记录 | 记录表（`table_id`） |

## 文章收藏（链接类）

**不抓取页面内容。** 直接保存链接和用户描述。

1. 提取 URL 和描述（用户的话去掉 URL 就是描述）
2. 检查文章表是否已收藏过该链接（`+record-list` on `article_table_id`）
3. 写入文章收藏表：

```bash
lark-cli base +record-upsert \
  --base-token <base_token> \
  --table-id <article_table_id> \
  --json '{"标题":"<描述或域名>","链接":"<url>","备注":"","标签":["其他"],"来源":"终端","收藏时间":"<YYYY-MM-DD>"}'
```

4. 回复：`已收藏：<标题>`

## 记录（非链接类）

### 1. 提取字段

- **title**：内容摘要（超50字要精简）
- **tags**：从 待办/灵感/其他 中选一个类型标签
- **content**：完整内容（简短时可以和 title 一样）
- **due_date**：截止日期（仅待办需要，无法判断时问用户）

时间推断：明天 → 明天日期，后天 → 后天日期，提及日期但无时间 → 当天。

### 2. 去重

```bash
lark-cli base +record-list --base-token <base_token> --table-id <table_id> --limit 200
```

对比"记录标题"和"详细内容"，核心含义相同则跳过。时间不同但内容相同也算重复。

### 3. 写入记录表

```bash
lark-cli base +record-upsert \
  --base-token <base_token> \
  --table-id <table_id> \
  --json '{
    "记录标题": "<title>",
    "来源": "终端",
    "标签": ["<tag1>", "<tag2>"],
    "详细内容": "<content>",
    "创建日期": "<YYYY-MM-DD>",
    "截止日期": "<YYYY-MM-DD 或空字符串>",
    "完成状态": "未完成",
    "关联文档": ""
  }'
```

### 4. 待办 → 创建飞书任务

标签含"待办"时：

```bash
lark-cli task +create \
  --summary "<title>" \
  --due "<YYYY-MM-DD>" \
  --assignee "<user_open_id>"
```

### 5. 回复

`已记录 [标签]：标题内容`

待办类额外说：截止日期 + 已创建飞书任务。
