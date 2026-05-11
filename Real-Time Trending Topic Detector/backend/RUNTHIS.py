# hi run this file to start all processes after running docker compose up -d in backend directory

import subprocess
import time
import sys

scripts = [
    ("Producer", "producer.py"),
    ("Consumer", "consumer.py"),
    ("Aggregator", "aggregate.py"),
    ("FastAPI Server", "app.py")
]

processes = []

def start(name, path):
    print(f"Starting {name}...")
    if sys.platform == "win32":
        p = subprocess.Popen(
            ["python", path], 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        p = subprocess.Popen([
            "gnome-terminal", "--", "python", path
        ])
    return p

try:
    for name, path in scripts:
        p = start(name, path)
        processes.append(p)
        time.sleep(2)
        print("\n all processes started successfully \n")
        while True:
            time.sleep(1)

except KeyboardInterrupt:
    print("Shutting down...")
    for p in processes:
        p.terminate()