## ADDED Requirements

### Requirement: 独立调度配置

系统 SHALL 为天气推送提供独立的调度配置，与新闻推送调度解耦。

#### Scenario: 配置推送时间
- **WHEN** 用户在 weather.schedule 中配置多个时间点
- **THEN** 系统在每个配置的时间点触发天气推送

#### Scenario: 未配置时默认行为
- **WHEN** weather 配置节未配置 schedule
- **THEN** 系统不触发任何天气推送

### Requirement: 推送类型区分

系统 SHALL 支持不同类型的推送内容配置。

#### Scenario: 晨间推送包含预报
- **WHEN** 配置 type 为 morning 且 include_forecast 为 true
- **THEN** 推送内容包含当前天气和今日预报

#### Scenario: 晚间推送不含预报
- **WHEN** 配置 type 为 evening 且 include_forecast 为 false
- **THEN** 推送内容仅包含当前天气

#### Scenario: 明日预报推送
- **WHEN** 配置 type 为 tomorrow 且 forecast_days 为 1
- **THEN** 推送内容包含明日天气预报

### Requirement: 执行去重

系统 SHALL 确保同一时间点的推送每天只执行一次。

#### Scenario: 首次执行
- **WHEN** 到达配置的推送时间点且当天未执行过
- **THEN** 系统执行天气推送并记录执行状态

#### Scenario: 重复执行防护
- **WHEN** 到达配置的推送时间点但当天已执行过
- **THEN** 系统跳过本次推送

#### Scenario: 跨日重置
- **WHEN** 日期变更（如 00:00）
- **THEN** 系统清除前一天的执行记录，允许新的推送

### Requirement: 调度状态存储

系统 SHALL 持久化天气推送的执行状态。

#### Scenario: 记录执行状态
- **WHEN** 天气推送成功执行
- **THEN** 系统在 storage 中记录日期、时间点、执行状态

#### Scenario: 读取执行状态
- **WHEN** 系统启动或到达推送时间
- **THEN** 系统从 storage 读取当天已执行的时间点

### Requirement: 部分地点推送

系统 SHALL 支持为不同时间点配置不同的推送地点。

#### Scenario: 指定地点子集
- **WHEN** 某个 schedule 项配置了 locations: ["北京"]
- **THEN** 该时间点仅推送北京的天气

#### Scenario: 使用全部地点
- **WHEN** 某个 schedule 项未配置 locations 或为空
- **THEN** 该时间点推送所有配置的地点天气
