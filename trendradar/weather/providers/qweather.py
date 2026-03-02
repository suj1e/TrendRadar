# coding=utf-8
"""
和风天气数据源

国内数据准确，需要 API Key。
免费版：1000 次/天
"""

import logging
from typing import Optional

import requests

from .base import WeatherProvider, WeatherData, ForecastItem

logger = logging.getLogger(__name__)


# 天气代码到 emoji 的映射
QWEATHER_CODE_TO_ICON = {
    "100": "☀️",  # 晴
    "101": "☁️",  # 多云
    "102": "⛅",  # 少云
    "103": "⛅",  # 晴间多云
    "104": "☁️",  # 阴
    "150": "☀️",  # 晴（夜间）
    "151": "☁️",  # 多云（夜间）
    "152": "⛅",  # 少云（夜间）
    "153": "⛅",  # 晴间多云（夜间）
    "300": "🌦️",  # 阵雨
    "301": "⛈️",  # 强阵雨
    "302": "⛈️",  # 雷阵雨
    "303": "⛈️",  # 强雷阵雨
    "304": "⛈️",  # 雷阵雨伴有冰雹
    "305": "🌧️",  # 小雨
    "306": "🌧️",  # 中雨
    "307": "🌧️",  # 大雨
    "308": "🌧️",  # 极端降雨
    "309": "🌧️",  # 毛毛雨
    "310": "⛈️",  # 暴雨
    "311": "⛈️",  # 大暴雨
    "312": "⛈️",  # 特大暴雨
    "313": "🌧️",  # 冻雨
    "314": "🌧️",  # 小到中雨
    "315": "🌧️",  # 中到大雨
    "316": "⛈️",  # 大到暴雨
    "317": "⛈️",  # 暴雨到大暴雨
    "318": "⛈️",  # 大暴雨到特大暴雨
    "399": "🌧️",  # 雨
    "400": "🌨️",  # 小雪
    "401": "🌨️",  # 中雪
    "402": "❄️",  # 大雪
    "403": "❄️",  # 暴雪
    "404": "🌨️",  # 雨夹雪
    "405": "🌨️",  # 雨雪天气
    "406": "🌨️",  # 阵雨夹雪
    "407": "🌨️",  # 阵雪
    "408": "🌨️",  # 小到中雪
    "409": "🌨️",  # 中到大雪
    "410": "❄️",  # 大到暴雪
    "499": "🌨️",  # 雪
    "500": "🌫️",  # 薄雾
    "501": "🌫️",  # 雾
    "502": "🌫️",  # 霾
    "503": "🌬️",  # 扬沙
    "504": "🌬️",  # 扬沙
    "507": "🌪️",  # 沙尘暴
    "508": "🌪️",  # 强沙尘暴
    "509": "🌫️",  # 浓雾
    "510": "🌫️",  # 强浓雾
    "511": "🌫️",  # 中度霾
    "512": "🌫️",  # 重度霾
    "513": "🌫️",  # 严重霾
    "514": "🌫️",  # 大雾
    "515": "🌫️",  # 特强浓雾
    "900": "🌡️",  # 热
    "901": "🌡️",  # 冷
    "999": "❓",  # 未知
}

DEFAULT_ICON = "🌤️"


class QWeatherProvider(WeatherProvider):
    """和风天气数据源"""

    name = "qweather"
    requires_api_key = True

    BASE_URL = "https://devapi.qweather.com/v7"

    def fetch(
        self,
        location: str,
        lang: str = "zh",
        days: int = 3,
    ) -> WeatherData:
        """
        从和风天气获取天气数据

        Args:
            location: 地点（城市 ID 或坐标，如 "101010100" 或 "116.41,39.92"）
            lang: 语言代码 (zh, en)
            days: 预报天数（最多 7 天）

        Returns:
            WeatherData: 统一格式的天气数据
        """
        if not self.api_key:
            raise ValueError("[qweather] API Key 未配置")

        # 获取当前天气
        now_data = self._fetch_now(location, lang)

        # 获取预报
        forecast_data = self._fetch_forecast(location, lang, days)

        return self._parse_qweather_data(now_data, forecast_data, location)

    def _fetch_now(self, location: str, lang: str) -> dict:
        """获取当前天气"""
        url = f"{self.BASE_URL}/weather/now"
        params = {
            "location": location,
            "key": self.api_key,
            "lang": lang,
        }

        response = requests.get(
            url,
            params=params,
            proxies=self.get_proxies(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200":
            raise ValueError(f"[qweather] API 错误: {data.get('code')}")

        return data

    def _fetch_forecast(self, location: str, lang: str, days: int) -> dict:
        """获取天气预报"""
        # 选择预报 API（3天、7天）
        if days <= 3:
            endpoint = "3d"
        else:
            endpoint = "7d"

        url = f"{self.BASE_URL}/weather/{endpoint}"
        params = {
            "location": location,
            "key": self.api_key,
            "lang": lang,
        }

        response = requests.get(
            url,
            params=params,
            proxies=self.get_proxies(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200":
            logger.warning(f"[qweather] 预报 API 错误: {data.get('code')}")
            return {"daily": []}

        return data

    def _parse_qweather_data(self, now_data: dict, forecast_data: dict, location: str) -> WeatherData:
        """解析和风天气返回的数据"""
        now = now_data.get("now", {})

        temp = float(now.get("temp", 0))
        feels_like = float(now.get("feelsLike", temp))
        humidity = int(now.get("humidity", 0))
        wind_speed = float(now.get("windSpeed", 0))
        wind_dir = now.get("windDir", "")
        weather_code = now.get("code", "100")
        condition = now.get("text", "未知")
        icon = QWEATHER_CODE_TO_ICON.get(weather_code, DEFAULT_ICON)

        visibility = float(now.get("vis", 0)) if now.get("vis") else None
        pressure = float(now.get("pressure", 0)) if now.get("pressure") else None

        # 预报数据
        forecast_items = []
        for day_data in forecast_data.get("daily", []):
            forecast_items.append(ForecastItem(
                date=day_data.get("fxDate", ""),
                temp_high=float(day_data.get("tempMax", 0)),
                temp_low=float(day_data.get("tempMin", 0)),
                condition=day_data.get("textDay", "未知"),
                icon=QWEATHER_CODE_TO_ICON.get(day_data.get("codeDay", "100"), DEFAULT_ICON),
                rain_prob=int(day_data.get("precip", 0)) if day_data.get("precip") else None,
            ))

        return WeatherData(
            location=location,
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
            raw_data={"now": now_data, "forecast": forecast_data},
        )
