import sqlite3
from datetime import datetime, timedelta


class DataBase:

    def __init__(self):
        self.connect = sqlite3.connect('money_bot.db')
        self.cursor = self.connect.cursor()

    async def add_user(self, user_id):
        with self.connect:
            return self.cursor.execute("""INSERT INTO users (user_id) VALUES (?)""", [user_id])

    async def update_label_bought(self, label_month, label_week, user_id, bought):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET label_for_month=(?), label_for_week=(?), bought=(?) WHERE user_id=(?)""",
                                       [label_month, label_week, bought,  user_id])

    async def update_label(self, label_month, label_week, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET label_for_month=(?), label_for_week=(?) WHERE user_id=(?)""",
                                       [label_month, label_week,  user_id,])


    async def get_bought(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT bought FROM users WHERE user_id=(?)""", [user_id]).fetchone()[0]

    async def get_payment_status(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT bought, label_for_month, label_for_week, last_day FROM users WHERE user_id=(?)""",
                                       [user_id]).fetchall()

    async def update_payment_status(self, status,  user_id, days):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET bought=(?), start_podpiska=(?), end_podpiska=(?) WHERE user_id=(?)""",
                                       [status, datetime.now(), datetime.now() + timedelta(days=days), user_id])

    async def get_subscribe_status(self):
        with self.connect:
            return self.cursor.execute("""SELECT user_id, start_podpiska, end_podpiska, bought FROM users""").fetchall()

    async def delete_user(self, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE FROM users WHERE user_id = (?)""", [user_id])

    async def get_label_month(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT label_for_month FROM users WHERE user_id = (?)""", [user_id]).fetchone()[0]

    async def get_label_week(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT label_for_week FROM users WHERE user_id = (?)""", [user_id]).fetchone()[0]

    async def get_timer(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT timer FROM users WHERE user_id=(?)""", [user_id]).fetchone()[0]

    async def set_timer(self, timer):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET timer=(?)""", [timer])

    async def get_users(self):
        with self.connect:
            return self.cursor.execute("""SELECT id, user_id, bought, start_podpiska, end_podpiska FROM users""").fetchall()

    async def get_cost(self):
        with self.connect:
            return self.cursor.execute("""SELECT cost FROM cost""").fetchone()[0]

    async def set_cost(self, cost):
        with self.connect:
            return self.cursor.execute("""UPDATE cost SET cost=(?)""", [cost])

    async def set_last_day(self, last_day, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET last_day=(?) WHERE user_id=(?)""", [last_day, user_id])
    async def get_last_day(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT last_day FROM users WHERE user_id=(?)""", [user_id]).fetchone()[0]

    async def set_new_podpiska_end(self, user_id, days):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET end_podpiska=(?) WHERE user_id=(?)""",
                                       [datetime.now() + timedelta(days=days), user_id])

    async def set_sale_cost_month(self, cost):
        with self.connect:
            return self.cursor.execute("""UPDATE cost SET cost_sale=(?)""", [cost])


    async def set_sale_cost_week(self, cost):
        with self.connect:
            return self.cursor.execute("""UPDATE cost SET cost_week_sale=(?)""", [cost])


    async def set_cost_week(self, cost):
        with self.connect:
            return self.cursor.execute("""UPDATE cost SET cost_week=(?)""", [cost])

    async def get_cost_week(self):
        with self.connect:
            return self.cursor.execute("""SELECT cost_week FROM cost""").fetchone()[0]

    async def get_cost_sale_week(self):
        with self.connect:
            return self.cursor.execute("""SELECT cost_week_sale FROM cost""").fetchone()[0]

    async def get_cost_sale(self):
        with self.connect:
            return self.cursor.execute("""SELECT cost_sale FROM cost""").fetchone()[0]

