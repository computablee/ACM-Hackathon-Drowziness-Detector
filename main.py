import _thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from imutils import face_utils
import numpy as np
import cv2
import dlib
import imutils
import argparse
import asyncio
import websockets
from imageio import imread
import io
import base64

class Serv(BaseHTTPRequestHandler):
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

def mag(vec):
	return np.sqrt(vec[0] * vec[0] + vec[1] * vec[1])

def sub(vec1, vec2):
	return (vec1[0] - vec2[0], vec1[1] - vec2[1])

def rect_to_bb(rect):
	x = rect.left()
	y = rect.top()
	w = rect.right() - x
	h = rect.bottom() - y

	return (x, y, w, h)

def shape_to_np(shape, dtype="int"):
	coords = np.zeros((68, 2), dtype=dtype)

	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)

	return coords

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True, help="path to facial landmark predictor")
ap.add_argument("-i", "--image", required=True, help="path to input image")

args = vars(ap.parse_args())

_thread.start_new_thread(serve_server, ())

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

async def handle_socket(websocket, path):
	while True:
		data = await websocket.recv()
		padding = len(data) % 4;
		data += '=' * (4 - padding)
		file_bytes = np.frombuffer(base64.b64decode(data), dtype=np.uint8)
		frame = cv2.imdecode(file_bytes, flags=cv2.IMREAD_UNCHANGED)

		frame = imutils.resize(frame, width=500)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		rects = detector(gray, 1)

		for (i, rect) in enumerate(rects):
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)

			print(shape[36], shape[37], shape[38], shape[39], shape[40], shape[41])
			print(shape[42], shape[43], shape[44], shape[45], shape[46], shape[47])

			eye1 = (mag(sub(shape[37], shape[41])) + mag(sub(shape[38], shape[40]))) / (2 * mag(sub(shape[36], shape[39])))
			eye2 = (mag(sub(shape[43], shape[47])) + mag(sub(shape[44], shape[46]))) / (2 * mag(sub(shape[42], shape[45])))

			avg = (eye1 + eye2)/2

			print(avg)

			if avg < 0.18:
				await websocket.send("::closed")
			else:
				await websocket.send("::open")

start_server = websockets.serve(handle_socket, "localhost", 8081)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
