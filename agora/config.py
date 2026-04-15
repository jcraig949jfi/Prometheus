"""
Agora configuration — Redis connection and agent identity.

Redis connection details are loaded from environment or keys.py.
"""
import os
import json
from pathlib import Path

# Redis connection
REDIS_HOST = os.environ.get("AGORA_REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("AGORA_REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("AGORA_REDIS_DB", 0))

# Auth — loaded from keys.py or environment
def get_redis_password():
    """Get Redis password from keys.py or environment."""
    password = os.environ.get("AGORA_REDIS_PASSWORD")
    if password:
        return password
    try:
        from keys import get_key
        return get_key("redis")
    except (ImportError, Exception):
        return None

# Stream names
STREAM_MAIN = "agora:main"
STREAM_CHALLENGES = "agora:challenges"
STREAM_TASKS = "agora:tasks"
STREAM_DISCOVERIES = "agora:discoveries"

# Agent state prefix
AGENT_PREFIX = "agent:"

# Hypothesis tracking
HYPOTHESES_ALIVE = "hypotheses:alive"
HYPOTHESES_KILLED = "hypotheses:killed"

# Leaderboards
LEADERBOARD_KILLS = "leaderboard:kills"
LEADERBOARD_DISCOVERIES = "leaderboard:discoveries"

# Heartbeat config
HEARTBEAT_INTERVAL_SEC = 60
HEARTBEAT_TIMEOUT_SEC = 300  # 5 minutes = presumed dead

# Consumer group name (each agent joins this group)
CONSUMER_GROUP = "agora-agents"
