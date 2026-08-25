"""
Telegram Bot Engine for Scalable Family Evolution System
Real-time dispatching, member deep-linking, and connection diagnostics.
"""
import logging
import asyncio
import httpx
from typing import Optional, List, Dict, Any, Tuple
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.request import HTTPXRequest

from core.config import config
from data.database import (
    get_all_members,
    get_member_by_id,
    get_member_by_telegram_id,
    link_telegram_id,
    log_checkin,
    get_today_chores_for_member,
    get_today_chores_all,
    update_chore_status,
    swap_chore_assignee,
    get_member_habits,
    toggle_habit_log,
    log_conflict,
    get_stats_summary
)
from bot.keyboards import (
    get_member_select_keyboard,
    get_mood_keyboard,
    get_chore_actions_keyboard,
    get_caregiver_report_keyboard,
    get_quick_menu_keyboard
)
from bot import dialogues_fa as dlg

logger = logging.getLogger(__name__)

class FamilyBot:
    def __init__(self):
        self.app: Optional[Application] = None
        self.bot_info: Optional[Dict[str, Any]] = None

    def build_application(self) -> Optional[Application]:
        """Build and configure the Telegram application instance"""
        token = config.telegram_bot_token
        if not token:
            logger.warning("No Telegram Bot Token configured.")
            return None

        proxy = config.telegram_proxy if config.use_proxy else None
        request_kwargs = {"connect_timeout": 15.0, "read_timeout": 20.0}
        if proxy:
            request_kwargs["proxy_url"] = proxy

        try:
            request = HTTPXRequest(**request_kwargs)
            builder = Application.builder().token(token).request(request)
            app = builder.build()

            # Commands
            app.add_handler(CommandHandler("start", self.cmd_start))
            app.add_handler(CommandHandler("help", self.cmd_help))
            app.add_handler(CommandHandler("chores", self.cmd_chores))
            app.add_handler(CommandHandler("habits", self.cmd_habits))
            app.add_handler(CommandHandler("calendar", self.cmd_calendar))
            app.add_handler(CommandHandler("status", self.cmd_status))
            app.add_handler(CommandHandler("caregiver", self.cmd_caregiver))
            app.add_handler(CommandHandler("breathing", self.cmd_breathing))

            # Callbacks & Text
            app.add_handler(CallbackQueryHandler(self.handle_callback))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

            self.app = app
            return app
        except Exception as e:
            logger.error(f"Error building telegram application: {e}")
            return None

    def test_connection(self) -> Dict[str, Any]:
        """Directly tests Telegram API connectivity and returns verified bot info"""
        token = config.telegram_bot_token
        if not token:
            return {"ok": False, "error": "توکن ربات تلگرام تنظیم نشده است."}

        proxies_to_try = []
        if config.use_proxy and config.telegram_proxy:
            proxies_to_try.append(config.telegram_proxy)
        proxies_to_try.append(None)  # Also try direct

        last_error = None
        for p in proxies_to_try:
            try:
                with httpx.Client(proxy=p, timeout=6.0) if p else httpx.Client(timeout=6.0) as client:
                    res = client.get(f"https://api.telegram.org/bot{token}/getMe")
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("ok"):
                            self.bot_info = data["result"]
                            return {
                                "ok": True,
                                "bot_id": self.bot_info["id"],
                                "username": self.bot_info.get("username", "Unknown"),
                                "first_name": self.bot_info.get("first_name", "FamilyBot"),
                                "proxy_used": p or "Direct"
                            }
                    last_error = f"HTTP {res.status_code}: {res.text}"
            except Exception as e:
                last_error = str(e)

        return {"ok": False, "error": f"عدم برقراری ارتباط با سرورهای تلگرام ({last_error})"}

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message and auto-bind if deep link parameter exists"""
        user_id = update.effective_user.id
        args = context.args or []

        # Check for deep link parameter e.g. /start member_2
        if args and args[0].startswith("member_"):
            try:
                target_member_id = int(args[0].split("_")[1])
                target_member = get_member_by_id(target_member_id)
                if target_member:
                    link_telegram_id(target_member_id, user_id)
                    await update.message.reply_text(
                        f"✅ حساب شما با موفقیت به **{target_member['name_fa']}** ({target_member['avatar']}) متصل شد!",
                        reply_markup=get_quick_menu_keyboard(),
                        parse_mode="Markdown"
                    )
                    return
            except Exception as e:
                logger.error(f"Deep link binding error: {e}")

        # Check existing binding
        member = get_member_by_telegram_id(user_id)
        if member:
            await update.message.reply_text(
                f"سلام {member['name_fa']} عزیز ({member['avatar']})!\nخوشحالم که دوباره می‌بینمت. چطور می‌تونم کمکت کنم؟",
                reply_markup=get_quick_menu_keyboard(),
                parse_mode="Markdown"
            )
        else:
            members = get_all_members()
            if not members:
                await update.message.reply_text(
                    "🌱 به سامانه خانواده‌یار خوش آمدید!\nهنوز عضوی در داشبورد ثبت نشده است. لطفاً ابتدا در داشبورد اعضای خانواده را تعریف کنید.",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    dlg.GREETING_WELCOME,
                    reply_markup=get_member_select_keyboard(members),
                    parse_mode="Markdown"
                )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "🌿 **راهنمای دستورات سامانه خانواده‌یار:**\n\n"
            "• `/start` - منوی اصلی و اتصال حساب\n"
            "• `/chores` - مشاهده و ثبت وظایف روزمره خانه\n"
            "• `/habits` - پایش عادت‌ها و مراقبت‌های سلامتی\n"
            "• `/calendar` - تقویم کارهای امروز همه اعضا\n"
            "• `/status` - گزارش خلاصه وضعیت خانواده\n"
            "• `/caregiver` - فرم سریع ثبت وضعیت پدر برای مراقبان\n"
            "• `/breathing` - تمرین آرامش و تنفس ۴-۷-۸"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def cmd_chores(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        member = get_member_by_telegram_id(user_id)
        if not member:
            await update.message.reply_text("لطفا ابتدا با زدن /start نام خود را انتخاب کنید.")
            return

        chores = get_today_chores_for_member(member["id"])
        if not chores:
            await update.message.reply_text(f"✨ {member['name_fa']} عزیز، برای امروز کار زمان‌بندی شده‌ای نداری! وقت استراحته.")
            return

        await update.message.reply_text(f"📋 **کارهای امروز شما ({member['name_fa']}):**", parse_mode="Markdown")
        for ch in chores:
            status_text = "✅ انجام شده" if ch["status"] == "done" else "⏳ در انتظار انجام"
            msg = f"{ch['icon']} **{ch['title_fa']}**\nوضعیت: {status_text}"
            await update.message.reply_text(
                msg,
                reply_markup=get_chore_actions_keyboard(ch["schedule_id"], ch["status"]),
                parse_mode="Markdown"
            )

    async def cmd_habits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        member = get_member_by_telegram_id(user_id)
        if not member:
            await update.message.reply_text("لطفا ابتدا با زدن /start نام خود را انتخاب کنید.")
            return

        habits = get_member_habits(member["id"])
        if not habits:
            await update.message.reply_text("عادت ثبت‌شده‌ای برای شما تعریف نشده است.")
            return

        text = f"🌱 **عادت‌ها و مراقبت‌های سلامت ({member['name_fa']}):**\n\n"
        for h in habits:
            st = "✅ ثبت شده" if h["today_status"] == "done" else "⭕ ثبت نشده"
            text += f"• {h['title_fa']} ({h['reminder_time'] or 'روزانه'}): {st}\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")

    async def cmd_calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_chores = get_today_chores_all()
        if not all_chores:
            await update.message.reply_text("امروز هیچ کار زمان‌بندی شده‌ای ثبت نشده است.")
            return

        text = "📅 **تقویم و مسئولیت‌های امروز خانه:**\n\n"
        for ch in all_chores:
            st_icon = "✅" if ch["status"] == "done" else "⏳"
            text += f"{st_icon} {ch['avatar']} **{ch['name_fa']}**: {ch['icon']} {ch['title_fa']}\n"

        await update.message.reply_text(text, parse_mode="Markdown")

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        stats = get_stats_summary(days=7)
        if not stats.get("has_data"):
            await update.message.reply_text("هنوز داده‌ای در ۷ روز گذشته ثبت نشده است. با ثبت وظایف یا احوالپرسی روزانه داده‌ها فعال می‌شوند.")
            return

        avg_str = f"{stats['avg_mood']} از ۵ 😊" if stats['avg_mood'] else "ثبت نشده"
        rate_str = f"{stats['chore_completion_rate']}٪" if stats['chore_completion_rate'] is not None else "ثبت نشده"
        text = (
            "📊 **گزارش خلاصه وضعیت ۷ روز گذشته:**\n\n"
            f"• میانگین حس و حال عمومی: {avg_str}\n"
            f"• درصد انجام وظایف خانه: {rate_str} ({stats['done_chores']}/{stats['total_chores']} کار) ✅\n"
            f"• تعداد تعارض‌های گزارش‌شده: {stats['conflict_count']} مورد 🕊️\n\n"
            "برای مشاهده تحلیل تفصیلی به داشبورد وب مراجعه کنید."
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    async def cmd_caregiver(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📋 **ثبت وضعیت و مراقبت‌های پدر:**\nگزینه مورد نظر را ثبت کنید:",
            reply_markup=get_caregiver_report_keyboard()
        )

    async def cmd_breathing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(dlg.ANGER_SUPPORT_MOTHER, parse_mode="Markdown")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button clicks"""
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = update.effective_user.id

        if data.startswith("bind_member:"):
            member_id = int(data.split(":")[1])
            link_telegram_id(member_id, user_id)
            member = get_member_by_id(member_id)
            await query.edit_message_text(
                f"✅ حساب شما با موفقیت به **{member['name_fa']}** ({member['avatar']}) متصل شد!",
                reply_markup=get_quick_menu_keyboard(),
                parse_mode="Markdown"
            )
            return

        if data.startswith("mood:"):
            parts = data.split(":")
            member = get_member_by_telegram_id(user_id)
            member_id = member["id"] if member else 1

            if parts[1] == "anger":
                log_checkin(member_id=member_id, mood=1, anger=1, notes="اعلام تنش عاطفی")
                await query.edit_message_text(
                    "مامان جان، احساس شما کاملاً شنیده شد ❤️\nبیایید چند ثانیه با هم تنفس آرامش‌بخش انجام دهیم:\n\n" + dlg.ANGER_SUPPORT_MOTHER,
                    parse_mode="Markdown"
                )
            else:
                mood_score = int(parts[1])
                log_checkin(member_id=member_id, mood=mood_score, checkin_type="daily")
                emoji_feedback = "عالیه! انرژیت پایدار 🌟" if mood_score >= 4 else "ممنون که گفتی. در کنارت هستیم 🌿"
                await query.edit_message_text(
                    f"حس و حال شما ({mood_score} از ۵) ثبت شد. {emoji_feedback}",
                    reply_markup=get_quick_menu_keyboard()
                )
            return

        if data == "action:breathing":
            await query.edit_message_text(dlg.ANGER_SUPPORT_MOTHER, parse_mode="Markdown")
            return

        if data.startswith("chore_toggle:"):
            schedule_id = int(data.split(":")[1])
            update_chore_status(schedule_id, "done")
            await query.edit_message_text(
                "✅ کار با موفقیت به عنوان «انجام شده» ثبت شد. خسته نباشی!",
                reply_markup=get_quick_menu_keyboard()
            )
            return

        if data.startswith("chore_swap:"):
            schedule_id = int(data.split(":")[1])
            all_members = get_all_members()
            next_assignee = next((m for m in all_members if m["role"] in ["sister", "brother", "user"]), all_members[0]) if all_members else None
            if next_assignee:
                swap_chore_assignee(schedule_id, next_assignee["id"])
                await query.edit_message_text(
                    f"🔄 کار با موفقیت به {next_assignee['name_fa']} محول شد.",
                    reply_markup=get_quick_menu_keyboard()
                )
            return

        if data.startswith("care:"):
            action = data.split(":")[1]
            member = get_member_by_telegram_id(user_id)
            reporter_id = member["id"] if member else 1
            log_checkin(member_id=reporter_id, mood=4, checkin_type="caregiver_report", notes=f"ثبت مراقبتی: {action}")
            await query.edit_message_text(
                "✅ گزارش وضعیت پدر با موفقیت ثبت شد. متشکریم از مهر و توجه شما! 🌿",
                reply_markup=get_quick_menu_keyboard()
            )
            return

        if data == "menu:my_chores":
            member = get_member_by_telegram_id(user_id)
            if member:
                chores = get_today_chores_for_member(member["id"])
                if chores:
                    txt = f"📋 کارهای امروز شما ({len(chores)} مورد):\n"
                    for c in chores:
                        st = "✅" if c['status'] == 'done' else "⏳"
                        txt += f"{st} {c['icon']} {c['title_fa']}\n"
                    await query.edit_message_text(txt, reply_markup=get_quick_menu_keyboard())
                else:
                    await query.edit_message_text("امروز کار معوقه‌ای نداری! 🌿", reply_markup=get_quick_menu_keyboard())
            return

        if data == "menu:family_calendar":
            all_chores = get_today_chores_all()
            if all_chores:
                txt = "📅 کارهای امروز خانه:\n" + "\n".join([f"{c['avatar']} {c['name_fa']}: {c['icon']} {c['title_fa']} ({'✅' if c['status']=='done' else '⏳'})" for c in all_chores])
            else:
                txt = "امروز وظیفه‌ای در تقویم ثبت نشده است."
            await query.edit_message_text(txt, reply_markup=get_quick_menu_keyboard())
            return

        if data == "menu:status_report":
            stats = get_stats_summary(days=7)
            avg_val = f"{stats['avg_mood']}/5" if stats['avg_mood'] else "داده‌ای نیست"
            rate_val = f"{stats['chore_completion_rate']}٪" if stats['chore_completion_rate'] is not None else "داده‌ای نیست"
            txt = f"📊 حال عمومی: {avg_val} | پیشرفت کارها: {rate_val}"
            await query.edit_message_text(txt, reply_markup=get_quick_menu_keyboard())
            return

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle open-ended text input from members"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        member = get_member_by_telegram_id(user_id)
        member_id = member["id"] if member else 1
        name = member["name_fa"] if member else "همراه عزیز"

        log_checkin(member_id=member_id, mood=4, win=text, notes=text, checkin_type="daily_text")
        reply = f"✨ سپاسگزارم {name} عزیز، پیام و حس شما در سیستم ثبت شد:\n«{text}»\nانرژی مثبت شما در خانه جاریست 🌿"
        await update.message.reply_text(reply, reply_markup=get_quick_menu_keyboard())

    # --- Real Dispatch Functions with Detailed Status ---

    async def dispatch_morning_checkins(self) -> Dict[str, Any]:
        """Broadcast morning check-in to all registered members with real delivery reporting"""
        if not self.app:
            return {"sent_count": 0, "failed_count": 0, "unlinked": [], "error": "Bot is not running."}

        members = get_all_members()
        sent_to = []
        failed = []
        unlinked = []

        for m in members:
            tid = m["telegram_id"]
            if not tid:
                unlinked.append(m["name_fa"])
                continue

            try:
                role = m["role"]
                if role == "father":
                    msg = dlg.MORNING_FATHER
                elif role == "mother":
                    msg = dlg.MORNING_MOTHER
                else:
                    msg = dlg.MORNING_MEMBER.format(name=m["name_fa"])

                await self.app.bot.send_message(
                    chat_id=tid,
                    text=msg,
                    reply_markup=get_mood_keyboard(role),
                    parse_mode="Markdown"
                )
                sent_to.append(m["name_fa"])
            except Exception as e:
                logger.error(f"Failed to send morning checkin to {m['name_fa']} ({tid}): {e}")
                failed.append({"name": m["name_fa"], "error": str(e)})

        return {
            "sent_count": len(sent_to),
            "sent_to": sent_to,
            "failed_count": len(failed),
            "failed": failed,
            "unlinked_members": unlinked
        }

    async def dispatch_evening_checkins(self) -> Dict[str, Any]:
        """Broadcast evening check-in and chore completion to registered members"""
        if not self.app:
            return {"sent_count": 0, "failed_count": 0, "unlinked": [], "error": "Bot is not running."}

        members = get_all_members()
        sent_to = []
        failed = []
        unlinked = []

        for m in members:
            tid = m["telegram_id"]
            if not tid:
                unlinked.append(m["name_fa"])
                continue

            try:
                chores = get_today_chores_for_member(m["id"])
                chore_summary = "\n".join([f"• {c['icon']} {c['title_fa']} ({'✅' if c['status']=='done' else '⏳'})" for c in chores]) if chores else "هیچ کار زمان‌بندی شده‌ای نداری."
                msg = dlg.EVENING_CHECKIN.format(name=m["name_fa"], chores_list=chore_summary)

                await self.app.bot.send_message(
                    chat_id=tid,
                    text=msg,
                    parse_mode="Markdown"
                )
                sent_to.append(m["name_fa"])
            except Exception as e:
                logger.error(f"Failed to send evening checkin to {m['name_fa']} ({tid}): {e}")
                failed.append({"name": m["name_fa"], "error": str(e)})

        return {
            "sent_count": len(sent_to),
            "sent_to": sent_to,
            "failed_count": len(failed),
            "failed": failed,
            "unlinked_members": unlinked
        }

    async def dispatch_custom_broadcast(self, message_text: str) -> Dict[str, Any]:
        """Send custom broadcast to all registered family members"""
        if not self.app:
            return {"sent_count": 0, "failed_count": 0, "unlinked": [], "error": "Bot is not running."}

        members = get_all_members()
        sent_to = []
        failed = []
        unlinked = []

        for m in members:
            tid = m["telegram_id"]
            if not tid:
                unlinked.append(m["name_fa"])
                continue

            try:
                await self.app.bot.send_message(chat_id=tid, text=message_text, parse_mode="Markdown")
                sent_to.append(m["name_fa"])
            except Exception as e:
                logger.error(f"Failed to broadcast to {m['name_fa']} ({tid}): {e}")
                failed.append({"name": m["name_fa"], "error": str(e)})

        return {
            "sent_count": len(sent_to),
            "sent_to": sent_to,
            "failed_count": len(failed),
            "failed": failed,
            "unlinked_members": unlinked
        }

telegram_bot = FamilyBot()
