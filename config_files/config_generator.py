class CryptoGenerator(object):

    @staticmethod
    def generate_peer_org(org_name, domain, peers, ca, users=1):
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

    @staticmethod
    def generate_orderer_org(org_name, orderers, domain):
        content = {

            "Name": org_name.capitalize(),
            "Domain": domain,
            "Specs": [
                {
                    "Hostname": orderer
                }
                for orderer in orderers
            ]
        }
        return content


class TxGenerator(object):

    def __init__(self):
        self.capabilities = {
            'Application': {'V1_1': False},
            'Global': {'V1_1': True},
            'Orderer': {'V1_1': True}
        }

    @staticmethod
    def group_orderer_org_config(name, domain):
        content = {
            "Name": '{}MSP'.format(name.capitalize()),
            "MSPDir": "crypto-config/ordererOrganizations/{}/msp".format(domain),
            "ID": "{}MSP".format(name.capitalize())
        }
        return content

    @staticmethod
    def group_peer_org_config(name, domain):
        content = {
            "AnchorPeers": [
                {
                    "Port": 7051,
                    "Host": "peer0.{}.{}".format(name, domain)
                }
            ],
            "Name": "{}MSP".format(name.capitalize()),
            "MSPDir": "crypto-config/peerOrganizations/{}.{}/msp".format(name, domain),
            "ID": "{}MSP".format(name.capitalize())
        }
        return content

    @staticmethod
    def group_orderer_config(consensus_plugin, domain, orderers):
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

    def orderer_profile(self, orderer, orderer_org, peer_orgs):
        orderer_config = {}
        orderer_config.update(orderer)
        orderer_config.update({'Organizations': [orderer_org]})
        orderer_config.update({'Capabilities': self.capabilities['Orderer']})
        content = {
            'Capabilities': self.capabilities['Global'],
            'Orderer': orderer_config,
            'Consortiums': {
                'SampleConsortium': {
                    'Organizations': peer_orgs
                }
            }
        }
        return {'OrdererGenesis': content}

    def group_channel_config(self, channel, orgs):
        content = {
            'Consortium': 'SampleConsortium',
            'Application': {
                'Organizations': orgs,
                'Capabilities': self.capabilities['Application'],
                'Resources': {
                    'DefaultModPolicy': '/Channel/Application/Writers'
                }
            }
        }
        return {channel: content}

    def group_tx_config(self, orgs, orderer, profiles):

        applications = {'Organizations': None}
        organizations = orgs
        content = {
            'Organizations': organizations,
            'Orderer': orderer,
            'Application': applications,
            'Capabilities': self.capabilities,
            'Profiles': profiles
        }
        return content

    def generate_tx_config(self, orderer_org, orgs, consensus_plugin, channel):
        org_list = []
        orderer_org_name = orderer_org.get('name')
        orderer_org_domain = orderer_org.get('domain')
        orderers = orderer_org.get('orderers')
        orderer_org_config = self.group_orderer_org_config(orderer_org_name, orderer_org_domain)
        org_list.append(orderer_org_config)
        peer_orgs = []
        for org in orgs:
            org_name = org.get('name')
            org_domain = org.get('domain')
            peer_org_config = self.group_peer_org_config(org_name, org_domain)
            peer_orgs.append(peer_org_config)
            org_list.append(peer_org_config)
        orderer_default_config = self.group_orderer_config(consensus_plugin, orderer_org_domain, orderers)

        profiles = {}
        orderer_profile = self.orderer_profile(orderer_default_config, orderer_org_config, peer_orgs)
        channel_config = self.group_channel_config(channel, peer_orgs)
        profiles.update(orderer_profile)
        profiles.update(channel_config)
        content = self.group_tx_config(org_list, orderer_default_config, profiles)
        return content


class ConfigGenerator(object):
    def __init__(self):
        self.crypto_generator = CryptoGenerator()
        self.tx_generator = TxGenerator()

    def generate_crypto_config(self, orderer_org, orgs):
        peer_orgs = []
        for org in orgs:
            org_name = org.get('name')
            org_domain = org.get('domain')
            peers = org.get('peers')
            ca = org.get('ca')
            peer_org_config = self.crypto_generator.generate_peer_org(org_name,org_domain, peers, ca)
            peer_orgs.append(peer_org_config)
        orderer_org_name = orderer_org.get('name')
        orderer_org_domain = orderer_org.get('domain')
        orderers = orderer_org.get('orderers')
        orderer_org = self.crypto_generator.generate_orderer_org(orderer_org_name,orderers,orderer_org_domain)
        content = {
            'OrdererOrgs': [orderer_org],
            'PeerOrgs': peer_orgs
        }
        return content

    def generate_tx_config(self, orderer_org, orgs, consensus_plugin, channel):
        content = self.tx_generator.generate_tx_config(orderer_org, orgs, consensus_plugin, channel)
        return content


