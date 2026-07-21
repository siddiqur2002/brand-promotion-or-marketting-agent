import asyncio
import uuid
import logging
from typing import Any
from sqlalchemy import select

from app.workers.celery_app import celery
from app.database.session import AsyncSessionLocal
from app.database.models import CampaignTask, TaskStatus
from app.agents.crew import run_marketing_crew

logger = logging.getLogger("celery.tasks")


@celery.task(name="execute_campaign_task", bind=True, max_retries=2)
def execute_campaign_task(self: Any, task_id_str: str) -> str:
    """
    Celery Task Wrapper যা Async Loop চালিয়ে CrewAI প্রসেস সম্পন্ন করবে।
    """
    task_id = uuid.UUID(task_id_str)
    
    try:
        # অ্যাসিঙ্ক ফাংশন রান করানো
        asyncio.run(_async_process_campaign(task_id))
        return f"Task {task_id_str} completed successfully."
    except Exception as exc:
        logger.error(f"Task {task_id_str} failed: {exc}")
        # বিফল হলে রিকভারি/রিট্রাই লজিক
        raise self.retry(exc=exc, countdown=10)


async def _async_process_campaign(task_id: uuid.UUID) -> None:
    """
    অ্যাসিঙ্ক ডাটাবেজ অপারেশন এবং CrewAI এক্সিকিউশন।
    """
    async with AsyncSessionLocal() as session:
        # ১. ডাটাবেজ থেকে আইডি অনুযায়ী রেকর্ড ফেচ করা
        result = await session.execute(
            select(CampaignTask).where(CampaignTask.id == task_id)
        )
        campaign = result.scalar_one_or_none()

        if not campaign:
            logger.error(f"Campaign with ID {task_id} not found.")
            return

        # ২. স্ট্যাটাস আপডেট -> PROCESSING
        campaign.status = TaskStatus.PROCESSING
        await session.commit()

        try:
            # ৩. এজেন্টের জন্য ইনপুট ডাটা সাজানো
            inputs = {
                "brand_name": campaign.brand_name,
                "product_description": campaign.product_description,
                "target_audience": campaign.target_audience,
                "campaign_goal": campaign.campaign_goal,
            }

            # 8. CrewAI রান করা (Blocking LLM calls happen here)
            crew_result = await run_marketing_crew(inputs)

            # ৫. সফল হলে ডাটাবেজে রেজাল্ট সেভ ও স্ট্যাটাস COMPLETED করা
            campaign.research_result = crew_result.get("research_result")
            campaign.ad_copies = crew_result.get("ad_copies")
            campaign.status = TaskStatus.COMPLETED

        except Exception as e:
            # ৬. এরর হলে স্ট্যাটাস FAILED করা এবং মেসেজ সেভ রাখা
            await session.rollback()
            campaign.status = TaskStatus.FAILED
            campaign.error_message = str(e)
            logger.exception(f"Error during Crew execution for task {task_id}")

        finally:
            await session.commit()

