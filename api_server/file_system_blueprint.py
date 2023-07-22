
from flask import Blueprint
fs_bp = Blueprint('file_system', __name__)

@fs_bp.route('/')
def hello():
    return 'Hello, World!'