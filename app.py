import os
import re
import sqlite3
import time
from datetime import datetime

import requests

DB = os.environ.get("DB_CONN", "gpings.db")
con = sqlite3.connect(DB)
session = requests.Session()

res = con.execute("select name from sqlite_master where name = 'gpings'")
tables = res.fetchone()
if not tables or "gpings" not in tables:
    con.execute("create table gpings(scan_time, ipaddress, status, name, location)")

error = 0
while error < 10:
    try:
        timestamp = datetime.now().isoformat()
        result = session.get("http://syswatch.science.mq.edu.au/gping/include.html")
        lines = result.text.split("\n")
        results = []
        for line in lines:
            m = re.match(
                r'<div id="(.*?)" class="indicator (.*?)"><span class="tooltiptext">.*?<br>(.*?)<br>(.*?)</span></div>',
                line,
            )
            if m and m.group(2) != "grey":
                results.append((timestamp, m.group(1), m.group(2), m.group(3), m.group(4)))

        con.executemany(
            f"insert into gpings(scan_time, ipaddress, status, name, location) values(?, ?, ?, ?, ?)", results
        )
        con.commit()

        print(f"{timestamp} - [{len(results)}] pings harvested")
        time.sleep(20)
        error = 0
    except RuntimeError as err:
        error += 1
        print(f"{timestamp} - [error] {err}")
