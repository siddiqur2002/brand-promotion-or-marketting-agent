import uuid
from typing import Any, Dict, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import CampaignTask, TaskStatus
from app.database.session import get_db
from app.workers.tasks import execute_campaign_task

router = APIRouter(prefix="/api/v1/campaigns", tags=["Marketing Campaigns"])


# --- Pydantic Schemas (Input & Output Validation) ---

class CampaignCreateRequest(BaseModel):
    brand_name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "EcoShoe"})
    product_description: str = Field(
        ..., min_length=10, json_schema_extra={"example": "Sustainable running shoes made from recycled ocean plastic."}
    )
    target_audience: str = Field(..., json_schema_extra={"example": "Eco-conscious marathon runners aged 25-40"})
    campaign_goal: str = Field(..., json_schema_extra={"example": "Direct sales for new product launch"})


class CampaignTaskResponse(BaseModel):
    # Map database 'id' column to 'task_id' in response output
    task_id: uuid.UUID = Field(..., validation_alias="id")
    status: TaskStatus
    brand_name: str
    research_result: Optional[str] = None
    # CrewAI output can be either a formatted dictionary or a raw text string
    ad_copies: Optional[Union[Dict[str, Any], str]] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Endpoints ---

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def create_campaign_task(
    payload: CampaignCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Creates a new marketing campaign task and queues it for background execution via Celery.
    """
    # 1. Create new task record in database with initial PENDING status
    new_task = CampaignTask(
        brand_name=payload.brand_name,
        product_description=payload.product_description,
        target_audience=payload.target_audience,
        campaign_goal=payload.campaign_goal,
        status=TaskStatus.PENDING,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # 2. Dispatch Celery background worker task asynchronously
    execute_campaign_task.delay(str(new_task.id))

    return {
        "message": "Campaign creation task accepted and queued.",
        "task_id": str(new_task.id),
        "status": TaskStatus.PENDING,
    }


@router.get("/{task_id}", response_model=CampaignTaskResponse)
async def get_campaign_status(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CampaignTask:
    """
    Retrieves the status and execution results for a specific campaign task by ID.
    """
    result = await db.execute(
        select(CampaignTask).where(CampaignTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign task with ID {task_id} not found.",
        )

    return task

