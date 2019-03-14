# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
from flask_restful import Resource, fields, marshal_with, reqparse
import logging
import sys
import os
from flask import current_app as app
import bcrypt
from flask_jwt import current_identity, jwt_required

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common import log_handler, LOG_LEVEL
from modules.user.user import User

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

user_password_fields = {
    'user_id': fields.String,
    # "username": fields.String,
    # "apikey": fields.String,
    # "isActivated": fields.Boolean,
    # "balance": fields.Integer,
    "stat": fields.Boolean,
    "msg": fields.String
}

user_password_parser = reqparse.RequestParser()
user_password_parser.add_argument('origin_password', required=True,
                                  location=[],
                                  help='Origin Password')
user_password_parser.add_argument('new_password', required=True,
                                  location='form',
                                  help='New Password')
user_password_parser.add_argument('new_password2', required=True,
                                  location='form',
                                  help='New Password')


class ChangePassword(Resource):
    """
    user logined change password api
    """

    @jwt_required()
    @marshal_with(user_password_fields)
    def post(self):
        args = user_password_parser.parse_args()
        origin_password, new_password, new_password2 = \
            args["origin_password"], args["new_password"], args["new_password2"]
        if new_password != new_password2:
            return {'stat': -1, 'msg': '两次密码输入不一致'}
        user_obj = User()
        user = user_obj.get_by_id(current_identity.id)
        if not user:
            return {"msg": "用户不存在", "stat": -1}, 400
        if user.check_password(user.dbUser.password, origin_password):
            return {"msg": "原始密码错误", "stat": -1}, 400

        password = user.set_password(new_password)
        user.update_password(password)

        data = {
            'id': user.id,
            "stat": -1,
            'msg': '密码修改成功'
        }

        return data, 200
