When is_race is true - there is
* `onTablo -> teams -> pilotName` displays pilot name, `teamName` for team name
* `onTablo -> teams -> number` displays team number
* `onTablo -> teams -> kart` to get kart number that teams is currently running
* we need to discard entries that have `teams->isOnPit` as true because idk what that tells me
* also might sense to discard times that are > 50secs because those make no sense
* `teams->bestLapOnSegment` for best lap on segment
* `teams->lastLapS2` and `teams->lastLapS1` to check sector times
* `teams->totalOnTrack` (`"00:37:18"`) is used to show time on track.
  - makes sense to discard when totalOnTrack is less than 2-3 minutes (to allow change of the kart number by admins)
  - maybe check current segment or smth
* `pilotName` and `teamName` might have unicode, gonna be careful with this


I also have **NO IDEA** how tracking of laps goes on - there is something with
transponders over there, seems to hard to figure out. Probably simply worth checking
if last lap != current lap, dont thing we will have too many issues

From the first look - sometimes there are laps that are similar to hundrends, but probably this is
not gonna happen very often. So might be fine to ignore for the start.


Probaly worth to split everything into 3 parts:
* worker that simply queues every 1 (maybe 5?) seconds
*



TODO list :
- [ ] ensure overrides work (in MINI 3 June 15->88)
- [ ] check if it is possible to have avg deviation ?
- [ ] average S1 and S2 in stint details
  - [ ] option to see either BEST sectors or TOP 10%
  - [ ] sector deviation?
- [ ] ASS RT - missing stint data, check ow to works and looks
- [ ] Find crashes in old races (Burim video, Dorokhin chat has some info)
  - [ ] Race 10 June: Bakhmatsky had 16 broken
- [ ] Find more nuances inside the races (e.g. multiple karts in same stint)
  - [ ] Chishkala in mini 3 june 3 karts
  - [ ] What if karts with 2 digits are typed one by one
  - [ ] Same for pilot name
- [ ] Add badges to the karts
  - [x] Repair badge, slowed down badge, boost up badge
  - [x] Check SVG, add buttons with SVG to kart details
  - [ ] Dialog to add badges
- [ ] Add color accents to the karts
  - [ ] Configurable?? on kart details page
- [ ] Per-user setting for filtering
- [ ] STINTS TABLE on teams details
- [ ] Performance testing
  - [ ] We do not need to re-generate all materialized views tbh
  - [ ] Performance of teams view (maybe dynamic loading? Or do everything in SQL?)
- [ ] Add RaceInfo parsed from BoardRequest (will be used for teams ordering and pits mode)
- [ ] add stint length to stint details view
- [ ] dynamic exclude team from calculations (is_active)
- [ ]
