from typing import List

from processing.detection import LapDetector
from processing.response_type import NFSResponseDict


def test_check_simple_10_laps(bg_recording: List[NFSResponseDict]):
    # 679 - 764 cover start of the race and first 10 laps of it
    all_results = []

    detector = LapDetector()
    for response in bg_recording[675:764]:
        laps = detector.process_race_info(response.onTablo)
        all_results.extend(laps)

    expected_teams_data = {
        6: [47.91, 43.34, 43.04, 43.19, 42.99, 42.88, 42.94, 42.90, 43.23, 42.92],
        9: [48.19, 44.34, 43.58, 43.62, 44.37, 43.33, 44.32, 43.66, 43.68, 43.23],
        10: [47.07, 46.01, 43.80, 43.67, 43.76, 44.21, 43.57, 43.30, 43.83, 43.70],
        # team 11 only finished 9 laps by then
        11: [48.55, 46.01, 45.77, 45.96, 46.45, 45.87, 44.96, 44.77, 45.00],
    }

    for team, team_laps in expected_teams_data.items():
        team_results = [entry for entry in all_results if entry.number == team]
        assert [
            entry.lastLap.to_float() for entry in team_results
        ] == team_laps, f'Bad laps for team {team}'
        assert [entry.lapCount for entry in team_results] == list(
            range(1, len(team_laps) + 1)
        )
