import automated_downloading
import collect1
import pickle

cla = input("type one of these: *check_new_crop_data* or *activate_satdata* or *get_download_links* or *download* or *check_changes_in_satdata* or *clear_automated_downloading* or *clear_collect1* or *both*\n")

if cla == 'check_new_crop_data':
	automated_downloading.check_satdata()
elif cla == 'activate_satdata':
	collect1.activate()
elif cla == 'get_download_links':
	collect1.get_download_links()
elif cla == 'download':
	collect1.download_images()
elif cla == 'check_changes_in_satdata':
	collect1.check_for_any_changes_satdata()
elif cla == 'clear_automated_downloading':
	file_object = open('automated_downloading.pkl', 'rb')
	lis = pickle.load(file_object)
	file_object.close()
	file_object = open('automated_downloading.pkl', 'wb')
	pickle.dump([lis[0], {}], file_object)
	file_object.close()
elif cla == 'clear_collect1':
	file_object = open('collect1.pkl', 'wb')
	pickle.dump([], file_object)
	file_object.close()
elif cla == 'both':
	file_object = open('automated_downloading.pkl', 'rb')
	lis = pickle.load(file_object)
	file_object.close()
	file_object = open('automated_downloading.pkl', 'wb')
	pickle.dump([lis[0], {}], file_object)
	file_object.close()
	file_object = open('collect1.pkl', 'wb')
	pickle.dump([], file_object)
	file_object.close()
else:
	print ('invalid command')

