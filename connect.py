from config import load_config
import asyncio
from psycopg_pool import AsyncConnectionPool

def create_pool(config):
    """ Create Pool """
    return AsyncConnectionPool(kwargs=config,open=False)

async def main():
    config = load_config()
    create_pool(config)
    await pool.open() #check errors here


if __name__ == '__main__':
    asyncio.run(main())
