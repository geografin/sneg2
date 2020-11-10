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
    dfout = pd.DataFrame({'data':snowdf.index,'temp':tempdf[stationname],'prec':precdf[stationname],'snow':snowdf[stationname],'sols':solsdf[stationname],'liqs':liqsdf[stationname],'liqn':liqndf[stationname]})
    dfout.to_csv(os.getcwd() + '/result_'+yr+'/'+stationname+'_out.csv')
    #plt.legend()
    plt.show()
    #fig.savefig(os.getcwd() + '/result_'+yr+'/'+stationname+'_plot.jpeg',format='jpeg',dpi=100)
    return None

def main():
    for station in range(1,67):
    #for station in range(5,7):
        plotter(station)

if __name__ == '__main__':
    
    main()