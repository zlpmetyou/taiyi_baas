
# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import logging
import os
import sys
import uuid
import sys
import datetime

if sys.version_info.major == 2:  # py2
    from urlparse import urlparse
else:  # py3
    from urllib.parse import urlparse
from flask_login import login_required
from flask_restful import Resource, reqparse, fields, marshal_with

from flask import jsonify, Blueprint, render_template
from flask import request as r
import json

from modules.host import HostHandler

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common import log_handler, LOG_LEVEL, \
    make_ok_resp, make_fail_resp, \
    CODE_CREATED, \
    request_debug

from common.utils import K8S_CRED_TYPE

from modules import host_handler
from modules.models import Cluster as ClusterModel
from modules.models import User as UserModel
from modules.models import Host as HostModel
from agent import detect_daemon_type, check_worker_api

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

host_list_parser = reqparse.RequestParser()
host_list_parser.add_argument('pageNo', type=int, default=1, help='第几页')
host_list_parser.add_argument('pageSize', type=int, default=10, help='每页显示数')

host_create_parser = reqparse.RequestParser()
host_create_parser.add_argument('host_name', required=True, location=['form', 'json'], help='主机名')
host_create_parser.add_argument('worker_api', required=True, location=['form', 'json'], help='服务器地址')
host_create_parser.add_argument('capacity', required=True, location=['form', 'json'], help='容量')
host_create_parser.add_argument('host_type', location=['form', 'json'], help='主机类型')

host_update_parser = reqparse.RequestParser()
host_update_parser.add_argument('host_id', required=True, location=['form', 'json'], help='主机id')
host_update_parser.add_argument('host_name', location=['form', 'json'], help='主机名')
host_update_parser.add_argument('worker_api', location=['form', 'json'], help='服务器地址')
host_update_parser.add_argument('capacity', location=['form', 'json'], help='容量')
host_update_parser.add_argument('host_type', location=['form', 'json'], help='主机类型')

host_delete_parser = reqparse.RequestParser()
host_delete_parser.add_argument('host_id', required=True, help='要删除的主机id')


available_host_fields = {
    'host_id': fields.String(attribute='id'),
    'host_name': fields.String(attribute='name')
}
available_host_result_fields = {
    'stat': fields.Integer(default=200),
    'data': fields.List(fields.Nested(available_host_fields)),
    'msg': fields.String(default='成功')
}


class AvailableHost(Resource):
    @login_required
    @marshal_with(available_host_result_fields)
    def get(self):
        hosts = HostModel.objects(status='active')
        available_host_list = []
        for host in hosts:
            if len(host.clusters) < int(host.capacity):
                available_host_list.append(host)
        result = {
            'data': available_host_list
        }
        return result


class HostView(Resource):
    @login_required
    def get(self):
        logger.info("/hosts_list method=" + r.method)
        request_debug(r, logger)
        args = host_list_parser.parse_args()
        page = args['pageNo']
        per_page = args['pageSize']

        offset = (page - 1) * per_page

        host_count = HostModel.objects.all().count()
        hosts = HostModel.objects.skip(offset).limit(per_page).order_by('-timestamp')
        hosts_list = []
        id = (page * per_page) - (per_page - 1)
        for host in hosts:
            host_info = {
                'id': id,
                "host_id": str(host.id),
                # 'users': host.users,
                "host_name": host.name,
                "worker_api": host.worker_api,
                'host_type': host.host_type,
                'capacity': host.capacity,
                # 'create_ts': host.create_ts.strftime("%Y-%m-%d %H:%M:%S"),
                'create_ts': (host.create_ts+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                "active": host.status,
                'clusters': host.clusters
            }
            hosts_list.append(host_info)
            id += 1
        result = {
            "hosts": hosts_list,
            "totalCount": host_count,
            "pageSize": per_page,
            "pageNo": page
        }
        return make_ok_resp(data=result)

    @login_required
    def post(self):
        request_debug(r, logger)
        args = host_create_parser.parse_args()
        name = args.get('host_name')
        worker_api = args.get('worker_api')
        capacity = args.get('capacity')
        host_type = args.get('host_type')

        if host_type != "docker":
            return {'stat': 20001, 'msg': '后续开放'}
            # vcaddress = args['vc_address']
            # if vcaddress.find(":") == -1:
            #     address = vcaddress
            #     port = "443"
            # else:
            #     address = vcaddress.split(':')[0]
            #     port = vcaddress.split(':')[1]
            # logger.debug("address={}, port={}".format(address, port))
            #
            # vmname = "cello-vsphere-" + str(uuid.uuid1())
            # vsphere_param = {
            #     'vc': {
            #         'address': address,
            #         'port': port,
            #         'username': args['vc_user'],
            #         'password': args['vc_password'],
            #         'network': args['vc_network'],
            #         'vc_datastore': args['datastore'],
            #         'vc_datacenter': args['datacenter'],
            #         'vc_cluster': args['cluster'],
            #         'template': args['vm_template']},
            #     'vm': {
            #         'vmname': vmname,
            #         'ip': args['vm_ip'],
            #         'gateway': args['vm_gateway'],
            #         'netmask': args['vm_netmask'],
            #         'dns': args['vm_dns'],
            #         'vcpus': int(args['vm_cpus']),
            #         'memory': int(args['vm_memory'])}}
            #
            # vsphere_must_have_params = {
            #     'Name': name,
            #     'Capacity': capacity,
            #     'VCAddress': address,
            #     'VCUser': args['vc_user'],
            #     'VCPassword': args['vc_password'],
            #     'VCNetwork': args['vc_network'],
            #     'Datastore': args['datastore'],
            #     'Datacenter': args['datacenter'],
            #     'Cluster': args['cluster'],
            #     'VMIp': args['vm_ip'],
            #     'VMGateway': args['vm_gateway'],
            #     'VMNetmask': args['vm_netmask']}
            # for key in vsphere_must_have_params:
            #     if vsphere_must_have_params[key] == '':
            #         error_msg = "host POST without {} data".format(key)
            #         logger.warning(error_msg)
            #         return make_fail_resp(error=error_msg, data=args)
            # result = host_handler.create(name=name, worker_api=worker_api,
            #                              capacity=int(capacity),
            #                              autofill=autofill,
            #                              schedulable=schedulable,
            #                              log_level=log_level,
            #                              log_type=log_type,
            #                              log_server=log_server,
            #                              host_type=host_type,
            #                              params=vsphere_param)

        # elif host_type == 'kubernetes':
        #     return {'stat': 20001, 'msg': '后续开放'}
        #
        #     worker_api = body['worker_api']
        #     k8s_param = create_k8s_host(name, capacity, log_type, body)
        #     if len(k8s_param) == 0:
        #         return make_fail_resp(error=error_msg, data=r.form)
        #
        #     logger.debug("name={}, worker_api={},  capacity={},"
        #                  "fillup={}, schedulable={}, log={}/{}, k8s_param={}".
        #                  format(name, worker_api, capacity, autofill,
        #                         schedulable, log_type, log_server, k8s_param))
        #
        #     result = host_handler.create(name=name, worker_api=worker_api,
        #                                  capacity=int(capacity),
        #                                  autofill=autofill,
        #                                  schedulable=schedulable,
        #                                  log_level=log_level,
        #                                  log_type=log_type,
        #                                  log_server=log_server,
        #                                  host_type=host_type,
        #                                  params=k8s_param)

        else:
            logger.debug("name={}, worker_api={}, capacity={},host_type={}".
                         format(name, worker_api, capacity, host_type if host_type else 'docker'))
            if not name or not worker_api or not capacity:
                error_msg = "参数缺失"
                logger.warning(error_msg)
                return make_fail_resp(error=error_msg, data=args)

            url = urlparse(worker_api)
            if not url.scheme:
                worker_api = "tcp://" + worker_api  # worker node listen on tcp port
            segs = worker_api.split(":")
            if len(segs) != 3:
                logger.error("Invalid daemon url = ", worker_api)
                return make_fail_resp(error='服务器地址格式错误', data={"worker_api": worker_api})

            host = HostModel.objects(name=name)
            if host:
                error_msg = '主机名已存在'
                return make_fail_resp(error=error_msg, data={'name': name})

            host = HostModel.objects(worker_api=worker_api)
            if host:
                error_msg = '服务器地址已存在'
                return make_fail_resp(error=error_msg, data={"worker_api": worker_api})
            if not check_worker_api(worker_api):
                error_msg = '服务器地址异常'
                logger.error(error_msg)
                # return make_fail_resp(error=error_msg, data={'worker_api': worker_api})
                return {'msg': error_msg, 'stat': 400}

            host_type = host_type if host_type else detect_daemon_type(worker_api)
            result = host_handler.create(name=name,
                                         worker_api=worker_api,
                                         capacity=int(capacity),
                                         host_type=host_type)

        logger.debug("result.msg={}".format(result.get('msg')))
        if (host_type == "vsphere") and ('msg' in result):
            vsphere_errmsg = result.get('msg')
            error_msg = "Failed to create vsphere host {}".format(vsphere_errmsg)
            logger.warning(error_msg)
            return make_fail_resp(error=error_msg)
        elif result:
            logger.debug("host creation successfully")
            return make_ok_resp()
        else:
            error_msg = "Failed to create host {}".format(args["host_name"])
            logger.warning(error_msg)
            return make_fail_resp(error=error_msg)

    @login_required
    def put(self):
        request_debug(r, logger)
        # if r.content_type.startswith("application/json"):
        #     body = dict(r.get_json(force=True, silent=True))
        # else:
        #     body = r.form
        # if "id" not in body:
        #     error_msg = "host PUT without enough data"
        #     logger.warning(error_msg)
        #     return make_fail_resp(error=error_msg,
        #                           data=body)
        # else:
        #     id, d = body["id"], {}
        #     for k in body:
        #         if k != "id":
        #             d[k] = body.get(k)
        args = host_update_parser.parse_args()
        id, d = args.get('host_id'), {}
        name = args.get('host_name')

        if name:
            d['name'] = name
        for k, v in args.items():
            if k not in ["host_id", 'host_name'] and v:
                d[k] = args.get(k)

        result = host_handler.update(id, d)
        if result:
            logger.debug("host PUT successfully")
            return make_ok_resp()
        else:
            error_msg = "Failed to update host {}".format(result.get("name"))
            logger.warning(error_msg)
            return make_fail_resp(error=error_msg)

    @login_required
    def delete(self):
        request_debug(r, logger)
        args = host_delete_parser.parse_args()
        host_id = args.get('host_id')
        # if "id" in r.form:
        #     host_id = r.form["id"]
        # elif "id" in request_data:
        #     host_id = request_data.get("id")
        # else:
        #     error_msg = "host delete without enough data"
        #     logger.warning(error_msg)
        #     return make_fail_resp(error=error_msg, data=r.form)
        if not host_id:
            error_msg = "缺少参数"
            logger.warning(error_msg)
            return make_fail_resp(error=error_msg)
        logger.debug("host delete with id={0}".format(host_id))
        try:
            host = HostModel.objects.get(id=host_id)
        except Exception:
            logger.warning("Cannot delete non-existed host")
            return make_fail_resp(error='无法删除不存在的主机')
        if ClusterModel.objects(host=host).count() > 0:
            return {'stat': 1000, 'msg': '主机存在已创建的区块链，无法删除'}
        if host_handler.delete(host):
            return make_ok_resp()
        else:
            error_msg = "Failed to delete host {}".format(host_id)
            logger.warning(error_msg)
            return make_fail_resp(error=error_msg)

# @bp_host_api.route('/hosts', methods=['GET'])
# def hosts_list():
#     logger.info("/hosts_list method=" + r.method)
#     request_debug(r, logger)
#     col_filter = dict((key, r.args.get(key)) for key in r.args)
#     items = list(host_handler.list(filter_data=col_filter))
#
#     return make_ok_resp(data=items)
#
#
# @bp_host_api.route('/host/<host_id>', methods=['GET'])
# def host_query(host_id):
#     request_debug(r, logger)
#     result = host_handler.schema(host_handler.get_by_id(host_id))
#     logger.debug(result)
#     if result:
#         return make_ok_resp(data=result)
#     else:
#         error_msg = "host not found with id=" + host_id
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg, data=r.form)


# @bp_host_api.route('/host', methods=['POST'])
# def host_create():
#     request_debug(r, logger)
#     if r.content_type.startswith("application/json"):
#         body = dict(r.get_json(force=True, silent=True))
#     else:
#         body = r.form
#     name, worker_api, capacity, log_type, log_server, log_level, host_type = \
#         body['name'], body['worker_api'], body['capacity'], \
#         body['log_type'], body.get('log_server', ''), body['log_level'], \
#         body['host_type'] if 'host_type' in body else None
#
#     if "autofill" in body and body["autofill"] == "on":
#         autofill = "true"
#     else:
#         autofill = "false"
#
#     if "schedulable" in body and body["schedulable"] == "on":
#         schedulable = "true"
#     else:
#         schedulable = "false"
#
#     if host_type == "vsphere":
#         vcaddress = body['vc_address']
#         if vcaddress.find(":") == -1:
#             address = vcaddress
#             port = "443"
#         else:
#             address = vcaddress.split(':')[0]
#             port = vcaddress.split(':')[1]
#         logger.debug("address={}, port={}".format(address, port))
#
#         vmname = "cello-vsphere-" + str(uuid.uuid1())
#         vsphere_param = {
#             'vc': {
#                 'address': address,
#                 'port': port,
#                 'username': body['vc_user'],
#                 'password': body['vc_password'],
#                 'network': body['vc_network'],
#                 'vc_datastore': body['datastore'],
#                 'vc_datacenter': body['datacenter'],
#                 'vc_cluster': body['cluster'],
#                 'template': body['vm_template']},
#             'vm': {
#                 'vmname': vmname,
#                 'ip': body['vm_ip'],
#                 'gateway': body['vm_gateway'],
#                 'netmask': body['vm_netmask'],
#                 'dns': body['vm_dns'],
#                 'vcpus': int(body['vm_cpus']),
#                 'memory': int(body['vm_memory'])}}
#
#         logger.debug("name={}, capacity={},"
#                      "fillup={}, schedulable={}, log={}/{}, vsphere_param={}".
#                      format(name, capacity, autofill, schedulable,
#                             log_type, log_server, vsphere_param))
#
#         vsphere_must_have_params = {
#             'Name': name,
#             'Capacity': capacity,
#             'LoggingType': log_type,
#             'VCAddress': address,
#             'VCUser': body['vc_user'],
#             'VCPassword': body['vc_password'],
#             'VCNetwork': body['vc_network'],
#             'Datastore': body['datastore'],
#             'Datacenter': body['datacenter'],
#             'Cluster': body['cluster'],
#             'VMIp': body['vm_ip'],
#             'VMGateway': body['vm_gateway'],
#             'VMNetmask': body['vm_netmask']}
#         for key in vsphere_must_have_params:
#             if vsphere_must_have_params[key] == '':
#                 error_msg = "host POST without {} data".format(key)
#                 logger.warning(error_msg)
#                 return make_fail_resp(error=error_msg, data=body)
#         result = host_handler.create(name=name, worker_api=worker_api,
#                                      capacity=int(capacity),
#                                      autofill=autofill,
#                                      schedulable=schedulable,
#                                      log_level=log_level,
#                                      log_type=log_type,
#                                      log_server=log_server,
#                                      host_type=host_type,
#                                      params=vsphere_param)
#
#     elif host_type == 'kubernetes':
#         worker_api = body['worker_api']
#         k8s_param = create_k8s_host(name, capacity, log_type, body)
#         if len(k8s_param) == 0:
#             return make_fail_resp(error=error_msg, data=r.form)
#
#         logger.debug("name={}, worker_api={},  capacity={},"
#                      "fillup={}, schedulable={}, log={}/{}, k8s_param={}".
#                      format(name, worker_api, capacity, autofill,
#                             schedulable, log_type, log_server, k8s_param))
#
#         result = host_handler.create(name=name, worker_api=worker_api,
#                                      capacity=int(capacity),
#                                      autofill=autofill,
#                                      schedulable=schedulable,
#                                      log_level=log_level,
#                                      log_type=log_type,
#                                      log_server=log_server,
#                                      host_type=host_type,
#                                      params=k8s_param)
#
#     else:
#         logger.debug("name={}, worker_api={}, capacity={}"
#                      "fillup={}, schedulable={}, log={}/{}".
#                      format(name, worker_api, capacity, autofill, schedulable,
#                             log_type, log_server))
#         if not name or not worker_api or not capacity or not log_type:
#             error_msg = "host POST without enough data"
#             logger.warning(error_msg)
#             return make_fail_resp(error=error_msg, data=body)
#         else:
#             host_type = host_type if host_type \
#                 else detect_daemon_type(worker_api)
#             result = host_handler.create(name=name, worker_api=worker_api,
#                                          capacity=int(capacity),
#                                          autofill=autofill,
#                                          schedulable=schedulable,
#                                          log_level=log_level,
#                                          log_type=log_type,
#                                          log_server=log_server,
#                                          host_type=host_type)
#     logger.debug("result.msg={}".format(result.get('msg')))
#     if (host_type == "vsphere") and ('msg' in result):
#         vsphere_errmsg = result.get('msg')
#         error_msg = "Failed to create vsphere host {}".format(vsphere_errmsg)
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg)
#     elif result:
#         logger.debug("host creation successfully")
#         return make_ok_resp(code=CODE_CREATED)
#     else:
#         error_msg = "Failed to create host {}".format(body["name"])
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg)
#
#
# @bp_host_api.route('/host', methods=['PUT'])
# def host_update():
#     request_debug(r, logger)
#     if r.content_type.startswith("application/json"):
#         body = dict(r.get_json(force=True, silent=True))
#     else:
#         body = r.form
#     if "id" not in body:
#         error_msg = "host PUT without enough data"
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg,
#                               data=body)
#     else:
#         id, d = body["id"], {}
#         for k in body:
#             if k != "id":
#                 d[k] = body.get(k)
#         result = host_handler.update(id, d)
#         if result:
#             logger.debug("host PUT successfully")
#             return make_ok_resp()
#         else:
#             error_msg = "Failed to update host {}".format(result.get("name"))
#             logger.warning(error_msg)
#             return make_fail_resp(error=error_msg)
#
#
# @bp_host_api.route('/host', methods=['PUT', 'DELETE'])
# def host_delete():
#     request_debug(r, logger)
#     request_data = r.get_json(force=True, silent=True)
#     if "id" in r.form:
#         host_id = r.form["id"]
#     elif "id" in request_data:
#         host_id = request_data.get("id")
#     else:
#         error_msg = "host delete without enough data"
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg, data=r.form)
#
#     logger.debug("host delete with id={0}".format(host_id))
#     if host_handler.delete(id=host_id):
#         return make_ok_resp()
#     else:
#         error_msg = "Failed to delete host {}".format(host_id)
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg)
#
#
# @bp_host_api.route('/host_op', methods=['POST'])
# def host_actions():
#     logger.info("/host_op, method=" + r.method)
#     request_debug(r, logger)
#     if r.content_type.startswith("application/json"):
#         body = dict(r.get_json(force=True, silent=True))
#     else:
#         body = r.form
#
#     host_id, action = body['id'], body['action']
#     if not host_id or not action:
#         error_msg = "host POST without enough data"
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg,
#                               data=body)
#     else:
#         if action == "fillup":
#             if host_handler.fillup(host_id):
#                 logger.debug("fillup successfully")
#                 return make_ok_resp()
#             else:
#                 error_msg = "Failed to fillup the host."
#                 logger.warning(error_msg)
#                 return make_fail_resp(error=error_msg, data=body)
#         elif action == "clean":
#             if host_handler.clean(host_id):
#                 logger.debug("clean successfully")
#                 return make_ok_resp()
#             else:
#                 error_msg = "Failed to clean the host."
#                 logger.warning(error_msg)
#                 return make_fail_resp(error=error_msg, data=body)
#         elif action == "reset":
#             if host_handler.reset(host_id):
#                 logger.debug("reset successfully")
#                 try:
#                     host_model = HostModel.objects.get(id=host_id)
#                     clusters = ClusterModel.objects(host=host_model)
#                     for cluster_item in clusters:
#                         cluster_item.delete()
#                 except Exception:
#                     pass
#                 return make_ok_resp()
#             else:
#                 error_msg = "Failed to reset the host."
#                 logger.warning(error_msg)
#                 return make_fail_resp(error=error_msg, data=body)
#
#     error_msg = "unknown host action={}".format(action)
#     logger.warning(error_msg)
#     return make_fail_resp(error=error_msg, data=body)

host_user_fields = {
    'user_id': fields.String(attribute='id'),
    "username": fields.String,
    'mobile': fields.String
}
host_result_fields = {
    "users": fields.List(fields.Nested(host_user_fields)),
    "totalCount": fields.Integer,
    "pageSize": fields.Integer,
    "pageNo": fields.Integer
}
host_user_list_fields = {
    'stat': fields.Integer(default=200),
    "data": fields.Nested(host_result_fields),
    'msg': fields.String(default='成功')
}
host_user_add_fields = {
    'stat': fields.Integer(default=200),
    "data": fields.String(default=''),
    'msg': fields.String(default='成功')
}

host_user_list_parser = reqparse.RequestParser()
host_user_list_parser.add_argument('pageNo', type=int, default=1, help='第几页')
host_user_list_parser.add_argument('pageSize', type=int, default=10, help='每页显示数')
host_user_list_parser.add_argument('host_id', required=True, help='主机id')

host_user_add_parser = reqparse.RequestParser()
host_user_add_parser.add_argument('host_id', required=True, help='主机id')
host_user_add_parser.add_argument('user_id', required=True, help='主机id')

host_user_delete_parser = reqparse.RequestParser()
host_user_delete_parser.add_argument('host_id', required=True, help='主机id')
host_user_delete_parser.add_argument('user_id', required=True, help='用户id')


class HostUserView(Resource):

    @marshal_with(host_user_list_fields)
    def get(self):
        args = host_user_list_parser.parse_args()
        host_id = args.get('host_id')
        page = args['pageNo']
        per_page = args['pageSize']
        if not host_id:
            error_msg = '缺少参数'
            return make_fail_resp(error=error_msg)

        host = HostModel.objects.get(id=host_id)
        if not host:
            error_msg = '主机不存在'
            return make_fail_resp(error=error_msg)

        offset = (page - 1) * per_page

        user_count = UserModel.objects(host=host).count()
        users = UserModel.objects(host=host).skip(offset).limit(per_page)
        data = {
            'users': users,
            'totalCount': user_count,
            'pageSize': per_page,
            'pageNo': page,
        }
        return {'data': data}

    @marshal_with(host_user_add_fields)
    def post(self):
        args = host_user_add_parser.parse_args()
        host_id = args.get('host_id')
        user_id = args.get('user_id')
        if not all([host_id, user_id]):
            return make_fail_resp(error='参数缺失')

        try:
            host = HostModel.objects.get(id=host_id)
            user = UserModel.objects.get(id=user_id)
        except Exception as e:
            logger.error(e)
            return make_fail_resp(error='db error')
        if not host:
            return make_fail_resp(error='主机不存在')

        # try:
        #     user = UserModel.objects(id=user_id)
        # except Exception as e:
        #     logger.error(e)
        #     return make_fail_resp(error='db error')
        if not user:
            return make_fail_resp(error='用户不存在')
        if user.host == host:
            return {'msg': '用户已在主机列表'}
        try:
            user.update(host=host)
        except Exception as exc:
            logger.warning(exc)
            return make_fail_resp(error='db error')
        return

    @marshal_with(host_user_list_fields)
    def delete(self):
        args = host_user_add_parser.parse_args()
        host_id = args.get('host_id')
        user_id = args.get('user_id')
        if not all([host_id, user_id]):
            return make_fail_resp(error='参数缺失')

        try:
            host = HostModel.objects(id=host_id)
        except Exception as e:
            logger.error(e)
            return make_fail_resp(error='db error')
        if not host:
            return make_fail_resp(error='主机不存在')

        try:
            user = UserModel.objects(id=user_id)
        except Exception as e:
            logger.error(e)
            return make_fail_resp(error='db error')
        try:
            user.update(host=None)
        except Exception as e:
            logger.error(e)
            return make_fail_resp(error='db error')

        return

    # 加个用户，主机对应表


def create_k8s_host(name, capacity, log_type, request):
    if request.get("k8s_ssl") == "on" and request.get("ssl_ca") is not None:
        k8s_ssl = "true"
        k8s_ssl_ca = request["ssl_ca"]
    else:
        k8s_ssl = "false"
        k8s_ssl_ca = None

    request['use_ssl'] = k8s_ssl
    request['use_ssl_ca'] = k8s_ssl_ca

    k8s_must_have_params = {
        'Name': name,
        'Capacity': capacity,
        'LoggingType': log_type,
        'K8SAddress': request['worker_api'],
        'K8SCredType': request['k8s_cred_type'],
        'K8SNfsServer': request['k8s_nfs_server'],
        'K8SUseSsl': request['use_ssl'],
        'K8SSslCert': request['use_ssl_ca']
    }

    if k8s_must_have_params['K8SCredType'] == K8S_CRED_TYPE['account']:
        k8s_must_have_params['K8SUsername'] = request['k8s_username']
        k8s_must_have_params['K8SPassword'] = request['k8s_password']
    elif k8s_must_have_params['K8SCredType'] == K8S_CRED_TYPE['cert']:
        k8s_must_have_params['K8SCert'] = request['k8s_cert']
        k8s_must_have_params['K8SKey'] = request['k8s_key']
    elif k8s_must_have_params['K8SCredType'] == K8S_CRED_TYPE['config']:
        k8s_must_have_params['K8SConfig'] = request['k8s_config']

    for key in k8s_must_have_params:
        if k8s_must_have_params[key] == '':
            error_msg = "host POST without {} data".format(key)
            logger.warning(error_msg)
            return []

    return k8s_must_have_params
