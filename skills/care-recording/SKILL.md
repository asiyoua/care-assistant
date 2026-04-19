---
name: care-recording
description: "CARE 录音转写：处理录音转写文档，提取待办/灵感/关键信息写入多维表格，生成飞书提炼文档。触发场景：处理录音、录音转写、分析转写、这是今天的录音。"
---

# CARE Recording — 录音转写

## 前置

**读取配置文件：**
```bash
CONFIG_FILE="$HOME/.care-assistant/config.json"
```

从配置中读取：
- `base_token`: 飞书多维表格 Base Token
- `table_id`: 记录表 ID
- `user_open_id`: 用户 Open ID
- `folder_token`: 飞书文件夹 Token
- `recordings_dir`: 已处理录音文档存放目录
- `output_dir`: 本地输出目录

**环境变量：**
```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
```

**文件路径配置（从 config.json 读取）：**
- 录音源文件：用户提供的原文档（只读）
- 处理后移动：`$recordings_dir/`（代表已处理）
- 本地输出目录：`$output_dir/`
- 飞书文件夹：$folder_token 指定的飞书云空间文件夹

**处理开始时：先移动录音文档到 recordings 文件夹**
- 使用 `mv` 命令将用户提供的录音文档移动到 `$recordings_dir/`
- 确保目标文件夹存在：`mkdir -p "$recordings_dir"`
- 移动代表文档已处理，避免重复处理

**命名格式（重要）：**
- 日期格式：YYMMDD（六位数字），如 260418 代表 2026-04-18
- 日录音：`YYMMDD日录音.md`（如 260418日录音.md）
- 主题录音：`YYMMDD_主题.md`（如 260418_太青年运分享.md）

**日期计算原则：**
- 按照录音发生的那一天计算，不是处理日期
- 如果用户没有明确说明日期，必须先询问用户："这个录音是哪一天的？"
- 推算方法：如果录音内容中有时间线索（如"今天"、"明天"），结合用户提供的参考日期计算

## 执行流程（必须按顺序）

**⚠️ 严格执行以下顺序，不可跳过任何步骤：**

0. **移动录音文档到 recordings 文件夹**（预处理）
   - 创建目标文件夹：`mkdir -p "$recordings_dir"`
   - 移动用户提供的文档到该文件夹：`mv "<源文件>" "$recordings_dir/"`

1. **先提取待办和灵感，写入飞书表格**（第一层：多维表格）
2. **再生成处理后的文档，保存到本地**（第二层：双端保存 - 本地）
3. **最后同步到飞书文档**（第二层：双端保存 - 飞书）
4. **汇报处理结果**（第三层）

**完成步骤0后，才能进入步骤1。完成步骤1后，才能进入步骤2。**

---

## 三层输出

### 第一层：多维表格（必须首先执行）

1. 读取转写内容
2. 读取已有记录用于去重：

```bash
# 使用 bot API 读取（按字段名，不依赖顺序）
lark-cli api GET --as bot "/open-apis/bitable/v1/apps/$base_token/tables/$table_id/records?limit=200"
```

3. 提取可记录项：
   - 待办（有行动要求）
   - 灵感（点子、计划）
   - 其他（知识、经验、决策）
4. 去重：新记录间互比合并，再与已有记录对比
5. 逐条写入记录表：

```bash
lark-cli base +record-upsert \
  --base-token $base_token \
  --table-id $table_id \
  --json '{
    "title": "<title>",
    "source": "录音",
    "tag": ["<tag>"],
    "content": "<content>",
    "created_date": "<YYYY-MM-DD>",
    "due_date": "",
    "status": "未完成",
    "related_doc": ""
  }'
```

6. 待办类创建飞书任务：`lark-cli task +create --summary "<title>" --due "<date>" --assignee $user_open_id`

### 第二层：双端保存（本地 + 飞书）

**步骤顺序：先本地保存，再同步飞书**

**1. 确定日期和文件名：**
- 如果用户没有说明日期，先问："这个录音是哪一天的？"
- 日录音文件名：`YYMMDD日录音.md`
- 主题录音文件名：`YYMMDD_主题.md`

**2. 本地保存（使用 Write 工具）：**

⚠️ **必须使用以下绝对路径（从配置读取），不能使用相对路径：**

```
$output_dir/YYMMDD_主题.md
```

**确认**：文件必须保存在 `$output_dir` 配置指定的目录下。

**3. 飞书同步（使用 Bash 工具，必须执行）：**

```bash
export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897
lark-cli docs +create \
  --title "录音：YYMMDD_主题" \
  --folder-token $folder_token \
  --markdown "<content>"
```

**4. 回填关联文档（必须执行）：**

创建飞书文档后，获取返回的 `doc_url`，然后回填所有本次录音写入的记录。

⚠️ **执行方式：在提取待办/灵感时，记录下写入的记录标题列表，然后通过标题匹配回填**

```bash
# 假设已保存本次写入的记录标题到变量（在步骤1中记录）
# 本次_titles 包含所有刚写入记录的标题，用 | 分隔
# 例如：本次_titles="买新鼠标|开会|复习"

# 使用 bot API 获取记录并回填
for title in $(echo "$本次_titles" | tr '|' '\n'); do
  # 通过标题查找 record_id
  record_id=$(lark-cli api GET --as bot \
    "/open-apis/bitable/v1/apps/$base_token/tables/$table_id/records?limit=200" | \
    jq -r ".data.items[] | select(.fields.title == \"$title\") | .record_id")
  
  # 回填关联文档
  if [ -n "$record_id" ]; then
    lark-cli base +record-upsert \
      --base-token $base_token \
      --table-id $table_id \
      --record-id "$record_id" \
      --json "{\"related_doc\": \"$doc_url\"}"
  fi
done
```

**简化方式（如果标题匹配复杂）：**

如果标题匹配困难，可以在步骤1写入记录时保存返回的 record_id（需要改用 API 方式写入），然后在步骤4直接用这些 ID 回填。

**重要：**
- 飞书同步是必须执行的步骤，不能跳过
- 回填关联文档是必须执行的步骤，确保记录与文档关联
- 务必记录下步骤1中写入的所有记录，以便步骤4准确回填

**文档结构（必须详细，不能简略）：**

```markdown
# 录音：主题描述

## 来源

简短描述录音背景、对话对象和主要讨论内容（1-2句话）。

---

## 好段落摘录

<callout emoji="💡" background-color="light-blue">

**小标题（概括核心观点）**

> "引用录音中的原文段落，保留说话人的原话和语气。"

补充说明：对这个观点的解读或延伸思考。
</callout>

<callout emoji="💡" background-color="light-blue">

**另一个小标题**

> "引用另一段有价值的原文。"

补充说明。
</callout>

（继续添加其他重要段落，至少3-5个）

---

## 写作话题灵感

### 话题1：话题标题

**切入点**：从什么角度切入，为什么这个角度有价值

**可参考段落**：
> "引用录音中支持这个话题的原话"

**适合发布平台**：小红书 / 公众号 / 知乎等（说明为什么适合）

---

### 话题2：另一个话题标题

**切入点**：...

**可参考段落**：
> "引用原文"

**适合发布平台**：...

（继续添加其他可写作的话题）

---

## 行动要点汇总

| 事项 | 优先级 | 备注 |
|------|--------|------|
| 具体行动项1 | 高/中/低 | 详细说明 |
| 具体行动项2 | 高/中/低 | 详细说明 |
| ... | ... | ... |

（至少5-7个行动项）

---

# 原文转写

采访者  00:00原文内容...
受访者  00:04原文内容...
```

**排版要求：**
- 摘录部分必须使用 `<callout>` 格式，包含 emoji、背景色、小标题
- 引用原文用 `>` quote 格式，保留说话人语气
- 每个写作话题必须包含：切入点、可参考段落、适合发布平台
- 行动要点用表格，包含事项、优先级、备注三列
- `# 原文转写` 使用一级标题（与前面的 `# 录音：` 分隔）
- **原文转写部分必须保留原始时间戳格式，每个时间戳独占一行**

**内容要求：**
- 摘录不能太简略，每个摘录要有完整的小标题、引用、解读
- 写作话题要有实际可操作性，不能泛泛而谈
- 行动要点要具体到可以执行的程度
- 总体内容要详细到能指导后续行动的程度

创建后回填所有录音记录的 `related_doc` 字段。

### 第三层：汇报

**必须包含以下所有信息：**

```
📊 录音处理完成

✅ 飞书表格：
   - 新增记录 N 条
   - 待办 X 条（已创建飞书任务）
   - 灵感 Y 条
   - 其他 Z 条

📄 双端文档：
   - 本地：$output_dir/YYMMDD_主题.md
   - 飞书：{doc_url}

📝 源文件：用户提供的原文档路径
```

## 提取原则

- 口语化 → 简洁标题
- 同话题多句 → 合并
- 明确行动 → 待办，模糊想法 → 灵感
- 金句/写作话题 → 放飞书文档不放表格
- 闲聊/重复/语气词 → 不记录
- 宁可标"其他"也不遗漏
