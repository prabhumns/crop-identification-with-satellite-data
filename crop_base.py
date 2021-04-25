from osgeo import gdal, osr, ogr, gdal_array
import os
import numpy as np
from numpy.linalg import inv
import pickle
from random import shuffle


def Convert(k, old_gt, old_cs, g, new_cs):
	i = k[0]; j= k[1]
	transform = osr.CoordinateTransformation(old_cs,new_cs)
	o1 = old_gt[0] + i*old_gt[1] + j*old_gt[2]
	o2 = old_gt[3] + i*old_gt[4] + j*old_gt[5]
	i = transform.TransformPoint(o1,o2)
	B= np.mat([[i[0]-g[0]],[i[1]-g[3]]])
	A = np.mat([[g[1],g[2]],[g[4],g[5]]])
	X = inv(A) * B
	return (int(X[0]), int(X[1]))

def check(file_name, i,j, cd_gt, cd_cs):
	sd = gdal.Open(file_name)
	sd_gt = sd.GetGeoTransform()
	sd_cs = osr.SpatialReference()
	sd_cs.ImportFromWkt(sd.GetProjectionRef())
	sd_ncols = sd.RasterXSize
	sd_nrows  = sd.RasterYSize
	s = [Convert(l,cd_gt,cd_cs, sd_gt,sd_cs) for l in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]]
	lat = (min([i[0] for i in s]),max([i[0] for i in s]))
	lon = (min([i[1] for i in s]),max([i[1] for i in s]))  
	total_band_value = np.array([0,0,0,0,0])
	n= 0
	for i in range(lat[0], lat[1]+1):
		for j in range(lon[0], lon[1]+1):  
			if i>=0 and i< sd_ncols and j >= 0 and j< sd_nrows:
				band_value = gdal_array.DatasetReadAsArray(sd,i,j,1,1)[:,0,0]
				if (band_value != np.array([0,0,0,0,0])).any():
					total_band_value = total_band_value + band_value
					n= n+1
	if n == 0:
		return total_band_value
	else:
		return total_band_value/n

def find_sat_data(i, j, cd_gt, cd_cs):
	lit = os.listdir('./satdata')
	band_values = {}
	months_list = ['08','09','10','11', '12'] #lit - [base_month]
	for month in months_list:
		total_band_value = np.array([0,0,0,0,0]); n= 0
		for t in os.listdir('./satdata/'+month):
			file_name = './satdata/'+month+'/'+t
			each_file_value = check(file_name, i, j, cd_gt, cd_cs)
			if (each_file_value != np.array([0,0,0,0,0])).any() :
				total_band_value = total_band_value + each_file_value
				n = n+1
		if (total_band_value == np.array([0,0,0,0,0])).all():
			return {}
		else:
			band_values[month] = total_band_value/n
	return band_values

def save():
	print('saving',t)
	for key, values in data.items():
		print('for ', key, 'found ', len(values), ' examples')
	file_object = open('crop_base.pkl','wb')
	pickle.dump(data, file_object)
	file_object.close()

crops = {1:'CORN',4:'SORGHUM', 5:'SOYABEENS', 13:'POP OR ORN', 36:'ALFALFA', 28:'OATS', 27:'RYE', 53:'PEAS', 111:'WATER BODY', 121:'DEVELOPED', 122:'DEVELOPED', 123:'DEVELOPED', 124:'DEVELOPED',141:'FOREST', 142:'FOREST',243:'CABBAGE' }
crop_data_files = ['./crop_data/'+i for i in os.listdir('./crop_data/')]
data = {}
t = 0
for ll in crop_data_files:
	cd = gdal.Open(ll)
	cd_ncols = cd.RasterXSize
	cd_nrows = cd.RasterYSize
	cd_gt = cd.GetGeoTransform()
	cd_cs = osr.SpatialReference()
	cd_cs.ImportFromWkt(cd.GetProjectionRef())
	cd_data = gdal_array.DatasetReadAsArray(cd,0,0,cd_ncols, cd_nrows)
	ncols = list(range(cd_ncols)); shuffle(ncols)
	nrows = list(range(cd_nrows)); shuffle(nrows)
	for i in ncols:
		for j in nrows:
			t = t+1
			crop_number = cd_data[j,i]
			if crop_number in crops:
				band_values = find_sat_data(i,j,cd_gt, cd_cs)
				crop_name = crops[crop_number]
				if len(band_values)!= 0:
					try:
						data[crop_name].append(band_values)
					except KeyError:
						data[crop_name] = [band_values]
			if t%1000 ==0:
				save()