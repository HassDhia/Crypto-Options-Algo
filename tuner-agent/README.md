# RL Parameter Tuner Agent

This service periodically adjusts trading filter parameters using OpenAI's API based on recent trading performance.

## Configuration

Set these environment variables:
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `TUNING_INTERVAL_HOURS`: Tuning frequency (default: 1 hour)

## Running the Service

```bash
docker build -t tuner-agent .
docker run -e OPENAI_API_KEY=your_api_key tuner-agent
```

## How It Works

1. Collects recent trading statistics
2. Sends performance data to OpenAI API
3. Parses suggested parameter updates
4. Updates Redis with new parameters
5. Runs hourly by default
