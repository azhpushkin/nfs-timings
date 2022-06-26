from http import server
import json
import pathlib
import random

SAMPLES_PATH = pathlib.Path(__file__).parent.resolve().parent / 'samples'
print('Loading samples from ', SAMPLES_PATH)

SAMPLES = []
for s in SAMPLES_PATH.iterdir():
    contents = json.load(open(s))
    
    SAMPLES.append((s.name, contents))



class CustomHTTPHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        print(self.path, self.path == '/getmaininfo.json')
        if self.path == '/getmaininfo.json':
            data = json.dumps(random.choice(SAMPLES)[1])
            self.send_response(code=200)
            self.send_header(keyword='Content-type', value='application/json')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))
        else:
            return super().do_GET()


if __name__ == '__main__':
    address = ('', 7000)
    httpd = server.HTTPServer(address, CustomHTTPHandler)
    print('Start serving on localhost:7000')
    httpd.serve_forever()
