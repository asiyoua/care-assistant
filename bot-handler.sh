#!/bin/bash
# CARE Bot Handler — 接收飞书消息，写入多维表格，回复确认
# 用法：bash bot-handler.sh
# 特性：自动重连、语义去重、链接→文章表、智能标签

set -uo pipefail

export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897

CONFIG="$HOME/.care-assistant/config.json"
BASE_TOKEN=$(jq -r '.base_token' "$CONFIG")
TABLE_ID=$(jq -r '.table_id' "$CONFIG")
ARTICLE_TABLE_ID=$(jq -r '.article_table_id' "$CONFIG")
USER_OPEN_ID=$(jq -r '.user_open_id' "$CONFIG")

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2; }

# ── 消息处理 ──────────────────────────────────────────

handle_message() {
  local line="$1"

  local chat_id msg_type content text
  chat_id=$(echo "$line" | jq -r '.event.message.chat_id // empty')
  msg_type=$(echo "$line" | jq -r '.event.message.message_type // empty')
  content=$(echo "$line" | jq -r '.event.message.content // empty')

  [[ -z "$chat_id" || -z "$content" ]] && return

  # 只处理文本消息
  if [[ "$msg_type" == "text" ]]; then
    text=$(echo "$content" | jq -r '.text // empty' 2>/dev/null || echo "")
  else
    text=""
  fi
  [[ -z "$text" ]] && return

  # 忽略过短的消息（单字符、表情等）
  if [[ ${#text} -lt 2 ]]; then
    log "Ignored short message: ${text}"
    return
  fi

  local today
  today=$(date +%Y-%m-%d)

  # ── 语义去重 ────────────────────────────────────────
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  local existing_titles
  existing_titles=$(lark-cli base +record-list \
    --base-token "$BASE_TOKEN" \
    --table-id "$TABLE_ID" \
    --limit 200 2>/dev/null | jq -r '.data.data[] | .[0]' 2>/dev/null)

  local dedup_result
  dedup_result=$(jq -n \
    --arg n "$text" \
    --argjson e "$(echo "$existing_titles" | jq -R -s 'split("\n") | map(select(length > 0))')" \
    '{"new":$n,"existing":$e}' | python3 "$SCRIPT_DIR/dedup.py" 2>/dev/null)

  if [[ "$dedup_result" == "dup" ]]; then
    reply_msg="已存在，跳过：${text:0:30}"
    lark-cli im +messages-send --as bot --chat-id "$chat_id" --text "$reply_msg" >/dev/null 2>&1
    log "Dedup: ${text:0:30}..."
    return
  fi

  # ── 链接 → 文章收藏表 ────────────────────────────────
  if echo "$text" | grep -qE 'https?://'; then
    local url
    url=$(echo "$text" | grep -oE 'https?://[^ ]+' | head -1)
    local user_desc="${text//$url/}"
    user_desc=$(echo "$user_desc" | xargs)

    # 提取网页内容
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    local article_info
    article_info=$(python3 "$SCRIPT_DIR/extract-article.py" "$url" 2>/dev/null)

    local title author description
    title=$(echo "$article_info" | jq -r '.title // empty' | head -1)
    author=$(echo "$article_info" | jq -r '.author // empty' | head -1)
    description=$(echo "$article_info" | jq -r '.description // empty' | head -1)

    # 优先级：用户描述 > 网页title > 链接
    [[ -n "$user_desc" ]] && title="$user_desc"
    [[ -z "$title" ]] && title="链接收藏"

    # 构建备注（作者+摘要）
    local remark=""
    [[ -n "$author" ]] && remark="作者：$author"
    [[ -n "$description" ]] && remark="${remark}${remark:+ | }${description:0:150}"

    local json
    json=$(jq -n \
      --arg t "$title" \
      --arg u "$url" \
      --arg r "$remark" \
      --arg d "$today" \
      '{"标题":$t,"链接":$u,"备注":$r,"标签":["其他"],"来源":"飞书对话","收藏时间":$d}')

    if lark-cli base +record-upsert \
      --base-token "$BASE_TOKEN" \
      --table-id "$ARTICLE_TABLE_ID" \
      --json "$json" >/dev/null 2>&1; then
      reply_msg="✅ 已收藏：$title"
      [[ -n "$author" ]] && reply_msg="$reply_msg\n👤 $author"
    else
      reply_msg="收藏失败，请稍后重试"
      log "ERROR: Failed to save article: ${title}"
    fi

    lark-cli im +messages-send --as bot --chat-id "$chat_id" --text "$reply_msg" >/dev/null 2>&1
    log "Article: ${title} → article table"
    return
  fi

  # ── 普通记录 → 记录表 ────────────────────────────────
  local title="$text"
  [[ ${#text} -gt 50 ]] && title="${text:0:50}..."

  # 智能标签检测
  local tags='["其他"]'
  if echo "$text" | grep -qE '明天|后天|下周|这周|周[一二三四五六日末]|[0-9]+号|[0-9]+日|上午|下午|晚上|几点|之前要|截止|deadline|DDL|ddl'; then
    tags='["待办"]'
  elif echo "$text" | grep -qE '灵感|想法|试试|做一个|搞一个|学|研究|探索|尝试|如果|说不定|也许能|可以考虑'; then
    tags='["灵感"]'
  fi

  local json
  json=$(jq -n \
    --arg t "$title" \
    --arg c "$text" \
    --arg d "$today" \
    --argjson tg "$tags" \
    '{"记录标题":$t,"来源":"飞书对话","标签":$tg,"详细内容":$c,"创建日期":$d,"截止日期":"","完成状态":"未完成","关联文档":""}')

  if ! lark-cli base +record-upsert \
    --base-token "$BASE_TOKEN" \
    --table-id "$TABLE_ID" \
    --json "$json" >/dev/null 2>&1; then
    reply_msg="记录失败，请稍后重试"
    lark-cli im +messages-send --as bot --chat-id "$chat_id" --text "$reply_msg" >/dev/null 2>&1
    log "ERROR: Failed to save record: ${title}"
    return
  fi

  local tag_label
  tag_label=$(echo "$tags" | jq -r '.[0]')
  reply_msg="已记录 [${tag_label}]：${title}"

  # 待办 → 创建飞书任务
  if [[ "$tag_label" == "待办" ]]; then
    if lark-cli task +create \
      --summary "$title" \
      --due "$today" \
      --assignee "$USER_OPEN_ID" >/dev/null 2>&1; then
      reply_msg="${reply_msg}（已创建飞书任务）"
    else
      log "WARN: Failed to create task for: ${title}"
    fi
  fi

  lark-cli im +messages-send \
    --as bot \
    --chat-id "$chat_id" \
    --text "$reply_msg" >/dev/null 2>&1

  log "Record: ${text:0:30}... → [${tag_label}] ${reply_msg:0:50}"
}

# ── 主循环（自动重连） ──────────────────────────────────

log "CARE Bot starting (auto-reconnect enabled)..."

while true; do
  log "Connecting to Lark event WebSocket..."
  lark-cli event +subscribe \
    --as bot \
    --event-types im.message.receive_v1 2>&1 | \
  while IFS= read -r line; do
    # 只处理包含 event.message 的行（跳过连接状态行）
    echo "$line" | jq -e '.event.message' >/dev/null 2>&1 || continue
    handle_message "$line"
  done

  # 如果 while 循环退出，说明连接断了
  EXIT_CODE=$?
  log "Connection lost (exit: ${EXIT_CODE}). Reconnecting in 5s..."
  sleep 5
done
