import os
from config import conf
from flask import request
from flask_cors import CORS

from flask import Blueprint
search_bp = Blueprint('search', __name__)
CORS(search_bp, supports_credentials=True)

################# VERSION 1 BELOW #################

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

'''
@search_bp.route("/search_log/v1")
def search_log_v1():
    # query parameters
    filename = request.args.get('filename', None)
    keyword = request.args.get('keyword', None)
    count = int(request.args.get('count', 0))
    # print(filename, keyword, count)

    if filename:
        # check if filename exists - error out if it doesn't
        full_file_name = os.path.join(conf['search_directory'],filename)
        if not os.path.isfile(full_file_name):
            return {"err_code": -1, "message": "File does not exist.", "data": []}

        with open(full_file_name) as file:
            result = []
            if keyword:
                keyword = keyword.lower().strip()
                for line in file:
                    if keyword in line.lower():     # substring matching
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

################# VERSION 2 BELOW #################

'''
Memory optimisation - reducing the size of "result" variable when there are too many matching records
v1 would load everything into memory, even if count was as small as 10 records

CONS:
Is slightly slower to execute due to extra computes but uses much less memory
Also. will take more memory if we need to return large number of records, compared to v1

'''
@search_bp.route("/search_log/v2")
def search_log_v2():
    # query parameters
    filename = request.args.get('filename', None)
    keyword = request.args.get('keyword', None)
    count = int(request.args.get('count', 0))
    # print(filename, keyword, count)


    matches = 0

    if filename:
        # check if filename exists - error out if it doesn't
        full_file_name = os.path.join(conf['search_directory'],filename)
        if not os.path.isfile(full_file_name):
            return {"err_code": -1, "message": "File does not exist.", "data": []}

        with open(full_file_name) as file:
            result = {}
            if keyword:
                keyword = keyword.lower().strip()
                for line in file:
                    if keyword in line.lower():     # substring matching
                        result[matches] = line
                        matches += 1

                        # if dictionary size increases more than count, remove previous records on each new insertion
                        if (count != 0) and (matches > count):
                            del(result[matches-count-1])
                        # print(result)
            else:
                for line in file:
                    result[matches] = line
                    matches += 1
                    if (count != 0) and (matches > count):
                        del(result[matches-count-1])
            result = list(result.values())[::-1]
            # print(result)
            
            return {"err_code": 0, "message": "Data successfully fetched", "data": result}

    else :
        return {"err_code": 1, "message": "File name not provided", "data": []}

################# VERSION 3 BELOW #################

'''
Process data for matching - used in v3
Searches for all keywords. AND is an operator
"two AND denmark" search keyword will find all records that have two annd denmark both

'''
def check_if_keyword_matches(line, keyword):
    line = line.lower()
    if keyword:
        keyword_array = [kw.strip().lower() for kw in keyword.split(' AND ')]
        # print(keyword_array)
        
        # if no AND operator, search directly without looping
        if len(keyword_array) == 1:
            kw = keyword_array[0]
            return True if kw in line else  False
        else:
            all_match = True
            for kw in keyword_array:
                if kw not in line:
                    all_match = False
            
            return True if all_match else False

    # if keyword is None - line is valid
    else:
        return True


'''
Implement File pointer approach.

Memory and Compute Optimisation
Reading file in reverse in chunks using pointers
Identifies one line at a time and processes it. 
Returns when count reached.

Cons:
    Processes only one line even if the chunk has multiple lines
    If there are enough matches in the entire file, it takes more time as reading from bottom to up is less efficient

'''
@search_bp.route("/search_log/v3")
def search_log_v3():
    # query parameters
    filename = request.args.get('filename', None)
    keyword = request.args.get('keyword', None)
    count = int(request.args.get('count', 0))
    chunk_size = int(request.args.get('chunk_size', 100)) # new - no. of bytes to read in each loop
    # print(filename, keyword, count, chunk_size)


    matches = 0

    try:

        if filename:
            # check if filename exists - error out if it doesn't
            full_file_name = os.path.join(conf['search_directory'],filename)
            if not os.path.isfile(full_file_name):
                return {"err_code": -1, "message": "File does not exist.", "data": []}
            
            with open(full_file_name, 'rb') as fp:
                
                curr_ptr = fp.seek(0, 2)    # go to end of file
                end_ptr = curr_ptr
                
                result = []

                while True:
                    # move one chunk back
                    fp.seek((-1*chunk_size), 1) # curr = 150

                    # read chunk and find last \n
                    temp_read = fp.read(chunk_size)
                    last_slash_n = temp_read.rfind(b'\n')

                    # if \n found
                    if last_slash_n != -1:
                        # move curr to that \n
                        fp.seek((-1*chunk_size), 1) # curr = 150
                        fp.read(last_slash_n)

                        # save length (end - curr)
                        length = end_ptr - fp.tell()

                        # read length
                        data = fp.read(length).decode("utf-8").lstrip() # lstrip because line starts with \n

                        # process data
                        # print(data)
                        if len(data):   # skip processsing empty line
                            if check_if_keyword_matches(data, keyword):
                                result.append(data)
                                if len(result) == count:    # if count is 0, returns entire file
                                    break
                            # print(data)



                        # move curr back to
                        fp.seek((-1*length), 1) # curr = 150
                        curr_ptr = fp.tell()
                        end_ptr = curr_ptr
                        
                    
                    # if \n not found
                    else:
                        # move back one chunk and continue
                        fp.seek((-1*chunk_size), 1)
                        curr_ptr = fp.tell()
                        if (curr_ptr >= chunk_size):
                            continue

                    # edge case
                    if (curr_ptr < chunk_size):
                        # move to start of file
                        fp.seek(0, 0)
                        
                        # read entire length till end
                        arr = fp.read(end_ptr).decode("utf-8")
                        # split by \n and reverse
                        arr = arr.split('\n')[::-1]

                        for data in arr:
                            # process data
                            if check_if_keyword_matches(data, keyword):
                                result.append(data)
                                if len(result) == count:
                                    break
                            # print(data)

                        break
                
                return {"err_code": 0, "message": "Data successfully fetched", "data": result}
        else:
            return {"err_code": 1, "message": "File name not provided", "data": []}
    except:
        return {"err_code": 2, "message": "Error while processing file.", "data": []}
