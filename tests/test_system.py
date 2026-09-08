"""
Comprehensive Unit and Integration Tests for Scalable Family Evolution System v2.6
Covers Informed Consent, Clinical Evaluations, Confidential Dynamics, and Adaptive Interventions.
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
    record_member_consent,
    log_family_evaluation,
    log_interpersonal_dynamics,
    get_systemic_health_trend,
    record_intervention_adaptation,
    get_intervention_history,
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
    get_stats_summary,
    get_weekly_matrix,
    rotate_chores_now
)
from brain.ai_engine import ai_engine
from brain.reporter import generate_weekly_analysis
from mcp_server import TOOLS, handle_tool_call
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

    def test_01_member_crud_and_consent(self):
        mid = create_member(
            name="Sara",
            name_fa="سارا",
            role="sister",
            age=28,
            conditions="معلم زبان",
            medical_history="سابقه سردردهای میگرنی",
            avatar="👩"
        )
        self.assertGreater(mid, 0)
        
        # Check initial consent is 0
        members = get_all_members()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["consent_given"], 0)
        self.assertEqual(members[0]["medical_history"], "سابقه سردردهای میگرنی")
        
        # Record consent
        c_ok = record_member_consent(mid, True)
        self.assertTrue(c_ok)
        
        members_after = get_all_members()
        self.assertEqual(members_after[0]["consent_given"], 1)
        self.assertIsNotNone(members_after[0]["consent_date"])
        
        # Update
        updated = update_member(
            member_id=mid,
            name="Sara Updated",
            name_fa="سارا رضایی",
            role="sister",
            age=29,
            conditions="معلم زبان و همیار",
            medical_history="تحت درمان دارویی"
        )
        self.assertTrue(updated)
        
        deleted = delete_member(mid)
        self.assertTrue(deleted)
        self.assertEqual(len(get_all_members()), 0)

    def test_02_clinical_evaluations_and_confidential_dynamics(self):
        m1 = create_member(name="Mother", name_fa="مادر", role="mother", age=60)
        m2 = create_member(name="Son", name_fa="پسر", role="brother", age=25)
        
        # Log confidential interpersonal dynamics
        dyn_id = log_interpersonal_dynamics(
            source_member_id=m1,
            target_member_id=m2,
            hurt_points="عدم مشارکت در نظافت آشپزخانه",
            appreciate_points="مهربانی و شوخ‌طبعی",
            relationship_valence=3
        )
        self.assertGreater(dyn_id, 0)
        
        # Log baseline & monthly evaluation
        eval_id = log_family_evaluation(
            member_id=m1,
            evaluation_type="baseline",
            psychological_safety=4,
            respect_status=3,
            perceived_care=4,
            overall_climate=3,
            narrative_text="احساس می‌کنم کارهای خانه زیاده اما امیدوارم به بهبود"
        )
        self.assertGreater(eval_id, 0)
        
        # Check trend aggregation
        trends = get_systemic_health_trend()
        self.assertGreater(len(trends["trends"]), 0)
        self.assertEqual(trends["trends"][0]["avg_safety"], 4.0)
        
        # Record intervention adaptation
        aid = record_intervention_adaptation(
            trigger_reason="افت نمره احترام مادر",
            changes_made={"chores_adjustment": "انتقال ظروف به پسر"},
            rationale="کاهش فرسودگی عاطفی مادر"
        )
        self.assertGreater(aid, 0)
        
        history = get_intervention_history()
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]["trigger_reason"], "افت نمره احترام مادر")
        
        delete_member(m1)
        delete_member(m2)

    def test_03_agent_template_initialization(self):
        sample_template = {
            "family_profile": {
                "family_name": "خانواده امید",
                "overview": "طرح تحول ساختاری و ارتقای امنیت روانی."
            },
            "short_term_goals": [
                {
                    "title": "نظم کارهای خانه",
                    "description": "چرخش نوبت شستشوی ظروف",
                    "target_date": "۲ هفته آینده",
                    "steps": ["تعیین نوبت", "ثبت تیک"]
                }
            ],
            "long_term_goals": [
                {
                    "title": "آرامش پایدار و احترام متقابل",
                    "description": "کاهش فرسودگی عاطفی",
                    "target_date": "۶ ماه آینده",
                    "steps": ["جلسات ماهانه", "پیاده‌روی"]
                }
            ],
            "members": [
                {
                    "name": "Father",
                    "name_fa": "پدر",
                    "role": "father",
                    "age": 65,
                    "conditions": "دمانس خفیف",
                    "medical_history": "داروی حافظه",
                    "avatar": "👴"
                }
            ],
            "chores": [
                {
                    "title_fa": "آبیاری گل‌ها",
                    "title_en": "Plants",
                    "category": "plants_pets",
                    "frequency": "daily",
                    "assigned_to": "پدر",
                    "icon": "🌱"
                }
            ],
            "habits": [
                {
                    "target_member": "پدر",
                    "habit": "مرور خاطرات",
                    "category": "cognitive",
                    "frequency": "روزانه",
                    "reminder_time": "09:00"
                }
            ],
            "communication_rules": ["توقف ۵ دقیقه‌ای در خشم"],
            "emergency_and_free_resources": [{"title": "۱۴۸۰", "phone": "1480", "description": "بهزیستی"}]
        }
        
        res = self.client.post("/api/setup/initialize-template", json={"template": sample_template})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_04_api_evaluation_and_intervention_endpoints(self):
        # Evaluation trends endpoint
        t_res = self.client.get("/api/evaluations/trends")
        self.assertEqual(t_res.status_code, 200)
        
        # Interventions history endpoint
        i_res = self.client.get("/api/interventions/history")
        self.assertEqual(i_res.status_code, 200)
        
        # Monthly evaluation trigger webhook
        m_res = self.client.post("/api/scheduler/trigger-monthly-evaluations")
        self.assertEqual(m_res.status_code, 200)

        # Weekly analysis
        leader_report, family_broadcast, stats = generate_weekly_analysis(days=7)
        self.assertTrue(len(leader_report) > 0)
        self.assertTrue(len(family_broadcast) > 0)

    def test_05_weekly_calendar_and_recipients(self):
        # Weekly matrix API
        res = self.client.get("/api/calendar/weekly?week_offset=0")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("days", data)
        self.assertEqual(len(data["days"]), 7)
        self.assertIn("chores", data["days"][3])

        # Direct database function
        matrix = get_weekly_matrix(week_offset=0)
        self.assertIn("days", matrix)
        self.assertEqual(len(matrix["days"]), 7)
        self.assertEqual(matrix["days"][0]["day_name_fa"], "شنبه")
        self.assertEqual(matrix["days"][6]["day_name_fa"], "جمعه")

        # Recipients endpoint
        recipients_res = self.client.get("/api/members/recipients")
        self.assertEqual(recipients_res.status_code, 200)
        recipients_data = recipients_res.json()
        self.assertIsInstance(recipients_data, list)
        self.assertGreater(len(recipients_data), 0)

    def test_06_database_backup_flow(self):
        # Trigger backup endpoint (returns 400 when bot offline in test mode, or 200 when online)
        backup_res = self.client.post("/api/admin/send-backup-telegram")
        self.assertIn(backup_res.status_code, [200, 400])
        if backup_res.status_code == 200:
            self.assertEqual(backup_res.json()["status"], "ok")
        else:
            self.assertIn("detail", backup_res.json())

    def test_07_intelligent_chore_rotation_algorithm(self):
        m1 = create_member(name="Sister", name_fa="خواهر", role="sister", age=28)
        m2 = create_member(name="Brother", name_fa="برادر", role="brother", age=22)
        
        # Create rotational chore
        cid = create_chore(
            title_fa="شستن ظروف چرخشی",
            title_en="Rotating dishwashing",
            category="kitchen",
            frequency="daily",
            default_assignee_id=m1,
            is_rotational=True,
            rotation_pool=[m1, m2]
        )
        self.assertGreater(cid, 0)

        # Trigger rotation
        rot_res = rotate_chores_now(days_ahead=7)
        self.assertEqual(rot_res["status"], "ok")

        # API rotation trigger
        api_rot = self.client.post("/api/chores/rotate")
        self.assertEqual(api_rot.status_code, 200)

        delete_member(m1)
        delete_member(m2)
        delete_chore(cid)

    def test_08_mcp_server_protocol_and_tools(self):
        import asyncio
        # Verify MCP tool definitions
        self.assertGreaterEqual(len(TOOLS), 7)
        tool_names = [t["name"] for t in TOOLS]
        self.assertIn("get_family_status", tool_names)
        self.assertIn("get_weekly_chore_matrix", tool_names)
        self.assertIn("rotate_chores_schedule", tool_names)
        self.assertIn("generate_weekly_ai_report", tool_names)
        self.assertIn("backup_database_to_telegram", tool_names)

        # Call get_family_status tool via handler
        status_res = asyncio.run(handle_tool_call("get_family_status", {"days": 7}))
        self.assertIn("content", status_res)
        self.assertEqual(status_res["content"][0]["type"], "text")
        parsed = json.loads(status_res["content"][0]["text"])
        self.assertIn("members_count", parsed)

        # Call get_weekly_chore_matrix tool via handler
        matrix_res = asyncio.run(handle_tool_call("get_weekly_chore_matrix", {"week_offset": 0}))
        self.assertIn("content", matrix_res)
        parsed_matrix = json.loads(matrix_res["content"][0]["text"])
        self.assertIn("days", parsed_matrix)
        self.assertEqual(len(parsed_matrix["days"]), 7)

if __name__ == "__main__":
    unittest.main()
