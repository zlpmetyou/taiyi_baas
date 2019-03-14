CA_IMAGE = 'hyperledger/fabric-ca:{}'
CA_ENVIRONMENT = [
    'FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server',
    'FABRIC_CA_SERVER_CA_NAME=ca-org1',
    'FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org1.example.com-cert.pem',
    'FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/ca_sk',
    'FABRIC_CA_SERVER_TLS_ENABLED=true',
    'FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org1.example.com-cert.pem',
    'FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/ca_sk',
]
CA_CONTAINER_NAME = '${COMPOSE_PROJECT_NAME}_ca_org1'
CA_PORTS = ['${CA_ORG1_ECAP_PORT}:7054']
CA_VOLUMES = ['${COMPOSE_PROJECT_PATH}/crypto-config/peerOrganizations/org1.example.com/ca/:/etc/hyperledger/fabric-ca-server-config']
CA_COMMAND = "sh -c 'fabric-ca-server start -b admin:adminpw -d'"

CA_CONTAINER = {
    '{}': {
        'image': CA_IMAGE,
        'container_name': CA_CONTAINER_NAME,
        'environment': CA_ENVIRONMENT,
        'ports': CA_PORTS,
        'volumes': CA_VOLUMES,
        'command': CA_COMMAND
    }
}

# class CA(object):
#
#     def __init__(self, name, container_name, ports, volumes, command,
#                  image=CA_IMAGE, environment=CA_ENVIRONMENT):
#         self.name = name
#         self.image = image
#         self.container_name = container_name
#         self.environment = environment
#         self.ports = ports
#         self.volumes = volumes
#         self.command = command
