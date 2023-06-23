import sys

import pandas as pd


def transform_csv_into_parquet(filename: str):
    df_raw = pd.read_csv(f'recordings/{filename}.csv')
    df = (
        df_raw.sort_values('id')
        .reset_index(drop=True)
        .reset_index()
        .drop(columns=['id'])
    )
    df.to_parquet(f'recordings/{filename}.parquet', compression='gzip')


def check_recording(filename: str):
    pd.read_parquet(f'recordings/{filename}.parquet')
    print('Recording is healthy')


def load_parquet():
    import json

    import pandas as pd
    from django.utils import timezone

    from stats.models import *
    from stats.processing import process_json

    df = pd.read_parquet('recordings/mini_06_may_2023.parquet')

    for _, r in df.iterrows():
        data = r.to_dict()
        board_request = BoardRequest.objects.create(
            url='http://example.com',
            race_id=2,
            created_at=timezone.now(),
            status=data['status'],
            response=data['response'],
            response_json=json.loads(data['response_json']),
            is_processed=False,
        )
        if data['status'] == 200:
            process_json(board_request)


ACTIONS = {
    'transform': transform_csv_into_parquet,
    'check': check_recording,
}

if __name__ == '__main__':
    action = sys.argv[1]
    filename = sys.argv[2]

    if action_func := ACTIONS.get(action):
        action_func(filename)
    else:
        raise ValueError(
            f'Unknown action {action}. Allowed values are {list(ACTIONS.keys())}'
        )
