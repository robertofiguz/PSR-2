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
        cv2.line(options['paint_wind'], (x1, y1), (x2, y2), options['pencil_color'], options['pencil_size']) #criar linha entre os dois ultimos pontos da lista

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
            if cv2.contourArea(mask_contour) > 1000: #blindagem para não captar objetos mais pequenos que 1000 pixeis
                x, y, w, h = cv2.boundingRect(mask_contour)
                cv2.circle(img, (int(x+w/2), int(y+h/2)), 5, (0, 0, 255), -1) #cv2.circle(image, center_coordinates, radius, color, thickness)
                options['xs'].append(int(x+w/2))
                options['ys'].append(int(y+h/2))


def compare_images(img1, img2):
    
    s = cv2.subtract(img2, img1)#subtrair as imagens (colorida original e colorida pelo user)
    s = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)#converter para escala de cinza
    num_black_pix = cv2.countNonZero(s)#contar os pixeis pretos (pixeis que foram pintados corretamente)
    total_pixels = s.shape[0]*s.shape[1]#contar o numero total de pixeis
    percentage_correct = 100-((num_black_pix*100)/total_pixels)#calcular a percentagem de pixeis pintados corretamente
    return percentage_correct

def main():
    mode = "regular"#iniciar o programa em modo regular

    # Create the parser and add arguments
    parser = argparse.ArgumentParser(description='Definition of test mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    parser.add_argument('-f', '--use_feed', action=argparse.BooleanOptionalAction ,required=False, help='Uses the camera feed as canvas.')
    parser.add_argument('-d', '--drawing', action=argparse.BooleanOptionalAction ,required=False, help='Use a drawing as canvas.')
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
   
    #Capture video from camera
    cap = cv2.VideoCapture(0)
    _, img = cap.read()
    
    #Inicializar o canvas em branco com o tamanho da imagem capturada
    paint_w = np.zeros((img.shape[0], img.shape[1],3),dtype = np.uint8) 
    paint_w.fill(255) #correponde à cor de background, 255 corresponde à cor branca
    #Criar dicionario com as opções usadas pelo prgrama, incluindo a cor do lapis e tamanho e a janela a ser usada pelo programa para desenhar
    options = {'paint_wind':  paint_w,'xs': [], 'ys':[], 'pencil_color':(0,255,0), 'pencil_size':3}  
    
    #Verificar se o utilizador escolheu a opção do desenho 
    if args['drawing']:
        #carregar a imagem colorida original
        image_color = cv2.imread('color.png', 1)
        #carregar a imagem a preto e branco (por colorir)
        image_bw = cv2.imread('bw.png',1)
        #converter ambas as imagens para o tamanho da imagem capturada
        image_color = cv2.resize(image_color, (img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA)
        image_bw = cv2.resize(image_bw, (img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA)
        #definir a tela usada para desenhar como a imagem a preto e branco
        options['paint_wind'] = image_bw
        #calcular a percentagem inicial que está correta de forma a subtrair a percentagem final
        initial_percentage = compare_images(image_color, image_bw)

    #Definir as janelas usadas pelo OpenCV
    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Original', img.shape[1], img.shape[0])
    cv2.namedWindow('Mask',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Mask', img.shape[1], img.shape[0])
    cv2.namedWindow('Paint',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Paint', img.shape[1], img.shape[0])

    def paint_circle(window, center, coordinates):
        #Desenhar elipses na janela de desenho
        cv2.ellipse(window, center, (int(coordinates[1]/2),int(coordinates[0]/2)),0,0,360,options['pencil_color'], options['pencil_size'])
    def paint_rectangle(window, center, radius):
        #Desenhar retangulos na janela de desenho
        cv2.rectangle(window, center, radius, options['pencil_color'], options['pencil_size'])

    key_presses = []

    while True:
        #Capturar a imagem da camera
        _, img = cap.read()

        #usando apenas um keypress como signal para iniciar os desenhos de figuras, usualmente gerava dois devido a um problema na captação do keypress, por isso verificamos se existem dois seguidos neste caso
        key_presses = key_presses[-2:]

        #Criar mascara com os valores de cor definidos no color_segmenter.py
        mask = cv2.inRange(img, lower, upper)
        #Aplicar a mascara à imagem original
        findObject(img, mask, options)
        press_key = cv2.waitKey(30)
        key_presses.append(press_key)
        if len(set(key_presses)) == 1:
            key = key_presses[0]
        if key == ord('o'):
            #iniciar modo de circulo se estiver a primir a tecla 'o'
            if mode != 'circle':   
                center = (options['xs'][-1], options['ys'][-1])
            mode = 'circle'
        elif key == ord('t'):
            #iniciar modo de retangulo se estiver a primir a tecla 't'
            if mode != 'rectangle':
                center = (options['xs'][-1], options['ys'][-1])
            mode = 'rectangle'
        elif press_key == ord('q'): #sai do programa 
            if args['drawing']:
                #calcular a percentagem final quando terminar o programa
                percentage = compare_images(image_color, options['paint_wind'])
                percentage -= initial_percentage
                print("Percentage of the drawing correct: {0:.0f}%".format(percentage))
            break
        else:
            mode = "regular"
            parameters(press_key, options) #mudar os parametros usados pelo paint usando o input do utilizador

        if mode != "regular":
            try:
                #se o modo for regular fazer update da janela com uma copia criada antes de iniciar o circulo ou retangulo, desta forma o retangulo só é desenhado quando o utilizador soltar a tecla
                options['paint_wind'] = image_copy   
            except UnboundLocalError:
                pass
        
        if mode == 'regular':
            #atualizar a copia da imagem sem o circulo ou retangulo
            image_copy = deepcopy(options['paint_wind'])
            paint(options)
        elif mode == 'circle':
            #atualizar a copia da imagem sem o circulo ou retangulo
            image_copy = deepcopy(options['paint_wind'])
            paint_circle(options['paint_wind'], center, (options['xs'][-1], options['ys'][-1]))
        elif mode == 'rectangle':
            #atualizar a copia da imagem sem o circulo ou retangulo
            image_copy = deepcopy(options['paint_wind'])
            paint_rectangle(options['paint_wind'], center, (options['xs'][-1], options['ys'][-1]))    

        #atualizar as janelas, original e mascara
        cv2.imshow('Original', img)
        cv2.imshow('Mask', mask)

        if args['use_feed']:
            #Caso o utilizador tenha escolhido usar o feed, criar uma janela fazendo overlay entre a imagem da caemra e o desenho
            feed =  cv2.bitwise_and(img, options['paint_wind'])
            cv2.imshow('Paint',feed)
        else:
            cv2.imshow('Paint', options['paint_wind'])
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()