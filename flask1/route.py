import flask1
from flask1 import app
from flask import render_template,Response,redirect,url_for,request,flash
import cv2
import time
import numpy as np
import handtracking_module as htm
import time
import autopy
import mouse
# import ai_mouse


def generate_frames():
    cap=cv2.VideoCapture(0)
    width, height=640,480
    cap.set(3,width)
    cap.set(4, height)

    smooth = 5
    prevx, prevy= 0,0
    currx, curry=0,0
    detector = htm.Detection(maxHands=1)
    ptime=0
    frameR = 100 # frame reduction
    screen_w, screen_h = autopy.screen.size()

    while True:
        success,frame=cap.read()
        if not success:
            break
        else:
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

                    # cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
                    prevx, prevy = currx, curry

                # both index and middle fingers are up: clicking mode
                if fingers[1]==1 and fingers[2]==1:
                    length, img, infoline = detector.findDistance(8,12,img)
                    # print(length)
                    if length<40:
                        # cv2.circle(img,(infoline[4],infoline[5]),15,(0,255,0),cv2.FILLED)
                        autopy.mouse.click()

                if fingers[1]==1 and fingers[2]==1 and fingers[3]==1:
                    length, img, infoline = detector.findDistance(8,12,img)
                    print(length)
                    if length<40:
                        # cv2.circle(img,(infoline[4],infoline[5]),15,(0,255,0),cv2.FILLED)
                        autopy.mouse.click()
            #11
            ctime = time.time()
            fps=1/(ctime-ptime)
            ptime=ctime
            # cv2.putText(
            #     img, str(int(fps)),
            #     (20,50),
            #     cv2.FONT_HERSHEY_PLAIN,
            #     3,(255,9,6), 3
            #     )

            #12
            # cv2.imshow("img",img)
            cv2.waitKey(1)

            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/active')
def active():
    return render_template("active.html")
    
@app.route('/video')
def video():
    # ai_mouse.aiFunct()
    # return render_template("index.html")
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')
       