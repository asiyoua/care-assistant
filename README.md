# CARE 助理 — 关心你的每一个想法

> 基于 [lark-cli](https://github.com/larksuite/cli) 的个人效率助理，参加 [飞书 CLI 创作者大赛](https://waytoagi.feishu.cn/wiki/R4S3w8wTTie04nkYiL6c8rxon4d)。

**说一句话就记录，AI 自动分类，定时整理，待办变飞书任务。**

```
CARE = Capture 随手记 + Auto-sort 自动分 + Review 定期回顾 + Execute 照着做
```

---

## ⚠️ 重要：配置方式选择

### 🤖 非技术人员：让 AI 帮你配置

**如果你不是技术人员，或者不想手动配置飞书应用和机器人：**

把整个 GitHub 仓库直接发给 Claude Code、ChatGPT 或其他 AI 工具，说：

> "请帮我一步步配置 CARE 助理，包括飞书应用和机器人设置。从安装开始，到最后可以使用的每一步都要详细说明。"

AI 会引导你完成所有配置：
- ✅ 安装 Claude Code 和 lark-cli
- ✅ 创建飞书应用和配置权限
- ✅ 创建飞书机器人
- ✅ 配置机器人事件订阅
- ✅ 获取所有需要的 token 和 ID
- ✅ 写入配置文件
- ✅ 测试是否配置成功

**遇到 AI 无法自动完成的步骤**，AI 会明确告诉你需要手动操作什么，跟着它的指示做就可以了。

### 📖 技术人员：自己配置

如果你想了解具体配置过程或自己手动配置，继续阅读下面的"快速开始"章节。

---

## 这是什么

CARE 助理是一个 Claude Code Skill，通过 lark-cli 操作飞书多维表格、云文档和任务。你在终端说一句话，AI 自动帮你：

1. **记录** — 把你的话写入飞书多维表格
2. **分类** — AI 自动判断是待办、灵感还是其他，打上标签
3. **回顾** — 生成飞书回顾文档，分析方向和建议
4. **执行** — 待办自动创建飞书任务，带截止日期

## 适用于什么场景

CARE 助理适合这些场景：

| 场景 | 说明 | 示例 |
|------|------|------|
| **灵感捕捉** | 突然有个想法，快速记下来 | "灵感：做一个自动整理录音的工具" |
| **待办管理** | 有时间要求的任务，自动创建飞书任务 | "明天下午3点开会" |
| **录音转写** | 把长对话转写成结构化文档，提取待办和灵感 | 发一个转写文档说"处理录音" |
| **定期回顾** | 每周看看记录了什么，发现方向和趋势 | "回顾一下这周" |
| **持续记录** | 7x24 后台运行，飞书聊天中随手发消息就记录 | 启动 Bot 模式，飞书里发消息 |

## 核心功能

### 1. 随手记 (Capture)

**触发方式**：说"记录"、"待办"、"灵感"等词，或直接说"时间+事件"的句子

```
你：明天10点开会
AI：已记录 [待办]：明天10点开会（已创建飞书任务）

你：灵感 做一个自动整理录音的工具
AI：已记录 [灵感]：做一个自动整理录音的工具
```

**智能处理**：
- AI 提取标题、标签、详细内容、截止日期
- 语义去重：核心含义相同则跳过
- 自动分类：有时间或行动要求 → 待办，想法 → 灵感
- 待办类自动创建飞书任务

### 2. 录音转写 (Recording)

**触发方式**：说"处理录音"、"录音转写"，或直接给一个转写文档

**三层输出**：

| 层 | 内容 | 说明 |
|----|------|------|
| 第一层 | 飞书表格记录 | 提取待办/灵感/其他，逐条写入多维表格 |
| 第二层 | 飞书文档 | 生成结构化提炼文档（亮点摘录 + 写作话题 + 行动要点） |
| 第三层 | 汇报统计 | 告知处理结果 |

**文档结构示例**：

```markdown
# 录音：主题描述

## 来源
简短描述录音背景

## 好段落摘录
<callout emoji="💡" background-color="light-blue">
**小标题**
> "引用原文"
补充说明
</callout>

## 写作话题灵感
### 话题1：标题
**切入点**：从什么角度切入
**可参考段落**：> "引用原文"
**适合发布平台**：小红书/公众号

## 行动要点汇总
| 事项 | 优先级 | 备注 |
|------|--------|------|
| 行动项1 | 高 | 详细说明 |

# 原文转写
[完整转写内容，保留时间戳]
```

**文件管理**：录音文件自动移到 `~/.care-assistant/recordings/`，已处理归档。

### 3. 回顾整理 (Review)

**触发方式**：说"回顾一下"、"周回顾"、"看看这周做了什么"

**两种模式**：

| 模式 | 触发词 | 产出 |
|------|--------|------|
| 查看模式 | "查看记录"、"有多少待办" | 快速统计，直接展示 |
| 回顾模式 | "回顾"、"周回顾" | 生成飞书回顾文档 |

**回顾文档包含**：
- 概览：记录数、待办完成情况
- 待办跟进：标注已过期/进行中/已完成
- 灵感回顾：按主题分组点评
- 方向观察：标签分布分析
- 下期建议：2-3 条可执行建议

### 4. Bot 模式 (7x24 后台运行)

**启动方式**：

```bash
nohup bash bot-handler.sh > /tmp/care-bot.log 2>&1 &
tail -f /tmp/care-bot.log   # 查看日志
```

**功能**：
- 7x24 监听飞书消息
- 自动记录、分类、去重
- 检测链接自动走文章收藏表
- 待办类自动创建飞书任务
- 自动回复确认
- 断线自动重连

## lark-cli 使用详解

CARE 助理通过 lark-cli 调用飞书开放平台 API，以下是具体使用情况：

### 多维表格操作

| lark-cli 命令 | 飞书 API | 在 CARE 中的用途 | 使用位置 |
|--------------|---------|-----------------|---------|
| `lark-cli base +record-list` | 读取记录 | 去重检查、查看记录、回顾整理 | care-capture, care-review, 录音转写 |
| `lark-cli base +record-upsert` | 写入/更新记录 | 写入新记录、更新标签/状态、回填关联文档 | 所有功能 |
| `lark-cli base +base-create` | 创建 Base | 首次使用自动建表 | setup |
| `lark-cli base +table-create` | 创建数据表 | 首次使用自动创建字段 | setup |
| `lark-cli api GET/DELETE` | API 调用 | 自动去重（获取 record_id 并删除重复） | auto-dedup.py |

### 任务操作

| lark-cli 命令 | 飞书 API | 在 CARE 中的用途 | 使用位置 |
|--------------|---------|-----------------|---------|
| `lark-cli task +create` | 创建任务 | 待办类记录自动创建飞书任务（带截止日期） | care-capture, 录音转写 |

### 文档操作

| lark-cli 命令 | 飞书 API | 在 CARE 中的用途 | 使用位置 |
|--------------|---------|-----------------|---------|
| `lark-cli docs +create` | 创建文档 | 录音转写提炼文档、周回顾文档 | care-recording, care-review |
| `lark-cli docs +fetch` | 获取文档 | 首次使用获取示例文档样式 | setup |

### 即时通讯操作

| lark-cli 命令 | 飞书 API | 在 CARE 中的用途 | 使用位置 |
|--------------|---------|-----------------|---------|
| `lark-cli im +messages-send` | 发送消息 | Bot 模式回复确认 | bot-handler.sh |

### 事件订阅

| lark-cli 命令 | 飞书 API | 在 CARE 中的用途 | 使用位置 |
|--------------|---------|-----------------|---------|
| `lark-cli event +subscribe` | WebSocket 订阅 | Bot 模式接收飞书消息 | bot-handler.sh |

### 认证

| lark-cli 命令 | 飞书 API | 在 CARE 中的用途 | 使用位置 |
|--------------|---------|-----------------|---------|
| `lark-cli auth status` | 获取用户信息 | 首次使用获取 open_id | setup |

## 数据结构

### 记录表 — 日常记录、待办、灵感

| 字段 | 类型 | 说明 |
|------|------|------|
| 记录标题 | 文本 | 内容摘要 |
| 标签 | 多选 | 待办 / 灵感 / 其他 / AI / 社群 / 内容创作 / 线下 / 效率工具 |
| 详细内容 | 文本 | 完整内容 |
| 创建日期 | 日期 | YYYY-MM-DD |
| 完成状态 | 单选 | 未完成 / 进行中 / 已完成 |
| 截止日期 | 日期 | 仅待办类 |
| 来源 | 单选 | 终端 / 飞书对话 / 录音 |
| 关联文档 | 链接 | 飞书文档 URL |

### 文章收藏表 — 链接收藏（Bot 模式）

| 字段 | 类型 | 说明 |
|------|------|------|
| 标题 | 文本 | 文章标题或链接描述 |
| 链接 | URL | 文章链接 |
| 备注 | 文本 | 补充说明 |
| 标签 | 多选 | AI / 效率 / 产品 / 技术 / 商业 / 其他 |
| 来源 | 单选 | 终端 / 飞书对话 / 浏览器 |
| 收藏时间 | 日期 | 收藏时间 |

## 快速开始

> 💡 **提示**：如果你是非技术人员，请回到文章开头，使用"让 AI 帮你配置"的方式。

### 步骤 1：安装 Claude Code

Claude Code 是 Anthropic 出品的 AI 编程助手，CARE 助理运行在它上面。

1. 访问 [Claude Code 官网](https://docs.anthropic.com/en/docs/claude-code) 下载安装
2. 安装后打开 Claude Code，登录你的 Anthropic 账号
3. 首次使用需要订阅（有免费额度）

### 步骤 2：安装 lark-cli

lark-cli 是飞书官方的命令行工具，用于操作飞书开放平台 API。

```bash
# 使用 npm 安装（需要 Node.js）
npm install -g @larksuite/cli

# 验证安装
lark-cli --version
```

### 步骤 3：创建飞书应用

1. 打开[飞书开放平台](https://open.feishu.cn/)
2. 点击"创建企业自建应用"
3. 填写应用信息：
   - 应用名称：CARE 助理
   - 应用描述：个人效率助理，基于 lark-cli
4. 创建后进入应用

### 步骤 4：配置应用权限

在飞书应用管理后台，配置以下权限：

**必需权限（按功能分类）：**

| 功能 | 权限项 | 说明 |
|------|--------|------|
| **多维表格** | bitable:app:readonly | 读取多维表格 |
| | bitable:app | 读写多维表格 |
| | bitable:app:record:create | 创建记录 |
| | bitable:app:record:delete | 删除记录（去重用） |
| **云文档** | docs:doc:create | 创建文档 |
| **任务** | task:task:create | 创建任务 |
| **即时通讯** | im:message | 发送消息（Bot 模式确认用） |
| **事件订阅** | - | 用于接收飞书消息（Bot 模式） |

**配置方法**：
1. 在应用管理后台，左侧点击"权限管理"
2. 搜索并添加上述权限
3. 每个权限都需要点击"申请权限"，填写申请理由："用于 CARE 个人效率助理"

### 步骤 5：创建飞书机器人（Bot 模式可选）

如果你想使用 Bot 模式（7x24 后台运行，飞书聊天中直接记录），需要创建机器人：

1. 在飞书应用管理后台，左侧点击"机器人"
2. 点击"创建机器人"
3. 机器人名称：CARE 助理 Bot
4. 机器人描述：个人效率助理，帮你记录待办和灵感
5. 创建后获取机器人 App ID 和 App Secret

**配置机器人事件订阅**：

1. 在飞书应用管理后台，左侧点击"事件订阅"
2. 选择"添加事件"
3. 订阅以下事件：
   - im.message.receive_v1（接收消息）
4. 选择订阅版本为"强推"（确保实时性）
5. 填写请求加密密钥（随便输入一个字符串，自己记住即可）
6. 点击"提交"完成订阅

**设置机器人接收消息**：

1. 在机器人页面，找到"事件设置"
2. 配置接收消息的 URL：
   - 开发环境：可以暂时留空，使用 bot-handler.sh 的轮询模式
   - 生产环境：需要配置服务器接收事件（略，可先用轮询模式）

### 步骤 6：获取凭证信息

**获取 App ID、App Secret、Encrypt Key、Verification Token**（Bot 模式需要）：

在飞书应用管理后台：
- 凭证与基本信息 → App ID
- 凭证与基本信息 → App Secret（点击"查看"，复制保存）
- 事件订阅 → Encrypt Key（点击"查看"，复制保存）
- 事件订阅 → Verification Token（点击"查看"，复制保存）

### 步骤 7：安装和配置 CARE 助理

```bash
# 1. 克隆仓库
git clone https://github.com/asiyoua/care-assistant.git
cd care-assistant

# 2. 安装技能
mkdir -p ~/.claude/skills/
cp -r skills/* ~/.claude/skills/

# 3. 创建配置目录
mkdir -p ~/.care-assistant

# 4. 复制配置模板
cp config.example.json ~/.care-assistant/config.json
```

### 步骤 8：写入配置信息

编辑 `~/.care-assistant/config.json`，填入你的信息：

```bash
nano ~/.care-assistant/config.json
```

**获取各项配置信息**：

#### 8.1 获取 user_open_id

```bash
lark-cli auth status
```

输出中的 `user_id` 就是 `user_open_id`。

#### 8.2 创建多维表格获取 base_token 和 table_id

```bash
# 创建多维表格 Base
lark-cli base +base-create "CARE 助理"

# 输出示例：
# Base created successfully!
# base_token: KuC6xxxxxxxxxxxxxxxxxxxxxPm  ← 保存这个（这是示例，你的会不同）

# 创建记录表
lark-cli base +table-create \
  --base-token <你的base_token> \
  --name "记录表" \
  --folder-token "" \
  --fields '[
    {"field_name": "记录标题", "type": "text"},
    {"field_name": "标签", "type": "text", "options": ["待办", "灵感", "其他"]},
    {"field_name": "详细内容", "type": "text"},
    {"field_name": "创建日期", "type": "date"},
    {"field_name": "完成状态", "type": "select", "options": ["未完成", "进行中", "已完成"]},
    {"field_name": "截止日期", "type": "date"},
    {"field_name": "来源", "type": "select", "options": ["终端", "飞书对话", "录音"]},
    {"field_name": "关联文档", "type": "text"}
  ]'

# 输出示例：
# Table created successfully!
# table_id: tblxxxxxxxxxxxxxxGL  ← 保存这个（这是示例，你的会不同）
```

#### 8.3 获取 folder_token

1. 打开飞书云空间
2. 创建一个新文件夹，命名"CARE 助理"
3. 进入文件夹，查看 URL：
   - URL 格式：`https://xxx.feishu.cn/wiki/XXXXXX`
   - 其中 `XXXXXX` 就是 `folder_token`

#### 8.4 配置 Bot 模式（可选）

如果你想使用 Bot 模式，编辑 `scripts/bot-handler.sh`：

```bash
nano ~/MyWorkspace/MyCode/Feishu/care-assistant/scripts/bot-handler.sh
```

填入你的机器人凭证：
- APP_ID：你的机器人 App ID
- APP_SECRET：你的机器人 App Secret
- ENCRYPT_KEY：事件订阅 Encrypt Key
- VERIFICATION_TOKEN：事件订阅 Verification Token

### 步骤 9：配置文件示例

完整的 `~/.care-assistant/config.json` 示例：

```json
{
  "base_token": "你的base_token",
  "table_id": "你的table_id",
  "view_id": "",
  "article_table_id": "你的文章收藏表ID",
  "user_open_id": "你的user_open_id",
  "folder_token": "你的folder_token",
  "recordings_dir": "/Users/你的用户名/.care-assistant/recordings",
  "output_dir": "/Users/你的用户名/MyWorkspace/Knowledge/Obsidian/V0-MyAntinet/5-DaliyCC/CARE_Assistant",
  "created_at": "2026-04-18"
}
```

### 步骤 10：测试配置

在 Claude Code 中随便说一句话测试：

```
你：你好
AI：检测到首次使用，正在初始化 CARE 助理...
    已创建多维表格 "CARE 助理"
    已创建记录表，包含 8 个字段
    配置已保存到 ~/.care-assistant/config.json
```

如果看到类似的回复，说明配置成功！

### 前置条件总结

- ✅ [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 已安装
- ✅ [lark-cli](https://github.com/larksuite/cli) 已安装
- ✅ 飞书应用已创建，权限已配置
- ✅ 飞书机器人已创建（Bot 模式需要）
- ✅ config.json 已填写完整

---

## 日常使用

配置完成后，你可以通过以下方式使用 CARE 助理：

### 在 Claude Code 中使用

打开 Claude Code，直接像对话一样说出你想记录的内容：

#### 场景1：记录待办
```
你：明天下午3点开会
AI：已记录 [待办]：明天下午3点开会（已创建飞书任务）
```

#### 场景2：记录灵感
```
你：灵感 做一个自动整理录音的工具
AI：已记录 [灵感]：做一个自动整理录音的工具
```

#### 场景3：处理录音转写
```
你：帮我处理一下这个录音 [文件路径或粘贴内容]
AI：
📊 录音处理完成

✅ 飞书表格：
   - 新增记录 5 条
   - 待办 3 条（已创建飞书任务）
   - 灵感 2 条

📄 双端文档：
   - 本地：/Users/xxx/.../YYMMDD_主题.md
   - 飞书：https://xxx.feishu.cn/doc/xxx
```

#### 场景4：回顾本周
```
你：回顾一下这周
AI：
📊 本周回顾
- 共记录 23 条
- 待办 8 条（已完成 3 条，进行中 2 条，已过期 3 条）
- 灵感 12 条

📄 回顾文档已生成：https://xxx.feishu.cn/doc/xxx
```

### Bot 模式（飞书中使用）

如果你想 7x24 后台运行，在飞书中直接记录：

```bash
# 启动 Bot 模式
cd ~/MyWorkspace/MyCode/Feishu/care-assistant
nohup bash scripts/bot-handler.sh > /tmp/care-bot.log 2>&1 &

# 查看日志
tail -f /tmp/care-bot.log

# 停止 Bot 模式
pkill -f bot-handler.sh
```

启动后，直接在飞书中给 CARE 助理 Bot 发消息即可记录。

### 技能文件位置（供参考）

安装后的技能文件位于 `~/.claude/skills/`：
```
~/.claude/skills/
├── care-assistant/              # 主路由 skill（识别意图并分发）
│   ├── SKILL.md
│   └── references/              # 子技能引用文档
│       ├── capture.md           # 随手记
│       ├── review.md            # 回顾整理
│       ├── recording.md         # 录音转写
│       └── setup.md             # 首次设置
├── care-capture/                # 随手记 skill（独立可用）
│   └── SKILL.md
├── care-recording/              # 录音转写 skill（独立可用）
│   └── SKILL.md
└── care-review/                 # 回顾整理 skill（独立可用）
    └── SKILL.md
```

---

## 根据自己的情况改写

CARE 助理的设计是模块化的，你可以根据需要修改：

### 修改标签体系

编辑 `~/.claude/skills/care-assistant/references/care-capture.md`，找到标签部分：

```markdown
**标签体系**：
- 类型标签：待办、灵感、其他
- 主题标签：AI 根据内容自动判断（如：AI、社群、内容创作、效率工具等）
```

### 修改文档样式

编辑 `~/.claude/skills/care-assistant/references/care-recording.md`，找到文档结构部分：

```markdown
**文档结构（必须详细，不能简略）：**
```markdown
# 录音：主题描述  ← 改成你喜欢的标题格式

## 来源
... 改成你想要的结构
`````

### 修改路径配置

所有路径都在 `~/.care-assistant/config.json` 中配置：

```json
{
  "recordings_dir": "改成你喜欢的路径",
  "output_dir": "改成你喜欢的输出路径"
}
```

### 修改触发词

编辑各个 skill 文件中的 `description` 字段，添加你自己的触发词。

### 增加新功能

1. 在 `references/` 下创建新的 skill 文件
2. 在主路由 `care-assistant.md` 中添加路由规则

## 常见问题

**Q: 录音转写文档支持什么格式？**

A: 支持 .md、.txt、.docx 格式。直接给文件路径或粘贴内容即可。

**Q: Bot 模式如何停止？**

A: `pkill -f bot-handler.sh`

**Q: 如何备份我的数据？**

A: 飞书多维表格自动在云端备份，本地文档在配置的 `output_dir` 中。

**Q: 可以同时用多个飞书表格吗？**

A: 可以，修改 `config.json` 中的 `table_id` 即可。建议为不同用途创建不同表格。

**Q: 录音转写的文档格式可以自定义吗？**

A: 可以，编辑 `care-recording.md` skill 文件中的文档结构部分。

## 技术架构

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
                      ├─ auto-dedup.py    (自动去重)
                      └─ 智能标签        (关键词匹配)
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT

---

**作者**: 胡九思  
**公众号**: 九思AI歪博  
**比赛**: [飞书 CLI 创作者大赛](https://waytoagi.feishu.cn/wiki/R4S3w8wTTie04nkYiL6c8rxon4d)
