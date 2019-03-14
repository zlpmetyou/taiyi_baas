# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import re

from flask_restful import Resource, reqparse, fields, marshal_with
import logging
import sys
import os
from flask import current_app as app
import bcrypt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common import log_handler, LOG_LEVEL
from modules.user.user import User
from modules.models.user import User as UserModel, Profile

ENABLE_EMAIL_ACTIVE = os.environ.get("ENABLE_EMAIL_ACTIVE", "False")
ENABLE_EMAIL_ACTIVE = ENABLE_EMAIL_ACTIVE == "True"

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

register_fields = {
    "stat": fields.Integer(default=200),
    'msg': fields.String(default='成功'),
    'data': fields.String(default='')
}

register_parser = reqparse.RequestParser()
register_parser.add_argument('username', required=True, location=['form', 'json'], help='name of user')
register_parser.add_argument('company', required=True, location=['form', 'json'], help='company of user')
register_parser.add_argument('department', location=['form', 'json'], help='department of company')
register_parser.add_argument('mobile', required=True, location=['form', 'json'], help='mobile number')
register_parser.add_argument('email', location=['form', 'json'], help='email of user')
register_parser.add_argument('reason', location=['form', 'json'], help='The reason of register')


class Register(Resource):
    @marshal_with(register_fields)
    def post(self):
        args = register_parser.parse_args()
        mobile = args.get('mobile')
        email = args.get('email')

        # 验证手机格式
        if not re.match('^1[3456789]\d{9}$', mobile):
            return {'stat': '400', 'msg': '手机号格式错误'}
        if not re.match('^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', email):
            return {'stat': '400', 'msg': '邮箱格式错误'}

        # 验证手机是否存在
        try:
            user = User().get_by_mobile(mobile)
            if user:
                return {'stat': '400', 'msg': '该手机号已提交申请，请耐心等待审核！'}
        except Exception as e:
            logger.error(e)
            return {'stat': '400', 'msg': '读取数据库错误'}

        # 存储用户
        args['password'] = mobile[-6:]
        try:
            user = User(**args, role=1)
            user.save()
        except Exception as e:
            logger.error(e)
            return {'stat': '400', 'msg': '数据库存储错误'}

        data = {
            "stat": 200,
            'msg': '申请成功'
        }
        return data
