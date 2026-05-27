"""Ventana de estado simple para la API local.

Uso: ejecutar desde el root del proyecto con el venv de python:

    .venv\Scripts\python.exe scripts\verify_health.py

Intentará obtener la informacion de salud de http://localhost:8000/health durante 60 segundos.
Saldrá con codigo 0 si la solicitud es exitosa, o con un codigo distinto a 0 si falla.
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
