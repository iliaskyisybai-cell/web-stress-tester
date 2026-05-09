import asyncio
import aiohttp
import time
import argparse
import os

async def send_request(session, semaphore, url, i, verbose):
    async with semaphore:
        try:
            async with session.get(f"{url}?test={i}", ssl=False) as response:
                if verbose and i % 100 == 0:
                    print(f"[{i}] Статус: {response.status}")
                return response.status
        except Exception:
            return None

async def main():
    parser = argparse.ArgumentParser(description="Async Web Stress Tester")
    parser.add_argument("url", help="Целевой URL (например, https://example.com/)")
    parser.add_argument("-c", "--concurrent", type=int, default=100, help="Количество одновременных соединений")
    parser.add_argument("-n", "--number", type=int, default=1000, help="Общее количество запросов")
    parser.add_argument("-v", "--verbose", action="store_true", help="Показывать лог отправки")
    
    args = parser.parse_args()

    semaphore = asyncio.Semaphore(args.concurrent)
    connector = aiohttp.TCPConnector(limit=args.concurrent, ssl=False)
    
    print(f"--- Запуск теста ---")
    print(f"Цель: {args.url}")
    print(f"Потоков: {args.concurrent} | Всего запросов: {args.number}\n")

    start_time = time.time()
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [send_request(session, semaphore, args.url, i, args.verbose) for i in range(args.number)]
        results = await asyncio.gather(*tasks)

    duration = time.time() - start_time
    success = [r for r in results if r == 200]
    errors = [r for r in results if r is None or r >= 400]

    print(f"\n--- Результаты ---")
    print(f"Время выполнения: {duration:.2f} сек")
    print(f"Успешных (200 OK): {len(success)}")
    print(f"Ошибок/Отказов: {len(errors)}")
    print(f"Средняя скорость: {len(results) / duration:.2f} запр/сек")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nТест прерван пользователем.")
