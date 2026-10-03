import socket
import time
import subprocess
import platform

def check_tcp(host, port, timeout=3):
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, round((time.time() - start) * 1000, 1)
    except OSError:
        return False, None

def check_dns(host):
    start = time.time()
    try:
        socket.gethostbyname(host)
        return True, round((time.time() - start) * 1000, 1)
    except socket.gaierror:
        return False, None

def check_ping(host):
    flag = "-n" if platform.system() == "Windows" else "-c"
    try:
        result = subprocess.run(["ping", flag, "1", host], 
                                capture_output=True, timeout=5)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def check_host(host, port):
    dns_ok, dns_ms = check_dns(host)
    tcp_ok, tcp_ms = check_tcp(host, port)
    ping_ok = check_ping(host)
    return {"host": host, "port": port, 
            "dns_ok": dns_ok, "dns_ms": dns_ms, 
            "tcp_ok": tcp_ok, "tcp_ms": tcp_ms, 
            "ping_ok": ping_ok}

#Threading

from concurrent.futures import ThreadPoolExecutor

def load_hosts(path="hosts.txt"):
    hosts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                host, port = line.split(",")
                hosts.append((host, int(port)))
    return hosts

def check_all(hosts):
    with ThreadPoolExecutor(max_workers=10) as pool:
        return list(pool.map(lambda h: check_host(*h), hosts))

#SQL Storage 

import sqlite3
from datetime import datetime

DB = "monitor.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                host TEXT,
                port INTEGER,
                dns_ok INTEGER,
                dns_ms REAL,
                tcp_ok INTEGER,
                tcp_ms REAL,
                ping_ok INTEGER
            )
        """)

def save_results(results):
    ts = datetime.now().isoformat(timespec="seconds")
    rows = [(ts, r["host"], r["port"], int(r["dns_ok"]), r["dns_ms"],
             int(r["tcp_ok"]), r["tcp_ms"], int(r["ping_ok"]))
             for r in results]
    with sqlite3.connect(DB) as conn:
        conn.executemany(
            "INSERT INTO checks (ts, host, port, dns_ok, dns_ms, tcp_ok, tcp_ms, ping_ok)"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)


if __name__ == "__main__":
    init_db()
    start = time.time()
    results = check_all(load_hosts())
    save_results(results)
    for r in results:
        print(r)
    print(f"Checked {len(results)} hosts in {round(time.time() - start, 1)}s, saved to {DB}")


