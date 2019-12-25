from flask import Blueprint, session

admin = Blueprint('admin', __name__, url_prefix='/admin', static_folder='static')


# @admin.before_request
# def make_session_permanent():
#     pass

from .views import *
from .ajax import *