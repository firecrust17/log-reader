import os
from config import conf

from flask import Blueprint
fs_bp = Blueprint('file_system', __name__)


'''
Returns List of files in the search directory present in the config

Response:
["abc.txt", "test.py"]

Can parameterise to move deeper into the file system - conf['search_directory'] will be root
'''
@fs_bp.route('/ls_files/')
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
        "name": "abc.txt"
    },
    {
        "type": "folder",
        "name": "folder1"
    }
]

Can parameterise to move deeper into the file system - conf['search_directory'] will be root
'''
@fs_bp.route('/ls/')
def list_all():
    result = []
    ls_data = os.listdir(conf['search_directory'])

    for item in ls_data:
        if os.path.isdir(os.path.join(conf['search_directory'], item)):
            result.append({"type": "folder", "name": item})
        if os.path.isfile(os.path.join(conf['search_directory'], item)):
            result.append({"type": "file", "name": item})
    
    # print(result)
    return result

