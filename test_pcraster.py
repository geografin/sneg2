#%%

from pcraster import *
import numpy
from osgeo import gdal
import subprocess

#%% перевод из GEOTIFF в ASCII
rpath='/home/jasny_jasen/Документы/PROJECTS/SNEG2/'
wpath='/home/jasny_jasen/Документы/programming/sneg2/' 
gdal.TranslateOptions(options=['of'])   #опции задаются отдельно
gdal.Translate('input.asc', rpath+'n55_e043_1arc_v3.tif')  #конвертация в ascii

#%% создание пустой карты с параметрами ASCII рельефа 
smmd='mapattr -s -R 3601 -C 1801 -P yb2t -x 42.999722222222 -y 54.999861111111 -l 0.0005 mask.map'
result=subprocess.run(smmd,shell=True,capture_output=True)
print(result.stderr)

#%% создание карты рельефа из ASCII рельефа с использованием clone mask.map
cmd="asc2map /home/jasny_jasen/Документы/programming/sneg2/input.asc -S -m -32767 -h 7 dem.map --clone mask.map"
result2=subprocess.run(cmd,shell=True,capture_output=True)
print(result2.stderr)

#%% 
import os
os.getcwd()

#%% создаем пробный файл
from pcraster import *
setclone('mask.map')
setglobaloption('lddin')
dem=readmap('dem.map')
result3=lddcreate(dem,9999999,5000,9999999,9999999)
report(result3,'accum.map')

#%% aguila
pcraster.aguila('accum.map')

#%%export
smmd='map2asc -a accum.map accum.asc'
result=subprocess.run(smmd,shell=True,capture_output=True)
#print(result.stderr)