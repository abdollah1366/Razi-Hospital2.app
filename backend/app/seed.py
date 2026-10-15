"""داده‌های پایه: نقش‌ها، قالب فرم گزارش خطا و (اختیاری) مدیر اولیه و داده نمایشی.

اجرا:
    python -m app.seed            # نقش‌ها و فرم؛ مدیر اولیه از RAZI_BOOTSTRAP_ADMIN_CODE/PASSWORD
    python -m app.seed --demo     # به‌علاوه واحدها و کاربران نمایشی (توسعه، یا staging با RAZI_DEMO_PASSWORD)
"""

import json
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.permissions import DEFAULT_ROLES
from app.core.security import hash_password
from app.models import Announcement, Faq, FormTemplate, Role, Unit, User, UserRole

INCIDENT_FORM = Path(__file__).parent / "data" / "incident_form.json"
DEMO_PASSWORD = "Razi1234"


def seed_roles(db: Session) -> None:
    existing = {r.code: r for r in db.scalars(select(Role))}
    for code, (name, perms) in DEFAULT_ROLES.items():
        role = existing.get(code)
        if role is None:
            db.add(Role(code=code, name=name, permissions=perms))
        else:
            role.name, role.permissions = name, perms


def seed_forms(db: Session) -> None:
    if db.scalar(select(FormTemplate).where(FormTemplate.code == "incident")) is None:
        schema = json.loads(INCIDENT_FORM.read_text(encoding="utf-8"))
        db.add(FormTemplate(code="incident", version=schema.get("version", 1), schema=schema, is_active=True))


def _user(
    db: Session, code: str, name: str, unit: Unit | None, roles: list[tuple[str, Unit | None]], password: str
):
    if db.scalar(select(User).where(User.personnel_code == code)) is not None:
        return
    by_code = {r.code: r for r in db.scalars(select(Role))}
    user = User(
        personnel_code=code,
        full_name=name,
        unit_id=unit.id if unit else None,
        password_hash=hash_password(password),
        must_change_password=False,
    )
    user.roles = [UserRole(role=by_code[r], unit_id=u.id if u else None) for r, u in roles]
    db.add(user)


def seed_bootstrap_admin(db: Session) -> None:
    s = get_settings()
    if not (s.bootstrap_admin_code and s.bootstrap_admin_password):
        return
    if db.scalar(select(User).where(User.personnel_code == s.bootstrap_admin_code)) is not None:
        return
    admin_role = db.scalar(select(Role).where(Role.code == "sysadmin"))
    user = User(
        personnel_code=s.bootstrap_admin_code,
        full_name="مدیر سیستم",
        password_hash=hash_password(s.bootstrap_admin_password),
        must_change_password=True,
    )
    user.roles = [UserRole(role=admin_role)]
    db.add(user)


def seed_demo(db: Session) -> None:
    s = get_settings()
    if s.env == "production":
        raise RuntimeError("داده نمایشی در محیط عملیاتی مجاز نیست")
    password = DEMO_PASSWORD
    if s.env == "staging":
        # سرور آزمایشی روی اینترنت نباید رمز عمومیِ README را داشته باشد.
        if not s.demo_password or len(s.demo_password) < 10 or s.demo_password == DEMO_PASSWORD:
            raise RuntimeError("در staging باید RAZI_DEMO_PASSWORD (حداقل ۱۰ نویسه) تنظیم شود")
        password = s.demo_password
    if db.scalar(select(Unit)) is not None:
        return
    units = {
        "emergency": Unit(
            name="اورژانس",
            type="ward",
            is_public=True,
            location="طبقه همکف، ورودی اصلی",
            phone="داخلی ۱۱۰",
            hours="شبانه‌روزی",
        ),
        "icu": Unit(name="ICU", type="ward", is_public=False, location="طبقه دوم"),
        "internal": Unit(name="بخش داخلی", type="ward", is_public=True, location="طبقه سوم"),
        "clinic": Unit(
            name="درمانگاه تخصصی",
            type="clinic",
            is_public=True,
            location="ساختمان درمانگاه",
            hours="شنبه تا چهارشنبه، ۸ تا ۱۴",
        ),
        "it": Unit(name="فناوری اطلاعات", type="support"),
        "quality": Unit(name="دفتر بهبود کیفیت و ایمنی بیمار", type="admin"),
    }
    db.add_all(units.values())
    db.flush()
    _user(db, "1001", "کارمند نمونه (پرستار اورژانس)", units["emergency"], [("staff", None)], password)
    _user(
        db,
        "1002",
        "سرپرستار اورژانس",
        units["emergency"],
        [("unit_manager", units["emergency"])],
        password,
    )
    _user(db, "1003", "کارشناس ایمنی بیمار", units["quality"], [("patient_safety", None)], password)
    _user(
        db,
        "1004",
        "مدیر محتوا",
        units["quality"],
        [("content_manager", None), ("staff", None)],
        password,
    )
    _user(db, "1005", "مدیر سیستم", units["it"], [("sysadmin", None), ("auditor", None)], password)
    db.add_all(
        [
            Faq(
                question="ساعت ملاقات بیماران چه زمانی است؟",
                answer="این متن نمونه است؛ ساعات واقعی را واحد روابط عمومی وارد می‌کند.",
                sort_order=1,
            ),
            Faq(
                question="برای پذیرش چه مدارکی لازم است؟",
                answer="این متن نمونه است؛ فهرست واقعی مدارک را واحد پذیرش وارد می‌کند.",
                sort_order=2,
            ),
            Announcement(
                title="به نسخه آزمایشی اپ بیمارستان رازی خوش آمدید",
                body="این یک اطلاعیه نمونه است.",
                category="news",
                audience="public",
            ),
            Announcement(
                title="بخشنامه نمونه: شناسایی صحیح بیمار",
                body="متن نمونه بخشنامه برای آزمایش تأیید مطالعه.",
                category="circular",
                audience="staff",
                is_important=True,
                requires_ack=True,
            ),
        ]
    )


def run(demo: bool = False) -> None:
    with SessionLocal() as db:
        seed_roles(db)
        seed_forms(db)
        db.flush()
        seed_bootstrap_admin(db)
        if demo:
            seed_demo(db)
        db.commit()


if __name__ == "__main__":
    run(demo="--demo" in sys.argv)
    print("seed done")
