#!/bin/bash

transformedPath=../videos/transf/
userD=`whoami`

#Date and unique ID for files labeling
numSECS=`date +%s`
now=$(date +"%m_%d_%Y")"_"$numSECS

rm -R RESULTS*
mkdir "RESULTS_$now"
mkdir "RESULTS_$now/TwoDim"
mkdir "RESULTS_$now/Intensidades"
ls $transformedPath

echo "------------------------------"
echo "Preprocesamiento finalizado... presione ENTER para continuar"
read analysis_mode

#PREprograma.py
for i in $(ls $transformedPath)
do
    if [ ${i:0:11} != "TRANSFORMED" ]
    then
        ./PREprograma.py $transformedPath $i
    fi
done

mv 2D_* "RESULTS_$now/TwoDim"
mv Centroides_* "RESULTS_$now/TwoDim"

#programa.py
for i in $(ls $transformedPath)
do
    if [ ${i:0:11} != "TRANSFORMED" ]
    then
        ./programa.py $transformedPath $i
    fi
done

mv Datos__* "RESULTS_$now/Intensidades"

#gnuplot plots generation
stringList=`ls "RESULTS_$now/Intensidades"`
arrayList=(${stringList//\ / })
for i in $(ls "RESULTS_$now/Intensidades")
do
    fileToProcess=${arrayList[$counter]}
    gnuplot << EOF
    #Ahora se puede hacer gnuplot scripting aqui...
    set isosamples 40
    unset key
    set title "Intensidad vs tiempo"
    set ztics 1
    plot "RESULTS_$now/Intensidades/$fileToProcess" with lines
    set term pngcairo mono enhanced
    set out 'Grafica_$fileToProcess.png'
    replot

    #set xlabel "Tiempo"
    #set ylabel "Intensidad"
    #plot "RESULTS_$now/Intensidades/$fileToProcess" using 1:2 with lines
    ##Una vez generado el .ps...
    #set term postscript
    #set output "PS_$fileToProcess.ps"
    #replot
    ##set term x11
    ##Se genera el png...
    #set term png
    #set output "Grafica_$fileToProcess.png"
    #replot
    ##set term x11
EOF
    counter=`expr $counter + 1`
done

mv Grafica_* "RESULTS_$now/Intensidades"
mv contornos.txt "../videos/transf/"

read -p "¿Desea almacenar la informacion recien procesada (en un repositorio de Github)? (s o n) " answr
echo ""
if [ "$answr" == "s" ]
then
    currentDir=`pwd`
    cd /home/$userD/LEEDcicima/
    git pull origin master
    cp -R $currentDir"/RESULTS_$now" .
    git add -A
    git commit -m "Analisis computacional de LEED: "$now
    echo ""
    echo "Si se le pide un usuario y la correspondiente contraseña a continuacion, es la informacion de su usuario de Github:"
    echo ""
    git push origin master
    echo ""
    echo "En caso de haber fallado el ingreso de contraseña de su usuario de Github, ejecutar el script gitpush.sh, ubicado en el mismo directorio en el que se encuentra este script."
    echo ""
    echo "Identificador unico para este analisis realizado (con este identificador se encuentra cual directorio, en el repositorio de Github, contiene los resultados obtenidos): "$numSECS
    echo ""
fi
