from osgeo import gdal, osr, ogr, gdal_array
import os
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
lat = []; lon = []
for i in os.listdir('./'):
    if i[-4:] == '.tif':
        cd = gdal.Open(i)
        cd_cs = osr.SpatialReference()
        cd_cs.ImportFromWkt(cd.GetProjectionRef())
        cd_gt = cd.GetGeoTransform()
        cd_ncols = cd.RasterXSize
        cd_nrows = cd.RasterYSize
        s = {1:(0,0),2:(0,cd_nrows),3:(cd_ncols,0),4:(cd_ncols, cd_nrows)}
        l ={key:(cd_gt[0]+ value[0]*cd_gt[1]+value[1]*cd_gt[2],cd_gt[3]+ value[0]*cd_gt[4]+value[1]*cd_gt[5]) for key, value in s.items()}
        transform = osr.CoordinateTransformation(cd_cs,new_cs)
        for z in l.values():
            x = transform.TransformPoint(z[0],z[1])
            lat.append(x[0])
            lon.append(x[1])

print('minimum latitude:', min(lat))
print('maximum latitude:', max(lat))
print('minimum longitude:', min(lon))
print('maximum latitude:', max(lon))