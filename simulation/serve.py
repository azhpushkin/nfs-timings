import json
import sys
from http import server

import psycopg2

request_id = sys.argv[1]
print("Serving request", request_id)

conn = psycopg2.connect(dbname='nfs')

with conn:
    with conn.cursor() as cursor:
        cursor.execute(
            'select status, response_json from requests where id = %s',
            [request_id, ]
        )
        status, response = cursor.fetchone()

if status != 200:
    raise RuntimeError(f'Status is {status}')

class CustomHTTPHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        print(self.path, self.path == "/getmaininfo.json")
        print(response)
        if self.path == "/getmaininfo.json":

            data = json.dumps(response)
            self.send_response(code=200)
            self.send_header(keyword="Content-type", value="application/json")
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))
        else:
            return super().do_GET()


if __name__ == "__main__":
    address = ("", 7000)
    httpd = server.HTTPServer(address, CustomHTTPHandler)
    print("Start serving on localhost:7000")
    httpd.serve_forever()
