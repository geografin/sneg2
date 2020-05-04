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

#%%gdal to PCR
path='/home/jasny_jasen/Документы/PROJECTS/SNEG2/data/'
testfile='pr_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
prjfile='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
sneg='19801009_northern_hemisphere_swe_0.25grid.nc'
test=gdal.Open(path+testfile)
prj=gdal.Open(path+prjfile)
#gdal.Info(path+sneg)
#%%
from osgeo import gdal, gdalconst

path='/home/jasny_jasen/Документы/PROJECTS/SNEG2/data/'
testfile='pr_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
prjfile='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
sneg='19801009_northern_hemisphere_swe_0.25grid.nc'

# Source
src = gdal.Open(path+sneg, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()

# We want a section of source that matches this:
match_ds = gdal.Open(path+prjfile, gdalconst.GA_ReadOnly)
match_proj = match_ds.GetProjection()
match_geotrans = match_ds.GetGeoTransform()
wide = match_ds.RasterXSize
high = match_ds.RasterYSize

# Output / destination
dst_filename = path+'precout2.tif'
dst = gdal.GetDriverByName('GTiff').Create(dst_filename, wide, high, 1, gdalconst.GDT_Float32)
dst.SetGeoTransform( match_geotrans )
dst.SetProjection( match_proj)

# Do the work
gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_Bilinear)

del dst # Flush