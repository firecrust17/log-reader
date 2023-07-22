import os
from config import conf

from flask import Blueprint
search_bp = Blueprint('search', __name__)

@search_bp.route('/')
def search():
    return "Search Performed"