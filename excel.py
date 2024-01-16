from openpyxl import Workbook
from database import DataBase
db = DataBase()


async def generate_excel():
    wb = Workbook()
    sheet = wb.active
    data = await db.get_users()
    # Заполните заголовки (если нужно)
    headers = ["Id в таблице", "Id Телеграма", "Статус Подписки", "Label для оплаты", "Старт Подписки", "Конец Подписки"]
    sheet.append(headers)

    # Заполните данные
    for row_data in data:
        sheet.append(row_data)

    # Сохраните файл Excel
    wb.save('users.xlsx')










