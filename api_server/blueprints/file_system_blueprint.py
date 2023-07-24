import os
from config import conf
from flask_cors import CORS

from flask import Blueprint
fs_bp = Blueprint('file_system', __name__)
CORS(fs_bp, supports_credentials=True)


'''
Returns List of files in the search directory present in the config

Response:
["abc.txt", "test.py"]

Can parameterise to move deeper into the file system - conf['search_directory'] will be root
'''
@fs_bp.route("/ls/files_only")
def list_files():
	result = []
	ls_data = os.listdir(conf['search_directory'])

	for item in ls_data:
		if os.path.isfile(os.path.join(conf['search_directory'], item)):
			result.append(item)

	# print(result)
	return result
    

'''
Returns List of files and folders along with their type in the search directory present in the config

Response:
[
    {
        "type": "file",
        "name": "abc.txt",
		"size": "10 MB",
		"byte_size": 142, 
		"extension": "log",
		"read_access": True,
    },
    {
        "type": "folder",
        "name": "folder1",
		"size": "1 GB",
		"byte_size": 1024, 
		"extension": "log",
		"read_access": False
    }
]

Can parameterise to move deeper into the file system - conf['search_directory'] will be root
'''
@fs_bp.route("/list_all")
def list_all():
	result = []
	ls_data = os.listdir(conf['search_directory'])

	for item in ls_data:
		if os.path.isdir(os.path.join(conf['search_directory'], item)):
			result.append({"type": "folder", "name": item, "byte_size": 999999999999999}) # around 1TB
		if os.path.isfile(os.path.join(conf['search_directory'], item)):
			size = os.path.getsize(os.path.join(conf['search_directory'], item))
			read_access = os. access(os.path.join(conf['search_directory'], item), os.R_OK)
			ext = item.split('.')[-1]
			if (ext in conf['remove_file_with_ext']) or (size == 0):
				continue
			
			byte_size = size
			if size < 500000:
				size = str(round(size / 1000, 2)) + ' KB'
			elif size < 500000000:
				size = str(round(size / (1000*1000), 2)) + ' MB'
			elif size >= 500000000:
				size = str(round(size / (1000*1000*1000), 2)) + ' GB'

			result.append({
				"type": "file", 
				"name": item, 
				"size": size, 
				"byte_size": byte_size, 
				"extension": ext,
				"read_access": read_access
			})

	result.sort(key=lambda x: x['byte_size'])


	# print(result)
	return result