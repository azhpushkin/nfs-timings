import time
import requests
import json


URL = "https://nfs-stats.herokuapp.com/getmaininfo.json"


while True:
    time.sleep(1)
    t = round(time.time())
    r = requests.get(URL)
    data = r.json()
    f = open(f"new-samples/{t}.json", "w")
    json.dump(data, f)
    f.close()
    print(f"Wrote new-samples/{t}.json")
