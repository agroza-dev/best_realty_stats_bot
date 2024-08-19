import uvicorn
from fastapi import FastAPI, Request, HTTPException
from stats_bot.services.logger import logger
from stats_bot.services.activity_by_customer import ActivityRequest, add_activity, ActivityEntity

app = FastAPI()


@app.post("/activity_by_customer")
async def activity_by_customer(request: Request):
    try:
        form_data = await request.form()
        logger.info(f"Получены данные: {form_data}")

        activity_data = ActivityRequest.from_form_data(form_data)
        logger.info(f"Объект запроса: {activity_data}")

        await add_activity(ActivityEntity.from_request(activity_data))

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
