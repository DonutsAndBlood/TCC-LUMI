import asyncio
import concurrent.futures
from multiprocessing import Process

import concurrent


if __name__ == "__main__":
    import main
    import server

    async def start():
        loop = asyncio.get_event_loop()
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=1)
        bot = loop.run_in_executor(pool, main.start_bot)
        sv = asyncio.create_task(server.main())
        while not sv.done() and not bot.done():
            await asyncio.sleep(1)

    asyncio.run(start())
