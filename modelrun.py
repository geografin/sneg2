#%% imports
from preproc import *
from sneg2_alg import *
from pcraster.framework import *
import os
import calendar
#%%
os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data/')
print(os.getcwd())
#%%
''' 
Препроцессинг здесь
'''
path='/home/hydronik/Документы/PROJECTS/SNEG2/data/models_data/'
ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
maskf='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
precf='pr_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
tempf='tas_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
dstf=ppath+'regridded_input.nc'
#%% Preprocess with cdo
regridcdo(path+precf,ppath+'regridded_prec.nc',ppath+maskf,0)
regridcdo(path+tempf,ppath+'regridded_temp.nc',ppath+maskf,1)
#%% create map files for run
mappath='/home/hydronik/Документы/PROJECTS/SNEG2/data/rez/'
srcfiles=(ppath+'regridded_temp.nc',ppath+'regridded_prec.nc')
#%%create clonemap file
createclone(ppath+'regridded_temp.nc',ppath)
stationfiles=ppath+'wr39399/wr*.txt'

#%% RUN THE MODEL
for yr in range(1980,1983,1):
    data1=dt.datetime(yr,7,1) #даты 1 2 надо вынести во входящие данные
    #data2=data1+dt.timedelta(days=30)
    data2=dt.datetime(yr+1,7,15)
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

#%% show
pathsave='/results/'
#aguila(os.getcwd()+'/rez/pr_map/prec0000.001.map')
aguila(os.getcwd()+'/rez/tas_map/temp0000.003.map')
#aguila(os.getcwd()+pathsave+'map20000.001')

#%%
file=gdal.Open(path+precf)
print(file.GetMetadata())