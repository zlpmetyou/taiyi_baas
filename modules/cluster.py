# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import datetime
import json
import logging
import os
import shutil
import sys
import time
from uuid import uuid4
from threading import Thread
import socket

import requests
# from xpinyin import Pinyin
from pymongo.collection import ReturnDocument

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.request_fabric_api import send_new_user_info
from agent import get_swarm_node_ip, KubernetesHost
from config_files.generate_config_files import GenerateChainBlockConfig
from config_files.compose_handler import ComposeHandler
from common import db, log_handler, LOG_LEVEL, utils, BLOCKCHAIN_CONFIG_FILES_PATH
from common import CLUSTER_PORT_START, CLUSTER_PORT_STEP, \
    NETWORK_TYPE_FABRIC_PRE_V1, NETWORK_TYPE_FABRIC_V1, \
    CONSENSUS_PLUGINS_FABRIC_V1, ORG_SIZE, \
    NETWORK_TYPE_FABRIC_V1_1, NETWORK_TYPE_FABRIC_V1_2, \
    WORKER_TYPES, WORKER_TYPE_DOCKER, WORKER_TYPE_SWARM, WORKER_TYPE_K8S, \
    WORKER_TYPE_VSPHERE, VMIP, \
    NETWORK_SIZE_FABRIC_PRE_V1, NETWORK_TYPES, \
    PEER_SERVICE_PORTS, \
    ORDERER_SERVICE_PORTS, \
    NETWORK_STATUS_CREATING, NETWORK_STATUS_RUNNING, NETWORK_STATUS_DELETING

from common import FabricPreNetworkConfig, FabricV1NetworkConfig, BLOCK_CHAIN_PROBATION_PERIOD

from modules import host

from agent import ClusterOnDocker, ClusterOnVsphere, ClusterOnKubernetes
from modules.models import Cluster as ClusterModel
from modules.models.host import Channel as ChannelModel
from modules.models.host import Org as OrgModel
from modules.models.host import Node
from modules.models import Host as HostModel
from modules.models import ClusterSchema, CLUSTER_STATE, \
    Container, ServicePort

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

peer_service_ports = {
    '{}_{}_grpc': 7051,
    '{}_{}_event': 7053,
}

ca_service_ports = {
    '{}_{}_ecap': 7054,
}

orderer_service_ports = {
    '{}_{}': 7050
}

url_map = {
    '120.27.20.114': '172.31.239.245',
    '47.105.86.107': '172.31.239.247',
    '47.105.161.225': '172.31.239.248',
    '47.105.64.58': '172.31.239.249',
    '47.105.164.116': '172.31.239.250',
    '47.105.163.14': '172.31.239.251'
}


# def to_pinyin(word):
#     p = Pinyin()
#     result = p.get_pinyin(word, '')
#     return result


class ClusterHandler(object):
    """ Main handler to operate the cluster in pool

    """

    def __init__(self):
        self.col_active = db["cluster_active"]
        self.col_released = db["cluster_released"]
        self.host_handler = host.host_handler
        self.cluster_agents = {
            'docker': ClusterOnDocker(),
            'swarm': ClusterOnDocker(),
            'vsphere': ClusterOnVsphere(),
            'kubernetes': ClusterOnKubernetes()
        }

    def list(self, user, page_no=1, page_size=10):
        """ List clusters with given criteria

        :param page_no: Image with the filter properties
        :param page_size: Use data in which col_name
        :return: list of serialized doc
        """
        # result = []
        # if col_name in [e.name for e in CLUSTER_STATE]:
        #     logger.debug("List all {} clusters".format(col_name))
        #     filter_data.update({
        #         "state": col_name
        #     })
        #     clusters = ClusterModel.objects(__raw__=filter_data)
        #     result = self._schema(clusters, many=True)
        # else:
        #     logger.warning("Unknown cluster col_name=" + col_name)
        offset = (page_no - 1) * page_size
        if user.isAdmin:
            clusters = ClusterModel.objects.skip(offset).limit(page_size).order_by('-create_ts')
            cluster_count = ClusterModel.objects.all().count()

        else:
            clusters = ClusterModel.objects(user=user).skip(offset).limit(page_size).order_by('-create_ts')
            cluster_count = ClusterModel.objects(user=user).count()

        cluster_list = []
        sequence_num = (page_no * page_size) - (page_size - 1)
        for cluster in clusters:
            channels = ChannelModel.objects.get(cluster=cluster)
            cluster_info = {
                'id': sequence_num,
                "cluster_id": str(cluster.id),
                'name': cluster.name,
                'config': 'fabric-1.1基础配置',
                'channel': channels.name,
                'channel_id': str(channels.alias),
                'username': cluster.user.username,
                "consensus_plugin": cluster.consensus_plugin,
                "host": str(cluster.host.name),
                'domain': cluster.domain,
                'create_ts': cluster.create_ts.strftime("%Y-%m-%d %H:%M:%S"),
                'due_time': cluster.due_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": cluster.status
            }
            cluster_list.append(cluster_info)
            sequence_num += 1
        result = {
            'pageNo': page_no,
            'pageSize': page_size,
            'totalCount': cluster_count,
            'clusters': cluster_list
        }

        return result

    def get_by_id(self, id, col_name="active"):
        """ Get a cluster for the external request

        :param id: id of the doc
        :param col_name: collection to check
        :return: serialized result or obj
        """
        try:
            state = CLUSTER_STATE.active.name if \
                col_name != CLUSTER_STATE.released.name else \
                CLUSTER_STATE.released.name
            logger.info("find state {} cluster".format(state))
            cluster = ClusterModel.objects.get(id=id)
        except Exception:
            logger.warning("No cluster found with id=" + id)
            return {}
        return self._schema(cluster)

    def gen_service_urls(self, cid, peer_ports, ca_ports, orderer_ports):
        """
        Generate the service urls based on the mapping ports
        :param cid: cluster id to operate with
        :param peer_ports: peer ports mapping
        :param ca_ports: ca ports mapping
        :param orderer_ports: orderer ports mapping
        :return: service url mapping. {} means failure
        """
        access_peer = 'peer0.org1.example.com'
        access_ca = 'ca.example.com'

        peer_host_ip = self._get_service_ip(cid, access_peer)
        # explorer_host_ip = self._get_service_ip(cid, access_explorer)
        # no api_url, then clean and return
        if not peer_host_ip:  # not valid api_url
            logger.error("Error to find peer host url, cleanup")
            self.delete(id=cid, record=False, forced=True)
            return {}
        ca_host_ip = self._get_service_ip(cid, access_ca)

        service_urls = {}
        for k, v in peer_ports.items():
            service_urls[k] = "{}:{}".format(peer_host_ip, v)
        for k, v in ca_ports.items():
            service_urls[k] = "{}:{}".format(ca_host_ip, v)
        for k, v in orderer_ports.items():
            service_urls[k] = "{}:{}".format(ca_host_ip, v)
        return service_urls

    def gen_ports_mapping(self, orderer_services, ca_services, peer_services, start_port, host_id):
        """
        Generate the ports and service mapping for given size of network
        :param orderer_services: number of peers
        :param ca_services: number of cas
        :param peer_services: number of orgs
        :param start_port: mapping range start with
        :param host_id: find ports at which host
        :return: the mapping ports, empty means failure
        """
        request_port_num = len(orderer_services)+len(ca_services)+len(peer_services)
        logger.debug("request port number {}".format(request_port_num))

        if start_port <= 0:  # need to dynamic find available ports
            ports = self.find_free_start_ports(host_id, request_port_num)
        else:
            ports = list(range(start_port, start_port + request_port_num))
        if not ports:
            logger.warning("No free port is found")
            return {}, {}, {}, {}, {}
        else:
            logger.debug("ports {}".format(ports))

        peer_ports, ca_ports, orderer_ports = {}, {}, {}
        all_ports = {}

        pos = 0

        for orderer_service in orderer_services:
            orderer_ports[orderer_service] = ports[pos]
            pos += 1
        for peer_service in peer_services:
            peer_ports[peer_service] = ports[pos]
            pos += 1
        for ca_service in ca_services:
            ca_ports[ca_service] = ports[pos]
            pos += 1

        all_ports.update(peer_ports)
        all_ports.update(ca_ports)
        all_ports.update(orderer_ports)

        return all_ports, peer_ports, ca_ports, orderer_ports

    def _create_cluster(self, cluster, cid, mapped_ports, worker, config,
                        user, peer_ports, ca_ports, orderer_ports):
        # start compose project, failed then clean and return
        logger.debug("Start compose project with name={}".format(cid))
        config_path = BLOCKCHAIN_CONFIG_FILES_PATH
        logger.info('config_path:{}'.format(config_path))
        compose_file_handler = ComposeHandler(cluster)
        compose_file_handler.create_cluster()

        containers = self.cluster_agents[worker.host_type] \
            .create(cid, mapped_ports, self.host_handler.schema(worker),
                    config=config, user_id=user)
        if not containers:
            logger.warning("failed to start cluster={}, then delete"
                           .format(cluster.name))
            self.delete(id=cid, record=False, forced=True)
            worker.update(pull__clusters=id)

            cluster.delete()
            return None

        # creation done, update the container table in db
        for k, v in containers.items():
            container = Container(id=v, name=k, cluster=cluster)
            container.save()

        service_urls = ClusterModel.objects.get(id=cid).service_url

        for k, v in service_urls.items():
            service_port = ServicePort(name=k, ip=v.split(":")[0],
                                       port=int(v.split(":")[1]),
                                       cluster=cluster)
            service_port.save()

        pos = 0
        cluster = ''
        peer_join_stat = False

        while pos <= 5:

            try:
                cluster = ClusterModel.objects.get(id=cid)
            except Exception as e:
                logger.error(e)
            if cluster.status == 'running':
                peer_join_stat = True
                break
            time.sleep(2)
            pos += 1
        # peer_join_stat = True
        # if peer_join_stat:

        def check_health_work(cid):
            # time.sleep(5)
            if self.refresh_health(cid):
                return True
        # t = Thread(target=check_health_work, args=(cid,))
        # t.start()
        # if check_health_work(cid):
        if check_health_work(cid) and peer_join_stat:
            cluster_info = compose_file_handler.generate_chaincode_config()
            logger.info('{}'.format(cluster_info))
            from tasks import send_cluster_info
            time.sleep(10)
            send_cluster_info(config_path=config_path, cid=cid, cluster_info=cluster_info, user_id=str(user.id))
            # org = OrgModel.objects.get(cluster=cluster,org_type='peer')
            # body = {
            #     "BlockchainSign": str(cluster.id),
            #     "ChannelId": config.channel,
            #     "OrgId": str(org.alias),
            #     "UserId": str(user.id)
            # }
            # logger.info('add user info:{}'.format(body))
            # if not send_new_user_info(str(user.id), body=body):
            #     return {'stat': 400, 'msg': '添加用户失败'}
            host_obj = HostModel.objects.get(id=worker.id)
            host_obj.update(add_to_set__clusters=[cid])
            logger.info("Create cluster OK, id={}".format(cid))
            return True
        else:
            logger.info('peer join channel failed')
            return False

    def create(self, name, host_id, config, user, start_port=0,
               ):
        """ Create a cluster based on given data

        TODO: maybe need other id generation mechanism
        Args:

            name: name of the cluster
            host_id: id of the host URL
            domain: domain of the cluster
            channel: channel of the cluster
            config: network configuration
            start_port: first service port for cluster, will generate
             if not given
            user: user_id of the cluster if start to be applied

        return: Id of the created cluster or None
        """
        logger.info("Create cluster {}, host_id={}, config={}, start_port={}, "
                    "user_id={}".format(name, host_id, config,
                                        start_port, user))

        worker = self.host_handler.get_active_host_by_id(host_id)
        if not worker:
            logger.error("Cannot find available host to create new network")
            return None
        cid = uuid4().hex

        orderer_services = []
        ca_services = []
        peer_services = []

        orderer_org = config.get('orderer_org')
        orderer_org_name = orderer_org.get('name')
        orderers = orderer_org.get('orderers')
        for orderer in orderers:
            for k in orderer_service_ports.keys():
                orderer_services.append(k.format(orderer, orderer_org_name))

        for peer_org in config.peer_orgs:
            ca_name = peer_org.get('ca')
            org_name = peer_org.get('name')
            peers = peer_org.get('peers')

            for j in ca_service_ports.keys():
                ca_services.append(j.format(ca_name, org_name))
            for peer in peers:
                for k in peer_service_ports.keys():
                    peer_services.append(k.format(peer, org_name))

        mapped_ports, peer_ports, ca_ports, orderer_ports = \
            self.gen_ports_mapping(orderer_services, ca_services, peer_services, start_port, host_id)

        if not mapped_ports:
            logger.error("mapped_ports={}".format(mapped_ports))
            return None
        worker.update(add_to_set__port_used=list(mapped_ports.values()))
        env_mapped_ports = dict(((k + '_port').upper(), str(v))
                                for (k, v) in mapped_ports.items())

        network_type = config['network_type']
        consensus_plugin = config['consensus_plugin']
        service_url = {}
        host_ip = worker.worker_api.split(':')[1][2:]
        for k, v in mapped_ports.items():
            service_url[k] = "{}:{}".format(url_map[host_ip], v)

        create_time = datetime.datetime.now()
        net = {
            'id': cid,
            'name': name,
            'host': worker,
            'domain': config.get('domain'),
            'network_type': network_type,
            'consensus_plugin': consensus_plugin,
            'ports': list(mapped_ports.values()),
            'env': env_mapped_ports,
            'status': NETWORK_STATUS_RUNNING,
            # 'status': NETWORK_STATUS_CREATING,
            # 'mapped_ports': mapped_ports,
            'create_ts': create_time,
            'due_time': create_time + datetime.timedelta(days=BLOCK_CHAIN_PROBATION_PERIOD),
            'user': user,
            'service_url': service_url,  # e.g., {rest: xxx:7050, grpc: xxx:7051}
        }

        # try to start one cluster at the host
        cluster = ClusterModel(**net)
        cluster.host = worker
        cluster.save()

        channel = ChannelModel(
            name=config.channel,
            alias='channel1',
            cluster=cluster
        )
        channel.save()

        orderer_org = OrgModel(
            name=orderer_org_name,
            alias='orderer',
            domain=config.orderer_org.get('domain'),
            org_type='orderer',
            cluster=cluster
        )
        orderer_org.save()
        start = 0
        for orderer in config.orderer_org.get('orderers'):
            orderer = Node(
                name=orderer,
                alias='orderer{}'.format(start if start else ''),
                ip=url_map[host_ip],
                org=orderer_org,
                node_type='orderer',
                ports={'orderer': mapped_ports.get('{}_{}'.format(orderer, orderer_org.name))}
            )
            orderer.save()
            channel.update(add_to_set__orderers=[orderer])
            start += 1

        org_start = 0
        for peer_org in config.peer_orgs:
            peer_org_name = peer_org.get('name')
            _peer_org = OrgModel(
                name=peer_org_name,
                alias='org{}'.format(org_start+1),
                domain=peer_org.get('domain'),
                org_type='peer',
                # users=[user],
                cluster=cluster
            )
            _peer_org.save()
            channel.update(add_to_set__orgs=[_peer_org])
            org_start += 1
            peer_start = 0
            for peer in peer_org.get('peers'):
                peer = Node(
                    name=peer,
                    alias='peer{}'.format(peer_start),
                    ip=url_map[host_ip],
                    org=_peer_org,
                    node_type='peer',
                    ports={
                        'grpc': mapped_ports.get("{}_{}_grpc".format(peer, _peer_org.name)),
                        'event': mapped_ports.get("{}_{}_event".format(peer, _peer_org.name))
                    }
                )
                peer.save()
                peer_start += 1

            ca_name = peer_org.get('ca')
            ca = Node(
                name=ca_name,
                alias='ca',
                ip=url_map[host_ip],
                node_type='ca',
                org=_peer_org,
                ports={'ecap': mapped_ports.get('{}_{}_ecap'.format(ca_name, _peer_org.name))}
            )
            ca.save()

        if self._create_cluster(cluster, cid, mapped_ports, worker, config, user, peer_ports, ca_ports, orderer_ports):
            return cid
        else:
            cluster.delete()
            return False

    def delete(self, id, record=False, forced=True):
        """ Delete a cluster instance

        Clean containers, remove db entry. Only operate on active host.

        :param id: id of the cluster to delete
        :param record: Whether to record into the released collections
        :param forced: Whether to removing user-using cluster, for release
        :return:
        """
        logger.debug("Delete cluster: id={}, forced={}".format(id, forced))

        try:
            cluster = ClusterModel.objects.get(id=id)
        except Exception:
            logger.warning("Cannot find cluster {}".format(id))
            return False
        user_id = str(cluster.user.id)
        channel = ChannelModel.objects.get(cluster=cluster)
        channel = channel.alias
        logger.info('delete channel :{}'.format(channel))
        from tasks import send_delete_cluster
        # send_delete_cluster.delay(body={'BlockchainSign': id})
        send_delete_cluster(body={'BlockchainSign': id, "ChannelId": channel}, user_id=user_id)
        c = self.db_update_one({"id": id}, {"status": NETWORK_STATUS_DELETING},
                               after=False)
        # we are safe from occasional applying now
        # user_id = c.user_id  # original user_id
        if not forced:
            # not forced, and chain is used by normal user, then no process
            logger.warning("Cannot delete cluster {} by "
                           "user {}".format(id, user_id))
            cluster.update(
                set__user_id=user_id,
                upsert=True
            )
            return False
        else:
            cluster.update(set__status=NETWORK_STATUS_DELETING, upsert=True)

        host_id, worker_api, network_type, consensus_plugin = \
            str(c.host.id), c.host.worker_api, \
            c.network_type if c.network_type else NETWORK_TYPE_FABRIC_PRE_V1, \
            c.consensus_plugin if c.consensus_plugin else \
                CONSENSUS_PLUGINS_FABRIC_V1[0]

        # port = api_url.split(":")[-1] or CLUSTER_PORT_START
        cluster_size = ''
        h = self.host_handler.get_active_host_by_id(host_id)
        if not h:
            logger.warning("Host {} inactive".format(host_id))
            cluster.update(set__user_id=user_id, upsert=True)
            return False

        if network_type == NETWORK_TYPE_FABRIC_V1:
            config = FabricV1NetworkConfig(consensus_plugin=consensus_plugin)

        elif network_type == NETWORK_TYPE_FABRIC_V1_1:
            config = FabricV1NetworkConfig(consensus_plugin=consensus_plugin)
            config.network_type = NETWORK_TYPE_FABRIC_V1_1

        elif network_type == NETWORK_TYPE_FABRIC_V1_2:
            config = FabricV1NetworkConfig(consensus_plugin=consensus_plugin)
            config.network_type = NETWORK_TYPE_FABRIC_V1_2

        elif network_type == NETWORK_TYPE_FABRIC_PRE_V1:
            config = FabricPreNetworkConfig(consensus_plugin=consensus_plugin,
                                            consensus_mode='',
                                            size=cluster_size)
        else:
            return False

        config.update({
            "env": cluster.env
        })

        delete_result = self.cluster_agents[h.host_type].delete(id, worker_api, config)
        config_path = BLOCKCHAIN_CONFIG_FILES_PATH + '/{}'.format(id)
        if os.path.exists(config_path):
            shutil.rmtree(config_path)

        if not delete_result:
            logger.warning("Error to run compose clean work")
            cluster.update(set__user_id=user_id, upsert=True)
            return False

        # remove cluster info from host
        logger.info("remove cluster from host, cluster:{}".format(id))
        h.update(pull__clusters=id)
        orgs = OrgModel.objects(cluster=cluster)
        for org in orgs:
            org_users = org.users
            for user in org_users:
                if int(user.role) in [2, 3]:
                    user.delete()

        c.delete()
        return True

    def delete_released(self, id):
        """ Delete a released cluster record from db

        :param id: id of the cluster to delete
        :return: True or False
        """
        logger.debug("Delete cluster: id={} from release records.".format(id))
        self.col_released.find_one_and_delete({"id": id})
        return True

    def apply_cluster(self, user_id, condition={}, allow_multiple=False):
        """ Apply a cluster for a user

        :param user_id: which user will apply the cluster
        :param condition: the filter to select
        :param allow_multiple: Allow multiple chain for each tenant
        :return: serialized cluster or None
        """
        if not allow_multiple:  # check if already having one
            filt = {"user_id": user_id, "release_ts": "", "health": "OK"}
            filt.update(condition)
            c = self.col_active.find_one(filt)
            if c:
                logger.debug("Already assigned cluster for " + user_id)
                return self._schema(c)
        logger.debug("Try find available cluster for " + user_id)
        cluster = ClusterModel. \
            objects(user_id="",
                    network_type__icontains=condition.get("apply_type",
                                                          "fabric"),
                    size=condition.get("size", 0),
                    status=NETWORK_STATUS_RUNNING,
                    health="OK").first()
        if cluster:
            cluster.update(upsert=True, **{
                "user_id": user_id,
                "apply_ts": datetime.datetime.now()
            })
            logger.info("Now have cluster {} at {} for user {}".format(
                cluster.id, cluster.host.id, user_id))
            return self._schema(cluster)
        logger.warning("Not find matched available cluster for " + user_id)
        return {}

    def release_cluster_for_user(self, user_id):
        """ Release all cluster for a user_id.

        :param user_id: which user
        :return: True or False
        """
        logger.debug("release clusters for user_id={}".format(user_id))
        c = self.col_active.find({"user_id": user_id, "release_ts": ""})
        cluster_ids = list(map(lambda x: x.get("id"), c))
        logger.debug("clusters for user {}={}".format(user_id, cluster_ids))
        result = True
        for cid in cluster_ids:
            result = result and self.release_cluster(cid)
        return result

    def release_cluster(self, cluster_id, record=True):
        """ Release a specific cluster.

        Release means delete and try best to recreate it with same config.

        :param cluster_id: specific cluster to release
        :param record: Whether to record this cluster to release table
        :return: True or False
        """
        c = self.db_update_one(
            {"id": cluster_id},
            {"release_ts": datetime.datetime.now()})
        if not c:
            logger.warning("No cluster find for released with id {}".format(
                cluster_id))
            return True
        if not c.release_ts:  # not have one
            logger.warning("No cluster can be released for id {}".format(
                cluster_id))
            return False

        return self.reset(cluster_id, record)

    def start(self, cluster_id):
        """Start a cluster

        :param cluster_id: id of cluster to start
        :return: Bool
        """
        c = self.get_by_id(cluster_id)
        if not c:
            logger.warning('No cluster found with id={}'.format(cluster_id))
            return False
        h_id = c.get('host_id')
        h = self.host_handler.get_active_host_by_id(h_id)
        if not h:
            logger.warning('No host found with id={}'.format(h_id))
            return False

        network_type = c.get('network_type')
        if network_type == NETWORK_TYPE_FABRIC_PRE_V1:
            config = FabricPreNetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                consensus_mode=c.get('consensus_mode'),
                size=c.get('size'))
        elif network_type == NETWORK_TYPE_FABRIC_V1:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
        elif network_type == NETWORK_TYPE_FABRIC_V1_1:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
            config.network_type = NETWORK_TYPE_FABRIC_V1_1
        elif network_type == NETWORK_TYPE_FABRIC_V1_2:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
            config.network_type = NETWORK_TYPE_FABRIC_V1_2
        else:
            return False

        result = self.cluster_agents[h.type].start(
            name=cluster_id, worker_api=h.worker_api,
            mapped_ports=c.get('mapped_ports', PEER_SERVICE_PORTS),
            log_type=h.log_type,
            log_level=h.log_level,
            log_server='',
            config=config,
        )

        if result:
            if h.type == WORKER_TYPE_K8S:
                service_urls = self.cluster_agents[h.type] \
                    .get_services_urls(cluster_id)
                self.db_update_one({"id": cluster_id},
                                   {'status': 'running',
                                    'api_url': service_urls.get('rest', ""),
                                    'service_url': service_urls})
            else:
                self.db_update_one({"id": cluster_id},
                                   {'status': 'running'})

            return True
        else:
            return False

    def restart(self, cluster_id):
        """Restart a cluster

        :param cluster_id: id of cluster to start
        :return: Bool
        """
        c = self.get_by_id(cluster_id)
        if not c:
            logger.warning('No cluster found with id={}'.format(cluster_id))
            return False
        h_id = c.get('host_id')
        h = self.host_handler.get_active_host_by_id(h_id)
        if not h:
            logger.warning('No host found with id={}'.format(h_id))
            return False

        network_type = c.get('network_type')
        if network_type == NETWORK_TYPE_FABRIC_PRE_V1:
            config = FabricPreNetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                consensus_mode=c.get('consensus_mode'),
                size=c.get('size'))
        elif network_type == NETWORK_TYPE_FABRIC_V1:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
        elif network_type == NETWORK_TYPE_FABRIC_V1_1:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
            config.network_type = NETWORK_TYPE_FABRIC_V1_1
        elif network_type == NETWORK_TYPE_FABRIC_V1_2:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
            config.network_type = NETWORK_TYPE_FABRIC_V1_2
        else:
            return False

        result = self.cluster_agents[h.type].restart(
            name=cluster_id, worker_api=h.worker_api,
            mapped_ports=c.get('mapped_ports', PEER_SERVICE_PORTS),
            log_type=h.log_type,
            log_level=h.log_level,
            log_server='',
            config=config,
        )
        if result:
            if h.type == WORKER_TYPE_K8S:
                service_urls = self.cluster_agents[h.type] \
                    .get_services_urls(cluster_id)
                self.db_update_one({"id": cluster_id},
                                   {'status': 'running',
                                    'api_url': service_urls.get('rest', ""),
                                    'service_url': service_urls})
            else:
                self.db_update_one({"id": cluster_id},
                                   {'status': 'running'})
            return True
        else:
            return False

    def stop(self, cluster_id):
        """Stop a cluster

        :param cluster_id: id of cluster to stop
        :return: Bool
        """
        c = self.get_by_id(cluster_id)
        if not c:
            logger.warning('No cluster found with id={}'.format(cluster_id))
            return False
        h_id = c.get('host_id')
        h = self.host_handler.get_active_host_by_id(h_id)
        if not h:
            logger.warning('No host found with id={}'.format(h_id))
            return False
        network_type = c.get('network_type')
        if network_type == NETWORK_TYPE_FABRIC_PRE_V1:
            config = FabricPreNetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                consensus_mode=c.get('consensus_mode'),
                size=c.get('size'))
        elif network_type == NETWORK_TYPE_FABRIC_V1:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
        elif network_type == NETWORK_TYPE_FABRIC_V1_1:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
            config.network_type = NETWORK_TYPE_FABRIC_V1_1
        elif network_type == NETWORK_TYPE_FABRIC_V1_2:
            config = FabricV1NetworkConfig(
                consensus_plugin=c.get('consensus_plugin'),
                size=c.get('size'))
            config.network_type = NETWORK_TYPE_FABRIC_V1_2
        else:
            return False

        result = self.cluster_agents[h.type].stop(
            name=cluster_id, worker_api=h.worker_api,
            mapped_ports=c.get('mapped_ports', PEER_SERVICE_PORTS),
            log_type=h.log_type,
            log_level=h.log_level,
            log_server='',
            config=config,
        )

        if result:
            self.db_update_one({"id": cluster_id},
                               {'status': 'stopped', 'health': ''})
            return True
        else:
            return False

    def reset(self, cluster_id, record=False):
        """
        Force to reset a chain.

        Delete it and recreate with the same configuration.
        :param cluster_id: id of the reset cluster
        :param record: whether to record into released db
        :return:
        """

        c = self.get_by_id(cluster_id)
        logger.debug("Run recreate_work in background thread")
        cluster_name, host_id, network_type, \
            = c.get("name"), c.get("host_id"), c.get("network_type")
        config = c.get('config')
        if not self.delete(cluster_id, record=record, forced=True):
            logger.warning("Delete cluster failed with id=" + cluster_id)
            return False
        network_type = c.get('network_type')
        # if network_type == NETWORK_TYPE_FABRIC_V1:
        #     config = FabricV1NetworkConfig(
        #         consensus_plugin=c.get('consensus_plugin'),
        #         size=c.get('size'))
        # elif network_type == NETWORK_TYPE_FABRIC_V1_1:
        #     config = FabricV1NetworkConfig(
        #         consensus_plugin=c.get('consensus_plugin'),
        #         size=c.get('size'))
        #     config.network_type = NETWORK_TYPE_FABRIC_V1_1
        # elif network_type == NETWORK_TYPE_FABRIC_V1_2:
        #     config = FabricV1NetworkConfig(
        #         consensus_plugin=c.get('consensus_plugin'),
        #         size=c.get('size'))
        #     config.network_type = NETWORK_TYPE_FABRIC_V1_2
        # else:
        #     return False

        if network_type not in NETWORK_TYPES:
            error_msg = "Unknown network_type={}".format(network_type)
            logger.warning(error_msg)
            return {'msg': error_msg, 'stat': 400}
        else:
            # pass
            new_config = FabricV1NetworkConfig(
                consensus_plugin=config.get('consensus_plugin'),
                peer=config.get('peer'),
                orderer=config.get('orderer'),
                ca=config.get('ca'),
                network_type=config.get('network_type')
            )
            # for k, v in config.items():
            #     new_config.k = v
        if not self.create(name=cluster_name, host_id=host_id, config=new_config):
            logger.warning("Fail to recreate cluster {}".format(cluster_name))
            return False
        return True

    def reset_free_one(self, cluster_id):
        """
        Reset some free chain, mostly because it's broken.

        :param cluster_id: id to reset
        :return: True or False
        """
        logger.debug("Try reseting cluster {}".format(cluster_id))
        self.db_update_one({"id": cluster_id, "user_id": ""},
                           {"status": NETWORK_STATUS_DELETING})
        return self.reset(cluster_id)

    def _serialize(self, doc, keys=('id', 'name', 'user_id', 'host_id',
                                    'network_type',
                                    'consensus_plugin',
                                    'consensus_mode', 'worker_api',
                                    'create_ts', 'apply_ts', 'release_ts',
                                    'duration', 'containers', 'size', 'status',
                                    'health', 'mapped_ports', 'service_url')):
        """ Serialize an obj

        :param doc: doc to serialize
        :param keys: filter which key in the results
        :return: serialized obj
        """
        result = {}
        if doc:
            for k in keys:
                result[k] = doc.get(k, '')
        return result

    def _get_service_ip(self, cluster_id, node='peer0'):
        """
        Get the node's servie ip

        :param cluster_id: The name of the cluster
        :param host: On which host to search the cluster
        :param node: name of the cluster node
        :return: service IP or ""
        """
        host_id = self.get_by_id(cluster_id).get("host_id")
        host = self.host_handler.get_by_id(host_id)
        if not host:
            logger.warning("No host found with cluster {}".format(cluster_id))
            return ""
        worker_api, host_type = host.worker_api, host.host_type
        if host_type not in WORKER_TYPES:
            logger.warning("Found invalid host_type=%s".format(host_type))
            return ""
        # we should diff with simple host and swarm host here
        if host_type == WORKER_TYPE_DOCKER:  # single
            segs = worker_api.split(":")  # tcp://x.x.x.x:2375
            if len(segs) != 3:
                logger.error("Invalid daemon url = ", worker_api)
                return ""
            host_ip = url_map.get(segs[1][2:])
            # host_ip = segs[1][2:]
            logger.debug("single host, ip = {}".format(host_ip))
        elif host_type == WORKER_TYPE_SWARM:  # swarm
            host_ip = get_swarm_node_ip(worker_api, "{}_{}".format(
                cluster_id, node))
            logger.debug("swarm host, ip = {}".format(host_ip))
        elif host_type == WORKER_TYPE_VSPHERE:
            host_ip = host.vcparam[utils.VMIP]
            logger.debug(" host, ip = {}".format(host_ip))
        else:
            logger.error("Unknown host type = {}".format(host_type))
            host_ip = ""
        return host_ip

    def find_free_start_ports(self, host_id, number):
        """ Find the first available port for a new cluster api

        This is NOT lock-free. Should keep simple, fast and safe!

        Check existing cluster records in the host, find available one.

        :param host_id: id of the host
        :param number: Number of ports to get
        :return: The port list, e.g., [7050, 7150, ...]
        """
        logger.debug("Find {} start ports for host {}".format(number, host_id))
        if number <= 0:
            logger.warning("number {} <= 0".format(number))
            return []
        host = self.host_handler.get_by_id(host_id)
        if not host:
            logger.warning("Cannot find host with id={}", host_id)
            return ""
        ports_used = []

        clusters_exists = ClusterModel.objects(host=host)
        for cluster in clusters_exists:
            ports_used.extend(cluster.ports)

        logger.debug("The ports existed: {}".format(ports_used))
        if len(ports_used) + number >= 1000:
            logger.warning("Too much ports are already in used.")
            return []
        candidates = [CLUSTER_PORT_START + i * CLUSTER_PORT_STEP
                      for i in range(len(ports_used) + number)]

        result = list(filter(lambda x: x not in ports_used, candidates))

        logger.debug("Free ports are {}".format(result[:number]))
        return result[:number]

    def refresh_health(self, cluster_id, timeout=5):
        """
        Check if the peer is healthy by counting its neighbour number
        :param cluster_id: id of the cluster
        :param timeout: how many seconds to wait for receiving response
        :return: True or False
        """
        cluster = self.get_by_id(cluster_id)
        cluster_id = cluster_id
        logger.debug("Cluster ID: {}".format(cluster_id))
        logger.debug("checking health of cluster={}".format(cluster))
        if not cluster:
            logger.warning("Cannot found cluster id={}".format(cluster_id))
            return True
        if cluster.get("status") != "running":
            logger.warning("cluster is not running id={}".format(cluster_id))
            return True
        if cluster.get("network_type") == NETWORK_TYPE_FABRIC_PRE_V1:
            rest_api = cluster["service_url"]["rest"] + "/network/peers"
            if not rest_api.startswith("http"):
                rest_api = "http://" + rest_api
            logger.debug("rest_api={}".format(rest_api))
            logger.debug("---In Network type Fabric V 0.6---")
            try:
                r = requests.get(rest_api, timeout=timeout)
            except Exception as e:
                logger.error("Error to refresh health of cluster {}: {}".
                             format(cluster_id, e))
                return True

            peers = r.json().get("peers")
            logger.debug("peers from rest_api: {}".format(peers))

            if len(peers) == cluster["size"]:
                self.db_update_one({"id": cluster_id},
                                   {"health": "OK"})
                return True
            else:
                logger.debug("checking result of cluster id={}".format(
                    cluster_id, peers))
                self.db_update_one({"id": cluster_id},
                                   {"health": "FAIL"})
                return False
        elif "fabric-1" in cluster.get('network_type'):
            service_url = cluster.get("service_url", {})
            health_ok = False
            i = 0
            while i <= 5:
                for url in service_url.values():
                    ip = url.split(":")[0]
                    port = int(url.split(":")[1])
                    socket.setdefaulttimeout(1)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    logger.debug("check {}:{} result {}".format(ip, port, result))
                    if result != 0:
                        health_ok = False
                        break
                    else:
                        health_ok = True
                if health_ok:
                    break
                else:
                    i += 1
                    time.sleep(1)

            if not health_ok:
                self.db_update_one({"id": cluster_id},
                                   {"health": "FAIL"})
                return False
            else:
                self.db_update_one({"id": cluster_id},
                                   {"health": "OK"})
                return True
        return True

    def db_update_one(self, filter, operations, after=True, col="active"):
        """
        Update the data into the active db

        :param filter: Which instance to update, e.g., {"id": "xxx"}
        :param operations: data to update to db, e.g., {"$set": {}}
        :param after: return AFTER or BEFORE
        :param col: collection to operate on
        :return: The updated host json dict
        """
        state = CLUSTER_STATE.active.name if col == "active" \
            else CLUSTER_STATE.released.name
        filter.update({
            "state": state
        })
        logger.info("filter {} operations {}".format(filter, operations))
        kwargs = dict(('set__' + k, v) for (k, v) in operations.items())
        for k, v in kwargs.items():
            logger.info("k={}, v={}".format(k, v))
        try:
            ClusterModel.objects(id=filter.get("id")).update(
                upsert=True,
                **kwargs
            )
            doc = ClusterModel.objects.get(id=filter.get("id"))
        except Exception as exc:
            logger.info("exception {}".format(exc))
            return None
        return doc

    def _schema(self, doc, many=False):
        cluster_schema = ClusterSchema(many=many)
        return cluster_schema.dump(doc).data


cluster_handler = ClusterHandler()

if __name__ == '__main__':
    cluster_handler._create_cluster()
