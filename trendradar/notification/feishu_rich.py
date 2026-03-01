# coding=utf-8
"""
飞书富文本转换模块

将 Markdown 格式内容转换为飞书富文本 (post) 格式
"""

import re
from typing import Dict, List, Optional, Tuple


def parse_markdown_to_feishu_rich(text: str, title: Optional[str] = None) -> Dict:
    """将 Markdown 文本转换为飞书富文本格式

    Args:
        text: Markdown 格式的文本
        title: 可选的标题

    Returns:
        飞书 post 消息格式的字典
    """
    content = _parse_text_to_paragraphs(text)

    result = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "content": content
                }
            }
        }
    }

    if title:
        result["content"]["post"]["zh_cn"]["title"] = title

    return result


def _parse_text_to_paragraphs(text: str) -> List[List[Dict]]:
    """将文本解析为飞书富文本段落格式

    Args:
        text: 输入文本

    Returns:
        飞书富文本段落列表
    """
    paragraphs = []

    # 按行分割
    lines = text.split('\n')

    for line in lines:
        if line.strip() == '':
            # 空行添加一个空段落
            continue

        # 解析每一行为富文本元素
        elements = _parse_line_to_elements(line)
        if elements:
            paragraphs.append(elements)

    return paragraphs


def _parse_line_to_elements(line: str) -> List[Dict]:
    """解析单行为富文本元素列表

    Args:
        line: 单行文本

    Returns:
        富文本元素列表
    """
    elements = []

    # 处理 HTML font 标签 <font color='xxx'>text</font>
    # 转换为飞书的颜色文本
    line = _convert_font_tags(line)

    # 处理 Markdown 链接 [text](url)
    # 先提取所有链接
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    # 处理加粗 **text**
    bold_pattern = r'\*\*([^*]+)\*\*'

    # 构建一个混合解析器
    pos = 0
    remaining = line

    while remaining:
        # 找到下一个特殊元素
        next_link = re.search(link_pattern, remaining)
        next_bold = re.search(bold_pattern, remaining)

        # 确定最近的一个
        next_match = None
        match_type = None

        if next_link and next_bold:
            if next_link.start() < next_bold.start():
                next_match = next_link
                match_type = 'link'
            else:
                next_match = next_bold
                match_type = 'bold'
        elif next_link:
            next_match = next_link
            match_type = 'link'
        elif next_bold:
            next_match = next_bold
            match_type = 'bold'

        if next_match:
            # 添加匹配前的普通文本
            if next_match.start() > 0:
                plain_text = remaining[:next_match.start()]
                if plain_text:
                    elements.append({"tag": "text", "text": plain_text})

            # 添加匹配的元素
            if match_type == 'link':
                elements.append({
                    "tag": "a",
                    "text": next_match.group(1),
                    "href": next_match.group(2)
                })
            elif match_type == 'bold':
                elements.append({
                    "tag": "text",
                    "text": next_match.group(1),
                    "style": ["bold"]
                })

            # 移动到剩余部分
            remaining = remaining[next_match.end():]
        else:
            # 没有更多特殊元素，添加剩余文本
            if remaining:
                elements.append({"tag": "text", "text": remaining})
            break

    return elements


def _convert_font_tags(text: str) -> str:
    """转换 HTML font 标签

    飞书富文本不支持 font 标签，需要将其转换为纯文本
    同时记录颜色信息（虽然飞书不直接支持颜色，但我们可以用 emoji 或其他方式标记）

    Args:
        text: 包含 font 标签的文本

    Returns:
        转换后的文本
    """
    # 移除 <font color='xxx'> 标签，保留内容
    # 由于飞书富文本不支持颜色，我们直接移除标签
    text = re.sub(r"<font\s+color='[^']*'>", '', text)
    text = re.sub(r"</font>", '', text)

    # 也处理双引号的情况
    text = re.sub(r'<font\s+color="[^"]*">', '', text)
    text = re.sub(r'</font>', '', text)

    return text


def convert_markdown_content_to_feishu_post(
    markdown_content: str,
    title: Optional[str] = None
) -> Dict:
    """将完整的 Markdown 内容转换为飞书 post 消息

    这是主要的外部接口函数

    Args:
        markdown_content: Markdown 格式的内容
        title: 可选的消息标题

    Returns:
        飞书 post 消息格式的字典
    """
    return parse_markdown_to_feishu_rich(markdown_content, title)


# 测试代码
if __name__ == "__main__":
    test_text = """📊 **热点词汇统计**

🔥 [1/3] **AI** : <font color='red'>15</font> 条

  1. [百度热搜] 🆕 ChatGPT-5正式发布
  2. [今日头条] AI芯片概念股暴涨 [__3__]

---

🆕 **本次新增热点新闻** (共 5 条)

更新时间：2026-03-01 16:17:30"""

    result = convert_markdown_content_to_feishu_post(test_text, "TrendRadar 热点推送")
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
