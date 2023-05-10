import pandas as pd
import sys


def transform_csv_into_parquet(filename: str):
    df_raw = pd.read_csv(f'recordings/{filename}.csv')
    df = df_raw.sort_values('id').drop(columns=['id']).reset_index()
    df.to_parquet(f'recordings/{filename}.parquet', compression='gzip')


def check_recording(filename: str):
    pd.read_parquet(f'recordings/{filename}.parquet')
    print('Recording is healthy')


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
