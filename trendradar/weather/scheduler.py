# coding=utf-8
"""
天气调度器

独立于新闻调度系统，按配置的时间点触发天气推送。
"""

import logging
from dataclasses import dataclass
from datetime import datetime, time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WeatherScheduleItem:
    """天气调度项"""
    time: str                           # 推送时间 (HH:MM)
    schedule_type: str                  # 推送类型 (morning, evening, tomorrow)
    include_forecast: bool              # 是否包含预报
    locations: List[str]                # 推送地点（为空则推送所有）


@dataclass
class WeatherScheduleResult:
    """调度检查结果"""
    should_push: bool                   # 是否应该推送
    schedule_item: Optional[WeatherScheduleItem] = None  # 命中的调度项
    already_executed: bool = False      # 是否当天已执行


class WeatherScheduler:
    """
    天气调度器

    简单的基于时间点的调度，每天在指定时间触发天气推送。
    支持：
    - 多个推送时间点
    - 每个时间点独立配置
    - 执行去重（每天每个时间点只执行一次）
    """

    def __init__(
        self,
        weather_config: Dict[str, Any],
        storage_backend: Any,
        get_time_func: Callable[[], datetime],
    ):
        """
        初始化天气调度器

        Args:
            weather_config: config.yaml 中的 weather 段
            storage_backend: 存储后端（用于执行去重记录）
            get_time_func: 获取当前时间的函数（应使用配置的时区）
        """
        self.config = weather_config
        self.storage = storage_backend
        self.get_time = get_time_func
        self.enabled = weather_config.get("ENABLED", False)

        # 解析调度配置
        self.schedules = self._parse_schedules(weather_config)

    def _parse_schedules(self, weather_config: Dict[str, Any]) -> List[WeatherScheduleItem]:
        """解析调度配置"""
        push_config = weather_config.get("PUSH", {})
        schedule_list = push_config.get("SCHEDULE", [])

        schedules = []
        for item in schedule_list:
            if not item.get("time"):
                continue

            schedules.append(WeatherScheduleItem(
                time=item.get("time", "08:00"),
                schedule_type=item.get("type", "morning"),
                include_forecast=item.get("include_forecast", True),
                locations=item.get("locations", []),
            ))

        return schedules

    def check(self) -> WeatherScheduleResult:
        """
        检查当前时间是否应该触发天气推送

        Returns:
            WeatherScheduleResult: 调度检查结果
        """
        if not self.enabled:
            return WeatherScheduleResult(should_push=False)

        if not self.schedules:
            return WeatherScheduleResult(should_push=False)

        now = self.get_time()
        current_time = now.strftime("%H:%M")
        date_str = now.strftime("%Y-%m-%d")

        # 查找匹配的调度项
        for schedule in self.schedules:
            if self._time_matches(current_time, schedule.time):
                # 检查是否已执行
                if self._already_executed(schedule.time, date_str):
                    return WeatherScheduleResult(
                        should_push=False,
                        schedule_item=schedule,
                        already_executed=True,
                    )

                # 记录执行
                self._record_execution(schedule.time, date_str)

                return WeatherScheduleResult(
                    should_push=True,
                    schedule_item=schedule,
                    already_executed=False,
                )

        return WeatherScheduleResult(should_push=False)

    def _time_matches(self, current: str, target: str) -> bool:
        """
        检查当前时间是否匹配目标时间

        精确匹配到分钟级别，允许 1 分钟的误差（用于处理循环检查的延迟）
        """
        try:
            current_minutes = self._time_to_minutes(current)
            target_minutes = self._time_to_minutes(target)

            # 允许 1 分钟的误差
            return abs(current_minutes - target_minutes) <= 1
        except ValueError:
            return False

    def _time_to_minutes(self, time_str: str) -> int:
        """将时间字符串转换为分钟数"""
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"无效的时间格式: {time_str}")
        return int(parts[0]) * 60 + int(parts[1])

    def _already_executed(self, schedule_time: str, date_str: str) -> bool:
        """检查指定调度项当天是否已执行"""
        key = f"weather_{schedule_time}"
        return self.storage.has_period_executed(date_str, key, "push")

    def _record_execution(self, schedule_time: str, date_str: str) -> None:
        """记录调度项执行"""
        key = f"weather_{schedule_time}"
        self.storage.record_period_execution(date_str, key, "push")
        logger.info(f"[WeatherScheduler] 记录执行: {date_str} {schedule_time}")

    def get_all_locations(self) -> List[Dict[str, Any]]:
        """获取所有配置的地点"""
        return self.config.get("LOCATIONS", [])

    def get_enabled_locations(self) -> List[Dict[str, Any]]:
        """获取所有启用的地点"""
        locations = self.get_all_locations()
        return [loc for loc in locations if loc.get("enabled", True)]

    def get_locations_for_schedule(self, schedule: WeatherScheduleItem) -> List[Dict[str, Any]]:
        """
        获取指定调度项应推送的地点

        如果调度项指定了 locations，则使用指定的；
        否则使用所有启用的地点。
        """
        if schedule.locations:
            # 使用调度项指定的地点
            all_locations = self.get_all_locations()
            location_names = set(schedule.locations)
            return [
                loc for loc in all_locations
                if loc.get("name") in location_names
            ]
        else:
            # 使用所有启用的地点
            return self.get_enabled_locations()
