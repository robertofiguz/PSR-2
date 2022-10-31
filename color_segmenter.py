#!/usr/bin/python3
import cv2 
import copy
import colorama
import numpy
import json
from functools import partial 


def trackbar(_, window, limits):
    
    min=[0, 0, 0]
    max=[0, 0, 0]

    min[0] = cv2.getTrackbarPos("min B", window)
    max[0] = cv2.getTrackbarPos("max B", window)
    min[1] = cv2.getTrackbarPos("min G", window)
    max[1] = cv2.getTrackbarPos("max G", window)
    min[2] = cv2.getTrackbarPos("min R", window)
    max[2] = cv2.getTrackbarPos("max R", window)

    [limits["limits"]["B"]["min"], limits["limits"]["G"]["min"], limits["limits"]["R"]["min"]] = min
    [limits["limits"]["B"]["max"], limits["limits"]["G"]["max"], limits["limits"]['R']["max"]] = max
    
    return limits, min, max

def main():
    capture = cv2.VideoCapture(0)

    cv2.namedWindow("original_window")
    cv2.namedWindow("segmented_window")

    original_limits= {'limits': {'B': {'max': 255, 'min': 0},
                                 'G': {'max': 255, 'min': 0},
                                 'R': {'max': 255, 'min': 0}}}
  
    limits=copy.deepcopy(original_limits)
    
    file_name = "limits.json"

    with open(file_name,"w") as file_handle:
        json.dump(limits,file_handle)


    trackbar_partial = partial(trackbar, window ="segmented_window", limits=limits)

    #-------#Adição das trackbars#-----------#
    cv2.createTrackbar('min B',"segmented_window", 100, 255, trackbar_partial)
    cv2.createTrackbar('max B',"segmented_window", 255, 255, trackbar_partial)
    cv2.createTrackbar('min G',"segmented_window", 100, 255, trackbar_partial)
    cv2.createTrackbar('max G',"segmented_window", 255, 255, trackbar_partial)
    cv2.createTrackbar('min R',"segmented_window", 100, 255, trackbar_partial)
    cv2.createTrackbar('max R',"segmented_window", 255, 255, trackbar_partial)
 
    w = False

    #------Captura de Video------#
    while True:
        _, frame = capture.read()
        frame_gui = copy.deepcopy(frame)

    #------Display Video----#

        cv2.imshow("original_window",frame_gui)

    #----Update dos valores das trackbars -----#
        limits , min , max = trackbar_partial(0)

    #-------Deteção das cores e resultado------------#
        mask_frame = cv2.inRange( frame_gui , numpy.array(min) , numpy.array(max))
        cv2.imshow("segmented_window", mask_frame)
        
        exitkey=cv2.waitKey(10)

        
    #----Tecla para sair e salvar-----------#
        if exitkey == ord("q"):
            print(" \nYou pressed" +'"q"'+" to leave")
            if not w:
                print('You didn\'t save any values')
                print('\nThe original values for limits were saved:')
                print(original_limits)

            elif w:
                print('\nThe vales of the segmentation limits saved:')
                print(limits)
            break

        elif exitkey == ord("w"):
            w = True

            with open(file_name,"w") as file_handle:
                print('** writing dictionary "limits" to file ' + file_name + ' **')
                json.dump(limits, file_handle)

if __name__ == '__main__':
    main()
