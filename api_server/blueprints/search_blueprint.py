import os
from config import conf
from flask import request

from flask import Blueprint
search_bp = Blueprint('search', __name__)

'''
Basic Method
Takes a filename [Mandatory]
    Checks if file exists - proceeds - else returns error
Takes one keyword [Optional]
    if keyword present, it is matched in every line and only valid records are returned
    if keyword NOT present, each line is a valid record
Takes a count [Optional]
    if present - returns N (count) valid records - starting from the bottom of the file
    if NOT present - returns all valid records - starting from the bottom of the file

Benchmarking
100 Million records - 10 GB file - 3000 count - took ~5 GB memory
    Response in 31 seconds
10 Million records - 1 GB file (no keyword) - 30000 count
    Response in 4.8 seconds
10 Million records - 1 GB file (with keyword) - 30000 count
    Response in 4.3 seconds
'''
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


'''
Memory optimisation - reducing the size of "result" variable when there are too many matching records
v1 would load everything into memory, even if count was as small as 10 records

CONS:
Is slightly slower to execute due to extra computes but uses much less memory
Also. will take more memory if we need to return large number of records, compared to v1

Benchmarking
100 Million records - 10 GB file - 3000 count (no keywords) - memory doesn't increase, CPU is also neutral
    Response in 30 seconds
10 Million records - 1 GB file - 30000 count (no keywords) - memory doesn't increase, CPU is also neutral
    Response in 5.8 seconds
10 Million records - 1 GB file - 30000 count (with keyword) - memory doesn't increase, CPU is also neutral
    Response in 4.5 seconds
'''
@search_bp.route('/search_log/v2/')
def search_log_v2():
    # query parameters
    filename = request.args.get('filename', None)
    keyword = request.args.get('keyword', None)
    count = int(request.args.get('count', 0))
    # print(filename, keyword, count)

    # check if filename exists - error out if it doesn't
    full_file_name = os.path.join(conf['search_directory'],filename)
    if not os.path.isfile(full_file_name):
        return {"err_code": -1, "message": "File does not exist.", "data": []}

    matches = 0

    if filename:
        with open(full_file_name) as file:
            result = {}
            if keyword:
                for line in file:
                    if keyword in line:     # substring matching
                        result[matches] = line
                        matches += 1

                        # if dictionary size increases more than count, remove previous records on each new insertion
                        if matches > count:
                            del(result[matches-count-1])
                        # print(result)
            else:
                for line in file:
                    result[matches] = line
                    matches += 1
                    if matches > count:
                        del(result[matches-count-1])
            result = list(result.values())[::-1]
            # print(result)
            
            return {"err_code": 0, "message": "Data successfully fetched", "data": result}

    else :
        return {"err_code": 1, "message": "File name not provided", "data": []}


'''
Implement File pointer approach
'''
@search_bp.route('/search_log/v3/')
def search_log_v3():
    return "Version 3"