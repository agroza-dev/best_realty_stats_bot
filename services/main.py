import asyncio
import uvicorn
import platform
from common.logger import logger
from common.db import db_close
from fastapi import FastAPI
from services.api_service.routes import router as webhook_router
from services.bot_service.bot import start as start_bot

app = FastAPI()
app.include_router(webhook_router)


async def start_fastapi():
    logger.info("Initializing FastAPI server...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    logger.info("Starting FastAPI server...")
    await server.serve()
    logger.info("FastAPI server stopped.")


async def main():
    try:
        await asyncio.gather(
            start_fastapi(),
            start_bot()
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        db_close()
        logger.info("Application shutdown complete.")


async def shutdown(loop):
    logger.info("Shutting down...")

    db_close()

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == "__main__":
    try:
        logger.info("Creating new event loop...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info("Event loop created and set.")

        logger.info("Starting main function with event loop.")
        loop.run_until_complete(main())
    except Exception:
        import traceback
        logger.error(traceback.format_exc())
    finally:
        db_close()
        logger.info("Shutting down application.")
