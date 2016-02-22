from collections import deque
import numpy as np
import argparse
import imutils
import cv2
#import picamera

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help = "path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=1,
	help="max buffer size")
args = vars(ap.parse_args())

status = " No Target"	


# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points

greenLower = np.array([75, 100, 6])
greenUpper = np.array([95, 255, 255])
#greenLower = (29, 86, 6) #29,86,6
#greenUpper = (64, 255, 255) #64,255,255

#lower blue = 110,50,50
#upper blue = 130,255,255

#reflective tape colors
#75, 100, 6
#95, 255, 255

pts = deque(maxlen=args["buffer"])

 
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	camera = cv2.VideoCapture(1)
	
	#camera = picamera.PiCamera()
 
# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])
	
	
	# keep looping
while True:
	# grab the current frame
	(grabbed, frame) = camera.read()
 
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if args.get("video") and not grabbed:
		break
 
	# resize the frame, blur it, and convert it to the HSV
	# color space
	
	
	frame = imutils.resize(frame, width=720)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	
	if len(cnts) > 0:

		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		# only proceed if the radius meets a minimum size
		if radius > 0:
			# draw a cross
			cv2.line(frame, (center[0]-25, center[1]), (center[0]+25, center[1]), (0, 255, 255), 2)
			cv2.line(frame, (center[0], center[1]-25), (center[0], center[1]+25), (0, 255, 255), 2)
			#center,
 
	# update the points queue
	pts.appendleft(center)
	
	# loop over the set of tracked points
	for i in xrange(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
	
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
 
	# show the frame to screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	
	
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	res = cv2.bitwise_and(frame, frame, mask = mask)
	
	
	cv2.imshow('mask', mask)
	cv2.imshow('res', res)
	
	print center
	if center >(0,0):
		status = "Target detect @ "+ str(center)
	
	cv2.putText(frame, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
		(0, 255, 255), 2)
	#cv2.line(frame, (center[0]-25, center[1]), (center[0]+25, center[1]), (0, 0, 255), 1)
	#cv2.line(frame, (center[0], center[1]-25), (center[0], center[1]+25), (0, 0, 255), 1)
	cv2.imshow('frame', frame)
	# q to end program
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
