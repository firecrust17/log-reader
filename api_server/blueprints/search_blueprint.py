import os
from config import conf
from flask import request

from flask import Blueprint
search_bp = Blueprint('search', __name__)


@search_bp.route('/search_log/v1/')
def search_log_v1():
    # query parameters
    filename = request.args.get('filename', None)
    keyword = request.args.get('keyword', None)
    count = int(request.args.get('count', 0))
    # print(filename, keyword, count)

    # check if filename exists - error out if it doesn't
    full_file_name = os.path.join(conf['search_directory'],filename)
    if not os.path.isfile(full_file_name):
        return {"err_code": -1, "message": "File does not exist.", "data": []}

    if filename:
        with open(full_file_name) as file:
            result = []
            if keyword:
                for line in file:
                    if keyword in line:     # substring matching
                        result.append(line)
            else:
                for line in file:
                    result.append(line)
            # print(len(result))

            # Returning last N (count) records - latest first
            # if count = 0, returns all results - latest first
            result = result[:(-1*count)-1:-1] if count != 0 else result[::-1]

            return {"err_code": 0, "message": "Data successfully fetched", "data": result}

    else :
        return {"err_code": 1, "message": "File name is mandatory.", "data": []}

