#%% imports
from preproc import *
from sneg2_alg import *
from pcraster.framework import *
import os
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
regridcdo(path+precf,ppath+'regridded_prec.nc',ppath+maskf)
regridcdo(path+tempf,ppath+'regridded_temp.nc',ppath+maskf)
#%% create map files for run
mappath='/home/hydronik/Документы/PROJECTS/SNEG2/data/rez/'
srcfiles=(ppath+'regridded_temp.nc',ppath+'regridded_prec.nc')
data1=dt.datetime(1981,7,1) #даты 1 2 надо вынести во входящие данные
#data2=data1+dt.timedelta(days=30)
data2=dt.datetime(1982,7,15)
createmaps(srcfiles[0],'temp',data1,data2,mappath)
createmaps(srcfiles[1],'prec',data1,data2,mappath)
#%%create clonemap file
createclone(ppath+'regridded_temp.nc',ppath)
stationfiles=ppath+'wr39399/wr*.txt'
#%% run the Model
myModel=Snow2Model(ppath+'clone.map')
dynModel = DynamicFramework(myModel, lastTimeStep=366)
dynModel.run()