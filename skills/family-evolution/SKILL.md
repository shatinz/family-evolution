---
name: family-evolution
description: "AI-Powered Family Behavioral & Cognitive Evolution Engine. Conducts an interactive setup drill, builds custom family scaffolding, capability-aware rotational chore calendars, dementia/elderly agency routines, informed consent, longitudinal evaluations, MCP server for Claude Desktop / Claude Code, and manages Telegram bot interactions."
---

# Family Evolution Skill 🌿

An autonomous AI engine and clinical-behavioral management platform designed to bring calm, structure, psychological safety, and behavioral scaffolding to households.

---

## 🚀 Multi-Agent & Platform Deployment Modes

Family Evolution can operate seamlessly across multiple agent environments:

| Platform | Integration Mode | Entry Point / Configuration |
| :--- | :--- | :--- |
| **Antigravity** | Native Skill | Auto-discovered via `family-evolution` skill or `/family` |
| **Claude Desktop** | Model Context Protocol (MCP) | `claude_desktop_config.json` running `mcp_server.py` |
| **Claude Code** | Stdio MCP Tool / Skill | CLI integration via `mcp_server.py` |
| **Direct API Key** | Autonomous Engine | OpenAI-compatible (`/v1`) or Google Gemini API Key |

---

## 🛠️ Claude Desktop One-Click MCP Setup

To install the Family Evolution tools into **Claude Desktop**, add this block to your `claude_desktop_config.json` (located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "family-evolution": {
      "command": "python",
      "args": [
        "C:\\Users\\PC\\prj\\family-evoloution\\mcp_server.py"
      ]
    }
  }
}
```

### Available MCP Tools

Once installed, Claude can autonomously call:
1. `get_family_status`: Returns members, today's chore completions, mood check-ins, and systemic health trends.
2. `get_weekly_chore_matrix`: Returns 7-day Persian schedule matrix (Saturday to Friday) with assignees, avatars, and statuses.
3. `rotate_chores_schedule`: Dynamically calculates and synchronizes fair round-robin chore rotations across family members.
4. `generate_weekly_ai_report`: Computes clinical evaluation analysis, producing a Leader Report and a supportive Family Broadcast.
5. `dispatch_telegram_broadcast`: Broadcasts messages to all linked Telegram accounts.
6. `log_clinical_evaluation`: Logs 4-axis Likert scores (Safety, Respect, Care, Climate) and private narrative vectors.
7. `backup_database_to_telegram`: Flushes SQLite WAL and sends the database file directly to the admin's Telegram chat.

---

## 🧹 Intelligent & Capability-Aware Chore Distribution Rules

When setting up or updating household chores, the AI MUST distribute duties based on individual cognitive, physical, and emotional capabilities:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CHORE ALLOCATION MATRIX                               │
├───────────────────────┬──────────────────────┬──────────────────────────────┤
│ Member Role / Context │ Capability Profile   │ Recommended Chores & Rules   │
├───────────────────────┼──────────────────────┼──────────────────────────────┤
│ 👴 Father             │ Elderly / Mild       │ • Non-hazardous, dignified   │
│                       │ Dementia             │   routines (Plant care 🌱)   │
│                       │                      │ • Light tidying, bird feed   │
│                       │                      │ • NEVER heavy / hot kitchen  │
├───────────────────────┼──────────────────────┼──────────────────────────────┤
│ 👵 Mother             │ Caregiver / Fatigue  │ • Relieved from daily dishes │
│                       │ Risk                 │ • Pleasant routines (After-  │
│                       │                      │   noon tea setup ☕)          │
├───────────────────────┼──────────────────────┼──────────────────────────────┤
│ 🧠 Leader / Sibling 1 │ Young Adult / High   │ • Active Rotational Pool     │
│ 👩 Sister / Sibling 2 │ Capacity             │ • Washing dishes (🍽️ Daily)   │
│ 👨 Brother / Sibling 3│                      │ • Cleaning living room (🛋️) │
│                       │                      │ • Sweeping floors (🧹 2-day) │
│                       │                      │ • Mopping floors (🧼 2/wk)   │
│                       │                      │ • Trash disposal (🗑️ Daily)  │
└───────────────────────┴──────────────────────┴──────────────────────────────┘
```

### Round-Robin Rotation Formula
For rotational chores (`is_rotational = 1`):
$$\text{Assignee ID} = \text{RotationPool}[(\text{DayOrdinal} + \text{ChoreID}) \pmod{|\text{RotationPool}|}]$$
This guarantees:
- Continuous, deterministic rotation across calendar dates without skips.
- Perfect turn distribution among adult siblings.
- Different rotational chores alternate so no single person receives all heavy tasks on the same day.

---

## 📋 Agent Execution Protocol (5 Phases)

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

### Phase 1: Interactive Diagnostic Drill
The AI Agent must proactively ask targeted, empathetic questions:
1. **Family Roster, Medical & Cognitive Context**: Names, Persian names, ages, conditions (elderly dementia, caregiver burnout, sleep issues).
2. **Household Chores & Friction Points**: Identify friction tasks (dishes, floor cleaning, trash) and who currently bears the burden.
3. **Elderly Agency Scaffolds**: Low-stress, live-feedback tasks for elderly members (plant care, bird feeding, photo sorting).
4. **Emotional De-escalation**: Communication boundaries (5-minute cooldown pause, weekly appreciation meeting).
5. **Roadmap & Goals**: Short-term (fair rotation, breathing habits) and Long-term (sustained harmony, cognitive retention).

### Phase 2: Credentials & Configuration
Configure Telegram Bot Token and LLM settings via `POST http://127.0.0.1:5055/api/config/save`:
```json
{
  "telegram_bot_token": "<TOKEN>",
  "gemini_api_key": "<GEMINI_KEY>",
  "llm_provider": "gemini_native",
  "telegram_proxy": "socks5h://127.0.0.1:10808",
  "use_proxy": true
}
```

### Phase 3: Template Synthesis & Blueprint
Format the family architecture into JSON and initialize via `POST http://127.0.0.1:5055/api/setup/initialize-template`:
```json
{
  "template": {
    "family_profile": {
      "family_name": "خانواده امید",
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
        "title": "حفظ استقلال شناختی و آرامش پایدار خانه",
        "description": "مهار افت حافظه از طریق مسئولیت‌های زنده و پیاده‌روی روزانه.",
        "target_date": "۶ ماه آینده",
        "steps": ["مراقبت روزانه از گلدان‌ها", "پیاده‌روی عصرگاهی", "جلسات هفتگی قدردانی"]
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
        "avatar": "👴"
      },
      {
        "name": "Mother",
        "name_fa": "مادر",
        "role": "mother",
        "age": 60,
        "conditions": "خستگی مراقبت، نیاز به آرامش و کاهش بار",
        "medical_history": "خستگی عاطفی و استرس مزمن",
        "avatar": "👵"
      },
      {
        "name": "Sister",
        "name_fa": "خواهر",
        "role": "sister",
        "age": 28,
        "conditions": "معلم زبان، مشارکت فعال در چرخش کارها",
        "avatar": "👩"
      },
      {
        "name": "Brother",
        "name_fa": "برادر",
        "role": "brother",
        "age": 22,
        "conditions": "دانشجو، مشارکت در نظافت و لجستیک",
        "avatar": "👨"
      },
      {
        "name": "Leader",
        "name_fa": "من (راهبر)",
        "role": "user",
        "age": 25,
        "conditions": "راهبر و هماهنگ‌کننده سیستم",
        "avatar": "🧠",
        "is_leader": 1
      }
    ],
    "chores": [
      {
        "title_fa": "شستن ظروف بعد ناهار و شام",
        "title_en": "Washing dishes",
        "category": "kitchen",
        "frequency": "daily",
        "is_rotational": 1,
        "rotation_pool": ["من (راهبر)", "خواهر", "برادر"],
        "icon": "🍽️"
      },
      {
        "title_fa": "مرتب کردن و گردگیری پذیرایی و هال",
        "title_en": "Cleaning the living room",
        "category": "cleaning",
        "frequency": "daily",
        "is_rotational": 1,
        "rotation_pool": ["خواهر", "برادر", "من (راهبر)"],
        "icon": "🛋️"
      },
      {
        "title_fa": "رسیدگی و آبیاری گلدان‌ها و گیاهان",
        "title_en": "Watering plants",
        "category": "plants_pets",
        "frequency": "daily",
        "assigned_to": "پدر",
        "is_rotational": 0,
        "icon": "🌱"
      },
      {
        "title_fa": "چیدمان چای و عصرانه آرامش خانواده",
        "title_en": "Afternoon tea setup",
        "category": "kitchen",
        "frequency": "daily",
        "assigned_to": "مادر",
        "is_rotational": 0,
        "icon": "☕"
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

### Phase 4: Informed Consent & Member Baseline Drill
When each member starts the bot via Telegram:
1. **Informed Consent**: System clarifies supportive purpose, voluntary participation, and **confidentiality guarantee** (narratives are stored confidentially for AI analysis only; no member or leader sees raw confessions).
2. **4-Axis Likert Baseline Drill (1 to 5)**:
   - 🛡️ **Psychological Safety**: *"چقدر در این خانه احساس امنیت روانی و پذیرفته شدن دارید؟"*
   - 👑 **Respect & Status**: *"چقدر احساس می‌کنید نظرات و جایگاه شما در خانواده محترم است؟"*
   - ❤️ **Perceived Care**: *"در سختی‌ها چقدر مطمئنید خانواده از شما مراقبت می‌کند؟"*
   - 🏡 **Family Climate**: *"فضای کلی خانه را چطور ارزیابی می‌کنید؟"*

### Phase 5: Monthly Longitudinal Re-assessments & Closed-Loop Tuning
- Automated 30-day re-evaluation: `POST http://127.0.0.1:5055/api/scheduler/trigger-monthly-evaluations`.
- The AI Engine compares scores against baseline:
  - Drop in **Perceived Care** -> Triggers chore re-balancing and appreciation nudges.
  - Drop in **Psychological Safety** -> Strengthens communication cooldown rules.
  - Drop in **Elderly Agency** -> Re-tunes cognitive habits.
- Adjustments are permanently tracked in `intervention_adaptations`.

---

## ⏰ Automated Webhook & Scheduler Triggers

- **09:00 Daily**: `POST http://127.0.0.1:5055/api/scheduler/trigger-morning` (Dispatches morning mood check-ins).
- **20:00 Daily**: `POST http://127.0.0.1:5055/api/scheduler/trigger-evening` (Dispatches chore completion check).
- **1st of Month 10:00**: `POST http://127.0.0.1:5055/api/scheduler/trigger-monthly-evaluations` (Dispatches monthly evaluation drill).
- **Saturday 21:00**: `POST http://127.0.0.1:5055/api/scheduler/trigger-weekly-review` (Generates weekly report, adapts interventions, and sends DB backup to Telegram).
