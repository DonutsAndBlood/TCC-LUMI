import asyncio
import concurrent.futures

import concurrent


if __name__ == "__main__":
    import bot.main as bot
    import websocket.main as websocket

    async def start():
        loop = asyncio.get_event_loop()
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=1)
        bot_loop = loop.run_in_executor(pool, bot.start_bot)
        sv_task = asyncio.create_task(websocket.main())
        while not sv_task.done() and not bot_loop.done():
            await asyncio.sleep(0)

    asyncio.run(start())
