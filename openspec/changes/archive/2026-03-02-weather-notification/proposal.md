## Why

TrendRadar 用户在接收新闻推送的同时，往往也需要了解天气信息来安排日常活动。当前系统缺乏天气通知能力，用户需要单独查看天气应用。通过在 TrendRadar 中集成天气通知，可以复用现有的多渠道推送基础设施，为用户提供一站式的信息推送服务。

## What Changes

- 新增天气通知模块，支持定时推送天气信息
- 支持多地点天气查询和推送
- 支持多个天气数据源（wttr.in、和风天气、心知天气、OpenWeatherMap）
- 天气推送独立于新闻推送，有独立的调度配置
- 所有地点合并为一条消息推送，复用现有通知渠道

## Capabilities

### New Capabilities

- `weather-provider`: 天气数据源抽象层，定义统一的天气数据获取接口，支持多种天气 API 的可插拔实现
- `weather-scheduler`: 天气独立调度系统，支持多时间点的定时天气推送
- `weather-notification`: 天气通知渲染和推送，将天气数据格式化为各渠道支持的消息格式

### Modified Capabilities

- 无。天气模块完全独立，不修改现有能力的需求。

## Impact

### 新增文件

```
trendradar/weather/
├── __init__.py
├── providers/
│   ├── __init__.py
│   ├── base.py           # Provider 基类和数据结构
│   ├── wttr.py           # wttr.in 实现
│   ├── qweather.py       # 和风天气实现
│   ├── seniverse.py      # 心知天气实现
│   └── openweathermap.py # OpenWeatherMap 实现
├── fetcher.py            # 天气数据获取器
├── renderer.py           # 天气内容渲染器
└── scheduler.py          # 天气调度器
```

### 配置变更

- `config/config.yaml` 新增 `weather` 配置节

### 依赖

- `requests`（已有）
- 无新增外部依赖
