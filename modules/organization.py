import logging
import os
import sys
import time

import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common import log_handler, LOG_LEVEL, \
    CLUSTER_PORT_START, CLUSTER_PORT_STEP, \
    BLOCKCHAIN_CONFIG_FILES_PATH

from common.utils import FABRIC_IMAGES_MAPPING, CRYPTO_GEN_TOOL,IP_MAPPINGS
from agent import get_project
from modules.models import Cluster as ClusterModel
from modules.models import ServicePort
from modules.models.host import Org as OrgModel, Container
from modules.models.host import Node
from modules.models.host import Channel as ChannelModel
from config_files.generate_config_files import ContainerService, GenerateChainBlockConfig
from config_files.compose_handler import ComposeHandler

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

peer_service_ports = ['{}_{}_grpc', '{}_{}_event']

ca_service_ports = '{}_{}_ecap'


class OrganizationHandler(object):

    @staticmethod
    def find_free_port(host, number):
        logger.debug("Find {} start ports for host {}".format(number, host.id))
        if number <= 0:
            logger.warning("number {} <= 0".format(number))
            return []

        if not host:
            logger.warning("Cannot find host")
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

    def generate_ports_mapping(self, peer_services, ca_service, host):
        request_port_num = len(peer_services) + 1
        ports = self.find_free_port(host, request_port_num)
        if not ports:
            logger.warning("No free port is found")
        else:
            logger.info("ports {}".format(ports))

        peer_ports = {}
        ca_port = {}
        all_ports = {}
        pos = 0
        for peer_service in peer_services:
            peer_ports[peer_service] = ports[pos]
            pos += 1
        ca_port[ca_service] = ports[pos]
        all_ports.update(peer_ports)
        all_ports.update(ca_port)
        return all_ports, ca_port, peer_ports

    @staticmethod
    def generate_config(name, domain, ca, peers):
        org_info = {
            "Users": {"Count": 1},  # TODO
            "Name": name.capitalize(),
            "Domain": "{}.{}".format(name, domain),

            "Specs": [
                {
                    "Hostname": str(peer.id)
                }
                for peer in peers
            ],
            "CA":
                {
                    "Hostname": ca.name
                }
        }
        return org_info

    @staticmethod
    def generate_ca_service(ca_name, org_name, domain, port, cluster):
        service_name = '{}.{}.{}'.format(ca_name, org_name, domain)
        image = FABRIC_IMAGES_MAPPING[cluster.network].get('ca_image')
        key_file = "./crypto-config/peerOrganizations/" + org_name + "." + domain + "/ca"
        key_name = ''
        for i in os.listdir(key_file):
            if i.endswith('_sk'):
                key_name = i
                break
        container_name = cluster.id + '_' + ca_name + '_' + org_name
        command = "sh -c 'fabric-ca-server start -b admin:adminpw -d'"
        ports = [
            '{}:7054'.format(port)
        ]
        environment = [
            "FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server",
            "FABRIC_CA_SERVER_CA_NAME=ca_peer" + org_name.capitalize(),
            "FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/" + service_name + "-cert.pem",
            "FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/{}".format(key_name),
            "FABRIC_CA_SERVER_TLS_ENABLED=false",
            "FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/" + service_name + "-cert.pem",
            "FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/{}".format(key_name)
        ]
        volumes = [
            "${COMPOSE_PROJECT_PATH}/" + cluster.id + "/crypto-config/peerOrganizations/" + org_name + "." + domain
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
        # ca_org_services.update(service)
        return service

    @staticmethod
    def generate_peer_service(peer_name, org_name, domain, peer_ports, cluster):
        service_name = "{}.{}.{}".format(peer_name, org_name, domain)
        image = FABRIC_IMAGES_MAPPING[cluster.network].get('peer_image')
        container_name = "{}_{}_{}".format(cluster.id, peer_name, org_name)
        command = "peer node start"
        volumes = [
            "/var/run/docker.sock:/var/run/docker.sock",
            "${COMPOSE_PROJECT_PATH}/" + cluster.id + "/crypto-config/peerOrganizations/" + "{}.{}".format(
                org_name,
                domain) +
            "/peers/{}/msp:/etc/hyperledger/fabric/msp".format(service_name),
            "${COMPOSE_PROJECT_PATH}/" + cluster.id + "/crypto-config/peerOrganizations/" + "{}.{}".format(
                org_name,
                domain) +
            "/peers/{}/tls:/etc/hyperledger/fabric/tls".format(service_name)
        ]
        working_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"
        ports = [
            "{}:7051".format(peer_ports.get('{}_{}_grpc'.format(peer_name, org_name))),
            "{}:7053".format(peer_ports.get('{}_{}_event'.format(peer_name, org_name))),
        ]
        environment = [
            # "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE={}_default".format(self.cluster_id),
            # "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=cello_net",
            "CORE_LOGGING_LEVEL=DEBUG",
            "CORE_PEER_GOSSIP_USELEADERELECTION=true",
            "CORE_PEER_GOSSIP_ORGLEADER=false",
            "CORE_PEER_GOSSIP_SKIPHANDSHAKE=true",
            "CORE_PEER_TLS_ENABLED=false",
            "CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt",
            "CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key",
            "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt",
            "CORE_VM_DOCKER_HOSTCONFIG_MEMORY=268435456",
            "CORE_PEER_ID={}".format(service_name),
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
                    working_dir=working_dir
                ).get_data()
        }
        return service

    def generate_compose_config(self, ca, peers, org, domain, ca_port, peer_ports, cluster):
        services = {}
        peer_services = {}
        for peer in peers:
            peer_services.update(self.generate_peer_service(peer, org, domain, peer_ports, cluster))
        ca_service = self.generate_ca_service(ca, org, domain, ca_port, cluster)
        services.update(peer_services)
        services.update(ca_service)
        compose_config = {
            'version': '3.2',
            'services': services,
            'networks': {
                'default': {
                    'external': {
                        'name': '{}_default'.format(cluster.id)
                    }
                }
            }
        }
        return compose_config

    @staticmethod
    def generate_yaml_file(config, file_name, file_path):
        target_file = os.path.join(file_path, file_name)
        logger.info('create {}'.format(target_file))
        with open(file_name, 'w') as f:
            yaml.safe_dump(config, f)
        if os.path.exists(file_name):
            logger.info('create {} success'.format(file_name))
            return True
        else:
            logger.info('create {} failed'.format(file_name))
            return False

    def generate_org_config_yaml(self, org_id, name, domain, ca, peers, path):
        config = self.generate_config(org_id, domain, ca, peers)
        file_name = 'crypto-config-{}.yaml'.format(name)
        if self.generate_yaml_file(config, file_name, path):
            logger.info('create {} success'.format(file_name))
            return os.path.join(path, file_name)
        else:
            logger.error('create {} failed'.format(file_name))
            return None

    def generate_compose_yaml(self, ca, peers, name, domain, ca_port, peer_ports, path, cluster):
        compose_file_content = self.generate_compose_config(ca, peers, name, domain, ca_port, peer_ports, cluster)
        compose_file_name = 'compose-file-{}'.format(name)
        if self.generate_yaml_file(compose_file_content, compose_file_name, path):
            return True
        else:
            return False

    @staticmethod
    def generate_org_crypto_file(config_file, out_path):
        out_put_path = os.path.join(out_path, 'crypto-config')
        result = os.system(CRYPTO_GEN_TOOL + ' generate --config={} --output={}'.
                           format(config_file, out_put_path))
        if result == 0:
            logger.info('create crypto-config-dir with crypto-config.yaml success')
            return True
        else:
            logger.info('create crypto-config-dir with crypto-config.yaml failed')
            return False

    def update_configtx(self, cluster, path):
        tx_content = GenerateChainBlockConfig(cluster, config_file_path=path).group_configtx()

    def generate_config_file(self, cluster, org, ca_port, peer_ports):
        org_id = str(org.id)
        name = org.name
        domain = org.domain
        ca = Node.objects.get(org=org, node_type='ca')
        peers = Node.objects(org=org, node_type='peer')

        cluster_config_path = os.path.join(BLOCKCHAIN_CONFIG_FILES_PATH, cluster.id)
        org_config_file = self.generate_org_config_yaml(org_id, name, domain, ca, peers, cluster_config_path)
        if not org_config_file:
            return False
        if not self.generate_org_crypto_file(org_config_file, cluster_config_path):
            logger.info('generate org crypto file failed')
            return False
        if not self.generate_compose_yaml(ca, peers, name, domain, ca_port, peer_ports, cluster_config_path, cluster):
            logger.info('generate compose file failed')
            return False

    @staticmethod
    def compose_up(cluster, host, file, timeout=5):
        logger.info("Compose start: name={}, host={}".format(cluster.id, host))
        envs = {
            'COMPOSE_PROJECT_NAME': cluster.id,
            # 'CLUSTER_LOG_LEVEL': log_level,
            'CLUSTER_NETWORK': "{}_default".format(cluster.id),
            'DOCKER_HOST': host.worker_api,
            'PEER_NETWORKID': cluster.id,
            'NETWORK_TYPES': cluster.network_type,
            'VM_ENDPOINT': host.worker_api,
            'VM_DOCKER_HOSTCONFIG_NETWORKMODE': "{}_default".format(cluster.id),
            'COMPOSE_FILE': "{}".format(file)
        }
        os.environ.update(envs)
        try:
            template_path = BLOCKCHAIN_CONFIG_FILES_PATH + os.sep + cluster.id
            logger.debug('template path {}'.format(template_path))
            project = get_project(template_path)
            containers = project.up(detached=True, timeout=timeout)
        except Exception as e:
            logger.warning("Exception when compose start={}".format(e))
            return {}
        logger.debug("containers={}".format(containers))
        if not containers:
            return {}
        result = {}
        for c in containers:
            result[c.name] = c.id

        logger.debug("compose started with containers={}".format(result))
        return result

    # def create_org_container(self):

    def create(self, name, domain, ca, peers, cluster, user):

        host = cluster.host
        peer_services = []
        if not isinstance(peers, list):
            peers = ['peer{}'.format(_) for _ in range(int(peers))]
        for peer in peers:
            for k in peer_service_ports:
                peer_services.append(k.format(peer, name))
        ca_service = ca_service_ports.format(ca, name)
        map_ports, ca_port, peer_ports = self.generate_ports_mapping(peer_services, ca_service, host)
        if not map_ports:
            logger.error("mapped_ports={}".format(map_ports))
            return None
        cluster.update(add_to_set__ports=list(map_ports.values()))

        # 写个方法得了
        host_ip = host.worker_api.split(':')[1][2:]
        original_orgs = OrgModel.objects(cluster=cluster, org_type='peer').all().count()
        new_org = OrgModel(
            name=name,
            alias='org{}'.format(original_orgs+1),
            domain=domain,
            org_type='peer',
            cluster=cluster
        )
        new_org.save()
        channels = ChannelModel.objects(cluster=cluster)
        channels[0].update(add_to_set__orgs=[new_org])
        pos = 0
        for peer in peers:
            peer = Node(
                name=peer,
                alias='peer{}'.format(pos),
                node_type='peer',
                ip=IP_MAPPINGS[host_ip],
                org=new_org,
                ports={
                    'grpc': map_ports.get("{}_{}_grpc".format(peer, new_org.name)),
                    'event': map_ports.get("{}_{}_event".format(peer, new_org.name))
                }
            )
            peer.save()
            pos += 1

        ca = Node(
            name=ca,
            alias='ca',
            ip=IP_MAPPINGS[host_ip],
            node_type='ca',
            org=new_org,
            ports={'ecap': map_ports.get('{}_{}_ecap'.format(ca, new_org.name))}
        )
        ca.save()
        compose_file_handler = ComposeHandler(cluster)
        compose_file = compose_file_handler.add_org(new_org)
        if not compose_file:
            logger.error('generate config file failed')
            new_org.delete()
            return None
        containers = self.compose_up(cluster=cluster, host=host, file=compose_file)
        config_path = BLOCKCHAIN_CONFIG_FILES_PATH
        cluster_info = compose_file_handler.generate_chaincode_config()

        if not containers:
            logger.warning("failed to create container")
            return {}
        else:
            from tasks import send_cluster_info
            time.sleep(20)
            send_cluster_info(config_path=config_path, cid=str(cluster.id), cluster_info=cluster_info, user_id=user)

            for k, v in containers.items():
                container = Container(id=v, name=k, cluster=cluster)
                container.save()

            service_urls = cluster.service_url

            for k, v in service_urls.items():
                service_port = ServicePort(name=k, ip=v.split(":")[0],
                                           port=int(v.split(":")[1]),
                                           cluster=cluster)
                service_port.save()
            logger.debug("Created containers={}".format(containers))
            return containers
