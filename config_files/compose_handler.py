import os
import logging

from common import log_handler, LOG_LEVEL
from .config_generator import CryptoGenerator, TxGenerator
from .service_generator import ServiceGenerator
from .yaml_generator import ClusterYamlGenerator
from .certificate_generator import FilesGenerator
from .config_generator import ConfigGenerator
from modules.models.host import Channel as ChannelModel
from modules.models.host import Org as OrgModel
from modules.models.host import Node
from common import BLOCKCHAIN_CONFIG_FILES_PATH


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


class ComposeHandler(object):

    def __init__(self, cluster):
        self.cluster = cluster
        self.crypto_generator = CryptoGenerator()
        self.tx_generator = TxGenerator()
        self.yaml_generator = ClusterYamlGenerator(cluster)
        self.service_generator = ServiceGenerator(cluster)
        self.channel = ChannelModel.objects.get(cluster=self.cluster)
        self.config_generator = ConfigGenerator()

    def create_cluster(self):
        channel = self.channel.alias
        crypto_config = {}
        services = {}
        orderer_services = {}
        peer_services = {}
        tx_orgs_lsit = []
        # channel = ChannelModel.objects.get(cluster=self.cluster)

        peer_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer')

        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        orderers = Node.objects(org=orderer_org, node_type='orderer')
        orderer_list = [orderer.alias for orderer in orderers]
        orderer_org_name = orderer_org.alias
        orderer_org_domain = orderer_org.domain
        orderer_service_list = ['{}.{}'.format(orderer, orderer_org_domain) for orderer in orderer_list]
        crypto_peer_orgs = []
        tx_peer_orgs = []
        cli_orgs = []
        for peer_org in peer_orgs:
            peer_org_name = peer_org.alias
            peer_org_domain = peer_org.domain
            peers = Node.objects(org=peer_org, node_type='peer')
            ca = Node.objects.get(org=peer_org, node_type='ca')
            peer_list = [peer.alias for peer in peers]
            # crypto peer org config
            crypto_org_config = self.crypto_generator.generate_peer_org(peer_org_name, peer_org_domain, peer_list,
                                                                        ca.alias)
            crypto_peer_orgs.append(crypto_org_config)

            # tx peer org config
            tx_peer_org_config = self.tx_generator.group_peer_org_config(peer_org_name, peer_org_domain)
            tx_peer_orgs.append(tx_peer_org_config)
            tx_orgs_lsit.append(tx_peer_org_config)
            cli_orgs.append({'name': peer_org_name, 'domain': peer_org_domain, 'peers': peer_list})
            # peer service
            for peer in peers:
                peer_ports = peer.ports
                peer_service = self.service_generator.generate_peer_config(peer.alias, peer_ports, peer_org_name, peer_org_domain,
                                                                           orderer_service_list)
                peer_services.update(peer_service)

        crypto_config.update({'PeerOrgs': crypto_peer_orgs})

        # generate orderer crypto config
        crypto_orderer_config = self.crypto_generator.generate_orderer_org(orderer_org_name, orderer_list,
                                                                           orderer_org_domain)
        crypto_config.update({'OrdererOrgs': [crypto_orderer_config]})
        # orderer services
        for orderer in orderers:
            orderer_ports = orderer.ports
            orderer_service = self.service_generator.generate_orderer_config(orderer.alias, orderer_ports, orderer_org_domain, peer_services)
            orderer_services.update(orderer_service)
        # tx orderer default config
        tx_orderer_default_config = self.tx_generator.group_orderer_config(
            self.cluster.consensus_plugin,
            orderer_org_domain,
            orderer_list
        )
        # tx orderer org config
        tx_orderer_org_config = self.tx_generator.group_orderer_org_config(orderer_org_name, orderer_org_domain)
        tx_orgs_lsit.append(tx_orderer_org_config)
        # tx orderer profile
        profiles = {}
        tx_orderer_profile = self.tx_generator.orderer_profile(tx_orderer_default_config, tx_orderer_org_config,
                                                               tx_peer_orgs)
        tx_channel_config = self.tx_generator.group_channel_config(channel, tx_peer_orgs)
        profiles.update(tx_orderer_profile)
        profiles.update(tx_channel_config)
        tx_config = self.tx_generator.group_tx_config(tx_orgs_lsit, tx_orderer_default_config, profiles)
        cli_service = self.service_generator.generate_create_cli_config(orderer_org_domain, cli_orgs, channel)
        services.update(peer_services)
        services.update(orderer_services)
        services.update(cli_service)

        self.yaml_generator.generate_create_yaml(crypto_config, tx_config)
        compose_file_path = BLOCKCHAIN_CONFIG_FILES_PATH + os.sep + self.cluster.id
        FilesGenerator(compose_file_path).generate_create_file(channel)
        for peer_org in peer_orgs:
            peer_org_name = peer_org.alias
            peer_org_domain = peer_org.domain
            ca = Node.objects.get(org=peer_org, node_type='ca')
            ca_service = self.service_generator.generate_ca_config(ca.alias, ca.ports, peer_org_name, peer_org_domain)
            services.update(ca_service)
        compose_config = {
            'version': '3.2',
            'services': services,
            'networks': {
                'default': {}
            }
        }
        compose_file = self.yaml_generator.generate_compose_yaml(compose_config)
        return compose_file

    def add_org(self, org):
        services = {}
        compose_file_path = BLOCKCHAIN_CONFIG_FILES_PATH + os.sep + self.cluster.id
        file_generator = FilesGenerator(compose_file_path)
        channel = self.channel.alias
        consensus_plugin = self.cluster.consensus_plugin
        all_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer')
        all_orgs_info = [
            {'name': org.alias, 'domain': org.domain}
            for org in all_orgs
        ]

        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        orderers = Node.objects(org=orderer_org, node_type='orderer')
        orderer_list = [orderer.alias for orderer in orderers]
        orderer_info = {
            'name': orderer_org.alias,
            'domain': orderer_org.domain,
            'orderers': orderer_list
        }
        # logger.info('org_info:{}, orderer_info:{}'.format(all_orgs_info, orderer_info))
        new_tx_config = self.config_generator.generate_tx_config(orderer_info, all_orgs_info,consensus_plugin,channel)
        # generate new tx yaml
        # logger.info('new tx config:{}'.format(new_tx_config))
        self.yaml_generator.generate_tx_yaml(new_tx_config)

        orderer_org_domain = orderer_org.domain
        orderer_service_list = ['{}.{}'.format(orderer, orderer_org_domain) for orderer in orderer_list]

        new_org_name = org.alias
        new_org_domain = org.domain
        peers = Node.objects(org=org, node_type='peer')
        ca = Node.objects.get(org=org, node_type='ca')
        peer_list = [peer.alias for peer in peers]
        new_org_info = {'name':new_org_name,'domain':new_org_domain,'peers':peer_list}
        # generate new org crypto config
        crypto_org_config = self.crypto_generator.generate_peer_org(new_org_name, new_org_domain, peer_list, ca.alias)
        # generate new org crypto yaml
        crypto_new_org_config = {'PeerOrgs': [crypto_org_config]}
        self.yaml_generator.generate_add_org_yaml(crypto_new_org_config, new_org_name)
        # generate new org cert files
        file_generator.generate_new_org_cert(new_org_name)

        ca_service = self.service_generator.generate_ca_config(ca.alias, ca.ports, new_org_name, new_org_domain)
        services.update(ca_service)
        for peer in peers:
            peer_ports = peer.ports
            peer_service = self.service_generator.generate_peer_config(peer.alias, peer_ports, new_org_name, new_org_domain)
            services.update(peer_service)

        original_orgs = OrgModel.objects(cluster=self.cluster, org_type='peer', alias__ne=new_org_name)
        original_org_list = {original_org.alias: original_org.domain for original_org in original_orgs}

        cli_service = self.service_generator.generate_add_org_cli(orderer_org_domain, channel,original_org_list, new_org_info)
        services.update(cli_service)
        compose_config = {
            'version': '3.2',
            'services': services,
            'networks': {
                'default': {}
            }
        }
        file_generator.generate_new_org_json(new_org_name)

        compose_file = self.yaml_generator.generate_new_org_compose_file(compose_config, new_org_name)
        if compose_file:
            return compose_file
        else:
            return None

    def generate_chaincode_config(self):

        all_orgs = []
        orderer_org = OrgModel.objects.get(cluster=self.cluster, org_type='orderer')
        orderer_name = orderer_org.name
        orderer_alias = orderer_org.alias
        orderer_domain = orderer_org.domain
        orderers = Node.objects(org=orderer_org, node_type='orderer')
        orderer_org_info = {
            'OrgId': orderer_alias,
            "Name": orderer_name,
            "Type": "orderer",
            "Domain": orderer_domain,
            "MspId": "{}MSP".format(orderer_alias.capitalize()),
            "Orderers": [
                {
                    "Name": '{}.{}'.format(orderer.alias, orderer_domain),
                    "Url": '{}:{}'.format(orderer.ip, orderer.ports['orderer'])
                }
                for orderer in orderers
            ]
        }

        all_orgs.append(orderer_org_info)

        peer_orgs = {}
        peer_orgs_list = OrgModel.objects(cluster=self.cluster, org_type='peer')
        for peer_org in peer_orgs_list:
            # org_id = str(peer_org.id)
            name = peer_org.name
            alias = peer_org.alias
            domain = peer_org.domain
            peers = Node.objects(org=peer_org, node_type='peer')
            cas = Node.objects(org=peer_org, node_type='ca')
            peer_org_info = {
                'OrgId': alias,
                "Name": name,
                "Type": "peer",
                "Domain": domain,
                "MspId": "{}MSP".format(alias.capitalize()),
                "Peers": [
                    {
                        "Name": '{}.{}.{}'.format(peer.alias, alias, domain),
                        "Url": '{}:{}'.format(peer.ip, peer.ports['grpc']),
                        "EventUrl": '{}:{}'.format(peer.ip, peer.ports['event'])
                    }
                    for peer in peers
                ],
                'Cas': [
                    {
                        "Name": '{}.{}.{}'.format(ca.alias, alias, domain),
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
            # channel_id = str(channel.id)
            name = channel.name
            alias = channel.alias
            orderers = channel.orderers
            orgs = channel.orgs
            channel_info = {
                "ChannelId": alias,
                'ChannelName': name,
                "ChannelConfigName": "{}.tx".format(alias),
                "Orderers": [
                    # str(orderer.id)
                    '{}.{}'.format(orderer.alias, orderer_domain)
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
            "BlockchainSign": str(self.cluster.id),
            "BlockchainName": self.cluster.name,
            "Algorithm": self.cluster.consensus_plugin,
            "CreateTime": self.cluster.create_ts.strftime("%Y%m%d%H%M%S"),
            "BlockChainCertPath": "zz",
            'TlsEnable': False,
            "Channels": channels
        }

        cluster_info.update({'Orgs': all_orgs})
        return cluster_info
