## Context

TrendRadar 是一个新闻聚合和推送系统，已有完善的多渠道通知基础设施。用户希望在此基础上增加天气通知功能，以便在同一渠道同时接收新闻和天气信息。

**现有架构特点：**
- 通知系统支持 9 种渠道（飞书、钉钉、企微、邮件等）
- 调度系统基于 periods + day_plans + week_map 模型
- 配置通过 YAML 文件管理

**设计约束：**
- 天气模块必须独立于新闻系统，不影响现有功能
- 复用现有通知发送器，不新增通知渠道
- 零配置即可使用（默认使用 wttr.in）
- 支持多地点、多数据源

## Goals / Non-Goals

**Goals:**
- 提供可插拔的天气数据源抽象，支持 wttr.in、和风天气、心知天气、OpenWeatherMap
- 实现独立于新闻推送的天气调度系统
- 支持多地点天气查询，合并为单条消息推送
- 天气消息格式适配所有现有通知渠道

**Non-Goals:**
- 不实现天气预警推送（可作为后续扩展）
- 不修改现有新闻采集和推送流程
- 不新增通知渠道
- 不实现天气相关的 AI 分析

## Decisions

### D1: 天气模块独立目录结构

**决定：** 在 `trendradar/weather/` 下创建独立模块

**理由：**
- 与 `crawler/`、`notification/`、`ai/` 等模块平级，职责清晰
- 便于后续独立测试和维护
- 不污染现有代码结构

**目录结构：**
```
trendradar/weather/
├── __init__.py
├── providers/           # 数据源实现
│   ├── __init__.py
│   ├── base.py
│   ├── wttr.py
│   ├── qweather.py
│   ├── seniverse.py
│   └── openweathermap.py
├── fetcher.py          # 统一获取接口
├── renderer.py         # 消息渲染
└── scheduler.py        # 独立调度
```

### D2: Provider 抽象设计

**决定：** 使用抽象基类定义统一接口

**核心数据结构：**
```python
@dataclass
class WeatherData:
    location: str           # 地点名称
    temp: float             # 当前温度
    feels_like: float       # 体感温度
    humidity: int           # 湿度
    condition: str          # 天气状况
    icon: str               # 天气图标
    forecast: List[ForecastItem]  # 预报数据
```

**Provider 接口：**
```python
class WeatherProvider(ABC):
    name: str
    requires_api_key: bool

    def fetch(self, location: str, lang: str) -> WeatherData
```

**备选方案：** 直接调用各 API 不抽象
- **放弃原因：** 无法支持多源切换，难以测试

### D3: wttr.in 作为默认 Provider

**决定：** 默认使用 wttr.in，零配置可用

**理由：**
- 无需 API Key，开箱即用
- 免费无请求限制
- 支持中文
- 数据格式简单

**其他 Provider 配置：**
```yaml
weather:
  provider: "wttr"  # 默认
  providers:
    qweather:
      api_key: "xxx"
```

### D4: 合并消息推送

**决定：** 所有地点天气合并为一条消息

**消息格式示例：**
```
🌤️ 晨间天气

📍 北京 18°C 晴转多云
   今日 12~22°C，午后有阵雨

📍 上海 20°C 多云
   今日 16~24°C，晴
```

**备选方案：** 每地点独立消息
- **放弃原因：** 多地点时消息过多，打扰用户

### D5: 独立调度系统

**决定：** 天气使用独立调度配置，不复用 timeline.yaml

**理由：**
- 天气推送节奏与新闻不同（可能每天 1-2 次 vs 新闻可能更频繁）
- 避免配置耦合，保持简洁
- 天气调度逻辑简单，不需要 periods 那么复杂

**调度配置：**
```yaml
weather:
  schedule:
    - time: "07:00"
      type: "morning"
      include_forecast: true
    - time: "18:00"
      type: "evening"
      include_forecast: false
```

### D6: 复用现有通知发送器

**决定：** 不新增发送逻辑，复用 `notification/senders.py`

**实现方式：**
- 天气渲染器生成各渠道格式的内容
- 调用现有 `send_to_feishu()`、`send_to_dingtalk()` 等函数
- 利用现有的消息分批、格式转换能力

## Risks / Trade-offs

### R1: wttr.in 稳定性风险

**风险：** wttr.in 是免费服务，可能存在可用性问题

**缓解：**
- 实现多 Provider 支持，用户可配置备用源
- 添加超时和重试机制
- 推送失败时优雅降级（记录日志，不阻塞主流程）

### R2: API 配额限制

**风险：** 商业天气 API 有请求配额限制

**缓解：**
- 默认使用无限制的 wttr.in
- 在文档中说明各 Provider 的配额
- 建议用户根据地点数量和推送频率选择合适的 Provider

### R3: 多地点请求延迟

**风险：** 多地点时需要串行请求多个 API，可能较慢

**缓解：**
- 使用 `asyncio` 并发请求
- 设置合理的超时时间（单请求 10s）
- 超时地点跳过，不影响其他地点

### R4: 时区问题

**风险：** "07:00" 推送在不同时区含义不同

**缓解：**
- 使用系统本地时区
- 配置文件中可指定时区（后续扩展）
