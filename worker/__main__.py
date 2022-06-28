import requests
import traceback
import time

while True:
    try:
        response = requests.get('https://nfs-stats.herokuapp2.com/getmaininfo.json')
    except Exception as e:
        print(e)
    else:
        print(response)

    time.sleep(1)


