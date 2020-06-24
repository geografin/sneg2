from preproc import *
from sneg2_alg import *

''' 
Препроцессинг здесь
'''
path='/home/hydronik/Документы/PROJECTS/SNEG2/data/models_data/'
ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
mappath='/home/hydronik/Документы/PROJECTS/SNEG2/data/rez/'
maskf='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
precf='pr_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
tempf='tas_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
dstf=ppath+'regridded_input.nc'

regridcdo(path+precf,ppath+'regridded_prec.nc')
regridcdo(path+tempf,ppath+'regridded_temp.nc')

srcfiles=(ppath+'regridded_temp.nc',ppath+'regridded_prec.nc')
createmaps(srcfiles[0],'temp')
createmaps(srcfiles[1],'prec')

stationfiles=ppath+'wr39399/wr*.txt'

myModel=Snow2Model('clone.map')
dynModel = DynamicFramework(myModel, lastTimeStep=16, firstTimeStep=1)
dynModel.run()