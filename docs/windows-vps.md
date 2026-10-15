# اجرای سرور آزمایشی روی VPS ویندوزی (بدون Docker)

برای VPSهایی که مجازی‌سازی ندارند و Docker Desktop روی آن‌ها نصب نمی‌شود.
**فقط داده ساختگی** وارد کنید؛ ارتباط HTTP است و رمزنگاری نمی‌شود.

## ۱. نصب پیش‌نیازها (یک بار)

- **Python 3.12** از python.org؛ در صفحه اول نصب، تیک «Add python.exe to PATH» را بزنید.
- **PostgreSQL 16** از سایت EDB (نصب‌کننده ویندوز). برای کاربر `postgres` یک رمز بگذارید و یادداشت کنید. Stack Builder لازم نیست.
- کد پروژه: در صفحه GitHub مخزن، Code ← Download ZIP، و آن را در `C:\razi` باز کنید (طوری که `C:\razi\backend` وجود داشته باشد).

## ۲. نصب بک‌اند و ساخت رمزها

در PowerShell عادی:

```powershell
cd C:\razi\backend
python -m venv .venv
.venv\Scripts\python -m pip install .
.venv\Scripts\python scripts\make_staging_env.py
```

دستور آخر فایل `backend\.env` را با رمزهای تصادفی می‌سازد و دو چیز چاپ می‌کند: دو خط SQL برای ساخت پایگاه داده، و رمز ورود کاربران نمایشی. خروجی را نگه دارید.

## ۳. ساخت پایگاه داده

```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

رمز کاربر `postgres` را بدهید، دو خط `CREATE ...` چاپ‌شده در مرحله قبل را paste کنید، سپس `\q`.

## ۴. ساخت جدول‌ها و داده نمایشی

```powershell
.venv\Scripts\alembic upgrade head
.venv\Scripts\python -m app.seed --demo
```

## ۵. اجرای سرور

```powershell
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000
```

تا وقتی این پنجره باز است سرور کار می‌کند.

## ۶. باز کردن پورت 8000

در PowerShell **Administrator**:

```powershell
New-NetFirewallRule -DisplayName "Razi API 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

اگر پنل شرکت VPS فایروال جداگانه دارد، پورت 8000 (TCP) را آنجا هم باز کنید. پورت 5432 پایگاه داده را **باز نکنید**.

## ۷. آزمایش

- در مرورگر گوشی: `http://IP-سرور:8000/health` باید `{"status":"ok"}` نشان دهد.
- در اپ (نسخه debug) در صفحه ورود «تغییر آدرس سرور» ← `http://IP-سرور:8000`، سپس ورود با کد 1001 و رمز نمایشی مرحله ۲.

## به‌روزرسانی کد

ZIP جدید را باز کنید، فایل `backend\.env` قبلی را به پوشه جدید کپی کنید، سپس مرحله‌های ۲ (به جز دستور آخر)، ۴ و ۵ را دوباره اجرا کنید.
