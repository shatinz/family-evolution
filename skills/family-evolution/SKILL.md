---
name: family-evolution
description: "AI-Powered Family Behavioral & Cognitive Evolution Engine. Conducts an interactive setup drill, builds custom family scaffolding, chore calendars, dementia/elderly agency routines, informed consent, longitudinal evaluations, and manages Telegram bot interactions."
---

# Family Evolution Skill 🌿

An autonomous AI engine designed to bring calm, structure, psychological safety, and behavioral scaffolding to households.

## Agent Workflow & Execution Protocol

When a user loads or triggers this skill, the AI Agent MUST follow this 5-phase protocol:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Interactive Diagnostic Drill (Interview the User)        │
├─────────────────────────────────────────────────────────────┤
│ 2. Credentials & Token Setup (Telegram & Gemini API Keys)   │
├─────────────────────────────────────────────────────────────┤
│ 3. Template Synthesis & Database Initialization             │
├─────────────────────────────────────────────────────────────┤
│ 4. Member Onboarding, Informed Consent & Baseline Drill     │
├─────────────────────────────────────────────────────────────┤
│ 5. Monthly Longitudinal Re-assessments & Adaptive Tuning    │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Interactive Diagnostic Drill (Drilling the User)

The AI Agent must proactively ask targeted, empathetic questions across these dimensions:

1. **Family Roster, Medical & Cognitive Context**:
   - Who lives in the house? (Names, Persian names, ages, occupations, relationship).
   - Medical history, medications, or cognitive conditions (e.g., elderly dementia/Alzheimer's, chronic illness, sleep issues, caregiving fatigue, chronic anger).
2. **Household Chores & Friction Points**:
   - What tasks are currently causing friction? (Dishes, floor cleaning, cooking, grocery runs, trash, elderly care).
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
      "family_name": "خانواده نمونه",
      "overview": "طرح تحول ساختاری جهت ارتقای بهزیستی، مهار دمانس و تقسیم عادلانه کارهای منزل."
    },
    "short_term_goals": [
      {
        "title": "استقرار تقویم عادلانه شستشوی ظروف و نظافت",
        "description": "کاهش بار کاری و چرخش نوبت میان فرزندان.",
        "target_date": "۲ هفته آینده",
        "steps": ["تعیین نوبت‌های روزانه", "ثبت تیک انجام کار در تلگرام"]
      }
    ],
    "long_term_goals": [
      {
        "title": "حفظ استقلال شناختی و آرامش پایدار خانه",
        "description": "مهار افت حافظه از طریق مسئولیت‌های زنده و پیاده‌روی روزانه.",
        "target_date": "۶ ماه آینده",
        "steps": ["مراقبت روزانه از پرنده", "پیاده‌روی عصرگاهی", "جلسات هفتگی قدردانی"]
      }
    ],
    "members": [
      {
        "name": "Father",
        "name_fa": "پدر",
        "role": "father",
        "age": 65,
        "conditions": "دمانس خفیف، نیاز به عاملیت و روتین زنده",
        "medical_history": "سابقه فشار خون و افت حافظه کوتاه‌مدت",
        "avatar": "👴",
        "is_leader": 0
      },
      {
        "name": "Mother",
        "name_fa": "مادر",
        "role": "mother",
        "age": 60,
        "conditions": "خشم مزمن، نیاز به تنفس ۴-۷-۸ و کاهش بار",
        "medical_history": "خستگی مراقبت و استرس مزمن",
        "avatar": "👵",
        "is_leader": 0
      },
      {
        "name": "Me",
        "name_fa": "راهبر",
        "role": "user",
        "age": 24,
        "conditions": "راهبر سیستم",
        "medical_history": "",
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
        "assigned_to": "راهبر",
        "icon": "🍽️"
      },
      {
        "title_fa": "غذا دادن و رسیدگی به پرنده",
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

## Phase 4: Informed Consent & Member Baseline Drill

When each member joins via `https://t.me/<bot_username>?start=member_<id>`:

1. **Informed Consent & Privacy Charter (منشور رضایت آگاهانه)**:
   - System clarifies purpose: Supportive AI behavioral & cognitive assistant.
   - Voluntary participation: Free to participate or opt-out.
   - **Confidentiality Guarantee**: Personal reflections, grievances, and interpersonal feelings are stored confidentially/vectorized. No human (including the system leader) can view raw personal confessions. Only the AI clinical engine processes them to formulate indirect, compassionate scaffolds.

2. **Baseline Clinical & Interpersonal Drill**:
   - **Medical Context**: Detailed medication, sleep, physical constraints.
   - **Confidential Pairwise Dynamics**:
     - *"در رابطه با X چه مسئله‌ای بیشتر از همه شما را آزرده است؟"*
     - *"در رابطه با X چه ویژگی یا رفتاری را بیشتر از همه تحسین می‌کنید؟"*
   - **Systemic Climate Likert Scales (1 to 5)**:
     - 🛡️ **Psychological Safety**: *"چقدر در این خانه احساس امنیت روانی و پذیرفته شدن دارید؟"*
     - 👑 **Respect & Status**: *"چقدر احساس می‌کنید نظرات و جایگاه شما در خانواده محترم است؟"*
     - ❤️ **Perceived Care**: *"در سختی‌ها چقدر مطمئنید خانواده از شما مراقبت می‌کند؟"*
     - 🏡 **Family Climate**: *"فضای کلی خانه را چطور ارزیابی می‌کنید؟"*

---

## Phase 5: Monthly Longitudinal Re-assessments & Adaptive Tuning

1. **Monthly Evaluation Trigger (Every 30 Days)**:
   - Automated webhook: `POST http://127.0.0.1:5055/api/scheduler/trigger-monthly-evaluations`.
   - Re-administers the 4 core Likert scale questions to measure psychological delta.

2. **Closed-Loop Intervention Adaptation**:
   - The AI analysis engine compares monthly evaluations against baseline:
     - If **Perceived Care** drops: Auto-suggests chore burden reduction and targeted appreciation prompts.
     - If **Psychological Safety** drops: Suggests stronger communication pauses and active listening scaffolds.
     - If **Elderly Agency** drops: Refines cognitive habits and daily structured activities.
   - All adjustments are logged into `intervention_adaptations` table for longitudinal audit.

---

## Scheduling & Agent Manager Webhooks

If the **Agent Manager** handles recurring schedules:
- **09:00 Daily**: `POST http://127.0.0.1:5055/api/scheduler/trigger-morning` (Dispatches morning mood check-ins).
- **20:00 Daily**: `POST http://127.0.0.1:5055/api/scheduler/trigger-evening` (Dispatches chore completion check).
- **1st of Month 10:00**: `POST http://127.0.0.1:5055/api/scheduler/trigger-monthly-evaluations` (Dispatches monthly evaluation drill).
- **Saturday 21:00**: `POST http://127.0.0.1:5055/api/scheduler/trigger-weekly-review` (Generates weekly report & adapts interventions).
