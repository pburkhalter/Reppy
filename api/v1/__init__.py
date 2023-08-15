from flask import Blueprint
from print import print
from system import system

blueprint = Blueprint('api_v1', __name__)
blueprint.register_blueprint(print, url_prefix='/printer')
blueprint.register_blueprint(system, url_prefix='/system')