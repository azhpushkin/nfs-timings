import json
from typing import List

import pandas as pd
import pytest
import pathlib

from pydantic import ValidationError

from worker.response_type import NFSResponseDict

BASE_TESTS_PATH = pathlib.Path(__file__).resolve().parent
TEST_RECORDING_PATH = BASE_TESTS_PATH / 'bg_13_may_q1h.parquet'


@pytest.fixture(scope='session')
def bg_recording() -> List[NFSResponseDict]:
    """
    Load test recording to use for tests. Decode and parse it only once per session, and half session
    before other tests if something is wrong with test responses.
    """
    recording = pd.read_parquet(TEST_RECORDING_PATH)
    responses = recording['response'].apply(
        lambda x: json.loads(eval(x).decode('utf-8'))
    )

    parsed_responses = []

    for i, response_json in enumerate(responses):
        try:
            parsed = NFSResponseDict.parse_obj(response_json)
            parsed_responses.append(parsed)
        except ValidationError as e:
            value = response_json
            for next_path in e.errors()[0]['loc']:
                value = value[next_path]
            raise ValueError(f'Failed response #{i}, bad value "{value}"')

    return parsed_responses
