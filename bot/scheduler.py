"""
Automated Scheduling Engine for Family Evolution
Pure AsyncIO-based scheduler for maximum portability across all Python environments.
Handles daily checkins, weekly review, monthly evaluations, and automated database backups to admin.
"""
import asyncio
import logging
from datetime import datetime
from core.config import config
from bot.telegram_bot import telegram_bot
from brain.reporter import generate_weekly_analysis
from data.database import generate_schedule_for_days, get_db_connection
from bot import dialogues_fa as dlg

logger = logging.getLogger(__name__)

class FamilyScheduler:
    def __init__(self):
        self._task: asyncio.Task = None
        self._running = False
        self._last_executed_slots = set()

    def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Family Evolution AsyncIO Scheduler loop launched.")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def _scheduler_loop(self):
        while self._running:
            try:
                now = datetime.now()
                hour = now.hour
                minute = now.minute
                weekday = now.weekday()  # Monday=0, Sunday=6
                day_of_month = now.day
                time_key = f"{now.strftime('%Y-%m-%d')}_{hour:02d}:{minute:02d}"

                if time_key not in self._last_executed_slots:
                    self._last_executed_slots.add(time_key)
                    if len(self._last_executed_slots) > 100:
                        self._last_executed_slots = set(list(self._last_executed_slots)[-50:])

                    # 1. Morning Check-in (09:00 daily)
                    if hour == 9 and minute == 0:
                        logger.info("Triggering scheduled morning check-in...")
                        await telegram_bot.dispatch_morning_checkins()

                    # 2. Evening Check-in (20:00 daily)
                    if hour == 20 and minute == 0:
                        logger.info("Triggering scheduled evening check-in...")
                        await telegram_bot.dispatch_evening_checkins()

                    # 3. Monthly Psychological Evaluation (1st day of month at 10:00)
                    if day_of_month == 1 and hour == 10 and minute == 0:
                        logger.info("Triggering scheduled monthly psychological evaluation...")
                        await telegram_bot.dispatch_monthly_evaluations()

                    # 4. Weekly AI Analysis & Report (Saturday at 21:00)
                    if weekday == 5 and hour == 21 and minute == 0:
                        logger.info("Triggering scheduled weekly AI analysis...")
                        leader_report, family_broadcast, _ = generate_weekly_analysis(days=7)
                        await telegram_bot.dispatch_custom_broadcast(f"📊 **پیام هفتگی آرامش و پیشرفت خانه:**\n\n{family_broadcast}")

                    # 5. Weekly Database Backup to Admin Telegram (Saturday at 21:05)
                    if weekday == 5 and hour == 21 and minute == 5:
                        logger.info("Triggering scheduled weekly database backup to admin...")
                        await telegram_bot.send_database_backup_to_admin()

                    # 6. Daily Schedule Maintenance (00:05 daily)
                    if hour == 0 and minute == 5:
                        generate_schedule_for_days(7)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler tick error: {e}")

            await asyncio.sleep(20)

family_scheduler = FamilyScheduler()
