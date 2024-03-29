
import pandas as pd
from scipy.stats import gamma
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import calendar
import os
from model_run import *

def readtss(path,yr):
    
    
    with open(path) as f:
        number = int(f.readlines()[1])
        #linn = f.readlines()[110].split()
        colnumbers = [str(i) for i in range(1,number)]
        #print(['timestep']+colnumbers)
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

def plotter(yr,stationrange,forestvals):
    
    printflag=0
    first = str(yr)+'-07-01'
    end=str(yr+1)+'-06-25'
    yr=str(yr)
    
    pathsnow = os.getcwd()+'/'+yr+'snow.tss'
    #pathtsnow = os.getcwd() + '/'+yr+'tsnow.tss'
    pathflow = os.getcwd() +'/'+yr+'flow.tss'
    pathtemp = os.getcwd() + '/'+yr+'temp.tss'
    pathprec = os.getcwd() + '/'+yr+'prec.tss'
    pathsols = os.getcwd() + '/'+yr+'sols.tss'
    pathliqs = os.getcwd() + '/'+yr+'liqs.tss'
    pathliqn = os.getcwd() + '/'+yr+'liqn.tss'
    snowdf = readtss(pathsnow,yr)[first:end]
    #tsnowdf = readtss(pathtsnow,yr)[first:end]
    flowdf = readtss(pathflow,yr)[first:end]
    tempdf = readtss(pathtemp,yr)[first:end]
    precdf = readtss(pathprec,yr)[first:end]
    solsdf = readtss(pathsols,yr)[first:end]
    liqsdf = readtss(pathliqs,yr)[first:end]
    liqndf = readtss(pathliqn,yr)[first:end]
    #precdf = precdf.mul(10)
    
    snowdf2=snowdf.drop('timestep',axis='columns')
    tempdf2=tempdf.drop('timestep',axis='columns')
    flowdf2=flowdf.drop('timestep',axis='columns')
    precdf2=precdf.drop('timestep',axis='columns')
    maxsnow = snowdf2.max(axis=0)
    
    maxsnowdate = snowdf2.idxmax()
    
    datesnow = snowdf2.loc[str(int(yr)+1)+'-02-28']
    changedate=maxsnowdate.copy()
    
    changedate.loc[(changedate<str(int(yr)+1)+'-01-01')]=str(int(yr)+1)+'-03-01' #делаем 1 марта там где дата максимума снега ранее января
    changedate=pd.to_datetime(changedate)
    
    endsnowdate = snowdf2.loc[changedate.min():].idxmin() #индекс первого случая минимума для усеченной таблицы по минимальной дате максимального снегозапаса
    # Search of maximums
        
    secondmax=[]
    
    for col,data in tempdf2.iteritems():
        # создаем для данной станции таблицу из температур и снега
        sdf=pd.concat([data,snowdf2[col]],axis=1,keys=['tempr','snowr'])
        # ограничиваем начало по дате максимального снегозапаса и выбираем отрицательные
        fdf=sdf[maxsnowdate.loc[col]:].where(sdf['tempr']<0)
        # проходим окном в 5 дней и находим максимумы, 
        # а затем удаляем пустые значения, таким образом получаем
        # таблицу где есть только периоды заморозков больше 5 суток
        fdf=fdf.rolling(5).max().dropna()
        
        fdf['date2']=fdf.index
        # Теперь сдвигаем столбец с датами на 1 день и считаем разницу с индексом
        # оставляем только строки где разница больше 1 дня
        fddf=fdf[fdf.shift(-1).diff()['date2']>dt.timedelta(1)]
        
        
        try:
            if len(fddf)>1:
                # сток между максимумами
                flow2=flowdf2[fddf.index[0]:fddf.index[1]+dt.timedelta(1)][col].sum(axis=0)
                flow1=flowdf2[maxsnowdate.loc[col]:fddf.index[0]+dt.timedelta(1)][col].sum(axis=0)
                
                secondmax.append({yr+'maxdate1':fddf.index[0],yr+'max1':fddf['snowr'][0],yr+'flow1':flow1,yr+'maxdate2':fddf.index[1],yr+'max2':fddf['snowr'][1],yr+'flow2':flow2})
            else:
                flow1=flowdf2[maxsnowdate.loc[col]:fddf.index[0]+dt.timedelta(1)][col].sum(axis=0)
                secondmax.append({yr+'maxdate1':fddf.index[0],yr+'max1':fddf['snowr'][0],yr+'flow1':flow1,yr+'maxdate2':np.nan,yr+'max2':np.nan,yr+'flow2':np.nan})
            
            
        except:
            secondmax.append({yr+'maxdate1':np.nan,yr+'max1':np.nan,yr+'flow1':np.nan,yr+'maxdate2':np.nan,yr+'max2':np.nan,yr+'flow2':np.nan})
        
    # SHOD procedure
    alphas = [1.8 if i==1 else 4.5 for i in forestvals]
    alphac = 1/(0.3*0.3)
    print(alphas)
    delta = 1.05
    tempgtzero=tempdf2[maxsnowdate.loc[col]:endsnowdate.loc[col]]
    tempgtzero[tempgtzero < 0] = 0
    hcdf = tempgtzero.mul(alphas,axis=1)
    
    KC = hcdf.sum(axis=0)/maxsnow
    print('Распечатка')
    print(KC)
    KCS = KC/delta
    fc = gamma.sf(KCS,alphac,loc=0,scale=1/alphac)
    hp = fc*hcdf.sum(axis=0)
    precsumdf = precdf2[maxsnowdate.loc[col]:endsnowdate.loc[col]].sum(axis=0)
    
    corrflow = hp + precsumdf - 0.3





    #End of SHOD procedure

    if printflag==1:
        for station in stationrange:
            station=str(station)
            fig,ax = plt.subplots()
            #ax.plot(tsnowdf.index,tsnowdf[stationname],label='tsnow')
            ax.plot(snowdf.index,snowdf[station],label='snow')
            ax.plot(liqsdf.index,liqsdf[station],label='liqs')
            plt.xticks(rotation='vertical')
            plt.grid(True)
            plt.legend()
            fig.savefig(os.getcwd() +yr+'_'+station+'_plot.jpeg',format='jpeg',dpi=100)
            plt.close()
            #ax2 = ax.twinx()
            #ax2.plot(liqsdf.index,liqsdf[stationname],label='liqs',color='red')
            #ax2.bar(precdf.index,precdf[stationname],label='prec')
            #ax2.plot(solsdf.index,solsdf[stationname],label='sols',color='green')
            dfout = pd.DataFrame({'data':snowdf.index,'temp':tempdf[station],'prec':precdf[station],'snow':snowdf[station],'sols':solsdf[station],'liqs':liqsdf[station],'liqn':liqndf[station],'flow':flowdf[station]})
            dfout.to_csv(os.getcwd() +'/' +yr+'_'+station+'_out.csv')
            #plt.legend()
            #plt.show()
            #print('.', end=' ')

    return maxsnow, maxsnowdate, datesnow, endsnowdate, secondmax, corrflow, hp


'''
#%% Testing SHOD
import pandas as pd
#import scipy as sp
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import calendar
import os
from model_run import *
table=pd.read_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/stations_leg.txt', 
                    delimiter='\t', decimal='.',engine='python')
table2=pd.read_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/leg_forest.csv', 
                    delimiter=',', decimal='.',engine='python')
stationrange = table['id'].values
indices = table['index'].values
forestvals = table2['rvalue_1'].values
inputfiles, model,scenario,period = ensembler()
os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data/'+scenario+'_'+period+'_'+model)

maxsnow, maxsnowdate, datesnow, endsnowdate, secondmax, corrflow, hp = plotter(2043,['23','32'],forestvals)

'''



def main(yr1yr2,stationrange,indices,forestvals):
    inputfiles, model,scenario,period = ensembler()
    os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data/'+scenario+'_'+period+'_'+model)
    if not os.path.exists(os.getcwd()+'/summaries'):
        os.mkdir(os.getcwd()+'/summaries')
    Smax = pd.DataFrame(columns=['Stations']+[str(col) for col in yr1yr2])
    Smax['Stations']=indices
    S28Feb = Smax.copy()
    DateSmax = Smax.copy()
    DateS0 = Smax.copy()
    SecondMx = Smax.copy()
    
    Shod = pd.DataFrame({'Stations':indices,'IsForest':forestvals})
    Shodhp = pd.DataFrame({'Stations':indices,'IsForest':forestvals})
    for yr in yr1yr2:
        maxsnow, maxsnowdate, datesnow, endsnowdate, secondmax, corrflow, hp = plotter(yr,stationrange,forestvals)
        Smax[str(yr)]=maxsnow.values
        S28Feb[str(yr)]=datesnow.values
        DateSmax[str(yr)]=maxsnowdate.values
        DateS0[str(yr)]=endsnowdate.values
        Shod[str(yr)]=corrflow.values
        Shodhp[str(yr)]=hp.values
        SecondMx = SecondMx.join(pd.DataFrame(secondmax))
        print('Завершён год '+str(yr))

    
    for var in ['Smax','S28Feb','DateSmax','DateS0','SecondMx','Shod','Shodhp']:
        locals()[var].to_csv(os.getcwd() + '/summaries/'+var+'_summary.csv')

if __name__ == '__main__':
    print('Год начала?')
    yr1=input()
    print('Год конца?')
    yr2=input()
    yr1yr2=range(int(yr1),int(yr2)+1)
    table=pd.read_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/stations_leg.txt', 
                    delimiter='\t', decimal='.',engine='python')
    table2=pd.read_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/leg_forest.csv', 
                    delimiter=',', decimal='.',engine='python')
    stationrange = table['id'].values
    indices = table['index'].values
    forestvals = table2['rvalue_1'].values
    main(yr1yr2, stationrange,indices,forestvals)