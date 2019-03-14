#!/usr/bin/python

# -*- coding: utf-8 -*-
# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os

from flask import Flask, redirect, url_for, jsonify, request
from flask_login import LoginManager
from flask_socketio import SocketIO
from mongoengine import connect

from common import log_handler, LOG_LEVEL
from modules.models import ADMIN
from resources import bp_index, bp_container_api,\
    bp_stat_view, bp_stat_api, \
    bp_cluster_view, bp_cluster_api, \
    bp_host_view, bp_host_api, bp_auth_api, bp_org_user_api,\
    bp_login, bp_user_api, bp_user_view, front_rest_user_v2, bp_organization_api
from modules.user import User
from sockets.custom import CustomSockets
from extensions import celery
from modules.user.auth.auth import jwt_decoding
from modules.models import User as UserModel


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"
app = Flask(__name__, static_folder=STATIC_FOLDER,
            template_folder=TEMPLATE_FOLDER)
socketio = SocketIO(app)

app.config.from_object('config.DevelopmentConfig')
app.config.from_envvar('CELLO_CONFIG_FILE', silent=True)

celery.conf.update(app.config)

connect(app.config.get("MONGODB_DB", "dashboard"),
        host=app.config.get("MONGODB_HOST", "mongo"),
        port=app.config.get("MONGODB_PORT", 27017),
        username=app.config.get("MONGODB_USERNAME", ""),
        password=app.config.get("MONGODB_PASSWORD", ""),
        connect=False, tz_aware=True)
logger.info('host{} port{}'.format(app.config.get('MONGODB_HOST'), app.config.get("MONGODB_PORT", 27017)))

# os.environ['COMPOSE_FILE_PATH'] = '/root/cello/src/agent/docker/_compose_files'
login_manager = LoginManager()
login_manager.init_app(app)

app.logger.setLevel(LOG_LEVEL)
app.logger.addHandler(log_handler)

app.register_blueprint(bp_index)
app.register_blueprint(bp_host_view)
app.register_blueprint(bp_host_api)
app.register_blueprint(bp_cluster_view)
app.register_blueprint(bp_cluster_api)
app.register_blueprint(bp_stat_view)
app.register_blueprint(bp_stat_api)
app.register_blueprint(bp_auth_api)
app.register_blueprint(bp_login)
app.register_blueprint(bp_user_api)
app.register_blueprint(bp_user_view)
app.register_blueprint(front_rest_user_v2)
app.register_blueprint(bp_container_api)
# app.register_blueprint(bp_org_user_api)
app.register_blueprint(bp_organization_api)
admin = os.environ.get("ADMIN", '18888888888')
admin_password = os.environ.get("ADMIN_PASSWOR", '888888')
# salt = app.config.get("SALT", b"")
# password = bcrypt.hashpw(admin_password.encode('utf8'), bytes(salt.encode()))
# password = generate_password_hash(admin_password)

try:
    user = User()
    if user.get_by_mobile(admin):
        pass
    else:
        user = User(username='admin', mobile=admin, apply_stat=1, password=admin_password, is_admin=True,role=0)
        user.save()
except Exception as e:
    logger.error(e)
    pass

#
# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html'), 404


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
            ##response.headers['Authorization'] = 'xiaominggessdfs3432ds34ds32432cedsad332e23'
    return response


# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('500.html'), 500


@login_manager.unauthorized_handler
def unauthorized_callback():
    # return redirect(url_for('bp_auth_api.login'))
    return redirect(url_for('bp_auth_api.login'))


@login_manager.user_loader
def load_user(id):
    if id is None:
        redirect(url_for('bp_auth_api.login'))
    user = User()
    user.get_by_id(id)
    if user.is_active():
        return user
    else:
        return None


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')

    if api_key:
        obj = jwt_decoding(api_key)
        user = obj.get('info', None)

        if user:
            try:
                id = user.get('id', None)
                user = User()
                user = user.get_by_id(id)
            except Exception as e:
                logger.error(e)
            else:
                return user
        else:
            # print("is exception !!!!" + str(obj['error_msg']))
            return None


socketio.on_namespace(CustomSockets('/socket.io'))

if __name__ == '__main__':
    # print(app.url_map)
    socketio.run(app, port=8080, host="0.0.0.0",
                 debug=app.config.get("DEBUG"))
    # print(os.getenv('DEBUG'))
