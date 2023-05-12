from http import server
import re
import json
import sys
from datetime import datetime
from tqdm import tqdm

import pandas as pd
import pathlib


# 1985 is start of the race (last request before the race)
# 40min covers first 40 minutes of the race ( requests bounds are #1980 - #2435 )
filename = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '').name
REQUESTS_FILE = pathlib.Path(__file__).parent.parent / 'recordings' / filename
assert REQUESTS_FILE.is_file(), f'{REQUESTS_FILE} must be a file'

print("Loading", REQUESTS_FILE)
df = pd.read_parquet(REQUESTS_FILE)

tqdm.pandas(desc='Parse json')
df['parsed_json'] = df['response_json'].progress_apply(json.loads)

df['parsed_created_at'] = df['created_at'].apply(datetime.fromisoformat)
# Print dataframe to see bounds of requests
print(df)


table_trs = []
for _, row in tqdm(
    df.sort_values('index').iterrows(), total=len(df), desc='Generate HTML'
):
    on_tablo_data = row['parsed_json'].get('onTablo', {})

    status_color = '' if row['status'] == 200 else ' bgcolor=gray '
    race_time_color = '' if on_tablo_data.get('totalRaceTime') else ' bgcolor=red '
    is_race_color = '' if on_tablo_data.get('isRace', False) else ' bgcolor=yellow '

    table_trs.append(
        f'''
        <tr>
            <td>{row['index']}</td>
            <td>{row['parsed_created_at'].time().replace(microsecond=0).isoformat()}</td>
            <td {status_color}>
                {row['status']}
            </td>
            <td {is_race_color}>
                {on_tablo_data.get('isRace', False)}
            </td>
            <td {race_time_color}>
                {on_tablo_data.get('totalRaceTime', 'NO TIME')}
            </td>
            <td>{row['is_processed'] == 't'}</td>
        </tr>
    '''
    )
table_trs = '\n'.join(table_trs)
TABLE_STYLE = '''
    table, th, td {
        border: 1px solid black;
        padding-left: 5px;
        padding-right: 5px;
    }
'''
HEALTH_HTML = f'''
    <!doctype html>
    <head>
    <style>
        {TABLE_STYLE}
    </style>
    </head>
    <body>
    <table>
        <tr>
            <td>Index</td>
            <td>Created at</td>
            <td>Status code</td>
            <td>Is Race</td>
            <td>Race time</td>
            <td>is processed</td>
        </tr>
        {table_trs}
    </table>
    </body>
'''


class CustomHTTPHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:

        if self.path.startswith("/getmaininfo.json"):
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
        elif self.path.startswith('/health'):
            self.send_response(code=200)
            self.end_headers()
            self.wfile.write(HEALTH_HTML.encode('utf-8'))
        else:
            return super().do_GET()


if __name__ == "__main__":
    address = ("", 7000)
    httpd = server.HTTPServer(address, CustomHTTPHandler)
    print("Start serving on localhost:7000")
    httpd.serve_forever()
