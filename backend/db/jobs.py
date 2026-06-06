import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models

# In-memory dictionary tracking running tasks: job_id -> asyncio.Task
active_tasks: Dict[str, asyncio.Task] = {}

async def create_job(
    db: AsyncSession,
    session_id: str,
    job_id: str,
    user_request: Optional[str] = None
) -> models.Job:
    db_job = models.Job(
        id=job_id,
        session_id=session_id,
        status="pending",
        user_request=user_request
    )
    db.add(db_job)
    await db.flush()
    return db_job

async def update_job_status(
    db: AsyncSession,
    job_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    errors: Optional[List[str]] = None
) -> Optional[models.Job]:
    db_job = await get_job(db, job_id)
    if db_job:
        db_job.status = status
        if result is not None:
            db_job.result = result
        if errors is not None:
            db_job.errors = errors
        await db.flush()
    return db_job

async def get_job(db: AsyncSession, job_id: str) -> Optional[models.Job]:
    result = await db.execute(select(models.Job).where(models.Job.id == job_id))
    return result.scalar_one_or_none()

async def cancel_job(db: AsyncSession, job_id: str) -> Optional[models.Job]:
    # 1. Cancel in-memory task if running
    task = active_tasks.pop(job_id, None)
    if task:
        task.cancel()
        
    # 2. Update status in database
    return await update_job_status(db, job_id, "cancelled")
