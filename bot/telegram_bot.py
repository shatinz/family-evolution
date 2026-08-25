"""
Telegram Bot Engine for Scalable Family Evolution System
Real-time dispatching, member deep-linking, informed consent, and confidential clinical evaluations.
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
    record_member_consent,
    update_member,
    log_checkin,
    log_family_evaluation,
    log_interpersonal_dynamics,
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
    get_consent_keyboard,
    get_likert_keyboard,
    get_member_select_keyboard,
    get_mood_keyboard,
    get_chore_actions_keyboard,
    get_quick_menu_keyboard
)
from bot import dialogues_fa as dlg

logger = logging.getLogger(__name__)

class FamilyBot:
    def __init__(self):
        self.app: Optional[Application] = None
        self.bot_info: Optional[Dict[str, Any]] = None
        self.user_states: Dict[int, Dict[str, Any]] = {}

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
            app.add_handler(CommandHandler("evaluation", self.cmd_evaluation))
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
        proxies_to_try.append(None)

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
                                "username": self.bot_info.get("username", ""),
                                "first_name": self.bot_info.get("first_name", "FamilyBot"),
                                "proxy_used": p or "Direct"
                            }
                    last_error = f"HTTP {res.status_code}: {res.text}"
            except Exception as e:
                last_error = str(e)

        return {"ok": False, "error": f"عدم برقراری ارتباط با سرورهای تلگرام ({last_error})"}

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message, deep link handler, and informed consent trigger"""
        user_id = update.effective_user.id
        args = context.args or []

        # 1. Deep Link Parameter: /start member_X
        if args and args[0].startswith("member_"):
            try:
                target_member_id = int(args[0].split("_")[1])
                target_member = get_member_by_id(target_member_id)
                if target_member:
                    link_telegram_id(target_member_id, user_id)
                    # Check if consent is already given
                    if not target_member.get("consent_given"):
                        await update.message.reply_text(
                            dlg.CONSENT_AND_PRIVACY_CHARTER,
                            reply_markup=get_consent_keyboard(target_member_id),
                            parse_mode="Markdown"
                        )
                    else:
                        await update.message.reply_text(
                            f"سلام {target_member['name_fa']} عزیز ({target_member['avatar']})!\nخوشحالم که دوباره در کنارت هستیم.",
                            reply_markup=get_quick_menu_keyboard(),
                            parse_mode="Markdown"
                        )
                    return
            except Exception as e:
                logger.error(f"Deep link binding error: {e}")

        # 2. Existing Member Check
        member = get_member_by_telegram_id(user_id)
        if member:
            if not member.get("consent_given"):
                await update.message.reply_text(
                    dlg.CONSENT_AND_PRIVACY_CHARTER,
                    reply_markup=get_consent_keyboard(member["id"]),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"سلام {member['name_fa']} عزیز ({member['avatar']})!\nچطور می‌توانم کمکتان کنم؟",
                    reply_markup=get_quick_menu_keyboard(),
                    parse_mode="Markdown"
                )
        else:
            members = get_all_members()
            if not members:
                await update.message.reply_text(
                    "🌱 **به سامانه خانواده‌یار خوش آمدید!**\nهنوز عضوی در سیستم تعریف نشده است. لطفاً ابتدا در عامل هوشمند یا پنل وب اعضا را ایجاد فرمایید.",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "🌱 **لطفاً برای اتصال به پروفایل، نام خود را انتخاب کنید:**",
                    reply_markup=get_member_select_keyboard(members),
                    parse_mode="Markdown"
                )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "🌿 **راهنمای دستورات سامانه خانواده‌یار:**\n\n"
            "• `/start` - منوی اصلی و ورود\n"
            "• `/chores` - مشاهده و ثبت وظایف روزمره خانه\n"
            "• `/habits` - پایش عادت‌ها و مراقبت‌های سلامتی\n"
            "• `/evaluation` - شرکت در ارزیابی جامع یا ماهانه خانواده\n"
            "• `/calendar` - تقویم کارهای امروز همه اعضا\n"
            "• `/status` - خلاصه آماری هفته\n"
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
            await update.message.reply_text(f"✨ {member['name_fa']} عزیز، برای امروز وظیفه زمان‌بندی شده‌ای نداری! وقت استراحته.")
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

    async def cmd_evaluation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manually trigger psychological evaluation drill"""
        user_id = update.effective_user.id
        member = get_member_by_telegram_id(user_id)
        if not member:
            await update.message.reply_text("لطفا ابتدا با زدن /start نام خود را انتخاب کنید.")
            return
        await self.start_evaluation_flow(user_id, member["id"], "monthly", update.message.reply_text)

    async def cmd_breathing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🌿 **تمرین تنفس آرامش‌بخش ۴-۷-۸:**\n\n"
            "۱. ۴ ثانیه آرام از بینی نفس بکشید 🌬️\n"
            "۲. ۷ ثانیه نفس را در سینه نگه دارید 🧘\n"
            "۳. ۸ ثانیه آرام از دهان بازدم کنید 🍃\n\n"
            "این چرخه را ۳ تا ۴ بار تکرار کنید تا ضربان قلب آرام گیرد.",
            parse_mode="Markdown"
        )

    # --- Interactive Clinical Evaluation State Machine ---

    async def start_evaluation_flow(self, user_id: int, member_id: int, eval_type: str, reply_fn):
        all_members = get_all_members()
        other_members = [m for m in all_members if m["id"] != member_id]

        self.user_states[user_id] = {
            "member_id": member_id,
            "eval_type": eval_type,
            "step": "medical" if eval_type == "baseline" else "safety",
            "other_members": other_members,
            "current_target_idx": 0,
            "interpersonal_substep": "hurt",
            "temp_data": {}
        }

        if eval_type == "baseline":
            await reply_fn(dlg.BASELINE_MEDICAL_PROMPT, parse_mode="Markdown")
        else:
            await reply_fn(
                dlg.MONTHLY_EVALUATION_INTRO.format(name="عزیز") + "\n\n" + dlg.SYSTEMIC_SAFETY_PROMPT,
                reply_markup=get_likert_keyboard("safety"),
                parse_mode="Markdown"
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button clicks"""
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = update.effective_user.id

        # 1. Member Binding Selection
        if data.startswith("bind_member:"):
            member_id = int(data.split(":")[1])
            link_telegram_id(member_id, user_id)
            member = get_member_by_id(member_id)
            if not member.get("consent_given"):
                await query.edit_message_text(
                    dlg.CONSENT_AND_PRIVACY_CHARTER,
                    reply_markup=get_consent_keyboard(member_id),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    f"✅ حساب شما با موفقیت به **{member['name_fa']}** ({member['avatar']}) متصل شد!",
                    reply_markup=get_quick_menu_keyboard(),
                    parse_mode="Markdown"
                )
            return

        # 2. Consent Action
        if data.startswith("consent:"):
            parts = data.split(":")
            action = parts[1]
            member_id = int(parts[2])
            member = get_member_by_id(member_id)
            name = member["name_fa"] if member else "همراه عزیز"

            if action == "agree":
                record_member_consent(member_id, True)
                await query.edit_message_text(
                    dlg.CONSENT_ACCEPTED.format(name=name),
                    parse_mode="Markdown"
                )
                await self.start_evaluation_flow(user_id, member_id, "baseline", query.message.reply_text)
            else:
                record_member_consent(member_id, False)
                await query.edit_message_text(dlg.CONSENT_DECLINED.format(name=name), parse_mode="Markdown")
            return

        # 3. Likert Scale Evaluations
        if data.startswith("eval:"):
            parts = data.split(":")
            metric = parts[1]
            score = int(parts[2])

            state = self.user_states.get(user_id, {})
            state.setdefault("temp_data", {})[metric] = score

            if metric == "safety":
                state["step"] = "respect"
                await query.edit_message_text(
                    f"ثبت شد: {score} از ۵ ✅\n\n" + dlg.SYSTEMIC_RESPECT_PROMPT,
                    reply_markup=get_likert_keyboard("respect"),
                    parse_mode="Markdown"
                )
            elif metric == "respect":
                state["step"] = "care"
                await query.edit_message_text(
                    f"ثبت شد: {score} از ۵ ✅\n\n" + dlg.SYSTEMIC_CARE_PROMPT,
                    reply_markup=get_likert_keyboard("care"),
                    parse_mode="Markdown"
                )
            elif metric == "care":
                state["step"] = "climate"
                await query.edit_message_text(
                    f"ثبت شد: {score} از ۵ ✅\n\n" + dlg.SYSTEMIC_CLIMATE_PROMPT,
                    reply_markup=get_likert_keyboard("climate"),
                    parse_mode="Markdown"
                )
            elif metric == "climate":
                # Finalize Evaluation
                member_id = state.get("member_id", 1)
                eval_type = state.get("eval_type", "monthly")
                td = state.get("temp_data", {})
                
                log_family_evaluation(
                    member_id=member_id,
                    evaluation_type=eval_type,
                    psychological_safety=td.get("safety", score),
                    respect_status=td.get("respect", score),
                    perceived_care=td.get("care", score),
                    overall_climate=td.get("climate", score),
                    narrative_text=td.get("medical_text", "")
                )
                self.user_states.pop(user_id, None)

                final_text = dlg.BASELINE_COMPLETED if eval_type == "baseline" else dlg.MONTHLY_COMPLETED
                await query.edit_message_text(final_text, reply_markup=get_quick_menu_keyboard(), parse_mode="Markdown")
            return

        # 4. Mood Checkin
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

        # 5. Chores & Menu
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

        if data == "menu:start_eval":
            member = get_member_by_telegram_id(user_id)
            if member:
                await self.start_evaluation_flow(user_id, member["id"], "monthly", query.message.reply_text)
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

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle open-ended text input & interview progression"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        member = get_member_by_telegram_id(user_id)
        member_id = member["id"] if member else 1

        state = self.user_states.get(user_id)

        # In-interview text processing
        if state:
            step = state.get("step")
            
            # Step A: Medical History
            if step == "medical":
                state.setdefault("temp_data", {})["medical_text"] = text
                if member:
                    update_member(
                        member_id=member["id"],
                        name=member["name"],
                        name_fa=member["name_fa"],
                        role=member["role"],
                        age=member["age"],
                        conditions=member["conditions"],
                        medical_history=text,
                        avatar=member.get("avatar", "👤")
                    )

                # Move to interpersonal perception if other members exist
                other_members = state.get("other_members", [])
                if other_members:
                    state["step"] = "interpersonal"
                    state["current_target_idx"] = 0
                    state["interpersonal_substep"] = "hurt"
                    target = other_members[0]
                    await update.message.reply_text(
                        dlg.INTERPERSONAL_HURT_PROMPT.format(target_name=target["name_fa"]),
                        parse_mode="Markdown"
                    )
                else:
                    # Directly to Likert safety
                    state["step"] = "safety"
                    await update.message.reply_text(
                        dlg.SYSTEMIC_SAFETY_PROMPT,
                        reply_markup=get_likert_keyboard("safety"),
                        parse_mode="Markdown"
                    )
                return

            # Step B: Interpersonal Pairwise Dynamics
            if step == "interpersonal":
                other_members = state.get("other_members", [])
                target_idx = state.get("current_target_idx", 0)
                substep = state.get("interpersonal_substep", "hurt")

                if target_idx < len(other_members):
                    target = other_members[target_idx]
                    
                    if substep == "hurt":
                        state.setdefault("current_pair_data", {})["hurt"] = text
                        state["interpersonal_substep"] = "appreciate"
                        await update.message.reply_text(
                            dlg.INTERPERSONAL_APPRECIATE_PROMPT.format(target_name=target["name_fa"]),
                            parse_mode="Markdown"
                        )
                    elif substep == "appreciate":
                        hurt_val = state.get("current_pair_data", {}).get("hurt", "")
                        # Save confidential dynamic
                        log_interpersonal_dynamics(
                            source_member_id=member_id,
                            target_member_id=target["id"],
                            hurt_points=hurt_val,
                            appreciate_points=text
                        )
                        state["current_pair_data"] = {}
                        
                        # Move to next target member or proceed to Likert scale
                        if target_idx + 1 < len(other_members):
                            state["current_target_idx"] = target_idx + 1
                            state["interpersonal_substep"] = "hurt"
                            next_target = other_members[target_idx + 1]
                            await update.message.reply_text(
                                dlg.INTERPERSONAL_HURT_PROMPT.format(target_name=next_target["name_fa"]),
                                parse_mode="Markdown"
                            )
                        else:
                            state["step"] = "safety"
                            await update.message.reply_text(
                                dlg.SYSTEMIC_SAFETY_PROMPT,
                                reply_markup=get_likert_keyboard("safety"),
                                parse_mode="Markdown"
                            )
                return

        # Normal text message (daily thoughts/notes)
        name = member["name_fa"] if member else "همراه عزیز"
        log_checkin(member_id=member_id, mood=4, win=text, notes=text, checkin_type="daily_text")
        reply = f"✨ سپاسگزارم {name} عزیز، پیام شما در سیستم ثبت شد:\n«{text}»\nانرژی مثبت شما در خانه جاریست 🌿"
        await update.message.reply_text(reply, reply_markup=get_quick_menu_keyboard())

    # --- Real Dispatch Functions with Detailed Status ---

    async def dispatch_morning_checkins(self) -> Dict[str, Any]:
        """Broadcast morning check-in to all consented members"""
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
                msg = dlg.MORNING_GREETING_GENERIC.format(name=m["name_fa"])
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

    async def dispatch_monthly_evaluations(self) -> Dict[str, Any]:
        """Broadcast monthly psychological evaluation drill to all consented members"""
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
                self.user_states[tid] = {
                    "member_id": m["id"],
                    "eval_type": "monthly",
                    "step": "safety",
                    "temp_data": {}
                }
                msg = dlg.MONTHLY_EVALUATION_INTRO.format(name=m["name_fa"]) + "\n\n" + dlg.SYSTEMIC_SAFETY_PROMPT
                await self.app.bot.send_message(
                    chat_id=tid,
                    text=msg,
                    reply_markup=get_likert_keyboard("safety"),
                    parse_mode="Markdown"
                )
                sent_to.append(m["name_fa"])
            except Exception as e:
                logger.error(f"Failed to dispatch monthly evaluation to {m['name_fa']}: {e}")
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
