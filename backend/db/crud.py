from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from . import models
from typing import List, Optional
import uuid

async def create_session(db: AsyncSession, file_name: str, file_path: str, session_id: Optional[str] = None) -> models.Session:
    if not session_id:
        session_id = str(uuid.uuid4())
    db_session = models.Session(
        id=session_id,
        file_name=file_name,
        file_path=file_path
    )
    db.add(db_session)
    await db.flush()
    return db_session

async def get_session(db: AsyncSession, session_id: str) -> Optional[models.Session]:
    result = await db.execute(select(models.Session).where(models.Session.id == session_id))
    return result.scalar_one_or_none()

async def update_session_report_path(db: AsyncSession, session_id: str, report_path: str):
    await db.execute(
        update(models.Session)
        .where(models.Session.id == session_id)
        .values(report_path=report_path)
    )
    await db.flush()

async def create_message(
    db: AsyncSession, 
    session_id: str, 
    role: str, 
    content: str, 
    msg_type: str = "text",
    metadata: Optional[dict] = None
) -> models.Message:
    db_message = models.Message(
        session_id=session_id,
        role=role,
        content=content,
        msg_type=msg_type,
        metadata_json=metadata
    )
    db.add(db_message)
    await db.flush()
    return db_message

async def get_messages(db: AsyncSession, session_id: str) -> List[models.Message]:
    result = await db.execute(
        select(models.Message)
        .where(models.Message.session_id == session_id)
        .order_by(models.Message.created_at.asc())
    )
    return result.scalars().all()

async def get_setting(db: AsyncSession, key: str) -> Optional[str]:
    result = await db.execute(select(models.Setting).where(models.Setting.key == key))
    setting = result.scalar_one_or_none()
    return setting.value if setting else None

async def update_setting(db: AsyncSession, key: str, value: str):
    # Try to update, if not exists, create
    result = await db.execute(select(models.Setting).where(models.Setting.key == key))
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = value
    else:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    
    await db.flush()
