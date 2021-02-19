
from preproc import *
from sneg2_alg import *
from pcraster.framework import *
import os, shutil
import calendar
import pandas as pd
import glob
#Ввод путей


def ensembler():
    # calculate ansembles of models for future
    #scenario='HIST'
    scenario='RCP85'
    #scenario='RCP45'
    #period='2041-2060'
    period='2081-2100'
    #period='1961-2005'
    models=[]
    inputfiles = {}
    # ---------------------------------------#
    cmnpath = '/home/hydronik/Документы/PROJECTS/SNEG2/data/models_data/MODELS/'
    wrkpath = cmnpath + scenario +'/' + period +'/'
    modelslist = glob.glob(wrkpath+'*')
    modelfiles = [fl[len(wrkpath):] for fl in modelslist]
    for i,itm in enumerate(glob.glob(wrkpath+'tas*')):
        m=itm.split('_')[3]
        models.append(m)
        print (i,m)
    print('Какую бы вы хотели модель? Впишите номер!')
    num=int(input())
    inputfiles['temp']=glob.glob(wrkpath+'tas*'+models[num]+'*')
    inputfiles['prec']=glob.glob(wrkpath+'pr*'+models[num]+'*')
    print(inputfiles)
    return inputfiles, models[num],scenario,period



def preprocessing(inputfiles,resultfolder,ppath):    

    #Preprocess with cdo
    maskf='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
    regridcdo(inputfiles['prec'],resultfolder+'/regridded_prec.nc',ppath+maskf,0)
    regridcdo(inputfiles['temp'],resultfolder+'/regridded_temp.nc',ppath+maskf,1)
    #create clonemap file
    createclone(resultfolder+'/regridded_temp.nc',resultfolder+'/')
    
def writetss(yr):
    #create tss
    ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
    stationfiles=ppath+'stationdata/*.txt'
    date1=dt.datetime(yr,7,1)#дата с которой надо начинать запись данных
    date2=dt.datetime(yr+1,7,15)
    indices=tsswriter(stationfiles,ppath,date1,date2,yr)
    return indices



def main(preprocflag=1,stationflag=1,mapsflag=1):
    #RUN THE MODEL
    os.chdir('/home/hydronik/Документы/PROJECTS/SNEG2/data/')
    path='/home/hydronik/Документы/PROJECTS/SNEG2/data/models_data/'
    ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
    inputfiles,model,scenario,period=ensembler()
    result_path='/home/hydronik/Документы/PROJECTS/SNEG2/data/'+scenario+'_'+period+'_'+model
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    resultfolder='/home/hydronik/Документы/PROJECTS/SNEG2/data/'+scenario+'_'+period+'_'+model
    if not os.path.exists(resultfolder+'/mapps'):
        os.mkdir(resultfolder+'/mapps')
    mappath=resultfolder+'/mapps'
    print('Расчет ведется по сценарию {} для периода {} моделью {}'.format(scenario,period,model))
    #dstf=ppath+'regridded_input.nc'
    #mappath='/home/hydronik/Документы/PROJECTS/SNEG2/data/rez/'
    srcfiles=(resultfolder+'/regridded_temp.nc',resultfolder+'/regridded_prec.nc')
    print('Введите год начала:')
    year1=int(input())
    print('Введите год конца:')
    year2=int(input())
    if preprocflag==1:
        preprocessing(inputfiles,resultfolder,ppath)
    if stationflag==1:
        for yr in range(year1,year2+1,1):
            indices=writetss(yr)
        stationgen(indices)
    
    for yr in range(year1,year2+1,1):
        
        
        os.chdir(resultfolder)
            
        data1=dt.datetime(yr,7,1) #даты 1 2 надо вынести во входящие данные
        #data2=data1+dt.timedelta(days=30)
        data2=dt.datetime(yr+1,7,15)
        if mapsflag==1:
            createmaps(srcfiles[0],'temp',data1,data2,mappath)
            createmaps(srcfiles[1],'prec',data1,data2,mappath)
        # run the Model
        if calendar.isleap(yr+1)==1: # проверка на високосность
            timesteps=366
        else:
            timesteps=365
            
        pathsave=scenario+'_'+period+'_'+model
        myModel=Snow2Model('clone.map',yr,pathsave)
        dynModel = DynamicFramework(myModel, lastTimeStep=timesteps)
        dynModel.run()
        folders=['/tas_map','/pr_map']
        for folder in folders:
            if os.path.exists(mappath+folder):
                shutil.rmtree(mappath+folder)
        

if __name__ == '__main__':
    #writetss(1981,1982)
    #ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
    #createforest(ppath+'forest.tif',ppath)
    main(preprocflag=1,stationflag=0,mapsflag=1)