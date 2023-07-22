# log-reader

This repository intends to read log files from /var/log folder on any server.
It can read files, check for matching keywords in each line and return requested number of rows in latest first order.

Setup Steps

# Create virtual env
python3 -m virtualenv log-venv

# Activate virtual environment
source log-venv/bin/activate

# Create Sample test files if required
use api_server/scripts/create_test_file.py to create sample test files
Changes file_name and ten_power to generate files with 10**ten_power records

