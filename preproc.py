#Разработка алгоритма SNEG-2
from osgeo import gdal 
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
from cdo import Cdo,CDOException,CdoTempfileStore
import datetime as dt
import numpy as np
import glob
import calendar

def regridcdo(infile,outfile,maskfile,temp):
    cdo=Cdo()
    if temp==1:
        temptemp=cdo.subc(273,input=infile)
        infile=temptemp
    else:
        temptemp=cdo.mulc(86400,input=infile)
        infile=temptemp
    cdo.remapbil(maskfile,input=infile,output=outfile)


#main preproc for model files nc
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
def createforest(src,path):
    source=gdal.Open(src,gdalconst.GA_ReadOnly)
    optt=gdal.TranslateOptions(format='PCRaster',bandList=[1],outputType=gdalconst.GDT_Byte,metadataOptions='VS_BOOLEAN')
    gdal.Translate(path+'forest.map',source,options=optt)

#создание карты леса через командную строку
#resample /home/hydronik/Документы/PROJECTS/SNEG2/data/forest.map /home/hydronik/Документы/PROJECTS/SNEG2/data/les_pole.map --clone /home/hydronik/Документы/PROJECTS/SNEG2/data/clone.map

#preproc for txt input files
#generates tss files
def tsswriter(stationfiles,ppath,date1,date2,yr):
    indices=[]
    prectss=open(ppath+'tssdata/'+str(yr)+'_prec.tss','w')
    temptss=open(ppath+'tssdata/'+str(yr)+'_temp.tss','w')
    temp=[]
    prec=[]
    for f in glob.glob(stationfiles):
        stationindex=f[-9:-4]
        print(stationindex)
        if stationindex in indices:
            continue
        elif stationindex=='23412':
            continue
        else:
            indices.append(int(stationindex))

        inputdata=open(f,'r') #открываем каждый файл
        t=0
        daterev=date1
        precc=[]
        tempp=[]
        for line in inputdata:
            
            yr,mo,da=int(line.split()[1]),int(line.split()[2]),int(line.split()[3])
            if calendar.isleap(yr)==False:
                if mo==2 and da==29:
                    continue
            date=dt.datetime(yr,mo,da) #получили дату из строки файла
            #print(yr,mo,da) #!!!!!!!!!!!!!!!!!
            if date >date2:
                break
            if date>=date1:
                datelag=abs(date-daterev).days #разница между предыдущей датой и текущей
                if datelag>1: #если разрыв больше суток - заполняем NaN
                    for i in range(1,datelag):
                        precc.append(np.nan)
                        tempp.append(np.nan)
                elif len(line.split())<6:
                    precc.append(np.nan)
                    tempp.append(np.nan)
                else:
                    tempp.append(float(line.split()[4]))
                    precc.append(float(line.split()[5]))
            daterev=date
        temp.append(tempp)
        prec.append(precc)
        inputdata.close()
    #Пишем файл tss:
    
    for fl in [temptss,prectss]:
        if fl==temptss:
            par = 'Температуры'+' '
            param = temp
        else:
            par = 'Осадки'+' '
            param = prec
        fl.write(par+'для {:d} станций'.format(len(indices))+'\n')
        fl.write(str(int(len(indices))+1)+'\n')
        fl.write('time'+'\n')
        num=1
        for st in indices: # для каждой станции
            fl.write(str(num)+'\n') #пишем список станций по индексам
            num += 1
        timestr=list(range(1,len(param[0])+1))
        print(type(timestr[2]))
        #mt=['%1.2f'for x in range()]
        fmt=(['%d']+['%1.2f']*len(param))
        print(len(param))
        print(fmt)
        z=[timestr]+param
        print(type(z[0][0]),type(z[1][0]),type(z[2][0]))
        np.savetxt(fl,np.transpose(z),fmt=fmt) #сохраняем массивы как таблицу: transpose чтобы не по строкам а по столбцам
    temptss.close()
    prectss.close()
    print(indices)
    return indices

def stationgen(indices):
    # получение координат станций
    import pandas as pd 
    table=pd.read_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/stations_coords.csv', 
                    header=0, parse_dates=True, sep=';', decimal=',',engine='python')
    #erronic=[8,29,33,36,44,47,50,55,66, 69,85,91,96,99,107,109,113]
    #table=table[(table['x_lon'].values > 22) & (table['x_lon'].values < 68)]
    #table=table[(table['y_lat'].values > 39) & (table['y_lat']< 72)]
    #table['id2']=table.index+1
    #table=table[~table['id2'].isin(erronic)]
    table['id']=table.index
    table=table[table['index'].isin(indices)]
    table=table.drop_duplicates(subset='index',keep='first', inplace=False, ignore_index=False)
    table.set_index('index',inplace=True)
    table.reindex(indices)
    table['index']=table.index
    table.set_index('id',inplace=True)
    table.reset_index(drop=True,inplace=True)
    table['id']=table.index+1
    table1=table[['x_lon','y_lat','id']]
    print(table1)
    table2=table[['id','x_lon','y_lat','index','name']]
    #table['index']=table['index']-20000
    table1.to_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/stations.txt',sep='\t',decimal='.',index=False,header=False)
    table2.to_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/stations_leg.txt',sep='\t',decimal='.',index=False,header=True)
    #создание файла станций map
    import subprocess
    ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
    subprocess.run('/home/hydronik/miniconda3/pkgs/pcraster-4.3.0-py37h9b3db4b_2/bin/col2map /home/hydronik/Документы/PROJECTS/SNEG2/data/stations.txt /home/hydronik/Документы/PROJECTS/SNEG2/data/stations.map --clone /home/hydronik/Документы/PROJECTS/SNEG2/data/clone.map -N --large',shell=True,capture_output=True)

if __name__ == "__main__":
    pass