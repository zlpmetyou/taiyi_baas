
# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import re

from flask_restful import Resource, reqparse, fields, marshal_with
from flask import url_for
from flask_login import login_user, logout_user
import logging
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common import log_handler, LOG_LEVEL
from modules.user.user import User
from modules.models.host import Org as OrgModel
from modules.models.host import Channel
from .auth import jwt_encoding


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

login_parser = reqparse.RequestParser()
login_parser.add_argument('mobile', required=True,
                          # location=['form', 'json'],
                          help='mobile for create')
login_parser.add_argument('password', required=True,
                          location=['form', 'json'],
                          help='Password for create')


class Login(Resource):

    def post(self):
        args = login_parser.parse_args()
        mobile, password = args["mobile"], args["password"]
        if not re.match('^1[3456789]\d{9}$', mobile):
            return {'stat': '400', 'msg': '手机号格式错误'}
        user_obj = User()
        try:
            user = user_obj.get_by_mobile(mobile)
            if not user:
                return {'stat': '400', 'msg': '用户不存在'}
            logger.info('stat:{}'.format(user.apply_stat))
            # compare input password with password in db
            # if user.apply_stat == 0:
            #     return {'stat': '-1', 'msg': '正在审核中'}, 400
            # elif user.apply_stat == -1:
            #     return {'stat': '-1', 'msg': '审核未通过'}, 400
            #
            if int(user.dbUser.apply_stat) == 0:
                return {'stat': '400', 'msg': '审核中'}

            if str(user.dbUser.apply_stat) == '-1':
                return {'stat': '400', 'msg': '审核未通过'}

            if user.check_password(user.password, password) and user.active:
                # login_user(user)

                # if login success save login history
                # login_history = LoginHistory(user=user.dbUser)
                # login_history.save()
                user_id = str(user.id)
                user_info = {
                    'id': user_id,
                    'username': user.username,
                    'mobile': user.mobile,
                    'isAdmin': user.isAdmin,
                    'role': user.role
                }

                token = jwt_encoding(user_info)
                user_orgs_id = user.dbUser.orgs
                cluster_id = ''
                channel_id = ''
                org_id = ''
                if user_orgs_id:
                    logger.info('user_orgs_id:{}'.format(user_orgs_id))
                    org = OrgModel.objects.get(id=user_orgs_id[0])
                    cluster = org.cluster
                    channel = Channel.objects.get(cluster=cluster)
                    org_id = org.alias
                    cluster_id = str(cluster.id)
                    # channel_id = str(channel.id)
                    channel_id = channel.alias

                result = {
                    'id': user_id,
                    'role': user.dbUser.role,
                    'username': user.dbUser.username,
                    'mobile': user.dbUser.mobile,
                    'company': user.dbUser.company,
                    'department': user.dbUser.department,
                    'active': user.dbUser.active,
                    'apply_stat': user.dbUser.apply_stat,
                    'isAdmin': user.dbUser.isAdmin,
                    'org_id': org_id,
                    'cluster_id': cluster_id,
                    'channel_id': channel_id
                }

                data = {
                    "stat": 200,
                    'data': {
                        'token': token,
                        'user_info': result
                    },
                    'msg': '登录成功'
                }

                return data
            else:
                data = {
                    "stat": 401,
                    "msg": "手机号或密码错误"
                }
                return data
        except Exception as exc:
            logger.info("error {}".format(exc))
            data = {
                "stat": 401,
                "msg": "登录失败"
            }
            return data
