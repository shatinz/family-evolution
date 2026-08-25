# 🌿 Family Evolution Hub (خانواده‌یار)

> **سامانه هوشمند تکامل، آرامش و هدایت رفتاری خانواده با رابط کاربری شیشه‌ای (Apple Liquid Glass) و ربات تلگرام خودکار.**
> 
> *An open, scalable AI-powered family behavioral & cognitive evolution engine designed to bring calm, structure, and psychological scaffolding to households.*

---

## ✨ ویژگی‌های کلیدی (Key Features)

1. **داربست‌های شناختی سالمندان (Elderly Dementia & Cognitive Scaffolds)**:
   - واگذاری وظایف زنده با بازخورد مثبت (آبیاری گلدان‌ها، رسیدگی به پرندگان/حیوانات خانگی، آلبوم خاطرات) جهت تقویت عاملیت و مهار افت شناختی.
   - فرم اختصاصی ثبت سریع وضعیت برای مراقبان و همراهان.

2. **مدیریت خشم مزمن و فرسودگی مراقبت (Caregiver Burnout & Anger De-escalation)**:
   - داربست‌های تنظیم هیجان (تنفس ۴-۷-۸، پیام‌های قدردانی روزانه).
   - قانون توقف ۵ دقیقه‌ای مکالمه در زمان تنش و اختصاص زمان خنک‌سازی.

3. **تقویم و ماتریس عادلانه وظایف منزل (Smart Chore Rotation Matrix)**:
   - تقسیم متعادل کارهای روزمره خانه (شستشوی ظروف، نظافت، خرید، آشپزی) با ثبت وضعیت انجام در تلگرام یا وب.

4. **اتصال آسان و مستقل تلگرام (Autonomous Telegram Bot Integration)**:
   - احوالپرسی‌های صبحگاهی (ارزیابی ۱ تا ۵ خلق‌وخو با دکمه‌های شیشه‌ای بدون نیاز به تایپ).
   - بررسی وظایف عصرگاهی و پیام‌های همگانی راهبر خانواده.
   - **لینک مستقیم و فوری (Deep Linking)**: اتصال هر عضو به ربات با ۱ کلیک (`/start member_<id>`).

5. **طرح و اهداف خانواده (Family Blueprint & Roadmap)**:
   - هدف‌گذاری کوتاه‌مدت (۱ تا ۴ هفته) با گام‌های اقدام مشخص.
   - هدف‌گذاری بلندمدت (۳ تا ۶ ماه) برای حفظ هارمونی و کاهش فرسودگی عاطفی.

6. **داشبورد لوکس شیشه‌ای (Apple-Grade Liquid Glass UI)**:
   - رابط کاربری مدرن با تم Glassmorphism، چارت‌های آماری واقعی، سازگاری کامل موبایل و چیدمان استاندارد RTL.

---

## 🚀 راهنمای نصب و راه‌اندازی سریع (Quick Start)

### ۱. نصب وابستگی‌ها
```bash
git clone https://github.com/<your-username>/family-evolution.git
cd family-evolution
pip install -r requirements.txt
```

### ۲. پیکربندی (Configuration)
تنظیمات را می‌توانید مستقیماً در **پنل تنظیمات وب (Settings Tab)**، از طریق **متغیرهای محیطی**، یا با کپی فایل نمونه انجام دهید:
```bash
cp data/config.example.json data/config.json
```

پارامترهای کلیدی:
- `TELEGRAM_BOT_TOKEN`: توکن ربات تلگرام دریافتی از `@BotFather`
- `GEMINI_API_KEY`: کلید Google Gemini API (اختیاری در صورت استفاده از جمینای)
- `LLM_PROVIDER`: `gemini_native` یا `openai_compatible`
- `TELEGRAM_PROXY`: آدرس پروکسی در صورت فیلتر بودن (مثلاً `socks5h://127.0.0.1:10808`)

### ۳. اجرای برنامه
```bash
python main.py
```
سپس داشبورد را در مرورگر باز کنید:
👉 **`http://127.0.0.1:5055`**

---

## 🤖 استفاده به عنوان مهارت هوش مصنوعی (Agent Skill)

این مخزن شامل یک مهارت استاندارد تحت عنوان `skills/family-evolution/SKILL.md` است.
هنگامی که این مهارت در سیستم‌هایی مانند **Antigravity** یا **Agent Managers** فعال شود:
1. عامل هوشمند یک مصاحبه تشخیصی چندمرحله‌ای (AI Drill) با شما انجام می‌دهد.
2. اعضا، وظایف، عادات و اهداف کوتاه‌مدت/بلندمدت را سازماندهی کرده و مستقیماً به دیتابیس تزریق می‌کند.
3. وب‌هوک‌های زمان‌بندی روزانه (`/api/scheduler/trigger-morning` و `/api/scheduler/trigger-evening`) توسط عامل اجرا می‌گردند.

---

## 🧪 تست و اعتبارسنجی
```bash
python -m unittest tests/test_system.py
```
