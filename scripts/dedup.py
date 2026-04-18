#!/usr/bin/env python3
"""语义去重：时间词先比 → 不一致则不重复 → 再用 Jaccard 比内容。"""
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


def extract_time_phrases(text):
    """提取时间相关的词组，用于时间维度的对比。

    返回一个 set，例如 "明天上午10点开会" → {"明天", "上午", "10点"}
    """
    phrases = set()
    # 相对日期
    for w in ["今天", "明天", "后天", "昨天", "前天"]:
        if w in text:
            phrases.add(w)
    # 星期
    for w in ["周一", "周二", "周三", "周四", "周五", "周六", "周日",
              "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日",
              "这周", "下周", "上周"]:
        if w in text:
            phrases.add(w)
    # 时段
    for w in ["上午", "下午", "晚上", "中午", "早上", "傍晚"]:
        if w in text:
            phrases.add(w)
    # 具体时间：X点、X号、X日
    m = re.findall(r'\d+[点号日]', text)
    phrases.update(m)
    return phrases


def extract_chars(text):
    """提取有意义的汉字（去停用词），用于内容维度的 Jaccard 比较。"""
    # 统一数字表示
    num_map = str.maketrans("0123456789", "〇一二三四五六七八九")
    text = text.translate(num_map)
    return set(c for c in text
               if '\u4e00' <= c <= '\u9fff' and c not in STOP_WORDS)


def is_duplicate(new_text, existing_titles, threshold=0.45):
    new_chars = extract_chars(new_text)
    if len(new_chars) < 2:
        return False

    new_time = extract_time_phrases(new_text)

    for title in existing_titles:
        if not title:
            continue
        old_chars = extract_chars(title)
        if len(old_chars) < 2:
            continue

        # ── 第一步：时间维度比较 ──────────────────────────
        # 两条都有时间信息，但时间不同 → 肯定不是重复
        old_time = extract_time_phrases(title)
        if new_time and old_time and new_time != old_time:
            continue

        # ── 第二步：内容维度 Jaccard 比较 ──────────────
        overlap = len(new_chars & old_chars)
        union = len(new_chars | old_chars)
        if union == 0:
            continue
        sim = overlap / union

        # 高相似度 → 重复
        if sim >= threshold:
            return True

        # 中等相似度 + 新内容大部分词在旧标题中 → 重复
        if sim >= 0.30 and overlap / len(new_chars) >= 0.70:
            return True

    return False


if __name__ == "__main__":
    data = json.load(sys.stdin)
    new_text = data["new"]
    existing = data["existing"]
    print("dup" if is_duplicate(new_text, existing) else "new")
