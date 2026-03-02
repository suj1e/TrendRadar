## 1. 基础设施

- [x] 1.1 创建 `trendradar/weather/` 模块目录结构
- [x] 1.2 在 `config/config.yaml` 中添加 weather 配置节模板
- [x] 1.3 更新 `trendradar/core/loader.py` 加载 weather 配置

## 2. Provider 抽象层

- [x] 2.1 创建 `trendradar/weather/providers/base.py`：定义 WeatherData、ForecastItem、WeatherAlert 数据类
- [x] 2.2 创建 `trendradar/weather/providers/base.py`：定义 WeatherProvider 抽象基类
- [x] 2.3 实现 `trendradar/weather/providers/wttr.py`：wttr.in Provider
- [x] 2.4 实现 `trendradar/weather/providers/qweather.py`：和风天气 Provider
- [x] 2.5 实现 `trendradar/weather/providers/seniverse.py`：心知天气 Provider
- [x] 2.6 实现 `trendradar/weather/providers/openweathermap.py`：OpenWeatherMap Provider
- [x] 2.7 创建 `trendradar/weather/providers/__init__.py`：导出所有 Provider

## 3. 天气获取器

- [x] 3.1 创建 `trendradar/weather/fetcher.py`：实现 WeatherFetcher 类
- [x] 3.2 实现 Provider 工厂方法，根据配置创建 Provider 实例
- [x] 3.3 实现单地点天气获取方法，包含超时和重试逻辑
- [x] 3.4 实现多地点并发获取方法（使用 asyncio）
- [x] 3.5 实现代理支持

## 4. 天气调度器

- [x] 4.1 创建 `trendradar/weather/scheduler.py`：实现 WeatherScheduler 类
- [x] 4.2 实现调度配置解析逻辑
- [x] 4.3 实现当前时间匹配调度时间点的逻辑
- [x] 4.4 实现执行状态存储和去重逻辑
- [x] 4.5 实现跨日重置逻辑

## 5. 天气渲染器

- [x] 5.1 创建 `trendradar/weather/renderer.py`：实现天气内容渲染
- [x] 5.2 实现天气状况到 emoji 图标的映射
- [x] 5.3 实现多地点合并消息格式化
- [x] 5.4 实现预报内容格式化
- [x] 5.5 实现不同推送类型的标题生成
- [x] 5.6 实现各渠道格式适配（飞书、钉钉、企微、邮件等）

## 6. 通知集成

- [x] 6.1 在 `trendradar/notification/dispatcher.py` 中添加天气推送方法
- [x] 6.2 实现天气消息复用现有 senders 发送逻辑
- [x] 6.3 实现推送失败处理和日志记录

## 7. 主流程集成

- [x] 7.1 在主程序循环中集成天气调度检查
- [x] 7.2 实现天气推送与新闻推送的并行独立性
- [x] 7.3 添加 weather 模块入口 `trendradar/weather/__init__.py`

## 8. 测试和文档

- [ ] 8.1 编写 Provider 单元测试
- [ ] 8.2 编写 Fetcher 单元测试
- [ ] 8.3 编写 Scheduler 单元测试
- [ ] 8.4 编写 Renderer 单元测试
- [ ] 8.5 更新 README 添加天气配置说明
