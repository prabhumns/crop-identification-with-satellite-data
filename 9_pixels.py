from osgeo import gdal, osr, ogr, gdal_array
import os
import numpy as np
from numpy.linalg import inv
import pickle
from random import shuffle
from shutil import copyfile
def check_centre(i,j):
    try:
        a = sdb_data[:,j-1,i-1]
        b = sdb_data[:,j-1,i] 
        c = sdb_data[:,j-1,i+1]
        d = sdb_data[:,j,i-1]
        e = sdb_data[:,j,i]
        f = sdb_data[:,j,i+1]
        g = sdb_data[:,j+1,i-1]
        h = sdb_data[:,j+1,i]
        i = sdb_data[:,j+1,i+1]
    except IndexError:
        return []
    if (a != np.array([0,0,0,0,0])).any() and (b != np.array([0,0,0,0,0])).any() and (c != np.array([0,0,0,0,0])).any() and (d != np.array([0,0,0,0,0])).any() and (e != np.array([0,0,0,0,0])).any() and (f != np.array([0,0,0,0,0])).any() and (g != np.array([0,0,0,0,0])).any() and (h != np.array([0,0,0,0,0])).any() and (i != np.array([0,0,0,0,0])).any():
        return [list(n) for n in [a,b,c,d,e,f,g,h,i]]
    else:
        return []
    
sat_file = 

crop_file = 

sdb = gdal.Open(sat_file)
sdb_ncols = sdb.RasterXSize
sdb_nrows = sdb.RasterYSize
sdb_gt = sdb.GetGeoTransform()
sdb_cs = osr.SpatialReference()
sdb_cs.ImportFromWkt(sdb.GetProjectionRef())
sdb_data = gdal_array.DatasetReadAsArray(sdb,0,0,sdb_ncols, sdb_nrows)
for i in range(sdb_ncols):
    for j in range(sdb_nrows):
        example = check_centre(i, j)
        if len(example) == 45:
            
