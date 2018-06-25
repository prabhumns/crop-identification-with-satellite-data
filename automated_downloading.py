from osgeo import gdal, osr
import os
import time
import pickle
import collect1

def check_band_value(sd, x, y, sd_ncols, sd_nrows):
	count =  sd.RasterCount
	for i in range(1, count+1):
		sd_data = sd.GetRasterBand(i).ReadAsArray(0, 0, sd_ncols, sd_nrows)
		if sd_data[y][x] != 0:
			return True
	return False

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
	if x in range(sd_ncols) and y in range(sd_nrows):
		return check_band_value(sd, x,y, sd_ncols, sd_ncols)
	else:
		return False

def check_download(coordinate):
	dicti = {}
	for month_folder in os.listdir('./satdata'):
		try:
			l = os.listdir('./satdata/' + month_folder)
		except NotADirectoryError:
			continue
		s = 'not in image'
		for each_file in l:
			if each_file[-4:] != '.tif':
				continue
			sd = gdal.Open('./satdata/' + month_folder+ '/' + each_file)
			if check_in_file(sd, coordinate):
				s = 'in image'
				break
		if s == 'not in image':
			find_image_text, dicti[month_folder] = collect1.find_image(coordinate, month_folder, cloud_cover = 0.1)
			if find_image_text == 'no image':
				break
		if month_folder == os.listdir('./satdata')[-1]:
			collect1.add_to_queue(list(dicti.values()))	
		

def file_checker(new_file,lis):
	cd = gdal.Open(new_file)
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
	cd_data = cd.GetRasterBand(1).ReadAsArray(0, 0, cd_ncols, cd_nrows)
	crop_data_details = lis[1]
	if new_file in crop_data_details:
		tup = crop_data_details[new_file]
		cols_beginning = tup[0]
		rows_beginning = tup[1]
	else:
		cols_beginning = 0
		rows_beginning = 0
		crop_data_details[new_file] = (0,0)
	for i in range(cols_beginning, cd_ncols, 10):
		if i == cols_beginning and rows_beginning < cd_nrows:
			for j in range(rows_beginning,cd_nrows, 10):
				if cd_data[j][i] != 0:
					o1 = cd_gt[0] + i * cd_gt[1] + j* cd_gt[2]
					o2 = cd_gt[3] + i * cd_gt[4] + j* cd_gt[5]
					coordinate = transform.TransformPoint(o1,o2)
					check_download(coordinate)
					crop_data_details[new_file] = (i, j+10)
					lis = [lis[0], crop_data_details]
					file_object = open('automated_downloading.pkl', 'wb')
					pickle.dump(lis, file_object)
					file_object.close()
		else:
			for j in range(0,cd_nrows,10):
				if cd_data[j][i] !=0:
					o1 = cd_gt[0] + i * cd_gt[1] + j* cd_gt[2]
					o2 = cd_gt[3] + i * cd_gt[4] + j* cd_gt[5]
					coordinate = transform.TransformPoint(o1,o2)
					check_download(coordinate)	
					crop_data_details[new_file] = (i, j+10)
					lis = [lis[0], crop_data_details]
					file_object = open('automated_downloading.pkl', 'wb')
					pickle.dump(lis, file_object)
					file_object.close()
	
def check_satdata():
	file_object = open('automated_downloading.pkl', 'rb')
	lis = pickle.load(file_object)
	file_object.close()
	last_checked_time = lis[0]
	crop_data_list = os.listdir('./crop_data')
	new_files = []
	for crop_data_file in crop_data_list:
		#print(last_checked_time)
		modified_time = os.stat('./crop_data/' + crop_data_file)[8]
		#print(modified_time)
		if modified_time < last_checked_time:
			new_files.append('./crop_data/' + crop_data_file)
	for new_file in new_files:
		file_checker(new_file, lis)
	file_object = open('automated_downloading.pkl', 'wb')
	pickle.dump(time.time(), file_object)
	file_object.close()