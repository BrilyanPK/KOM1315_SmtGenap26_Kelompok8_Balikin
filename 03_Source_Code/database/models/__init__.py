import uuid
from nanoid import generate
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Text, Integer, Boolean

def generate_prefixed_id(prefix: str, size: int = 10) -> str:
    return f"{prefix}-{generate(size=size)}"

from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class RoleEnum(str, enum.Enum):
    PENCARI = "Pencari"
    PETUGAS = "Petugas"
    ADMIN = "Admin"


class ReportStatusEnum(str, enum.Enum):
    HILANG = "Hilang"
    DITEMUKAN = "Ditemukan"
    DIPROSES = "Diproses"
    DIKEMBALIKAN = "Dikembalikan"


class User(Base):
    __tablename__ = "users"

    id = Column(String(21), primary_key=True, default=lambda: generate_prefixed_id("USR"))
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.PENCARI)
    mfa_enabled = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reports = relationship("Report", foreign_keys="[Report.user_id]", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")


class Item(Base):
    __tablename__ = "items"

    id = Column(String(21), primary_key=True, default=lambda: generate_prefixed_id("ITM"))
    name = Column(String, index=True)
    category = Column(String, index=True)
    photo_url = Column(String, nullable=True)

    reports = relationship("Report", back_populates="item")
    inventory = relationship("Inventory", back_populates="item", uselist=False)


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(21), primary_key=True, default=lambda: generate_prefixed_id("REP"))
    contact_info = Column(String, nullable=True)
    user_id = Column(String(21), ForeignKey("users.id"))
    item_id = Column(String(21), ForeignKey("items.id"))
    report_time = Column(DateTime, default=datetime.utcnow)
    location = Column(String)
    description = Column(Text)
    finder_id = Column(String(21), ForeignKey("users.id"), nullable=True)
    receiver_id = Column(String(21), ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ReportStatusEnum), default=ReportStatusEnum.HILANG)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="reports")
    finder = relationship("User", foreign_keys=[finder_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    item = relationship("Item", back_populates="reports")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String(21), primary_key=True, default=lambda: generate_prefixed_id("INV"))
    item_id = Column(String(21), ForeignKey("items.id"), unique=True)
    quantity = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    item = relationship("Item", back_populates="inventory")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(String(21), primary_key=True, default=lambda: generate_prefixed_id("LOG"))
    user_id = Column(String(21), ForeignKey("users.id"))
    action = Column(String)
    target_detail = Column(String)
    ip_address = Column(String, nullable=True)
    status = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_logs")
