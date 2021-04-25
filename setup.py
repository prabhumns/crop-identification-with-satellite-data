import os
import json
import pickle
file_object = open('collect1.pkl', 'rb')
in_queue_files = pickle.load(file_object)
file_object.close()

metadata_files = []
lis = os.listdir('./satdata/10/planet_order_200514')
for i in lis:
	if i[:-4] != '.xml':
		lit = os.listdir('./satdata/10/planet_order_200514/'+ i)
		for l in lit:
			if l[-5:] == '.json':
				file_object = open('./satdata/10/planet_order_200514/'+ i+'/'+l)
				json_dict = json.load(file_object)
				file_object.close()
				print(type(json_dict))
				metadata_files.append(json_dict)

lis = os.listdir('./satdata/11/planet_order_200513')
for i in lis:
	lit = os.listdir('./satdata/11/planet_order_200513/'+ i)
	for l in lit:
		if l[:-5] == '.json':
			file_object = open('./satdata/11/planet_order_200513/'+ i+'/'+l)
			json_dict = json.load(file_object)
			file_object.close()
			print(type(json_dict))
			metadata_files.append(json_dict)

in_queue_files_images = [ dicti['image'] for dicti in in_queue_files]

for i in range(len(in_queue_files)):
	dicti = in_queue_files[i]
	if dicti['image'] in metadata_files:
		print(i)