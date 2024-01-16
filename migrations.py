import sqlite3

conn = sqlite3.connect('money_bot.db')

cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, 
             user_id INT UNIQUE, 
             bought BOOLEAN DEFAULT 0, 
             label_for_month TEXT DEFAULT "1", 
             label_for_week TEXT DEFAULT "1", 
             start_podpiska TIMESTAMP, 
             end_podpiska TIMESTAMP, 
             last_day BOOLEAN DEFAULT 0)''')

cursor.execute("""CREATE TABLE IF NOT EXISTS cost (
    cost INT,
    cost_week INT,
    cost_sale INT,
    cost_week_sale INT
)""")

cursor.execute("""INSERT INTO  cost (cost, cost_week, cost_sale, cost_week_sale) VALUES (?, ?, ?, ?)""",
               [100, 100, 100, 100])

conn.commit()
conn.close()
