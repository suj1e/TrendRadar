# coding=utf-8
"""
飞书卡片消息构建模块

构建飞书 interactive 卡片消息，提供更好的视觉效果
"""

from datetime import datetime
from typing import Dict, List, Optional, Callable


def build_feishu_card(
    report_data: Dict,
    update_info: Optional[Dict] = None,
    mode: str = "daily",
    get_time_func: Optional[Callable[[], datetime]] = None,
    rss_items: Optional[list] = None,
    show_new_section: bool = True,
) -> Dict:
    """构建飞书卡片消息

    Args:
        report_data: 报告数据字典
        update_info: 版本更新信息
        mode: 报告模式
        get_time_func: 获取当前时间的函数
        rss_items: RSS 条目列表
        show_new_section: 是否显示新增热点区域

    Returns:
        飞书卡片消息字典
    """
    now = get_time_func() if get_time_func else datetime.now()

    elements = []

    # 头部摘要
    total_stats = len(report_data["stats"])
    total_titles = sum(len(stat["titles"]) for stat in report_data["stats"])
    total_new = report_data.get("total_new_count", 0)
    rss_count = len(rss_items) if rss_items else 0

    summary_parts = []
    if total_stats > 0:
        summary_parts.append(f"📊 {total_stats}个热点词")
    if total_titles > 0:
        summary_parts.append(f"📰 {total_titles}条新闻")
    if total_new > 0:
        summary_parts.append(f"🆕 {total_new}条新增")
    if rss_count > 0:
        summary_parts.append(f"📡 {rss_count}条RSS")

    if summary_parts:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": " **" + " | ".join(summary_parts) + "**"
            }
        })
        elements.append({"tag": "hr"})

    # 热点词汇统计部分
    if report_data["stats"]:
        for i, stat in enumerate(report_data["stats"]):
            word = stat["word"]
            count = stat["count"]
            titles = stat["titles"]

            # 热度等级颜色
            if count >= 10:
                emoji = "🔥"
                color = "red"
            elif count >= 5:
                emoji = "📈"
                color = "orange"
            else:
                emoji = "📌"
                color = "grey"

            # 词汇标题
            word_title = f"{emoji} **{word}** · {count}条"
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": word_title
                }
            })

            # 新闻列表
            for j, title_data in enumerate(titles, 1):
                title = title_data.get("title", "")
                source = title_data.get("source_name", "")
                url = title_data.get("mobile_url") or title_data.get("url", "")

                if url:
                    line = f"  [{title}]({url})"
                else:
                    line = f"  {title}"

                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{j}. [{source}] {line}"
                    }
                })

            # 分隔线
            if i < len(report_data["stats"]) - 1:
                elements.append({"tag": "hr"})

    # 新增新闻部分
    if show_new_section and report_data.get("new_titles"):
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"🆕 **本次新增热点新闻** (共 {report_data['total_new_count']} 条)"
            }
        })

        for source_data in report_data["new_titles"]:
            source_name = source_data["source_name"]
            titles = source_data["titles"]

            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{source_name}** ({len(titles)} 条)"
                }
            })

            for j, title_data in enumerate(titles, 1):
                title = title_data.get("title", "")
                url = title_data.get("mobile_url") or title_data.get("url", "")

                if url:
                    line = f"  [{title}]({url})"
                else:
                    line = f"  {title}"

                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{j}. {line}"
                    }
                })

    # RSS 部分 - rss_items 是关键词统计格式，和热榜 stats 一样
    if rss_items:
        elements.append({"tag": "hr"})

        # 统计总条目数
        total_rss = sum(item.get("count", 0) for item in rss_items)
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"📰 **RSS 订阅更新** (共 {len(rss_items)} 个关键词，{total_rss} 条)"
            }
        })

        for stat in rss_items:
            word = stat.get("word", "")
            count = stat.get("count", 0)
            titles = stat.get("titles", [])

            if not word:
                continue

            # 关键词标题
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"📌 **{word}** · {count}条"
                }
            })

            # 新闻列表
            for j, title_data in enumerate(titles, 1):
                title = title_data.get("title", "")
                source = title_data.get("source_name", "")
                url = title_data.get("url", "") or title_data.get("mobile_url", "")
                time_display = title_data.get("time_display", "")

                if url:
                    line = f"[{title}]({url})"
                else:
                    line = title

                content = f"{j}. [{source}] {line}"
                if time_display:
                    content += f" `{time_display}`"

                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                })

    # 空内容提示
    if not elements:
        mode_texts = {
            "incremental": "增量模式下暂无新增匹配的热点词汇",
            "current": "当前榜单模式下暂无匹配的热点词汇",
            "daily": "暂无匹配的热点词汇"
        }
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"📭 {mode_texts.get(mode, '暂无匹配的热点词汇')}"
            }
        })

    # 失败平台
    if report_data.get("failed_ids"):
        elements.append({"tag": "hr"})
        failed_text = "⚠️ **数据获取失败的平台:**\n"
        for fid in report_data["failed_ids"]:
            failed_text += f"\n  • {fid}"
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": failed_text
            }
        })

    # 更新时间
    elements.append({"tag": "hr"})
    time_text = f"⏰ 更新时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"
    if update_info:
        time_text += f"\n📢 发现新版本 {update_info['remote_version']}，当前 {update_info['current_version']}"
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": time_text
        }
    })

    # 构建卡片
    card = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "TrendRadar 热点推送"
                },
                "template": "blue"
            },
            "elements": elements
        }
    }

    return card


def build_feishu_rss_card(
    rss_items: list,
    feeds_info: Optional[Dict] = None,
    get_time_func: Optional[Callable[[], datetime]] = None,
) -> Dict:
    """构建 RSS 飞书卡片消息

    Args:
        rss_items: RSS 条目列表
        feeds_info: RSS 源信息
        get_time_func: 获取当前时间的函数

    Returns:
        飞书卡片消息字典
    """
    now = get_time_func() if get_time_func else datetime.now()

    elements = []

    if not rss_items:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "📭 暂无新的 RSS 订阅内容"
            }
        })
    else:
        # 摘要
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**共 {len(rss_items)} 条更新**"
            }
        })
        elements.append({"tag": "hr"})

        # 按 feed 分组
        feeds_map: Dict[str, list] = {}
        for item in rss_items:
            feed_id = item.get("feed_id", "unknown")
            if feed_id not in feeds_map:
                feeds_map[feed_id] = []
            feeds_map[feed_id].append(item)

        # 已知的 feed_id 到名称的映射（备用）
        known_feeds = {
            "hacker-news": "Hacker News",
            "ruanyifeng": "阮一峰的网络日志",
        }

        for feed_id, items in feeds_map.items():
            # 优先级：feeds_info > item.feed_name > known_feeds > feed_id
            feed_name = items[0].get("feed_name", "") if items else ""
            if feeds_info and feed_id in feeds_info:
                feed_name = feeds_info[feed_id]
            elif not feed_name or feed_name == feed_id:
                feed_name = known_feeds.get(feed_id, feed_id)

            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"📰 **{feed_name}** ({len(items)} 条)"
                }
            })

            for i, item in enumerate(items, 1):
                title = item.get("title", "")
                url = item.get("url", "")
                published = item.get("published_at", "")

                if url:
                    line = f"[{title}]({url})"
                else:
                    line = title

                if published:
                    line += f" `{published}`"

                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{i}. {line}"
                    }
                })

            elements.append({"tag": "hr"})

    # 更新时间
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"⏰ 更新时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"
        }
    })

    card = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "RSS 订阅更新"
                },
                "template": "green"
            },
            "elements": elements
        }
    }

    return card
