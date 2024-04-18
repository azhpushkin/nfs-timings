import json
import pathlib
import re
import sys
from http import server

import pandas as pd
from tqdm import tqdm


def try_parse_json(data, row) -> dict:
    try:
        return json.loads(data.decode('utf-8').replace('\\', '\\\\'))
    except Exception:
        print('Error parsing data for row', row)
        raise


# 1985 is start of the race (last request before the race)
# 40min covers first 40 minutes of the race ( requests bounds are #1980 - #2435 )
filename = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '').name
REQUESTS_FILE = pathlib.Path(__file__).parent.parent / 'recordings' / filename
assert REQUESTS_FILE.is_file(), f'{REQUESTS_FILE} must be a file'

print("Loading", REQUESTS_FILE)
df = pd.read_parquet(REQUESTS_FILE)

tqdm.pandas(desc='Parse json')
response_json = pd.Series(index=df.index)

for i, row in tqdm(df.iterrows(), total=len(df)):
    body = eval(row['response'])
    if body == b'CONNECTION ERROR' or body.startswith(b'Access violation at address '):
        continue
    else:
        response_json[i] = try_parse_json(body, row)

df['response_json'] = response_json


class CustomHTTPHandler(server.SimpleHTTPRequestHandler):
    COUNTER = 0

    def do_GET(self) -> None:

        if self.path.startswith("/getmaininfo.json"):
            if 'use_counter' in self.path:
                req_id = self.__class__.COUNTER
                print('Return request', req_id)
                self.__class__.COUNTER = req_id + 1

                if req_id >= len(df):
                    self.send_response(
                        code=508
                    )  # custom http header instead of generic status code
                    self.end_headers()
                    self.wfile.write(b"NO CONNECTION")
                    return

            else:
                req_id_match = re.search(r"req_id=(\d+)", self.path)
                req_id = int(req_id_match.group(1)) if req_id_match else 0

            recorded_request = df.loc[req_id]

            if recorded_request["status"] == 200:
                self.send_response(code=200)
                self.send_header(keyword="Content-type", value="application/json")
                self.end_headers()
                self.wfile.write(eval(recorded_request["response"]))
            else:
                self.send_response(code=500)
                self.end_headers()
                self.wfile.write(b"CONNECTION ERROR")
                self.wfile.close()

        elif self.path.startswith('/reset'):
            self.__class__.COUNTER = 0

            self.send_response(code=200)
            self.end_headers()
            self.wfile.write(b'RESETED!')
            self.wfile.close()
        else:
            return super().do_GET()


if __name__ == "__main__":
    address = ("0.0.0.0", 7000)
    httpd = server.HTTPServer(address, CustomHTTPHandler)
    print("Start serving on localhost:7000")
    httpd.serve_forever()
