"""Simple healthcheck poller for the local API.

Usage: run this from the project root with the venv python:

    .venv\Scripts\python.exe scripts\verify_health.py

It will try for up to 60 seconds to GET http://localhost:8000/health
and exit 0 on success, non-zero on failure.
"""
import sys
import time
import urllib.request

URL = "http://localhost:8000/health"
TIMEOUT = 60
INTERVAL = 2

def check():
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(URL, timeout=5) as r:
                code = r.getcode()
                body = r.read().decode(errors="ignore")
                print("HTTP", code)
                print(body)
                if code == 200:
                    return 0
        except Exception as e:
            print("waiting for service...", str(e))
        time.sleep(INTERVAL)
    print(f"Service did not respond OK within {TIMEOUT}s")
    return 2

if __name__ == "__main__":
    sys.exit(check())
