import os
import asyncio
from common import db_execute, db_fetch_all, db_close_async
from common.config import config


async def apply_migrations():
    migrations_dir = config.Db.MIGRATIONS_DIR
    await db_execute(
        '''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY
            )
        '''
    )

    applied_migrations = set(row['version'] for row in await db_fetch_all("SELECT version FROM schema_migrations"))

    migrations = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])

    for migration in migrations:
        if migration in applied_migrations:
            print(f"Skipping already applied migration: {migration}")
            continue

        with open(os.path.join(migrations_dir, migration), 'r') as f:
            sql = f.read()
            await db_execute(sql)
            await db_execute("INSERT INTO schema_migrations (version) VALUES (?)", (migration,))
            print(f"Applied migration: {migration}")

    db_close_async()

if __name__ == "__main__":
    asyncio.run(apply_migrations())

