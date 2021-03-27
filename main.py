from imutils import face_utils
import numpy as np
import cv2
import dlib
import imutils
import argparse

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

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

frame = cv2.imread(args["image"])

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

	if avg < 0.2:
		print("Eyes closed.")
	else:
		print("Eyes open.")

	for (x, y) in shape[36:48]:
		cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

	cv2.imwrite("output.jpg", frame)

cv2.destroyAllWindows()
