---
name: care-recording
description: "CARE 录音转写：处理录音转写文档，提取待办/灵感/关键信息写入多维表格，生成飞书提炼文档。触发场景：处理录音、录音转写、分析转写、这是今天的录音。"
---

# CARE Recording — 录音转写

## 前置

读取 `~/.care-assistant/config.json` 获取 `base_token`、`table_id`、`user_open_id`、`folder_token`。

lark-cli 需要代理：`https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897`。

录音文件目录：`~/.care-assistant/recordings/`，命名 `YYYY-MM-DD_主题描述.docx`。

## 三层输出

### 第一层：多维表格

1. 读取转写内容
2. 读取已有记录用于去重：`+record-list --limit 200`
3. 提取可记录项：
   - 待办（有行动要求）
   - 灵感（点子、计划）
   - 其他（知识、经验、决策）
4. 去重：新记录间互比合并，再与已有记录对比
5. 逐条写入记录表：

```bash
lark-cli base +record-upsert \
  --base-token <base_token> \
  --table-id <table_id> \
  --json '{
    "记录标题": "<title>",
    "来源": "录音",
    "标签": ["<tag>"],
    "详细内容": "<content>",
    "创建日期": "<YYYY-MM-DD>",
    "截止日期": "",
    "完成状态": "未完成",
    "关联文档": ""
  }'
```

6. 待办类创建飞书任务：`lark-cli task +create --summary "<title>" --due "<date>" --assignee "<user_open_id>"`

### 第二层：飞书文档

```bash
lark-cli docs +create \
  --title "录音：<主题>" \
  --folder-token <folder_token> \
  --markdown "<content>"
```

文档结构：

```
## 精炼提炼

### 亮点摘录（callout 高亮块）
### 写作话题（切入点 + 参考段落 + 适合平台）
### 行动要点（表格：行动项 | 优先级）

---

## 原文转写

**重要：保留原始时间戳格式，每个时间戳独占一行。**

输入格式通常是：
```
采访者  00:00你你你你你你对吧，不着急，不着急。
受访者  00:04嗯，没事，我反正我正好也要整理一下到底哪些平台大概是什么样子的。
```

输出时**必须保持这个格式**，每个说话人+时间戳+内容独占一行，不要把多行合并或删除换行。
```

创建后回填所有录音记录的 `关联文档` 字段。

### 第三层：汇报

```
录音处理完成：
- 表格记录 N 条（待办 X / 灵感 Y / 其他 Z）
- 飞书文档已创建：{doc_url}
- 录音文件已归档：~/.care-assistant/recordings/YYYY-MM-DD_主题.docx
```

## 提取原则

- 口语化 → 简洁标题
- 同话题多句 → 合并
- 明确行动 → 待办，模糊想法 → 灵感
- 金句/写作话题 → 放飞书文档不放表格
- 闲聊/重复/语气词 → 不记录
- 宁可标"其他"也不遗漏
