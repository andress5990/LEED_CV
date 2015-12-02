#!/usr/bin/python

import numpy as np
import cv2
import sys
import math
import subprocess

#TODO: merge this script with PREprograma.py script
#Contour extraction
miarchivoContornos=open("contornos.txt", 'r')
for linea in miarchivoContornos:
    listadoGeneralCONTORNOS=[]
    for lineaContorno in linea.split(':'):
        listadoGeneralCONTORNOS.append([])
        for puntoContorno in lineaContorno.split(';'):
            listadoGeneralCONTORNOS[len(listadoGeneralCONTORNOS)-1].append([int(puntoContorno.split(',')[0]),int(puntoContorno.split(',')[1])])
miarchivoContornos.close()

drawing = False
ix,iy = -1,-1

listadoFilesLazos=[]
generalList=[]
specificList=[]

generalList=listadoGeneralCONTORNOS
espaciadoTemporal=15
listaIntensidades=[]
counterFrames=1
numberFramesRewind=24
ciclosSaltados=0

FPSextract=8

def funcionDetencionYReanudacion(counterMAS, filename2, img2, ciclosSaltadosX):
    global generalList, listaIntensidades, counterFrames
    tmpPRT=0
    while(1):
        cv2.imshow(filename2, img2)
        kp=cv2.waitKey(200) & 0xFF
        if kp==ord('q'):
            print "Reanudado..."
            tmpPRT=2
            break
        if kp==ord('r'):
            tmpPRT=1
            break
    if tmpPRT==1:
        tmpVideoBuff = cv2.VideoCapture(sys.argv[1]+filename2)
        for cntrFrmsBuff in range(0,(counterFrames-numberFramesRewind*ciclosSaltadosX)):
            tmpRetBuff, tmpFrameBuff=tmpVideoBuff.read()
        imgBuff = cv2.cvtColor(tmpFrameBuff, cv2.COLOR_BGR2GRAY)
        cntROTULADO=0
        for x in generalList:
            fontSCR = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(imgBuff,str(cntROTULADO),(generalList[cntROTULADO][0][0],generalList[cntROTULADO][0][1]), fontSCR, 1,(255,255,255),2,2)
            cv2.polylines(imgBuff,[np.array(x, np.int32).reshape((-1,1,2))],True,(255,0,0))
            cntROTULADO+=1
        cv2.namedWindow(filename2)
        cv2.setMouseCallback(filename2,draw_lines, imgBuff)
        cv2.imshow(filename2, imgBuff)
        for cntrPOL in range(0,len(listaIntensidades[counter-2])):
            for cntBORR in range(0,numberFramesRewind):
                listaIntensidades[counter-2][cntrPOL].pop()
        counterFrames-=numberFramesRewind*ciclosSaltadosX
        filename3=filename2
        funcionDetencionYReanudacion(0, filename3, imgBuff, ciclosSaltadosX)

def draw_lines(event, x, y, flags, param):
    global generalList, specificList
    global ix,iy,drawing
    global ciclosSaltados
    if event == cv2.EVENT_LBUTTONDOWN:
        fontSCR = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(param,str(len(generalList)),(x,y), fontSCR, 1,(255,255,255),2,2)

        specificList=[]
        bufferArray=[x,y]
        specificList.append(bufferArray)
        drawing = True
        ix,iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            bufferArray=[x,y]
            specificList.append(bufferArray)
            cv2.circle(param,(x,y),5,(0,0,255),-1)
    elif event == cv2.EVENT_LBUTTONUP:
        print "Ciclos saltados: "+str(ciclosSaltados)
        listaIntensidades[counter-2].append([])
        for cnt in range(0, int(float(counterFrames)/float(ciclosSaltados))):
            listaIntensidades[counter-2][len(listaIntensidades[counter-2])-1].append(0)

        bufferArray=[x,y]
        specificList.append(bufferArray)
        drawing = False
        cv2.circle(param,(x,y),1,(0,0,255),-1)
        generalList.append(specificList)
        pts = np.array(specificList, np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(param,[pts],True,(255,0,0))
        print "Cantidad de lazos dibujados hasta el momento: 1 global mas %d locales" %(len(generalList)-1)

def procesado(filename):
    global listadoFilesLazos, generalList, counterFrames, ciclosSaltados
    for cnt in range(0, len(generalList)):
        listaIntensidades[counter-2].append([])
    print "\nIniciando procesado del archivo %s..." %filename
    tmpVideo = cv2.VideoCapture(sys.argv[1]+filename)
    str_command = "mediainfo "+sys.argv[1]+filename
    process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0].split('\n')
    fps_video = 'a'
    for line_from_str in output:
        if line_from_str.startswith('Frame rate'):
            fps_video = line_from_str
            break
    fps_video = float(fps_video.split()[3].split('.')[0])
    if not tmpVideo:
        print "Falla en extraccion de video..."
    tmpRet, tmpFrame=tmpVideo.read()
    cap = cv2.VideoCapture(sys.argv[1]+filename)
    counterFrames=1
    devolucionFRAMES=0
    fontSCR = cv2.FONT_HERSHEY_SIMPLEX
    ciclosSaltados=int(fps_video/FPSextract)
    print ciclosSaltados
    while True:
        estadoFinal="sin interrumpir"
        if devolucionFRAMES==1:
            cap.release()
            cap = cv2.VideoCapture(sys.argv[1]+filename)
            for x in range(0,counterFrames):
                ret, frame = cap.read()
            devolucionFRAMES=0
        else:
            ret, frame = cap.read()
        if type(frame)!=type(tmpFrame):
            break
        if counterFrames%ciclosSaltados==0:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            del frame
            cntROTULADO=0
            for x in generalList:
                cv2.putText(img,str(cntROTULADO),(generalList[cntROTULADO][0][0],generalList[cntROTULADO][0][1]), fontSCR, 1,(255,255,255),2,2)
                cv2.polylines(img,[np.array(x, np.int32).reshape((-1,1,2))],True,(255,0,0))
                cntROTULADO+=1
            cv2.putText(img,str("{0:.2f}".format(counterFrames/fps_video)),(0,60), fontSCR, 1,(255,255,255),2,2)
            cv2.namedWindow(filename)
            cv2.setMouseCallback(filename,draw_lines, img)
            cv2.imshow(filename, img)
            for cnt in range(0, len(generalList)):
                mask2=np.zeros(img.shape,np.uint8)
                cv2.drawContours(mask2,[np.array(generalList[cnt], np.int32).reshape((-1,1,2))],0,255,-1)
                mean_val = cv2.mean(img,mask = mask2)
                M = cv2.moments(np.array(generalList[cnt], np.int32).reshape((-1,1,2)))
                centroid_x = int(M['m10']/M['m00'])
                centroid_y = int(M['m01']/M['m00'])
                (center_x,center_y),radiusOrigCircle = cv2.minEnclosingCircle(np.array(generalList[cnt], np.int32).reshape((-1,1,2)))
                NewDoubleCircle=[]
                NewDoubleCircleOrig=[]
                for radiansCounter in range(0,60):
                    NewDoubleCircle.append([center_x+1.15*radiusOrigCircle*math.cos((2*math.pi)*(radiansCounter*6/360)),center_y+2*radiusOrigCircle*math.sin((2*math.pi)*(radiansCounter*6/360))])
                for radiansCounter in range(0,60):
                    NewDoubleCircleOrig.append([center_x+radiusOrigCircle*math.cos((2*math.pi)*(radiansCounter*6/360)),center_y+2*radiusOrigCircle*math.sin((2*math.pi)*(radiansCounter*6/360))])
                mask3=np.zeros(img.shape,np.uint8)
                cv2.drawContours(mask3,[np.array(NewDoubleCircle, np.int32).reshape((-1,1,2))],0,255,-1)
                mask4=cv2.bitwise_xor(mask2,mask3)
                mean_val2 = cv2.mean(img,mask = mask4)
                listaIntensidades[counter-2][cnt].append(mean_val[0]-mean_val2[0])
            keyFinger=cv2.waitKey(espaciadoTemporal) & 0xFF
            if keyFinger == ord('q'):
                print "Detenido..."
                counterFramesBefore=counterFrames
                funcionDetencionYReanudacion(0, filename, img, ciclosSaltados)
                counterFramesAfter=counterFrames
                if counterFramesBefore!=counterFramesAfter:
                    devolucionFRAMES=1
            elif keyFinger == ord('s'):
                estadoFinal="interrumpido"
                break
        else:
            del ret
            del frame
        counterFrames+=1
    tmpVideo.release()
    cap.release()

    listadoFilesLazos.append(generalList)
    generalList=[]
    print "Procesamiento del archivo %s se ha completado (%s)." % (unicode(filename), unicode(estadoFinal))
    cv2.destroyWindow(filename)

counter=0
for elem in sys.argv:
    if counter>=2:
        listaIntensidades.append([])
        procesado(sys.argv[counter])
    counter+=1

minutoInicial=float(sys.argv[2].split('.')[0][10:])*30
espaciadoTemporalMS=1/float(FPSextract)
for cntAR in range(len(listaIntensidades)):
    for cntAR2 in range(len(listaIntensidades[cntAR])):
        miarchivo = open('Datos_'+'_'+str(cntAR2)+'.dat', 'a')
        for cntAR3 in range(len(listaIntensidades[cntAR][cntAR2])):
            miarchivo.write(str(minutoInicial+cntAR3*espaciadoTemporalMS)+"    "+str(listaIntensidades[cntAR][cntAR2][cntAR3])+"\n")

print "\nFin del programa"
