import sqlite3

def check_sql_injection(user_input):
    # 建立一個虛擬資料庫
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin')")

    # 檢測SQL注入
    try:
        cursor.execute(f"SELECT * FROM users WHERE username = '{user_input}'")
        result = cursor.fetchall()
        print("Result:", result)
    except sqlite3.OperationalError as e:
        print("Detected SQL Injection attempt:", e)

if __name__ == "__main__":
    user_input = "admin' OR '1'='1"
    check_sql_injection(user_input)
