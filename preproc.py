#%% Разработка алгоритма SNEG-2
from pcraster import *
import numpy
from osgeo import gdal
from osgeo import gdal_merge as gdalmg 
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
import glob
import subprocess
import netCDF4
from cdo import Cdo,CDOException,CdoTempfileStore
import datetime as dt
path='/home/hydronik/Документы/PROJECTS/SNEG2/data/models_data/'
ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
destination=ppath+'test33.nc'
maskf='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
precf='pr_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
tempf='tas_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
dstf=ppath+'regridded_input.nc'

#%%cdoregrid

def regridcdo(infile,outfile):
    cdo=Cdo()
    cdo.remapbil(ppath+maskf,input=infile,output=outfile)

regridcdo(path+precf,ppath+'regridded_prec.nc')
regridcdo(path+tempf,ppath+'regridded_temp.nc')

#%%main preproc
#gettin index from file
def gettintime(file):
    startingday=dt.datetime(1,1,1)
    metadata=file.GetMetadata()['NETCDF_DIM_time_VALUES']
    metarray=metadata.strip('}{').split(',')
    metarray=[float(item)for item in metarray]
    deltas=list(map(lambda x: dt.timedelta(days=x),metarray))
    datas=list(map(lambda x: startingday+x,deltas))
    return datas
def getindex(data,array):
    datacorr=data+dt.timedelta(hours=12)
    ind=array.index(datacorr)+1
    return ind,data

# cycle for create map files from netcdf
def createmaps(src,param):
    test=gdal.Open(src,gdalconst.GA_ReadOnly)
    data1=dt.datetime(1981,1,1)
    data2=data1+dt.timedelta(days=30)
    index1=getindex(data1,gettintime(test))
    index2=getindex(data2,gettintime(test))
    if param=='temp':
        mapprpath='/home/hydronik/Документы/PROJECTS/SNEG2/data/rez/tas_map/'
    else:
        mapprpath='/home/hydronik/Документы/PROJECTS/SNEG2/data/rez/pr_map/'
    for index in range(index1[0],index2[0]):
        dataf=index1[1]+dt.timedelta(index-index1[0])
        dataf=dt.datetime.strftime(dataf,'%Y_%m_%d')
        optt=gdal.TranslateOptions(format='PCRaster',bandList=[index],outputType=gdalconst.GDT_Float32,metadataOptions='VS_SCALAR')
        gdal.Translate(mapprpath+param+dataf+'.map',test,options=optt)
srcfiles=(ppath+'regridded_temp.nc',ppath+'regridded_prec.nc')
createmaps(srcfiles[0],'temp')
createmaps(srcfiles[1],'prec')


