#!/usr/bin/env python3

#######################################################################################
#  Trabalho Prático 2 - PSR Augmented Reality Paint 
#       A funcionalidade principal deste programa é permitir ao utilizador desenhar 
#       numa imagem movendo um objeto colorido em frente à câmara do portátil.
# 
#  Elaborado por:
#       João Nogueiro 111807
#       Fransico Lopes 98511
#       Roberto Figueiredo 116147
#######################################################################################

################## Library ###################
import argparse
import cv2
import numpy as np
import json
from copy import deepcopy
from time import ctime
from pprint import pprint
##############################################

def paint(options):
    if (len(options['xs'])>2) & (len(options['ys'])>2):#Para garantir que as litas têm pelo menos dois elementos
        x1 = options['xs'][-2]
        y1 = options['ys'][-2]
        x2 = options['xs'][-1]
        y2 = options['ys'][-1]
        cv2.line(options['paint_wind'], (x1, y1), (x2, y2), options['pencil_color'], options['pencil_size'])

def parameters(key, options):
    if key == ord('r'): #para mudar a cor do lápis para vermelho
        print('Change pencil color to red')
        options['pencil_color'] = (0,0,250)

    if key == ord('g'): #mudar a cor do lápis para verde
        print('Change pencil color to green')
        options['pencil_color'] = (0,255,0)

    if key == ord('b'): #mudar a cor do lápis para azul
        print('Change pencil color to blue')
        options['pencil_color'] = (255,0,0)

    if key == ord('+'): #aumentar o tamanho do lápis
        options['pencil_size'] +=1
        print('Increase pencil size:', options['pencil_size'])

    if key == ord('-'): #diminuir o tamanho do lápis
        if options['pencil_size'] !=1: #para evitar termos o tamalho do pincel a 0
            options['pencil_size'] -=1
            print('Decrease pencil, size:', options['pencil_size'])

    if key == ord('c'): #limpar a tela
        print('Clear the screen')
        options['paint_wind'].fill(255)
        options['xs']=[]
        options['ys']=[]

    if key == ord('w'): #gravar a tela atual
        print('Save image')
        cv2.imwrite('drawing_'+ctime().replace(' ','_')+'.png', options['paint_wind'])        

def findObject(img, mask, options):
    mask_contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(mask_contours) != 0:
        for mask_contour in mask_contours:
            if cv2.contourArea(mask_contour) > 1000: #blindagem para não captar objetos mais pequenos que 10000 pixeis
                x, y, w, h = cv2.boundingRect(mask_contour)
                cv2.circle(img, (int(x+w/2), int(y+h/2)), 5, (0, 0, 255), -1) #cv2.circle(image, center_coordinates, radius, color, thickness)
                options['xs'].append(int(x+w/2))
                options['ys'].append(int(y+h/2))


def compare_images(img1, img2):
    #check similarity between images
    s = cv2.subtract(img2, img1)
    #count black pixels in image s
    s = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
    num_black_pix = cv2.countNonZero(s)  
    print('Number of black pixels:', num_black_pix)
    total_pixels = s.shape[0]*s.shape[1]
    percentage_correct = 100-((num_black_pix*100)/total_pixels)
    return percentage_correct

def main():
    mode = "regular"
    drawing = False

    parser = argparse.ArgumentParser(description='Definition of test mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    parser.add_argument('-usp', '--use_shake_prevention', type=str, required=False, help='Runs the snake prevention code.')
    parser.add_argument('-f', '--use_feed',  required=False, help='Uses the camera feed as canvas.')
    parser.add_argument('-d', '--drawing', required=False, help='Use a drawing as canvas.')
    args = vars(parser.parse_args())

    #Abre o ficheiro json
    #E retira os valores de max e min definidos no color_segmenter.py e coloca-os numa lista
    min=[]
    max=[]

    f=open(args['json'])
    data=json.load(f)
    pprint(data)
    for i in data['limits'].values():
        min.append(i.get('min'))
        max.append(i.get('max'))
    f.close() #fechar o ficheiro

    lower = np.array(min)
    upper = np.array(max)

   
    cap = cv2.VideoCapture(0)
    _, img = cap.read()
    paint_w = np.zeros((img.shape[0], img.shape[1],3),dtype = np.uint8) 
    paint_w.fill(255) #correponde à cor de background, 255 corresponde à cor branca
    options = {'paint_wind':  paint_w,'xs': [], 'ys':[], 'pencil_color':(0,255,0), 'pencil_size':3}  
    
    if args['drawing']:
        image_color = cv2.imread('color.png', 1)
        image_bw = cv2.imread('bw.png',1)
        image_color = cv2.resize(image_color, (img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA)
        image_bw = cv2.resize(image_bw, (img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA)
        options['paint_wind'] = image_bw
        drawing = True
        initial_percentage = compare_images(image_color, image_bw)

    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Original', img.shape[1], img.shape[0])
    cv2.namedWindow('Mask',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Mask', img.shape[1], img.shape[0])
    cv2.namedWindow('Paint',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Paint', img.shape[1], img.shape[0])

    def paint_circle(window, center, coordinates):
        #draw an ellipse
        cv2.ellipse(window, center, (int(coordinates[1]/2),int(coordinates[0]/2)),0,0,360,options['pencil_color'], options['pencil_size'])
    def paint_rectangle(window, center, radius):
        #draw an ellipse
        cv2.rectangle(window, center, radius, options['pencil_color'], options['pencil_size'])
    key_presses = []
    while True:
        _, img = cap.read()
        key_presses = key_presses[-2:]
        mask = cv2.inRange(img, lower, upper)
        findObject(img, mask, options)
        press_key = cv2.waitKey(30)
        key_presses.append(press_key)
        if len(set(key_presses)) == 1:
            key = key_presses[0]
        if key == ord('o'):
            if mode != 'circle':   
                center = (options['xs'][-1], options['ys'][-1])
            mode = 'circle'
        elif key == ord('t'):
            if mode != 'rectangle':
                center = (options['xs'][-1], options['ys'][-1])
            mode = 'rectangle'
        elif press_key == ord('q'): #sai do programa 
            if drawing:
                percentage = compare_images(image_color, options['paint_wind'])
                percentage -= initial_percentage
                print("Percentage of the drawing correct: {0:.0f}%".format(percentage))
            break
        else:
            mode = "regular"
            parameters(press_key, options)

        if mode != "regular":
            try:
                options['paint_wind'] = image_copy   
            except UnboundLocalError:
                pass
            print("reset")

        if mode == 'regular':
            image_copy = deepcopy(options['paint_wind'])
            paint(options)
        elif mode == 'circle':
            image_copy = deepcopy(options['paint_wind'])
            paint_circle(options['paint_wind'], center, (options['xs'][-1], options['ys'][-1]))
        elif mode == 'rectangle':
            image_copy = deepcopy(options['paint_wind'])
            paint_rectangle(options['paint_wind'], center, (options['xs'][-1], options['ys'][-1]))    
        
        cv2.imshow('Original', img)
        cv2.imshow('Mask', mask)
        if args['use_feed']:
            feed =  cv2.bitwise_and(img, options['paint_wind'])
            cv2.imshow('Paint',feed)
        else:
            cv2.imshow('Paint', options['paint_wind'])
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()