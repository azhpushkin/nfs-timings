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
