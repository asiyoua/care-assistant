#!/usr/bin/env python3
"""
配置加载模块
从 ~/.care-assistant/config.json 读取配置
"""

import json
import os
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path.home() / ".care-assistant" / "config.json"


def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_config():
    """获取配置，单例模式"""
    if not hasattr(get_config, "_cache"):
        get_config._cache = load_config()
    return get_config._cache


# 便捷访问函数
def get_base_token():
    return get_config()["base_token"]


def get_table_id():
    return get_config()["table_id"]


def get_user_open_id():
    return get_config()["user_open_id"]


def get_folder_token():
    return get_config()["folder_token"]


def get_recordings_dir():
    return get_config().get("recordings_dir", str(Path.home() / ".care-assistant" / "recordings"))


def get_output_dir():
    return get_config().get("output_dir", str(Path.home() / "MyWorkspace" / "Knowledge" / "Obsidian" / "V0-MyAntinet" / "5-DaliyCC" / "CARE_Assistant"))


if __name__ == "__main__":
    # 测试配置加载
    config = get_config()
    print("配置加载成功:")
    for key, value in config.items():
        if "token" in key.lower() or "id" in key.lower():
            print(f"  {key}: *** (脱敏)")
        else:
            print(f"  {key}: {value}")
