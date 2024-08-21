from pydantic import BaseModel, Field
from typing import Optional, Dict
from starlette.datastructures import FormData

from common import logger, db_execute


class ActivityRequest(BaseModel):
    lead_id: int
    event: str
    lead_status: str
    responsible_name: str
    event_time: str
    lead_url: str
    client_name: Optional[str] = None
    adres: Optional[str] = None
    pipeline: Optional[str] = None
    lead_type: Optional[str] = None
    object_type: Optional[str] = None
    area: Optional[str] = None
    analog_or_original: Optional[str] = None

    @staticmethod
    def from_form_data(data: FormData) -> 'ActivityRequest':
        logger.info(f"Получены данные для формирования ActivityRequest: {data}")
        return ActivityRequest(
            lead_id=int(data.get('lead_id')),
            event=data.get('event'),
            lead_status=data.get('lead_status'),
            responsible_name=data.get('responsible_name'),
            event_time=data.get('event_time'),
            lead_url=data.get('lead_url'),
            client_name=data.get('client_name'),
            adres=data.get('adres'),
            pipeline=data.get('pipeline'),
            lead_type=data.get('lead_type'),
            object_type=data.get('object_type'),
            area=data.get('area'),
            analog_or_original=data.get('analog_or_original')
        )


class BaseActivityEntity(BaseModel):
    lead_id: int = Field(..., description="ID сделки, не уникальный в рамках этой таблицы")
    lead_status: str = Field(..., description="Статус активности")
    responsible_name: str = Field(..., description="Ответственный за активность менеджер")

    @staticmethod
    def from_request(data: ActivityRequest) -> 'BaseActivityEntity':
        logger.info(f"Создаем ActivityEntity из ActivityRequest: {data}")
        return BaseActivityEntity(
            lead_id=data.lead_id,
            lead_status=data.lead_status,
            responsible_name=data.responsible_name,
        )


class ActivityEntity(BaseActivityEntity):
    customer_activity_id: int = Field(..., description="Автоинкрементный ID")
    created_at: str = Field(..., description="Дата добавления события")

    @staticmethod
    def from_db(data: Dict[str, str]) -> 'ActivityEntity':
        logger.info(f"Создаем ActivityEntity из ActivityRequest: {data}")
        return ActivityEntity(**data)


async def add(activity: BaseActivityEntity):
    if isinstance(activity, ActivityRequest):
        activity = BaseActivityEntity.from_request(activity)

    await db_execute(
        """
            INSERT INTO customer_activity 
            (lead_id, status, event_manager, created_at)
            VALUES 
            (:lead_id, :status, :event_manager, datetime('now', 'localtime'));
        """,
        {
            "lead_id": activity.lead_id,
            "status": activity.lead_status,
            "event_manager": activity.responsible_name,
        },
        autocommit=True,
    )