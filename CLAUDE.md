# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Run main program
python -m trendradar

# Run MCP Server
python -m mcp_server.server

# Docker (recommended for production)
cd docker
docker-compose up -d                    # Start services
docker-compose up -d --build            # Rebuild and restart
```

## Architecture Overview

```
trendradar/
├── __main__.py      # Main entry, NewsAnalyzer class
├── context.py       # AppContext - dependency container, eliminates global state
├── core/
│   ├── loader.py    # Config loading (YAML + env vars)
│   ├── scheduler.py # Timeline-based scheduling (collect/analyze/push)
│   └── analyzer.py  # Keyword matching, platform stats
├── crawler/
│   ├── fetcher.py   # Hot list API fetcher
│   └── rss/         # RSS feed fetcher & parser
├── storage/         # SQLite + TXT/HTML + S3 (abstracted backend)
├── notification/
│   ├── dispatcher.py  # Multi-channel, multi-account dispatcher
│   ├── senders.py     # Channel-specific senders
│   └── renderer.py    # Content formatting per channel
├── ai/              # LiteLLM-based analysis & translation
├── weather/         # Weather notification module
└── report/          # HTML/Markdown report generation

mcp_server/          # FastMCP 2.0 server for AI assistants
├── server.py        # Entry point
└── tools/           # MCP tools (search, analyze, notify, etc.)
```

## Data Flow

```
Hot List APIs (NewsNow) ──┬──> SQLite Storage ──> Report Generator ──> Notification
RSS Feeds ────────────────┘                         │
                                                    ▼
                                              AI Analysis (optional)
```

## Configuration

- `config/config.yaml` - Main config (platforms, RSS, AI, notifications, weather)
- `config/timeline.yaml` - Schedule presets (when to collect/analyze/push)
- `config/frequency_words.txt` - Keyword filters and groups
- Environment variables override YAML (see `docker/.env` for examples)

## Key Patterns

1. **AppContext**: All config-dependent operations go through `AppContext` methods (e.g., `ctx.create_scheduler()`, `ctx.get_storage_manager()`). Never access config directly in business logic.

2. **Storage Backend**: Abstract `StorageBackend` with `LocalStorageBackend` and `RemoteStorageBackend` implementations. Use `ctx.get_storage_manager()`.

3. **Notification Dispatcher**: `NotificationDispatcher.dispatch_all()` handles all channels. Each channel supports multi-account via `;` separator.

4. **Scheduler**: Timeline-based scheduling with periods, day_plans, week_map. Supports once-per-period execution with deduplication.

## Environment Variables

Key variables (set in `docker/.env` or GitHub Secrets):

- Notifications: `FEISHU_WEBHOOK_URL`, `DINGTALK_WEBHOOK_URL`, `TELEGRAM_BOT_TOKEN`, etc.
- AI: `AI_API_KEY`, `AI_MODEL` (LiteLLM format: `provider/model`)
- Storage: `S3_ENDPOINT_URL`, `S3_BUCKET_NAME`, etc.
- Schedule: `CRON_SCHEDULE` (default: `*/30 * * * *`)
