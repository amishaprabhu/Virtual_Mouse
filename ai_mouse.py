import cv2
import numpy as np
import handtracking_module as htm
import time
import autopy
import mouse


def aiFunct():
	cap=cv2.VideoCapture(0)
	width, height=640,480
	cap.set(3,width)
	cap.set(4, height)

	# steps:-
	'''
	1. find the hand landmarks
	2. set the tip of the index and middle fingers
	3. check which fingers are up
	4. only index finger: Moving mode
	5. convert coordinates
	6. smoothing so that flickering is not happend
	7. move the mouse
	8. both index and middle fingers are up: clicking mode
	9. find the distance between the fingers
	10. click mouse if distance short
	11. frame rate
	12. display
	'''

	smooth = 5
	prevx, prevy= 0,0
	currx, curry=0,0
	detector = htm.Detection(maxHands=1)
	ptime=0
	frameR = 100 # frame reduction
	screen_w, screen_h = autopy.screen.size()
	while True:
		#1
		success, img=cap.read()
		img = detector.findHands(img)
		lmList, bbox = detector.findPosition(img)
		#2
		if len(lmList)!=0:
			x1,y1=lmList[8][1:]
			x2,y2=lmList[12][1:]

			#3 
			fingers=detector.fingersUp()
			print(fingers)
			cv2.rectangle(img,(frameR,frameR),(width-frameR,height-frameR),(255,0,255),2)
			#4 only index finger:  moving move
			if fingers[1]==1 and fingers[2]==0 :

				#5 convert coordinates
				
				x3=np.interp(x1, (frameR,width-frameR),(0,screen_w))
				y3=np.interp(y1, (frameR,height-frameR),(0,screen_h))

				currx=prevx+(x3-prevx)/smooth
				curry=prevy+(y3-prevy)/smooth
				autopy.mouse.move(screen_w-currx,curry)
				# scale = autopy.screen.scale()
				# autopy.mouse.smooth_move((screen_w-x3)/scale,(screen_h-y3)/scale)

				cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
				prevx, prevy = currx, curry

			# both index and middle fingers are up: clicking mode
			if fingers[1]==1 and fingers[2]==1:
				length, img, infoline = detector.findDistance(8,12,img)
				# print(length)
				if length<40:
					cv2.circle(img,(infoline[4],infoline[5]),15,(0,255,0),cv2.FILLED)
					autopy.mouse.click()

			if fingers[1]==1 and fingers[2]==1 and fingers[3]==1:
				length, img, infoline = detector.findDistance(8,12,img)
				print(length)
				if length<40:
					cv2.circle(img,(infoline[4],infoline[5]),15,(0,255,0),cv2.FILLED)
					autopy.mouse.click()







		#11
		ctime = time.time()
		fps=1/(ctime-ptime)
		ptime=ctime
		cv2.putText(
	    	img, str(int(fps)),
	    	(20,50),
	    	cv2.FONT_HERSHEY_PLAIN,
	    	3,(255,9,6), 3
	    	)

	    #12
		cv2.imshow("img",img)
		cv2.waitKey(1)