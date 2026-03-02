# coding=utf-8
"""
天气通知渲染器

将天气数据格式化为各渠道支持的消息格式。
"""

import logging
from typing import Dict, List, Optional

from .providers import WeatherData, ForecastItem

logger = logging.getLogger(__name__)


# 推送类型到标题的映射
SCHEDULE_TYPE_TITLES = {
    "morning": "🌤️ 晨间天气",
    "evening": "🌙 晚间天气",
    "tomorrow": "📅 明日天气",
}


def get_schedule_title(schedule_type: str) -> str:
    """获取推送类型对应的标题"""
    return SCHEDULE_TYPE_TITLES.get(schedule_type, "🌡️ 天气")


def render_weather_content(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
    format_type: str = "text",
) -> str:
    """
    渲染天气消息内容

    Args:
        weather_data_list: 天气数据列表（多个地点）
        schedule_type: 推送类型 (morning, evening, tomorrow)
        include_forecast: 是否包含预报
        format_type: 格式类型 (text, markdown, html)

    Returns:
        格式化的天气消息
    """
    if not weather_data_list:
        return ""

    title = get_schedule_title(schedule_type)

    if format_type == "markdown":
        return _render_markdown(title, weather_data_list, include_forecast)
    elif format_type == "html":
        return _render_html(title, weather_data_list, include_forecast)
    else:
        return _render_text(title, weather_data_list, include_forecast)


def _render_text(
    title: str,
    weather_data_list: List[WeatherData],
    include_forecast: bool,
) -> str:
    """渲染纯文本格式（飞书）"""
    lines = [title, ""]

    for data in weather_data_list:
        # 地点和当前天气
        lines.append(f"📍 {data.location} {data.icon} {data.temp}°C")
        lines.append(f"   {data.condition}，体感 {data.feels_like}°C")

        # 详细信息
        details = []
        if data.humidity:
            details.append(f"湿度 {data.humidity}%")
        if data.wind_speed:
            details.append(f"{data.wind_dir}风 {data.wind_speed}km/h")
        if details:
            lines.append(f"   {' | '.join(details)}")

        # 预报
        if include_forecast and data.forecast:
            lines.append("")
            for i, forecast in enumerate(data.forecast[:3]):  # 最多显示3天
                if i == 0:
                    # 今日预报
                    lines.append(
                        f"   📊 今日 {forecast.temp_low}~{forecast.temp_high}°C "
                        f"{forecast.icon} {forecast.condition}"
                    )
                else:
                    date_short = _format_date_short(forecast.date)
                    lines.append(
                        f"   📅 {date_short} {forecast.temp_low}~{forecast.temp_high}°C "
                        f"{forecast.icon} {forecast.condition}"
                    )

        lines.append("")

    return "\n".join(lines).strip()


def _render_markdown(
    title: str,
    weather_data_list: List[WeatherData],
    include_forecast: bool,
) -> str:
    """渲染 Markdown 格式（钉钉、企微、Slack）"""
    lines = [f"## {title}", ""]

    for data in weather_data_list:
        # 地点和当前天气
        lines.append(f"### 📍 {data.location}")
        lines.append(f"> {data.icon} **{data.temp}°C** - {data.condition}")
        lines.append(f"> 体感温度：{data.feels_like}°C")

        # 详细信息
        details = []
        if data.humidity:
            details.append(f"湿度 {data.humidity}%")
        if data.wind_speed:
            details.append(f"{data.wind_dir}风 {data.wind_speed}km/h")
        if details:
            lines.append(f"> {' | '.join(details)}")

        # 预报
        if include_forecast and data.forecast:
            lines.append("")
            lines.append("| 日期 | 温度 | 天气 |")
            lines.append("|:---:|:---:|:---:|")
            for i, forecast in enumerate(data.forecast[:3]):
                date_str = "今日" if i == 0 else _format_date_short(forecast.date)
                lines.append(
                    f"| {date_str} | {forecast.temp_low}~{forecast.temp_high}°C | "
                    f"{forecast.icon} {forecast.condition} |"
                )

        lines.append("")

    return "\n".join(lines).strip()


def _render_html(
    title: str,
    weather_data_list: List[WeatherData],
    include_forecast: bool,
) -> str:
    """渲染 HTML 格式（邮件）"""
    html_parts = [
        f"<h2>{title}</h2>",
        "<style>",
        ".weather-card { margin: 15px 0; padding: 15px; background: #f5f5f5; border-radius: 8px; }",
        ".weather-location { font-size: 18px; font-weight: bold; color: #333; }",
        ".weather-current { font-size: 24px; margin: 10px 0; }",
        ".weather-details { color: #666; font-size: 14px; }",
        ".weather-forecast { margin-top: 10px; }",
        ".forecast-table { width: 100%; border-collapse: collapse; margin-top: 8px; }",
        ".forecast-table th, .forecast-table td { padding: 8px; text-align: center; border: 1px solid #ddd; }",
        "</style>",
    ]

    for data in weather_data_list:
        html_parts.append('<div class="weather-card">')

        # 地点和当前天气
        html_parts.append(f'<div class="weather-location">📍 {data.location}</div>')
        html_parts.append(
            f'<div class="weather-current">{data.icon} {data.temp}°C - {data.condition}</div>'
        )
        html_parts.append(
            f'<div class="weather-details">体感 {data.feels_like}°C'
        )

        details = []
        if data.humidity:
            details.append(f"湿度 {data.humidity}%")
        if data.wind_speed:
            details.append(f"{data.wind_dir}风 {data.wind_speed}km/h")
        if details:
            html_parts.append(f" | {' | '.join(details)}")
        html_parts.append("</div>")

        # 预报
        if include_forecast and data.forecast:
            html_parts.append('<div class="weather-forecast">')
            html_parts.append('<table class="forecast-table">')
            html_parts.append("<tr><th>日期</th><th>温度</th><th>天气</th></tr>")

            for i, forecast in enumerate(data.forecast[:3]):
                date_str = "今日" if i == 0 else _format_date_short(forecast.date)
                html_parts.append(
                    f"<tr><td>{date_str}</td>"
                    f"<td>{forecast.temp_low}~{forecast.temp_high}°C</td>"
                    f"<td>{forecast.icon} {forecast.condition}</td></tr>"
                )

            html_parts.append("</table></div>")

        html_parts.append("</div>")

    return "".join(html_parts)


def _format_date_short(date_str: str) -> str:
    """格式化日期为简短形式（如 3/2）"""
    try:
        if "-" in date_str:
            parts = date_str.split("-")
            if len(parts) == 3:
                return f"{parts[1]}/{parts[2]}"
        return date_str
    except Exception:
        return date_str


# 各渠道渲染函数
def render_weather_feishu(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染飞书天气消息"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="text",
    )


def render_weather_dingtalk(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染钉钉天气消息"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="markdown",
    )


def render_weather_wework(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染企业微信天气消息"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="markdown",
    )


def render_weather_telegram(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染 Telegram 天气消息（HTML 格式）"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="html",
    )


def render_weather_email(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染邮件天气消息（HTML 格式）"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="html",
    )


def render_weather_slack(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染 Slack 天气消息（mrkdwn 格式）"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="markdown",
    )


def render_weather_ntfy(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染 ntfy 天气消息（Markdown 格式）"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="markdown",
    )


def render_weather_bark(
    weather_data_list: List[WeatherData],
    schedule_type: str = "morning",
    include_forecast: bool = True,
) -> str:
    """渲染 Bark 天气消息（纯文本）"""
    return render_weather_content(
        weather_data_list,
        schedule_type,
        include_forecast,
        format_type="text",
    )
