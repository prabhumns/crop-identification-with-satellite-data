<<<<<<< HEAD
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time
import sys

def location_date_cloud_satellite(l,start_date, end_date, cloud_cover_less = 0.05, satellite = "REOrthoTile"):
	if type(l[0]) == list:
		geo_json_geometry = {"type": "Polygon","coordinates": [l]}
	elif type(l[0]) == float:
		geo_json_geometry = {"type": "Point","coordinates": l}
	geometry_filter = {  "type": "GeometryFilter",  "field_name": "geometry",  "config": geo_json_geometry}
	start_date = start_date + "T00:00:00.000Z" ; end_date = end_date + "T00:00:00.000Z"
	date_range_filter = {  "type": "DateRangeFilter",  "field_name": "acquired",  "config": {"gte": start_date, "lte": end_date}}
	cloud_cover_filter = { "type": "RangeFilter",  "field_name": "cloud_cover",  "config": { "lte": cloud_cover_less }}
	redding_reservoir = {  "type": "AndFilter",  "config": [geometry_filter, date_range_filter, cloud_cover_filter] }
	search_endpoint_request = {"item_types": [satellite], "filter": redding_reservoir}
	return search_endpoint_request

l = [[-90.000, 40.000],[-90.000,30.000],[-80.000,30.0000],[-80.0000,40.0000]]
start_date = "2016-01-"
end_date = "2017-07-30"
cloud_cover_less = 0.05
ser = location_date_cloud_satellite(l,start_date, end_date, cloud_cover_less = cloud_cover_less)

emailid = "me16b022@smail.iitm.ac.in"
password = "howareyou"
session = requests.Session()
session.auth = (emailid,password) 
search_result = session.post('https://api.planet.com/data/v1/quick-search', json=ser).json()

def download(image, session):
    item_id = image['id']
    item = session.get(image['_links']['assets'])
    asset_type = "analytic"
    session.auth = (emailid,password) 
    item_activation_url = item.json()[asset_type]["_links"]["activate"] #link to activate
    response = session.post(item_activation_url) #activating
    
    item_status = item.json()[asset_type]["status"]
    while item_status != 'active':
        time.sleep(2) 
        print('still inactive')
        item = session.get(image['_links']['assets'])
        item_status = item.json()[asset_type]["status"]

    download_link = item.json()[asset_type]["location"]
    file_name = item_id + '.tif'
    with open(file_name, "wb") as f:
            print ("Downloading %s" % file_name)
            response = session.get(download_link, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                    sys.stdout.flush()
    return file_name
    
month_wise_images = {}
for single_image in search_result['features']:
    try:
        month_wise_images[single_image['properties']['acquired'][5:7]].append(single_image)
    except KeyError:
        month_wise_images[single_image['properties']['acquired'][5:7]] = [single_image]

downloading_images = []
for key, value in month_wise_images.items():
    print (len(value),' images are available for this AOI belonging to ', key, 'th month')
    downloading_images.append(value[0])

for image in downloading_images:
    file_name = download(image, session)
    cwd = os.getcwd()
=======
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time
import sys

def location_date_cloud_satellite(l,start_date, end_date, cloud_cover_less = 0.05, satellite = "REOrthoTile"):
	if type(l[0]) == list:
		geo_json_geometry = {"type": "Polygon","coordinates": [l]}
	elif type(l[0]) == float:
		geo_json_geometry = {"type": "Point","coordinates": l}
	geometry_filter = {  "type": "GeometryFilter",  "field_name": "geometry",  "config": geo_json_geometry}
	start_date = start_date + "T00:00:00.000Z" ; end_date = end_date + "T00:00:00.000Z"
	date_range_filter = {  "type": "DateRangeFilter",  "field_name": "acquired",  "config": {"gte": start_date, "lte": end_date}}
	cloud_cover_filter = { "type": "RangeFilter",  "field_name": "cloud_cover",  "config": { "lte": cloud_cover_less }}
	redding_reservoir = {  "type": "AndFilter",  "config": [geometry_filter, date_range_filter, cloud_cover_filter] }
	search_endpoint_request = {"item_types": [satellite], "filter": redding_reservoir}
	return search_endpoint_request

l = [[-90.000, 40.000],[-90.000,30.000],[-80.000,30.0000],[-80.0000,40.0000]]
start_date = "2016-01-"
end_date = "2017-07-30"
cloud_cover_less = 0.05
ser = location_date_cloud_satellite(l,start_date, end_date, cloud_cover_less = cloud_cover_less)

emailid = "me16b022@smail.iitm.ac.in"
password = "howareyou"
session = requests.Session()
session.auth = (emailid,password) 
search_result = session.post('https://api.planet.com/data/v1/quick-search', json=ser).json()

def download(image, session):
    item_id = image['id']
    item = session.get(image['_links']['assets'])
    asset_type = "analytic"
    session.auth = (emailid,password) 
    item_activation_url = item.json()[asset_type]["_links"]["activate"] #link to activate
    response = session.post(item_activation_url) #activating
    
    item_status = item.json()[asset_type]["status"]
    while item_status != 'active':
        time.sleep(2) 
        print('still inactive')
        item = session.get(image['_links']['assets'])
        item_status = item.json()[asset_type]["status"]

    download_link = item.json()[asset_type]["location"]
    file_name = item_id + '.tif'
    with open(file_name, "wb") as f:
            print ("Downloading %s" % file_name)
            response = session.get(download_link, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                    sys.stdout.flush()
    return file_name
    
month_wise_images = {}
for single_image in search_result['features']:
    try:
        month_wise_images[single_image['properties']['acquired'][5:7]].append(single_image)
    except KeyError:
        month_wise_images[single_image['properties']['acquired'][5:7]] = [single_image]

downloading_images = []
for key, value in month_wise_images.items():
    print (len(value),' images are available for this AOI belonging to ', key, 'th month')
    downloading_images.append(value[0])

for image in downloading_images:
    file_name = download(image, session)
    cwd = os.getcwd()
>>>>>>> b1d77540898af5ff5f5be875cbd0eee6732525ba
    os.rename(cwd+'\\'+file_name, cwd+'\\'+single_image['properties']['acquired'][5:7] + '\\'+file_name)