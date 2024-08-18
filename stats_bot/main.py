from fastapi import FastAPI
from stats_bot.services import logger

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}