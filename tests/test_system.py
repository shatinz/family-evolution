"""
Comprehensive Unit and Integration Tests for Scalable Family Evolution System v2.5
Zero mock data, clean template initialization, and scheduler webhooks.
"""
import unittest
import os
import json
from pathlib import Path
from starlette.testclient import TestClient

from core.config import config, BASE_DIR
from data.database import (
    init_db,
    save_family_profile,
    get_family_profile,
    get_family_goals,
    initialize_full_family_template,
    create_member,
    update_member,
    delete_member,
    get_all_members,
    create_chore,
    update_chore,
    delete_chore,
    get_all_chores,
    create_habit,
    update_habit,
    delete_habit,
    get_member_habits,
    toggle_habit_log,
    log_checkin,
    log_conflict,
    get_stats_summary
)
from brain.ai_engine import ai_engine
from brain.reporter import generate_weekly_analysis
from api.app import app

class TestScalableFamilyEvolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = str(BASE_DIR / "data" / "test_family.db")
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass
        config.db_path = cls.test_db_path
        init_db(seed_defaults=False)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    def test_01_member_crud(self):
        mid = create_member(
            name="Sara",
            name_fa="سارا",
            role="sister",
            age=28,
            conditions="معلم زبان",
            avatar="👩"
        )
        self.assertGreater(mid, 0)
        
        members = get_all_members()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["name_fa"], "سارا")
        
        updated = update_member(
            member_id=mid,
            name="Sara Updated",
            name_fa="سارا رضایی",
            role="sister",
            age=29,
            conditions="معلم زبان و همیار"
        )
        self.assertTrue(updated)
        
        deleted = delete_member(mid)
        self.assertTrue(deleted)
        self.assertEqual(len(get_all_members()), 0)

    def test_02_chore_crud(self):
        mid = create_member(name="Ali", name_fa="علی", role="brother")
        cid = create_chore(
            title_fa="خرید نان",
            title_en="Buy bread",
            category="groceries",
            frequency="daily",
            default_assignee_id=mid,
            icon="🥖"
        )
        self.assertGreater(cid, 0)
        
        chores = get_all_chores()
        self.assertEqual(len(chores), 1)
        self.assertEqual(chores[0]["title_fa"], "خرید نان")
        
        updated = update_chore(
            chore_id=cid,
            title_fa="خرید نان سنگک",
            title_en="Buy Sangak bread",
            category="groceries",
            frequency="daily",
            default_assignee_id=mid,
            icon="🥖"
        )
        self.assertTrue(updated)
        
        deleted = delete_chore(cid)
        self.assertTrue(deleted)
        delete_member(mid)

    def test_03_habit_crud(self):
        mid = create_member(name="Father", name_fa="پدر", role="father")
        hid = create_habit(
            member_id=mid,
            title_fa="غذا دادن به پرنده",
            title_en="Bird feeding",
            category="cognitive"
        )
        self.assertGreater(hid, 0)
        
        status1 = toggle_habit_log(hid, mid, target_date="2099-01-01")
        self.assertEqual(status1, "done")
        status2 = toggle_habit_log(hid, mid, target_date="2099-01-01")
        self.assertEqual(status2, "missed")
        
        delete_habit(hid)
        delete_member(mid)

    def test_04_agent_template_initialization(self):
        sample_agent_template = {
            "family_profile": {
                "family_name": "خانواده نمونه",
                "overview": "طرح تحول ساختاری جهت ارتقای بهزیستی و تقسیم کار عادلانه."
            },
            "short_term_goals": [
                {
                    "title": "تقویم نظافت آشپزخانه",
                    "description": "کاهش بار کاری و چرخش نوبت",
                    "target_date": "۲ هفته آینده",
                    "steps": ["تعیین نوبت", "ارسال پیام یادآوری"]
                }
            ],
            "long_term_goals": [
                {
                    "title": "ارتقای تعاملات خانوادگی",
                    "description": "افزایش همدلی و کاهش اصطکاک",
                    "target_date": "۶ ماه آینده",
                    "steps": ["جلسات ماهانه", "پیاده‌روی جمعی"]
                }
            ],
            "members": [
                {
                    "name": "Father",
                    "name_fa": "پدر",
                    "role": "father",
                    "age": 65,
                    "conditions": "نیاز به فعالیت روزمره",
                    "avatar": "👴",
                    "is_leader": 0
                },
                {
                    "name": "Me",
                    "name_fa": "راهبر",
                    "role": "user",
                    "age": 25,
                    "conditions": "مدیریت برنامه",
                    "avatar": "🧠",
                    "is_leader": 1
                }
            ],
            "chores": [
                {
                    "title_fa": "شستن ظروف",
                    "title_en": "Dishes",
                    "category": "kitchen",
                    "frequency": "daily",
                    "assigned_to": "راهبر",
                    "icon": "🍽️"
                }
            ],
            "habits": [
                {
                    "target_member": "پدر",
                    "habit": "آبیاری گلدان‌ها",
                    "category": "cognitive",
                    "frequency": "روزانه",
                    "reminder_time": "09:00"
                }
            ],
            "communication_rules": [
                "توقف ۵ دقیقه‌ای در صورت بروز خشم"
            ],
            "emergency_and_free_resources": [
                {
                    "title": "سامانه ۱۴۸۰",
                    "phone": "1480",
                    "description": "مشاوره رایگان بهزیستی"
                }
            ]
        }
        
        # Test API initialization endpoint
        res = self.client.post("/api/setup/initialize-template", json={"template": sample_agent_template})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["members_count"], 2)
        self.assertEqual(data["chores_count"], 1)
        self.assertEqual(data["habits_count"], 1)

        # Check template endpoint
        t_res = self.client.get("/api/setup/template")
        self.assertEqual(t_res.status_code, 200)
        t_data = t_res.json()
        self.assertEqual(t_data["profile"]["family_name"], "خانواده نمونه")
        self.assertEqual(len(t_data["goals"]), 2)

    def test_05_stats_and_reporting(self):
        members = get_all_members()
        if members:
            log_checkin(member_id=members[0]["id"], mood=5, checkin_type="morning")
            log_conflict(reported_by_id=members[0]["id"], involved="اعضا", trigger="خستگی", severity=1)
        
        stats = get_stats_summary(days=7)
        self.assertIn("has_data", stats)
        self.assertIn("avg_mood", stats)
        
        leader_report, family_broadcast, _ = generate_weekly_analysis(days=7)
        self.assertTrue(len(leader_report) > 0)
        self.assertTrue(len(family_broadcast) > 0)

    def test_06_scheduler_webhooks_and_diagnostics(self):
        # Diagnostics
        tg_res = self.client.post("/api/telegram/test-connection")
        self.assertEqual(tg_res.status_code, 200)
        
        ai_res = self.client.post("/api/ai/test-connection")
        self.assertEqual(ai_res.status_code, 200)
        
        # Scheduler webhooks
        m_res = self.client.post("/api/scheduler/trigger-morning")
        self.assertEqual(m_res.status_code, 200)
        
        e_res = self.client.post("/api/scheduler/trigger-evening")
        self.assertEqual(e_res.status_code, 200)
        
        w_res = self.client.post("/api/scheduler/trigger-weekly-review")
        self.assertEqual(w_res.status_code, 200)

        # HTML Dashboard
        html_res = self.client.get("/")
        self.assertEqual(html_res.status_code, 200)
        self.assertIn("خانواده‌یار", html_res.text)

if __name__ == "__main__":
    unittest.main()
