---
name: care-recording
description: "CARE 录音转写：处理录音转写文档，提取待办/灵感/关键信息写入多维表格，生成飞书提炼文档。触发场景：处理录音、录音转写、分析转写、这是今天的录音。"
---

# CARE Recording — 录音转写

## 前置

读取 `~/.care-assistant/config.json` 获取 `base_token`、`table_id`、`user_open_id`、`folder_token`。

lark-cli 需要代理：`https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897`。

**文件路径配置：**
- 录音源文件：用户提供的原文档（只读）
- 本地目录：`/Users/bian/MyWorkspace/Knowledge/Obsidian/V0-MyAntinet/5-DaliyCC/CARE_Assistant/`
- 飞书文件夹：folder_token 指定的飞书云空间文件夹

**命名格式（重要）：**
- 日期格式：YYMMDD（六位数字），如 260418 代表 2026-04-18
- 日录音：`YYMMDD日录音.md`（如 260418日录音.md）
- 主题录音：`YYMMDD_主题.md`（如 260418_太青年运分享.md）

**日期计算原则：**
- 按照录音发生的那一天计算，不是处理日期
- 如果用户没有明确说明日期，必须先询问用户："这个录音是哪一天的？"
- 推算方法：如果录音内容中有时间线索（如"今天"、"明天"），结合用户提供的参考日期计算

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

### 第二层：双端保存（本地 + 飞书）

**步骤顺序：先本地保存，再同步飞书**

**1. 确定日期和文件名：**
- 如果用户没有说明日期，先问："这个录音是哪一天的？"
- 日录音文件名：`YYMMDD日录音.md`
- 主题录音文件名：`YYMMDD_主题.md`

**2. 本地保存（使用 Write 工具）：**

完整路径：`/Users/bian/MyWorkspace/Knowledge/Obsidian/V0-MyAntinet/5-DaliyCC/CARE_Assistant/YYMMDD_主题.md`

**3. 飞书同步（使用 Bash 工具，必须执行）：**

```bash
export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897
lark-cli docs +create \
  --title "录音：YYMMDD_主题" \
  --folder-token <folder_token> \
  --markdown "<content>"
```

**重要：飞书同步是必须执行的步骤，不能跳过。**

文档结构：

```markdown
# 精炼提炼

## 亮点摘录
> 金句1
> 金句2

## 写作话题
| 话题 | 切入点 | 适合平台 |
|------|--------|----------|
| AI教学 | 从反面出发 | 小红书视频 |

## 行动要点
| 行动项 | 类型 | 紧急度 |
|--------|------|--------|
| 明天开会 | 待办 | 高 |

---

## 完整对话记录

**重要：保留原始时间戳格式，每个时间戳独占一行。**

采访者  00:00你你你你你你对吧，不着急，不着急。
受访者  00:04嗯，没事，我反正我正好也要整理一下到底哪些平台大概是什么样子的。
```

**排版要求：**
- `## 完整对话记录` 使用二级标题
- 少用加粗 `**text**`，多用高亮块 `> quote`
- 需要强调的内容用标题（# ##）而非加粗

创建后回填所有录音记录的 `关联文档` 字段。

### 第三层：汇报

```
录音处理完成：
- 表格记录 N 条（待办 X / 灵感 Y / 其他 Z）
- 本地文档：/Users/bian/MyWorkspace/Knowledge/Obsidian/V0-MyAntinet/5-DaliyCC/CARE_Assistant/YYMMDD_主题.md
- 飞书文档：{doc_url}
- 录音源文件：用户提供的原文档
```

## 提取原则

- 口语化 → 简洁标题
- 同话题多句 → 合并
- 明确行动 → 待办，模糊想法 → 灵感
- 金句/写作话题 → 放飞书文档不放表格
- 闲聊/重复/语气词 → 不记录
- 宁可标"其他"也不遗漏
