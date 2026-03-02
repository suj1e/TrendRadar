# coding=utf-8
"""
天气数据源抽象基类和数据结构

定义统一的天气数据格式和 Provider 接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ForecastItem:
    """天气预报项"""
    date: str                           # 日期 (YYYY-MM-DD)
    temp_high: float                    # 最高温度
    temp_low: float                     # 最低温度
    condition: str                      # 天气状况
    icon: str                           # 天气图标 emoji
    rain_prob: Optional[int] = None     # 降水概率 (0-100)


@dataclass
class WeatherData:
    """统一的天气数据结构"""
    location: str                       # 地点名称
    temp: float                         # 当前温度
    feels_like: float                   # 体感温度
    humidity: int                       # 湿度 (%)
    wind_speed: float                   # 风速 (km/h)
    wind_dir: str                       # 风向
    condition: str                      # 天气状况（晴/多云/雨...）
    icon: str                           # 天气图标 emoji
    visibility: Optional[float] = None  # 能见度 (km)
    pressure: Optional[float] = None    # 气压 (hPa)

    # 预报数据（可选）
    forecast: List[ForecastItem] = field(default_factory=list)

    # 原始数据（用于调试）
    raw_data: Optional[dict] = None


@dataclass
class WeatherAlert:
    """天气预警"""
    type: str                           # 预警类型
    level: str                          # 预警级别
    title: str                          # 预警标题
    description: str                    # 预警描述


class WeatherProvider(ABC):
    """天气数据源抽象基类"""

    name: str                           # 数据源名称
    requires_api_key: bool              # 是否需要 API Key

    def __init__(
        self,
        api_key: str = "",
        timeout: int = 10,
        proxy_url: Optional[str] = None,
    ):
        """
        初始化 Provider

        Args:
            api_key: API 密钥（部分 Provider 需要）
            timeout: 请求超时时间（秒）
            proxy_url: 代理 URL
        """
        self.api_key = api_key
        self.timeout = timeout
        self.proxy_url = proxy_url

    @abstractmethod
    def fetch(
        self,
        location: str,
        lang: str = "zh",
        days: int = 3,
    ) -> WeatherData:
        """
        获取天气数据

        Args:
            location: 地点（城市名或坐标）
            lang: 语言代码
            days: 预报天数

        Returns:
            WeatherData: 统一格式的天气数据
        """
        pass

    def get_proxies(self) -> Optional[dict]:
        """获取代理配置"""
        if self.proxy_url:
            return {"http": self.proxy_url, "https": self.proxy_url}
        return None
