"""
Reporter, Longitudinal Clinical Evaluation, and Intervention Adaptation Engine
Evaluates psychological safety, respect, perceived care, and automatically adapts family interventions.
"""
import json
from typing import Dict, Any, Tuple
from brain.ai_engine import ai_engine
from data.database import (
    get_stats_summary,
    save_ai_report,
    get_db_connection,
    get_systemic_health_trend,
    record_intervention_adaptation
)

def generate_weekly_analysis(days: int = 7) -> Tuple[str, str, Dict[str, Any]]:
    """
    Analyzes historical database records, longitudinal evaluations, and chore metrics:
    - Detailed Leader Clinical & Operational Report
    - Family Encouragement Broadcast
    - Closed-loop Intervention Adaptation Recommendations
    """
    stats = get_stats_summary(days=days)
    systemic_trends = get_systemic_health_trend()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT m.name_fa, m.role, c.date, c.mood, c.anger_reported, c.win_of_the_day, c.notes
           FROM checkins c
           JOIN members m ON c.member_id = m.id
           ORDER BY c.id DESC LIMIT 20"""
    )
    recent_checkins = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute(
        """SELECT date, trigger_reason, severity, resolution_notes FROM conflicts ORDER BY id DESC LIMIT 5"""
    )
    recent_conflicts = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute(
        """SELECT date, trigger_reason, changes_made_json, rationale FROM intervention_adaptations ORDER BY id DESC LIMIT 3"""
    )
    recent_interventions = [dict(r) for r in cursor.fetchall()]
    
    conn.close()

    context_payload = {
        "metrics": stats,
        "systemic_psychological_trends": systemic_trends,
        "recent_checkins": recent_checkins,
        "recent_conflicts": recent_conflicts,
        "recent_interventions": recent_interventions
    }
    
    prompt = f"""
شما مشاور و تحلیل‌گر ارشد سیستم‌های رفتاری و سلامت روان خانواده هستید.
بر اساس داده‌های واقعی زیر از شاخص‌های روزانه و ارزیابی‌های روانشناختی (امنیت روانی، احترام، مراقبت ادراک‌شده و کارهای منزل)، گزارش تحلیلی هفتگی و تنظیم مداخله‌ها را تدوین کنید:

داده‌های ورودی:
{json.dumps(context_payload, ensure_ascii=False, indent=2)}

دستورالعمل تولید خروجی:
۱. گزارش اول (راهبر): تحلیل دقیق شاخص‌های امنیت روانی، احترام، خستگی، نرخ انجام وظایف، میزان اثربخشی مداخله‌های فعلی و توصیه‌های تعدیل مداخله برای هفته آینده.
۲. گزارش دوم (پیام همگانی خانواده): متن دلگرم‌کننده، کوتاه و مثبت برای پخش در تلگرام.
۳. بخش تغییرات مداخله (Intervention Tuning): در صورت افت هر شاخص، تغییرات پیشنهادی در عادات، تقسیم کار یا قواعد ارتباطی را مشخص کنید.

لطفاً خروجی را با جداکننده‌های استاندارد زیر ارسال فرمایید:
===LEADER_REPORT===
(متن کامل گزارش تحلیلی راهبر به فارسی با ساختار مارک‌داون)
===FAMILY_BROADCAST===
(متن کوتاه و تشویقی برای اعضای خانواده)
===ADAPTATION_JSON===
{{
  "trigger_reason": "دلیل نیاز به تغییر مداخله یا ثبات روند",
  "recommended_changes": {{
    "chores_adjustment": "تغییرات پیشنهادی در نوبت‌ها",
    "habits_adjustment": "تغییرات پیشنهادی در روتین‌های آرامش/شناختی",
    "communication_rule": "قاعده ارتباطی جدید در صورت نیاز"
  }},
  "rationale": "تبیین روانشناختی چرایی این تغییر"
}}
"""

    messages = [
        {"role": "system", "content": "شما دستیار هوشمند، روانشناس بالینی و معمار سیستم‌های خانواده هستید."},
        {"role": "user", "content": prompt}
    ]

    response_text = ai_engine.chat_completion(messages, temperature=0.6, max_tokens=2500)

    leader_report = ""
    family_broadcast = ""
    adaptation_data = {}

    try:
        if "===LEADER_REPORT===" in response_text and "===FAMILY_BROADCAST===" in response_text:
            parts = response_text.split("===FAMILY_BROADCAST===")
            leader_report = parts[0].replace("===LEADER_REPORT===", "").strip()
            
            subparts = parts[1].split("===ADAPTATION_JSON===")
            family_broadcast = subparts[0].strip()
            
            if len(subparts) > 1:
                clean_json_str = subparts[1].strip().replace("```json", "").replace("```", "").strip()
                adaptation_data = json.loads(clean_json_str)
        else:
            leader_report = response_text
            family_broadcast = "خانواده عزیز، با همدلی و انجام وظایف گام‌های ارزشمندی برای آرامش خانه برداشته‌ایم. خسته نباشید! 🌿✨"
    except Exception:
        leader_report = response_text
        family_broadcast = "خانواده عزیز، با همدلی و انجام وظایف گام‌های ارزشمندی برای آرامش خانه برداشته‌ایم. خسته نباشید! 🌿✨"

    # Record automated adaptation if generated
    if adaptation_data:
        record_intervention_adaptation(
            trigger_reason=adaptation_data.get("trigger_reason", "تحلیل هفتگی شاخص‌ها"),
            changes_made=adaptation_data.get("recommended_changes", {}),
            rationale=adaptation_data.get("rationale", "تعدیل پویای روتین‌ها")
        )

    recommendations = [
        "پایش مستمر شاخص‌های امنیت روانی و مراقبت ادراک‌شده در ارزیابی‌های ماهانه",
        "تعدیل بار کارهای خانه در صورت افت نمرات رفاه",
        "جلسات هفتگی ۲۰ دقیقه‌ای قدردانی متقابل"
    ]
    
    save_ai_report(
        report_type="weekly",
        summary_fa=leader_report,
        summary_en="Weekly family analysis and progress evaluation",
        recommendations=recommendations,
        metrics=stats
    )

    return leader_report, family_broadcast, stats
