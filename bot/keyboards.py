"""
Telegram Inline Keyboards for Family Evolution Bot
Includes Consent Charters, Clinical Likert Rating Keyboards, and Task Actions.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any

def get_consent_keyboard(member_id: int) -> InlineKeyboardMarkup:
    """Informed Consent & Privacy acceptance buttons"""
    buttons = [
        [
            InlineKeyboardButton("✅ بله، با رضایت و آگاهی کامل شرکت می‌کنم", callback_data=f"consent:agree:{member_id}")
        ],
        [
            InlineKeyboardButton("❌ خیر، مایل به همراهی نیستم", callback_data=f"consent:decline:{member_id}")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_likert_keyboard(metric: str) -> InlineKeyboardMarkup:
    """1 to 5 Likert Scale for Psychological Evaluations"""
    buttons = [
        [
            InlineKeyboardButton("۵ - بسیار زیاد / عالی 🌟", callback_data=f"eval:{metric}:5"),
            InlineKeyboardButton("۴ - خوب و مطلوب ✨", callback_data=f"eval:{metric}:4")
        ],
        [
            InlineKeyboardButton("۳ - متوسط و قابل قبول 😐", callback_data=f"eval:{metric}:3")
        ],
        [
            InlineKeyboardButton("۲ - ضعیف / کم 😕", callback_data=f"eval:{metric}:2"),
            InlineKeyboardButton("۱ - بسیار کم / ناامن 😔", callback_data=f"eval:{metric}:1")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_member_select_keyboard(members: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Keyboard to bind Telegram account to a family member"""
    keyboard = []
    for m in members:
        btn_text = f"{m['avatar']} {m['name_fa']} ({m['role']})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"bind_member:{m['id']}")])
    return InlineKeyboardMarkup(keyboard)

def get_mood_keyboard(member_role: str = "member") -> InlineKeyboardMarkup:
    """Liquid-touch simple mood buttons (1-5 mapped to emojis)"""
    if member_role == "father":
        buttons = [
            [
                InlineKeyboardButton("😊 عالی و خوشحالم", callback_data="mood:5:father"),
                InlineKeyboardButton("😐 معمولیم", callback_data="mood:3:father"),
                InlineKeyboardButton("😔 خسته‌ام", callback_data="mood:1:father")
            ]
        ]
    elif member_role == "mother":
        buttons = [
            [
                InlineKeyboardButton("😊 خوب و راضی‌ام (۵)", callback_data="mood:5:mother"),
                InlineKeyboardButton("🙂 متوسط (۳)", callback_data="mood:3:mother"),
                InlineKeyboardButton("😔 ناراحتم (۱)", callback_data="mood:1:mother")
            ],
            [
                InlineKeyboardButton("🌬️ تمرین تنفس و آرامش", callback_data="action:breathing"),
                InlineKeyboardButton("⚡ احساس خستگی و تنش", callback_data="mood:anger:mother")
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton("🤩 عالی (۵)", callback_data="mood:5"),
                InlineKeyboardButton("😊 خوب (۴)", callback_data="mood:4"),
                InlineKeyboardButton("😐 متوسط (۳)", callback_data="mood:3")
            ],
            [
                InlineKeyboardButton("😕 بی‌حوصله (۲)", callback_data="mood:2"),
                InlineKeyboardButton("😔 تحت فشار (۱)", callback_data="mood:1")
            ]
        ]
    return InlineKeyboardMarkup(buttons)

def get_chore_actions_keyboard(schedule_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Buttons for updating a chore status or requesting swap"""
    status_icon = "✅ انجام شد" if current_status == "done" else "⏳ ثبت انجام"
    buttons = [
        [
            InlineKeyboardButton(status_icon, callback_data=f"chore_toggle:{schedule_id}"),
            InlineKeyboardButton("🔄 درخواست تعویض نوبت", callback_data=f"chore_swap:{schedule_id}")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_quick_menu_keyboard() -> InlineKeyboardMarkup:
    """Main action menu"""
    buttons = [
        [
            InlineKeyboardButton("📋 کارهای امروز من", callback_data="menu:my_chores"),
            InlineKeyboardButton("🌱 عادت‌ها و سلامت", callback_data="menu:my_habits")
        ],
        [
            InlineKeyboardButton("📊 ارزیابی جامع خانواده", callback_data="menu:start_eval"),
            InlineKeyboardButton("📅 تقویم کلی خانه", callback_data="menu:family_calendar")
        ]
    ]
    return InlineKeyboardMarkup(buttons)
