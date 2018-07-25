from osgeo import gdal, osr, gdal_array
import os
import time
import pickle
import collect
import numpy as np

def check_in_file(sd, coordinate):
	sd_ncols = sd.RasterXSize
	sd_nrows = sd.RasterYSize
	sd_gt = sd.GetGeoTransform()
	sd_cs= osr.SpatialReference()
	sd_cs.ImportFromWkt(sd.GetProjectionRef())
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
	transform = osr.CoordinateTransformation(new_cs,sd_cs)
	new_location = transform.TransformPoint(coordinate[0],coordinate[1])
	x = int((new_location[0]-sd_gt[0])/sd_gt[1])
	y = int((new_location[1]-sd_gt[3])/sd_gt[5])
	if y>=0 and y<sd_nrows and x>=0 and sd < sd_ncols:
		return (gdal_array.DatasetReadAsArray(sd,x,y,1,1)[:,0,0] != np.array([0,0,0,0,0])).any()
	else:
		return False

def check_download(coordinate, year):
	lin = []
	for month_folder in os.listdir('./satdata/'+year):
		try:
			l = ['./satdata/'+year+'/' + month_folder + '/'+t for t in os.listdir('./satdata/'+year+'/' + month_folder)]
		except NotADirectoryError:
			continue
		s = 'not in image'
		for each_file in l:
			if each_file[-4:] != '.tif':
				continue
			sd = gdal.Open(each_file)
			if check_in_file(sd, coordinate):
				s = 'in image'
				break
		if s == 'not in image':
			list_element = collect.find_image(coordinate,year, month_folder, cloud_cover = 0.1)
			if len(list_element) == 0:return None
			else: lin.append(list_element)
	collect.add_to_queue(lin)	
	
def file_checker(file_name,details, year):
	if file_name in details: t = details[file_name]
	else: t = 0
	cd = gdal.Open(file_name)
	cd_ncols = cd.RasterXSize
	cd_nrows = cd.RasterYSize
	cd_gt = cd.GetGeoTransform()
	cd_cs= osr.SpatialReference()
	cd_cs.ImportFromWkt(cd.GetProjectionRef())
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
	transform = osr.CoordinateTransformation(cd_cs, new_cs)
	for i in range(t, cd_ncols, 10):
		for j in range(0, cd_nrows, 10):
			if int(gdal_array.DatasetReadAsArray(cd,i,j,1,1)) != 0:
				o1 = cd_gt[0] + i * cd_gt[1] + j* cd_gt[2]
				o2 = cd_gt[3] + i * cd_gt[4] + j* cd_gt[5]
				coordinate = transform.TransformPoint(o1,o2)
				check_download(coordinate, year)
		details[file_name] = i+10
		file_object = open('automated_downloading.pkl', 'wb')
		pickle.dump(details, file_object)
		file_object.close()
	
def check_satdata():
	try:
		file_object = open('automated_downloading.pkl', 'rb')
		details = pickle.load(file_object)
		file_object.close()
	except FileNotFoundError:
		details= {}
	all_files = os.listdir('./crop_data')
	for one_file in all_files:
		year = one_file[4:8]
		file_name = './crop_data/' + one_file
		file_checker(file_name, details, year)