# CARE 助理 — 关心你的每一个想法

> 基于 [lark-cli](https://github.com/larksuite/cli) 的个人效率助理，参加 [飞书 CLI 创作者大赛](https://waytoagi.feishu.cn/wiki/R4S3w8wTTie04nkYiL6c8rxon4d)。

**说一句话就记录，AI 自动分类，定时整理，待办变飞书任务。**

```
CARE = Capture 随手记 + Auto-sort 自动分 + Review 定期回顾 + Execute 照着做
```

## 这是什么

CARE 助理是一个 Claude Code Skill，通过 lark-cli 操作飞书多维表格、云文档和任务。你在终端说一句话，AI 自动帮你：

1. **记录** — 把你的话写入飞书多维表格
2. **分类** — AI 自动判断是待办、灵感还是其他，打上标签
3. **回顾** — 生成飞书回顾文档，分析方向和建议
4. **执行** — 待办自动创建飞书任务，带截止日期

## lark-cli 使用情况

CARE 助理通过 lark-cli 调用飞书开放平台 API，涉及以下能力：

| lark-cli 命令 | 飞书 API | 使用场景 |
|--------------|---------|---------|
| `lark-cli base +record-list` | 多维表格 · 读取记录 | 去重检查、查看记录、回顾整理 |
| `lark-cli base +record-upsert` | 多维表格 · 写入/更新记录 | 写入记录、更新标签/状态、回填关联文档 |
| `lark-cli base +base-create` | 多维表格 · 创建 Base | 首次 Setup 自动建表 |
| `lark-cli base +table-create` | 多维表格 · 创建数据表 | 首次 Setup 自动建字段 |
| `lark-cli task +create` | 飞书任务 · 创建任务 | 待办类记录自动创建飞书任务 |
| `lark-cli docs +create` | 飞书云文档 · 创建文档 | 录音转写提炼文档、周回顾文档 |
| `lark-cli im +messages-send` | 飞书即时通讯 · 发消息 | Bot 模式回复确认 |
| `lark-cli event +subscribe` | 飞书事件订阅 · WebSocket | Bot 模式接收消息 |
| `lark-cli auth status` | 飞书认证 · 用户信息 | 首次 Setup 获取 open_id |

## 详细功能

### 1. 随手记 (Capture)

**触发词**：记录、待办、灵感、记一下、随手记、帮我记。说了包含时间+动作的句子也会自动触发。

**流程**：
1. AI 提取标题、标签、详细内容、截止日期
2. 读取多维表格已有记录，语义去重
3. 写入飞书多维表格（`lark-cli base +record-upsert`）
4. 待办类自动创建飞书任务（`lark-cli task +create`）

**标签体系**：
- 类型标签：待办、灵感、其他
- 主题标签：AI、社群、内容创作、备孕、线下
- 一条记录可叠加多个标签（如"待办 + AI"）

**智能分类**：AI 根据内容自动判断标签。有时间或行动要求 → 待办，想法闪现 → 灵感，其他 → 其他。

**语义去重**：写入前对比已有记录的标题和内容，核心含义相同则跳过。支持时间维度比较——"明天开会"和"后天开会"不会误判为重复。

```
你：明天10点开会
AI：已记录 [待办]：明天10点开会（已创建飞书任务）

你：灵感 做一个自动整理录音的工具
AI：已记录 [灵感]：做一个自动整理录音的工具
```

### 2. 录音转写 (Recording)

**触发词**：处理录音、录音转写、分析转写。或直接给一个转写文档。

**三层输出**：

| 层 | 输出 | lark-cli 命令 |
|----|------|--------------|
| 第一层 | 多维表格记录（待办/灵感/其他） | `base +record-upsert` 逐条写入 |
| 第二层 | 飞书文档（精炼提炼 + 原文存档） | `docs +create` 创建文档 |
| 第三层 | 汇报统计 | 终端输出 |

**飞书文档结构**：
- 精炼提炼：亮点摘录（callout 高亮）→ 写作话题（切入点+适合平台）→ 行动要点（表格）
- 原文转写：完整内容保持原样

**额外动作**：
- 待办类自动创建飞书任务（`lark-cli task +create`）
- 创建飞书文档后，自动回填所有录音记录的"关联文档"字段

**文件管理**：录音文件统一存放在 `~/.care-assistant/recordings/`，自动归档和重命名。

### 3. 回顾整理 (Review)

**触发词**：回顾一下、整理一下、周回顾、看看这周做了什么、查看记录、有多少待办。

**两种模式**：

| 模式 | 触发 | 动作 |
|------|------|------|
| 查看模式 | "查看记录"、"有多少待办" | 读表格 → 按维度汇总展示 |
| 回顾模式 | "回顾"、"整理"、"周回顾" | 读表格 → 分析 → 生成飞书回顾文档 |

**回顾文档结构**（`lark-cli docs +create`）：
- 概览：记录数、待办完成情况、文章收藏数
- 待办跟进：表格展示状态（已过期/进行中/已完成）
- 灵感回顾：按主题分组，每条附点评
- 方向观察：标签分布分析
- 下期建议：2-3 条可执行建议

**整理动作**（"整理"时额外执行）：
- 标签不准的自动修正（`base +record-upsert` 只改标签）
- 过期待办状态更新为"进行中"

### 4. Bot 模式 (Always-On)

除了在 Claude Code 终端交互，CARE 还可以作为飞书机器人 7x24 后台运行。

```bash
nohup bash bot-handler.sh > /tmp/care-bot.log 2>&1 &
tail -f /tmp/care-bot.log   # 查看日志
```

**Bot 模式工作方式**：

| 步骤 | lark-cli 命令 | 说明 |
|------|--------------|------|
| 监听消息 | `event +subscribe --as bot` | WebSocket 接收飞书消息 |
| 语义去重 | `base +record-list` + `dedup.py` | 写入前对比已有记录 |
| 链接收藏 | `base +record-upsert` → 文章表 | 检测到链接自动走文章收藏表 |
| 写入记录 | `base +record-upsert` → 记录表 | 普通消息写入记录表 |
| 智能标签 | 关键词匹配 | 时间词 → 待办，想法词 → 灵感 |
| 创建任务 | `task +create` | 待办类自动创建飞书任务 |
| 回复确认 | `im +messages-send` | 发送"已记录 [标签]：xxx" |
| 断线重连 | 自动 | 5 秒后重新连接 |

### 5. 首次 Setup

首次使用时自动检测配置，引导建表：

| 步骤 | lark-cli 命令 | 说明 |
|------|--------------|------|
| 获取用户信息 | `auth status` | 提取 open_id |
| 创建多维表格 | `base +base-create` | 命名"CARE 助理" |
| 创建记录表 | `base +table-create` | 含 8 个字段：标题、标签、内容、日期、状态等 |
| 创建文章收藏表 | `base +table-create` | 含 7 个字段：标题、链接、备注、标签等 |

配置保存在 `~/.care-assistant/config.json`。

## 架构

```
用户 ──说话──┬─▶ Claude Code (Skill 模式) ──交互式操作
             │        │
             │        ├─ care-assistant  (路由：识别意图)
             │        ├─ care-capture    (记录：写入表格 + 创建任务)
             │        ├─ care-review     (回顾：分析 + 生成文档)
             │        └─ care-recording  (录音：提取 + 文档 + 任务)
             │
             └─▶ Bot 模式 ──7x24 后台运行
                      │
                      ├─ bot-handler.sh  (消息处理 + 自动重连)
                      ├─ dedup.py        (语义去重引擎)
                      └─ 智能标签        (关键词匹配)
```

### 数据结构

**记录表** — 日常记录、待办、灵感

| 字段 | 类型 | 说明 |
|------|------|------|
| 记录标题 | 文本 | 内容摘要 |
| 标签 | 多选 | 待办 / 灵感 / 其他 / AI / 社群 / 内容创作 / 备孕 / 线下 |
| 详细内容 | 文本 | 完整内容 |
| 创建日期 | 日期 | YYYY-MM-DD |
| 完成状态 | 单选 | 未完成 / 进行中 / 已完成 |
| 截止日期 | 日期 | 仅待办类 |
| 来源 | 单选 | 终端 / 飞书对话 / 录音 |
| 关联文档 | 链接 | 飞书文档 URL |

**文章收藏表** — 链接收藏（Bot 模式使用）

| 字段 | 类型 | 说明 |
|------|------|------|
| 标题 | 文本 | 文章标题或链接描述 |
| 链接 | URL | 文章链接 |
| 备注 | 文本 | 补充说明 |
| 标签 | 多选 | AI / 效率 / 产品 / 技术 / 商业 / 其他 |
| 来源 | 单选 | 终端 / 飞书对话 / 浏览器 |
| 收藏时间 | 日期 | 收藏时间 |

## 快速开始

### 前置条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 已安装
- [lark-cli](https://github.com/larksuite/cli) 已安装并配置好飞书应用
- 飞书应用权限：多维表格读写、云文档创建、任务创建、即时通讯

### 安装

```bash
git clone https://github.com/asiyoua/care-assistant.git
cp -r care-assistant ~/.claude/skills/care-assistant
mkdir -p ~/.care-assistant
```

首次使用时在 Claude Code 中说任何话即可自动触发 Setup。

### 文件结构

```
care-assistant/
├── README.md                          # 本文件
├── SKILL.md                           # 主路由 skill
├── bot-handler.sh                     # 飞书机器人后台脚本
├── dedup.py                           # 语义去重引擎
└── references/
    ├── setup.md                       # 首次配置流程
    ├── care-capture.md                # 随手记 skill
    ├── care-review.md                 # 回顾整理 skill
    └── care-recording.md              # 录音转写 skill
```

## License

MIT
