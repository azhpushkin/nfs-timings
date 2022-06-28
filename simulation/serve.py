from http import server
import json
import pathlib
import random
import sys


SAMPLES_PATH = pathlib.Path(__file__).parent.resolve().parent / "samples"
print("Loading samples from ", SAMPLES_PATH)

SAMPLES = []
for s in SAMPLES_PATH.iterdir():
    contents = json.load(open(s))

    SAMPLES.append((s.name, contents))


def get_sample():
    if len(sys.argv) > 1 and sys.argv[1] == "single":
        return json.load(open("sample2.json"))
    else:
        return random.choice(SAMPLES)[1]


class CustomHTTPHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        print(self.path, self.path == "/getmaininfo.json")
        if self.path == "/getmaininfo.json":

            data = json.dumps(get_sample())
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
