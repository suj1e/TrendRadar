# coding=utf-8
"""
天气数据源模块

提供多种天气 API 的可插拔实现。
"""

from .base import WeatherProvider, WeatherData, ForecastItem, WeatherAlert
from .wttr import WttrProvider
from .qweather import QWeatherProvider
from .seniverse import SeniverseProvider
from .openweathermap import OpenWeatherMapProvider

# Provider 注册表
PROVIDERS = {
    "wttr": WttrProvider,
    "qweather": QWeatherProvider,
    "seniverse": SeniverseProvider,
    "openweathermap": OpenWeatherMapProvider,
}


def get_provider(name: str) -> type:
    """
    获取 Provider 类

    Args:
        name: Provider 名称

    Returns:
        Provider 类

    Raises:
        ValueError: 不支持的 Provider
    """
    if name not in PROVIDERS:
        raise ValueError(f"不支持的天气数据源: {name}，支持的: {list(PROVIDERS.keys())}")
    return PROVIDERS[name]


__all__ = [
    "WeatherProvider",
    "WeatherData",
    "ForecastItem",
    "WeatherAlert",
    "WttrProvider",
    "QWeatherProvider",
    "SeniverseProvider",
    "OpenWeatherMapProvider",
    "PROVIDERS",
    "get_provider",
]
