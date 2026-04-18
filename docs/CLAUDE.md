# CARE 助理 — 项目开发备忘

> 基于 lark-cli 的 Claude Code 个人效率助理，参加飞书 CLI 创作者大赛。
> CARE = Capture 随手记 + Auto-sort 自动分 + Review 定期回顾 + Execute 照着做

## 文件布局

| 位置 | 作用 |
|------|------|
| `~/.claude/skills/care-assistant/SKILL.md` | 主路由 skill（运行时） |
| `~/.claude/skills/care-capture/SKILL.md` | 随手记 skill（运行时） |
| `~/.claude/skills/care-review/SKILL.md` | 回顾整理 skill（运行时） |
| `~/.claude/skills/care-recording/SKILL.md` | 录音转写 skill（运行时） |
| `~/MyWorkspace/MyCode/Feishu/care-assistant/` | Git 仓库（版本管理） |
| `references/care-*.md` | 仓库中 skill 的镜像（从 `~/.claude/skills/` 同步） |
| `~/.care-assistant/config.json` | 运行时配置（base_token, table_id, user_open_id, folder_token） |

**同步规则**：改 skill 时改 `~/.claude/skills/`，提交时同步到 `references/`。

## lark-cli 注意事项

- 需要代理：`https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897`
- 配置信息从 `~/.care-assistant/config.json` 读取：
  - `base_token`: 飞书多维表格 Base Token
  - `table_id`: 记录表 ID
  - `user_open_id`: 用户 Open ID
  - `folder_token`: 飞书文件夹 Token

## 已完成

- [x] Skill 拆分：主路由 care-assistant + 子 skill (capture/review/recording)
- [x] 随手记：语义去重、智能标签、待办创建飞书任务
- [x] 录音转写：三层输出（表格记录 + 飞书文档 + 汇报）
- [x] 回顾整理：查看模式 + 回顾模式（生成飞书文档）
- [x] Bot 模式：bot-handler.sh 7x24 后台运行 + 自动重连
- [x] 去重引擎：dedup.py 时间感知语义去重
- [x] 首次 Setup：自动建表建字段
- [x] README 重写：详细 lark-cli 使用情况 + 功能文档

## 已知问题

- **被动语句触发不稳定**："今天下午三点有个会议" 这类不带明确触发词的句子，有时不会触发 care-capture skill。已强化 description 但尚未在新会话中验证。
- **文章收藏功能已移除**：因为 skill 无法阻止 Claude 抓取网页内容，收藏功能从 skill 侧移除。Bot 侧 (bot-handler.sh) 仍保留。

## Backlog

- [ ] 验证被动语句触发是否修复（新会话测试）
- [ ] Bot 模式功能与 Skill 模式对齐（是否也移除 bot 的文章收藏）
- [ ] 录音转写 skill 实际测试（处理一个真实 .docx 转写文件）
- [ ] 回顾文档实际测试（生成飞书回顾文档）
- [ ] 比赛提交准备（录制 demo 视频、写提交说明）
