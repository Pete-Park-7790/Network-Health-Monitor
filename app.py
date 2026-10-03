import sqlite3
from flask import Flask, render_template, redirect
from monitor import init_db, load_hosts, check_all, save_results, DB

app = Flask(__name__)

QUERY = """
SELECT s.host, s.port, s.checks, s.avg_ms, s.uptime_pct,
    l.tcp_ok, l.ping_ok, l.dns_ok, l.ts
FROM (
    SELECT host, port,
        COUNT(*) AS checks,
        ROUND(AVG(tcp_ms), 1) AS avg_ms,
        ROUND(100.0 * SUM(tcp_ok) / COUNT(*), 1) AS uptime_pct,
        MAX(id) AS last_id
    FROM checks GROUP BY host, port
) s
JOIN checks l on l.id = s.last_id
ORDER BY s.host 
"""

@app.route("/")
def index():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(QUERY).fetchall()
    return render_template("index.html", rows=rows)

@app.route("/run")
def run_checks():
    save_results(check_all(load_hosts()))
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

