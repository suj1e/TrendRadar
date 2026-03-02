# coding=utf-8
"""
wttr.in 天气数据源

免费、无需 API Key 的天气服务。
支持中文，数据格式简单。
"""

import logging
from typing import Optional

import requests

from .base import WeatherProvider, WeatherData, ForecastItem

logger = logging.getLogger(__name__)


# 天气状况到 emoji 的映射
WTTR_CODE_TO_ICON = {
    "113": "☀️",  # Sunny
    "116": "⛅",  # Partly cloudy
    "119": "☁️",  # Cloudy
    "122": "☁️",  # Overcast
    "143": "🌫️",  # Mist
    "176": "🌧️",  # Patchy rain
    "179": "🌨️",  # Patchy snow
    "182": "🌨️",  # Patchy sleet
    "185": "🌨️",  # Patchy freezing drizzle
    "200": "⛈️",  # Thunder
    "227": "❄️",  # Blowing snow
    "230": "❄️",  # Blizzard
    "248": "🌫️",  # Fog
    "260": "🌫️",  # Freezing fog
    "263": "🌧️",  # Patchy light drizzle
    "266": "🌧️",  # Light drizzle
    "281": "🌧️",  # Freezing drizzle
    "284": "🌧️",  # Heavy freezing drizzle
    "293": "🌧️",  # Patchy light rain
    "296": "🌧️",  # Light rain
    "299": "🌧️",  # Moderate rain
    "302": "🌧️",  # Heavy rain
    "305": "🌧️",  # Heavy rain
    "308": "🌧️",  # Heavy rain
    "311": "🌧️",  # Freezing rain
    "314": "🌧️",  # Heavy freezing rain
    "317": "🌨️",  # Sleet
    "320": "🌨️",  # Heavy sleet
    "323": "🌨️",  # Patchy snow
    "326": "🌨️",  # Light snow
    "329": "🌨️",  # Moderate snow
    "332": "❄️",  # Heavy snow
    "335": "❄️",  # Heavy snow
    "338": "❄️",  # Heavy snow
    "350": "🌨️",  # Ice pellets
    "353": "🌧️",  # Rain shower
    "356": "🌧️",  # Heavy rain shower
    "359": "🌧️",  # Torrential rain
    "362": "🌨️",  # Sleet showers
    "365": "🌨️",  # Heavy sleet showers
    "368": "🌨️",  # Snow showers
    "371": "🌨️",  # Heavy snow showers
    "374": "🌨️",  # Ice pellets
    "377": "🌨️",  # Heavy ice pellets
    "386": "⛈️",  # Thunder with rain
    "389": "⛈️",  # Thunder with heavy rain
    "392": "⛈️",  # Thunder with snow
    "395": "⛈️",  # Heavy thunder snow
}

# 默认图标
DEFAULT_ICON = "🌤️"


class WttrProvider(WeatherProvider):
    """wttr.in 天气数据源"""

    name = "wttr"
    requires_api_key = False

    BASE_URL = "https://wttr.in"

    def fetch(
        self,
        location: str,
        lang: str = "zh",
        days: int = 3,
    ) -> WeatherData:
        """
        从 wttr.in 获取天气数据

        Args:
            location: 地点（城市名或坐标）
            lang: 语言代码 (zh, en, etc.)
            days: 预报天数（最多 3 天）

        Returns:
            WeatherData: 统一格式的天气数据
        """
        # wttr.in 最多支持 3 天预报
        days = min(days, 3)

        url = f"{self.BASE_URL}/{location}"
        params = {
            "format": "j1",  # JSON 格式
            "lang": lang,
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

            return self._parse_wttr_data(data, location)

        except requests.RequestException as e:
            logger.error(f"[wttr] 请求失败: {location}, 错误: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"[wttr] 数据解析失败: {location}, 错误: {e}")
            raise

    def _parse_wttr_data(self, data: dict, location: str) -> WeatherData:
        """解析 wttr.in 返回的 JSON 数据"""
        current = data.get("current_condition", [{}])[0]
        area = data.get("nearest_area", [{}])[0]

        # 当前天气
        temp = float(current.get("temp_C", 0))
        feels_like = float(current.get("FeelsLikeC", temp))
        humidity = int(current.get("humidity", 0))
        wind_speed = float(current.get("windspeedKmph", 0))
        wind_dir = current.get("winddir16Point", "")
        weather_code = current.get("weatherCode", "113")
        condition = current.get("lang_zh", [{}])[0].get("value", current.get("weatherDesc", [{}])[0].get("value", "未知"))
        icon = WTTR_CODE_TO_ICON.get(weather_code, DEFAULT_ICON)

        # 能见度和气压
        visibility = float(current.get("visibility", 0)) if current.get("visibility") else None
        pressure = float(current.get("pressure", 0)) if current.get("pressure") else None

        # 地点名称
        location_name = area.get("areaName", [{}])[0].get("value", location)

        # 预报数据
        forecast_items = []
        weather_data = data.get("weather", [])
        for day_data in weather_data:
            hourly = day_data.get("hourly", [{}])[0] if day_data.get("hourly") else {}
            forecast_code = hourly.get("weatherCode", "113")

            forecast_items.append(ForecastItem(
                date=day_data.get("date", ""),
                temp_high=float(day_data.get("maxtempC", 0)),
                temp_low=float(day_data.get("mintempC", 0)),
                condition=hourly.get("lang_zh", [{}])[0].get("value", hourly.get("weatherDesc", [{}])[0].get("value", "未知")) if hourly else "未知",
                icon=WTTR_CODE_TO_ICON.get(forecast_code, DEFAULT_ICON),
                rain_prob=int(hourly.get("chanceofrain", 0)) if hourly.get("chanceofrain") else None,
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
