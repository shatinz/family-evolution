"""
Telegram Inline Keyboards for Family Evolution Bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any

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
        # Ultra simple 3-button keyboard for dementia
        buttons = [
            [
                InlineKeyboardButton("😊 عالی و خوشحالم", callback_data="mood:5:father"),
                InlineKeyboardButton("😐 معمولیم", callback_data="mood:3:father"),
                InlineKeyboardButton("😔 خسته‌ام", callback_data="mood:1:father")
            ]
        ]
    elif member_role == "mother":
        # Includes anger/stress relief trigger
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

def get_caregiver_report_keyboard() -> InlineKeyboardMarkup:
    """Quick report on Father's condition from whoever is with him"""
    buttons = [
        [
            InlineKeyboardButton("💊 داروها مصرف شد", callback_data="care:meds_done"),
            InlineKeyboardButton("🐦 به پرنده غذا داد", callback_data="care:bird_done")
        ],
        [
            InlineKeyboardButton("🌱 گل‌ها آبیاری شد", callback_data="care:plants_done"),
            InlineKeyboardButton("🚶‍♂️ پیاده‌روی رفتند", callback_data="care:walk_done")
        ],
        [
            InlineKeyboardButton("✨ حال عمومی عالی بود", callback_data="care:good_mood"),
            InlineKeyboardButton("⚠️ نیاز به توجه و استراحت", callback_data="care:needs_rest")
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
            InlineKeyboardButton("📅 تقویم کلی خانه", callback_data="menu:family_calendar"),
            InlineKeyboardButton("📊 وضعیت هفتگی", callback_data="menu:status_report")
        ]
    ]
    return InlineKeyboardMarkup(buttons)
