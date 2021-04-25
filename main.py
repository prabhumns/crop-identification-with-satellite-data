<<<<<<< HEAD
import automated_downloading
import collect
import pickle

cla = input("type one of these: *check_new_crop_data* or *download* or *check_changes_in_satdata*\n")

if cla == 'check_new_crop_data':
	automated_downloading.check_satdata()
elif cla == 'download':
	collect.download_images()
elif cla == 'check_changes_in_satdata':
	collect.check_for_any_changes_satdata()
else:
	print ('invalid command')

=======
import automated_downloading
import collect
import pickle

cla = input("type one of these: *check_new_crop_data* or *download* or *check_changes_in_satdata*\n")

if cla == 'check_new_crop_data':
	automated_downloading.check_satdata()
elif cla == 'download':
	collect.download_images()
elif cla == 'check_changes_in_satdata':
	collect.check_for_any_changes_satdata()
else:
	print ('invalid command')

>>>>>>> b1d77540898af5ff5f5be875cbd0eee6732525ba
