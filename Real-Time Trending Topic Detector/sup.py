import time
from datetime import datetime, UTC
import json


print(time.time())
time = datetime.fromtimestamp(time.time(), tz=UTC).isoformat()

time1 = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

print(time1)

with open('time.json', 'w') as f:
    json.dump(time, f)
