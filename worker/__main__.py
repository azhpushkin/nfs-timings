import select
import json

from database.tables import engine

sa_connection = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
sa_connection.execute("LISTEN job_updates")


raw_connection = sa_connection.connection
while True:
    if select.select([raw_connection], [], [], 5) == ([], [], []):
        print("Timeout")
    else:
        raw_connection.poll()
        while raw_connection.notifies:
            notify = raw_connection.notifies.pop(0)
            print("Got NOTIFY:", notify.channel, json.loads(notify.payload))
