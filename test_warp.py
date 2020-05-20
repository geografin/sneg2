#%%
from osgeo import gdal
from osgeo import gdal_merge as gdalmg 
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
path='/home/hydronik/Документы/PROJECTS/SNEG2/data/models_data/'
ppath='/home/hydronik/Документы/PROJECTS/SNEG2/data/'
destination=ppath+'test33.nc'
maskf='pr_Amon_ACCESS1-0_rcp85_r1i1p1_1961_90box_remapmulcyearsum.nc'
precf='pr_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
tempf='tas_day_ACCESS1-0_historical_r1i1p1_1961-2005box.nc'
mask=gdal.Open(ppath+maskf,gdalconst.GA_ReadOnly)
src=gdal.Open(path+precf,gdalconst.GA_ReadOnly)
src_temp=gdal.Open(path+tempf,gdalconst.GA_ReadOnly)

#%%
print(mask.RasterCount)
bnds=(mask.GetGeoTransform()[0],mask.GetGeoTransform()[3]-mask.RasterYSize,mask.GetGeoTransform()[0]+mask.RasterXSize,mask.GetGeoTransform()[3])
optt=gdal.WarpOptions(format='netCDF',resampleAlg='bilinear',warpOptions=('OPTIMIZE_SIZE=TRUE'),creationOptions=('COMPRESS=DEFLATE','PREDICTOR=1','ZLEVEL=6'),outputType=gdalconst.GDT_Float32,srcSRS='EPSG:4326',dstSRS='EPSG:4326',xRes=mask.RasterXSize,yRes=mask.RasterYSize,outputBounds=bnds,width=mask.GetGeoTransform()[1])
dst=gdal.Warp(destination,src,options=optt)
dst=None