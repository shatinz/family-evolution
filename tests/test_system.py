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

if __name__ == "__main__":
    unittest.main()
