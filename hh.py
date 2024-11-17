import csv
import sqlite3
from enum import Enum

import requests


class Employers(Enum):
    ALFA = 80
    OZON = 2180
    TBANK = 78638
    WILDBERRIES = 87021


url = "https://api.hh.ru/vacancies"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
period = 7  # days
area = 1  # Moscow


def fetch_vacancies(employer: Employers, page: int) -> list[tuple[str, str, str]]:
    params = {
        "employer_id": employer.value,
        "area": area,
        "employment": "full",
        "schedule": ["fullDay", "remote"],
        "experience": ["between1And3", "between3And6", "moreThan6"],
        "period": period,
        "page": page,
        "per_page": 100,
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return [
        (employer.name, item.get("name"), item.get("published_at"))
        for item in data.get("items", [])
    ]


def main():
    results = []
    for employer in Employers:
        for page in range(21):
            items = fetch_vacancies(employer, page)
            if items:
                results.extend(items)
            else:
                break
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


if __name__ == "__main__":
    main()
