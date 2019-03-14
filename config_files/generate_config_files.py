import os
import logging
import shutil
import sys

import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common import log_handler, LOG_LEVEL, BLOCKCHAIN_CONFIG_FILES_PATH, CRYPTO_GEN_TOOL, CONFIG_TX_GEN_TOOL
from modules.models.host import Channel as ChannelModel
from modules.models.host import Org as OrgModel
from modules.models.host import Node

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

fabric_images_maps = {
    'fabric-1.1': {
        'fabric_image': '1.1.0',
        'ca_image': 'hyperledger/fabric-ca:1.1.0',
        'peer_image': 'foodchainbaas/fabric-peer:chainfood-1.1',
        'orderer_image': 'hyperledger/fabric-orderer:1.1.0',
        'cli_image': 'foodchainbaas/fabric-tools:1.1.0',
        'kafka_image': 'hyperledger/fabric-kafka:1.1.0',
        'zookeeper_image': 'hyperledger/fabric-zookeeper:1.1.0'
    },
    # 'fabric-1.2': {},  # TODO
    # 'fabric-1.0': {},  # TODO
}


def generate_yaml_file(config, file_name, target_path):
    logger.info('create {} output into {}'.format(file_name, target_path))
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    target_file = os.path.join(target_path, file_name)
    with open(target_file, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    if os.path.exists(file_name):
        logger.info('create {} success'.format(file_name))
        return True
    else:
        logger.info('create {} failed'.format(file_name))

        return False


def group_crypto_org_config(org_name, domain, users, peers, ca):
    content = {
        "Users": {"Count": users},
        "Name": org_name.capitalize(),
        "Domain": "{}.{}".format(org_name, domain),
        "Specs": [
            {
                "Hostname": peer
            }
            for peer in peers
        ],
        "CA":
            {
                "Hostname": ca
            }
    }
    return content


def group_tx_org_config(org_name, domain, peer_name):
    content = {
        "AnchorPeers": [
            {
                "Port": 7051,
                "Host": "{}.{}.{}".format(peer_name, org_name, domain)
            }
        ],
        "Name": "{}MSP".format(org_name.capitalize()),
        "MSPDir": "crypto-config/peerOrganizations/{}.{}/msp".format(org_name, domain),
        "ID": "{}MSP".format(org_name.capitalize())
    }
    return content


# def group_tx_org_config

class GenerateClusterFiles(object):

    def __init__(self):
        # self.tool_path = tool_path if tool_path else os.path.dirname(__file__)
        self.crypto_tool = CRYPTO_GEN_TOOL
        self.channel_tx_tool = CONFIG_TX_GEN_TOOL

    def generate_crypto_file(self, config_file):
        if os.path.exists('crypto-config'):
            shutil.rmtree('crypto-config')
        result = os.system(self.crypto_tool + ' generate --config={}'.format(config_file))
        if result == 0:
            logger.info('create crypto-config-dir with crypto-config.yaml success')
            return True
        else:
            logger.info('create crypto-config-dir with crypto-config.yaml failed')
            return False

    def generate_tx_file(self, channel_name):
        result = os.system(self.channel_tx_tool +
                           ' -profile {} -outputCreateChannelTx ./channel-artifacts/{}.tx -channelID {}'
                           .format(channel_name, channel_name, channel_name))
        if result == 0:
            logger.info('create {}_tx with configtx.yaml success'.format(channel_name))
            return True
        else:
            logger.info('create {}_tx with configtx.yaml failed'.format(channel_name))
            return False

    def generate_new_org_json_file(self, org_name):
        # name is the msp name of new org
        org_msp_name = '{}MSP'.format(org_name.capitalize())
        result = os.system(self.channel_tx_tool +
                           ' -printOrg {} -profile ./configtx.yaml > channel-artifacts/{}.json'
                           .format(org_msp_name, org_name))
        if result == 0:
            logger.info('create {}.json with configtx.yaml success'.format(org_name))
            return True
        else:
            logger.info('create {}.json with configtx.yaml failed'.format(org_name))
            return False


class TxOrg:
    def __init__(self, name, domain, id=None, msp_dir=None, anchor_peers=None):
        self.name = '{}MSP'.format(name)
        self.id = id if id else '{}MSP'.format(name)
        self.msp_dir = msp_dir if msp_dir else "crypto-config/peerOrganizations/{}.{}/msp".format(name, domain)
        self.anchor_peers = anchor_peers

    def group_config(self):
        content = {
            "AnchorPeers": self.anchor_peers,
            "Name": self.name,
            "MSPDir": self.msp_dir,
            "ID": self.id
        }
        return content


class TxOrderer:
    def __init__(self, orderer_type, addresses, kafka):
        self.orderer_type = orderer_type
        self.addresses = addresses
        self.batch_time = '2s'
        self.batch_size = {
                "MaxMessageCount": 10,
                "AbsoluteMaxBytes": "98 MB",
                "PreferredMaxBytes": "512 KB"
            }
        self.kafka = kafka

    def group_config(self):
        content = {
            "OrdererType": self.orderer_type,
            "BatchTimeout": self.batch_time,
            "BatchSize": self.batch_size,
            "Organizations": None
        }
        if self.kafka:
            content.update({'Kafka': self.kafka})
        return content


# class TxProfile:
#     def __init__(self, orderer_org, channels):
#         self.orderer_org = orderer_org
#         self.channels = channels
#
#     def group_config(self):
#

# class GenerateTxConfig(object):
#
#     def group_org_config(self,):
#         content = {
#             "AnchorPeers": [
#                 {
#                     "Port": 7051,
#                     "Host": "{}.{}.{}".format(peer_name, org_name, domain)
#                 }
#             ],
#             "Name": "{}MSP".format(org_name.capitalize()),
#             "MSPDir": "crypto-config/peerOrganizations/{}.{}/msp".format(org_name, domain),
#             "ID": "{}MSP".format(org_name.capitalize())
#         }
class ContainerService(dict):

    def __init__(self, image, container_name, environment, **kwargs):
        self.image = image
        self.container_name = container_name
        self.environment = environment
        # self.ports = ports
        # self.volumes = volumes
        # self.command = command
        # self.working_dir = working_dir
        # self.restart = restart
        # self.depends_on = depends_on
        # self.links = links
        # self.external_links = external_links
        # self.tty = tty
        # self.hostname = hostname

        for k, v in kwargs.items():
            setattr(self, k, v)
        super(ContainerService, self).__init__()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, name, value):
        self[name] = value

    def get_data(self):
        """
        Get the configuration data for the block chain network
        Returns: data dict
        """
        return dict(self)


class GenerateChainBlockConfig(object):

    def __init__(self, cluster, config_file_path, base_path=os.path.dirname(__file__)):

        self.cluster = cluster
        self.consensus_plugin = cluster.consensus_plugin
        self.cluster_id = str(cluster.id)
        self.mapped_ports = cluster.mapped_ports
        self.service_url = cluster.service_url
        self.network_type = cluster.network_type
        self.network = '{}_default'.format(str(cluster.id))

        self.base_path = base_path
        self.target_dir = os.path.join(config_file_path, self.cluster_id)

        self.crypto_tool = os.path.join(self.base_path, 'cryptogen')
        self.channel_tx_tool = os.path.join(self.base_path, 'configtxgen')

        self.images = fabric_images_maps.get(self.network_type)

    def generate_chaincode_config(self):

        all_orgs = []
        orderer_orgs = OrgModel.objects(cluster=self.cluster, org_type='orderer')
        for orderer_org in orderer_orgs:
            org_id = str(orderer_org.id)
            name = orderer_org.name
            alias = orderer_org.alias
            domain = orderer_org.domain
            orderers = Node.objects(org=orderer_org, node_type='orderer')
            orderer_org_info = {
                'OrgId': org_id,
                "Name": name,
                "Type": "orderer",
                "Domain": domain,
                "MspId": "{}MSP".format(alias.capitalize()),
                "Orderers": [
                    {
                        "Name": str(orderer.alias),
                        "Url": '{}:{}'.format(orderer.ip, orderer.ports['orderer'])
                    }
                    for orderer in orderers
                ]
            }

            all_orgs.append(orderer_org_info)

        peer_orgs = {}
        peer_orgs_list = OrgModel.objects(cluster=self.cluster, org_type='peer')
        for peer_org in peer_orgs_list:
            org_id = str(peer_org.id)
            name = peer_org.name
            alias = peer_org.alias
            domain = peer_org.domain
            peers = Node.objects(org=peer_org, node_type='peer')
            cas = Node.objects(org=peer_org, node_type='ca')
            peer_org_info = {
                'OrgId': org_id,
                "Name": name,
                "Type": "peer",
                "Domain": domain,
                "MspId": "{}MSP".format(alias.capitalize()),
                "Peers": [
                    {
                        "Name": str(peer.id),
                        "Url": '{}:{}'.format(peer.ip, peer.ports['grpc']),
                        "EventUrl": '{}:{}'.format(peer.ip, peer.ports['event'])
                    }
                    for peer in peers
                ],
                'Cas': [
                    {
                        "Name": ca.alias,
                        "Url": '{}:{}'.format(ca.ip, ca.ports['ecap']),
                        "EnrollId": "admin",
                        "EnrollSecret": "adminpw",
                        "ContainerName": "{}_peer{}".format(str(ca.alias), alias.capitalize())
                    }
                    for ca in cas
                ]
            }
            all_orgs.append(peer_org_info)
            peer_orgs.update({name: {'domain': domain, 'peers': peers}})

        channels = []
        channels_list = ChannelModel.objects(cluster=self.cluster)
        for channel in channels_list:
            channel_id = str(channel.id)
            name = channel.name
            alias = channel.alias
            orderers = channel.orderers
            orgs = channel.orgs
            channel_info = {
                "ChannelId": channel_id,
                'ChannelName': name,
                "ChannelConfigName": "{}.tx".format(alias),
                "Orderers": [
                    # str(orderer.id)
                    orderer.alias
                    for orderer in orderers
                ]
            }
            channel_org_peers = []
            for org in orgs:
                channel_org_peers.append({
                    "OrgId": org.alias,
                    "Peers": [
                        '{}.{}.{}'.format(peer.alias, org.alias, org.domain)
                        for peer in Node.objects(org=org, node_type='peer')
                    ]
                })
            channel_info.update({"Orgs": channel_org_peers})
            channels.append(channel_info)

        cluster_info = {
            "ChannelId": channels_list[0].alias,
            # "ChannelId": str(channels_list[0].id),
            "BlockchainSign": self.cluster_id,
            "BlockchainName": self.cluster.name,
            "Algorithm": self.consensus_plugin,
            "CreateTime": self.cluster.create_ts.strftime("%Y%m%d%H%M%S"),
            "BlockChainCertPath": "zz",
            'TlsEnable': False,
            "Channels": channels
        }

        cluster_info.update({'Orgs': all_orgs})
        return cluster_info

    def group_cryptogen_orderer_orgs(self):

        orderer_org_list = []
        orderer_orgs = OrgModel.objects(cluster=self.cluster, org_type='orderer')
        for orderer_org in orderer_orgs:
            org_id = str(orderer_org.id)
            alias = orderer_org.alias
            domain = orderer_org.domain
            orderers = Node.objects(org=orderer_org, node_type='orderer')
            orderer_org_info = {
                "Name": alias.capitalize(),
                "Domain": domain,
                "Specs": [
                    {
                        "Hostname": orderer.alias
                    }
                    for orderer in orderers
                ]
            }
            orderer_org_list.append(orderer_org_info)

        return orderer_org_list

    def group_cryptogen_peer_orgs(self):

        peer_org_list = []
        peer_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer')
        for peer_org in peer_orgs:
            org_id = str(peer_org.id)
            alias = peer_org.alias
            domain = peer_org.domain
            ca = Node.objects.get(org=peer_org, node_type='ca')
            peers = Node.objects(org=peer_org, node_type='peer')
            peer_org_info = {
                "Users": {"Count": 1},
                "Name": alias.capitalize(),
                "Domain": "{}.{}".format(alias, domain),
                "Specs": [
                    {
                        "Hostname": peer.alias
                    }
                    for peer in peers
                ],
                "CA":
                    {
                        "Hostname": ca.alias
                    }
            }
            peer_org_list.append(peer_org_info)

        return peer_org_list

    def group_cryptogen(self):

        orderer_orgs = self.group_cryptogen_orderer_orgs()
        peer_orgs = self.group_cryptogen_peer_orgs()

        crypto_config = {"OrdererOrgs": orderer_orgs, "PeerOrgs": peer_orgs}
        return crypto_config

    def group_configtx_orderer_org(self):
        orderer_org_list = []
        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        org_id = str(orderer_org.id)
        alias = orderer_org.alias
        domain = orderer_org.domain
        orderer_org_info = {
            "Name": '{}MSP'.format(alias.capitalize()),  # maybe OrdererOrg
            "MSPDir": "crypto-config/ordererOrganizations/{}/msp".format(domain),
            "ID": "{}MSP".format(alias.capitalize())
        }
        orderer_org_list.append(orderer_org_info)
        return orderer_org_list

    @staticmethod
    def group_peer_org_config(org):
        org_id = str(org.id)
        alias = org.alias
        domain = org.domain
        peer = Node.objects.get(org=org, name='peer0')
        peer_org_info = {
            "AnchorPeers": [
                {
                    "Port": 7051,
                    "Host": "{}.{}.{}".format(peer.alias, alias, domain)
                }
            ],
            "Name": "{}MSP".format(alias.capitalize()),
            "MSPDir": "crypto-config/peerOrganizations/{}.{}/msp".format(alias, domain),
            "ID": "{}MSP".format(alias.capitalize())
        }
        content = {alias: peer_org_info}

        return content

    def group_configtx_peer_org(self):

        peer_org_dict = {}
        peer_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer')
        for peer_org in peer_orgs:
            peer_org_info = self.group_peer_org_config(peer_org)
            peer_org_dict.update(peer_org_info)

        return peer_org_dict

    @staticmethod
    def unit_to_word(u):
        convert_table = {
            1: "One",
            2: "Two",
            3: "Three",
            4: "Four",
            5: "Five",
            6: "Six",
            7: "Seven",
            8: "Eight",
            9: "Nine",
        }
        return convert_table[u]

    def generate_orderer_node_config(self):

        orderer_type = self.cluster.consensus_plugin
        orderer_node_config = {
            "OrdererType": orderer_type,
            "BatchTimeout": "2s",
            "BatchSize": {
                "MaxMessageCount": 10,
                "AbsoluteMaxBytes": "98 MB",
                "PreferredMaxBytes": "512 KB"
            },
            "Organizations": None
        }
        orderers_address = []
        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        orderers = Node.objects(org=orderer_org, node_type='orderer')
        for orderer in orderers:
            orderer_address = '{}.{}:7050'.format(orderer.alias, orderer_org.alias)
            orderers_address.append(orderer_address)

        orderer_node_config.update({'Addresses': orderers_address})
        if orderer_type == 'kafka':
            kafka_config = {
                'Brokers': [
                    'kafka0:9092',
                    'kafka1:9092',
                    'kafka2:9092',
                    'kafka3:9092'
                ]
            }
            orderer_node_config.update({'Kafka': kafka_config})
        return orderer_node_config

    def group_orderer_genesis_profile(self, orderer_default, orderer_orgs, peer_orgs, capabilities):

        orderer_default_config = dict(**orderer_default)
        orderer_default_config['Organizations'] = orderer_orgs
        orderer_default_config['Capabilities'] = capabilities.get('Orderer')
        orderer_system_config = {
            'Orderer': orderer_default_config,
            "Consortiums": {
                "SampleConsortium": {
                    "Organizations": list(peer_orgs.values())
                }
            },
            'Capabilities': capabilities.get('Global')
        }

        return orderer_system_config

    def group_org_channel_profile(self, peer_orgs, capabilities):

        content = {
            "Consortium": "SampleConsortium",
            "Application": {
                "Organizations": peer_orgs,
                "Resources": {
                    "DefaultModPolicy": "/Channel/Application/Writers"
                },
                "Capabilities": capabilities.get('Application')
            }
        }
        return content

    def group_configtx(self):

        tx_content = {}
        orderer = self.generate_orderer_node_config()
        tx_content.update({'Orderer': orderer})

        orderer_orgs = self.group_configtx_orderer_org()
        peer_orgs = self.group_configtx_peer_org()
        organizations = []
        for orderer_org in orderer_orgs:
            organizations.append(orderer_org)
        for peer_org in peer_orgs.values():
            organizations.append(peer_org)

        tx_content.update({'Organizations': organizations})

        capabilities = {
            'Application': {'V1_1': False},
            'Global': {'V1_1': True},
            'Orderer': {'V1_1': True}
        }
        tx_content.update({'Capabilities': capabilities})

        applications = {'Organizations': None}
        tx_content.update({'Application': applications})

        profiles = {}
        profile_orderer_content = self.group_orderer_genesis_profile(orderer, orderer_orgs, peer_orgs, capabilities)
        profiles.update({'OrdererGenesis': profile_orderer_content})

        channels = ChannelModel.objects(cluster=self.cluster)
        for channel in channels:
            name = str(channel.id)
            channel_alias = channel.alias
            channel_orgs = channel.orgs
            channel_orgs_info = []
            for org in channel_orgs:
                org_info = peer_orgs[org.alias]
                channel_orgs_info.append(org_info)
            channel_info = self.group_org_channel_profile(channel_orgs_info, capabilities)
            profiles.update({channel_alias: channel_info})
        tx_content.update({'Profiles': profiles})
        return tx_content

    @staticmethod
    def generate_yaml_file(config, file_name):
        logger.info('create {} '.format(file_name))
        with open(file_name, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)
        if os.path.exists(file_name):
            logger.info('create {} success'.format(file_name))
            return True
        else:
            logger.info('create {} failed'.format(file_name))

            return False

    def generate_crypto_config(self):
        crypto_config = self.group_cryptogen()
        result = self.generate_yaml_file(crypto_config, 'crypto-config.yaml')
        if result:
            logger.info('create {} success'.format('crypto-config.yaml'))
        else:
            logger.info('create {} failed'.format('crypto-config.yaml'))

    def generate_channel_config(self):
        channel_tx_config = self.group_configtx()
        result = self.generate_yaml_file(channel_tx_config, 'configtx.yaml')
        if result:
            logger.info('create {} success'.format('configtx.yaml'))
        else:
            logger.info('create {} failed'.format('configtx.yaml'))

    def generate_crypto_dir(self):
        if os.path.exists('crypto-config'):
            shutil.rmtree('crypto-config')
        result = os.system(self.crypto_tool + ' generate --config=crypto-config.yaml')
        if result == 0:
            logger.info('create crypto-config-dir with crypto-config.yaml success')
            return True
        else:
            logger.info('create crypto-config-dir with crypto-config.yaml failed')

            return False

    def generate_genesis_block(self):

        logger.info('path:' + os.getcwd())

        profile_name = 'OrdererGenesis'
        commond = self.channel_tx_tool + ' -profile ' + profile_name + \
                  ' --outputBlock ./channel-artifacts/orderer.genesis.block'
        logger.info('commond:' + commond)
        result = os.system(commond)

        if result == 0:
            logger.info('create genesis_block with configtx.yaml success')
            return True
        else:
            logger.info('create genesis_block with configtx.yaml failed')
            return False

    def generate_channel_tx(self):

        channels = ChannelModel.objects(cluster=self.cluster)
        for channel in channels:
            name = channel.alias
            result = os.system(self.channel_tx_tool +
                               ' -profile {} -outputCreateChannelTx ./channel-artifacts/{}.tx -channelID {}'
                               .format(name, name, name))
            if result == 0:
                logger.info('create {}_tx with configtx.yaml success'.format(name))
                return True
            else:
                logger.info('create {}_tx with configtx.yaml failed'.format(name))
                return False

    def generate_ca_service(self, org):

        # org_id = str(org.id)
        org_name = org.alias
        domain = org.domain
        ca = Node.objects.get(org=org, node_type='ca')
        ca_org_services = {}
        ca_name = ca.alias
        service_name = '{}.{}.{}'.format(ca_name, org_name, domain)
        image = self.images.get('ca_image')
        key_file = "./crypto-config/peerOrganizations/" + org_name + "." + domain + "/ca"
        key_name = ''
        for i in os.listdir(key_file):
            if i.endswith('_sk'):
                key_name = i
                break
        container_name = '{}_{}_{}'.format(self.cluster_id, ca_name, org_name)
        command = "sh -c 'fabric-ca-server start -b admin:adminpw -d'"
        ports = [
            '{}:7054'.format(ca.ports.get('ecap'))
        ]
        environment = [
            "FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server",
            "FABRIC_CA_SERVER_CA_NAME=ca_peer" + org_name.capitalize(),
            "FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/{}.{}.{}-cert.pem"
                .format(ca_name, org_name, domain),
            "FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/{}".format(key_name),
            "FABRIC_CA_SERVER_TLS_ENABLED=false",
            "FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/{}.{}.{}-cert.pem"
                .format(ca_name, org_name, domain),
            "FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/{}".format(key_name)
        ]
        volumes = [
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config/peerOrganizations/" + org_name + "." + domain
            + "/ca/:/etc/hyperledger/fabric-ca-server-config"
        ]
        service = {
            service_name:
                ContainerService(
                    image=image,
                    container_name=container_name,
                    command=command,
                    ports=ports,
                    environment=environment,
                    volumes=volumes
                ).get_data()
        }
        ca_org_services.update(service)

        return ca_org_services

    def generate_orderer_service(self, orderer, org, domain):

        # orderer_id = str(orderer.id)
        orderer_name = orderer.alias
        org_name = org.alias
        service_name = '{}.{}'.format(orderer_name, domain)
        image = self.images.get('orderer_image')
        container_name = '{}_{}_{}'.format(self.cluster_id, orderer_name, org_name)
        command = "orderer"
        ports = ["{}:7050".format(orderer.ports.get('orderer'))]
        environment = [
            "ORDERER_GENERAL_LOGLEVEL=DEBUG",
            "ORDERER_GENERAL_LISTENADDRESS=0.0.0.0",
            "ORDERER_GENERAL_GENESISMETHOD=file",
            "ORDERER_GENERAL_GENESISFILE=/var/hyperledger/orderer/orderer.genesis.block",
            "ORDERER_GENERAL_LOCALMSPID={}MSP".format(org_name.capitalize()),
            "ORDERER_GENERAL_LOCALMSPDIR=/var/hyperledger/orderer/msp",
            "ORDERER_GENERAL_TLS_ENABLED=false",
            "ORDERER_GENERAL_TLS_PRIVATEKEY=/var/hyperledger/orderer/tls/server.key",
            "ORDERER_GENERAL_TLS_CERTIFICATE=/var/hyperledger/orderer/tls/server.crt",
            "ORDERER_GENERAL_TLS_ROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]",
        ]
        volumes = [
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/channel-artifacts/orderer.genesis.block:"
                                                           "/var/hyperledger/orderer/orderer.genesis.block",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config/ordererOrganizations/" + domain +
            "/orderers/" + '{}.{}'.format(orderer_name, domain) + "/msp:/var/hyperledger/orderer/msp",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config/ordererOrganizations/" + domain +
            "/orderers/" + '{}.{}'.format(orderer_name, domain) + "/tls/:/var/hyperledger/orderer/tls"
        ]
        restart = 'always'
        depends_on = []
        if self.cluster.consensus_plugin == 'kafka':
            depends_on = [
                'zookeeper0',
                'zookeeper1',
                'zookeeper2',
                'kafka0',
                'kafka1',
                'kafka2',
                'kafka3',
            ]

        external_links = []
        return {
            service_name:
                ContainerService(
                    image=image,
                    container_name=container_name,
                    command=command,
                    ports=ports,
                    environment=environment,
                    volumes=volumes,
                    restart=restart,
                    external_links=external_links,
                    depends_on=depends_on
                ).get_data()
        }

    def generate_peer_org_service(self, org, orderer_services):

        peer_org_services = {}
        # org_id = str(org.id)
        org_name = org.alias
        peers = Node.objects(org=org, node_type='peer')
        domain = org.domain
        for peer in peers:
            # peer_id = str(peer.id)
            peer_name = peer.alias
            service_name = '{}.{}.{}'.format(peer_name, org_name, domain)
            image = self.images.get('peer_image')
            container_name = '{}_{}_{}'.format(self.cluster_id, peer_name, org_name)
            command = "peer node start"
            volumes = [
                "/var/run/docker.sock:/var/run/docker.sock",
                "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config/peerOrganizations/" + "{}.{}".format(
                    org_name,
                    domain) +
                "/peers/{}/msp:/etc/hyperledger/fabric/msp".format('{}.{}.{}'.format(peer_name, org_name, domain)),
                "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config/peerOrganizations/" + "{}.{}".format(
                    org_name,
                    domain) +
                "/peers/{}/tls:/etc/hyperledger/fabric/tls".format('{}.{}.{}'.format(peer_name, org_name, domain))
            ]
            working_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"
            depends_on = orderer_services
            ports = [
                "{}:7051".format(peer.ports.get('grpc')),
                "{}:7053".format(peer.ports.get('event')),
            ]
            environment = [
                # "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE={}_default".format(self.network),
                "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=cello_net",
                "CORE_LOGGING_LEVEL=DEBUG",
                "CORE_PEER_GOSSIP_USELEADERELECTION=true",
                "CORE_PEER_GOSSIP_ORGLEADER=false",
                "CORE_PEER_GOSSIP_SKIPHANDSHAKE=true",
                "CORE_PEER_TLS_ENABLED=false",
                "CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt",
                "CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key",
                "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt",
                "CORE_VM_DOCKER_HOSTCONFIG_MEMORY=268435456",
                "CORE_PEER_ID={}".format(peer_name),
                "CORE_PEER_LOCALMSPID={}MSP".format(org_name.capitalize()),
                "CORE_PEER_ADDRESS={}:7051".format(service_name)
            ]
            service = {
                service_name:
                    ContainerService(
                        image=image,
                        container_name=container_name,
                        command=command,
                        ports=ports,
                        environment=environment,
                        volumes=volumes,
                        restart='always',
                        working_dir=working_dir,
                        depends_on=depends_on
                    ).get_data()
            }
            peer_org_services.update(service)

        return peer_org_services

    def generate_cli_service(self, orderer_services, peer_org_services):

        service_name = 'cli'
        image = self.images.get('cli_image')

        container_name = "{}_cli".format(self.cluster_id)
        command = "bash -c 'sleep 5; cd /tmp && " \
                  "source scripts/func_new.sh && " \
                  "bash scripts/channel_create.sh && " \
                  "bash scripts/channel_join.sh && curl http://120.27.22.25:8083/container?id={} && " \
                  "while true; do sleep 20180101; done'".format(self.cluster.id)
        tty = True
        volumes = [
            "${COMPOSE_PROJECT_PATH}/scripts:/tmp/scripts",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config.yaml:/etc/hyperledger/fabric/crypto-config.yaml",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config:/etc/hyperledger/fabric/crypto-config",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/configtx.yaml:/etc/hyperledger/fabric/configtx.yaml",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/channel-artifacts:/tmp/channel-artifacts",
        ]
        working_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"
        hostname = "{}_cli".format(self.cluster.id)
        environment = [
            "CORE_LOGGING_LEVEL=DEBUG",
            "CORE_LOGGING_FORMAT=%{color}[%{id:03x} %{time:01-02 15:04:05.00 MST}] [%{longpkg}] %{callpath} -> "
            "%{level:.4s}%{color:reset} %{message}",
            "CORE_PEER_TLS_ENABLED=false",
            "TIMEOUT=30",
            "MAX_RETRY=5",
            "GEN_IMG=yeasy/hyperledger-fabric:{}".format(self.images.get('fabric_image')),
            'GEN_CONTAINER=generator',
            'FABRIC_CFG_PATH=/etc/hyperledger/fabric',
            'CHANNEL_ARTIFACTS=channel-artifacts',
            'CRYPTO_CONFIG=crypto-config',
            'ARCH=x86_64',
            'BASE_IMG_TAG=0.4.6',
            'FABRIC_IMG_TAG={}'.format(self.images.get('fabric_image')),
            'PROJECT_VERSION={}'.format(self.images.get('fabric_image')),
            'CTL_IMG=yeasy/hyperledger-fabric:{}'.format(self.images.get('fabric_image')),
            'CTL_CONTAINER=configtxlator',
            'CTL_BASE_URL=http://127.0.0.1:7059',
            'CTL_ENCODE_URL=http://127.0.0.1:7059/protolator/encode',
            'CTL_DECODE_URL=http://127.0.0.1:7059/protolator/decode',
            'CTL_COMPARE_URL=http://127.0.0.1:7059/configtxlator/compute/update-from-configs'
        ]
        depends_on = []
        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        orderer_domain = orderer_org.domain
        orderers = Node.objects(org=orderer_org, node_type='orderer')
        for orderer in orderers:
            orderer_name = orderer.alias
            depends_on.append('{}.{}'.format(orderer_name, orderer_domain))

            environment.append(
                "{}_TLS_CA=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/"
                "{}/orderers/{}.{}/msp/tlscacerts/tlsca.{}-cert.pem".format(
                    'ORDERER', orderer_domain, orderer_name, orderer_domain, orderer_domain))
            environment.append(
                "{}_MSP=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/orderers/{}.{}/msp".format(
                    'ORDERER', orderer_domain, orderer_name, orderer_domain))
            environment.append(
                "{}_TLS_ROOTCERT=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/orderers/{}.{}/tls/ca.crt"
                    .format('ORDERER', orderer_domain, orderer_name, orderer_domain)
            )
            environment.append(
                "{}_ADMIN_MSP=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/users/Admin@{}/msp"
                    .format('ORDERER', orderer_domain, orderer_domain)
            )

            environment.append("ORDERER_URL={}:7050".format('{}.{}'.format(orderer_name,orderer_domain)))
            environment.append('ORDERER_GENESIS=orderer.genesis.block')

        org_list = []
        peer_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer')
        for org in peer_orgs:
            org_name = org.alias
            domain = org.domain
            peers = Node.objects(org=org, node_type='peer')
            for peer in peers:
                peer_name = peer.alias
                org_peer_name = '{}_{}'.format(org_name.upper(), peer_name.upper())
                org_peer_service = '{}.{}.{}'.format(peer_name, org_name, domain)
                environment.append("{}_TLS_ROOTCERT=/etc/hyperledger/fabric/crypto-config/peerOrganizations/"
                                   "{}.{}/peers/{}/tls/ca.crt".format(org_peer_name, org_name, domain, org_peer_service))
                environment.append("{}_URL={}:7051".format(org_peer_name, org_peer_service))
            org_list.append(org_name)
            org_key = org_name.upper()
            org_host = '{}.{}'.format(org_name, domain)
            environment.append(
                "{}_ADMIN_MSP=/etc/hyperledger/fabric/crypto-config/peerOrganizations/{}/users/Admin@{}/msp".format(
                    org_key, org_host, org_host))
            environment.append("{}MSP={}MSP".format(org_key, org_name.capitalize()))
            environment.append("UPDATE_ANCHOR_{}_TX={}MSPanchors.tx".format(org_key, org_name.capitalize()))

        environment.append('ORDERER_PROFILE=OrdererGenesis')
        environment.append('ORGS={}'.format(','.join(org_list)))
        channel_list = []
        channels = ChannelModel.objects(cluster=self.cluster)
        for channel in channels:
            # name = str(channel.id)
            name = channel.alias
            channel_orgs = channel.orgs
            channel_list.append(name)
            channel_create_org = channel_orgs[0]
            channel_create_peer = Node.objects(org=channel_create_org, node_type='peer')[0]

            environment.append('{}_CREATE_ORG={}'.format(name.upper(), channel_create_org.alias))
            environment.append('{}_CREATE_PEER={}'.format(name.upper(), channel_create_peer.alias))
            environment.append('{}_ORGS={}'.format(name.upper(), ','.join([org.alias for org in channel_orgs])))

        environment.append('APP_CHANNELS={}'.format(','.join(channel_list)))

        for org in peer_orgs:
            peers = Node.objects(org=org, node_type='peer')
            peer_orgs_name = [peer.alias for peer in peers]
            environment.append('{}={}'.format(org.alias.upper(), ','.join(peer_orgs_name)))

        return {
            service_name:
                ContainerService(
                    image=image,
                    container_name=container_name,
                    command=command,
                    tty=tty,
                    restart='always',
                    environment=environment,
                    volumes=volumes,
                    working_dir=working_dir,
                    depends_on=depends_on,
                    hostname=hostname
                ).get_data()
        }

    def generate_add_org_cli(self, orgs, new_org, orderer_org, channel):
        service_name = 'new_cli'
        image = self.images.get('cli_image')

        container_name = "{}_add_org_cli".format(self.cluster_id)
        command = "bash -c 'sleep 5; cd /tmp && " \
                  "bash scripts/add_org.sh && curl http://120.27.22.25:8083/container?id={} && " \
                  "while true; do sleep 20180101; done'".format(self.cluster.id)
        tty = True
        volumes = [
            "${COMPOSE_PROJECT_PATH}/scripts:/tmp/scripts",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config.yaml:/etc/hyperledger/fabric/crypto-config.yaml",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/crypto-config:/etc/hyperledger/fabric/crypto-config",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/configtx.yaml:/etc/hyperledger/fabric/configtx.yaml",
            "${COMPOSE_PROJECT_PATH}/" + self.cluster_id + "/channel-artifacts:/tmp/channel-artifacts",
        ]
        working_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"
        hostname = "{}_add_org_cli".format(self.cluster.id)
        orderer_org_domain = orderer_org.domain
        environment = [
            "CORE_LOGGING_LEVEL=DEBUG",
            "CORE_LOGGING_FORMAT=%{color}[%{id:03x} %{time:01-02 15:04:05.00 MST}] [%{longpkg}] %{callpath} -> "
            "%{level:.4s}%{color:reset} %{message}",
            "CORE_PEER_TLS_ENABLED=false",
            "TIMEOUT=30",
            "MAX_RETRY=5",
            "GEN_IMG=yeasy/hyperledger-fabric:{}".format(self.images.get('fabric_image')),
            'GEN_CONTAINER=generator',
            'FABRIC_CFG_PATH=/etc/hyperledger/fabric',
            'CHANNEL_ARTIFACTS=channel-artifacts',
            'CRYPTO_CONFIG=crypto-config',
            'ARCH=x86_64',
            'BASE_IMG_TAG=0.4.6',
            'FABRIC_IMG_TAG={}'.format(self.images.get('fabric_image')),
            'PROJECT_VERSION={}'.format(self.images.get('fabric_image')),
            'CTL_IMG=yeasy/hyperledger-fabric:{}'.format(self.images.get('fabric_image')),
            'CTL_CONTAINER=configtxlator',
            'CTL_BASE_URL=http://127.0.0.1:7059',
            'CTL_ENCODE_URL=http://127.0.0.1:7059/protolator/encode',
            'CTL_DECODE_URL=http://127.0.0.1:7059/protolator/decode',
            'CTL_COMPARE_URL=http://127.0.0.1:7059/configtxlator/compute/update-from-configs',
            'CHANNEL={}'.format(channel),
            'ORGS={}'.format(','.join(orgs)),
            'NEW_ORG={}'.format(new_org.alias),
            'ORDERER_ORG={}'.format(orderer_org.alias),
            'ORDERER_DOMAIN={}'.format(orderer_org.domain),
            'ORDERER_CA=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/orderers/'
            'orderer.{}/msp/tlscacerts/tlsca.{}-cert.pem'.
                format(orderer_org_domain,orderer_org_domain,orderer_org_domain)
        ]
        return {
            service_name:
                ContainerService(
                    image=image,
                    container_name=container_name,
                    command=command,
                    tty=tty,
                    restart='always',
                    environment=environment,
                    volumes=volumes,
                    working_dir=working_dir,
                    # depends_on=depends_on,
                    hostname=hostname
                ).get_data()
        }

    def generate_kafka_service(self):
        kafka_list = {
            'kafka0': 9092,
            'kafka1': 9092,
            'kafka2': 9092,
            'kafka3': 9092
        }
        kafka_services = {}
        pos = 0
        for k, v in kafka_list.items():
            service_name = k
            image = self.images.get('kafka_image')
            restart = 'always'
            tty = True
            container_name = self.cluster.id + '_' + k
            hostname = k
            expose = [v]
            environment = [
                'KAFKA_MESSAGE_MAX_BYTES=1048576',
                'KAFKA_REPLICA_FETCH_MAX_BYTES=1048576',
                'KAFKA_UNCLEAN_LEADER_ELECTION_ENABLE=false',
                'KAFKA_LOG_RETENTION_MS=-1',
                'KAFKA_BROKER_ID={}'.format(pos),
                'KAFKA_MIN_INSYNC_REPLICAS=2',
                'KAFKA_DEFAULT_REPLICATION_FACTOR=3',
                'KAFKA_ZOOKEEPER_CONNECT=zookeeper0:2181,zookeeper1:2181,zookeeper2:2181'
            ]
            depends_on = [
                'zookeeper0',
                'zookeeper1',
                'zookeeper2'
            ]
            service = {
                service_name:
                    ContainerService(
                        image=image,
                        container_name=container_name,
                        environment=environment,
                        restart=restart,
                        depends_on=depends_on,
                        expose=expose,
                        tty=tty,
                        hostname=hostname
                    ).get_data()
            }
            kafka_services.update(service)
            pos += 1
        return kafka_services

    def generate_zookeeper_service(self):
        zookeeper_list = ['zookeeper0', 'zookeeper1', 'zookeeper2']
        image = self.images.get('zookeeper_image')
        zookeeper_services = {}
        pos = 1
        for zookeeper in zookeeper_list:
            service_name = zookeeper
            restart = 'always'
            tty = True
            container_name = self.cluster.id + '_' + zookeeper
            hostname = zookeeper
            environment = [
                'ZOO_MY_ID={}'.format(pos),
                'ZOO_SERVERS=server.1=zookeeper0:2888:3888 server.2=zookeeper1:2888:3888 server.3=zookeeper2:2888:3888'
            ]
            expose = [
                '2181', '2888', '3888'
            ]
            service = {
                service_name:
                    ContainerService(
                        image=image,
                        container_name=container_name,
                        environment=environment,
                        restart=restart,
                        expose=expose,
                        tty=tty,
                        hostname=hostname
                    ).get_data()
            }
            zookeeper_services.update(service)
            pos += 1
        return zookeeper_services

    def generate_start_file(self):

        orderer_services = {}
        peer_org_services = {}
        ca_services = {}
        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        orderers = Node.objects(org=orderer_org, node_type='orderer')
        domain = orderer_org.domain
        for orderer in orderers:
            orderer_services.update(self.generate_orderer_service(orderer, orderer_org, domain))

        peer_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer')

        for org in peer_orgs:
            peer_org_services.update(self.generate_peer_org_service(org, list(orderer_services.keys())))
            ca_services.update(self.generate_ca_service(org))

        cli_services = self.generate_cli_service(list(orderer_services.keys()), peer_org_services.keys())

        for peer_org_service_name in peer_org_services.keys():

            for k, v in orderer_services.items():
                v['external_links'].append(peer_org_service_name)

        services = {}
        services.update(ca_services)
        services.update(orderer_services)
        services.update(peer_org_services)
        services.update(cli_services)

        if self.cluster.consensus_plugin == 'kafka':
            kafka_services = self.generate_kafka_service()
            zookeeper_services = self.generate_zookeeper_service()
            services.update(kafka_services)
            services.update(zookeeper_services)

        return {
            'version': '3.2',
            'services': services,
            'networks': {
                # 'default': {
                #     'external': {
                #         'name': 'cello_net'
                #     }
                # }
                'default': {}
            }
        }

    def generate_compose_yaml(self):
        file_name = "{}.yaml".format(self.cluster_id)
        config = self.generate_start_file()
        self.generate_yaml_file(config, file_name)

    # def generate_one_org_config_file(self):
    #     nam

    def generate_start(self):
        logger.info('target_dir---{}'.format(self.target_dir))
        source_path = os.getcwd()
        logger.info('source path is {}'.format(source_path))
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)
        os.mkdir(self.target_dir)
        os.chdir(self.target_dir)
        out_dir = 'channel-artifacts'
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.mkdir(out_dir)

        self.generate_crypto_config()
        self.generate_channel_config()

        self.generate_crypto_dir()

        self.generate_genesis_block()
        self.generate_channel_tx()
        self.generate_compose_yaml()

        os.chdir(source_path)
        cluster_info = self.generate_chaincode_config()

        return cluster_info


class OrgConfig(object):

    def __init__(self, name, domain, peers, users, ca):
        # peers should be a list of peer's name
        self.name = name
        self.domain = domain
        self.peers = peers
        self.users = users
        self.ca = ca

    def group_config_content(self):
        content = {
            "Users": {"Count": self.users},
            "Name": self.name.capitalize(),
            "Domain": "{}.{}".format(self.name, self.domain),
            "Specs": [
                {
                    "Hostname": peer
                }
                for peer in self.peers
            ],
            "CA":
                {
                    "Hostname": self.ca
                }
        }
        return content


class GenerateYamlFile(object):
    def __init__(self, path):
        self.path = path

    def generate_org_file(self, config, file_name):
        generate_yaml_file(config, file_name, self.path)


class TxHandler:

    def group_orderer_org_config(self,name, domain):
        content = {
            "Name": '{}MSP'.format(name.capitalize()),  # maybe OrdererOrg
            "MSPDir": "crypto-config/ordererOrganizations/{}/msp".format(domain),
            "ID": "{}MSP".format(name.capitalize())
        }
        return {name: content}

    def group_peer_org_config(self, name, domain, peer):
        content = {
            "AnchorPeers": [
                {
                    "Port": 7051,
                    "Host": "{}.{}.{}".format(peer, name, domain)
                }
            ],
            "Name": "{}MSP".format(name.capitalize()),
            "MSPDir": "crypto-config/peerOrganizations/{}.{}/msp".format(name, domain),
            "ID": "{}MSP".format(name.capitalize())
        }
        return {name: content}

    def group_orderer_config(self, consensus_plugin, domain, orderers):
        content = {
            "OrdererType": consensus_plugin,
            "Addresses": ['{}.{}:7050'.format(orderer, domain) for orderer in orderers],
            "BatchTimeout": "2s",
            "BatchSize": {
                "MaxMessageCount": 10,
                "AbsoluteMaxBytes": "98 MB",
                "PreferredMaxBytes": "512 KB"
            },
            "Organizations": None
        }
        if consensus_plugin == 'kafka':
            kafka_config = {
                'Brokers': [
                    'kafka0:9092',
                    'kafka1:9092',
                    'kafka2:9092',
                    'kafka3:9092'
                ]
            }
            content.update({'Kafka': kafka_config})
        return content

    def orderer_profile(self, capabilities,orderer,orderer_orgs,peer_orgs):
        orderer_config = {}
        orderer_config.update(orderer)
        orderer_config.update({'Organizations': orderer_orgs})
        orderer_config.update({'Capabilities': capabilities['Orderer']})
        content = {
            'Capabilities': capabilities['Global'],
            'Orderer': orderer_config,
            'Consortiums': {
                'SampleConsortium': {
                    'Organizations': peer_orgs
                }
            }
        }
        return {'OrdererGenesis': content}

    def group_channel_config(self, channel, orgs, capabilities):
        content = {
            'Consortium': 'SampleConsortium',
            'Application': {
                'Organizations': orgs,
                'Capabilities': capabilities['Application'],
                'Resources': {
                    'DefaultModPolicy': '/Channel/Application/Writers'
                }
            }
        }
        return {channel: content}

    def group_tx_config(self, orgs, orderer, profiles):
        capabilities = {
            'Application': {'V1_1': False},
            'Global': {'V1_1': True},
            'Orderer': {'V1_1': True}
        }
        applications = {'Organizations': None}
        organizations = orgs
        content = {
            'Organizations': organizations,
            'Orderer': orderer,
            'Application': applications,
            'Capabilities': capabilities,
            'Profiles': profiles
        }
        return content


class GenerateTxFile:
    def __init__(self, cluster):
        self.cluster = cluster
        self.peer_orgs_config = {}
        self.orderer_org_config = {}

    def generate_tx_config(self):
        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        peer_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer')
        channels = ChannelModel.objects(cluster=self.cluster)
        handler = TxHandler()
        orderer_org_config = handler.group_orderer_org_config(str(orderer_org.id), orderer_org.domain)
        self.orderer_org_config.update(orderer_org_config)
        for org in peer_orgs:
            achor_peer = Node.objects(org=org, node_type='peer')[0]
            org_config = handler.group_peer_org_config(str(org.id),org.domain, achor_peer.name)
            self.peer_orgs_config.update(org_config)
        capabilities = {
            'Application': {'V1_1': False},
            'Global': {'V1_1': True},
            'Orderer': {'V1_1': True}
        }
        profiles = {}
        for channel in channels:
            channel_id = str(channel.id)
            orgs = channel.orgs
            channel_orgs_list = [self.peer_orgs_config[str(org.id)] for org in orgs]
            channel_profile = handler.group_channel_config(channel.name,channel_orgs_list,capabilities)
            profiles.update({channel_id: channel_profile})
        orderers = Node.objects.get(org=orderer_org,node_type='orderer')
        orderers_list = [str(orderer.id) for orderer in orderers]
        orderer_config = handler.group_orderer_config(self.cluster.consensus_plugin, orderer_org .domain, orderers_list)
        orderer_profile = handler.orderer_profile(capabilities,
                                                  orderer_config,
                                                  self.orderer_org_config.values(),
                                                  self.peer_orgs_config.values()
                                                  )
        profiles.update(orderer_profile)
        all_orgs = {}
        all_orgs.update(self.peer_orgs_config.values())
        all_orgs.update(self.orderer_org_config.values())
        content = handler.group_tx_config(all_orgs, orderer_config, profiles)
        return content


class AddOrg:

    def __init__(self, cluster):
        self.cluster = cluster
        self.handler = GenerateClusterFiles()
        self.target_path = os.path.join(BLOCKCHAIN_CONFIG_FILES_PATH, str(self.cluster.id))

    def generate_new_org_crypto(self, org):
        name = str(org.id)
        ca = 'ca'
        domain = org.domain
        peers = Node.objects(org=org, node_type='peer')
        peer_list = [str(peer.id) for peer in peers]
        config = group_crypto_org_config(name, domain, 1, peer_list, ca)
        config = {'PeerOrgs': [config]}
        file_name = 'crypto-config-{}.yaml'.format(name)
        generate_yaml_file(config, file_name, self.target_path)
        self.handler.generate_crypto_file(file_name)

    def generate_new_tx_file(self, cluster):
        tx_handler = GenerateTxFile(cluster)
        tx_config = tx_handler.generate_tx_config()
        file_name = 'configtx.yaml'
        generate_yaml_file(tx_config, file_name, self.target_path)

    def generate_new_org_json(self, org):
        name = str(org.id)
        self.handler.generate_new_org_json_file(name)
        logger.info('path:' + os.getcwd())

    def generate_start(self, org):
        logger.info('target_dir---{}'.format(self.target_path))
        source_path = os.getcwd()
        os.chdir(self.target_path)
        out_dir = 'channel-artifacts'
        # 生成新组织的crypto-config-org
        self.generate_new_org_crypto(org)
        # 重新生成完整crypto-config.yaml
        # 重新生成configtx文件
        self.generate_new_tx_file(self.cluster)
        # 用新的configtx文件生成新组织的信息，json文件
        self.generate_new_org_json(org)
        # 生成启动容器文件
        generate_handler = GenerateChainBlockConfig(self.cluster, self.target_path)
        # 生成新组织容器配置文件
        original_orgs = OrgModel.objects(cluster=self.cluster,org_type='peer',name__ne=org.name)
        orderer_org = OrgModel.objects.get(cluster=self.cluster)
        orderers = Node.objects(org=orderer_org)
        orderers_id = [str(orderer.id) for orderer in orderers]
        channel = ChannelModel.objects.get(cluster=self.cluster)
        org_service = generate_handler.generate_peer_org_service(org, orderers_id)
        # 新组织ca配置文件
        ca_service = generate_handler.generate_ca_service(org)
        # 新的cli配置文件
        add_org_cli = generate_handler.generate_add_org_cli(
            [org.alias for org in original_orgs],
            org,
            orderer_org,
            channel
        )
        os.chdir(source_path)


if __name__ == '__main__':
    generate_yaml_file({'Name': 'aaa', 'Domain': 'haha.com'}, 'ceshi.yaml', './haha')
