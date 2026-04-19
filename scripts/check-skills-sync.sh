#!/bin/bash
# 检查运行时 skill 和仓库 skill 是否同步
# 用法：bash scripts/check-skills-sync.sh

set -euo pipefail

RUNTIME_SKILLS_DIR="$HOME/.claude/skills"
REPO_SKILLS_DIR="/Users/bian/MyWorkspace/MyCode/Feishu/care-assistant/skills"

echo "=== 检查 skill 同步状态 ==="
echo ""

skills=("care-capture" "care-recording" "care-review" "care-assistant")
all_synced=true

for skill in "${skills[@]}"; do
  runtime_file="$RUNTIME_SKILLS_DIR/$skill/SKILL.md"
  repo_file="$REPO_SKILLS_DIR/$skill/SKILL.md"

  if [ ! -f "$runtime_file" ]; then
    echo "❌ $skill: 运行时 skill 不存在"
    all_synced=false
    continue
  fi

  if [ ! -f "$repo_file" ]; then
    echo "❌ $skill: 仓库 skill 不存在"
    all_synced=false
    continue
  fi

  if diff -q "$runtime_file" "$repo_file" >/dev/null 2>&1; then
    echo "✅ $skill: 已同步"
  else
    echo "❌ $skill: 未同步"
    all_synced=false
  fi
done

echo ""
if [ "$all_synced" = true ]; then
  echo "🎉 所有 skill 已同步，可以安全提交"
  exit 0
else
  echo "⚠️  存在未同步的 skill，请先同步"
  exit 1
fi
