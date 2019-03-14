import os

from common import MAP_PATH, BLOCKCHAIN_CONFIG_FILES_PATH

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

        return dict(self)


class ServiceGenerator(object):

    def __init__(self, cluster):
        self.cluster = cluster
        self.cluster_id = cluster.id
        self.network_type = cluster.network_type
        self.images = fabric_images_maps.get(self.network_type)
        self.compose_file_path = MAP_PATH

    def generate_ca_config(self, ca, ca_ports, org, domain):

        image = self.images.get('ca_image')
        service_name = '{}.{}.{}'.format(ca, org, domain)
        key_file = "{}/{}/crypto-config/peerOrganizations/{}.{}/ca".format(
            BLOCKCHAIN_CONFIG_FILES_PATH,
            self.cluster_id,
            org,
            domain
        )
        key_name = ''
        for i in os.listdir(key_file):
            if i.endswith('_sk'):
                key_name = i
                break
        container_name = '{}_{}_{}'.format(self.cluster_id, ca, org)
        command = "sh -c 'fabric-ca-server start -b admin:adminpw -d'"
        ports = [
            '{}:7054'.format(ca_ports.get('ecap'))
        ]
        environment = [
            "FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server",
            "FABRIC_CA_SERVER_CA_NAME=ca_peer" + org.capitalize(),
            "FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/{}.{}.{}-cert.pem"
                .format(ca, org, domain),
            "FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/{}".format(key_name),
            "FABRIC_CA_SERVER_TLS_ENABLED=false",
            "FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/{}.{}.{}-cert.pem"
                .format(ca, org, domain),
            "FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/{}".format(key_name)
        ]
        volumes = [
            self.compose_file_path + self.cluster_id + "/crypto-config/peerOrganizations/" + org + "." + domain
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

        return service

    def generate_orderer_config(self, orderer, orderer_ports, domain, peer_services, org='orderer'):

        service_name = '{}.{}'.format(orderer, domain)
        image = self.images.get('orderer_image')
        container_name = '{}_{}_{}'.format(self.cluster_id, org, orderer)
        command = "orderer"
        ports = ["{}:7050".format(orderer_ports.get('orderer'))]
        environment = [
            "ORDERER_GENERAL_LOGLEVEL=DEBUG",
            "ORDERER_GENERAL_LISTENADDRESS=0.0.0.0",
            "ORDERER_GENERAL_GENESISMETHOD=file",
            "ORDERER_GENERAL_GENESISFILE=/var/hyperledger/orderer/orderer.genesis.block",
            "ORDERER_GENERAL_LOCALMSPID={}MSP".format(org.capitalize()),
            "ORDERER_GENERAL_LOCALMSPDIR=/var/hyperledger/orderer/msp",
            "ORDERER_GENERAL_TLS_ENABLED=false",
            "ORDERER_GENERAL_TLS_PRIVATEKEY=/var/hyperledger/orderer/tls/server.key",
            "ORDERER_GENERAL_TLS_CERTIFICATE=/var/hyperledger/orderer/tls/server.crt",
            "ORDERER_GENERAL_TLS_ROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]",
        ]
        volumes = [
            self.compose_file_path + self.cluster_id + "/channel-artifacts/orderer.genesis.block:"
                                                       "/var/hyperledger/orderer/orderer.genesis.block",
            self.compose_file_path + self.cluster_id + "/crypto-config/ordererOrganizations/" + domain +
            "/orderers/" + '{}.{}'.format(orderer, domain) + "/msp:/var/hyperledger/orderer/msp",
            self.compose_file_path + self.cluster_id + "/crypto-config/ordererOrganizations/" + domain +
            "/orderers/" + '{}.{}'.format(orderer, domain) + "/tls/:/var/hyperledger/orderer/tls"
        ]
        depends_on = []
        restart = 'always'
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

        external_links = [
            '{}_{}'.format(self.cluster_id, peer_service)
            for peer_service in peer_services
        ]
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

    def generate_peer_config(self, peer, peer_ports, org, domain, orderer_services=[]):

        service_name = '{}.{}.{}'.format(peer, org, domain)
        image = self.images.get('peer_image')
        container_name = '{}_{}_{}'.format(self.cluster_id, peer, org)
        command = "peer node start"
        volumes = [
            "/var/run/docker.sock:/var/run/docker.sock",
            self.compose_file_path + self.cluster_id + "/crypto-config/peerOrganizations/" + "{}.{}".format(
                org,
                domain) +
            "/peers/{}/msp:/etc/hyperledger/fabric/msp".format('{}.{}.{}'.format(peer, org, domain)),
            self.compose_file_path + self.cluster_id + "/crypto-config/peerOrganizations/" + "{}.{}".format(
                org,
                domain) +
            "/peers/{}/tls:/etc/hyperledger/fabric/tls".format('{}.{}.{}'.format(peer, org, domain))
        ]
        working_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"
        depends_on = orderer_services
        ports = [
            "{}:7051".format(peer_ports.get('grpc')),
            "{}:7053".format(peer_ports.get('event')),
        ]
        environment = [
            "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE={}_default".format(self.cluster_id),
            "CORE_LOGGING_LEVEL=DEBUG",
            "CORE_PEER_GOSSIP_USELEADERELECTION=true",
            "CORE_PEER_GOSSIP_ORGLEADER=false",
            "CORE_PEER_GOSSIP_SKIPHANDSHAKE=true",
            "CORE_PEER_TLS_ENABLED=false",
            "CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt",
            "CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key",
            "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt",
            "CORE_VM_DOCKER_HOSTCONFIG_MEMORY=268435456",
            "CORE_PEER_ID={}".format(peer),
            "CORE_PEER_LOCALMSPID={}MSP".format(org.capitalize()),
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

        return service

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

    def generate_create_cli_config(self, orderer_domain, orgs, channel):
        # orgs should be a list contain the peers of this org,
        # example: [{name:org1, peers:[peer0, peer1],domain:example.com},
        # {name: org2, peers:[peer0, peer1],domain:example.com}]
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
            self.compose_file_path + "scripts:/tmp/scripts",
            self.compose_file_path + self.cluster_id + ":/tmp",
            self.compose_file_path + self.cluster_id + "/crypto-config.yaml:/etc/hyperledger/fabric/crypto-config.yaml",
            self.compose_file_path + self.cluster_id + "/crypto-config:/etc/hyperledger/fabric/crypto-config",
            self.compose_file_path + self.cluster_id + "/configtx.yaml:/etc/hyperledger/fabric/configtx.yaml",
            # self.compose_file_path + self.cluster_id + "/channel-artifacts:/tmp/channel-artifacts",
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
            'CTL_COMPARE_URL=http://127.0.0.1:7059/configtxlator/compute/update-from-configs',
            "ORDERER_TLS_CA=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/orderers/"
            "orderer.{}/msp/tlscacerts/tlsca.{}-cert.pem".format(orderer_domain, orderer_domain, orderer_domain),
            "ORDERER_MSP=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/orderers/orderer.{}/msp".format(
                orderer_domain, orderer_domain),
            "ORDERER_TLS_ROOTCERT=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/orderers/orderer.{}/"
            "tls/ca.crt".format(orderer_domain, orderer_domain),
            "ORDERER_ADMIN_MSP=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/users/Admin@{}/msp".format(
                orderer_domain, orderer_domain),
            "ORDERER_URL=orderer.{}:7050".format(orderer_domain),
            'ORDERER_GENESIS=orderer.genesis.block',
        ]

        depends_on = []
        org_list = []
        for org in orgs:
            # org should be dict as like org:[peer0,peer1]
            org_name = org.get('name')
            peers = org.get('peers')
            domain = org.get('domain')
            for peer in peers:
                org_peer_name = '{}_{}'.format(org_name.upper(), peer.upper())
                org_peer_service = '{}.{}.{}'.format(peer, org_name, domain)
                depends_on.append(org_peer_service)
                environment.append("{}_TLS_ROOTCERT=/etc/hyperledger/fabric/crypto-config/peerOrganizations/"
                                   "{}.{}/peers/{}/tls/ca.crt".format(org_peer_name, org_name, domain,
                                                                      org_peer_service))
                environment.append("{}_URL={}:7051".format(org_peer_name, org_peer_service))
            environment.append('{}={}'.format(org_name.upper(), ','.join(peers)))
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
        channel_list = [channel]
        environment.append('{}_CREATE_ORG=org1'.format(channel.upper()))
        environment.append('{}_CREATE_PEER=peer0'.format(channel.upper()))
        environment.append('{}_ORGS={}'.format(channel.upper(), ','.join(org_list)))
        environment.append('APP_CHANNELS={}'.format(','.join(channel_list)))

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

    def generate_add_org_cli(self, orderer_domain, channel, orgs, new_org):
        service_name = 'add_org_cli'
        image = self.images.get('cli_image')
        container_name = "{}_add_org_cli".format(self.cluster_id)
        command = "bash -c 'sleep 5; cd /tmp && " \
                  "bash scripts/add_org.sh && " \
                  "bash scripts/new_org_join.sh &&" \
                  "curl http://120.27.22.25:8083/container?id={}&org={} && " \
                  "while true; do sleep 20180101; done'".format(self.cluster.id, new_org['name'])
        tty = True
        volumes = [
            self.compose_file_path + "scripts:/tmp/scripts",
            self.compose_file_path + self.cluster_id + ":/tmp",
            self.compose_file_path + self.cluster_id + "/crypto-config.yaml:/etc/hyperledger/fabric/crypto-config.yaml",
            self.compose_file_path + self.cluster_id + "/crypto-config:/etc/hyperledger/fabric/crypto-config",
            self.compose_file_path + self.cluster_id + "/configtx.yaml:/etc/hyperledger/fabric/configtx.yaml",
            # self.compose_file_path + self.cluster_id + "/channel-artifacts:/tmp/channel-artifacts",
        ]
        working_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"
        hostname = "{}_add_org_cli".format(self.cluster.id)
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
            'ORGS={}'.format(','.join(orgs.keys())),
            'NEW_ORG={}'.format(new_org['name']),
            'NEW_ORG_PEERS={}'.format(','.join(new_org['peers'])),
            'NEW_ORG_DOMAIN={}'.format(new_org['domain']),
            'ORDERER_ORG=Orderer',
            'ORDERER_DOMAIN={}'.format(orderer_domain),
            'ORDERER_CA=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/{}/orderers/'
            'orderer.{}/msp/tlscacerts/tlsca.{}-cert.pem'.format(orderer_domain, orderer_domain, orderer_domain)
        ]
        for k, v in orgs.items():
            environment.append('{}_DOMAIN={}'.format(k.upper(), v))
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
                    hostname=hostname
                ).get_data()
        }
