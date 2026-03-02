# coding=utf-8
"""
天气通知模块

提供天气数据获取、调度和推送功能。
"""

from .providers import (
    WeatherProvider,
    WeatherData,
    ForecastItem,
    WeatherAlert,
    WttrProvider,
    QWeatherProvider,
    SeniverseProvider,
    OpenWeatherMapProvider,
    PROVIDERS,
    get_provider,
)
from .fetcher import WeatherFetcher
from .scheduler import WeatherScheduler, WeatherScheduleResult, WeatherScheduleItem
from .renderer import (
    render_weather_content,
    render_weather_feishu,
    render_weather_dingtalk,
    render_weather_wework,
    render_weather_telegram,
    render_weather_email,
    render_weather_slack,
    render_weather_ntfy,
    render_weather_bark,
    get_schedule_title,
)

__all__ = [
    # Provider
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
    # Fetcher
    "WeatherFetcher",
    # Scheduler
    "WeatherScheduler",
    "WeatherScheduleResult",
    "WeatherScheduleItem",
    # Renderer
    "render_weather_content",
    "render_weather_feishu",
    "render_weather_dingtalk",
    "render_weather_wework",
    "render_weather_telegram",
    "render_weather_email",
    "render_weather_slack",
    "render_weather_ntfy",
    "render_weather_bark",
    "get_schedule_title",
]


def run_weather_push(
    config: dict,
    storage_backend,
    dispatcher,
    get_time_func,
    proxy_url: str = None,
) -> dict:
    """
    执行天气推送（主入口）

    Args:
        config: 配置字典
        storage_backend: 存储后端
        dispatcher: 通知调度器
        get_time_func: 获取当前时间的函数
        proxy_url: 代理 URL

    Returns:
        dict: 推送结果
    """
    import logging
    from .scheduler import WeatherScheduler
    from .fetcher import WeatherFetcher
    from .providers import WeatherData

    logger = logging.getLogger(__name__)

    weather_config = config.get("WEATHER", {})
    if not weather_config.get("ENABLED", False):
        return {}

    # 初始化调度器
    scheduler = WeatherScheduler(
        weather_config=weather_config,
        storage_backend=storage_backend,
        get_time_func=get_time_func,
    )

    # 检查是否需要推送
    result = scheduler.check()
    if not result.should_push:
        return {}

    logger.info(f"[天气] 触发推送: {result.schedule_item.time}")

    # 获取需要推送的地点
    locations_config = scheduler.get_locations_for_schedule(result.schedule_item)
    if not locations_config:
        logger.warning("[天气] 没有配置地点")
        return {}

    # 初始化获取器
    provider_name = weather_config.get("PROVIDER", "wttr")
    provider_config = weather_config.get("PROVIDERS", {}).get(provider_name, {})

    fetcher = WeatherFetcher(
        provider_name=provider_name,
        provider_config=provider_config,
        proxy_url=proxy_url,
    )

    # 获取天气数据
    queries = [loc.get("query", loc.get("name", "")) for loc in locations_config]
    fetch_results = fetcher.fetch_multiple(queries)

    # 提取成功的数据
    weather_data_list = []
    for location, data, error in fetch_results:
        if data:
            # 使用配置中的名称
            loc_config = next(
                (loc for loc in locations_config if loc.get("query", loc.get("name", "")) == location),
                {"name": location}
            )
            data.location = loc_config.get("name", location)
            weather_data_list.append(data)
        elif error:
            logger.error(f"[天气] 获取 {location} 天气失败: {error}")

    if not weather_data_list:
        logger.warning("[天气] 没有成功获取任何地点的天气数据")
        return {}

    # 推送通知
    schedule_item = result.schedule_item
    push_results = dispatcher.dispatch_weather(
        weather_data_list=weather_data_list,
        schedule_type=schedule_item.schedule_type,
        include_forecast=schedule_item.include_forecast,
        proxy_url=proxy_url,
        custom_channels=weather_config.get("PUSH", {}).get("CHANNELS", {}),
    )

    # 打印结果
    success_channels = [k for k, v in push_results.items() if v]
    failed_channels = [k for k, v in push_results.items() if not v]

    if success_channels:
        print(f"✅ 天气通知发送成功: {', '.join(success_channels)}")
    if failed_channels:
        print(f"❌ 天气通知发送失败: {', '.join(failed_channels)}")

    return push_results
