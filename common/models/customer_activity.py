from collections import defaultdict
from datetime import date, datetime
from uuid import uuid4
from enum import Enum
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, Iterable
from starlette.datastructures import FormData

from common import logger, db_execute, db_fetch_all, DatabaseException, config


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
    status: str = Field(..., description="Статус активности")
    event_manager: str = Field(..., description="Ответственный за активность менеджер")

    @staticmethod
    def from_request(data: ActivityRequest) -> 'BaseActivityEntity':
        logger.info(f"Создаем ActivityEntity из ActivityRequest: {data}")
        return BaseActivityEntity(
            lead_id=data.lead_id,
            status=data.lead_status,
            event_manager=data.responsible_name,
        )


class ActivityEntity(BaseActivityEntity):
    created_at: str = Field(..., description="Дата добавления события")
    status_id: str = Field(..., description="Виртуальный ид статуса")

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
            "status": activity.status,
            "event_manager": activity.event_manager,
        },
        autocommit=True,
    )


class Statuses(Enum):
    id_1 = 'Аванс получен/подготовка начата'
    id_2 = 'Взят в работу'
    id_3 = 'Закрыто и не реализовано'
    id_4 = 'Квалифицирован'
    id_5 = 'Новый лид'
    id_6 = 'Показ назначен'
    id_7 = 'Сделка состоялась'
    id_8 = 'Показ подтвержден'
    id_9 = 'Состоявшиеся показы'


def _get_status_id_alias_query():
    cases = ''
    for status in Statuses:
        cases += f"WHEN status = '{status.value}' THEN '{status.name}' \r\n"
    return f"""
    CASE
        WHEN status = 'Аванс получен/подготовка начата' THEN 'id_1'
        WHEN status = 'Взят в работу' THEN 'id_2'
        WHEN status = 'Закрыто и не реализовано' THEN 'id_3'
        WHEN status = 'Квалифицирован' THEN 'id_4'
        WHEN status = 'Новый лид' THEN 'id_5'
        WHEN status = 'Показ назначен' THEN 'id_6'
        WHEN status = 'Сделка состоялась' THEN 'id_7'
        WHEN status = 'Показ подтвержден' THEN 'id_8'
        WHEN status = 'Состоявшиеся показы' THEN 'id_9'
        ELSE 'id_err'
    END
    """


def _get_base_query():
    return f"""
        SELECT
            lead_id,
            status,
            date(created_at) as created_at,
            event_manager,
            {_get_status_id_alias_query()} as status_id
        FROM (
            SELECT
                lead_id,
                CASE
                    WHEN status IN ('Показ состоялся', 'Покупатель заинтересован') THEN 'Состоявшиеся показы'
                    ELSE status
                END as status,
                event_manager,
                created_at
            FROM
                customer_activity
        ) as subquery
        WHERE 1=1 
    """


async def get_raw_activity(
        date_start: date,
        status_id: Union[Statuses, None] = None,
        date_end: Union[date, None] = None
) -> Iterable[ActivityEntity] | None:

    date_filter = f"AND date(created_at) = date('{date_start}')"

    if date_end:
        date_filter = f"AND date(created_at) BETWEEN date('{date_start}') AND date('{date_end}')"

    status_filter = ''
    if status_id:
        status_filter = f"AND {_get_status_id_alias_query()} = '{status_id}'"

    query = f"""
        {_get_base_query()}
        {date_filter}
        {status_filter}
        ORDER BY 
            CASE status
                WHEN 'Квалифицирован' THEN 1
                WHEN 'Показ подтвержден' THEN 2
                WHEN 'Показ назначен' THEN 3
                WHEN 'Покупатель заинтересован' THEN 4
                WHEN 'Показ состоялся' THEN 5
                WHEN 'Аванс получен/подготовка начата' THEN 6
                ELSE 7
            END
    """
    logger.info(f'Запрос {query}')
    try:
        activity = await db_fetch_all(query)
    except DatabaseException as e:
        logger.error(f'Ошибка при выполнении запроса {query}: {e}')
        return None

    if not activity:
        return None
    result = []
    for item in activity:
        result.append(ActivityEntity(**item))
    return result


async def group_activity_by_status(activity: Iterable[ActivityEntity]) -> Union[dict, None]:
    result = defaultdict(lambda: {
        'status': '',
        'status_id': '',
        'count': 0,
        'data': defaultdict(lambda: {
            'event_manager': '',
            'count': 0
        })
    })
    if not activity:
        return None

    for entry in activity:
        status = entry.status
        status_id = entry.status_id
        event_manager = entry.event_manager

        result[status]['status'] = status
        result[status]['status_id'] = status_id
        result[status]['count'] += 1

        result[status]['data'][event_manager]['event_manager'] = event_manager
        result[status]['data'][event_manager]['count'] += 1

    final_result = {k: dict(v) for k, v in result.items()}
    for status, info in final_result.items():
        info['data'] = dict(info['data'])

    return final_result


async def get_plot(activities: Union[dict, None], date_start: str, date_end: Union[str, None] = None) -> str:
    # Параметры графика
    fig, ax = plt.subplots(figsize=(10, 7))

    # Настройка цвета
    colors = plt.cm.Paired(range(len(activities)))

    # Генерация графиков по каждому статусу
    for i, (status, status_data) in enumerate(activities.items()):
        labels = list(status_data['data'].keys())
        values = [manager_data['count'] for manager_data in status_data['data'].values()]
        ax.barh(labels, values, color=colors[i], label=f"{status} ({status_data['count']})")

    title = f"Оперативный отчет за {date_start}"
    if date_end:
        title = f"Оперативный отчет за период c {date_start} по {date_end}"
    ax.legend()
    ax.set_title(title)
    ax.set_xlabel('Количество')
    ax.set_ylabel('Менеджеры')

    # Сохранение графика в файл
    plt.tight_layout()
    name = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
    name = f'{config.Store.IMG_DIR}/{name}.png'
    plt.savefig(name, dpi=300)

    return name
