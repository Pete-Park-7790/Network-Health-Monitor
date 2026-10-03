-- Uptime and latency summary per host and port
SELECT host, port,
       COUNT(*) AS checks,
       ROUND(AVG(tcp_ms), 1) AS avg_ms,
       ROUND(100.0 * SUM(tcp_ok) / COUNT(*), 1) AS uptime_pct
FROM checks
GROUP BY host, port;

-- Latest 20 checks
SELECT ts, host, port, dns_ok, tcp_ok, tcp_ms, ping_ok
FROM checks
ORDER BY id DESC
LIMIT 20;

-- Hosts that have ever been DOWN
SELECT host, port, COUNT(*) AS failed_checks
FROM checks
WHERE tcp_ok = 0
GROUP BY host, port;
