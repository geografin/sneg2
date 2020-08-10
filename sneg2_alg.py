'''
Model for calculating snow
'''

from pcraster import *
from pcraster.framework import *
import numpy

class Snow2Model(DynamicModel):
    def __init__(self,clonemap,currentyear,pathsave):
        DynamicModel.__init__(self)
        setclone(clonemap)
        self.a=scalar(1.8) # Зависит от леса и поля и от оттепель-весна
        self.b=scalar(0.13/(1-0.13))
        self.c=scalar(20)
        self.pathsave=pathsave
        self.tpath='/rez/tas_map/'
        self.prpath='/rez/pr_map/'
        self.currentyear=currentyear

    def initial(self):
        self.start=boolean(0)
        self.TempSum=scalar(0)
        self.LiqSnowpack=scalar(0)
        self.LiqSnowpackNext=scalar(0)
        self.SnowCapacity=scalar(0)
        self.SolSnowpack=scalar(0)
        self.Snowpack=scalar(0)
        self.SnowFrost=scalar(0)
        self.map1=boolean(0)
        self.mask=boolean(0)
        self.OttTemp=scalar(0)
        self.SpringMask=boolean(0)


    def dynamic(self):
        self.TEMP = self.readmap(os.getcwd()+self.tpath+'temp') # Чтение стэка файлов температуры формата temp0000.001
        mintemp=mapminimum(self.TEMP)
        #print(float(mapminimum(self.TEMP)))
        self.start=ifthenelse(self.TEMP<scalar(0),boolean(1),self.start)
        
        self.PREC = self.readmap(os.getcwd()+self.prpath+'prec')
        # начало HOLOD   
        TEMP=self.TEMP
        PREC=self.PREC
        a=self.a
        b=self.b
        c=self.c
        self.TempSum = ifthenelse((TEMP <= scalar(0)), self.TempSum + abs(TEMP), scalar(0))
        self.OttTemp = ifthenelse((TEMP > scalar(0)),self.OttTemp + scalar(1), scalar(0))
        self.SpringMask = self.OttTemp > scalar(3)
        #self.report(self.TempSum, os.getcwd()+self.pathsave+'tempsum')
        self.SnowFrost = c*sqrt(self.TempSum)
        #--------------- до сих пор пишется нормально! -----
        #self.report(self.SnowFrost, os.getcwd()+self.pathsave+'frost')
        
        test=(TEMP <= scalar(0)) & (self.SnowFrost < self.Snowpack)
        Snowpackone=ifthenelse(test,self.Snowpack,scalar(1))
        condTrue=self.LiqSnowpackNext*(scalar(1) - (self.SnowFrost / Snowpackone))
        self.LiqSnowpack = ifthenelse(test,condTrue, scalar(0))
        #self.LiqSnowpack = ifthenelse((TEMP <= scalar(0)) & (self.SnowFrost < self.Snowpack),self.LiqSnowpackNext*(scalar(1) - self.SnowFrost / self.Snowpack), scalar(0))
        self.report(self.LiqSnowpack, os.getcwd()+self.pathsave+'liqsn')
        self.LiqSnowpackNext = ifthenelse((TEMP <= scalar(0)) & (self.SnowFrost < self.Snowpack), self.LiqSnowpack, scalar(0))
        self.Snowpack = ifthenelse((TEMP <= scalar(0)), self.Snowpack + PREC, self.Snowpack)
        print(float(mapmaximum(self.Snowpack)))
        print(float(mapminimum(self.Snowpack)))
        self.map1 = ifthenelse(self.Snowpack > scalar(0), boolean(1), self.map1)
        self.report(self.map1, os.getcwd()+self.pathsave+'map1') # !!!!!!!!!!!
        self.SolSnowpack = ifthenelse((TEMP <= scalar(0)), self.Snowpack - self.LiqSnowpackNext, self.SolSnowpack - a*TEMP)
        #начало TEPLO
        self.Flow = ifthenelse((TEMP > scalar(0)) & (self.SolSnowpack <= scalar(0)), self.Snowpack + PREC, scalar(0))
        self.Snowpack = ifthenelse((TEMP > scalar(0)) & (self.SolSnowpack <= scalar(0)), scalar(0), self.Snowpack)
        
        map2 = (TEMP > scalar(0)) & (self.SolSnowpack <= scalar(0))
        map2 = map2 & (self.map1==boolean(1))
        map2 = map2 & self.SpringMask # проверка на оттепель: если оттепель - не завершать расчет снегонакопления
        # начало VODA
        self.LiqSnowpack = ifthenelse((TEMP > scalar(0)) & (self.SolSnowpack > scalar(0)), self.LiqSnowpackNext + a*TEMP + PREC, self.LiqSnowpack)
        self.LiqSnowpackNext = ifthenelse ((TEMP > scalar(0)) & (self.SolSnowpack <= scalar(0)), scalar(0), self.LiqSnowpackNext)
        self.SnowCapacity = ifthenelse ((TEMP > scalar(0)) & (self.SolSnowpack > scalar(0)), b*self.SolSnowpack, scalar(0))
        self.Snowpack = ifthenelse((TEMP > scalar(0)) & (self.LiqSnowpack > self.SnowCapacity), self.Snowpack + self.SnowCapacity, self.Snowpack + PREC)
        self.Snowpack = ifthenelse(self.start==boolean(1),self.Snowpack,scalar(0))
        self.report(map2, os.getcwd()+self.pathsave+'map2') # !!!!!!!!!!!
        self.Flow = ifthenelse((TEMP > scalar(0)) & (self.LiqSnowpack > self.SnowCapacity), self.LiqSnowpack - self.SnowCapacity, scalar(0))
        self.LiqSnowpackNext = ifthenelse((TEMP > scalar(0)) & (self.LiqSnowpack > self.SnowCapacity), self.SnowCapacity, self.LiqSnowpack)
        
        
        self.mask = ifthenelse(map2,boolean(1),self.mask) 
        self.report(self.mask, os.getcwd()+self.pathsave+'mask') # !!!!!!!!!!!
        # сохранение результатов
        
        Snow=ifthen(self.mask & self.start,self.Snowpack)
        Flowr=ifthen(self.mask & self.start,self.Flow)
        self.report(Snow, os.getcwd()+self.pathsave+'snow')
        self.report(Flowr, os.getcwd()+self.pathsave+'flow')
        # ПЕРЕБИРАТЬ (УБИРАТЬ) УСЛОВИЯ ПОКА НЕ НАЙДЕМ ОШИБКУ