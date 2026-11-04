import sqlite3
from datetime import datetime

DB_FILE = "hospital.db"


def connect():
    return sqlite3.connect(DB_FILE)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    con = connect()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS ambulances (
        ambulance_id TEXT PRIMARY KEY,
        driver TEXT NOT NULL,
        status TEXT DEFAULT 'IDLE')""")
    cur.execute("""CREATE TABLE IF NOT EXISTS transits (
        transit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ambulance_id TEXT, source TEXT, hospital TEXT,
        route TEXT, start_time TEXT, end_time TEXT, status TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS signal_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        transit_id INTEGER, junction TEXT, action TEXT, time TEXT)""")
    seed = [
        ("AMB01", "Anil Kumar"),
        ("AMB02", "Rahul Nair"),
        ("AMB03", "Fathima Beevi"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO ambulances (ambulance_id, driver) VALUES (?, ?)", seed
    )
    con.commit()
    con.close()


def get_ambulance(ambulance_id):
    con = connect()
    row = con.execute(
        "SELECT ambulance_id, driver, status FROM ambulances WHERE ambulance_id = ?",
        (ambulance_id,),
    ).fetchone()
    con.close()
    return row  # tuple or None


def set_ambulance_status(ambulance_id, status):
    con = connect()
    con.execute(
        "UPDATE ambulances SET status = ? WHERE ambulance_id = ?",
        (status, ambulance_id),
    )
    con.commit()
    con.close()


def create_transit(ambulance_id, source, hospital, route):
    con = connect()
    cur = con.execute(
        "INSERT INTO transits (ambulance_id, source, hospital, route, start_time, status) "
        "VALUES (?, ?, ?, ?, ?, 'ACTIVE')",
        (ambulance_id, source, hospital, "->".join(route), now()),
    )
    con.commit()
    transit_id = cur.lastrowid
    con.close()
    return transit_id


def close_transit(transit_id):
    con = connect()
    con.execute(
        "UPDATE transits SET status = 'COMPLETED', end_time = ? WHERE transit_id = ?",
        (now(), transit_id),
    )
    con.commit()
    con.close()


def log_signal(transit_id, junction, action):
    con = connect()
    con.execute(
        "INSERT INTO signal_log (transit_id, junction, action, time) VALUES (?, ?, ?, ?)",
        (transit_id, junction, action, now()),
    )
    con.commit()
    con.close()


def get_signal_log(transit_id):
    con = connect()
    rows = con.execute(
        "SELECT junction, action, time FROM signal_log WHERE transit_id = ? ORDER BY log_id",
        (transit_id,),
    ).fetchall()
    con.close()
    return rows


def get_transits():
    con = connect()
    rows = con.execute(
        "SELECT transit_id, ambulance_id, source, hospital, route, status FROM transits"
    ).fetchall()
    con.close()
    return rows


if __name__ == "__main__":
    init_db()
    print("Transit history")
    for t in get_transits():
        print(t)
