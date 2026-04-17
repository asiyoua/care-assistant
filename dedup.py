#!/usr/bin/env python3
"""语义去重：中文停用词过滤 + 单字 Jaccard + 时间关键词匹配。"""
import sys
import json
import re

STOP_WORDS = {
    "的", "了", "在", "是", "我", "你", "他", "这", "那", "和", "与",
    "但", "就", "也", "都", "还", "去", "来", "到", "过", "把", "被",
    "从", "向", "往", "给", "让", "用", "对", "为", "一", "个", "上",
    "下", "中", "大", "小", "有", "要", "说", "会", "能", "做", "没",
    "不", "又", "很", "而", "之", "于", "吗", "吧", "呢", "啊", "呀",
    "么", "得", "着", "些", "什", "么", "怎", "几", "多",
}

# 时间/数量词 — 去重时忽略，避免"明天开会"和"后天开会"被判重复
TIME_WORDS = {
    "今", "明", "后", "昨", "周", "月", "年", "日", "号",
    "上", "下", "早", "晚", "午", "点", "分",
    "〇", "零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
}


def extract_chars(text, ignore_time=False):
    """提取有意义的汉字，可选忽略时间词。"""
    # 统一数字表示
    num_map = str.maketrans("0123456789", "〇一二三四五六七八九")
    text = text.translate(num_map)
    chars = set()
    for c in text:
        if '\u4e00' <= c <= '\u9fff' and c not in STOP_WORDS:
            if ignore_time and c in TIME_WORDS:
                continue
            chars.add(c)
    return chars


def is_duplicate(new_text, existing_titles, threshold=0.45):
    new_chars = extract_chars(new_text)
    if len(new_chars) < 2:
        return False

    new_chars_no_time = extract_chars(new_text, ignore_time=True)

    for title in existing_titles:
        if not title:
            continue
        old_chars = extract_chars(title)
        if len(old_chars) < 2:
            continue

        # 标准比较
        overlap = len(new_chars & old_chars)
        union = len(new_chars | old_chars)
        if union == 0:
            continue
        sim = overlap / union
        if sim >= threshold:
            return True

        # 去掉时间词后再比较（"明天开会" vs "后天开会"）
        if new_chars_no_time and len(new_chars_no_time) >= 2:
            old_chars_no_time = extract_chars(title, ignore_time=True)
            if old_chars_no_time:
                overlap2 = len(new_chars_no_time & old_chars_no_time)
                union2 = len(new_chars_no_time | old_chars_no_time)
                if union2 > 0 and overlap2 / union2 >= threshold + 0.15:
                    return True

        # 中等相似度 + 核心词高度重叠
        if sim >= 0.30 and overlap / len(new_chars) >= 0.70:
            return True

    return False


if __name__ == "__main__":
    data = json.load(sys.stdin)
    new_text = data["new"]
    existing = data["existing"]
    print("dup" if is_duplicate(new_text, existing) else "new")
