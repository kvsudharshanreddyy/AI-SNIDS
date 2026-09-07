"""
database/models.py

SQLAlchemy ORM models for AI-SNIDS.

Why SQLite?
-----------
SQLite is a zero-configuration, serverless, embedded database engine.
It is ideal for a single-node academic prototype: no server process,
no credentials to manage, and the database is a single portable file.
In production IDS systems, PostgreSQL or TimescaleDB would be used instead.

Why SQLAlchemy?
--------------
SQLAlchemy provides a Pythonic ORM layer over raw SQL, making it easy to
add, query, and filter security events without writing raw SQL strings.
It also supports multiple database backends via connection string — if the
project were to scale to PostgreSQL, only the DATABASE_URL would change.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class SecurityEvent(Base):
    """
    Represents a single network security event detected by the AI model.

    Each row corresponds to one analyzed traffic sample (from dataset
    or live capture). The model's prediction, confidence, risk level,
    and recommended action are stored alongside network metadata.
    """
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Timestamps — always stored as UTC
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Network identifiers
    source_ip = Column(String(45), nullable=False, default="unknown")
    destination_ip = Column(String(45), nullable=False, default="unknown")
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(10), nullable=True)

    # AI model outputs
    attack_type = Column(String(50), nullable=False)    # e.g., "DDoS", "BENIGN"
    confidence = Column(Float, nullable=False)           # Model probability [0.0–1.0]

    # Risk engine outputs
    risk_level = Column(String(10), nullable=False)     # LOW / MEDIUM / HIGH
    risk_score = Column(Float, nullable=False)           # Composite score [0.0–1.0]

    # Response
    action = Column(String(20), nullable=False)         # ALLOW / LOG / ALERT / BLOCK
    is_blocked = Column(Boolean, default=False)         # Application-level block flag

    # Additional context
    notes = Column(Text, nullable=True)                 # Human-readable explanation
    
    # Simulation distinction
    data_source = Column(String(20), nullable=False, default="CICIDS2017")
    simulation_scenario = Column(String(50), nullable=True)

    def to_dict(self) -> dict:
        """Serialize to plain dict for API responses and dashboard display."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "source_port": self.source_port,
            "destination_port": self.destination_port,
            "protocol": self.protocol,
            "attack_type": self.attack_type,
            "confidence": round(self.confidence, 4),
            "risk_level": self.risk_level,
            "risk_score": round(self.risk_score, 4),
            "action": self.action,
            "is_blocked": self.is_blocked,
            "notes": self.notes,
            "data_source": self.data_source,
            "simulation_scenario": self.simulation_scenario,
        }

    def __repr__(self) -> str:
        return (
            f"<SecurityEvent id={self.id} "
            f"type={self.attack_type} "
            f"risk={self.risk_level} "
            f"ts={self.timestamp}>"
        )


class BlockedIP(Base):
    """
    Application-level IP blocklist.

    IMPORTANT SECURITY NOTE:
    ------------------------
    This is a prototype simulation. The IPs listed here are NOT blocked at
    the OS firewall level (iptables/nftables). Blocking is enforced only
    within the application's own routing logic.

    In a production IDS, this would integrate with:
    - Linux iptables / nftables
    - pfSense / OPNsense
    - A SIEM like Splunk or Elastic SIEM

    For this academic prototype, application-level blocking is intentional
    to avoid accidentally disrupting the student's development network.
    """
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    blocked_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    event_count = Column(Integer, default=1, nullable=False)  # How many events triggered this

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "reason": self.reason,
            "blocked_at": self.blocked_at.isoformat() if self.blocked_at else None,
            "is_active": self.is_active,
            "event_count": self.event_count,
        }
