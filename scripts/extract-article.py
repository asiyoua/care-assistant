#!/usr/bin/env python3
"""
网页内容提取工具
用法：echo "https://example.com" | python3 extract-article.py
输出：JSON格式 {title, author, description, content}
"""

import sys
import json
import urllib.request
from urllib.error import URLError
from html.parser import HTMLParser
import re
import ssl

# 禁用SSL验证（用于某些证书配置问题）
ssl._create_default_https_context = ssl._create_unverified_context

class MetaParser(HTMLParser):
    """提取HTML meta信息和title"""
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.author = ""
        self.in_title = False
        self.meta_done = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")

            if name == "description":
                self.description = content
            elif name == "author":
                self.author = content
            elif prop == "og:title" and not self.title:
                self.title = content
            elif prop == "og:description":
                self.description = content or self.description
            elif prop == "article:author":
                self.author = content or self.author

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title = data.strip()

def extract_article(url):
    """提取文章信息"""
    result = {
        "title": "",
        "author": "",
        "description": "",
        "url": url.strip()
    }

    try:
        # 设置User-Agent避免被拦截
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

        parser = MetaParser()
        parser.feed(html)

        result["title"] = parser.title or ""
        result["author"] = parser.author or ""
        result["description"] = parser.description or ""

        # 如果没有description，尝试从body中提取前200字
        if not result["description"]:
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
            if body_match:
                body_text = re.sub(r'<[^>]+>', ' ', body_match.group(1))
                body_text = ' '.join(body_text.split())
                result["description"] = body_text[:200] + "..."

    except URLError as e:
        result["error"] = f"网络错误: {e}"
    except Exception as e:
        result["error"] = f"解析错误: {e}"

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供URL"}))
        sys.exit(1)

    url = sys.argv[1]
    result = extract_article(url)
    print(json.dumps(result, ensure_ascii=False))
