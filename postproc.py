import pandas as pd
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import calendar
import os

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

def plotter(yr,stationrange):
    printflag=0
    first = str(yr)+'-07-01'
    end=str(yr+1)+'-06-25'
    yr=str(yr)
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
    
    snowdf2=snowdf.drop('timestep',axis='columns')
    maxsnow = snowdf2.max(axis=0)
    
    maxsnowdate = snowdf2.idxmax()
    
    datesnow = snowdf2.loc[str(int(yr)+1)+'-02-28']
    changedate=maxsnowdate.copy()
    changedate.loc[(changedate<str(int(yr)+1)+'-01-01')]=str(int(yr)+1)+'-03-01'
    changedate=pd.to_datetime(changedate)
    endsnowdate = snowdf2.loc[min(changedate.values):].idxmin()

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
            fig.savefig(os.getcwd() + '/result_'+yr+'/'+station+'_plot.jpeg',format='jpeg',dpi=100)
            plt.close()
            #ax2 = ax.twinx()
            #ax2.plot(liqsdf.index,liqsdf[stationname],label='liqs',color='red')
            #ax2.bar(precdf.index,precdf[stationname],label='prec')
            #ax2.plot(solsdf.index,solsdf[stationname],label='sols',color='green')
            dfout = pd.DataFrame({'data':snowdf.index,'temp':tempdf[station],'prec':precdf[station],'snow':snowdf[station],'sols':solsdf[station],'liqs':liqsdf[station],'liqn':liqndf[station],'flow':flowdf[station]})
            dfout.to_csv(os.getcwd() + '/result_'+yr+'/'+station+'_out.csv')
            #plt.legend()
            #plt.show()
            #print('.', end=' ')

    return maxsnow, maxsnowdate, datesnow, endsnowdate

def main(yr1yr2,stationrange,indices):
    Smax = pd.DataFrame(columns=['Stations']+[str(col) for col in yr1yr2])
    Smax['Stations']=indices
    S28Feb = Smax.copy()
    DateSmax = Smax.copy()
    DateS0 = Smax.copy()

    for yr in yr1yr2:
        maxsnow, maxsnowdate, datesnow, endsnowdate = plotter(yr,stationrange)
        Smax[str(yr)]=maxsnow.values
        S28Feb[str(yr)]=datesnow.values
        DateSmax[str(yr)]=maxsnowdate.values
        DateS0[str(yr)]=endsnowdate.values
        print('Завершён год '+str(yr))

    
    for var in ['Smax','S28Feb','DateSmax','DateS0']:
        locals()[var].to_csv(os.getcwd() + '/summaries/'+var+'_summary.csv')

if __name__ == '__main__':
    print('Год начала?')
    yr1=input()
    print('Год конца?')
    yr2=input()
    yr1yr2=range(int(yr1),int(yr2)+1)
    table=pd.read_csv('/home/hydronik/Документы/PROJECTS/SNEG2/data/stations_leg.txt', 
                    delimiter='\t', decimal='.',engine='python')
    stationrange = table['id'].values
    indices = table['index'].values
    main(yr1yr2, stationrange,indices)