"""
FastAPI / Web Dashboard Backend for Scalable Family Evolution System
Comprehensive REST APIs with full CRUD, agent-driven setup templates, and scheduler webhooks.
"""
import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from core.config import config, AppConfig, BASE_DIR
from data.database import (
    init_db,
    get_db_connection,
    save_family_profile,
    get_family_profile,
    get_family_goals,
    initialize_full_family_template,
    create_member,
    update_member,
    delete_member,
    get_all_members,
    get_member_by_id,
    unbind_telegram_id,
    create_chore,
    update_chore,
    delete_chore,
    get_all_chores,
    get_today_chores_all,
    get_calendar_events,
    update_chore_status,
    swap_chore_assignee,
    create_habit,
    update_habit,
    delete_habit,
    get_member_habits,
    toggle_habit_log,
    log_checkin,
    log_conflict,
    get_stats_summary,
    get_latest_reports,
    generate_schedule_for_days
)
from brain.ai_engine import ai_engine
from brain.reporter import generate_weekly_analysis
from bot.telegram_bot import telegram_bot
from bot.scheduler import family_scheduler

logger = logging.getLogger(__name__)

app = FastAPI(title="Family Evolution Hub", version="2.5.0")

# Setup directories
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- Pydantic Request Models ---
class MemberCreateReq(BaseModel):
    name: str
    name_fa: str
    role: str
    age: Optional[int] = None
    conditions: Optional[str] = None
    avatar: Optional[str] = "👤"
    is_leader: Optional[int] = 0
    is_co_leader: Optional[int] = 0

class MemberUpdateReq(BaseModel):
    name: str
    name_fa: str
    role: str
    age: Optional[int] = None
    conditions: Optional[str] = None
    avatar: Optional[str] = "👤"
    is_leader: Optional[int] = 0
    is_co_leader: Optional[int] = 0
    telegram_id: Optional[int] = None

class ChoreCreateReq(BaseModel):
    title_fa: str
    title_en: Optional[str] = "Chore"
    category: str = "cleaning"
    frequency: str = "daily"
    default_assignee_id: Optional[int] = None
    difficulty: Optional[str] = "medium"
    icon: Optional[str] = "📋"

class ChoreUpdateReq(BaseModel):
    title_fa: str
    title_en: Optional[str] = "Chore"
    category: str
    frequency: str
    default_assignee_id: Optional[int] = None
    difficulty: Optional[str] = "medium"
    icon: Optional[str] = "📋"

class ChoreToggleReq(BaseModel):
    schedule_id: int
    status: str

class HabitCreateReq(BaseModel):
    member_id: int
    title_fa: str
    title_en: Optional[str] = "Habit"
    category: str = "general"
    target_frequency: str = "daily"
    reminder_time: Optional[str] = None

class HabitUpdateReq(BaseModel):
    member_id: int
    title_fa: str
    title_en: Optional[str] = "Habit"
    category: str = "general"
    target_frequency: str = "daily"
    reminder_time: Optional[str] = None

class HabitToggleReq(BaseModel):
    habit_id: int
    member_id: int
    date: Optional[str] = None

class ConflictReq(BaseModel):
    reported_by_id: Optional[int] = None
    involved: str
    trigger: str
    severity: int = 1
    resolution: Optional[str] = ""

class TemplateInitReq(BaseModel):
    template: dict

class BroadcastReq(BaseModel):
    message: str

class ConfigSaveReq(BaseModel):
    telegram_bot_token: Optional[str] = None
    telegram_proxy: Optional[str] = None
    use_proxy: Optional[bool] = None
    llm_provider: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    language: Optional[str] = None

# --- Lifespan & Startup ---
@app.on_event("startup")
async def startup_event():
    init_db(seed_defaults=False)
    try:
        family_scheduler.start()
    except Exception as e:
        logger.warning(f"Scheduler start warning: {e}")
    try:
        telegram_bot.build_application()
        if telegram_bot.app:
            asyncio.create_task(telegram_bot.app.initialize())
            asyncio.create_task(telegram_bot.app.start())
            asyncio.create_task(telegram_bot.app.updater.start_polling(drop_pending_updates=True))
            logger.info("Telegram Bot polling started.")
    except Exception as e:
        logger.error(f"Telegram Bot initialization warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        family_scheduler.stop()
        if telegram_bot.app and telegram_bot.app.updater:
            await telegram_bot.app.updater.stop()
            await telegram_bot.app.stop()
            await telegram_bot.app.shutdown()
    except Exception:
        pass

# --- Page Route ---
@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"config": config})

# --- System Status & Settings ---
@app.get("/api/status")
async def get_system_status():
    members = get_all_members()
    linked_count = sum(1 for m in members if m["telegram_id"])
    return {
        "status": "online",
        "bot_configured": bool(config.telegram_bot_token),
        "bot_username": telegram_bot.bot_info.get("username") if telegram_bot.bot_info else "",
        "llm_provider": config.llm_provider,
        "llm_endpoint": config.llm_base_url,
        "llm_model": config.llm_model,
        "proxy": config.telegram_proxy if config.use_proxy else "Direct",
        "members_count": len(members),
        "linked_members_count": linked_count,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config")
async def api_get_config():
    return {
        "telegram_bot_token": config.telegram_bot_token,
        "telegram_proxy": config.telegram_proxy,
        "use_proxy": config.use_proxy,
        "llm_provider": config.llm_provider,
        "llm_base_url": config.llm_base_url,
        "llm_model": config.llm_model,
        "llm_api_key": config.llm_api_key,
        "gemini_api_key": config.gemini_api_key,
        "language": config.language
    }

@app.post("/api/config/save")
async def api_save_config(req: ConfigSaveReq):
    if req.telegram_bot_token is not None:
        config.telegram_bot_token = req.telegram_bot_token.strip()
    if req.telegram_proxy is not None:
        config.telegram_proxy = req.telegram_proxy.strip()
    if req.use_proxy is not None:
        config.use_proxy = req.use_proxy
    if req.llm_provider is not None:
        config.llm_provider = req.llm_provider
    if req.llm_base_url is not None:
        config.llm_base_url = req.llm_base_url.strip()
    if req.llm_model is not None:
        config.llm_model = req.llm_model.strip()
    if req.llm_api_key is not None:
        config.llm_api_key = req.llm_api_key.strip()
    if req.gemini_api_key is not None:
        config.gemini_api_key = req.gemini_api_key.strip()
    if req.language is not None:
        config.language = req.language
    config.save()
    return {"status": "ok", "message": "Settings saved successfully."}

@app.post("/api/telegram/test-connection")
async def api_test_telegram():
    result = telegram_bot.test_connection()
    return result

@app.post("/api/ai/test-connection")
async def api_test_ai():
    result = ai_engine.test_connection()
    return result

# --- Agent Template Setup & Blueprint ---
@app.get("/api/setup/template")
async def api_get_template():
    profile = get_family_profile()
    goals = get_family_goals()
    members = get_all_members()
    chores = get_all_chores()
    return {
        "profile": profile,
        "goals": goals,
        "members": members,
        "chores": chores
    }

@app.post("/api/setup/initialize-template")
async def api_initialize_template(req: TemplateInitReq):
    try:
        res = initialize_full_family_template(req.template)
        return res
    except Exception as e:
        logger.error(f"Initialize template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/setup/reset-database")
async def api_reset_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habit_logs")
    cursor.execute("DELETE FROM habits")
    cursor.execute("DELETE FROM chore_schedule")
    cursor.execute("DELETE FROM chores")
    cursor.execute("DELETE FROM checkins")
    cursor.execute("DELETE FROM conflicts")
    cursor.execute("DELETE FROM reports")
    cursor.execute("DELETE FROM family_goals")
    cursor.execute("DELETE FROM family_profile")
    cursor.execute("DELETE FROM members")
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Database cleared completely."}

# --- Members CRUD ---
@app.get("/api/members")
async def api_get_members():
    return get_all_members()

@app.post("/api/members")
async def api_create_member(m: MemberCreateReq):
    mid = create_member(
        name=m.name,
        name_fa=m.name_fa,
        role=m.role,
        age=m.age,
        conditions=m.conditions,
        avatar=m.avatar or "👤",
        is_leader=m.is_leader or 0,
        is_co_leader=m.is_co_leader or 0
    )
    return {"status": "ok", "member_id": mid}

@app.put("/api/members/{member_id}")
async def api_update_member(member_id: int, m: MemberUpdateReq):
    ok = update_member(
        member_id=member_id,
        name=m.name,
        name_fa=m.name_fa,
        role=m.role,
        age=m.age,
        conditions=m.conditions,
        avatar=m.avatar or "👤",
        is_leader=m.is_leader or 0,
        is_co_leader=m.is_co_leader or 0,
        telegram_id=m.telegram_id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"status": "ok"}

@app.delete("/api/members/{member_id}")
async def api_delete_member(member_id: int):
    ok = delete_member(member_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"status": "ok"}

@app.post("/api/members/{member_id}/unbind")
async def api_unbind_member_telegram(member_id: int):
    unbind_telegram_id(member_id)
    return {"status": "ok"}

# --- Chores CRUD ---
@app.get("/api/chores")
async def api_get_all_chores():
    return get_all_chores()

@app.post("/api/chores/add")
async def api_create_chore(req: ChoreCreateReq):
    cid = create_chore(
        title_fa=req.title_fa,
        title_en=req.title_en or "Chore",
        category=req.category,
        frequency=req.frequency,
        default_assignee_id=req.default_assignee_id,
        difficulty=req.difficulty or "medium",
        icon=req.icon or "📋"
    )
    return {"status": "ok", "chore_id": cid}

@app.put("/api/chores/{chore_id}")
async def api_update_chore(chore_id: int, req: ChoreUpdateReq):
    ok = update_chore(
        chore_id=chore_id,
        title_fa=req.title_fa,
        title_en=req.title_en or "Chore",
        category=req.category,
        frequency=req.frequency,
        default_assignee_id=req.default_assignee_id,
        difficulty=req.difficulty or "medium",
        icon=req.icon or "📋"
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Chore not found")
    return {"status": "ok"}

@app.delete("/api/chores/{chore_id}")
async def api_delete_chore(chore_id: int):
    ok = delete_chore(chore_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Chore not found")
    return {"status": "ok"}

@app.get("/api/chores/today")
async def api_get_today_chores():
    return get_today_chores_all()

@app.post("/api/chores/toggle")
async def api_toggle_chore(req: ChoreToggleReq):
    success = update_chore_status(req.schedule_id, req.status)
    return {"status": "ok" if success else "not_found"}

# --- Habits CRUD ---
@app.get("/api/habits")
async def api_get_habits():
    members = get_all_members()
    result = []
    for m in members:
        habits = get_member_habits(m["id"])
        result.append({
            "member": m,
            "habits": habits
        })
    return result

@app.post("/api/habits/add")
async def api_create_habit(req: HabitCreateReq):
    hid = create_habit(
        member_id=req.member_id,
        title_fa=req.title_fa,
        title_en=req.title_en or "Habit",
        category=req.category,
        target_frequency=req.target_frequency,
        reminder_time=req.reminder_time
    )
    return {"status": "ok", "habit_id": hid}

@app.put("/api/habits/{habit_id}")
async def api_update_habit(habit_id: int, req: HabitUpdateReq):
    ok = update_habit(
        habit_id=habit_id,
        member_id=req.member_id,
        title_fa=req.title_fa,
        title_en=req.title_en or "Habit",
        category=req.category,
        target_frequency=req.target_frequency,
        reminder_time=req.reminder_time
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"status": "ok"}

@app.delete("/api/habits/{habit_id}")
async def api_delete_habit(habit_id: int):
    ok = delete_habit(habit_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"status": "ok"}

@app.post("/api/habits/toggle")
async def api_toggle_habit(req: HabitToggleReq):
    new_status = toggle_habit_log(req.habit_id, req.member_id, req.date)
    return {"status": "ok", "new_status": new_status}

# --- Calendar & Stats ---
@app.get("/api/calendar")
async def api_get_calendar(start: Optional[str] = None, end: Optional[str] = None):
    start_date = start or (date.today() - timedelta(days=7)).isoformat()
    end_date = end or (date.today() + timedelta(days=14)).isoformat()
    return get_calendar_events(start_date, end_date)

@app.get("/api/stats")
async def api_get_stats(days: int = 7):
    return get_stats_summary(days=days)

@app.get("/api/reports")
async def api_get_reports(limit: int = 5):
    return get_latest_reports(limit=limit)

@app.post("/api/conflicts/add")
async def api_log_conflict(req: ConflictReq):
    log_conflict(req.reported_by_id, req.involved, req.trigger, req.severity, req.resolution)
    return {"status": "ok"}

@app.post("/api/analysis/run")
async def api_run_analysis():
    try:
        leader_report, family_broadcast, stats = generate_weekly_analysis(days=7)
        return {
            "status": "ok",
            "leader_report": leader_report,
            "family_broadcast": family_broadcast,
            "metrics": stats
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Scheduler Webhooks (Agent Manager / Cron friendly) ---
@app.post("/api/scheduler/trigger-morning")
async def api_scheduler_morning():
    res = await telegram_bot.dispatch_morning_checkins()
    return {"status": "ok", "dispatched": res}

@app.post("/api/scheduler/trigger-evening")
async def api_scheduler_evening():
    res = await telegram_bot.dispatch_evening_checkins()
    return {"status": "ok", "dispatched": res}

@app.post("/api/scheduler/trigger-weekly-review")
async def api_scheduler_weekly():
    leader_report, family_broadcast, stats = generate_weekly_analysis(days=7)
    await telegram_bot.dispatch_custom_broadcast(f"📊 **پیام هفتگی آرامش و پیشرفت خانه:**\n\n{family_broadcast}")
    return {"status": "ok", "metrics": stats}

# --- Telegram Dispatches ---
@app.post("/api/telegram/broadcast")
async def api_send_broadcast(req: BroadcastReq):
    res = await telegram_bot.dispatch_custom_broadcast(req.message)
    return res

@app.post("/api/telegram/trigger-morning")
async def api_trigger_morning():
    res = await telegram_bot.dispatch_morning_checkins()
    return res

@app.post("/api/telegram/trigger-evening")
async def api_trigger_evening():
    res = await telegram_bot.dispatch_evening_checkins()
    return res
