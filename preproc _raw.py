#%% Разработка алгоритма SNEG-2
from osgeo import gdal 
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
from cdo import Cdo,CDOException,CdoTempfileStore
import datetime as dt


#%%cdoregrid

def regridcdo(infile,outfile):
    cdo=Cdo()
    cdo.remapbil(ppath+maskf,input=infile,output=outfile)

regridcdo(path+precf,ppath+'regridded_prec.nc')
regridcdo(path+tempf,ppath+'regridded_temp.nc')

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
def createmaps(src,param):
    test=gdal.Open(src,gdalconst.GA_ReadOnly)
    data1=dt.datetime(1981,1,1) #даты 1 2 надо вынести во входящие данные
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

#%%preproc for txt input files
#generates tss files
import numpy as np
import glob
prectss=open(ppath+'prec.tss','w')
temptss=open(ppath+'temp.tss','w')
date1=dt.datetime(1981,1,1)
ind=[]
temp=[]
prec=[]
for file in glob.glob(ppath+'wr39399/wr*.txt'):
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
#Пишем файл tss
temptss.write('Температуры для {:d} станций'.format(len(ind))+'\n')
temptss.write(str(int(len(ind))+1)+'\n')
temptss.write('time'+'\n')
for st in ind: # для каждой станции
    temptss.write('station'+'\t'+str(st)+'\n') #пишем список станций по индексам
timestr=list(range(1,len(temp[0])+1))
print(type(timestr[2]))
#mt=['%1.2f'for x in range()]
fmt=(['%d']+['%1.2f']*len(temp))
print(len(temp))
print(fmt)
z=[timestr]+temp
print(type(z[0][0]),type(z[1][0]),type(z[2][0]))
np.savetxt(temptss,np.transpose(z),fmt=fmt) #сохраняем массивы как таблицу: transpose чтобы не по строкам а по столбцам
temptss.close()
prectss.close()

#%%numpy это тест
import numpy as np
test=open(ppath+'test.tss','w')
test.write('Это начало...'+'\n')
test.write('123442'+'\n')
x=[1,2,4,5,23,5,5,67,8]
y=[[65,45,7,56,68,68,454,4,34],[99,56,7,56,68,68,7,4,34]]
z=[x]+y
print(z)
np.savetxt(test,np.transpose(z),fmt=('%d','%1.1f','%1.1f'))
test.close()






# %%
