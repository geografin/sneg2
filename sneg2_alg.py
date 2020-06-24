'''
Model for calculating snow
'''

from pcraster import *
from pcraster.framework import *
import numpy

class Snow2Model(DynamicModel):
    def __init__(self,clonemap):
        DynamicModel.__init__(self)
        setclone(clonemap)
        a=1.8 # Зависит от леса и поля и от оттепель-весна
        b=0.13/(1-0.13)
        c=20
        pathsave='/home/hydronik/Документы/PROJECTS/SNEG2/data/results/'

    def initial(self):
        start=0
        TEMP=0
        LiqSnowpack=0
        LiqSnowpackNext=0
        SnowCapacity=0
        SolSnowpack=0
        SnowFrost=0
        


    def dynamic(self):
        TEMP = readmap(temp) # Чтение стэка файлов температуры формата temp0000.001
        if start == 0:
            if mapminimum(TEMP)<0:
                start=1
                map1=ifthen(TEMP<-9999)
        else:        
            PREC = readmap(prec) # Чтение стэка файлов температуры формата prec0000.001
            # начало HOLOD
            TempSum = ifthenelse(TEMP <= 0, TempSum + abs(TEMP), 0)
            SnowFrost = c*sqrt(TempSum)
            LiqSnowpack = ifthenelse(TEMP <= 0 & SnowFrost < Snowpack,LiqSnowpackNext*(1 - SnowFrost/Snowpack),0)
            LiqSnowpackNext = ifthenelse(TEMP <= 0 & SnowFrost < Snowpack, LiqSnowpack, 0)
            Snowpack = ifthenelse(TEMP <= 0, Snowpack + PREC, Snowpack)
            map1 = ifthenelse(Snowpack > 0, 1, map1)
            SolSnowpack = ifthenelse(TEMP <= 0, Snowpack - LiqSnowpackNext, SolSnowpack - a*TEMP)
            #начало TEPLO
            Flow = ifthenelse(TEMP > 0 & SolSnowpack <= 0, Snowpack + PREC, 0)
            Snowpack = ifthenelse(TEMP > 0 & SolSnowpack <= 0, 0, Snowpack)
            # начало VODA
            LiqSnowpack = ifthenelse(TEMP > 0 & SolSnowpack > 0, LiqSnowpackNext + a*TEMP + PREC, LiqSnowpack)
            LiqSnowpackNext = ifthenelse (TEMP > 0 & SolSnowpack <= 0, 0, LiqSnowpackNext)
            SnowCapacity = ifthenelse (TEMP > 0 & SolSnowpack > 0, b*SolSnowpack, 0)
            Snowpack = ifthenelse(TEMP > 0 & LiqSnowpack > SnowCapacity, Snowpack + SnowCapacity, Snowpack + PREC)
            map2 = ifthen(TEMP > 0 & LiqSnowpack > SnowCapacity)
            Flow = ifthenelse(TEMP > 0 & LiqSnowpack > SnowCapacity, LiqSnowpack - SnowCapacity, 0)
            LiqSnowpackNext = ifthenelse(TEMP > 0 & LiqSnowpack > SnowCapacity, SnowCapacity,LiqSnowpack)
            #
            map3 = ifthen(map1 & map2)
            map3 = cover(~ map3, 57)
            mask = ifthenelse(mask==57,mask,map3) 
            # сохранение результатов
            Snowpack = ifthenelse(mask==57,0,Snowpack)
            Flow = ifthenelse(mask==57,0,Flow)
            report(Snowpack, pathsave+'snow')
            report(Flow, pathsave+'flow')





