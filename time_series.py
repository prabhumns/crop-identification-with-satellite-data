from osgeo import gdal, osr, ogr, gdal_array
import os
import numpy as np
from numpy.linalg import inv
import pickle
from random import shuffle
from shutil import copyfile
main_folder ='E:/Time Series'
base_month = '12'
crops = {1:'CORN',4:'SORGHUM', 5:'SOYABEENS', 13:'POP OR ORN', 36:'ALFALFA', 28:'OATS', 27:'RYE', 53:'PEAS', 111:'WATER BODY', 121:'DEVELOPED', 122:'DEVELOPED', 123:'DEVELOPED', 124:'DEVELOPED',141:'FOREST', 142:'FOREST',243:'CABBAGE' }

def create_ogr_polygons(poly_corners):
	ogr_poly = {}
	for key, value in poly_corners.items():
		ring = ogr.Geometry(ogr.wkbLinearRing)
		for t in value:
			ring.AddPoint(t[0]*10000,t[1]*10000)
		ring.AddPoint(value[0][0]*10000, value[0][1]*10000)
		poly = ogr.Geometry(ogr.wkbPolygon)
		poly.AddGeometry(ring)
		ogr_poly[key] = poly
	return ogr_poly


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

def calculate2(a, g):
	B= np.mat([[a[0]-g[0]],[a[1]-g[3]]])
	A = np.mat([[g[1],g[2]],[g[4],g[5]]])
	X = inv(A) * B
	return (X[0,0], X[1,0])
	
def common_area(w,l, sd_cs, sd_gt, sdb_gt, sdb_cs):
	x= w[0]; y = w[1]
	poly_corners = {}
	poly_corners[1] = [calculate2(Convert(a,sdb_gt, sdb_cs, sd_cs),sd_gt) for a in l]
	poly_corners[2] = [(x,y),(x+1,y),(x+1,y+1),(x,y+1)]
	wgs84_wkt = """
	GEOGCS["WGS 84",
		DATUM["WGS_1984",
			SPHEROID["WGS 84",6378137,298.257223563,
				AUTHORITY["EPSG","7030"]],
			AUTHORITY["EPSG","6326"]],
		PRIMEM["Greenwich",0,
			AUTHORITY["EPSG","8901"]],
		UNIT["degree",0.01745329251994328,
			AUTHORITY["EPSG","9122"]],
		AUTHORITY["EPSG","4326"]]"""
	new_cs = osr.SpatialReference()
	new_cs.ImportFromWkt(wgs84_wkt)  
	poly_corner = {key:[Convert(s, sd_gt, sd_cs, new_cs) for s in value]for key, value in poly_corners.items()}
	ogr_polygons = create_ogr_polygons(poly_corner)
	intersection = ogr_polygons[1].Intersection(ogr_polygons[2])
	try: 
		return intersection.GetArea()
	except AttributeError:
		return 0.0

def each_file_checker(file, i,j, sdb):
	sdb_gt = sdb.GetGeoTransform()
	sdb_cs = osr.SpatialReference()
	sdb_cs.ImportFromWkt(sdb.GetProjectionRef())
	sd = gdal.Open(file)
	sd_gt = sd.GetGeoTransform()
	sd_cs = osr.SpatialReference()
	sd_cs.ImportFromWkt(sd.GetProjectionRef())
	sd_ncols = sd.RasterXSize
	sd_nrows = sd.RasterYSize	
	l = [(i,j),(i+1,j),(i+1,j+1),(i,j+1)] #sdb_gt, sdb_cs
	s = [calculate(Convert(ton, old_gt = sdb_gt, old_cs = sdb_cs, new_cs=sd_cs), sd_gt) for ton in l] #sd_cs, #sd_gt
	lat = (min([I[0] for I in s]),max([I[0] for I in s]))
	lon = (min([I[1] for I in s]),max([I[1] for I in s]))
	area = 0.0; total_band_values = np.array([0,0,0,0,0])
	for q in range(lat[0], lat[1]+1):
		for w in range(lon[0], lon[1]+1):
			x = (q,w) #sd_cs, sd_gt
			if q>=0 and q< sd_ncols and w >= 0 and w< sd_nrows:
				band_value = gdal_array.DatasetReadAsArray(sd,q,w ,1, 1)[:,0,0]
				area2 = common_area(x,l, sd_cs, sd_gt, sdb_gt, sdb_cs)
				if area2!=0.0 and (band_value == np.array([0,0,0,0,0])).all():
					return np.array([0,0,0,0,0])
				area = area + area2; total_band_values = total_band_values + band_value*area2
	if area != 0:
		return total_band_values/area
	else: return np.array([0,0,0,0,0])
			
def any_band_value(i, j, sdb, month):
	lis = os.listdir(main_folder + '/satdata/'+month)
	for each_file in lis:
		if each_file[-4:] == '.tif':
			each_file2 = main_folder + '/satdata/'+month+'/'+each_file
			band_values = each_file_checker(each_file2, i,j, sdb)
			if (band_values != np.array([0,0,0,0,0])).any():
				return band_values
			else: continue
	return np.array([0,0,0,0,0])
			

def check_other_month_satdata(i, j, sdb):
	lit = os.listdir(main_folder + '/satdata')
	band_values = {}
	months_list = ['07','08','09','10','11'] #lit - [base_month]
	for month in months_list:
		bandvalues = any_band_value(i,j, sdb, month)
		if (bandvalues != np.array([0,0,0,0,0])).any():
			band_values[month] = bandvalues
		else:
			#print('not found in month', month)
			return {}
	return band_values


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

def save_now(ss,pra, pick_pixel,base_month, data, linad):
	for key, value in data.items():
		print(key, 'has', len(value), 'examples')
	dicti['looped_till'] = {'sss':ss, 'last_stop': pra+1, 'pick_pixel':pick_pixel}
	dicti['base_month'] = base_month
	dicti['data'] = data
	dicti['list of base month files'] = linad
	file_object = open(main_folder + '/data_collect4.pkl', 'wb')
	pickle.dump(dicti, file_object)
	file_object.close()
	copyfile ('data_collect4.pkl', 'data_collect4.bkp')

def check(pixel,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil):
	if pra%10000 ==0:
		print('saving', pra)
		save_now(ss,pra, pick_pixel,base_month, data, linad)
		print('b')
	i = pixel[0]; j =pixel[1]
	band_values_base = sdb_data[:,j,i]
	#if (band_values_base != np.array([0,0,0,0,0])).any():
	crop_name = check_crop_data(i, j, sdb_gt, sdb_cs, crops)
	if crop_name != 'USELESS':
		#print(crop_name)
		band_values = check_other_month_satdata(i,j, sdb)
		if len(band_values) !=0:
			band_values[base_month] = band_values_base
			band_values['info'] = {'base_month': base_month, 'file_name':fil, 'pixel_position': (i,j)}
			try:
				data[crop_name].append(band_values)
			except KeyError:
				data[crop_name] = [band_values]
	return data
			#check((i-1, j-1), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
			#check((i-1, j), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
			#check((i-1, j+1), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
			#check((i, j-1), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
			#check((i, j+1), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
			#check((i+1, j-1), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
			#check((i+1, j), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
			#check((i+1, j+1), pixelTF,n,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)

if __name__ == '__main__':
	month_folders = {month : os.listdir(main_folder + '/satdata/' +month) for month in os.listdir(main_folder + '/satdata')}
	linad = month_folders[base_month]
	try:
		file_object = open(main_folder + '/data_collect4.pkl', 'rb')
		dicti = pickle.load(file_object)
		file_object.close()
		data = dicti['data']
		looped_till = dicti['looped_till']
		sss = looped_till['sss']
		last_stop = looped_till['last_stop']
		pick_pixel = looped_till['pick_pixel']
		linad = dicti['list of base month files']
	except FileNotFoundError:
		dicti = {}
		data = {}
		last_stop=0
		sss = 0
		shuffle(linad)
	for ss in range(sss, len(linad)):
		fil = linad[ss]
		if fil[-4:] == '.tif':
			sdb = gdal.Open(main_folder + '/satdata/'+base_month + '/' + fil)
			sdb_ncols = sdb.RasterXSize
			sdb_nrows = sdb.RasterYSize
			sdb_gt = sdb.GetGeoTransform()
			sdb_cs = osr.SpatialReference()
			sdb_cs.ImportFromWkt(sdb.GetProjectionRef())
			sdb_data = gdal_array.DatasetReadAsArray(sdb,0,0,sdb_ncols, sdb_nrows)
			if ss != sss or last_stop == 0:	
				last_stop = 0
				pick_pixel = [(i,j) for i in range(sdb_ncols) for j in range(sdb_nrows) if (sdb_data[:,j,i] != np.array([0,0,0,0,0])).any()]
				print('done creating pick_pixel')
			for pra in range(last_stop,len(pick_pixel)):
				data = check(pick_pixel[pra],ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil)
		exit()