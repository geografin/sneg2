
import pandas as pd
from scipy.stats import gamma
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import calendar
import os
from model_run import *
import argparse

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
    
    pathsnow = modelpath+yr+'snow.tss'
    #pathtsnow = os.getcwd() + '/'+yr+'tsnow.tss'
    pathflow = modelpath+yr+'flow.tss'
    pathtemp = modelpath+yr+'temp.tss'
    pathprec = modelpath+yr+'prec.tss'
    pathsols = modelpath+yr+'sols.tss'
    pathliqs = modelpath+yr+'liqs.tss'
    pathliqn = modelpath+yr+'liqn.tss'
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
    alphas = [1.8 if i==1 else 4.5 for i in forestvals]
    alphac = 1/(0.3*0.3)
    delta = 1.05
    hcdfsum=[]
    precsumdf=[]
    shoddays=[]
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
        
        precsumdf.append(precdf2[maxsnowdate.loc[col]:endsnowdate.loc[col]][col].sum(axis=0))
        # SHOD procedure
        
        #print(alphas)
        alpha = alphas[int(col)-1]
        tempgtzero=data[maxsnowdate.loc[col]:endsnowdate.loc[col]]
        shoddays.append(len(tempgtzero))
        tempgtzero.loc[tempgtzero.values < 0] = 0
        hcdf = tempgtzero*alpha
        hcdfsum.append(hcdf.sum(axis=0))
        
        #print('Распечатка')
        #print(KC)
    
    KC = hcdfsum/maxsnow.values
    KCS = KC/delta
    
    fc = np.array(list(map(lambda x:gamma.sf(x,alphac,loc=0,scale=1/alphac),KCS)))
    
    hp = fc*hcdfsum
    evap=[0.3]*len(indices)
    
    corrflow = [x+y-z for x,y,z in zip(hp,precsumdf,evap)]
    
    



    #End of SHOD procedure

    if printflag==1:
        for pth in ['pics','picstables']:
            if not os.path.exists(args.workdir+pth):
                os.mkdir(args.workdir+pth)
        for station in stationrange:
            station=str(station)
            fig,ax = plt.subplots()
            #ax.plot(tsnowdf.index,tsnowdf[stationname],label='tsnow')
            ax.plot(snowdf.index,snowdf[station],label='snow')
            ax.plot(liqsdf.index,liqsdf[station],label='liqs')
            plt.xticks(rotation='vertical')
            plt.grid(True)
            plt.legend()
            fig.savefig(args.workdir+ 'pics/'+yr+'_'+station+'_plot.jpeg',format='jpeg',dpi=100)
            plt.close()
            #ax2 = ax.twinx()
            #ax2.plot(liqsdf.index,liqsdf[stationname],label='liqs',color='red')
            #ax2.bar(precdf.index,precdf[stationname],label='prec')
            #ax2.plot(solsdf.index,solsdf[stationname],label='sols',color='green')
            dfout = pd.DataFrame({'data':snowdf.index,'temp':tempdf[station],'prec':precdf[station],'snow':snowdf[station],'sols':solsdf[station],'liqs':liqsdf[station],'liqn':liqndf[station],'flow':flowdf[station]})
            dfout.to_csv(args.workdir +'picstables/' +yr+'_'+station+'_out.csv')
            #plt.legend()
            #plt.show()
            #print('.', end=' ')

    return maxsnow, maxsnowdate, datesnow, endsnowdate, secondmax, corrflow, hp, precsumdf, shoddays


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

maxsnow, maxsnowdate, datesnow, endsnowdate, secondmax, corrflow, hp, precsumdf, shoddays = plotter(2043,['23','32'],forestvals)

'''



def main(yr1yr2,stationrange,indices,forestvals,x_coords,y_coords):
    inputfiles, model,scenario,period = ensembler()
    os.chdir(args.workdir+scenario+'_'+period+'_'+model)
    modelpath=args.workdir+scenario+'_'+period+'_'+model+'/'
    if not os.path.exists(args.workdir+'/summaries'):
        os.mkdir(args.workdir+'/summaries')
    Smax = pd.DataFrame(columns=['XCOORD','YCOORD']+[str(col) for col in yr1yr2])
    Smax['XCOORD']=x_coords
    Smax['YCOORD']=y_coords
    S28Feb = Smax.copy()
    DateSmax = Smax.copy()
    DateS0 = Smax.copy()
    SecondMx = Smax.copy()
    
    Shod = pd.DataFrame({'XCOORD':x_coords,'YCOORD':y_coords,'IsForest':forestvals})
    Shodhp = pd.DataFrame({'XCOORD':x_coords,'YCOORD':y_coords,'IsForest':forestvals})
    Shodprec = pd.DataFrame({'XCOORD':x_coords,'YCOORD':y_coords,'IsForest':forestvals})
    Shoddays = pd.DataFrame({'XCOORD':x_coords,'YCOORD':y_coords,'IsForest':forestvals})
    for yr in yr1yr2:
        try:
            maxsnow, maxsnowdate, datesnow, endsnowdate, secondmax, corrflow, hp, precsumdf, shoddays = plotter(yr,stationrange,forestvals)
            Smax[str(yr)]=maxsnow.values
            S28Feb[str(yr)]=datesnow.values
            DateSmax[str(yr)]=maxsnowdate.values
            DateS0[str(yr)]=endsnowdate.values
            Shod[str(yr)]=corrflow
            Shodhp[str(yr)]=hp
            Shodprec[str(yr)]=precsumdf
            Shoddays[str(yr)]=shoddays
            SecondMx = SecondMx.join(pd.DataFrame(secondmax))
            print('Завершён год '+str(yr))
        except:
            continue

    
    for var in ['Smax','S28Feb','DateSmax','DateS0','SecondMx','Shod','Shodhp','Shodprec','Shoddays']:
        locals()[var].to_csv(args.workdir + '/summaries/'+var+'_summary.csv')

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('workdir', type=str, help='Working folder')
    parser.add_argument('printflag', type=int, help='Make preproc or not')
    parser.add_argument('scenario', type=str, help='Choosing scenario: HIST, RCP85, RCP45')
    parser.add_argument('period', type=str, help='Choosing period: 1961-2005, 2081-2100, 2041-2060')
    args = parser.parse_args()
    
    
    
    
    print('Год начала?')
    yr1=input()
    print('Год конца?')
    yr2=input()
    yr1yr2=range(int(yr1),int(yr2)+1)
    table=pd.read_csv(args.workdir+'reg_stations_coords.csv', 
                    delimiter=',', decimal='.',engine='python')
    stationrange = table['ID'].values
    indices = table['ID'].values
    forestvals = table['LES'].values
    x_coords = table['X'].values
    y_coords = table['Y'].values
    main(yr1yr2, stationrange,indices,forestvals,x_coords,y_coords)