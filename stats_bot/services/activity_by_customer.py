from dataclasses import dataclass, field
from typing import Optional
from fastapi import Form

from stats_bot.db import execute
from stats_bot.services.logger import logger


@dataclass()
class ActivityRequest:
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
    def from_form_data(data: Form) -> 'ActivityRequest':
        logger.error(f"Получили данные для формирования ActivityRequest: {data}")
        required_fields = ['lead_id', 'lead_status', 'responsible_name']
        for required_field in required_fields:
            if required_field not in data:
                logger.error(f"Отсутствует обязательное поле: {required_field}")
                raise ValueError(f"Missing required field: {required_field}")

        return ActivityRequest(
            lead_id=int(data['lead_id']),
            event=data['event'],
            lead_status=data['lead_status'],
            responsible_name=data['responsible_name'],
            event_time=data['event_time'],
            lead_url=data['lead_url'],
            client_name=data.get('client_name'),
            adres=data.get('adres'),
            pipeline=data.get('pipeline'),
            lead_type=data.get('lead_type'),
            object_type=data.get('object_type'),
            area=data.get('area'),
            analog_or_original=data.get('analog_or_original')
        )


@dataclass()
class ActivityEntity:
    lead_id: int = field(metadata={"comment": "ID сделки, не уникальный в рамках этой таблицы"})
    lead_status: str = field(metadata={"comment": "Статус активности"})
    responsible_name: str = field(metadata={"comment": "Ответственный за активность менеджер"})

    @staticmethod
    def from_request(data: ActivityRequest) -> 'ActivityEntity':
        required_fields = ['lead_id', 'lead_status', 'responsible_name']
        for required_field in required_fields:
            if not hasattr(data, required_field):
                logger.error(f"Отсутствует обязательное поле: {required_field} в {data}")
                raise ValueError(f"Missing required field: {required_field}")

        return ActivityEntity(
            lead_id=int(data.lead_id),
            lead_status=data.lead_status,
            responsible_name=data.responsible_name,
        )


async def add_activity(activity: ActivityEntity):
    await execute(
        """
            INSERT INTO customer_activity 
            (lead_id, status, event_manager, created_at)
            VALUES 
            (:deal_id, :status, :event_manager, datetime('now', 'localtime'));
        """,
        {
            "deal_id": activity.lead_id,
            "status": activity.lead_status,
            "event_manager": activity.responsible_name,
        },
        autocommit=True,
    )