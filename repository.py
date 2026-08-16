from psycopg_pool import AsyncConnectionPool

async def list_tasks(pool: AsyncConnectionPool, done: bool | None = None):
   async with pool.connection() as conn:
        if done == False:
            cursor = await conn.execute("SELECT * FROM tasks WHERE done = 'F'")
        elif done == None:
            cursor = await conn.execute("SELECT * FROM tasks")
        else:
            cursor = await conn.execute("SELECT * FROM tasks WHERE done = 't'")
        rows = await cursor.fetchall()
        return rows

async def get_task(pool: AsyncConnectionPool, id: int):
    async with pool.connection() as conn:
        cursor = await conn.execute("SELECT * FROM tasks WHERE id = %s",(id,))
    task = await cursor.fetchall()
    if task:
        return task
    else:
        return None

async def create_task(pool: AsyncConnectionPool, title: str, done: bool):
    async with pool.connection() as conn:
        cursor = await conn.execute("INSERT INTO tasks (title,done) VALUES (%s,%s) returning id,title,done",(title,done,))
        new_task = await cursor.fetchone()
        return new_task
    
async def update_task(pool: AsyncConnectionPool, title: str, done: bool):
    async with pool.connection() as conn:
        cursor = await conn.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s returning id,title,done",(title,done,id))
        updated_task = await cursor.fetchone()
        return updated_task

async def delete_task(pool: AsyncConnectionPool, int: id):
    async with pool.connection() as conn:
        cursor = await conn.execute("DELETE FROM tasks WHERE id = %s returning id,title,done",(id,))
        return cursor.fetchone()
