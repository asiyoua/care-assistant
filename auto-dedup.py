#!/usr/bin/env python3
"""
自动去重：删除没有关联文档的重复记录
"""

import json
import subprocess
import os
import sys

# 添加项目路径以导入 config_loader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_base_token, get_table_id

def run_command(cmd):
    """运行命令并返回输出"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        env={**os.environ, "https_proxy": "http://127.0.0.1:7897", "http_proxy": "http://127.0.0.1:7897"}
    )
    return result.stdout, result.stderr, result.returncode

def get_all_records():
    """获取所有记录（使用 bot API）"""
    base_token = get_base_token()
    table_id = get_table_id()
    cmd = f'lark-cli api GET --as bot "/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records?limit=200"'
    output, _, _ = run_command(cmd)
    data = json.loads(output)
    return data.get("data", {}).get("items", [])

def delete_record(record_id):
    """删除记录"""
    base_token = get_base_token()
    table_id = get_table_id()
    cmd = f'lark-cli api DELETE --as bot "/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records/{record_id}"'
    _, stderr, returncode = run_command(cmd)
    return returncode == 0

def main():
    records = get_all_records()

    # 按标题分组
    title_groups = {}
    for record in records:
        title = record.get("fields", {}).get("记录标题")
        if not title:
            continue

        if title not in title_groups:
            title_groups[title] = []
        title_groups[title].append(record)

    print("=" * 60)
    print("🧹 自动去重")
    print("=" * 60)

    deleted_count = 0

    for title, group in title_groups.items():
        if len(group) > 1:
            # 找出有关联文档的和没有关联文档的
            with_doc = [r for r in group if r.get("fields", {}).get("关联文档")]
            without_doc = [r for r in group if not r.get("fields", {}).get("关联文档")]

            print(f"\n📌 '{title}'")
            print(f"   有关联文档: {len(with_doc)} 条")
            print(f"   无关联文档: {len(without_doc)} 条")

            # 删除没有关联文档的记录
            for record in without_doc:
                record_id = record.get("record_id")
                print(f"   删除记录 {record_id}...", end=" ")
                if delete_record(record_id):
                    print("✅")
                    deleted_count += 1
                else:
                    print("❌")

    print(f"\n" + "=" * 60)
    print(f"✅ 去重完成！共删除 {deleted_count} 条重复记录")
    print("=" * 60)

if __name__ == "__main__":
    main()
