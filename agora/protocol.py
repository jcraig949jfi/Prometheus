"""
Agora message protocol — schemas, validation, serialization.

Every message on a stream follows a strict schema. No claim without calibration.
"""
import json
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


class MessageType(Enum):
    ANNOUNCE = "announce"       # Status update, what I'm working on
    CHALLENGE = "challenge"     # I challenge hypothesis X because Y
    REQUEST = "request"         # I need help with X
    SHARE = "share"             # Here's what I found
    VOTE = "vote"               # I vote to accept/reject X
    HEARTBEAT = "heartbeat"     # I'm alive
    RESPONSE = "response"       # Direct reply to another message
    TASK_CLAIM = "task_claim"   # I'm taking task X
    TASK_OFFER = "task_offer"   # Task X is available
    KILL = "kill"               # Hypothesis X is dead, here's why


@dataclass
class AgoraMessage:
    sender: str
    machine: str
    type: MessageType
    subject: str
    body: str
    confidence: float  # 0.0 - 1.0, mandatory
    evidence: str = ""
    reply_to: Optional[str] = None  # Stream message ID being replied to
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self):
        """Validate message before sending."""
        if not self.sender:
            raise ValueError("sender is required")
        if not self.machine:
            raise ValueError("machine is required")
        if not isinstance(self.type, MessageType):
            raise ValueError(f"type must be a MessageType, got {type(self.type)}")
        if not self.subject:
            raise ValueError("subject is required")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be 0.0-1.0, got {self.confidence}")
        if self.type == MessageType.CHALLENGE and not self.evidence:
            raise ValueError("challenges require evidence")
        if self.type == MessageType.KILL and not self.evidence:
            raise ValueError("kills require evidence")

    def to_redis(self) -> dict:
        """Serialize to Redis stream entry (flat string dict)."""
        self.validate()
        return {
            "sender": self.sender,
            "machine": self.machine,
            "type": self.type.value,
            "subject": self.subject,
            "body": self.body,
            "confidence": str(self.confidence),
            "evidence": self.evidence,
            "reply_to": self.reply_to or "",
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_redis(cls, data: dict) -> "AgoraMessage":
        """Deserialize from Redis stream entry."""
        return cls(
            sender=data["sender"],
            machine=data["machine"],
            type=MessageType(data["type"]),
            subject=data["subject"],
            body=data["body"],
            confidence=float(data["confidence"]),
            evidence=data.get("evidence", ""),
            reply_to=data.get("reply_to") or None,
            timestamp=data["timestamp"],
        )

    def __str__(self):
        prefix = f"[{self.sender}@{self.machine}]"
        conf = f"(conf={self.confidence:.1f})"
        return f"{prefix} {self.type.value}: {self.subject} {conf}\n  {self.body}"
