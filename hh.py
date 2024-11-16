from enum import Enum
import aiohttp
import sqlite3
import asyncio


class Employers(Enum):
    ALFA = 80
    OZON = 2180
    TBANK = 78638
    WILDBERRIES = 87021


url = "https://api.hh.ru/vacancies"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.101.76 Safari/537.36",
}

pages = 20


async def fetch_vacancies(session, employer, page):
    params = {
        "id": employer.value,
        "area": 1,
        "employment": "full",
        "schedule": ["fullDay", "flexible", "remote"],
        "experience": ["between1And3", "between3And6", "moreThan6"],
        "period": 1,
        "page": page,
        "per_page": 100,
        "vacancy_search_order": "publication_time"
    }
    async with session.get(url, params=params, headers=headers) as response:
        data = await response.json()
        return [(employer.name, item["name"], item["published_at"]) for item in data["items"]]


async def main():
    async with aiohttp.ClientSession() as session:
        results = []
        for employer in Employers:
            for i in range(1, pages):
                items = await fetch_vacancies(session, employer, i)
                results.extend(items)

        with sqlite3.connect("hh.db") as con:
            cur = con.cursor()

            cur.execute("""CREATE TABLE IF NOT EXISTS vacancies(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer TEXT,
                vacancy TEXT,
                published_at TEXT
            )""")
            cur.executemany(
                "INSERT INTO vacancies (employer, vacancy, published_at) VALUES (?, ?, ?)",
                results,
            )

            con.commit()


asyncio.run(main())
