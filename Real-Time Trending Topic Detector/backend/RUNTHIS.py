# hi run this file to start all processes after running docker compose up -d in backend directory
# if this doesn't work for you, run each file in its own terminal

"""
run order:
BEFORE RUNNING PYTHON FILES: 
fill out your .env file w/ postgres credentials and kafka config
docker compose up -d (in backend directory)
pip install -r requirements.txt

and then run backend:
1. Producer.py
2. Consumer.py
3. aggregate.py
4. app.py

for frontend:
1. go to frontend directory
2. npm install -> react typescript
3. npm start
4. open localhost:5173 in browser

"""
import subprocess
import time
import sys
import os

scripts = [
    ("Producer", "producer.py"),
    ("Consumer", "consumer.py"),
    ("Aggregator", "aggregate.py"),
    ("FastAPI Server", "app.py")
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

processes = []

def start(name, path):
    print(f"Starting {name}...")
    if sys.platform == "win32":
        p = subprocess.Popen(
            ["python", path], 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        full_path = os.path.join(BASE_DIR, path)
        script = f"""
            tell application "Terminal"
                activate
                do script "python3 '{full_path}'"
            end tell
        """
        p = subprocess.Popen(
            ["osascript", "-e", script]
        )
    return p

try:
    for name, path in scripts:
        p = start(name, path)
        processes.append(p)
        time.sleep(2)
        print(f"{name} started.")
        
    print("All processes started successfully.")
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Shutting down...")
    subprocess.run(["killall", "python3"])