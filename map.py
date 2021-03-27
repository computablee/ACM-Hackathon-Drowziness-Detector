import _thread
import asyncio
from http.server import HTTPServer
from socketserver import BaseRequestHandler
import websockets
import requests
import os
import json


class Serv(BaseRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = "/index.html"
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, "utf-8"))


def serve_server():
    httpd = HTTPServer(("localhost", 8080), Serv)
    httpd.serve_forever()


async def handle_socket(websocket, path):
    while True:
        latlon = await websocket.recv()
        api_key = os.environ["MAP_API_KEY"]
        response = requests.get(
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={api_key}&location={latlon}&radius=2000&type=cafe")
        if (response.status_code >= 400):
            print("API Error")
        else:
            await websocket.send(json.dumps(response.json()))

start_server = websockets.serve(handle_socket, "localhost", 8081)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


_thread.start_new_thread(serve_server, ())
