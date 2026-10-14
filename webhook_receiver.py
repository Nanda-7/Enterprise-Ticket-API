
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)

        print("Webhook received:", data)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"message": "Webhook received"}).encode()
        )

server = HTTPServer(("127.0.0.1", 9000), WebhookHandler)
print("Webhook listening on port 9000")
server.serve_forever()