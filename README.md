# log-reader

This repository intends to read log files from /var/log folder on any server.
It can read files, check for matching keywords in each line and return requested number of rows in latest first order.

# Assumptions
- We are only searching for files in /var/log , not going inside folders
- One row in log file is one log record (no multi-line log)
- Log file only contains logs - no other entries like heading and footers

# Setup Steps

### Create virtual env
```
python3 -m virtualenv log-venv
```

### Activate virtual environment
```
source log-venv/bin/activate
```

### Create Sample test files if required
use `api_server/scripts/create_test_file.py` to create sample test files
Changes `file_name` and `ten_power` to generate files with 10**ten_power records

### Install dependencies for Flask server
```
pip install -r dependencies.txt
```

### Setup
create `config.py` using `config.template.py` and add appropriate path in __`search_directory`__ key

### Start flask server
```
python app.py
```

It should load run the server on port `5000` by default. 

Test by going to `http://localhost:5000/fs/list_all`  - this should list down the files in the `search_directory` mentioned in `config.py`

### ENDPOINTS

`/fs/ls/files_only`
- Empty request payload
- Response format - list of objects - check file_system_blueprint.py

`/fs/list_all`
- Empty request payload
- Response format - list of strings (file names) - check file_system_blueprint.py

`/search/search_log/v1`

`/search/search_log/v2`

`/search/search_log/v3`

- Request Payload Parameters
    - filename [Mandatory]
    - keyword [Optional]
    - count [Optional]
    - chunk_size [Optional] - only in v3
- Response Format
    ```
    {
        err_code: 0,  # 0 for success, !0 for error
        message: "Success / Error Message",
        data: [
            "log record 1",
            "log record 2",
            "log record 3",
            "log record 4"
        ]
    }
    ```

### Angular App

```
cd app_interface/log-viewer/src/app
npm i
ng serve --port 4444 --poll=2000 --watch
```

The app will load on `http://localhost:4444`

### Logo
Add a logo with name `logo.svg` in `app_interface/log-viewer/src/assets/`