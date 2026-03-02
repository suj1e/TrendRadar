# coding=utf-8
"""
心知天气数据源

国内数据准确，需要 API Key。
免费版：400 次/天
"""

import logging
from typing import Optional

import requests

from .base import WeatherProvider, WeatherData, ForecastItem

logger = logging.getLogger(__name__)


# 天气代码到 emoji 的映射
SENIVERSE_CODE_TO_ICON = {
    "0": "☀️",   # 晴
    "1": "☁️",   # 多云
    "2": "☁️",   # 阴
    "3": "🌧️",   # 阵雨
    "4": "⛈️",   # 雷阵雨
    "5": "⛈️",   # 雷阵雨伴有冰雹
    "6": "🌨️",   # 雨夹雪
    "7": "🌨️",   # 小雨
    "8": "🌧️",   # 中雨
    "9": "🌧️",   # 大雨
    "10": "⛈️",  # 暴雨
    "11": "⛈️",  # 大暴雨
    "12": "⛈️",  # 特大暴雨
    "13": "🌨️",  # 阵雪
    "14": "🌨️",  # 小雪
    "15": "🌨️",  # 中雪
    "16": "❄️",  # 大雪
    "17": "❄️",  # 暴雪
    "18": "🌫️",  # 雾
    "19": "🌨️",  # 冻雨
    "20": "🌫️",  # 沙尘暴
    "21": "🌨️",  # 小到中雨
    "22": "🌧️",  # 中到大雨
    "23": "⛈️",  # 大到暴雨
    "24": "⛈️",  # 暴雨到大暴雨
    "25": "⛈️",  # 大暴雨到特大暴雨
    "26": "🌨️",  # 小到中雪
    "27": "🌨️",  # 中到大雪
    "28": "❄️",  # 大到暴雪
    "29": "🌫️",  # 浮尘
    "30": "🌫️",  # 扬沙
    "31": "🌪️",  # 强沙尘暴
    "32": "🌫️",  # 霾
    "99": "❓",  # 未知
}

DEFAULT_ICON = "🌤️"


class SeniverseProvider(WeatherProvider):
    """心知天气数据源"""

    name = "seniverse"
    requires_api_key = True

    BASE_URL = "https://api.seniverse.com/v4"

    def fetch(
        self,
        location: str,
        lang: str = "zh",
        days: int = 3,
    ) -> WeatherData:
        """
        从心知天气获取天气数据

        Args:
            location: 地点（城市名或坐标）
            lang: 语言代码 (zh, en)
            days: 预报天数（最多 3 天）

        Returns:
            WeatherData: 统一格式的天气数据
        """
        if not self.api_key:
            raise ValueError("[seniverse] API Key 未配置")

        # 获取当前天气和预报
        data = self._fetch_weather(location, lang, days)
        return self._parse_seniverse_data(data, location)

    def _fetch_weather(self, location: str, lang: str, days: int) -> dict:
        """获取天气数据（心知天气支持一次性获取当前和预报）"""
        url = f"{self.BASE_URL}/weather.json"
        params = {
            "key": self.api_key,
            "location": location,
            "language": lang,
            "unit": "c",
        }

        try:
            response = requests.get(
                url,
                params=params,
                proxies=self.get_proxies(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                raise ValueError(f"[seniverse] API 错误: {data.get('status')}")

            return data

        except requests.RequestException as e:
            logger.error(f"[seniverse] 请求失败: {location}, 错误: {e}")
            raise

    def _parse_seniverse_data(self, data: dict, location: str) -> WeatherData:
        """解析心知天气返回的数据"""
        now = data.get("now", {})
        location_info = data.get("location", {})

        temp = float(now.get("temperature", 0))
        # 心知天气没有体感温度，使用实际温度
        feels_like = temp
        humidity = int(now.get("humidity", 0))
        # 心知天气风速单位不同，需要转换
        wind_speed = float(now.get("wind_speed", 0))
        wind_dir = now.get("wind_direction", "")
        weather_code = now.get("code", "0")
        condition = now.get("text", "未知")
        icon = SENIVERSE_CODE_TO_ICON.get(weather_code, DEFAULT_ICON)

        visibility = float(now.get("visibility", 0)) if now.get("visibility") else None
        pressure = float(now.get("pressure", 0)) if now.get("pressure") else None

        # 地点名称
        location_name = location_info.get("text", location)

        # 预报数据（心知天气免费版支持 3 天预报）
        forecast_items = []
        daily = data.get("daily", [])
        for day_data in daily:
            forecast_items.append(ForecastItem(
                date=day_data.get("date", ""),
                temp_high=float(day_data.get("high", 0)),
                temp_low=float(day_data.get("low", 0)),
                condition=day_data.get("text_day", "未知"),
                icon=SENIVERSE_CODE_TO_ICON.get(day_data.get("code_day", "0"), DEFAULT_ICON),
                rain_prob=None,  # 心知天气不提供降水概率
            ))

        return WeatherData(
            location=location_name,
            temp=temp,
            feels_like=feels_like,
            humidity=humidity,
            wind_speed=wind_speed,
            wind_dir=wind_dir,
            condition=condition,
            icon=icon,
            visibility=visibility,
            pressure=pressure,
            forecast=forecast_items,
            raw_data=data,
        )
