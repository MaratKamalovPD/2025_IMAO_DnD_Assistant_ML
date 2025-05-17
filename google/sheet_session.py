import os
import time
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class SheetSession:
    def __init__(self, spreadsheet_id, default_range):
        self.spreadsheet_id = spreadsheet_id
        self.default_range = default_range
        self.service = self._auth()
        self.data = []
        self.buffer = []
        self.last_flush = time.time()
        self.flush_interval = 60  # Автоматическая отправка через 60 секунд
        self.max_buffer_size = 10  # Отправлять, если накопилось 10 изменений

        self.refresh()

    def _auth(self):
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return build('sheets', 'v4', credentials=creds)

    # ========== ЧТЕНИЕ ==========

    def refresh(self):
        print("[Sheets] Обновляю локальный кэш...")
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.default_range
        ).execute()
        self.data = result.get('values', [])
        print("[Sheets] Кэш обновлён.")

    def get(self):
        return self.data

    def get_cell(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return None

    # ========== ЗАПИСЬ ==========

    def queue_write(self, range_name, values):
        self.buffer.append({
            'range': range_name,
            'values': values
        })
        self._maybe_flush()

    def _maybe_flush(self):
        if len(self.buffer) >= self.max_buffer_size or time.time() - self.last_flush > self.flush_interval:
            #self.flush()
            pass

    def flush(self):
        if not self.buffer:
            return
        print(f"[Sheets] Отправка {len(self.buffer)} операций...")
        body = {
            'valueInputOption': 'RAW',
            'data': self.buffer
        }
        result = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        ).execute()
        print(f"[Sheets] Обновлено {result.get('totalUpdatedCells')} ячеек.")
        self.buffer.clear()
        self.last_flush = time.time()
