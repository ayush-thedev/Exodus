import asyncio
from backend.db.database import engine

async def alter_table():
    async with engine.begin() as conn:
        try:
            await conn.execute(
                __import__('sqlalchemy').text("ALTER TABLE sessions ADD COLUMN report_path VARCHAR")
            )
            print("Successfully added report_path column.")
        except Exception as e:
            print(f"Error (might already exist): {e}")

if __name__ == "__main__":
    asyncio.run(alter_table())
