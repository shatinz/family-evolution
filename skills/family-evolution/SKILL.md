---
name: family-evolution
description: "AI-Powered Family Behavioral & Cognitive Evolution Engine. Conducts an interactive setup drill, builds custom family scaffolding, chore calendars, dementia/elderly agency routines, and manages Telegram bot interactions."
---

# Family Evolution Skill 🌿

An autonomous AI engine designed to bring calm, structure, and psychological scaffolding to households.

## Agent Workflow & Execution Protocol

When a user loads or triggers this skill, the AI Agent MUST follow this 4-phase protocol:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Interactive Diagnostic Drill (Interview the User)        │
├─────────────────────────────────────────────────────────────┤
│ 2. Credentials & Token Setup (Telegram & Gemini API Keys)   │
├─────────────────────────────────────────────────────────────┤
│ 3. Template Synthesis & Database Initialization             │
├─────────────────────────────────────────────────────────────┤
│ 4. Dashboard Launch & Member Telegram Onboarding            │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Interactive Diagnostic Drill (Drilling the User)

The AI Agent must proactively ask targeted, empathetic questions across these dimensions:

1. **Family Roster & Roles**:
   - Who lives in the house? (Names, Persian names, ages, occupations, relationship).
   - Are there specific cognitive or emotional conditions? (e.g., elderly dementia/Alzheimer's, caregiving fatigue, chronic anger, lack of motivation).
2. **Household Chores & Bottlenecks**:
   - What tasks are currently causing friction? (Dishes, floor cleaning, cooking, grocery runs, trash).
   - Who is currently bearing the heaviest burden?
3. **Elderly & Meaningful Agency Scaffolds**:
   - What low-stress, live-feedback tasks can be given to elderly/isolated members? (e.g., bird care, watering plants, sorting photos, simple daily puzzles).
4. **Emotional De-escalation & Communication Rules**:
   - Triggers for anger or tension.
   - Agreement on communication boundaries (e.g., 5-minute cooling pause if voices rise, weekly 20-min family meeting).
5. **Roadmap & Goals**:
   - **Short-Term Goals (1-4 weeks)**: e.g., establish fair chore rotation, daily 4-7-8 breathing practice, medication routine.
   - **Action Steps**: Specific daily/weekly habits.
   - **Long-Term Goals (3-6 months)**: e.g., sustained emotional harmony, elderly cognitive retention, reduced burnout.

---

## Phase 2: Credentials & Token Configuration

Ask the user for:
1. **Telegram Bot Token** (from `@BotFather`).
2. **Gemini API Key** (from `ai.google.dev`) OR confirm usage of local OpenAI-compatible endpoint (`http://localhost:20128/v1`).
3. *(Optional)* Telegram Proxy URL (e.g., `socks5h://127.0.0.1:10808` for Iran).

The agent can save these directly by calling:
```http
POST http://127.0.0.1:5055/api/config/save
Content-Type: application/json

{
  "telegram_bot_token": "<TOKEN>",
  "gemini_api_key": "<GEMINI_KEY>",
  "llm_provider": "gemini_native",
  "telegram_proxy": "socks5h://127.0.0.1:10808",
  "use_proxy": true
}
```

---

## Phase 3: Template Synthesis & Initialization

Once the user provides the family details, the AI Agent formats the complete architecture as a JSON payload and sends it to `POST http://127.0.0.1:5055/api/setup/initialize-template`:

```json
{
  "template": {
    "family_profile": {
      "family_name": "خانواده رضایی",
      "overview": "طرح تحول ساختاری جهت ارتقای بهزیستی، مهار دمانس و تقسیم عادلانه کارهای منزل."
    },
    "short_term_goals": [
      {
        "title": "استقرار تقویم عادلانه شستشوی ظروف و نظافت",
        "description": "کاهش بار کاری مادر و چرخش نوبت میان فرزندان.",
        "target_date": "۲ هفته آینده",
        "steps": ["تعیین نوبت‌های روزانه", "ثبت تیک انجام کار در تلگرام"]
      }
    ],
    "long_term_goals": [
      {
        "title": "حفظ استقلال شناختی پدر و آرامش پایدار خانه",
        "description": "مهار افت حافظه از طریق مسئولیت‌های زنده و پیاده‌روی روزانه.",
        "target_date": "۶ ماه آینده",
        "steps": ["مراقبت روزانه از پرنده", "پیاده‌روی عصرگاهی با برادر", "جلسات هفتگی قدردانی"]
      }
    ],
    "members": [
      {
        "name": "Father",
        "name_fa": "پدر",
        "role": "father",
        "age": 65,
        "conditions": "دمانس خفیف، نیاز به عاملیت و روتین زنده",
        "avatar": "👴",
        "is_leader": 0
      },
      {
        "name": "Mother",
        "name_fa": "مادر",
        "role": "mother",
        "age": 60,
        "conditions": "خشم مزمن، نیاز به تنفس ۴-۷-۸ و کاهش بار",
        "avatar": "👵",
        "is_leader": 0
      },
      {
        "name": "Me",
        "name_fa": "من (راهبر)",
        "role": "user",
        "age": 23,
        "conditions": "دانشجوی روانشناسی و راهبر سیستم",
        "avatar": "🧠",
        "is_leader": 1
      }
    ],
    "chores": [
      {
        "title_fa": "ظرف شستن بعد ناهار و شام",
        "title_en": "Washing dishes",
        "category": "kitchen",
        "frequency": "daily",
        "assigned_to": "من (راهبر)",
        "icon": "🍽️"
      },
      {
        "title_fa": "غذا دادن و رسیدگی به پرنده (بابا)",
        "title_en": "Feeding bird",
        "category": "plants_pets",
        "frequency": "daily",
        "assigned_to": "پدر",
        "icon": "🐦"
      }
    ],
    "habits": [
      {
        "target_member": "مادر",
        "habit": "تمرین تنفس ۴-۷-۸ در هنگام خشم",
        "category": "emotional",
        "frequency": "روزانه",
        "reminder_time": "12:00"
      },
      {
        "target_member": "پدر",
        "habit": "مصرف دقیق دارو و مرور عکس‌های خاطره‌انگیز",
        "category": "cognitive",
        "frequency": "روزانه",
        "reminder_time": "09:00"
      }
    ],
    "communication_rules": [
      "قانون توقف ۵ دقیقه‌ای مکالمه در صورت بالا رفتن صدا",
      "جلسه ۲۰ دقیقه‌ای یکشنبه شب‌ها با محوریت قدردانی متقابل",
      "احترام به حریم خصوصی اتاق اعضا"
    ],
    "emergency_and_free_resources": [
      {
        "title": "سامانه ۱۴۸۰ (صدای مشاور بهزیستی)",
        "phone": "1480",
        "description": "مشاوره رایگان تلفنی فردی و خانوادگی (۸ تا ۲۴)"
      },
      {
        "title": "انجمن آلزایمر و دمانس ایران",
        "phone": "021-44645510",
        "description": "راهنمایی و توانبخشی شناختی رایگان مراقبان"
      }
    ]
  }
}
```

---

## Phase 4: Scheduling & Agent Manager Webhooks

If the user prefers the **Agent Manager** to handle recurring schedules rather than the internal background task, the Agent Manager can trigger these standard webhooks:

- **09:00 Daily**: `POST http://127.0.0.1:5055/api/scheduler/trigger-morning` (Dispatches morning mood check-ins).
- **20:00 Daily**: `POST http://127.0.0.1:5055/api/scheduler/trigger-evening` (Dispatches chore completion check).
- **Saturday 21:00**: `POST http://127.0.0.1:5055/api/scheduler/trigger-weekly-review` (Executes AI psychological report and sends family summary).

---

## Direct Telegram Onboarding Link

For each member created in the database, guide the user to share the personalized link:
`https://t.me/<bot_username>?start=member_<id>`
Clicking this link binds their Telegram account in 1 tap without any typing needed.
