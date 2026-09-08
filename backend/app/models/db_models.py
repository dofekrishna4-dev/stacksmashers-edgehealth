"""SQLAlchemy ORM models mirroring database/schema.sql."""
import uuid
from sqlalchemy import (Column, String, Numeric, Boolean, TIMESTAMP, ForeignKey,
                         CheckConstraint, Text, Date, Integer, func)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(120), nullable=False)
    role = Column(String(20), nullable=False)
    email = Column(String(160), unique=True, nullable=False)
    phone = Column(String(30))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('patient','caregiver','clinician','admin')"),
    )


class Device(Base):
    __tablename__ = "devices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_type = Column(String(20), nullable=False)
    device_serial = Column(String(80), unique=True, nullable=False)
    firmware_version = Column(String(20))
    last_seen_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recorded_at = Column(TIMESTAMP(timezone=True), nullable=False)
    heart_rate_avg = Column(Numeric(5, 2))
    spo2_avg = Column(Numeric(5, 2))
    resp_rate_avg = Column(Numeric(5, 2))
    tremor_score = Column(Numeric(5, 2))
    activity_level = Column(Numeric(5, 2))
    sleep_stage = Column(String(20))
    data_quality = Column(Numeric(3, 2))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class DigitalTwinRecord(Base):
    __tablename__ = "digital_twin"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    baseline_hr = Column(Numeric(5, 2))
    baseline_spo2 = Column(Numeric(5, 2))
    baseline_resp = Column(Numeric(5, 2))
    baseline_tremor = Column(Numeric(5, 2))
    twin_state = Column(JSONB, nullable=False)
    last_updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    twin_version = Column(Integer, default=1)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    predicted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    condition = Column(String(60), nullable=False)
    risk_score = Column(Numeric(5, 2), nullable=False)
    horizon_hours = Column(Numeric(4, 1), nullable=False)
    contributing_agents = Column(JSONB)
    explanation = Column(Text)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"))
    tier = Column(String(10), nullable=False)
    channel = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    acknowledged_at = Column(TIMESTAMP(timezone=True))
    escalated = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    summary = Column(Text)
    file_url = Column(Text)
