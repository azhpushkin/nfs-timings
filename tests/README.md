### Test file notes

Tests are run over bg_13_may_q1h.parquet file. Timeline of requests is:

* 22-105: Q1, board is not refreshed until Q2
* 197-280: Q2, board is not refreshed, but names are still filled after the end
* 679: start of the race, mode is not switched immediately
* 690: race mode switched to BG, already 1 lap passed (check if this affects?)
