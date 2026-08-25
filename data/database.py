"""
Database Operations and Models for Scalable Family Evolution Engine
100% Clean, Dynamic, and Non-mocked. Supports Agent-Driven Setup & Templates.
"""
import sqlite3
import json
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from core.config import config, BASE_DIR

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.db_path, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(seed_defaults: bool = False):
    """Initialize clean database tables without any hardcoded mock data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    schema_path = BASE_DIR / "data" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()

# Auto ensure schema on import
try:
    init_db(seed_defaults=False)
except Exception:
    pass


# --- Family Profile & Blueprint ---

def save_family_profile(family_name: str, overview: str, communication_rules: list, emergency_resources: list) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM family_profile")
    cursor.execute(
        """INSERT INTO family_profile (family_name, overview, communication_rules_json, emergency_resources_json, updated_at)
           VALUES (?, ?, ?, ?, datetime('now'))""",
        (
            family_name,
            overview,
            json.dumps(communication_rules, ensure_ascii=False),
            json.dumps(emergency_resources, ensure_ascii=False)
        )
    )
    pid = cursor.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_family_profile() -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM family_profile ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["communication_rules"] = json.loads(data["communication_rules_json"]) if data.get("communication_rules_json") else []
    data["emergency_resources"] = json.loads(data["emergency_resources_json"]) if data.get("emergency_resources_json") else []
    return data

def add_family_goal(goal_type: str, title: str, description: str, target_date: Optional[str] = None, steps: Optional[list] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO family_goals (goal_type, title, description, target_date, steps_json)
           VALUES (?, ?, ?, ?, ?)""",
        (goal_type, title, description, target_date, json.dumps(steps or [], ensure_ascii=False))
    )
    gid = cursor.lastrowid
    conn.commit()
    conn.close()
    return gid

def get_family_goals() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM family_goals ORDER BY goal_type DESC, id ASC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        item = dict(r)
        item["steps"] = json.loads(item["steps_json"]) if item.get("steps_json") else []
        result.append(item)
    return result

def initialize_full_family_template(template_json: dict) -> Dict[str, Any]:
    """
    Called by AI Agent after drilling the user. Atomically populates:
    - Family Profile (Name, Overview, Communication Rules, Free Resources)
    - Short-term & Long-term Goals + Action Steps
    - Members (Roles, Ages, Conditions, Avatars)
    - Chores Matrix & Dynamic Scheduling
    - Health Habits & Scaffolds
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Profile
    profile = template_json.get("family_profile", {})
    family_name = profile.get("family_name", "خانواده ما")
    overview = profile.get("overview", "")
    comm_rules = template_json.get("communication_rules", [])
    emergency_res = template_json.get("emergency_and_free_resources", [])
    
    cursor.execute("DELETE FROM family_profile")
    cursor.execute(
        """INSERT INTO family_profile (family_name, overview, communication_rules_json, emergency_resources_json, updated_at)
           VALUES (?, ?, ?, ?, datetime('now'))""",
        (family_name, overview, json.dumps(comm_rules, ensure_ascii=False), json.dumps(emergency_res, ensure_ascii=False))
    )
    
    # 2. Goals
    cursor.execute("DELETE FROM family_goals")
    for g in template_json.get("short_term_goals", []):
        cursor.execute(
            """INSERT INTO family_goals (goal_type, title, description, target_date, steps_json)
               VALUES ('short_term', ?, ?, ?, ?)""",
            (g.get("title", ""), g.get("description", ""), g.get("target_date", "1 ماه آینده"), json.dumps(g.get("steps", []), ensure_ascii=False))
        )
    for g in template_json.get("long_term_goals", []):
        cursor.execute(
            """INSERT INTO family_goals (goal_type, title, description, target_date, steps_json)
               VALUES ('long_term', ?, ?, ?, ?)""",
            (g.get("title", ""), g.get("description", ""), g.get("target_date", "6 ماه آینده"), json.dumps(g.get("steps", []), ensure_ascii=False))
        )

    # 3. Members
    member_map = {}
    for m in template_json.get("members", []):
        name_fa = m.get("name_fa", "عضو")
        name = m.get("name", name_fa)
        role = m.get("role", "member")
        age = m.get("age", None)
        conditions = m.get("conditions", "")
        avatar = m.get("avatar", "👤")
        is_leader = 1 if m.get("is_leader") or "راهبر" in name_fa else 0
        is_co_leader = 1 if m.get("is_co_leader") or "همیار" in name_fa else 0

        cursor.execute(
            """INSERT INTO members (name, name_fa, role, age, conditions, avatar, is_leader, is_co_leader)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, name_fa, role, age, conditions, avatar, is_leader, is_co_leader)
        )
        mid = cursor.lastrowid
        member_map[name_fa] = mid
        member_map[name] = mid

    # 4. Chores
    for c in template_json.get("chores", []):
        title_fa = c.get("title_fa", "کار خانه")
        title_en = c.get("title_en", "Chore")
        category = c.get("category", "cleaning")
        freq = c.get("frequency", "daily")
        assignee_name = c.get("assigned_to", "")
        icon = c.get("icon", "📋")
        
        assignee_id = member_map.get(assignee_name)
        if not assignee_id and member_map:
            assignee_id = list(member_map.values())[0]

        cursor.execute(
            """INSERT INTO chores (title_fa, title_en, category, frequency, default_assignee_id, icon)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title_fa, title_en, category, freq, assignee_id, icon)
        )

    # 5. Habits
    for h in template_json.get("habits", []):
        target_name = h.get("target_member", "")
        habit_text = h.get("habit", "")
        freq = h.get("frequency", "روزانه")
        category = h.get("category", "general")
        reminder = h.get("reminder_time", "09:00")
        
        assignee_id = member_map.get(target_name)
        if not assignee_id and member_map:
            assignee_id = list(member_map.values())[0]

        if assignee_id:
            cursor.execute(
                """INSERT INTO habits (member_id, title_fa, title_en, category, target_frequency, reminder_time)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (assignee_id, habit_text, habit_text, category, freq, reminder)
            )

    conn.commit()
    generate_schedule_for_days(conn, days_ahead=7)
    conn.close()
    
    return {
        "status": "ok",
        "members_count": len(template_json.get("members", [])),
        "chores_count": len(template_json.get("chores", [])),
        "habits_count": len(template_json.get("habits", [])),
        "goals_count": len(template_json.get("short_term_goals", [])) + len(template_json.get("long_term_goals", []))
    }

# --- Member CRUD ---

def create_member(name: str, name_fa: str, role: str, age: Optional[int] = None, 
                  conditions: Optional[str] = None, avatar: str = "👤", 
                  is_leader: int = 0, is_co_leader: int = 0) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO members (name, name_fa, role, age, conditions, avatar, is_leader, is_co_leader)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, name_fa, role, age, conditions, avatar, is_leader, is_co_leader)
    )
    member_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return member_id

def update_member(member_id: int, name: str, name_fa: str, role: str, age: Optional[int] = None, 
                  conditions: Optional[str] = None, avatar: str = "👤", 
                  is_leader: int = 0, is_co_leader: int = 0, telegram_id: Optional[int] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE members 
           SET name = ?, name_fa = ?, role = ?, age = ?, conditions = ?, avatar = ?, 
               is_leader = ?, is_co_leader = ?, telegram_id = ?
           WHERE id = ?""",
        (name, name_fa, role, age, conditions, avatar, is_leader, is_co_leader, telegram_id, member_id)
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_member(member_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habit_logs WHERE member_id = ?", (member_id,))
    cursor.execute("DELETE FROM habits WHERE member_id = ?", (member_id,))
    cursor.execute("DELETE FROM chore_schedule WHERE member_id = ?", (member_id,))
    cursor.execute("DELETE FROM checkins WHERE member_id = ?", (member_id,))
    cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def get_all_members() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_member_by_id(member_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_member_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def link_telegram_id(member_id: int, telegram_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET telegram_id = ? WHERE id = ?", (telegram_id, member_id))
    conn.commit()
    conn.close()

def unbind_telegram_id(member_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET telegram_id = NULL WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

# --- Chores CRUD ---

def create_chore(title_fa: str, title_en: str, category: str, frequency: str, 
                 default_assignee_id: Optional[int], difficulty: str = "medium", icon: str = "📋") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO chores (title_fa, title_en, category, frequency, default_assignee_id, difficulty, icon)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (title_fa, title_en, category, frequency, default_assignee_id, difficulty, icon)
    )
    chore_id = cursor.lastrowid
    conn.commit()
    
    if default_assignee_id:
        today_str = date.today().isoformat()
        cursor.execute(
            """INSERT INTO chore_schedule (chore_id, member_id, date, status)
               VALUES (?, ?, ?, 'pending')""",
            (chore_id, default_assignee_id, today_str)
        )
        conn.commit()

    conn.close()
    return chore_id

def update_chore(chore_id: int, title_fa: str, title_en: str, category: str, frequency: str, 
                 default_assignee_id: Optional[int], difficulty: str = "medium", icon: str = "📋") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE chores 
           SET title_fa = ?, title_en = ?, category = ?, frequency = ?, 
               default_assignee_id = ?, difficulty = ?, icon = ?
           WHERE id = ?""",
        (title_fa, title_en, category, frequency, default_assignee_id, difficulty, icon, chore_id)
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_chore(chore_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chore_schedule WHERE chore_id = ?", (chore_id,))
    cursor.execute("DELETE FROM chores WHERE id = ?", (chore_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def get_all_chores() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT c.*, m.name_fa as assignee_name_fa, m.avatar as assignee_avatar
           FROM chores c
           LEFT JOIN members m ON c.default_assignee_id = m.id
           ORDER BY c.id ASC"""
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def generate_schedule_for_days(conn: sqlite3.Connection, days_ahead: int = 7):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chores WHERE default_assignee_id IS NOT NULL")
    chores = cursor.fetchall()
    
    today = date.today()
    for i in range(days_ahead + 1):
        curr_date = (today + timedelta(days=i)).isoformat()
        for chore in chores:
            chore_id = chore["id"]
            assignee_id = chore["default_assignee_id"]
            freq = chore["frequency"]
            
            if freq == "every_2_days" and i % 2 != 0:
                continue
            if freq == "weekly" and i != 0 and i != 6:
                continue
            
            cursor.execute(
                "SELECT id FROM chore_schedule WHERE chore_id = ? AND date = ?",
                (chore_id, curr_date)
            )
            if not cursor.fetchone():
                cursor.execute(
                    """INSERT INTO chore_schedule (chore_id, member_id, date, status)
                       VALUES (?, ?, ?, 'pending')""",
                    (chore_id, assignee_id, curr_date)
                )
    conn.commit()

def get_today_chores_for_member(member_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    cursor.execute(
        """SELECT cs.id as schedule_id, cs.status, c.id as chore_id, c.title_fa, c.title_en, c.icon, c.category
           FROM chore_schedule cs
           JOIN chores c ON cs.chore_id = c.id
           WHERE cs.member_id = ? AND cs.date = ?""",
        (member_id, today_str)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_today_chores_all() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    cursor.execute(
        """SELECT cs.id as schedule_id, cs.date, cs.status, cs.completed_at,
                  c.id as chore_id, c.title_fa, c.title_en, c.icon, c.category, c.difficulty,
                  m.id as member_id, m.name_fa, m.name, m.avatar
           FROM chore_schedule cs
           JOIN chores c ON cs.chore_id = c.id
           JOIN members m ON cs.member_id = m.id
           WHERE cs.date = ?
           ORDER BY cs.status DESC, c.id ASC""",
        (today_str,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_calendar_events(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT cs.id as schedule_id, cs.date, cs.status, cs.completed_at,
                  c.id as chore_id, c.title_fa, c.title_en, c.icon, c.category,
                  m.id as member_id, m.name_fa, m.name, m.avatar
           FROM chore_schedule cs
           JOIN chores c ON cs.chore_id = c.id
           JOIN members m ON cs.member_id = m.id
           WHERE cs.date BETWEEN ? AND ?
           ORDER BY cs.date ASC, c.id ASC""",
        (start_date, end_date)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def update_chore_status(schedule_id: int, status: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    completed_at = datetime.now().strftime("%H:%M:%S") if status == "done" else None
    cursor.execute(
        "UPDATE chore_schedule SET status = ?, completed_at = ? WHERE id = ?",
        (status, completed_at, schedule_id)
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def swap_chore_assignee(schedule_id: int, new_member_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chore_schedule SET member_id = ?, status = 'pending' WHERE id = ?",
        (new_member_id, schedule_id)
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

# --- Habits CRUD ---

def create_habit(member_id: int, title_fa: str, title_en: str, category: str = "general", 
                 target_frequency: str = "daily", reminder_time: Optional[str] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO habits (member_id, title_fa, title_en, category, target_frequency, reminder_time)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (member_id, title_fa, title_en, category, target_frequency, reminder_time)
    )
    habit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return habit_id

def update_habit(habit_id: int, member_id: int, title_fa: str, title_en: str, category: str = "general", 
                 target_frequency: str = "daily", reminder_time: Optional[str] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE habits 
           SET member_id = ?, title_fa = ?, title_en = ?, category = ?, 
               target_frequency = ?, reminder_time = ?
           WHERE id = ?""",
        (member_id, title_fa, title_en, category, target_frequency, reminder_time, habit_id)
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_habit(habit_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habit_logs WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def get_member_habits(member_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    cursor.execute(
        """SELECT h.*, 
                  (SELECT status FROM habit_logs hl WHERE hl.habit_id = h.id AND hl.date = ?) as today_status
           FROM habits h
           WHERE h.member_id = ?""",
        (today_str, member_id)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def toggle_habit_log(habit_id: int, member_id: int, target_date: str = None) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    d_str = target_date or date.today().isoformat()
    now_str = datetime.now().strftime("%H:%M:%S")
    
    cursor.execute(
        "SELECT id, status FROM habit_logs WHERE habit_id = ? AND member_id = ? AND date = ?",
        (habit_id, member_id, d_str)
    )
    row = cursor.fetchone()
    if row:
        new_status = "missed" if row["status"] == "done" else "done"
        cursor.execute("UPDATE habit_logs SET status = ?, logged_at = ? WHERE id = ?", (new_status, now_str, row["id"]))
    else:
        new_status = "done"
        cursor.execute(
            """INSERT INTO habit_logs (habit_id, member_id, date, status, logged_at)
               VALUES (?, ?, ?, 'done', ?)""",
            (habit_id, member_id, d_str, now_str)
        )
    conn.commit()
    conn.close()
    return new_status

# --- Checkins & Conflicts ---

def log_checkin(member_id: int, mood: int, notes: str = "", checkin_type: str = "morning", anger: int = 0, win: str = "") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M:%S")
    
    cursor.execute(
        """INSERT INTO checkins (member_id, date, time, checkin_type, mood, notes, anger_reported, win_of_the_day)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (member_id, today_str, now_time, checkin_type, mood, notes, anger, win)
    )
    checkin_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return checkin_id

def log_conflict(reported_by_id: Optional[int], involved: str, trigger: str, severity: int, resolution: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    cursor.execute(
        """INSERT INTO conflicts (date, reported_by_id, involved_members, trigger_reason, severity, resolution_notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (today_str, reported_by_id, involved, trigger, severity, resolution)
    )
    conn.commit()
    conn.close()

# --- Real Analytical Metrics (No Mock Values) ---

def get_stats_summary(days: int = 7) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_date = (date.today() - timedelta(days=days)).isoformat()
    today_str = date.today().isoformat()
    
    cursor.execute(
        "SELECT AVG(mood) as avg_mood, COUNT(*) as count FROM checkins WHERE date >= ?",
        (start_date,)
    )
    checkin_stat = cursor.fetchone()
    has_checkins = (checkin_stat["count"] or 0) > 0
    avg_mood = round(checkin_stat["avg_mood"], 1) if (has_checkins and checkin_stat["avg_mood"] is not None) else None
    
    cursor.execute(
        """SELECT m.id, m.name_fa, m.name, AVG(c.mood) as member_avg_mood, COUNT(c.id) as checkins_count
           FROM members m
           LEFT JOIN checkins c ON m.id = c.member_id AND c.date >= ?
           GROUP BY m.id""",
        (start_date,)
    )
    member_moods = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute(
        """SELECT 
               COUNT(*) as total_scheduled,
               SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done_count
           FROM chore_schedule
           WHERE date BETWEEN ? AND ?""",
        (start_date, today_str)
    )
    chore_stat = cursor.fetchone()
    total_chores = chore_stat["total_scheduled"] or 0
    done_chores = chore_stat["done_count"] or 0
    chore_rate = round((done_chores / total_chores * 100), 1) if total_chores > 0 else None
    
    cursor.execute(
        "SELECT COUNT(*) as conflict_count FROM conflicts WHERE date >= ?",
        (start_date,)
    )
    conflict_count = cursor.fetchone()["conflict_count"] or 0
    
    conn.close()
    return {
        "days": days,
        "has_data": has_checkins or (total_chores > 0),
        "avg_mood": avg_mood,
        "member_moods": member_moods,
        "total_chores": total_chores,
        "done_chores": done_chores,
        "chore_completion_rate": chore_rate,
        "conflict_count": conflict_count
    }

def save_ai_report(report_type: str, summary_fa: str, summary_en: str, recommendations: list, metrics: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    now_str = datetime.now().isoformat()
    
    cursor.execute(
        """INSERT INTO reports (report_type, period_start, period_end, summary_fa, summary_en, recommendations_json, metrics_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (report_type, today_str, today_str, summary_fa, summary_en, json.dumps(recommendations, ensure_ascii=False), json.dumps(metrics, ensure_ascii=False), now_str)
    )
    conn.commit()
    conn.close()

def get_latest_reports(limit: int = 5) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
