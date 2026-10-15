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
    "training.read": "شرکت در دوره‌ها و آزمون‌های آموزشی",
    "training.manage": "مدیریت دوره، محتوا و آزمون و دیدن نتایج و آمار آموزش",
    "request.create": "ثبت درخواست پشتیبانی (فناوری اطلاعات، تجهیزات، تأسیسات)",
    "request.handle": "رسیدگی به درخواست‌های پشتیبانی واحد",
    "request.read": "مشاهده درخواست‌های پشتیبانی کارکنان واحد و آمار آن",
    "request.type.manage": "تعریف انواع درخواست و واحد مسئول",
}

DEFAULT_ROLES: dict[str, tuple[str, list[str]]] = {
    "staff": ("کارمند", ["incident.create", "announcement.read", "training.read", "request.create"]),
    "unit_manager": (
        "مسئول واحد",
        [
            "incident.create",
            "incident.read",
            "announcement.read",
            "training.read",
            "request.create",
            "request.read",
        ],
    ),
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
            "training.read",
            "request.create",
        ],
    ),
    "content_manager": (
        "مدیر محتوا",
        [
            "announcement.read",
            "announcement.manage",
            "faq.manage",
            "feedback.manage",
            "training.read",
            "request.create",
        ],
    ),
    "training_manager": (
        "مسئول آموزش",
        ["announcement.read", "training.read", "training.manage", "request.create"],
    ),
    # با واحد انتساب داده شود (مثلاً فناوری اطلاعات) تا فقط صف همان واحد را ببیند.
    "support_agent": (
        "کارشناس پشتیبانی",
        ["announcement.read", "training.read", "request.create", "request.handle"],
    ),
    "executive": (
        "مدیر ارشد",
        ["announcement.read", "dashboard.read", "training.read", "request.create", "request.read"],
    ),
    "auditor": ("حسابرس", ["audit.read"]),
    # مدیر سیستم عمداً به محتوای گزارش‌های خطا دسترسی ندارد.
    "sysadmin": (
        "مدیر سیستم",
        ["user.manage", "unit.manage", "form.manage", "announcement.read", "request.type.manage"],
    ),
}
