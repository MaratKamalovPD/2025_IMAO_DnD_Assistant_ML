import requests
import json

URL = "https://ttg.club/api/v1/bestiary"
OUTPUT_FILE = "bestiary_data.json"

headers = {
    "Content-Type": "application/json"
}

def fetch_page(page: int, size: int = 160):
    payload = {
        "page": page,
        "size": size,
        "search": {"value": "", "exact": False},
        "order": [
            {"field": "exp", "direction": "asc"},
            {"field": "name", "direction": "asc"}
        ]
    }
    response = requests.post(URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка {response.status_code} при получении страницы {page}")
        return None

def crawl_all_pages():
    all_data = []
    page = 0

    while True:
        data = fetch_page(page)
        if not data:
            break
        
        all_data.extend(data)
        print(f"Страница {page} обработана, получено {len(data)} записей")
        
        if len(data) < 160:  # Если вернулось меньше 160 записей, значит это последняя страница
            break
        
        page += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"Сохранено {len(all_data)} записей в {OUTPUT_FILE}")

if __name__ == "__main__":
    crawl_all_pages()
