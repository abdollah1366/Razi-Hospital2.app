"""تعریف مجوزها و نقش‌های پیش‌فرض.

دامنه مجوز از نحوه انتساب نقش می‌آید: اگر نقشی همراه با یک واحد به کاربر داده شود،
مجوزهای آن فقط برای داده‌های همان واحد معتبر است؛ بدون واحد، برای همه واحدها.
"""

PERMISSIONS: dict[str, str] = {
    "incident.create": "ثبت گزارش خطا",
    "incident.read": "مشاهده گزارش‌های خطا",
    "incident.manage": "ارجاع، تغییر وضعیت و ثبت اقدام اصلاحی",
    "incident.reporter.view": "مشاهده هویت گزارش‌دهنده (گزارش‌های غیرناشناس)",
    "incident.sensitive.view": "مشاهده اطلاعات هویتی بیمار در گزارش",
    "announcement.read": "مشاهده اطلاعیه‌های داخلی",
    "announcement.manage": "انتشار و مدیریت اطلاعیه‌ها",
    "faq.manage": "مدیریت پرسش‌های متداول",
    "feedback.manage": "رسیدگی به پیشنهادها و شکایات",
    "dashboard.read": "مشاهده داشبورد آماری",
    "audit.read": "مشاهده لاگ حسابرسی",
    "user.manage": "مدیریت کاربران و نقش‌ها",
    "unit.manage": "مدیریت واحدها",
    "form.manage": "مدیریت قالب فرم‌ها",
}

DEFAULT_ROLES: dict[str, tuple[str, list[str]]] = {
    "staff": ("کارمند", ["incident.create", "announcement.read"]),
    "unit_manager": ("مسئول واحد", ["incident.create", "incident.read", "announcement.read"]),
    "patient_safety": (
        "کارشناس ایمنی بیمار",
        [
            "incident.create",
            "incident.read",
            "incident.manage",
            "incident.reporter.view",
            "incident.sensitive.view",
            "announcement.read",
            "dashboard.read",
        ],
    ),
    "content_manager": (
        "مدیر محتوا",
        ["announcement.read", "announcement.manage", "faq.manage", "feedback.manage"],
    ),
    "executive": ("مدیر ارشد", ["announcement.read", "dashboard.read"]),
    "auditor": ("حسابرس", ["audit.read"]),
    # مدیر سیستم عمداً به محتوای گزارش‌های خطا دسترسی ندارد.
    "sysadmin": ("مدیر سیستم", ["user.manage", "unit.manage", "form.manage", "announcement.read"]),
}
