import logging
import re

from flask_restful import Resource, reqparse, fields, marshal_with
from flask_login import login_required, utils

from modules.models.user import User as UserModel
from modules.models.host import Channel as ChannelModel
from modules.models.host import Org as OrgModel
# from modules.models.host import Node
from modules.models.host import Cluster as ClusterModel
from modules.user.user import User
from common import log_handler, LOG_LEVEL
from common.request_fabric_api import send_new_user_info

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

user_list_parser = reqparse.RequestParser()
user_list_parser.add_argument('org_id', help='org id')
user_list_parser.add_argument('cluster_id', help='cluster id')

user_create_parser = reqparse.RequestParser()
user_create_parser.add_argument('username', help='Username for create')
user_create_parser.add_argument('password', help='Username for create')
user_create_parser.add_argument('company', help='company of user')
user_create_parser.add_argument('mobile', help='mobile of user')
user_create_parser.add_argument('email', help='email of user')
user_create_parser.add_argument('channel_id', help='channel will join')
user_create_parser.add_argument('cluster_id', help='cluster')
user_create_parser.add_argument('org_id', help='org of user')
user_create_parser.add_argument('is_admin', help='is admin or not')


class OrgUser(Resource):

    @login_required
    def get(self):
        args = user_list_parser.parse_args()
        org_id = args.get('org_id')
        cluster_id = args.get('cluster_id')
        cluster = ClusterModel.objects.get(id=cluster_id)
        org = OrgModel.objects.get(cluster=cluster, alias=org_id)
        users = org.users
        users_list = []
        for user in users:
            user_info = {
                "user_id": str(user.id),
                "username": user.username,
                "mobile": user.mobile,
                "timestamp": user.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'role': user.role
            }
            users_list.append(user_info)

        data = {'stat': 200, 'data': users_list, 'msg': '成功'}
        return data

    @login_required
    def post(self):
        user = utils._get_user()
        user_id = str(user.dbUser.id)
        args = user_create_parser.parse_args()
        mobile = args.get('mobile')
        email = args.get('email')
        password = args.get('password')
        org_id = args.get('org_id')
        channel_id = args.get('channel_id')
        cluster_id = args.get('cluster_id')
        is_admin = args.get('is_admin', False)

        if mobile:
            if not re.match('^1[3456789]\d{9}$', mobile):
                return {'stat': '400', 'msg': '手机号格式错误'}
        if email:
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
            cluster = ClusterModel.objects.get(id=cluster_id)
            org = OrgModel.objects.get(cluster=cluster, org_type='peer',alias=org_id)
        except Exception as e:
            logger.error(e)
            return {'msg': '组织不存在', 'stat': 400}

        try:
            ChannelModel.objects.get(cluster=cluster, alias=channel_id)
        except Exception as e:
            logger.error(e)
            return {'msg': '通道不存在', 'stat': 400}

        args['password'] = User.set_password(password)
        # args['orgs'] = [org_id]
        args.pop('org_id')
        args.pop('channel_id')
        args.pop('is_admin')
        args.pop('cluster_id')
        if int(is_admin) == 1:
            role = 2
        else:
            role = 3

        try:
            new_user = UserModel(**args, orgs=[org.id], apply_stat=1, active=True, role=role)
            new_user.save()
        except Exception as exc:
            logger.error("exc %s", exc)
            return {'stat': "-1", 'msg': "存储数据库失败"}

        body = {
            "BlockchainSign": str(org.cluster.id),
            "ChannelId": channel_id,
            "OrgId": str(org_id),
            "UserId": str(new_user.id)
        }
        logger.info('add user info:{}'.format(body))
        if not send_new_user_info(str(user_id), body=body):
            new_user.delete()
            return {'stat': 400, 'msg': '添加用户失败'}

        org.update(add_to_set__users=[new_user])

        data = {
            'stat': 200,
            'msg': '成功'
        }

        return data
