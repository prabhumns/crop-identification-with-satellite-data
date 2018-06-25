from osgeo import gdal, osr, ogr, gdal_array
import os
import numpy as np
from numpy.linalg import inv
import pickle
from random import shuffle
gdal.UseExceptions() 
base_month = '12'
crops = {1:'CORN',4:'SORGHUM', 5:'SOYABEENS', 13:'POP OR ORN', 36:'ALFALFA', 28:'OATS', 27:'RYE', 53:'PEAS', 111:'WATER BODY', 121:'DEVELOPED', 122:'DEVELOPED', 123:'DEVELOPED', 124:'DEVELOPED',141:'FOREST', 142:'FOREST',243:'CABBAGE' }

def create_ogr_polygons(poly_corners):
	ogr_poly = {}
	for key, value in poly_corners.items():
		ring = ogr.Geometry(ogr.wkbLinearRing)
		for i in value:
			ring.AddPoint(i[0],i[1])
		poly = ogr.Geometry(ogr.wkbPolygon)
		poly.AddGeometry(ring)
		ogr_poly[key] = poly
	return ogr_poly


def Convert(k, old_gt, old_cs, new_cs):
	i = k[0]; j= k[1]
	transform = osr.CoordinateTransformation(old_cs,new_cs)
	o1 = old_gt[0] + i*old_gt[1] + j*old_gt[2]
	o2 = old_gt[3] + i*old_gt[4] + j*old_gt[5]
	l = transform.TransformPoint(o1,o2)
	return (l[0],l[1])

def calculate(i, g):
	B= np.mat([[i[0]-g[0]],[i[1]-g[3]]])
	A = np.mat([[g[1],g[2]],[g[4],g[5]]])
	X = inv(A) * B
	return (int(X[0]), int(X[1]))

def calculate2(i, g):
	B= np.mat([[i[0]-g[0]],[i[1]-g[3]]])
	A = np.mat([[g[1],g[2]],[g[4],g[5]]])
	X = inv(A) * B
	return (X[0,0], X[1,0])

def convert_to_lat_lon(poly_corners, sd_cs, sd_gt):
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
	poly_corner = {}
	for key, value in poly_corners.items():
		for i in value:
			poly_corner[key] = Convert(i, sdb_gt, sdb_cs, new_cs)
	return poly_corner
	
def common_area(w,l, sd_cs, sd_gt, sdb_gt, sdb_cs):
	x= w[0]; y = w[1]
	poly_corners = {}
	poly_corners[1] = [calculate2(Convert(i,sdb_gt, sdb_cs, sd_cs),sd_gt) for i in l]
	poly_corners[2] = [(x,y),(x+1,y),(x,y+1),(x+1,y+1)]
	poly_corner = convert_to_lat_lon(poly_corners,sd_cs, sd_gt)
	ogr_polygons = create_ogr_polygons(poly_corner)
	intersection = ogr_polygons[1].Intersection(ogr_polygons[2])
	return intersection.GetArea() 

def each_file_checker(file, i,j, sdb):
	sdb_gt = sdb.GetGeoTransform()
	sdb_cs = osr.SpatialReference()
	sdb_cs.ImportFromWkt(sdb.GetProjectionRef())
	sd = gdal.Open(file)
	sd_gt = sd.GetGeoTransform()
	sd_cs = osr.SpatialReference()
	sd_cs.ImportFromWkt(sd.GetProjectionRef())
	l = [(i,j),(i+1,j),(i,j+1),(i+1,j+1)] #sdb_gt, sdb_cs
	s = [calculate(Convert(ton, old_gt = sdb_gt, old_cs = sdb_cs, new_cs=sd_cs), sd_gt) for ton in l] #sd_cs, #sd_gt
	lat = (min([i[0] for i in s]),max([i[0] for i in s]))
	lon = (min([i[1] for i in s]),max([i[1] for i in s]))
	area = 0; total_band_values = np.array([0,0,0,0,0])
	for i in range(lat[0], lat[1]+1):
		for j in range(lon[0], lat[1]+1):
			x = (i,j) #sd_cs, sd_gt
			band_value = gdal_array.DatasetReadAsArray(sd,i,j ,1, 1)[:,0,0]
			area2 = common_area(x,l, sd_cs, sd_gt, sdb_gt, sdb_cs)
			#print(area2)
			if area2!=0 and (band_value == np.array([0,0,0,0,0])).all():
				return np.array([0,0,0,0,0])
			area = area + area2; total_band_values = total_band_values + band_value*area
	if area != 0:
		return total_band_values/area
	else: return np.array([0,0,0,0,0])
			
def any_band_value(i, j, sdb, month):
	lis = os.listdir('./satdata/'+month)
	for each_file in lis:
		if each_file[-4:] == '.tif':
			try:
				each_file2 = './satdata/'+month+'/'+each_file
				band_values = each_file_checker(each_file2, i,j, sdb)
			except TypeError:
				continue			
			if (band_values != np.array([0,0,0,0,0])).any():
				return band_values
	return np.array([0,0,0,0,0])
			

def check_other_month_satdata(i, j, sdb):
	lit = os.listdir('./satdata')
	band_values = {}
	months_list = ['08','09','10','11'] #lit - [base_month]
	for month in months_list:
		bandvalues = any_band_value(i,j, sdb, month)
		if (bandvalues != np.array([0,0,0,0,0])).any():
			band_values[month] = bandvalues
		else:
			return {}
	return band_values


def Crop(i,j, sdb_gt, sdb_cs):
	lis = os.listdir('./crop_data')
	for crop_file in lis:
		if crop_file[-4:] == '.tif':
			cd = gdal.Open('./crop_data/' + crop_file)
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
	for i, l in data.items():
		print(i, 'has', len(l), 'examples')
	dicti['looped_till'] = {'sss':ss, 'last_stop': pra+1, 'pick_pixel':pick_pixel}
	dicti['base_month'] = base_month
	dicti['data'] = data
	dicti['list of base month files'] = linad
	file_object = open('data_collect.pkl', 'wb')
	pickle.dump(dicti, file_object)
	file_object.close()

def check(pixel,ss,pra,pick_pixel,base_month, linad, sdb,sdb_gt, sdb_cs, crops,data,fil):
	if pra%1000 ==0:
		print('saving', pra)
		save_now(ss,pra, pick_pixel,base_month, data, linad)
	i = pixel[0]; j =pixel[1]
	band_values_base = sdb_data[:,j,i]
	#if (band_values_base != np.array([0,0,0,0,0])).any():
	crop_name = check_crop_data(i, j, sdb_gt, sdb_cs, crops)
	if crop_name != 'USELESS':
		band_values = check_other_month_satdata(i,j, sdb)
		if len(band_values) !=0:
			band_values[base_month] = band_values_base
			band_values['info'] = {'base_month': base_month, 'file_name':fil, 'pixel_position': (i,j)}
			print('success', crop_name)
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
	month_folders = {month : os.listdir('./satdata/' +month) for month in os.listdir('./satdata')}
	linad = month_folders[base_month]
	try:
		file_object = open('data_collect.pkl', 'rb')
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
			sdb = gdal.Open('./satdata/'+base_month + '/' + fil)
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