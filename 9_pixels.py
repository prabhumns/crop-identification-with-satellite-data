import h5py
import tables
import time
from osgeo import gdal, osr, ogr, gdal_array
import os
import numpy as np
from numpy.linalg import inv
import pickle
from shutil import copyfile

#sat_file = 'E:/Time Series/satdata/12/1557907_2016-12-29_RE1_3A_Analytic.tif'

def Convert(k, old_gt, old_cs, new_cs):
	a = k[0]; s= k[1]
	transform = osr.CoordinateTransformation(old_cs,new_cs)
	o1 = old_gt[0] + a*old_gt[1] + s*old_gt[2]
	o2 = old_gt[3] + a*old_gt[4] + s*old_gt[5]
	d = transform.TransformPoint(o1,o2)
	return (d[0],d[1])

def calculate(a, g):
	B= np.mat([[a[0]-g[0]],[a[1]-g[3]]])
	A = np.mat([[g[1],g[2]],[g[4],g[5]]])
	X = inv(A) * B
	return (int(X[0]), int(X[1]))


def Crop(i,j, sdb_gt, sdb_cs):
	lis = os.listdir(main_folder + '/crop_data')
	for crop_file in lis:
		if crop_file[-4:] == '.tif':
			cd = gdal.Open(main_folder + '/crop_data/' + crop_file)
			cd_gt = cd.GetGeoTransform()
			cd_cs = osr.SpatialReference()
			cd_cs.ImportFromWkt(cd.GetProjectionRef())
			q = Convert((i,j), old_gt = sdb_gt, old_cs = sdb_cs, new_cs = cd_cs)
			ww = calculate(q, cd_gt)
			#print(ww)
			x = ww[0]; y = ww[1]
			if x >= 0 and x < cd.RasterXSize and y >=0 and y < cd.RasterYSize:
				return int(gdal_array.DatasetReadAsArray(cd, x,y,1, 1))
	return 0
			
def check_crop_data(i,j,sdb_gt,sdb_cs, crops):
	sdb_gt = sdb.GetGeoTransform()
	sdb_cs = osr.SpatialReference()
	sdb_cs.ImportFromWkt(sdb.GetProjectionRef())
	p = Crop(i, j, sdb_gt, sdb_cs)
	if p in crops:
		if Crop(i+1, j, sdb_gt, sdb_cs) == p:
			if Crop(i, j+1, sdb_gt, sdb_cs) == p:
				if Crop(i+1, j+1, sdb_gt, sdb_cs) == p:
					return crops[p]
				else:
					return 'USELESS'
			else:
				return 'USELESS'
		else:
			return 'USELESS'
	else:
		return 'USELESS'

def find_data(t, f):
	if t>=0 and t<sdb_ncols and f >=0 and f<sdb_nrows:
		return sdb_data[:,f,t]
	return np.array([0,0,0,0,0])
def check_centre(i,j):
	a = find_data(i-1,j-1)
	b = find_data(i, j-1)
	c = find_data(i+1, j-1)
	d = find_data(i-1, j)
	e = find_data(i, j)
	f = find_data(i+1,j)
	g = find_data(i-1, j+1)
	h = find_data(i, j+1)
	i = find_data(i+1, j+1)
	if (a != np.array([0,0,0,0,0])).any() and (b != np.array([0,0,0,0,0])).any() and (c != np.array([0,0,0,0,0])).any() and (d != np.array([0,0,0,0,0])).any() and (e != np.array([0,0,0,0,0])).any() and (f != np.array([0,0,0,0,0])).any() and (g != np.array([0,0,0,0,0])).any() and (h != np.array([0,0,0,0,0])).any() and (i != np.array([0,0,0,0,0])).any():
		return [t for n in [a,b,c,d,e,f,g,h,i] for t in list(n)] 
	else:
		return []
def check_length(dic):
	for value in dic.values():
		if value < 20000:
			return False
	return True

if __name__ == '__main__':
	sat_file = 'E:/crop_identification_with_satellite_data/1557907_2016-09-05_RE5_3A_Analytic.tif'
	main_folder = 'E:/Time Series'
	crops = {1:'CORN', 5:'SOYABEENS', 36:'ALFALFA', 111:'WATER_BODY', 121:'DEVELOPED', 122:'DEVELOPED', 123:'DEVELOPED', 124:'DEVELOPED'}
	t = 0
	num = {}
	for value in crops.values():
		num[value] = 0
	if 	'9_pixels2.pkl' in os.listdir('E:/Time Series'):
		file_object = open('E:/Time Series/9_pixels2.pkl', 'rb')
		lidas = pickle.load(file_object)
		file_object.close()
		t = lidas[0]; num = lidas[1]
	print(t)
	data = {}
	sdb = gdal.Open(sat_file)
	sdb_ncols = sdb.RasterXSize
	sdb_nrows = sdb.RasterYSize
	sdb_gt = sdb.GetGeoTransform()
	sdb_cs = osr.SpatialReference()
	sdb_cs.ImportFromWkt(sdb.GetProjectionRef())
	sdb_data = gdal_array.DatasetReadAsArray(sdb,0,0,sdb_ncols, sdb_nrows)
	for i in range(t, sdb_ncols):
		for j in range(sdb_nrows):
			example = check_centre(i, j)
			if len(example) == 45:
				crop_name = check_crop_data(i,j,sdb_gt,sdb_cs, crops)
				if crop_name != 'USELESS':
					if crop_name in num:
						if num[crop_name] < 20000:
							try:
								data[crop_name].append(example)
							except KeyError:
								data[crop_name] = [example]
							num[crop_name] =num[crop_name]+1
					else:
						try:
							data[crop_name].append(example)
						except KeyError:
							data[crop_name] = [example]
						num[crop_name] =num[crop_name]+1
		print(i)
		if i%100 == 0:
			print('saving', i)
			for key, value in data.items():
				key1 = 'E:/Time Series/hdf_files2/'+key
				key2 = 'E:/Time Series/hdf_files2_backup/'+key+'.bkp'
				old_examples = []
				if key in os.listdir('E:/Time Series/hdf_files2'):
					f = h5py.File(key1, 'r')
					old_examples = list(list(f.values())[0])
					f.close()
				h5file = tables.open_file(key1, mode='w', title="Test Array")
				root  = h5file.root
				h5file.create_array(root, "test", old_examples + value)
				h5file.close()
				copyfile(key1, key2)
				print(key, '----', len(old_examples + value))
			file_object = open('E:/Time Series/9_pixels2.pkl', 'wb')
			pickle.dump([i+1, num], file_object)
			file_object.close()
			copyfile('E:/Time Series/9_pixels2.pkl','E:/Time Series/9_pixels2.bkp' )
			print('done saving')
			data = {}
			if check_length(num):
				break		