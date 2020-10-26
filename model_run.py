from preproc import *
from sneg2_alg import *
from pcraster.framework import *
import os
import calendar
import pandas as pd
#Ввод путей
def preprocessing():    

    #Preprocess with cdo
    
    regridcdo(path+precf,ppath+'regridded_prec.nc',ppath+maskf,0)
    regridcdo(path+tempf,ppath+'regridded_temp.nc',ppath+maskf,1)
    #create clonemap file
    
    createclone(ppath+'regridded_temp.nc',ppath)
def writetss(year1,year2):
    #create tss
    ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
    stationfiles=ppath+'stationdata/*.txt'
    date1=dt.datetime(year1,7,1)#дата с которой надо начинать запись данных
    date2=dt.datetime(year2,7,15)
    indices=tsswriter(stationfiles,ppath,date1,date2)
    stationgen(indices)


def main(preprocflag=1,stationflag=1,mapsflag=1):
    #RUN THE MODEL
    os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data/')
    path='/home/hydronik/Документы/PROJECTS/SNEG2/data/models_data/'
    ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
    maskf='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
    precf='pr_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
    tempf='tas_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
    dstf=ppath+'regridded_input.nc'
    mappath='/home/hydronik/Документы/PROJECTS/SNEG2/data/rez/'
    srcfiles=(ppath+'regridded_temp.nc',ppath+'regridded_prec.nc')
    print('Введите год начала:')
    year1=int(input())
    print('Введите год конца:')
    year2=int(input())
    if preprocflag==1:
        preprocessing()
    if stationflag==1:
        writetss(year1,year2)
    for yr in range(year1,year2+1,1):

        data1=dt.datetime(yr,7,1) #даты 1 2 надо вынести во входящие данные
        #data2=data1+dt.timedelta(days=30)
        data2=dt.datetime(yr+1,7,15)
        if mapsflag==1:
            createmaps(srcfiles[0],'temp',data1,data2,mappath)
            createmaps(srcfiles[1],'prec',data1,data2,mappath)
        # run the Model
        if calendar.isleap(yr+1)==1: # проверка на високосность
            timesteps=366
        else:
            timesteps=365
        os.mkdir('/home/hydronik/Документы/PROJECTS/SNEG2/data/result_'+str(yr))
        pathsave='/result_'+str(yr)+'/'
        myModel=Snow2Model(ppath+'clone.map',yr,pathsave)
        dynModel = DynamicFramework(myModel, lastTimeStep=timesteps)
        dynModel.run()

if __name__ == '__main__':
    #writetss(1981,1982)
    main(preprocflag=0,stationflag=0,mapsflag=0)