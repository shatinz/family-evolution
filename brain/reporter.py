"""
Reporter and Diagnostic Engine
Produces deep analytical reports for the project leader and simplified encouragement summaries for the family.
"""
import json
from typing import Dict, Any, Tuple
from brain.ai_engine import ai_engine
from data.database import get_stats_summary, save_ai_report, get_db_connection

def generate_weekly_analysis(days: int = 7) -> Tuple[str, str, Dict[str, Any]]:
    """
    Analyzes historical database records over the past `days` and produces:
    - Detailed Leader Psychological & Operational Report
    - Simplified Family Encouragement Summary
    """
    stats = get_stats_summary(days=days)
    
    # Fetch recent checkins and notes
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
    conn.close()

    context_payload = {
        "metrics": stats,
        "recent_checkins": recent_checkins,
        "recent_conflicts": recent_conflicts
    }
    
    prompt = f"""
شما مشاور و راهنمای روانشناسی خانواده و سیستم‌ساز هستید.
بر اساس داده‌های واقعی زیر از عملکرد و وضعیت هفتگی این خانواده، دو گزارش تهیه کنید:

داده‌های ورودی:
{json.dumps(context_payload, ensure_ascii=False, indent=2)}

دستورالعمل تولید خروجی:
۱. گزارش اول: ویژه راهبر سیستم (دانشجوی روانشناسی). بسیار تحلیلی، دقیق، اشاره به روند خلق‌وخو، وضعیت دمانس پدر، سطح فرسودگی مادر، نرخ مشارکت خواهر و برادر در کارهای خانه، و ۳ توصیه اجرایی مشخص برای هفته آینده.
۲. گزارش دوم: ویژه پخش عمومی در گروه خانواده (متن کوتاه، صمیمی، امیدبخش و تشویقی با اموجی‌های زیبا).

لطفاً خروجی را دقیقاً با این جداکننده ارسال کنید:
===LEADER_REPORT===
(متن کامل گزارش راهبر به فارسی با مارک‌داون تمیز)
===FAMILY_BROADCAST===
(متن کوتاه و دلگرم‌کننده عمومی خانواده)
"""

    messages = [
        {"role": "system", "content": "شما دستیار هوشمند و روانشناس اختصاصی تحول خانواده هستید."},
        {"role": "user", "content": prompt}
    ]

    response_text = ai_engine.chat_completion(messages, temperature=0.6, max_tokens=2000)

    leader_report = ""
    family_broadcast = ""

    if "===LEADER_REPORT===" in response_text and "===FAMILY_BROADCAST===" in response_text:
        parts = response_text.split("===FAMILY_BROADCAST===")
        leader_report = parts[0].replace("===LEADER_REPORT===", "").strip()
        family_broadcast = parts[1].strip()
    else:
        leader_report = response_text
        family_broadcast = "خانواده عزیز، هفته گذشته گام‌های خوبی برای نظم و آرامش خانه برداشتیم. ممنون از تلاش همه اعضا! 🌿✨"

    # Save to database
    recommendations = [
        "استمرار وظایف سبک و زنده برای پدر (پرنده و گیاهان) جهت مهار پیشرفت دمانس",
        "توزیع عادلانه نوبت شستن ظروف بین زهرا و رضا برای کاهش بار مادر",
        "برگزاری جلسه ۲۰ دقیقه‌ای یکشنبه با محوریت قدردانی متقابل"
    ]
    save_ai_report(
        report_type="weekly",
        summary_fa=leader_report,
        summary_en="Weekly family analysis and progress evaluation",
        recommendations=recommendations,
        metrics=stats
    )

    return leader_report, family_broadcast, stats
