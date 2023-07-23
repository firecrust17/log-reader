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
Process data for matching - used in v3
'''
def check_if_keyword_matches(line, keyword):
    if keyword:
        if keyword in line:
            return True
        else:
            return False
    
    # if keyword is None - line is valid
    else:
        return True


'''
Implement File pointer approach.

Memory and Compute Optimisation
Reading file in reverse in chunks using pointers
Identifies one line at a time and processes it. 
Returns when count reached.

Benchmarking
100 Million records - 10 GB file - 3000 count (no keywords) - 100 chunk size
    Response in 100-200 ms - memory doesn't increase, CPU goes up for some time
100 Million records - 10 GB file - 3000 count (WITH keywords) - 100 chunk size
    Response in 250-750 ms - memory doesn't increase, CPU goes up for some time


MAX
100 Million records - 10 GB file - 30000 count (no keywords) - 100 chunk size
    Response in 2.3 seconds - memory doesn't increase, HIGH CPU
100 Million records - 10 GB file - 30000 count (WITH keywords) - 100 chunk size
    Response in 3.1 seconds - memory doesn't increase, CPU is also neutral

'''
@search_bp.route('/search_log/v3/')
def search_log_v3():
    # query parameters
    filename = request.args.get('filename', None)
    keyword = request.args.get('keyword', None)
    count = int(request.args.get('count', 0))
    chunk_size = int(request.args.get('chunk_size', 100)) # new - no. of bytes to read in each loop
    # print(filename, keyword, count, chunk_size)

    # check if filename exists - error out if it doesn't
    full_file_name = os.path.join(conf['search_directory'],filename)
    if not os.path.isfile(full_file_name):
        return {"err_code": -1, "message": "File does not exist.", "data": []}

    matches = 0

    if filename:
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

            ########################################################


            # if curr_ptr < chunk_size:
            #     fp.seek(0, 0)
            #     x = fp.read().decode("utf-8").split('\n')[::-1]
            #     x = [rec for rec in x if rec != '']
            #     print(x)
            #     return {}
            
            # while fp.tell() > chunk_size:
            #     fp.seek((-1*chunk_size), 1)
            #     data = fp.read(chunk_size)
            #     print(data, data.split(b'\n'))
            #     skip_merge = False
            #     if data.split(b'\n')[-1] == b'':
            #         skip_merge = True
            #     x = [rec.decode("utf-8") for rec in data.split(b'\n') if rec != b'']
            #     # print(x)
            #     fp.seek((-1*chunk_size), 1)

            # return {}


            #############################################################3


            # move to last \n - should not be required
            # fp.seek((-1*chunk_size), 1)
            # n = fp.read(chunk_size).rfind(b'\n')
            # curr_ptr = curr_ptr - chunk_size + n
            # prev_ptr = curr_ptr
            # fp.seek(curr_ptr, 0)
            

            # print(curr_ptr)
            # print(fp.read(chunk_size))
            # print(fp.tell())

            # while fp.tell() > chunk_size:
            #     fp.seek((-1*chunk_size), 1)
            #     read_size = curr_ptr - fp.tell()
            #     data = fp.read(read_size)
            #     nl = data.rfind(b'\n')
                
            #     # print(data)
            #     # return {}
            #     # print(nl)
            #     if nl == -1:    # if no \n - undo read()
            #         fp.seek((-1*read_size), 1)
            #     else:
            #         curr_ptr = curr_ptr - read_size + nl
            #         # fp.seek(curr_ptr, 0)
            #         length = prev_ptr - curr_ptr
            #         print(fp.read(length))
            #         fp.seek(curr_ptr, 0)
            #         prev_ptr = curr_ptr
                    
            #         # fp.seek(curr_ptr, 0)
            #         # # print(curr_ptr)
            #         # len = curr_ptr - fp.tell() - (nl + 1)
            #         # print(fp.read(len))

            #         # curr_ptr = curr_ptr - chunk_size + nl - 1
            #         # fp.seek(curr_ptr, 0)
            #         # print(fp.read(last_ptr-curr_ptr))
            #         # fp.seek(curr_ptr-1, 0)
                
                
            #     # fp.seek((-1*chunk_size), 1)
                
            # # print()




            # return {"err_code": 0, "message": "Data successfully fetched", "data": result}
            
            
            
            
            # result = {}
            # if keyword:
            #     for line in infile:
            #         if keyword in line:     # substring matching
            #             result[matches] = line
            #             matches += 1
            #             if matches > count:
            #                 del(result[matches-count-1])
            #             # print(result)
            # else:
            #     for line in infile:
            #         result[matches] = line
            #         matches += 1
            #         if matches > count:
            #             del(result[matches-count-1])
            # result = list(result.values())[::-1]
            
            # return {"err_code": 0, "message": "Data successfully fetched", "data": result}

    # else :
    #     return {"err_code": 1, "message": "File name not provided", "data": []}

