#%% Разработка алгоритма SNEG-2
from osgeo import gdal 
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
from cdo import Cdo,CDOException,CdoTempfileStore
import datetime as dt
import numpy as np
import glob

#%%cdoregrid

def regridcdo(infile,outfile,maskfile):
    cdo=Cdo()
    cdo.remapbil(maskfile,input=infile,output=outfile)

#%%main preproc for model files nc
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
def createmaps(src,param,data1,data2,mappath):
    source=gdal.Open(src,gdalconst.GA_ReadOnly)
    index1=getindex(data1,gettintime(source))
    index2=getindex(data2,gettintime(source))
    if param=='temp':
        mapprpath='tas_map/'+param+'0000'
    else:
        mapprpath='pr_map/'+param+'0000'
    for index in range(index1[0],index2[0]):
        dataf=index1[1]+dt.timedelta(index-index1[0])
        dataf=dt.datetime.strftime(dataf,'%Y_%m_%d')
        optt=gdal.TranslateOptions(format='PCRaster',bandList=[index],outputType=gdalconst.GDT_Float32,metadataOptions='VS_SCALAR')
        gdal.Translate(mappath+mapprpath+'.{:03d}.map'.format(index-index1[0]),source,options=optt)
    print('Созданы .map файлы для модели') 
    print('Индекс 0000 соответствует дате {:%Y-%m-%d}'.format(index1[1])) 
    print('Индекс {:d} соответствует дате {:%Y-%m-%d}'.format(index-index1[0],index2[1]))       
def createclone(src,path):
    source=gdal.Open(src,gdalconst.GA_ReadOnly)
    optt=gdal.TranslateOptions(format='PCRaster',bandList=[1],outputType=gdalconst.GDT_Float32,metadataOptions='VS_SCALAR')
    gdal.Translate(path+'clone.map',source,options=optt)

#%%preproc for txt input files
#generates tss files
def tsswriter(stationfiles):
    prectss=open(ppath+'prec.tss','w')
    temptss=open(ppath+'temp.tss','w')
    date1=dt.datetime(1981,1,1)
    ind=[]
    temp=[]
    prec=[]
    for file in glob.glob(stationfiles):
        input=open(file,'r') #открываем каждый файл
        t=0
        daterev=date1
        precc=[]
        tempp=[]
        for line in input:
            if t==0:
                ind.append(line.split()[0]) #записали номер станции в массив
                t=1
            yr,mo,da=int(line.split()[1]),int(line.split()[2]),int(line.split()[3])
            date=dt.datetime(yr,mo,da) #получили дату из строки файла
            if date>=date1:
                datelag=abs(date-daterev).days #разница между предыдущей датой и текущей
                if datelag>1: #если разрыв больше суток - заполняем NaN
                    for i in range(1,datelag):
                        precc.append(np.nan)
                        tempp.append(np.nan)
                else:
                    tempp.append(float(line.split()[4]))
                    precc.append(float(line.split()[5]))
            daterev=date
        temp.append(tempp)
        prec.append(precc)
        input.close()
    #Пишем файл tss:
    for fl in [temptss,prectss]:
        if fl==temptss:
            par = 'Температуры'+''
        else:
            par = 'Осадки'+''
        fl.write(par+'для {:d} станций'.format(len(ind))+'\n')
        fl.write(str(int(len(ind))+1)+'\n')
        fl.write('time'+'\n')
        for st in ind: # для каждой станции
            fl.write('station'+'\t'+str(st)+'\n') #пишем список станций по индексам
        timestr=list(range(1,len(temp[0])+1))
        print(type(timestr[2]))
        #mt=['%1.2f'for x in range()]
        fmt=(['%d']+['%1.2f']*len(temp))
        print(len(temp))
        print(fmt)
        z=[timestr]+temp
        print(type(z[0][0]),type(z[1][0]),type(z[2][0]))
        np.savetxt(fl,np.transpose(z),fmt=fmt) #сохраняем массивы как таблицу: transpose чтобы не по строкам а по столбцам
    temptss.close()
    prectss.close()