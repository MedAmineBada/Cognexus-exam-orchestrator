import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .external_services import purge_files

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def scheduled_purge():
    """Auto-purge draft folders every 2 days"""

    folders = ["corrections_draft", "exams_draft"]

    for folder in folders:
        try:
            logger.info(f"Auto-purging folder: {folder}")
            result = await purge_files(folder)
            logger.info(f"Purge completed for {folder}: deleted {result.get('deleted_count', 0)} files")
        except Exception as e:
            logger.error(f"Auto-purge failed for {folder}: {str(e)}")


def start_scheduler():
    scheduler.add_job(
        scheduled_purge,
        trigger=IntervalTrigger(days=2),
        id="auto_purge_drafts",
        name="Auto-purge draft folders",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started - auto-purge runs every 2 days")