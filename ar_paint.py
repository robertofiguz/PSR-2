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
from nis import cat
from click import option
import cv2
from exceptiongroup import catch
from matplotlib import image
import numpy as np
import json
import math
from copy import deepcopy
from time import ctime, sleep
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

    if key == ord('v'): #mudar a cor do lápis para verde
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
def main():
    mode = "regular"
    parser = argparse.ArgumentParser(description='Definition of test mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    parser.add_argument('-usp', '--use_shake_prevention', type=str, required=False, help='Runs the snake prevention code.')
    parser.add_argument('-f', '--use_feed',  required=False, help='Uses the camera feed as canvas.')

    #args = vars(parser.parse_args())

    #Abre o ficheiro json
    #E retira os valores de max e min definidos no color_segmenter.py e coloca-os numa lista
    min=[]
    max=[]

    f=open('limits.json')
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
    paint_w = np.zeros((img.shape[0], img.shape[1],3),dtype = np.uint8) #criação da "tela" com o mesmo tamanho que as outras janelas->(500,700) corresponde ao tamanho, 3 é o canal e uint8 é o tipo
    paint_w.fill(255) #correponde à cor de background, 255 corresponde à cor branca
    options = {'paint_wind':  paint_w,'xs': [], 'ys':[], 'pencil_color':(0,255,0), 'pencil_size':3}  
    
    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Original', img.shape[1], img.shape[0])
    cv2.namedWindow('Mask',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Mask', img.shape[1], img.shape[0])
    cv2.namedWindow('paint',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('paint', img.shape[1], img.shape[0])

    def paint_circle(window, center, coordinates):
        #draw an ellipse
        cv2.ellipse(window, center, (int(coordinates[1]/2),int(coordinates[0]/2)),0,0,360,options['pencil_color'], options['pencil_size'])
    def paint_rectangle(window, center, radius):
        #draw an ellipse
        cv2.rectangle(window, center, radius, options['pencil_color'], options['pencil_size'])
    def draw_on_feed(options):
        if (len(options['xs'])>2) & (len(options['ys'])>2):#Para garantir que as litas têm pelo menos dois elementos
            xs = iter(options['xs'])
            ys = iter(options['ys'])
            last_used = (next(xs), next(ys))
            try:
                for x, y in zip(xs, ys):
                    cv2.line(options['paint_wind'], (last_used[0], last_used[1]), (x, y), options['pencil_color'], options['pencil_size'])
                    last_used = (x, y)
            except Exception:
                pass
    key_presses = []
    while True:
        _, img = cap.read()
        #array with max length of 10
        key_presses = key_presses[-2:]
        #options['paint_wind'] = paint_w
        mask = cv2.inRange(img, lower, upper)
        findObject(img, mask, options)
        press_key = cv2.waitKey(30)
        key_presses.append(press_key)
        if len(set(key_presses)) == 1:
            key = key_presses[0]
        print(mode)
        if key == ord('o'):
            if mode != 'circle':   
                center = (options['xs'][-1], options['ys'][-1])
            mode = 'circle'
        elif key == ord('t'):
            if mode != 'rectangle':
                center = (options['xs'][-1], options['ys'][-1])
            mode = 'rectangle'
        elif press_key == ord('q'): #sai do programa 
            break
        else:
            mode = "regular"
            parameters(key, options)

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
        cv2.imshow('paint', options['paint_wind'])
        s = cv2.threshold(options['paint_wind'], 100,50,cv2.THRESH_BINARY)
        #s = img+options['paint_wind']
        s =  cv2.bitwise_and(img, options['paint_wind'])
        cv2.imshow('s',s)
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()