"""
Agora client — connects Claude Code sessions to the shared Redis brain.

Usage:
    from agora.client import AgoraClient
    client = AgoraClient(agent_name="Charon", machine="M1")
    client.connect()
    client.send(stream="main", subject="Hello", body="First message", confidence=1.0)
    messages = client.listen(stream="main", count=10)
"""
import redis
import json
import time
import threading
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from agora.config import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, get_redis_password,
    STREAM_MAIN, STREAM_CHALLENGES, STREAM_TASKS, STREAM_DISCOVERIES,
    AGENT_PREFIX, CONSUMER_GROUP,
    HEARTBEAT_INTERVAL_SEC, HEARTBEAT_TIMEOUT_SEC,
)
from agora.protocol import AgoraMessage, MessageType


STREAM_MAP = {
    "main": STREAM_MAIN,
    "challenges": STREAM_CHALLENGES,
    "tasks": STREAM_TASKS,
    "discoveries": STREAM_DISCOVERIES,
}


class AgoraClient:
    """Client for a single agent to participate in the Agora."""

    def __init__(self, agent_name: str, machine: str, host: str = None, port: int = None):
        self.agent_name = agent_name
        self.machine = machine
        self.host = host or REDIS_HOST
        self.port = port or REDIS_PORT
        self.r: Optional[redis.Redis] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._running = False

    def connect(self):
        """Connect to Redis and register the agent."""
        password = get_redis_password()
        self.r = redis.Redis(
            host=self.host,
            port=self.port,
            db=REDIS_DB,
            password=password,
            decode_responses=True,
        )
        # Test connection
        self.r.ping()

        # Register agent
        self.r.hset(f"{AGENT_PREFIX}{self.agent_name}", mapping={
            "machine": self.machine,
            "status": "online",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        })

        # Ensure consumer groups exist for all streams
        for stream_name in STREAM_MAP.values():
            try:
                self.r.xgroup_create(stream_name, CONSUMER_GROUP, id="0", mkstream=True)
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise

        print(f"[Agora] {self.agent_name}@{self.machine} connected.")

    def disconnect(self):
        """Gracefully disconnect."""
        self._running = False
        if self.r:
            self.r.hset(f"{AGENT_PREFIX}{self.agent_name}", "status", "offline")
            print(f"[Agora] {self.agent_name} disconnected.")

    def send(self, stream: str, subject: str, body: str, confidence: float,
             msg_type: MessageType = MessageType.ANNOUNCE,
             evidence: str = "", reply_to: str = None) -> str:
        """Send a message to a stream. Returns the message ID."""
        stream_key = STREAM_MAP.get(stream, stream)
        msg = AgoraMessage(
            sender=self.agent_name,
            machine=self.machine,
            type=msg_type,
            subject=subject,
            body=body,
            confidence=confidence,
            evidence=evidence,
            reply_to=reply_to,
        )
        msg_id = self.r.xadd(stream_key, msg.to_redis())
        return msg_id

    def listen(self, stream: str = "main", count: int = 10,
               last_id: str = "0-0") -> List[Tuple[str, AgoraMessage]]:
        """Read recent messages from a stream. Returns list of (id, message) tuples."""
        stream_key = STREAM_MAP.get(stream, stream)
        raw = self.r.xrange(stream_key, min=last_id, count=count)
        results = []
        for msg_id, data in raw:
            try:
                msg = AgoraMessage.from_redis(data)
                results.append((msg_id, msg))
            except (KeyError, ValueError) as e:
                print(f"[Agora] Skipping malformed message {msg_id}: {e}")
        return results

    def listen_new(self, stream: str = "main", count: int = 10,
                   block_ms: int = 0) -> List[Tuple[str, AgoraMessage]]:
        """Read new messages via consumer group (each message delivered once).
        Set block_ms > 0 to wait for new messages."""
        stream_key = STREAM_MAP.get(stream, stream)
        raw = self.r.xreadgroup(
            CONSUMER_GROUP, self.agent_name,
            {stream_key: ">"},
            count=count,
            block=block_ms if block_ms > 0 else None,
        )
        results = []
        if raw:
            for _stream, messages in raw:
                for msg_id, data in messages:
                    try:
                        msg = AgoraMessage.from_redis(data)
                        results.append((msg_id, msg))
                        # Acknowledge
                        self.r.xack(stream_key, CONSUMER_GROUP, msg_id)
                    except (KeyError, ValueError) as e:
                        print(f"[Agora] Skipping malformed message {msg_id}: {e}")
        return results

    def challenge(self, subject: str, body: str, evidence: str,
                  confidence: float, reply_to: str = None) -> str:
        """Post a challenge to the challenges stream."""
        return self.send(
            stream="challenges",
            subject=subject,
            body=body,
            confidence=confidence,
            msg_type=MessageType.CHALLENGE,
            evidence=evidence,
            reply_to=reply_to,
        )

    def kill(self, hypothesis: str, evidence: str, confidence: float) -> str:
        """Kill a hypothesis. Moves it from alive to killed, posts to stream."""
        # Record the kill
        self.r.smove("hypotheses:alive", "hypotheses:killed", hypothesis)
        self.r.zincrby("leaderboard:kills", 1, self.agent_name)

        return self.send(
            stream="main",
            subject=f"KILL: {hypothesis}",
            body=f"Hypothesis killed by {self.agent_name}",
            confidence=confidence,
            msg_type=MessageType.KILL,
            evidence=evidence,
        )

    def share_discovery(self, subject: str, body: str, evidence: str,
                        confidence: float) -> str:
        """Share a discovery for group verification."""
        return self.send(
            stream="discoveries",
            subject=subject,
            body=body,
            confidence=confidence,
            msg_type=MessageType.SHARE,
            evidence=evidence,
        )

    def claim_task(self, task_id: str, description: str) -> str:
        """Claim a task from the task pool."""
        return self.send(
            stream="tasks",
            subject=f"CLAIMED: {task_id}",
            body=description,
            confidence=1.0,
            msg_type=MessageType.TASK_CLAIM,
        )

    def get_agents(self) -> dict:
        """Get all registered agents and their status."""
        agents = {}
        for key in self.r.scan_iter(f"{AGENT_PREFIX}*"):
            name = key.replace(AGENT_PREFIX, "")
            agents[name] = self.r.hgetall(key)
        return agents

    def heartbeat(self):
        """Send a single heartbeat."""
        now = datetime.now(timezone.utc).isoformat()
        self.r.hset(f"{AGENT_PREFIX}{self.agent_name}", "last_heartbeat", now)

    def start_heartbeat(self):
        """Start background heartbeat thread."""
        self._running = True
        def _beat():
            while self._running:
                try:
                    self.heartbeat()
                except Exception:
                    pass
                time.sleep(HEARTBEAT_INTERVAL_SEC)
        self._heartbeat_thread = threading.Thread(target=_beat, daemon=True)
        self._heartbeat_thread.start()

    def get_dead_agents(self) -> List[str]:
        """Find agents that haven't heartbeated within the timeout."""
        dead = []
        now = datetime.now(timezone.utc)
        for key in self.r.scan_iter(f"{AGENT_PREFIX}*"):
            data = self.r.hgetall(key)
            if data.get("status") == "offline":
                continue
            last = data.get("last_heartbeat", "")
            if last:
                last_dt = datetime.fromisoformat(last)
                if (now - last_dt).total_seconds() > HEARTBEAT_TIMEOUT_SEC:
                    dead.append(key.replace(AGENT_PREFIX, ""))
        return dead

    def print_stream(self, stream: str = "main", count: int = 20, last_id: str = "0-0"):
        """Pretty-print recent messages from a stream."""
        messages = self.listen(stream, count, last_id)
        if not messages:
            print(f"[Agora] No messages on {stream}")
            return
        for msg_id, msg in messages:
            print(f"\n--- {msg_id} ---")
            print(msg)
        print(f"\n[Agora] {len(messages)} messages on {stream}")
