## ADDED Requirements

### Requirement: Provider 抽象接口

系统 SHALL 提供统一的天气数据源抽象接口，支持多种天气 API 的可插拔实现。

#### Scenario: 获取 wttr.in 天气数据
- **WHEN** 配置 provider 为 wttr 且未配置 api_key
- **THEN** 系统使用 wttr.in 免费接口获取天气数据

#### Scenario: 获取和风天气数据
- **WHEN** 配置 provider 为 qweather 且配置了有效 api_key
- **THEN** 系统使用和风天气 API 获取天气数据

#### Scenario: Provider 切换
- **WHEN** 用户修改配置中的 provider 字段
- **THEN** 系统在下次请求时使用新的 Provider 获取数据

### Requirement: 统一天气数据结构

系统 SHALL 将不同 Provider 返回的数据转换为统一的 WeatherData 结构。

#### Scenario: wttr.in 数据转换
- **WHEN** 从 wttr.in 获取到原始天气数据
- **THEN** 系统转换为包含 location、temp、feels_like、humidity、condition、icon、forecast 字段的 WeatherData 对象

#### Scenario: 数据字段缺失处理
- **WHEN** Provider 返回的数据缺少某些可选字段（如 visibility、pressure）
- **THEN** 系统将缺失字段设为 None，不影响其他字段的正常使用

### Requirement: 多地点天气获取

系统 SHALL 支持同时获取多个地点的天气数据。

#### Scenario: 获取多地点天气
- **WHEN** 配置了多个 location（如北京、上海）
- **THEN** 系统返回每个地点的天气数据列表

#### Scenario: 单地点失败不影响其他
- **WHEN** 获取某个地点天气失败（如城市名错误）
- **THEN** 系统记录错误日志，继续返回其他成功获取的地点数据

#### Scenario: 并发获取
- **WHEN** 配置了多个地点
- **THEN** 系统使用并发请求提高获取效率

### Requirement: 请求超时和重试

系统 SHALL 对天气 API 请求设置超时和重试机制。

#### Scenario: 请求超时
- **WHEN** 天气 API 响应时间超过 10 秒
- **THEN** 系统取消请求并返回超时错误

#### Scenario: 请求重试
- **WHEN** 天气 API 请求失败（网络错误、5xx 错误）
- **THEN** 系统最多重试 2 次，重试间隔 1 秒

### Requirement: 代理支持

系统 SHALL 支持通过代理访问天气 API。

#### Scenario: 使用代理
- **WHEN** 配置了全局代理 proxy_url
- **THEN** 天气 API 请求通过代理发送
