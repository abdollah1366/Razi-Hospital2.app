import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


def pk() -> Mapped[uuid.UUID]:
    return mapped_column(primary_key=True, default=uuid.uuid4)


# ---------------------------------------------------------------- هسته


class Unit(TimestampMixin, Base):
    """بخش، درمانگاه یا واحد اداری/پشتیبانی (ساختار درختی)."""

    __tablename__ = "units"
    id: Mapped[uuid.UUID] = pk()
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(30))  # ward | clinic | support | admin
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    location: Mapped[str | None] = mapped_column(String(300))
    phone: Mapped[str | None] = mapped_column(String(50))
    hours: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = pk()
    personnel_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    mobile: Mapped[str | None] = mapped_column(String(20))
    unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"))
    password_hash: Mapped[str] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    roles: Mapped[list["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[uuid.UUID] = pk()
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    permissions: Mapped[list[str]] = mapped_column(JSONB, default=list)


class UserRole(Base):
    """نقش کاربر؛ اگر unit_id داشته باشد، مجوزهای «.unit» فقط برای همان واحد معتبرند."""

    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", "unit_id"),)
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"))
    unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"))

    user: Mapped[User] = relationship(back_populates="roles")
    role: Mapped[Role] = relationship(lazy="joined")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    family_id: Mapped[uuid.UUID] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    device: Mapped[str | None] = mapped_column(String(200))


class AuditLog(Base):
    """فقط درج؛ هیچ endpointی برای ویرایش یا حذف آن وجود ندارد."""

    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = pk()
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[str | None] = mapped_column(String(64))
    ip: Mapped[str | None] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSONB, default=dict)


class FormTemplate(Base):
    __tablename__ = "form_templates"
    __table_args__ = (UniqueConstraint("code", "version"),)
    id: Mapped[uuid.UUID] = pk()
    code: Mapped[str] = mapped_column(String(50), index=True)
    version: Mapped[int] = mapped_column(Integer)
    schema: Mapped[dict] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ---------------------------------------------------------------- گزارش خطا


class Incident(TimestampMixin, Base):
    __tablename__ = "incidents"
    id: Mapped[uuid.UUID] = pk()
    tracking_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    client_uuid: Mapped[uuid.UUID] = mapped_column(unique=True)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    form_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("form_templates.id"))
    answers: Mapped[dict] = mapped_column(JSONB, default=dict)
    sensitive_answers_encrypted: Mapped[str | None] = mapped_column(Text)
    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id"), index=True)
    occurred_on: Mapped[date] = mapped_column(Date)
    shift: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30), default="submitted", index=True)
    assigned_unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"))
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    # در گزارش ناشناس null می‌ماند؛ هیچ ستون دیگری هم هویت گزارش‌دهنده را نگه نمی‌دارد.
    reporter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    follow_up_secret_hash: Mapped[str | None] = mapped_column(String(64))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    history: Mapped[list["IncidentStatusChange"]] = relationship(
        order_by="IncidentStatusChange.at", cascade="all, delete-orphan"
    )
    actions: Mapped[list["IncidentAction"]] = relationship(
        order_by="IncidentAction.created_at", cascade="all, delete-orphan"
    )


class IncidentStatusChange(Base):
    __tablename__ = "incident_status_history"
    id: Mapped[uuid.UUID] = pk()
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str] = mapped_column(String(30))
    by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class IncidentAction(Base):
    """اقدام اصلاحی."""

    __tablename__ = "incident_actions"
    id: Mapped[uuid.UUID] = pk()
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(Text)
    owner_name: Mapped[str | None] = mapped_column(String(200))
    due_date: Mapped[date | None] = mapped_column(Date)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ---------------------------------------------------------------- اطلاع‌رسانی


class Announcement(TimestampMixin, Base):
    __tablename__ = "announcements"
    id: Mapped[uuid.UUID] = pk()
    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(30))  # news | circular | guideline | notice
    audience: Mapped[str] = mapped_column(String(10), index=True)  # public | staff
    target_role_codes: Mapped[list[str]] = mapped_column(JSONB, default=list)
    target_unit_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_ack: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    author_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))


class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"
    __table_args__ = (UniqueConstraint("announcement_id", "user_id"),)
    id: Mapped[uuid.UUID] = pk()
    announcement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("announcements.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ---------------------------------------------------------------- بخش عمومی


class Faq(Base):
    __tablename__ = "faqs"
    id: Mapped[uuid.UUID] = pk()
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class Feedback(TimestampMixin, Base):
    """پیشنهاد، انتقاد، شکایت یا قدردانی مراجعان."""

    __tablename__ = "feedback"
    id: Mapped[uuid.UUID] = pk()
    tracking_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(20))  # suggestion | criticism | complaint | praise
    name: Mapped[str | None] = mapped_column(String(200))
    mobile: Mapped[str | None] = mapped_column(String(20))
    unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="received")  # received | reviewing | answered
    response: Mapped[str | None] = mapped_column(Text)
