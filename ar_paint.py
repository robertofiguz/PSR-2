#!/usr/bin/env python3

#######################################################################################
#  Trabalho Prático 2 - PSR Augmented Reality Paint 
#       A funcionalidade principal deste programa é permitir ao utilizador desenhar 
#       numa imagem movendo um objeto colorido em frente à câmara do portátil.
# 
#  Elaborado por:
#       João Nogueiro 111807
#       
#######################################################################################

################## Library ###################
import argparse
from functools import partial
import cv2
import numpy as np
import json
from pprint import pprint
from copy import deepcopy
##############################################

def paint(options):
    if len(options['xs'])!=0 & len(options['ys'])!=0:
        x1 = options['xs'][-2]
        y1 = options['ys'][-2]
        x2 = options['xs'][-1]
        y2 = options['ys'][-1]
        cv2.line(options['paint_wind'], (x1, y1), (x2, y2), options['pencil_color'], options['pencil_size'])

def parameters(key, options):
    if key == 114: #114 ascii para "r" -> para mudar a cor do lápis para vermelho
        print('Change pencil color to red')
        options['pencil_color'] = (0,0,250)

    if key == 103: #103 ascii para "g" -> para mudar a cor do lápis para verde
        print('Change pencil color to green')
        options['pencil_color'] = (0,255,0)

    if key == 98: #98 ascii para "b" -> para mudar a cor do lápis para azul
        print('Change pencil color to blue')
        options['pencil_color'] = (255,0,0)

    if key == 43: #43 ascii para "+" -> para aumentar o tamanho do lápis
        print('Increase pencil size')
        options['pencil_size'] +=1

    if key == 45: #45 ascii para "-" -> para diminuir o tamanho do lápis
        print('Decrease pencil size')
        if options['pencil_size'] !=1: #para evitar termos o tamalho do pincel a 0
            options['pencil_size'] -=1

    if key == 99: #99 ascii para "c" -> para limpar (clear) a tela, voltando a colocá-la toda branca
        print('Clear the screen')
        options['xs']=[]
        options['ys']=[]

    if key == 119: #119 ascii para "w" -> para gravar (write) a imagem atual
        print('Save image')
    
    else:
        return 1

def findObject(img, mask, options):
    mask_contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Finding contours in mask image

    if len(mask_contours) != 0:
        for mask_contour in mask_contours:
            if cv2.contourArea(mask_contour) > 1000: #blindagem para não captar objetos mais pequenos que 1000 pixeis
                x, y, w, h = cv2.boundingRect(mask_contour)
                cv2.circle(img, (int(x+w/2), int(y+h/2)), 5, (0, 0, 255), -1) #cv2.circle(image, center_coordinates, radius, color, thickness)
                options['xs'].append(int(x+w/2))
                options['ys'].append(int(y+h/2))
def main():

    global paint_wind, xs, ys, pencil_color, pencil_size

    parser = argparse.ArgumentParser(description='Definition of test mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    parser.add_argument('-usp', '--use_shake_prevention', type=str, required=False, help='Runs the snake prevention code.')
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
    #print(min)
    #print(max)
    
    f.close() #fechar o ficheiro

    lower = np.array(min)
    upper = np.array(max)  
    
    # white_img = cv2.imread('../images/altascar.png')
    # window_name = 'paint'
    # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    paint_w = np.zeros((471,636,3))+255
    cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

    options = {'paint_wind':  paint_w,'xs': [], 'ys':[], 'pencil_color':(0,255,0), 'pencil_size':1}  
    

    cap = cv2.VideoCapture(0)
    
    while True:
        
        _, img = cap.read()

        image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        cv2.namedWindow('original',cv2.WINDOW_NORMAL)

        mask = cv2.inRange(image, lower, upper)

        findObject(img, mask, options)

        paint(options)

        #print(options)

        cv2.imshow('Original', img)
        cv2.imshow('Mask', mask)
        cv2.imshow('paint', options['paint_wind'])

        press_key = cv2.waitKey(30)
        if press_key == 113: #q em ascii= sai do programa 
            break
        else:
            parameters(press_key, options)

    cv2.destroyAllWindows()
    
    # #estrutura de opções
    # if args['use_snake_prevention']:
    #     snakePrevention()
    
    # else:
    #     paint()

if __name__ == '__main__':
    main()