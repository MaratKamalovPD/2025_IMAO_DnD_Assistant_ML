from google.sheet_session import SheetSession


if __name__ == "__main__":
    SPREADSHEET_ID = '1IJiRhD5OziG_1IpwHP1VwlDhhZruesxLZgIrVn4ehBg'
    RANGE = 'CreatureImages!A2:D1887'  # Подставь актуальное имя листа

    sheet = SheetSession(spreadsheet_id=SPREADSHEET_ID, default_range=RANGE)

    print(sheet.get_cell(1, 0))  # Получить A2 (нумерация с нуля)

    # Очередь изменений
    sheet.queue_write('CreatureImages!E10:G10', [['Новое', 'значение', 'в таблице']])
    sheet.queue_write('CreatureImages!E11:G11', [['Буфер', 'работает', 'OK']])

    # Можно принудительно отправить
    sheet.flush()
