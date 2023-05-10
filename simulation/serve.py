from http import server
import re
import sys

import pandas as pd
import pathlib


# 1985 is start of the race (last request before the race)
# 40min covers first 40 minutes of the race ( requests bounds are #1980 - #2435 )
filename = pathlib.Path(sys.argv[1]).name
REQUESTS_FILE = pathlib.Path(__file__).parent.parent / 'recordings' / filename

print("Loading", REQUESTS_FILE)

df = pd.read_parquet(REQUESTS_FILE)
# Print dataframe to see bounds of requests
print(df)


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

        else:
            return super().do_GET()


if __name__ == "__main__":
    address = ("", 7000)
    httpd = server.HTTPServer(address, CustomHTTPHandler)
    print("Start serving on localhost:7000")
    httpd.serve_forever()
