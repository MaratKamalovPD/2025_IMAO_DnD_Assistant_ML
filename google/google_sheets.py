import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Загружаем переменные из .env
load_dotenv()

# Берём путь к ключу из переменной окружения
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

# Права доступа
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

load_dotenv()

# ID таблицы из твоей ссылки
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = 'CreatureImages!A1:B10'

# Авторизация с использованием Service Account
def authenticate_service_account():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

# Чтение данных из таблицы
def read_sheet():
    service = authenticate_service_account()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    values = result.get('values', [])

    if not values:
        print('Нет данных.')
    else:
        for row in values:
            print(row)

if __name__ == '__main__':
    read_sheet()
