# coding=utf-8
"""
天气数据获取器

提供统一的天气数据获取接口，支持多地点并发获取。
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

from .providers import get_provider, WeatherData

logger = logging.getLogger(__name__)


class WeatherFetcher:
    """天气数据获取器"""

    def __init__(
        self,
        provider_name: str = "wttr",
        provider_config: Optional[Dict] = None,
        proxy_url: Optional[str] = None,
        timeout: int = 10,
        max_workers: int = 5,
    ):
        """
        初始化天气获取器

        Args:
            provider_name: 数据源名称
            provider_config: 数据源配置（如 api_key）
            proxy_url: 代理 URL
            timeout: 请求超时（秒）
            max_workers: 并发获取的最大线程数
        """
        self.provider_name = provider_name
        self.provider_config = provider_config or {}
        self.proxy_url = proxy_url
        self.timeout = timeout
        self.max_workers = max_workers

        # 创建 Provider 实例
        self._provider = self._create_provider()

    def _create_provider(self):
        """创建 Provider 实例"""
        provider_class = get_provider(self.provider_name)
        return provider_class(
            api_key=self.provider_config.get("api_key", ""),
            timeout=self.timeout,
            proxy_url=self.proxy_url,
        )

    def fetch_one(
        self,
        location: str,
        lang: str = "zh",
        days: int = 3,
        retries: int = 2,
    ) -> Tuple[str, Optional[WeatherData], Optional[str]]:
        """
        获取单个地点的天气数据

        Args:
            location: 地点
            lang: 语言
            days: 预报天数
            retries: 重试次数

        Returns:
            (location, WeatherData, error_message)
        """
        last_error = None

        for attempt in range(retries + 1):
            try:
                data = self._provider.fetch(location, lang, days)
                logger.info(f"[WeatherFetcher] 成功获取天气: {location}")
                return location, data, None

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"[WeatherFetcher] 获取天气失败: {location}, "
                    f"尝试 {attempt + 1}/{retries + 1}, 错误: {e}"
                )
                if attempt < retries:
                    import time
                    time.sleep(1)  # 重试间隔

        logger.error(f"[WeatherFetcher] 获取天气最终失败: {location}, 错误: {last_error}")
        return location, None, last_error

    def fetch_multiple(
        self,
        locations: List[str],
        lang: str = "zh",
        days: int = 3,
    ) -> List[Tuple[str, Optional[WeatherData], Optional[str]]]:
        """
        并发获取多个地点的天气数据

        Args:
            locations: 地点列表
            lang: 语言
            days: 预报天数

        Returns:
            [(location, WeatherData, error_message), ...]
        """
        if not locations:
            return []

        # 单地点直接获取
        if len(locations) == 1:
            return [self.fetch_one(locations[0], lang, days)]

        # 多地点并发获取
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.fetch_one, loc, lang, days)
                for loc in locations
            ]

            for future in futures:
                try:
                    result = future.result(timeout=self.timeout + 5)
                    results.append(result)
                except Exception as e:
                    logger.error(f"[WeatherFetcher] 并发获取异常: {e}")
                    # 异常情况下添加 None 结果
                    results.append(("", None, str(e)))

        return results

    async def fetch_multiple_async(
        self,
        locations: List[str],
        lang: str = "zh",
        days: int = 3,
    ) -> List[Tuple[str, Optional[WeatherData], Optional[str]]]:
        """
        异步并发获取多个地点的天气数据

        Args:
            locations: 地点列表
            lang: 语言
            days: 预报天数

        Returns:
            [(location, WeatherData, error_message), ...]
        """
        if not locations:
            return []

        loop = asyncio.get_event_loop()

        tasks = [
            loop.run_in_executor(
                None,
                lambda loc=loc: self.fetch_one(loc, lang, days)
            )
            for loc in locations
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[WeatherFetcher] 异步获取异常: {result}")
                processed_results.append((locations[i], None, str(result)))
            else:
                processed_results.append(result)

        return processed_results
