#!/usr/bin/python3
import cv2
import copy
import colorama
import numpy
import json
import colorama
from functools import partial


def trackbar(_,window,limits):
    
    min=[0,0,0]
    max=[0,0,0]

    min[0] = cv2.getTrackbarPos("min B", window)
    max[0] = cv2.getTrackbarPos("max B", window)
    min[1] = cv2.getTrackbarPos("min G", window)
    max[1] = cv2.getTrackbarPos("max G", window)
    min[2] = cv2.getTrackbarPos("min R", window)
    max[2] = cv2.getTrackbarPos("max R", window)

    [limits["limits"]["B"]["min"], limits["limits"]["G"]["min"], limits["limits"]["R"]["min"]] = min
    [limits["limits"]["B"]["max"], limits["limits"]["G"]["max"], limits["limits"]['R']["max"]] = max

def main():
    capture = cv2.VideoCapture(0)
    if capture.isOpened():
        print("Capturing video from webcam")
    else:
        print("Camera is not working")
    
        #original_window = "Original"
        #segmented_window = "Segmented"
    cv2.namedWindow("original_window",cv2.WINDOW_NORMAL)
    cv2.namedWindow("segmented_window",cv2.WINDOW_NORMAL)
    original_limits= {'limits': {'B': {'max': 100, 'min':50},
                                'G': {'max': 100, 'min': 50},
                                'R': {'max': 255, 'min': 0}}}

    limits=copy.deepcopy(original_limits)
    trackbar_partial = partial(trackbar, window ="segmented_window", limits=limits)
    cv2.createTrackbar('min B',"segmented_window", 0, 255, trackbar_partial)
    cv2.createTrackbar('max B',"segmented_window", 255, 255, trackbar_partial)
    cv2.createTrackbar('min G',"segmented_window", 0, 255, trackbar_partial)
    cv2.createTrackbar('max G',"segmented_window", 255, 255, trackbar_partial)
    cv2.createTrackbar('min R',"segmented_window", 0, 255, trackbar_partial)
    cv2.createTrackbar('max R',"segmented_window", 255, 255, trackbar_partial)

    while True:
        ret, frame = capture.read()

        file_name = "limits.json"

        with open(file_name,"w") as file_handle:
            json.dump(str(limits),file_handle)




    #-------#Adição das trackbars#-----------#
        
       
        segmented_frame = cv2.inRange(
            frame, 
        (limits["limits"]["B"]["min"], 
        limits["limits"]["G"]["min"], 
        limits["limits"]["R"]["min"]), 

        (limits["limits"]["B"]["max"], 
        limits["limits"]["G"]["max"], 
        limits["limits"]["R"]["max"])
        )

        cv2.imshow('segmented_window', segmented_frame)
        cv2.imshow('original_window', frame)
        if cv2.waitKey(1) & 0xff == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()