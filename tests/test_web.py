import json
import threading
from urllib.request import Request, urlopen

from scicalc.web import create_server


def test_api_evaluate():
    server = create_server(host="127.0.0.1", port=8765)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        req = Request(
            "http://127.0.0.1:8765/api/evaluate",
            data=json.dumps({"expression": "2+2"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req) as resp:
            assert resp.status == 200
            data = json.load(resp)
        assert data["result"] == 4
    finally:
        server.shutdown()
        thread.join()
