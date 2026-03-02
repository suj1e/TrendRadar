## ADDED Requirements

### Requirement: 合并消息渲染

系统 SHALL 将多个地点的天气数据合并为一条消息进行推送。

#### Scenario: 多地点合并渲染
- **WHEN** 获取到北京、上海两个地点的天气数据
- **THEN** 渲染为包含两个地点信息的单条消息

#### Scenario: 单地点渲染
- **WHEN** 仅获取到一个地点的天气数据
- **THEN** 渲染为单地点天气消息（格式与多地点一致）

### Requirement: 多渠道格式适配

系统 SHALL 为不同通知渠道渲染适配的消息格式。

#### Scenario: 飞书消息格式
- **WHEN** 推送到飞书渠道
- **THEN** 使用飞书支持的文本格式（emoji + 纯文本）

#### Scenario: 钉钉消息格式
- **WHEN** 推送到钉钉渠道
- **THEN** 使用 Markdown 格式

#### Scenario: 企业微信消息格式
- **WHEN** 推送到企业微信渠道
- **THEN** 使用 Markdown 或 Text 格式（根据配置）

#### Scenario: 邮件消息格式
- **WHEN** 推送到邮件渠道
- **THEN** 使用 HTML 格式

### Requirement: 天气图标映射

系统 SHALL 将天气状况映射为对应的 emoji 图标。

#### Scenario: 晴天图标
- **WHEN** 天气状况为晴（Clear/Sunny）
- **THEN** 使用 ☀️ 图标

#### Scenario: 多云图标
- **WHEN** 天气状况为多云（Cloudy/Overcast）
- **THEN** 使用 ☁️ 图标

#### Scenario: 雨天图标
- **WHEN** 天气状况为雨（Rain/Drizzle/Shower）
- **THEN** 使用 🌧️ 图标

#### Scenario: 雪天图标
- **WHEN** 天气状况为雪（Snow/Sleet）
- **THEN** 使用 ❄️ 图标

### Requirement: 预报内容格式

系统 SHALL 在推送中包含格式化的预报信息（如果配置启用）。

#### Scenario: 包含今日预报
- **WHEN** include_forecast 为 true
- **THEN** 消息中显示今日最高/最低温度和天气趋势

#### Scenario: 不包含预报
- **WHEN** include_forecast 为 false
- **THEN** 消息中仅显示当前天气，不显示预报

### Requirement: 复用现有通知渠道

系统 SHALL 复用 TrendRadar 现有的通知发送器和渠道配置。

#### Scenario: 使用全局通知渠道
- **WHEN** weather.push.channels 未配置
- **THEN** 使用全局 notification.channels 配置推送

#### Scenario: 使用独立通知渠道
- **WHEN** weather.push.channels 配置了特定渠道
- **THEN** 仅使用配置的渠道推送天气

### Requirement: 推送失败处理

系统 SHALL 优雅处理天气推送失败的情况。

#### Scenario: 部分渠道失败
- **WHEN** 推送到多个渠道时某个渠道失败
- **THEN** 记录失败日志，继续推送到其他渠道

#### Scenario: 所有渠道失败
- **WHEN** 所有配置的渠道都推送失败
- **THEN** 记录错误日志，不抛出异常，不影响新闻推送等主流程

### Requirement: 推送标题

系统 SHALL 为天气推送设置明确的标题。

#### Scenario: 晨间推送标题
- **WHEN** 推送类型为 morning
- **THEN** 消息标题为 "🌤️ 晨间天气"

#### Scenario: 晚间推送标题
- **WHEN** 推送类型为 evening
- **THEN** 消息标题为 "🌙 晚间天气"

#### Scenario: 明日预报标题
- **WHEN** 推送类型为 tomorrow
- **THEN** 消息标题为 "📅 明日天气"
