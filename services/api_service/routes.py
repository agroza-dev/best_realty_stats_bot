from fastapi import Request, HTTPException, APIRouter
from common.logger import logger
from common import customer_activity

router = APIRouter()


@router.post("/activity_by_customer")
async def activity_by_customer(request: Request):
    try:
        form_data = await request.form()
        logger.info(f"Получены данные: {form_data}")

        activity_data = customer_activity.ActivityRequest.from_form_data(form_data)
        logger.info(f"Объект запроса: {activity_data}")

        await customer_activity.add(customer_activity.BaseActivityEntity.from_request(activity_data))

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing: {str(e)}")