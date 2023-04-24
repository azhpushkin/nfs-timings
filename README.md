### NFS-timings


Used for gathering statistics during endurance karting races 
in "Need For Speed" Kyiv karting center.

![How the app looks](fe-example.png)


### Basic architecture

* Simple django app with templates to show kart stats
* Worker that queues racing API every 5 seconds and detects new laps
  via comparison to previous request
* Postgres DB to store requests and detected laps
* [Materialized view](stats/stints.py) to aggregate data per-team and per-kart to improve performance
* Services are run on basic VPS using docker-compose
* Basic django-admin setup to control whether to query API
  (do not send requests when there is no race running)
* Simulation script that runs test dataset and emulates real karting dashboard
  (used for test and debug purposes)