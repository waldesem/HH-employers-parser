import asyncio
import csv
import sqlite3
from enum import Enum
from itertools import chain

from aiohttp import ClientSession


class Employers(Enum):
    ALFA = 80
    OZON = 2180
    TBANK = 78638
    WILDBERRIES = 87021


url = "https://api.hh.ru/vacancies"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
pages = 20  # not more
period = 1


async def fetch_vacancies(
    session: ClientSession, employer: Employers, page: int
) -> list[tuple[str, str, str]]:
    params = {
        "id": employer.value,
        "area": 1,
        "employment": "full",
        "schedule": ["fullDay", "remote"],
        "experience": ["between1And3", "between3And6", "moreThan6"],
        "period": period,
        "page": page,
        "per_page": 100,
        "vacancy_search_order": "publication_time",
    }
    async with session.get(url, params=params, headers=headers) as response:
        data = await response.json()
        return [
            (employer.name, item.get("name"), item.get("published_at"))
            for item in data.get("items", [])
        ]


async def main():
    async with ClientSession() as session:
        results = []
        for employer in Employers:
            items = await asyncio.gather(
                *[
                    fetch_vacancies(session, employer, page)
                    for page in range(pages + 1)
                ]
            )
            results.extend(chain.from_iterable(items))
            print(f"done {employer}")

        # write to csv
        with open("hh.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["employer", "vacancy", "published_at"])
            writer.writerows(results)

        # write to db
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

        print("done all")


asyncio.run(main())

lst = [["employer", "vacancy", "published_at"], ["employer", "vacancy", "published_at"]]