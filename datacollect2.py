from osgeo import osr, gdal
import sys
import pandas as pd
main_folder = 'E:/Time Series'
def Convert(i,j, sd_gt, sd_cs, cd_cs):
    transform = osr.CoordinateTransformation(sd_cs,cd_cs)
    o1 = sd_gt[0] + i *sd_gt[1] + j*sd_gt[2]
    o2 = sd_gt[3] + i *sd_gt[4] + j*sd_gt[5]
    return transform.TransformPoint(o1,o2)

def Crop(i,j, sd_gt, sd_cs, cd_cs,cd_gt, cd_data):
    q = Convert(i,j, sd_gt = sd_gt, sd_cs = sd_cs, cd_cs = cd_cs)
    x = int((q[0]-cd_gt[0])/cd_gt[1])
    y = int((q[1]-cd_gt[3])/cd_gt[5])
    try: 
        return cd_data[y][x]
    except IndexError:
        return 0

def YRN(i,j,sd_gt, sd_cs,cd_cs,cd_gt, cd_data, crops):
    p = Crop(i,j,sd_gt = sd_gt, sd_cs = sd_cs,cd_gt =cd_gt, cd_cs = cd_cs, cd_data = cd_data)
    if p in crops:
        if Crop(i,j+1,sd_gt = sd_gt, sd_cs = sd_cs, cd_cs = cd_cs,cd_gt =cd_gt, cd_data = cd_data) == p:
            if Crop(i+1,j, sd_gt = sd_gt, sd_cs = sd_cs, cd_cs = cd_cs,cd_gt =cd_gt, cd_data = cd_data) == p:
                if Crop(i+1,j+1,sd_gt = sd_gt, sd_cs = sd_cs, cd_cs = cd_cs,cd_gt =cd_gt, cd_data = cd_data) == p:
                    return crops[p]
                else:
                    return 'USELESS'
            else:
                return 'USELESS'
        else:
            return 'USELESS'
    else:
        return 'USELESS'

def processsat(file, crops,cd_gt,number_of_examples,number, band1, band2, band3, band4, crop, cd_cs, cd_data):
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
    k = 0
    for i in range(sd_ncols):
        for j in range(sd_nrows):
            while k < len(num)*number:
                a = sd_data1[j][i]; b = sd_data2[j][i]; c = sd_data3[j][i]; d = sd_data4[j][i]
                print ('collecting data', i*j)
                if a != 0 or b != 0 or c!= 0 or d!= 0:
                    yrn = YRN(i,j,sd_gt = sd_gt, sd_cs = sd_cs,cd_cs = cd_cs,cd_gt=cd_gt, cd_data =cd_data, crops= crops)
                    if yrn != 'USELESS' and number_of_examples[yrn] < number:
                        number_of_examples[yrn] += 1
                        band1.append(a)
                        band2.append(b)
                        band3.append(c)
                        band4.append(d)
                        crop.append(yrn); k = k+1

def collect(number):

    band1 = []
    band2 = []
    band3 = []
    band4 = []
    crop = []

    crops = {1:'CORN', 176:'GRASS OR PASTURE', 5:'SOYABEENS', 121:'DEVELOPED',190:'WETLANDS',36:'ALFALFA',122:'DEVELOPED',111:'WATERBODY',141:'FOREST',195:'WETLANDS',123:'DEVELOPED',24:'SOYABEENS',4:'SORGHUM',61:'CROPLAND'} #number:cropname
    number_of_examples = {}
    for values in crops.values():
        number_of_examples[values] = 0
    cd = gdal.Open('./Cropdata/Cropdata.tif')
    cd_ncols = cd.RasterXSize
    cd_nrows = cd.RasterYSize
    cd_gt = cd.GetGeoTransform()
    cd_band = cd.GetRasterBand(1)
    cd_data = cd_band.ReadAsArray(0, 0, cd_ncols, cd_nrows)
    cd_cs= osr.SpatialReference()
    cd_cs.ImportFromWkt(cd.GetProjectionRef())

    satfiles = ['./Satdata1/Satdata1/Satdata1.tif']
    for file in satfiles:
        processsat(file,crop = crop, band1= band1,number = number, number_of_examples = number_of_examples, band2 = band2, band3 = band3, band4 = band4, crops = crops, cd_gt = cd_gt, cd_data = cd_data, cd_cs = cd_cs)
    for cropname, numb in number_of_examples:
        if numb < number:
            print('got only', numb, 'labelled exaples for', cropname)
    cols = ['band1','band2','band3', 'band4', 'cropname']
    babydataset = list(zip(band1,band2, band3, band4, crop))
    df = pd.DataFrame(data = babydataset, columns = cols)
    df.to_csv('entiredata.csv', header = True, index = True)
    return df

