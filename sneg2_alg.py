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
        self.a=1.8 # Зависит от леса и поля и от оттепель-весна
        self.b=0.13/(1-0.13)
        self.c=20
        self.pathsave='/results/'
        self.tpath='/rez/tas_map/'
        self.prpath='/rez/pr_map/'

    def initial(self):
        self.start=0
        self.TempSum=scalar(0)
        self.LiqSnowpack=scalar(0)
        self.LiqSnowpackNext=scalar(0)
        self.SnowCapacity=scalar(0)
        self.SolSnowpack=scalar(0)
        self.Snowpack=scalar(0)
        self.SnowFrost=scalar(0)
        self.map1=scalar(0)
        self.mask=scalar(0)


    def dynamic(self):
        self.TEMP = self.readmap(os.getcwd()+self.tpath+'temp') # Чтение стэка файлов температуры формата temp0000.001
        mintemp=mapminimum(self.TEMP)
        self.start=ifthenelse(mintemp<0,scalar(1),self.start)
        self.PREC = self.readmap(os.getcwd()+self.prpath+'prec')
        # начало HOLOD   
        TEMP=self.TEMP
        PREC=self.PREC
        a=self.a
        b=self.b
        c=self.c
        self.TempSum = ifthenelse(TEMP <= 0, self.TempSum + abs(TEMP), 0)
        self.SnowFrost = c*sqrt(self.TempSum)
        self.LiqSnowpack = ifthenelse(TEMP <= 0 & self.SnowFrost < self.Snowpack,self.LiqSnowpackNext*(1 - self.SnowFrost/self.Snowpack),0)
        self.LiqSnowpackNext = ifthenelse(TEMP <= 0 & ifthen(self.SnowFrost < self.Snowpack,scalar(1))==1, self.LiqSnowpack, 0)
        self.Snowpack = ifthenelse(TEMP <= 0, self.Snowpack + PREC, self.Snowpack)
        self.map1 = ifthenelse(self.Snowpack > 0, 1, self.map1)
        self.SolSnowpack = ifthenelse(TEMP <= 0, self.Snowpack - self.LiqSnowpackNext, self.SolSnowpack - a*TEMP)
        #начало TEPLO
        self.Flow = ifthenelse(TEMP > 0 & self.SolSnowpack <= 0, self.Snowpack + PREC, 0)
        self.Snowpack = ifthenelse(TEMP > 0 & self.SolSnowpack <= 0, 0, self.Snowpack)
        # начало VODA
        self.LiqSnowpack = ifthenelse(TEMP > 0 & self.SolSnowpack > 0, self.LiqSnowpackNext + a*TEMP + PREC, self.LiqSnowpack)
        self.LiqSnowpackNext = ifthenelse (TEMP > 0 & self.SolSnowpack <= 0, 0, self.LiqSnowpackNext)
        self.SnowCapacity = ifthenelse (TEMP > 0 & self.SolSnowpack > 0, b*self.SolSnowpack, 0)
        self.Snowpack = ifthenelse(TEMP > 0 & self.LiqSnowpack > self.SnowCapacity, self.Snowpack + self.SnowCapacity, self.Snowpack + PREC)
        self.map2 = ifthen(TEMP > 0 & self.LiqSnowpack > self.SnowCapacity)
        self.Flow = ifthenelse(TEMP > 0 & self.LiqSnowpack > self.SnowCapacity, self.LiqSnowpack - self.SnowCapacity, 0)
        self.LiqSnowpackNext = ifthenelse(TEMP > 0 & self.LiqSnowpack > self.SnowCapacity, self.SnowCapacity, self.LiqSnowpack)
        #
        map3 = ifthen(map1 & map2)
        map3 = cover(~ map3, 57)
        self.mask = ifthenelse(self.mask==57,self.mask,map3) 
        # сохранение результатов
        self.Snowpack = ifthenelse(self.mask==57,0,self.Snowpack)
        self.Flow = ifthenelse(self.mask==57,0,self.Flow)
        self.Snowpack=ifthen(self.start==1,self.Snowpack)
        self.Flow=ifthen(self.start==1,self.Flow)
        self.report(self.Snowpack, os.getcwd()+self.pathsave+'snow')
        self.report(self.Flow, os.getcwd()+self.pathsave+'flow')
       