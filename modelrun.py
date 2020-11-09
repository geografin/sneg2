#%% imports
from preproc import *
from sneg2_alg import *
from pcraster.framework import *
import os
import calendar
import pandas as pd
%reload_ext autoreload
%autoreload 2
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
#%%create tss
stationfiles=ppath+'wr39399/wr*.txt'
tsswriter(stationfiles,ppath)
#%%create map of stations

#%% postprocessing - получение данных за год
import pandas as pd
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import calendar
%matplotlib inline
def readtss(path,yr):
    
    
    with open(path) as f:
        number = int(f.readlines()[1])
        #linn = f.readlines()[110].split()
        colnumbers = [str(i) for i in range(1,number)]
        print(['timestep']+colnumbers)
        #print(len(linn))
    if calendar.isleap(int(yr)+1)==True:
        per=366
    else:
        per=365
    df = pd.read_csv(path, skiprows=number+2, sep='\s+', \
    names=['timestep']+colnumbers,  decimal='.',engine='python')
    df = df.where(df < 1000000)
    df['dates']=pd.date_range(dt.datetime(int(yr),7,1),periods=per)
    df=df.set_index(['dates'])
    # чтение файла: определяем кол-=во строк станций
    # считываем станции по порядку в массив
    # считываем шаги модели и переводим в даты - пишем в массив дат
    # считываем для каждой станции значения
    # объединяем в  DataFrame
    # ищем средние, даты, макс
    return df

def plotter(stationname):
    yr='1981'
    stationname=str(stationname)
    first = '1981-09-01'
    end='1982-06-25'
    os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data')
    pathsnow = os.getcwd() + '/result_'+yr+'/'+yr+'snow.tss'
    #pathtsnow = os.getcwd() + '/result_'+yr+'/'+yr+'tsnow.tss'
    pathflow = os.getcwd() + '/result_'+yr+'/'+yr+'flow.tss'
    pathtemp = os.getcwd() + '/result_'+yr+'/'+yr+'temp.tss'
    pathprec = os.getcwd() + '/result_'+yr+'/'+yr+'prec.tss'
    pathsols = os.getcwd() + '/result_'+yr+'/'+yr+'sols.tss'
    pathliqs = os.getcwd() + '/result_'+yr+'/'+yr+'liqs.tss'
    pathliqn = os.getcwd() + '/result_'+yr+'/'+yr+'liqn.tss'
    snowdf = readtss(pathsnow,yr)[first:end]
    #tsnowdf = readtss(pathtsnow,yr)[first:end]
    flowdf = readtss(pathflow,yr)[first:end]
    tempdf = readtss(pathtemp,yr)[first:end]
    precdf = readtss(pathprec,yr)[first:end]
    solsdf = readtss(pathsols,yr)[first:end]
    liqsdf = readtss(pathliqs,yr)[first:end]
    liqndf = readtss(pathliqn,yr)[first:end]
    #precdf = precdf.mul(10)
    fig,ax = plt.subplots()
    #ax.plot(tsnowdf.index,tsnowdf[stationname],label='tsnow')
    ax.plot(snowdf.index,snowdf[stationname],label='snow')
    ax.plot(liqndf.index,precdf[stationname],label='prec')
    plt.xticks(rotation='vertical')
    plt.grid(True)
    plt.legend()
    #ax2 = ax.twinx()
    #ax2.plot(liqsdf.index,liqsdf[stationname],label='liqs',color='red')
    #ax2.bar(precdf.index,precdf[stationname],label='prec')
    #ax2.plot(solsdf.index,solsdf[stationname],label='sols',color='green')
    dfout = pd.DataFrame({'data':snowdf.index,'temp':tempdf[stationname],'prec':precdf[stationname],'snow':snowdf[stationname],'liqn':liqndf[stationname]})
    dfout.to_csv(os.getcwd() + '/result_'+yr+'/'+stationname+'_out.csv')
    #plt.legend()
    plt.show()
    #fig.savefig(os.getcwd() + '/result_'+yr+'/'+stationname+'_plot.jpeg',format='jpeg',dpi=100)
    return None
#for station in range(1,67):
for station in range(5,7):
    plotter(station)

#%% RUN THE MODEL
for yr in range(1979,1982,1):
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
os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data')
pathsave='/results/'
#aguila(os.getcwd()+'/rez/pr_map/prec0000.001.map')
aguila(os.getcwd()+'/result_1980/mask0000')
#aguila(os.getcwd()+pathsave+'map20000.001')

#%% test
files = '/home/hydronik/Документы/PROJECTS/SNEG2/data/stationdata/test.txt'
with open(files,'r') as f:
    for line in f:
        #yr,mo,da,t,pr=int(line.split('\t')[1]),int(line.split('\t')[2]),int(line.split('\t')[3]),float(line.split('\t')[4]),float(line.split('\t')[5])
        print(len(line.strip('\n').split()))
#%% 
t=os.path.abspath('/home/hydronik/Документы/PROJECTS/SNEG2/data/'+str(1888)+'snow.tss')
t