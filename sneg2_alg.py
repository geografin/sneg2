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
        os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data/'+pathsave)
        self.ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
        self.tpath=os.getcwd()+'/mapps/tas_map/'
        self.prpath=os.getcwd()+'/mapps/pr_map/'
        self.ttimepath=self.ppath+'tssdata/'+str(currentyear)+'_temp.tss'
        self.ptimepath=self.ppath+'tssdata/'+str(currentyear)+'_prec.tss'
        self.currentyear=currentyear

    def initial(self):
        self.start=boolean(0)
        self.TempSum=scalar(0)
        self.LiqSnowpack=scalar(0)
        self.LiqSnowpackNext=scalar(0)
        self.SolSnowpack=scalar(0)
        self.Snowpack=scalar(0)
        self.forestmap=readmap(self.ppath+'les_pole.map')
        self.map1=boolean(0)
        self.map2=boolean(0)
        self.mask=boolean(0)
        self.OttTemp=scalar(0)
        self.SpringMask=boolean(0)
        self.stationmap=readmap(self.ppath+'stations.map')
        self.SnowPackTime=TimeoutputTimeseries(str(self.currentyear)+'snow',self,self.stationmap,noHeader=False)
        #self.TSnowPackTime=TimeoutputTimeseries(str(self.currentyear)+'tsnow',self,self.stationmap,noHeader=False)
        self.FlowTime=TimeoutputTimeseries(str(self.currentyear)+'flow',self,self.stationmap,noHeader=False)
        self.TempTime=TimeoutputTimeseries(str(self.currentyear)+'temp',self,self.stationmap,noHeader=False)
        self.SolSnowpackTime=TimeoutputTimeseries(str(self.currentyear)+'sols',self,self.stationmap,noHeader=False)
        self.PrecTime=TimeoutputTimeseries(str(self.currentyear)+'prec',self,self.stationmap,noHeader=False)
        self.LiqTime=TimeoutputTimeseries(str(self.currentyear)+'liqs',self,self.stationmap,noHeader=False)
        self.FrostTime=TimeoutputTimeseries(str(self.currentyear)+'frost',self,self.stationmap,noHeader=False)
        self.LiqNextTime=TimeoutputTimeseries(str(self.currentyear)+'liqn',self,self.stationmap,noHeader=False)
        self.a=ifthenelse(self.forestmap,scalar(1.8),scalar(4.5)) # Зависит от леса и поля и от оттепель-весна
        self.b=scalar(0.13/(1-0.13))
        self.c=scalar(20)
    def dynamic(self):
        TEMP = self.readmap(self.tpath+'temp') # Чтение стэка файлов температуры формата temp0000.001
        #TEMP = timeinputscalar(self.ttimepath,self.stationmap)   # Чтение файла по станциям - для тестирования
        #mintemp=mapminimum(TEMP)
        #print(float(mapminimum(self.TEMP)))
        self.start=ifthenelse(TEMP < scalar(0),boolean(1),self.start)
        
        PREC = self.readmap(self.prpath+'prec') # Чтение стэка файлов осадков формата prec0000.001
        #PREC = timeinputscalar(self.ptimepath,self.stationmap) # Чтение файла по станциям - для тестирования
        # начало HOLOD   
        self.TempTime.sample(TEMP)
        self.PrecTime.sample(PREC)
        a=self.a
        b=self.b
        c=self.c
        self.TempSum = ifthenelse((TEMP < scalar(0)), self.TempSum + abs(TEMP), scalar(0))
        #Условие на оттепели
        self.OttTemp = ifthenelse((TEMP >= scalar(0)),self.OttTemp + scalar(1), scalar(0))
        self.OttTemp = ifthenelse(self.map1 & (int(time()) > 140),self.OttTemp, scalar(0))
        self.SpringMask = ifthenelse((self.OttTemp > scalar(5)), boolean(0),self.SpringMask) # Мы отключили условие на оттепель
        #self.report(self.TempSum, os.getcwd()+self.pathsave+'tempsum')
        SnowFrost = c*sqrt(self.TempSum)
        #--------------- до сих пор пишется нормально! -----
        #self.report(self.SnowFrost, os.getcwd()+self.pathsave+'frost')
        
        test=(TEMP < scalar(0)) & (SnowFrost < self.Snowpack)
        Snowpackone=ifthenelse(test,self.Snowpack,scalar(1))
        condTrue=self.LiqSnowpackNext*(scalar(1) - (SnowFrost / Snowpackone))
        self.LiqSnowpack = ifthenelse(test,condTrue, self.LiqSnowpack)
        self.LiqSnowpack = ifthenelse((TEMP < scalar(0)) & (SnowFrost >= self.Snowpack), scalar(0),self.LiqSnowpack)
        #self.LiqSnowpack = ifthenelse((TEMP <= scalar(0)) & (self.SnowFrost < self.Snowpack),self.LiqSnowpackNext*(scalar(1) - self.SnowFrost / self.Snowpack), scalar(0))
        #self.report(self.LiqSnowpack, os.getcwd()+self.pathsave+'liqsn')
        self.LiqSnowpackNext = ifthenelse((TEMP < scalar(0)) & (SnowFrost < self.Snowpack), self.LiqSnowpack, self.LiqSnowpackNext)
        self.LiqSnowpackNext = ifthenelse((TEMP < scalar(0)) & (SnowFrost >= self.Snowpack), scalar(0), self.LiqSnowpackNext)

        

        self.Snowpack = ifthenelse((TEMP < scalar(0)), self.Snowpack + PREC, self.Snowpack)
        #self.TSnowPackTime.sample(self.Snowpack)
        self.map1 = ifthenelse(self.Snowpack > scalar(0), boolean(1), self.map1)
        #self.report(self.map1, os.getcwd()+self.pathsave+'map1') # !!!!!!!!!!!
        Melt = a*TEMP
        Melt = ifthenelse((Melt > self.SolSnowpack),self.SolSnowpack,Melt)
        self.SolSnowpack = ifthenelse((TEMP < scalar(0)), self.Snowpack - self.LiqSnowpackNext, self.SolSnowpack - Melt)
        #self.SolSnowpack = ifthenelse((self.SolSnowpack < scalar(0)),scalar(0),self.SolSnowpack) #ТУПОЕ ОБНУЛЕНИЕ
        #начало TEPLO
        #Flow = ifthenelse((TEMP >= scalar(0)) & (self.SolSnowpack <= scalar(0)), self.Snowpack + PREC, scalar(0)) - удалили условие
        self.Snowpack = ifthenelse((TEMP >= scalar(0)) & (self.SolSnowpack <= scalar(0)), scalar(0), self.Snowpack)
        #self.LiqSnowpackNext = ifthenelse ((TEMP >= scalar(0)) & (self.SolSnowpack <= scalar(0)), scalar(0), self.LiqSnowpackNext)
        #self.LiqSnowpack = ifthenelse ((TEMP >= scalar(0)) & (self.SolSnowpack <= scalar(0)), scalar(0), self.LiqSnowpack)
        # проверка на оттепель: если оттепель - не завершать расчет снегонакопления
        self.map2 = ifthenelse((TEMP >= scalar(0)) & (self.SolSnowpack <= scalar(0)),self.SpringMask,self.map2)
        # начало VODA
        
        self.LiqSnowpack = ifthenelse((TEMP >= scalar(0)), self.LiqSnowpackNext + Melt + PREC, self.LiqSnowpack)
        
        SnowCapacity = b*self.SolSnowpack
        self.Snowpack = ifthenelse((TEMP >= scalar(0)) & (self.LiqSnowpack > SnowCapacity), self.SolSnowpack + SnowCapacity, self.Snowpack)
        self.Snowpack = ifthenelse((TEMP >= scalar(0)) & (self.LiqSnowpack <= SnowCapacity), self.SolSnowpack + self.LiqSnowpack, self.Snowpack)
        
        #self.Snowpack = ifthenelse(self.start==boolean(1),self.Snowpack,scalar(0))
        #self.report(map2, os.getcwd()+self.pathsave+'map2') # !!!!!!!!!!!
        Flow = ifthenelse((TEMP >= scalar(0)) & (self.LiqSnowpack > SnowCapacity), self.LiqSnowpack - SnowCapacity, scalar(0))
        self.LiqSnowpackNext = ifthenelse((TEMP >= scalar(0)) & (self.LiqSnowpack > SnowCapacity), SnowCapacity, self.LiqSnowpackNext)
        self.LiqSnowpackNext = ifthenelse((TEMP >= scalar(0)) & (self.LiqSnowpack <= SnowCapacity), self.LiqSnowpack, self.LiqSnowpackNext)
        self.mask = ~ self.map2
        #self.report(self.mask, os.getcwd()+self.pathsave+'mask') # !!!!!!!!!!!
        
        
        #self.Snowpack = ifthenelse((self.Snowpack < scalar(0)),scalar(0),self.Snowpack) #ТУПОЕ ОБНУЛЕНИЕ
        
        # сохранение результатов
        self.Snowpack = ifthenelse(self.mask & self.start,self.Snowpack,scalar(0))
        self.SolSnowpack = ifthenelse(self.mask & self.start,self.SolSnowpack,scalar(0))
        self.LiqSnowpack = ifthenelse(self.mask & self.start,self.LiqSnowpack,scalar(0))
        #Flow=ifthenelse(self.mask & self.start,Flow, scalar(0))
        #Ниже если по станциям:
        # репортить tss по снегу, водоотдаче, стоку
        self.SnowPackTime.sample(self.Snowpack)
        self.FlowTime.sample(Flow)
        self.SolSnowpackTime.sample(self.SolSnowpack)
        self.FrostTime.sample(SnowFrost)
        self.LiqTime.sample(self.LiqSnowpack)
        self.LiqNextTime.sample(self.LiqSnowpackNext)
        #Тесты для вспомогательных карт:
        #self.report(self.mask,os.getcwd()+self.pathsave+'mask')
        #self.report(self.map2,os.getcwd()+self.pathsave+'map2')
        #self.report(self.map1,os.getcwd()+self.pathsave+'map1')
        #self.report(self.SpringMask,os.getcwd()+self.pathsave+'spng')
        #Ниже если по модели а не по станциям
        #self.report(Snow, os.getcwd()+self.pathsave+'snow')
        #self.report(Flowr, os.getcwd()+self.pathsave+'flow')

if __name__ == "__main__":
    pass      