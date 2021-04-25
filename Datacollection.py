from osgeo import osr, gdal
from openpyxl.workbook import Workbook
import sys
import pandas as pd

crops = {1:'Corn', 5:'Soybeans', 27:'Rye', 53:'Peas',28:'Oats'} #number:cropname

babydatasets = {}
for num, cropname in crops.items():
    babydatasets[cropname] = []

cd = gdal.Open('./Cropdata/Cropdata.tif')
cd_ncols = cd.RasterXSize
cd_nrows = cd.RasterYSize
cd_nbands = cd.RasterCount 
cd_gt = cd.GetGeoTransform()
cd_band = cd.GetRasterBand(1)
cd_data = cd_band.ReadAsArray(0, 0, cd_ncols, cd_nrows)
cd_cs= osr.SpatialReference()
cd_cs.ImportFromWkt(cd.GetProjectionRef())
 
def Convert(i,j, sd_gt, sd_cs):
    transform = osr.CoordinateTransformation(sd_cs,cd_cs)
    o1 = sd_gt[0] + i *sd_gt[1] + j*sd_gt[2]
    o2 = sd_gt[3] + i *sd_gt[4] + j*sd_gt[5]
    return transform.TransformPoint(o1,o2)

def Crop(i,j, sd_gt, sd_cs):
    q = Convert(i,j, sd_gt, sd_cs)
    x = int((q[0]-cd_gt[0])/cd_gt[1])
    y = int((q[1]-cd_gt[3])/cd_gt[5])
    try: 
        return cd_data[y][x]
    except IndexError:
        return 0

def YRN(i,j,sd_gt, sd_cs, crops):
    p = Crop(i,j,sd_gt, sd_cs)
    if p in crops:
        if Crop(i,j+1,sd_gt, sd_cs) == p:
            if Crop(i+1,j,sd_gt, sd_cs) == p:
                if Crop(i+1,j+1,sd_gt, sd_cs) == p:
                    return crops[p]
                else:
                    return 'USELESS'
            else:
                return 'USELESS'
        else:
            return 'USELESS'
    else:
        return 'USELESS'

def processsat(file, crops = crops):
    croplists1 = {'a':[]}
    croplists2 = {'a':[]}
    croplists3 = {'a':[]}
    croplists4 = {'a':[]}
    for nums, name in crops.items():
        croplists1[name] = []
        croplists2[name] = []
        croplists3[name] = []
        croplists4[name] = []
    del croplists1['a']
    del croplists2['a']
    del croplists3['a']
    del croplists4['a']
    sd = gdal.Open(file)
    sd_ncols = sd.RasterXSize
    sd_nrows = sd.RasterYSize
    sd_gt = sd.GetGeoTransform()
    sd_data1 = sd.GetRasterBand(1).ReadAsArray(0, 0, sd_ncols, sd_nrows)
    sd_data2 = sd.GetRasterBand(2).ReadAsArray(0, 0, sd_ncols, sd_nrows)
    sd_data3 = sd.GetRasterBand(3).ReadAsArray(0, 0, sd_ncols, sd_nrows)
    sd_data4 = sd.GetRasterBand(4).ReadAsArray(0, 0, sd_ncols, sd_nrows)
    sd_cs= osr.SpatialReference()
    sd_cs.ImportFromWkt(sd.GetProjectionRef())
    l = 1
    totalsize = sd_ncols*sd_nrows
    for i in range(sd_ncols):
        for j in range(sd_nrows):
            a = sd_data1[j][i]; b = sd_data2[j][i]; c = sd_data3[j][i]; d = sd_data4[j][i]
            if a != 0 or b != 0 or c!= 0 or d!= 0:
                yrn = YRN(i,j, sd_gt, sd_cs, crops)
                if yrn != 'USELESS':
                    croplists1[yrn].append(a)
                    croplists2[yrn].append(b)
                    croplists3[yrn].append(c)
                    croplists4[yrn].append(d)
            l = l+1
    return croplists1, croplists2, croplists3, croplists4


satfiles = ['./Satdata1/Satdata1/Satdata1.tif','./Satdata2/Satdata2/Satdata2.tif']
for file in satfiles:
    croplists1,croplists2, croplists3, croplists4 = processsat(file)
    for num , cropname in crops.items():
        babydatasets[cropname] = babydatasets[cropname] + list(zip(croplists1[cropname], croplists2[cropname], croplists3[cropname], croplists4[cropname]))
    del croplists1; del croplists2; del croplists3; del croplists4

for name, dataset in babydatasets.items():
    df = pd.DataFrame(data = dataset, columns=['band1','band2','band3', 'band4'])
    df.to_csv(cropname+'.csv',index=False,header = False)