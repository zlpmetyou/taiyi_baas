# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import os

CLUSTER_NETWORK = "cello_net"

# go后端api
GO_HOST = 'http://120.27.20.114:9000'
# GO_HOST = 'https://120.27.22.25:9000'
FABRIC_TOKEN_API_PATH = GO_HOST + '/baasServer/getToken'
FABRIC_SEND_CLUSTER_CONFIG_PATH = GO_HOST + '/baasServer/blockchainManager/modifyBlockChainConfig'
DELETE_BLOCK_CHAIN_API_PATH = GO_HOST + '/baasServer/blockchainManager/deleteBlockChainConfig'
ADD_USER_API = GO_HOST + '/baasServer/userManager/registerUser'
USER_ACCOUNT = {"UserId": "from_python", "Passwd": "123456"}

# 云片配置
API_KEY = '77d482b5060dc4bf56bc16b2ce2b6752'
TEMPLATE_ID = '2558770'

# The probation period of block chain(days)
BLOCK_CHAIN_PROBATION_PERIOD = 7

# the block chain config files path
# BLOCKCHAIN_CONFIG_FILES_PATH = '/app/config_files'
# MAP_PATH = '/opt/cello/baas_test/config_files'
BLOCKCHAIN_CONFIG_FILES_PATH = '/app/agent/docker/_compose_files'
# MAP_PATH = '/opt/cello/'
MAP_PATH = '/opt/cello/baas_test/agent/docker/_compose_files/'

# tools
CRYPTO_GEN_TOOL = '/app/config_files/cryptogen'
CONFIG_TX_GEN_TOOL = '/app/config_files/configtxgen'

# inside and outside network ip mappings
IP_MAPPINGS = {
    '120.27.20.114': '172.31.239.245',
    '47.105.86.107': '172.31.239.247',
    '47.105.161.225': '172.31.239.248',
    '47.105.64.58': '172.31.239.249',
    '47.105.164.116': '172.31.239.250',
    '47.105.163.14': '172.31.239.251'
}

# images
FABRIC_IMAGES_MAPPING = {
    'fabric-1.1': {
        'fabric_image': '1.1.0',
        'ca_image': 'hyperledger/fabric-ca:1.1.0',
        'peer_image': 'foodchainbaas/fabric-peer:chainfood-1.1',
        'orderer_image': 'hyperledger/fabric-orderer:1.1.0',
        'cli_image': 'foodchainbaas/fabric-tools:chainfood-1.1',
        'kafka_image': 'hyperledger/fabric-kafka:1.1.0',
        'zookeeper_image': 'hyperledger/fabric-zookeeper:1.1.0'
    },
    # 'fabric-1.2': {},  # TODO
    # 'fabric-1.0': {},  # TODO
}

CA_CONTAINER = {
    "{}": {
        'image': 'a'
    }
}
NETWORK_SIZE_FABRIC_PRE_V1 = [4, 6]
NETWORK_SIZE_FABRIC_V1 = [1, 2, 3, 4]
ORG_SIZE = 2

# first port that can be assigned as cluster API
CLUSTER_PORT_START = int(os.getenv("CLUSTER_PORT_START", 7050))
# number of port allocated to each cluster in case collision
CLUSTER_PORT_STEP = 10

# Fabric image related varible
# should be the same with scripts/worker_node/download_images.sh
HLF_VERSION = '1.0.5'
HLF_VERSION_1_1 = '1.1.0'
HLF_VERSION_1_2 = '1.2.0'

# vSphere requires this
ARCH = 'x86_64'
VERSION = '1.0.5'
BASEIMAGE_RELEASE = '0.3.2'
FABRIC_IMAGE_FULL = 'hyperledger/fabric-{}:{}-{}'
FABRIC_IMAGE_TAG = 'hyperledger/fabric-{}:{}'
FABRIC_IMAGE = 'hyperledger/fabric-{}'
FABRIC_IMAGES = ['peer', 'tools', 'orderer', 'ca', 'ccenv', 'kafka',
                 'zookeeper']
FABRIC_BASE_IMAGES = ['baseimage', 'baseos']

# explorer images
BLOCKCHAIN_EXPLORER_IMAGE = 'yeasy/blockchain-explorer'
BLOCKCHAIN_EXPLORER_TAG = '0.1.0-preview'

MYSQL_IMAGE = 'mysql'
MYSQL_TAG = '5.7'

# host status
HOST_STATUS = 'status'
HOST_STATUS_ACTIVE = 'active'
HOST_STATUS_PENDING = 'pending'



PEER_SERVICE_PORTS = {
    'rest': 7050,  # this is the reference starter for cluster port step
    'grpc': 7051,
    'cli': 7052,
    'event': 7053,
}

CA_SERVICE_PORTS = {
    'ecap': 7054,
    'ecaa': 7055,
    'tcap': 7056,
    'tcaa': 7057,
    'tlscap': 7058,
    'tlscaa': 7059,
}

ORDERER_SERVICE_PORTS = {
    'orderer': 7050
}

EXPLORER_PORTS = {
    'explorer': 8080
}

SERVICE_PORTS = dict(list(PEER_SERVICE_PORTS.items()) +
                     list(CA_SERVICE_PORTS.items()))

NETWORK_TYPE_FABRIC_PRE_V1 = 'fabric-0.6'  # TODO: deprecate 0.6 support soon
NETWORK_TYPE_FABRIC_V1 = 'fabric-1.0'
NETWORK_TYPE_FABRIC_V1_1 = 'fabric-1.1'
NETWORK_TYPE_FABRIC_V1_2 = 'fabric-1.2'
NETWORK_TYPES = [NETWORK_TYPE_FABRIC_V1, NETWORK_TYPE_FABRIC_V1_1, NETWORK_TYPE_FABRIC_V1_2]
# only support fabric v1.x now

CLUSTER_SIZE = 4

CONSENSUS_PLUGIN_NOOPS = 'noops'
CONSENSUS_PLUGIN_PBFT = 'pbft'
CONSENSUS_PLUGIN_SOLO = 'solo'
CONSENSUS_PLUGIN_KAFKA = 'kafka'

CONSENSUS_PLUGINS_FABRIC_V1 = [CONSENSUS_PLUGIN_SOLO, CONSENSUS_PLUGIN_KAFKA]
CONSENSUS_PLUGINS_FABRIC_PRE_V1 = [CONSENSUS_PLUGIN_NOOPS,
                                   CONSENSUS_PLUGIN_PBFT]
CONSENSUS_MODES_FABRIC_V1 = ['', '']

# CONSENSUS_MODES = ['classic', 'batch', 'sieve']  # pbft has various modes
CONSENSUS_MODE_BATCH = 'batch'
CONSENSUS_MODES = [CONSENSUS_MODE_BATCH]  # pbft has various modes

CONSENSUS_TYPES_FABRIC_PRE_V1 = [
    (CONSENSUS_PLUGIN_NOOPS, ''),
    (CONSENSUS_PLUGIN_PBFT, CONSENSUS_MODE_BATCH),
]

CONSENSUS_TYPES_FABRIC_V1 = [
    (CONSENSUS_PLUGIN_SOLO, ''),
    (CONSENSUS_PLUGIN_KAFKA, '')
]

WORKER_TYPE_DOCKER = 'docker'
WORKER_TYPE_SWARM = 'swarm'
WORKER_TYPE_K8S = 'kubernetes'
WORKER_TYPE_VSPHERE = 'vsphere'
WORKER_TYPES = [WORKER_TYPE_DOCKER, WORKER_TYPE_SWARM, WORKER_TYPE_K8S,
                WORKER_TYPE_VSPHERE]

# TODO: might deprecate as can use agent to collect log seperately
CLUSTER_LOG_TYPES = ['local']  # TODO: we may remove this option
CLUSTER_LOG_LEVEL = ['DEBUG', 'INFO', 'NOTICE', 'WARNING', 'ERROR',
                     'CRITICAL']

NETWORK_STATUS_CREATING = 'creating'  # just in-creation
NETWORK_STATUS_RUNNING = 'running'  # running now, waiting for health check
NETWORK_STATUS_DELETING = 'deleting'  # network is in deleting
NETWORK_STATUS_STOPPED = 'stopped'  # network is stopped

K8S_CRED_TYPE = {
    'account': '0',
    'cert': '1',
    'config': '2'
}

# Vcenter and VirtualMachine Confs
VIRTUAL_MACHINE = 'vm'
VCENTER = 'vc'
VMUUID = 'vm_uuid'
VM_DEFAULT_HOSTNAME = "Cello"
VMMEMORY = 'memory'
VMCPU = 'vcpus'
VMNAME = 'vmname'
VMIP = 'ip'
VMNETMASK = 'netmask'
VMDNS = 'dns'
VMGATEWAY = 'gateway'
TEMPLATE = 'template'
VC_DATACENTER = 'vc_datacenter'
VC_CLUSTER = 'vc_cluster'
VC_DATASTORE = 'vc_datastore'
NETWORK = 'network'
NIC_DEVICE_ADDRESS_TYPE = 'assigned'
VCIP = 'address'
VCUSERNAME = 'username'
VCPWD = 'password'
VCPORT = 'port'
VC_DEFAULT_PORT = 443
VCTHREAD_NAME = "setupvm"
WORKER_API_PORT = 2375
DEFAULT_TIMEOUT = 300


def json_decode(jsonstr):
    try:
        json_object = json.loads(jsonstr)
    except json.decoder.JSONDecodeError as e:
        print(e)
        return jsonstr
    return json_object


def request_debug(request, logger):
    logger.debug("path={}, method={}".format(request.path, request.method))
    logger.debug("request args:")
    for k in request.args:
        logger.debug("Arg: {0}:{1}".format(k, request.args[k]))
    logger.debug("request form:")
    for k in request.form:
        logger.debug("Form: {0}:{1}".format(k, request.form[k]))
    logger.debug("request raw body data:")
    logger.debug(request.data)
    logger.debug(request.get_json(force=True, silent=True))


def request_get(request, key, default_value=None):
    if key in request.args:
        return request.args.get(key)
    elif key in request.form:
        return request.form.get(key)
    try:
        json_body = request.get_json(force=True, silent=True)
        if key in json_body:
            return json_body[key]
        else:
            return default_value
    except Exception:
        return default_value


def request_json_body(request, default_value={}):
    try:
        json_body = request.get_json(force=True, silent=True)
        return json_body
    except Exception:
        return default_value
