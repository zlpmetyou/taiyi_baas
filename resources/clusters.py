# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import logging
import os
import sys
import json
import demjson

from flask import Blueprint
from flask import request as r
from flask_login import login_required, utils
from flask_restful import Resource, reqparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common import log_handler, LOG_LEVEL, \
    request_get, make_ok_resp, make_fail_resp, \
    request_debug, request_json_body, \
    CODE_CREATED, CODE_NOT_FOUND, \
    NETWORK_TYPES, NETWORK_TYPE_FABRIC_PRE_V1, \
    NETWORK_TYPE_FABRIC_V1, NETWORK_TYPE_FABRIC_V1_1, \
    NETWORK_TYPE_FABRIC_V1_2, \
    CONSENSUS_PLUGINS_FABRIC_V1, CONSENSUS_MODES, NETWORK_SIZE_FABRIC_PRE_V1, \
    FabricPreNetworkConfig, FabricV1NetworkConfig,CLUSTER_SIZE, FabricNetworkConfig

from modules.models import Host as HostModel
from modules.models import Cluster as ClusterModel
from modules import cluster_handler, host_handler
from tasks import release_cluster, delete_cluster
# from common.request_fabric_api import get_token_api,send_cluster_info_api

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

cluster_list_parser = reqparse.RequestParser()
cluster_list_parser.add_argument('pageNo', type=int, default=1, help='第几页')
cluster_list_parser.add_argument('pageSize', type=int, default=10, help='每页显示数')
# cluster_list_parser.add_argument('host_id', required=True, help='主机id')

cluster_create_parser = reqparse.RequestParser()
cluster_create_parser.add_argument('cluster_name', required=True, help='链名')
# cluster_create_parser.add_argument('host', required=True, location=['form', 'json'], help='主机')
cluster_create_parser.add_argument('domain', help='域名')
cluster_create_parser.add_argument('channel', help='通道')
cluster_create_parser.add_argument('network_type', help='网络类型')
cluster_create_parser.add_argument('channels', help='通道', action='append')
cluster_create_parser.add_argument('consensus_plugin', help='共识算法')
cluster_create_parser.add_argument('ca', help='CA')
cluster_create_parser.add_argument('orderers', help='orderers')
cluster_create_parser.add_argument('orderer_orgs', help='orderer_orgs', action='append')
cluster_create_parser.add_argument('peer_orgs', help='peer_orgs', action='append')

cluster_delete_parser = reqparse.RequestParser()
cluster_delete_parser.add_argument('cluster_id', help='链id')
# cluster_delete_parser.add_argument('state', location=['form', 'json'], help='活动状态')


class ClusterView(Resource):

    @login_required
    def get(self):

        request_debug(r, logger)
        user = utils._get_user()
        user = user.dbUser
        user_id = str(user.id)
        args = cluster_list_parser.parse_args()
        page = args['pageNo']
        per_page = args['pageSize']
        result = cluster_handler.list(page_no=page, page_size=per_page, user=user)
        # result = cluster_handler.list(page_no=page, page_size=per_page, user_id=user_id)
        return make_ok_resp(data=result)

    @login_required
    def post(self):
        user = utils._get_user()
        user = user.dbUser

        body = cluster_create_parser.parse_args()
        cluster_name = body.get('cluster_name')
        network_type = body.get('network_type')
        consensus_plugin = body.get('consensus_plugin')
        domain = body.get('domain')
        channel = body.get('channel')
        orderer = body.get('orderer')
        peer_orgs = body.get('peer_orgs')
        orderer_org = body.get('orderer_org')

        if not all([cluster_name, network_type, peer_orgs, channel, domain]):
            error_msg = "参数缺失"
            logger.warning(error_msg)
            return make_fail_resp(error=error_msg, data=body)

        host_id = ''
        try:
            hosts = HostModel.objects.all()
            for host in hosts:
                if len(host.clusters) < host.capacity:
                    host_id = host.id
                    break
        except Exception as e:
            logger.error(e)
            return make_fail_resp(error='db error')

        if not host_id:
            return {'stat': 401, 'msg': '服务器已满，请联系客服'}

        if network_type not in NETWORK_TYPES:
            error_msg = "Unknown network_type={}".format(network_type)
            logger.warning(error_msg)
            return make_fail_resp()

        peer_org_list = []

        orderer_org = {'name': 'orderer', 'domain': domain, 'orderers': ['orderer']}

        for peer_org in peer_orgs:
            peer_org = demjson.decode(peer_org)
            if not all([peer_org.get('name'), peer_org.get('peers')]):
                return make_fail_resp(error='参数缺失', data=body)
            peer_org['peers'] = ['peer{}'.format(i) for i in range(int(peer_org['peers']))]
            peer_org['domain'] = domain
            peer_org['ca'] = 'ca'
            peer_org_list.append(peer_org)

        cluster = ClusterModel.objects(name=cluster_name)
        if cluster:
            return make_fail_resp(error='链名重复')

        config = FabricNetworkConfig(
            consensus_plugin=consensus_plugin,
            network_type=network_type,
            channel=channel,
            orderer_org=orderer_org,
            peer_orgs=peer_org_list
        )
        config.domain = domain
        if not config.validate():
            return make_fail_resp(error="config not validated",
                                  data=config.get_data())

        if cluster_handler.create(name=cluster_name, host_id=host_id, config=config, user=user):
            logger.debug("cluster POST successfully")
            return make_ok_resp()
        else:
            logger.debug("cluster creation failed using handlder")
            return make_fail_resp(error="Failed to create cluster {}".
                                  format(cluster_name))

    def put(self):
        pass

    @login_required
    def delete(self):
        """Delete a cluster
        #
        #     DELETE /cluster
        #     {
        #         id: xxx
        #         col_name: active
        #     }
        #
        #     :return: response obj
        #     """
        logger.info("/cluster action=" + r.method)
        # request_data = r.get_json(force=True, silent=True)
        # if r.form:
        #     cluster_id = r.form["id"]
        #     col_name = r.form["col_name"]
        # else:
        #     cluster_id = request_data.get("id")
        #     col_name = request_data.get("col_name")
        # request_debug(r, logger)
        args = cluster_delete_parser.parse_args()
        cluster_id = args.get('cluster_id')
        # col_name = args.get('state')
        if not cluster_id:
            error_msg = "缺少参数"
            logger.warning(error_msg)
            return make_fail_resp(error=error_msg)
        else:
            logger.debug("cluster delete with id={0}".format(
                cluster_id))
            try:
                cluster = ClusterModel.objects.get(id=cluster_id)
            except Exception as e:
                logger.error(e)
                return {'stat': 400, 'msg': '不存在'}
            # status = cluster.state
            delete_cluster(cluster_id=cluster_id, status='active')
            return make_ok_resp()


# def cluster_start(r):
#     """Start a cluster which should be in stopped status currently.
#
#     :param r:
#     :return:
#     """
#     cluster_id = request_get(r, "cluster_id")
#     if not cluster_id:
#         logger.warning("No cluster_id is given")
#         return make_fail_resp("No cluster_id is given")
#     if cluster_handler.start(cluster_id):
#         return make_ok_resp()
#
#     return make_fail_resp("cluster start failed")
#
#
# def cluster_restart(r):
#     """Start a cluster which should be in stopped status currently.
#
#     :param r:
#     :return:
#     """
#     cluster_id = request_get(r, "cluster_id")
#     if not cluster_id:
#         logger.warning("No cluster_id is given")
#         return make_fail_resp("No cluster_id is given")
#     if cluster_handler.restart(cluster_id):
#         return make_ok_resp()
#
#     return make_fail_resp("cluster restart failed")
#
#
# def cluster_stop(r):
#     """Stop a cluster which should be in running status currently.
#
#     :param r:
#     :return:
#     """
#     cluster_id = request_get(r, "cluster_id")
#     if not cluster_id:
#         logger.warning("No cluster_id is given")
#         return make_fail_resp("No cluster_id is given")
#     if cluster_handler.stop(cluster_id):
#         return make_ok_resp()
#
#     return make_fail_resp("cluster stop failed")
#
#
# def cluster_apply(r):
#     """Apply a cluster.
#
#     Return a Cluster json body.
#     """
#     request_debug(r, logger)
#
#     user_id = request_get(r, "user_id")
#     if not user_id:
#         logger.warning("cluster_apply without user_id")
#         return make_fail_resp("cluster_apply without user_id")
#
#     allow_multiple, condition = request_get(r, "allow_multiple"), {}
#
#     consensus_plugin = request_get(r, "consensus_plugin")
#     consensus_mode = request_get(r, "consensus_mode")
#     cluster_size = int(request_get(r, "size") or -1)
#     if consensus_plugin:
#         if consensus_plugin not in CONSENSUS_PLUGINS_FABRIC_V1:
#             logger.warning("Invalid consensus_plugin")
#             return make_fail_resp("Invalid consensus_plugin")
#         else:
#             condition["consensus_plugin"] = consensus_plugin
#
#     if consensus_mode:
#         if consensus_mode not in CONSENSUS_MODES:
#             logger.warning("Invalid consensus_mode")
#             return make_fail_resp("Invalid consensus_mode")
#         else:
#             condition["consensus_mode"] = consensus_mode
#
#     if cluster_size >= 0:
#         if cluster_size not in NETWORK_SIZE_FABRIC_PRE_V1:
#             logger.warning("Invalid cluster_size")
#             return make_fail_resp("Invalid cluster_size")
#         else:
#             condition["size"] = cluster_size
#
#     logger.debug("condition={}".format(condition))
#     c = cluster_handler.apply_cluster(user_id=user_id, condition=condition,
#                                       allow_multiple=allow_multiple)
#     if not c:
#         logger.warning("cluster_apply failed")
#         return make_fail_resp("No available res for {}".format(user_id))
#     else:
#         return make_ok_resp(data=c)
#
#
# def cluster_release(r):
#     """Release a cluster which should be in used status currently.
#
#     :param r:
#     :return:
#     """
#     cluster_id = request_get(r, "cluster_id")
#     if not cluster_id:
#         logger.warning("No cluster_id is given")
#         return make_fail_resp("No cluster_id is given")
#     release_cluster.delay(cluster_id)
#
#     return make_ok_resp()
#
#
# @front_rest_v2.route('/cluster_op', methods=['GET', 'POST'])
# @bp_cluster_api.route('/cluster_op', methods=['GET', 'POST'])
# def cluster_actions():
#     """Issue some operations on the cluster.
#     Valid operations include: apply, release, start, stop, restart
#     e.g.,
#     apply a cluster for user: GET /cluster_op?action=apply&user_id=xxx
#     release a cluster: GET /cluster_op?action=release&cluster_id=xxx
#     start a cluster: GET /cluster_op?action=start&cluster_id=xxx
#     stop a cluster: GET /cluster_op?action=stop&cluster_id=xxx
#     restart a cluster: GET /cluster_op?action=restart&cluster_id=xxx
#
#     Return a json obj.
#     """
#     request_debug(r, logger)
#     action = request_get(r, "action")
#     logger.info("cluster_op with action={}".format(action))
#     if action == "apply":
#         return cluster_apply(r)
#     elif action == "release":
#         return cluster_release(r)
#     elif action == "start":
#         return cluster_start(r)
#     elif action == "stop":
#         return cluster_stop(r)
#     elif action == "restart":
#         return cluster_restart(r)
#     else:
#         return make_fail_resp(error="Unknown action type")

#
# @bp_cluster_api.route('/cluster/<cluster_id>', methods=['GET'])
# @front_rest_v2.route('/cluster/<cluster_id>', methods=['GET'])
# def cluster_query(cluster_id):
#     """Query a json obj of a cluster
#
#     GET /cluster/xxxx
#
#     Return a json obj of the cluster.
#     """
#     request_debug(r, logger)
#     result = cluster_handler.get_by_id(cluster_id)
#     logger.info(result)
#     if result:
#         return make_ok_resp(data=result)
#     else:
#         error_msg = "cluster not found with id=" + cluster_id
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg, data=r.form,
#                               code=CODE_NOT_FOUND)
#
#
# @bp_cluster_api.route('/cluster', methods=['POST'])
# def cluster_create():
#     """Create a cluster on a host
#
#     POST /cluster
#     {
#     name: xxx,
#     host_id: xxx,
#     network_type=fabric-0.6,
#     consensus_plugin: pbft,
#     consensus_mode: batch,
#     size: 4,
#     }
#
#     :return: response object
#     """
#     logger.info("/cluster action=" + r.method)
#     request_debug(r, logger)
#     if r.content_type.startswith("application/json"):
#         body = dict(r.get_json(force=True, silent=True))
#     else:
#         body = r.form
#     if not body["name"] or not body["host_id"] or \
#             not body["network_type"]:
#         error_msg = "cluster post without enough data"
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg, data=body)
#
#     name, host_id, network_type, size = \
#         body['name'], body['host_id'],\
#         body['network_type'], int(body['size'])
#
#     if network_type == NETWORK_TYPE_FABRIC_PRE_V1:  # TODO: deprecated soon
#         config = FabricPreNetworkConfig(
#             consensus_plugin=body['consensus_plugin'],
#             consensus_mode=body['consensus_mode'],
#             size=size)
#     elif network_type == NETWORK_TYPE_FABRIC_V1:
#         config = FabricV1NetworkConfig(
#             consensus_plugin=body['consensus_plugin'],
#             size=size)
#     elif network_type == NETWORK_TYPE_FABRIC_V1_1:
#         config = FabricV1NetworkConfig(
#             consensus_plugin=body['consensus_plugin'],
#             size=size)
#         config.network_type = NETWORK_TYPE_FABRIC_V1_1
#     elif network_type == NETWORK_TYPE_FABRIC_V1_2:
#         config = FabricV1NetworkConfig(
#             consensus_plugin=body['consensus_plugin'],
#             size=size)
#         config.network_type = NETWORK_TYPE_FABRIC_V1_2
#     else:
#         error_msg = "Unknown network_type={}".format(network_type)
#         logger.warning(error_msg)
#         return make_fail_resp()
#
#     if not config.validate():
#         return make_fail_resp(error="config not validated",
#                               data=config.get_data())
#
#     if cluster_handler.create(name=name, host_id=host_id, config=config):
#         logger.debug("cluster POST successfully")
#         return make_ok_resp(code=CODE_CREATED)
#     else:
#         logger.debug("cluster creation failed using handlder")
#         return make_fail_resp(error="Failed to create cluster {}".
#                               format(name))
#
#
# @bp_cluster_api.route('/cluster', methods=['DELETE'])
# def cluster_delete():
#     """Delete a cluster
#
#     DELETE /cluster
#     {
#         id: xxx
#         col_name: active
#     }
#
#     :return: response obj
#     """
#     logger.info("/cluster action=" + r.method)
#     request_data = r.get_json(force=True, silent=True)
#     if r.form:
#         cluster_id = r.form["id"]
#         col_name = r.form["col_name"]
#     else:
#         cluster_id = request_data.get("id")
#         col_name = request_data.get("col_name")
#     request_debug(r, logger)
#     if not cluster_id or not col_name:
#         error_msg = "cluster operation post without enough data"
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg, data=r.form)
#     else:
#         logger.debug("cluster delete with id={0}, col_name={1}".format(
#             cluster_id, col_name))
#         delete_cluster.delay(cluster_id, col_name)
#         return make_ok_resp()
#
#
# @bp_cluster_api.route('/clusters', methods=['GET', 'POST'])
# @front_rest_v2.route('/clusters', methods=['GET', 'POST'])
# def cluster_list():
#     """List clusters with the filter
#     e.g.,
#
#     GET /clusters?consensus_plugin=pbft
#
#     Return objs of the clusters.
#     """
#     request_debug(r, logger)
#     f = {}
#     if r.method == 'GET':
#         f.update(r.args.to_dict())
#     elif r.method == 'POST':
#         f.update(request_json_body(r))
#     logger.info(f)
#     col_name = f.get("state", "active")
#     result = cluster_handler.list(filter_data=f, col_name=col_name)
#     logger.error(result)
#     return make_ok_resp(data=result)
#
#
# # will deprecate
# @front_rest_v2.route('/cluster_apply', methods=['GET', 'POST'])
# def cluster_apply_dep():
#     """
#     Return a Cluster json body.
#     """
#     request_debug(r, logger)
#
#     user_id = request_get(r, "user_id")
#     if not user_id:
#         error_msg = "cluster_apply without user_id"
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg)
#
#     allow_multiple, condition = request_get(r, "allow_multiple"), {}
#
#     consensus_plugin = request_get(r, "consensus_plugin")
#     consensus_mode = request_get(r, "consensus_mode")
#     cluster_size = int(request_get(r, "size") or -1)
#     if consensus_plugin:
#         if consensus_plugin not in CONSENSUS_PLUGINS_FABRIC_V1:
#             error_msg = "Invalid consensus_plugin"
#             logger.warning(error_msg)
#             return make_fail_resp(error=error_msg)
#         else:
#             condition["consensus_plugin"] = consensus_plugin
#
#     if consensus_mode:
#         if consensus_mode not in CONSENSUS_MODES:
#             error_msg = "Invalid consensus_mode"
#             logger.warning(error_msg)
#             return make_fail_resp(error=error_msg)
#         else:
#             condition["consensus_mode"] = consensus_mode
#
#     if cluster_size >= 0:
#         if cluster_size not in NETWORK_SIZE_FABRIC_PRE_V1:
#             error_msg = "Invalid cluster_size"
#             logger.warning(error_msg)
#             return make_fail_resp(error=error_msg)
#         else:
#             condition["size"] = cluster_size
#
#     logger.debug("condition={}".format(condition))
#     c = cluster_handler.apply_cluster(user_id=user_id, condition=condition,
#                                       allow_multiple=allow_multiple)
#     if not c:
#         error_msg = "No available res for {}".format(user_id)
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg)
#     else:
#         return make_ok_resp(data=c)
#
#
# # will deprecate
# @front_rest_v2.route('/cluster_release', methods=['GET', 'POST'])
# def cluster_release_dep():
#     """
#     Return status.
#     """
#     request_debug(r, logger)
#     user_id = request_get(r, "user_id")
#     cluster_id = request_get(r, "cluster_id")
#     if not user_id and not cluster_id:
#         error_msg = "cluster_release without id"
#         logger.warning(error_msg)
#         return make_fail_resp(error=error_msg, data=r.args)
#     else:
#         result = None
#         if cluster_id:
#             result = cluster_handler.release_cluster(cluster_id=cluster_id)
#         elif user_id:
#             result = cluster_handler.release_cluster_for_user(user_id=user_id)
#         if not result:
#             error_msg = "cluster_release failed user_id={} cluster_id={}". \
#                 format(user_id, cluster_id)
#             logger.warning(error_msg)
#             data = {
#                 "user_id": user_id,
#                 "cluster_id": cluster_id,
#             }
#             return make_fail_resp(error=error_msg, data=data)
#         else:
#             return make_ok_resp()
