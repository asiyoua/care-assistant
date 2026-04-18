#!/usr/bin/env python3
"""
整理多维表格中的未完成记录
- 分类统计
- 待办类创建飞书任务
- 更新状态
"""

import sys
import json
import subprocess
import os
from datetime import datetime

# 配置
BASE_TOKEN = "KuC6bRThXa5qAbsYP3Uck2pmn8g"
TABLE_ID = "tbl7WLdmqaX1GL4j"
USER_OPEN_ID = "ou_c31c3b7ab2774cc6cb1cfe6a17810aeb"

def run_command(cmd):
    """运行命令并返回输出"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        env={**os.environ, "https_proxy": "http://127.0.0.1:7897", "http_proxy": "http://127.0.0.1:7897"}
    )
    return result.stdout

def get_records():
    """获取所有记录"""
    cmd = f"lark-cli base +record-list --base-token {BASE_TOKEN} --table-id {TABLE_ID} --limit 200"
    output = run_command(cmd)
    data = json.loads(output)
    return data.get("data", {}).get("data", [])

def update_record(record_id, updates):
    """更新记录"""
    json_data = json.dumps(updates, ensure_ascii=False)
    cmd = f"lark-cli base +record-upsert --base-token {BASE_TOKEN} --table-id {TABLE_ID} --record-id {record_id} --json '{json_data}'"
    run_command(cmd)

def create_task(summary, due_date):
    """创建飞书任务"""
    cmd = f"lark-cli task +create --summary '{summary}' --due '{due_date}' --assignee {USER_OPEN_ID}"
    result = run_command(cmd)
    return result

def main():
    # 获取记录
    records = get_records()

    # 字段映射（根据返回顺序）
    # 0: 记录标题, 1: 标签, 2: 详细内容, 3: 创建日期, 4: 完成状态, 5: 截止日期, 6: 来源, 7: 关联文档

    # 分类统计
    stats = {
        "待办": [],
        "灵感": [],
        "其他": [],
        "总计": 0
    }

    print("=" * 60)
    print("📊 未完成记录整理")
    print("=" * 60)

    for record in records:
        # 跳过已完成的
        status = record[4][0] if record[4] else ""
        if status != "未完成":
            continue

        title = record[0]
        tags = [tag for tag in record[1]] if record[1] else []
        content = record[2] if record[2] else ""
        due_date = record[5] if len(record) > 5 else None

        # 统计
        stats["总计"] += 1
        tag_type = "其他"
        for tag in tags:
            if tag in ["待办", "灵感", "其他"]:
                tag_type = tag
                break

        stats[tag_type].append({
            "title": title,
            "content": content,
            "due_date": due_date,
            "tags": tags
        })

    # 输出统计
    print(f"\n📈 统计概览：")
    print(f"  总计：{stats['总计']} 条未完成")
    print(f"  待办：{len(stats['待办'])} 条")
    print(f"  灵感：{len(stats['灵感'])} 条")
    print(f"  其他：{len(stats['其他'])} 条")

    # 详细列表
    if stats["待办"]:
        print(f"\n✅ 待办类 ({len(stats['待办'])} 条)：")
        for i, item in enumerate(stats["待办"], 1):
            due = item["due_date"][:10] if item["due_date"] else "无截止日期"
            print(f"  {i}. {item['title']} (截止：{due})")

    if stats["灵感"]:
        print(f"\n💡 灵感类 ({len(stats['灵感'])} 条)：")
        for i, item in enumerate(stats["灵感"], 1):
            print(f"  {i}. {item['title']}")

    if stats["其他"]:
        print(f"\n📝 其他类 ({len(stats['其他'])} 条)：")
        for i, item in enumerate(stats["其他"][:5], 1):
            print(f"  {i}. {item['title']}")
        if len(stats["其他"]) > 5:
            print(f"  ... 还有 {len(stats['其他']) - 5} 条")

    print(f"\n" + "=" * 60)
    print(f"💡 建议：")
    if stats["待办"]:
        print(f"  • 有 {len(stats['待办'])} 条待办未处理，建议优先关注过期待办")
    if stats["灵感"]:
        print(f"  • 有 {len(stats['灵感'])} 条灵感待行动，考虑是否转化为具体待办")

if __name__ == "__main__":
    main()
