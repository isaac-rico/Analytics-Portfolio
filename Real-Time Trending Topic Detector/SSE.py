from sseclient import SSEClient
import requests
import json
from datetime import datetime, timedelta
import time

# start_time = datetime.now()
# duration = timedelta(seconds=30)

end_time = time.time() + 60  # Run for 60 seconds

url = "https://stream.wikimedia.org/v2/stream/recentchange"

headers = {
    "Accept": "text/event-stream",
    "User-Agent": "isaacarnell.rico@gmail.com"
}

res = requests.get(url, stream=True, headers=headers)
client = SSEClient(res)

total = 0
non_english_count = 0
bot_count = 0
english_non_bot = 0

for event in client.events():
    if time.time() >= end_time:
        print("Stream stopped after 60 seconds.")
        break
    data = json.loads(event.data)
    total += 1
    if data.get("wiki") != "enwiki": # if not enwiki continue, don't want non english
        non_english_count += 1
        print("non english")
        continue
    if data.get("bot"): # if bot continue, don't want bots
        bot_count += 1
        print("bot")
        continue
    if data.get("bot") == False and data.get("wiki") == "enwiki": # if bot and not enwiki continue, don't want bots or non english
        print("english non bot")
        english_non_bot += 1
        
        
print(f"Total events: {total}")
print(f"English events: {total - non_english_count} \n Percentage of English events: {(total - non_english_count) / total * 100:.2f}%")
print(f"Non-Bot events: {total - bot_count} \n Percentage of Non-Bot events: {(total - bot_count) / total * 100:.2f}%")
print(f"English non-Bot events: {english_non_bot} \n Percentage of English non-Bot events: {english_non_bot / total * 100:.2f}%")


# try:
#     while True:
#         pass
# except KeyboardInterrupt:
#     print("Stream stopped by user.")
    