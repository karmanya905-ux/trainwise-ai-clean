import sqlite3

def add_weight(weight):
    conn = sqlite3.connect("fitgen.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO weight_logs (weight) VALUES (?)",
        (weight,)
    )

    conn.commit()
    conn.close()


def get_weights():
    conn = sqlite3.connect("fitgen.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT log_date, weight FROM weight_logs ORDER BY log_date ASC"
    )

    rows = cursor.fetchall()
    conn.close()

    return rows