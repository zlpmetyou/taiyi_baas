
# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import random
import re
import string

from flask_restful import Resource, reqparse, fields, marshal_with
from flask_login import login_required, utils
from flask import current_app as app
import logging
import sys
import os
import time
import datetime
import bcrypt
from flask_jwt import JWT, jwt_required

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common import log_handler, LOG_LEVEL
from modules.models import User as UserModel
from modules.user.user import User
from common import send_sms


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


user_fields = {
    "id": fields.String,
    "username": fields.String,
    'company': fields.String,
    'department': fields.String,
    'mobile': fields.Integer,
    "isAdmin": fields.Boolean,
    "role": fields.Integer,
    "apply_stat": fields.Integer,
    # "balance": fields.Integer,
    "timestamp": fields.DateTime
}

user_result_fields = {
    "users": fields.List(fields.Nested(user_fields)),
    "totalCount": fields.Integer,
    "pageSize": fields.Integer,
    "pageNo": fields.Integer
}

user_list_fields = {
    'stat': fields.Integer(default=200),
    "data": fields.Nested(user_result_fields),
    'msg': fields.String(default='成功')
}

user_info_fields = {
    "username": fields.String,
    "apikey": fields.String,
    "isActivated": fields.Boolean,
    "balance": fields.Integer,
    "success": fields.Boolean,
    "error": fields.String
}

user_create_fields = {
    "id": fields.String,
    "stat": fields.String,
    'msg': fields.String
}

user_update_fields = {
    "stat": fields.String(default=200),
    'data': fields.String,
    "msg": fields.String(default='成功')
}

user_delete_fields = {
    "stat": fields.String,
    'msg': fields.String
}

verification_fields = {
    "stat": fields.String,
    'msg': fields.String
}

user_list_parser = reqparse.RequestParser()
user_list_parser.add_argument('pageNo', type=int, default=1, help='Page number to query')
user_list_parser.add_argument('pageSize', type=int, default=10, help='Page size to query')
user_list_parser.add_argument('mobile', default="", help='用户手机号')

user_create_parser = reqparse.RequestParser()
user_create_parser.add_argument('username', required=True, location=['form', 'json'], help='Username for create')
user_create_parser.add_argument('company', required=True, location=['form', 'json'], help='company of user')
user_create_parser.add_argument('mobile', required=True, location=['form', 'json'], help='mobile of user')
user_create_parser.add_argument('email', required=True, location=['form', 'json'], help='email of user')

user_update_parser = reqparse.RequestParser()
user_update_parser.add_argument('user_id', required=True, location=['form', 'json'], help='user_id for update')
user_update_parser.add_argument('username', location=['form', 'json'], help='Username for update')
user_update_parser.add_argument('mobile', location=['form', 'json'], help='mobile for user')
user_update_parser.add_argument('company', location=['form', 'json'], help='company for user')
user_update_parser.add_argument('department', location=['form', 'json'], help='department for user')
user_update_parser.add_argument('active', location=['form', 'json'], help='Whether active user when update')
user_update_parser.add_argument('apply_stat', location=['form', 'json'], help='verification for user')
user_update_parser.add_argument('password', location=['form', 'json'], help='new password for user')
user_update_parser.add_argument('password2', location=['form', 'json'], help='verification password for user')

user_delete_parser = reqparse.RequestParser()
user_delete_parser.add_argument('user_id', help='User_id to delete')

APPLY_STAT = {
    0: '审核中',
    1: '审核通过',
    -1: '审核未通过'
}


class UserView(Resource):

    @login_required
    def get(self):
        # user = utils._get_user()
        args = user_list_parser.parse_args()
        page = args['pageNo']
        per_page = args['pageSize']
        mobile = args.get('mobile')
        if mobile:
            user = User().get_by_mobile(mobile)
            # print(user.id)
            user_info = {
                'user_id': str(user.id),
                'username': user.username,
                'mobile': mobile
            }
            data = {
                'stat': 200,
                'data': user_info,
                'msg': '成功'
            }
            return data
        # sort_columns = 'timestamp'
        # sort_columns = sort_columns.split(" ")
        # sort_str = ''
        # if len(sort_columns) > 1:
        #     sort_type = sort_columns[1]
        #     sort_field = sort_columns[0]
        #     if sort_type == "desc":
        #         sort_str = "-%s" % sort_field
        #     else:
        #         sort_str = sort_field
        offset = (page - 1) * per_page

        user_count = UserModel.objects.all().count()-1
        users = \
            UserModel.objects(role__ne=0).skip(offset).limit(per_page).order_by('-timestamp')

        users_list = []
        sequence_num = (page*per_page)-(per_page-1)
        for user in users:
            user_info = {
                'id': sequence_num,
                "user_id": str(user.id),
                "username": user.username,
                "mobile": user.mobile,
                "company": user.company,
                "department": user.department,
                'email': user.email,
                "reason": user.reason,
                "isAdmin": user.isAdmin,
                "apply_stat": user.apply_stat,
                'role': user.role,
                "active": user.active,
                "timestamp": user.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            users_list.append(user_info)
            sequence_num += 1

        result = {
            "users": users_list,
            "totalCount": user_count,
            "pageSize": per_page,
            "pageNo": page

        }
        data = {'stat': 200, 'data': result, 'msg': '成功'}

        return data

    @login_required
    def post(self):
        args = user_create_parser.parse_args()
        mobile = args.get('mobile')
        email = args.get('email')
        if not re.match('^1[3456789]\d{9}$', mobile):
            return {'stat': '400', 'msg': '手机号格式错误'}
        if not re.match('^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', email):
            return {'stat': '400', 'msg': '邮箱格式错误'}
        try:
            user = UserModel.objects.get(mobile=mobile)
            if user:
                return {'stat': "400", 'msg': "手机号已存在"}
        except Exception as exc:
            logger.error(exc)
            pass

        try:
            user = UserModel(**args, role=1)
            user.save()
            # user_id = user.id
        except Exception as exc:
            logger.error("exc %s", exc)
            return {'stat': "-1", 'msg': "存储数据库失败"}
        data = {
            'stat': 200,
            'msg': '新增用户成功'
        }

        return data

    @login_required
    @marshal_with(user_update_fields)
    def put(self):
        args = user_update_parser.parse_args()
        password = args.get('password')
        password2 = args.get('password2')
        user_id = args.get('user_id')
        apply_stat = args.get('apply_stat')

        if password and password2:
            if password2 == password:
                hash_password = User.set_password(password)
                args['password'] = hash_password
                args['password2'] = None
            else:
                data = {'stat': 400, 'msg': '密码不一致'}
                return data
        elif password or password2:
            data = {'stat': 400, 'msg': '缺少参数'}
            return data

        if apply_stat and int(apply_stat) == 1:
            try:
                user = UserModel.objects.get(id=user_id)
            except Exception as e:
                logger.error(e)
                return {'msg': '用户不存在'}
            mobile = user.mobile
            # salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            # args['password'] = User.set_password(salt)
            send_sms(mobile, str(mobile)[-6:])

        args['user_id'] = None

        update_fields = {arg: args[arg] for arg in args if args.get(arg)}

        try:
            UserModel.objects(id=user_id).update(**update_fields)
        except Exception as exc:
            logger.warning(exc)
            return {'stat': 400, 'msg': '更新数据库失败'}
        data = {
            'msg': '更新成功'
        }
        return data

    @login_required
    @marshal_with(user_delete_fields)
    def delete(self, **kwargs):
        args = user_delete_parser.parse_args()
        user_id = args.get('user_id')
        try:
            user = UserModel.objects.get(id=user_id)
        except Exception:
            pass
        else:
            user.delete()

        return {"stat": 200, 'msg': "删除成功"}


