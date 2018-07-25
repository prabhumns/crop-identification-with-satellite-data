import simplejson
import os
import requests
import time
import sys	
import pickle
import json
from shapely.geometry import shape, Point
import urllib3

def get_que_files():
	try:
		file_object = open('collect.pkl','rb')
		in_queue_files = pickle.load(file_object)
		file_object.close()
	except FileNotFoundError:
		in_queue_files = []
	return in_queue_files

def check_queue():
	in_queue_files = get_que_files()
	while {} in in_queue_files:
		in_queue_files.remove({})
	lit = []
	for i in in_queue_files:
		if i in lit:
			continue
		lit.append(i)
	file_object = open('collect.pkl','wb')
	pickle.dump(lit, file_object)
	file_object.close()

def check_for_any_changes_satdata():
	check_queue()
	in_queue_files = get_que_files()
	for i in range(len(in_queue_files)):
		dicti = in_queue_files[i]
		if dicti['status'] != 'downloaded':
			lis = os.listdir('./'+dicti['month'])
			image = dicti['image']
			if image['id'] in lis:
				dicti['status'] = 'downloaded'
				in_queue_files[i] = dicti
	file_object = open('collect.pkl', 'wb')
	pickle.dump(in_queue_files, file_object)
	file_object.close()

def check_in_downloading_image(coordinate, image):
	polygon = shape(image['geometry'])
	point = Point(coordinate[0], coordinate[1])
	return polygon.contains(point)

def check_in_queue_files(coordinate,year, month):
	check_queue()
	in_queue_files = get_que_files()
	for i in in_queue_files:
		if len(i) == 0:
			print (i)
	for i in in_queue_files:
		if i['month'] == month and i['year'] == year:
			if check_in_downloading_image(coordinate, i['image']):
				return True
	return False
			

def location_date_cloud_satellite(l,start_date, end_date, cloud_cover_less = 0.10, satellite = "REOrthoTile"):
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

def download_images():
	check_queue()
	in_queue_files = get_que_files()
	for i in range(len(in_queue_files)):
		dicti = in_queue_files[i]
		if dicti['status'] == 'download not started':
			image = dicti['image']
			session = requests.Session()
			login = True
			while login: #logging into session
				try:
					session.auth = (emailid, password)
					login = False
				except NameError:
					emailid = input('Email Id: ')
					password = input('Password: ')
				except requests.exceptions.ConnectionError:
					print('check network connection')
					time.sleep(2)
			asset_type = "analytic"
			login = True
			while login: #getting activation link
				try:
					item = session.get(image['_links']['assets'])
				except requests.exceptions.ConnectionError:
					print('check network connection')
					time.sleep(2)
					continue
				if asset_type in item.json():
					item_activation_url = item.json()[asset_type]["_links"]["activate"]
					login = False
				elif 'message' in item.json():
					print ("wrong login details")
					emailid = input('Emailid: ' )
					password = input('Password: ')
					session.auth = (emailid, password)
				else:
					print ("account expired")
					emailid = input('Emailid: ' )
					password = input('Password: ')
					session.auth = (emailid, password)
			login = True
			while login: #activating
				try:
					session.post(item_activation_url) 
					login = False
				except requests.exceptions.ConnectionError:
					print('check network connection')
					time.sleep(2)
			download_image(dicti, emailid, password, in_queue_files, i, session)
		elif dicti['status'] == 'downloading started':
			session = requests.Session()
			session.auth = (dicti['emailid'], dicti['password'])
			download_image(dicti, dicti['emailid'], dicti['password'], in_queue_files, i, session)

def image_accounted(emailid, password, dicti, in_queue_files, i):
	dicti['emailid'] = emailid
	dicti['password'] = password
	dicti['status'] = 'downloading started'
	in_queue_files[i] = dicti
	file_object = open('collect.pkl', 'wb')
	pickle.dump(in_queue_files, file_object)
	file_object.close()
	return dicti
		

def download_image(dicti, emailid, password, in_queue_files, i, session):
	image = dicti['image']
	asset_type = "analytic"
	login =  True
	while login :
		try:
			item = session.get(image['_links']['assets'])
			login = False
		except requests.exceptions.ConnectionError:
			print('check network connection')
			time.sleep(2)
	item_status = item.json()[asset_type]["status"]
	while item_status != 'active': 
		time.sleep(2)
		login = True
		while login:
			try:
				item = session.get(image['_links']['assets'])
				login = False
			except requests.exceptions.ConnectionError:
				print('check network connection')
				time.sleep(2)
		item_status = item.json()[asset_type]["status"]
	download_link = item.json()[asset_type]["location"]
	file_name = dicti['image']['id'] + '.tif'
	with open(file_name, "wb") as f:
		print ("Downloading %s" % file_name)
		response = requests.get(download_link, stream=True)
		if dicti['status'] != 'downloading started':
			dicti = image_accounted(emailid, password, dicti, in_queue_files, i)
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
	month = dicti['month']; year = dicti['year']
	os.rename('./'+file_name, './satdata/'+year+'/' + month+'/'+file_name)
	dicti['status'] = 'downloaded'
	in_queue_files[i] = dicti
	file_object = open('collect.pkl', 'wb')
	pickle.dump(in_queue_files, file_object)
	file_object.close() 

def find_image(coordinate,year, month, cloud_cover):
	if check_in_queue_files(coordinate,year, month):
		return {}
	else:
		l = [coordinate[0], coordinate[1]]
		start_date = year + "-"+ month + "-01"
		one = ['01','03','05','07','08','10','12']
		zero = ['04','06','09','11']
		if month in one:
			end_date = year + "-" + month + "-31"
		elif month in zero:
			end_date = year + "-" + month + "-30"
		else:
			if int(year)%4 ==0:end_date = year + "-02-29"
			else: end_date = year + "-02-28"
		ser = location_date_cloud_satellite(l,start_date, end_date, cloud_cover_less = cloud_cover)
		session = requests.Session()
		emailid = 'prabhumns123@gmail.com'
		password = 'prabhu123'
		login = True
		while login:
			try:
				session.auth = (emailid,password)
				login = False
			except requests.exceptions.ConnectionError:
				print('check network connection')
				time.sleep(2)
		login = True
		while login:
			try:
				search_result = session.post('https://api.planet.com/data/v1/quick-search', json=ser).json()
				login = False
			except requests.exceptions.ConnectionError:
				print('check network connection')
				time.sleep(2)
			except simplejson.scanner.JSONDecodeError:time.sleep(1)
		list_of_images = search_result["features"]
		if len(list_of_images) == 0: return {}
		else: return {'month':month, 'image':list_of_images[0],'year':year, 'status': 'download not started'}
			
def add_to_queue(listi):
	print('adding files to queue')
	check_queue()
	in_queue_files = get_que_files()
	in_queue_files = listi + in_queue_files
	file_object = open('collect.pkl', 'wb')
	pickle.dump(in_queue_files, file_object)
	file_object.close()
