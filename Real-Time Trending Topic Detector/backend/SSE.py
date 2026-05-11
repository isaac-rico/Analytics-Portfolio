# sse stream testing and filtering
# uhh for testing and some quick analysis of data stream

from sseclient import SSEClient
import requests
import json
import time
from datetime import datetime, UTC

url = "https://stream.wikimedia.org/v2/stream/recentchange"

headers = {
    "Accept": "text/event-stream",
    "User-Agent": "isaacarnell.rico@gmail.com"
}

res = requests.get(url, stream=True, headers=headers)
client = SSEClient(res)

def get_stream(client, runtime):

    total = 0
    non_english_or_bot_count = 0
    english_non_bot_count = 0

    end_time = time.time() + runtime
    for event in client.events():
        if time.time() >= end_time:
            print(f"Stream stopped after {runtime} seconds.")
            break
        data = json.loads(event.data)
        total += 1
        if data.get("bot") or data.get("wiki") != "enwiki": # if bot or not enwiki continue, don't want non english or bots
            non_english_or_bot_count += 1
            continue

        data_filtered = {
            "id": data.get("id"),
            "title": data.get("title"),
            "user": data.get("user"),
            "wiki": data.get("wiki"),
            "server_url": data.get("server_url"),   
            "is_bot": data.get("bot"),
            "timestamp": datetime.fromtimestamp(data.get("timestamp"), tz=UTC).isoformat(), # convert unix to datetime in utc
            "time_received": datetime.fromtimestamp(int(time.time()), tz=UTC).isoformat() # same as above
        }

        english_non_bot_count += 1
        print(data_filtered)

        with open('./data.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(data_filtered) + '\n')

    print(f"Total events: {total}")
    print(f"Non-English or Bot events: {non_english_or_bot_count}")
    print(f"Non-Bot English events: {english_non_bot_count} \n Percentage of Non-bot English events: {(english_non_bot_count) / total * 100:.2f}%")
    
if __name__ == "__main__":
    print("Please enter runtime: ")
    runtime = int(input())
    get_stream(client, runtime)