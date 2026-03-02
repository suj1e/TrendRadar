# coding=utf-8
"""
OpenWeatherMap 天气数据源

国际化支持好，需要 API Key。
免费版：1000 次/天
"""

import logging
from typing import Optional

import requests

from .base import WeatherProvider, WeatherData, ForecastItem

logger = logging.getLogger(__name__)


# 天气图标映射（OpenWeatherMap icon code）
OWM_ICON_MAP = {
    "01d": "☀️",  # clear sky (day)
    "01n": "🌙",  # clear sky (night)
    "02d": "⛅",  # few clouds (day)
    "02n": "☁️",  # few clouds (night)
    "03d": "☁️",  # scattered clouds
    "03n": "☁️",  # scattered clouds
    "04d": "☁️",  # broken clouds
    "04n": "☁️",  # broken clouds
    "09d": "🌧️",  # shower rain
    "09n": "🌧️",  # shower rain
    "10d": "🌦️",  # rain (day)
    "10n": "🌧️",  # rain (night)
    "11d": "⛈️",  # thunderstorm
    "11n": "⛈️",  # thunderstorm
    "13d": "❄️",  # snow
    "13n": "❄️",  # snow
    "50d": "🌫️",  # mist
    "50n": "🌫️",  # mist
}

DEFAULT_ICON = "🌤️"


class OpenWeatherMapProvider(WeatherProvider):
    """OpenWeatherMap 天气数据源"""

    name = "openweathermap"
    requires_api_key = True

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def fetch(
        self,
        location: str,
        lang: str = "zh",
        days: int = 3,
    ) -> WeatherData:
        """
        从 OpenWeatherMap 获取天气数据

        Args:
            location: 地点（城市名或坐标，如 "Beijing" 或 "39.92,116.41"）
            lang: 语言代码 (zh, en)
            days: 预报天数（最多 5 天）

        Returns:
            WeatherData: 统一格式的天气数据
        """
        if not self.api_key:
            raise ValueError("[openweathermap] API Key 未配置")

        # 获取当前天气
        now_data = self._fetch_current(location, lang)

        # 获取预报
        forecast_data = self._fetch_forecast(location, lang)

        return self._parse_owm_data(now_data, forecast_data, location, days)

    def _fetch_current(self, location: str, lang: str) -> dict:
        """获取当前天气"""
        url = f"{self.BASE_URL}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
            "lang": lang,
        }

        # 支持坐标格式
        if "," in location and location.replace(",", "").replace(".", "").replace("-", "").isdigit():
            lat, lon = location.split(",")
            params = {
                "lat": lat.strip(),
                "lon": lon.strip(),
                "appid": self.api_key,
                "units": "metric",
                "lang": lang,
            }

        response = requests.get(
            url,
            params=params,
            proxies=self.get_proxies(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _fetch_forecast(self, location: str, lang: str) -> dict:
        """获取天气预报（5天/3小时预报）"""
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
            "lang": lang,
            "cnt": 40,  # 5天 x 8个时间段
        }

        # 支持坐标格式
        if "," in location and location.replace(",", "").replace(".", "").replace("-", "").isdigit():
            lat, lon = location.split(",")
            params = {
                "lat": lat.strip(),
                "lon": lon.strip(),
                "appid": self.api_key,
                "units": "metric",
                "lang": lang,
                "cnt": 40,
            }

        try:
            response = requests.get(
                url,
                params=params,
                proxies=self.get_proxies(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"[openweathermap] 预报请求失败: {e}")
            return {"list": []}

    def _parse_owm_data(self, now_data: dict, forecast_data: dict, location: str, days: int) -> WeatherData:
        """解析 OpenWeatherMap 返回的数据"""
        main = now_data.get("main", {})
        weather = now_data.get("weather", [{}])[0]
        wind = now_data.get("wind", {})
        sys = now_data.get("sys", {})

        temp = float(main.get("temp", 0))
        feels_like = float(main.get("feels_like", temp))
        humidity = int(main.get("humidity", 0))
        wind_speed = float(wind.get("speed", 0))
        # 风向转换（度数转方位）
        wind_deg = wind.get("deg", 0)
        wind_dir = self._deg_to_direction(wind_deg)
        condition = weather.get("description", "未知")
        icon_code = weather.get("icon", "01d")
        icon = OWM_ICON_MAP.get(icon_code, DEFAULT_ICON)

        visibility = float(now_data.get("visibility", 0)) / 1000 if now_data.get("visibility") else None  # 转为 km
        pressure = float(main.get("pressure", 0)) if main.get("pressure") else None

        # 地点名称
        location_name = now_data.get("name", location)

        # 预报数据（按天聚合）
        forecast_items = self._aggregate_forecast_by_day(forecast_data, days)

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
            raw_data={"now": now_data, "forecast": forecast_data},
        )

    def _deg_to_direction(self, deg: int) -> str:
        """将风向角度转换为方位"""
        directions = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
        index = round(deg / 45) % 8
        return directions[index]

    def _aggregate_forecast_by_day(self, forecast_data: dict, days: int) -> list:
        """将 3 小时预报聚合成每日预报"""
        from collections import defaultdict
        from datetime import datetime

        daily_data = defaultdict(list)

        for item in forecast_data.get("list", []):
            dt = datetime.fromtimestamp(item.get("dt", 0))
            date_str = dt.strftime("%Y-%m-%d")
            daily_data[date_str].append(item)

        forecast_items = []
        for i, (date_str, items) in enumerate(sorted(daily_data.items())):
            if i >= days:
                break

            temps = [item.get("main", {}).get("temp", 0) for item in items]
            temp_high = max(temps) if temps else 0
            temp_low = min(temps) if temps else 0

            # 使用中午时段的天气状况
            midday_item = items[len(items) // 2] if items else {}
            weather = midday_item.get("weather", [{}])[0]
            icon_code = weather.get("icon", "01d")

            forecast_items.append(ForecastItem(
                date=date_str,
                temp_high=temp_high,
                temp_low=temp_low,
                condition=weather.get("description", "未知"),
                icon=OWM_ICON_MAP.get(icon_code, DEFAULT_ICON),
                rain_prob=None,
            ))

        return forecast_items
