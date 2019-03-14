
# class OrdererOrg(object):
#
#     def __init__(self, orderer_org):
#         self.domain = orderer_org.get('domain','example.com')
#         self.orderers = orderer_org.get('orderers',['orderer']),
#         self.consensus_plugin = orderer_org.get('consensus_plugin','solo')
#
#     def output_
import json


class HandleCluster(object):

    def __init__(self, cluster):
        self.cluster = cluster

    def generate_orderer_org_info(self):

        if hasattr(self.cluster, 'orderer_org'):
            orderer_org = self.cluster.orderer_org
            if not isinstance(dict, orderer_org):
                orderer_org = json.loads(orderer_org)
                domain = orderer_org.get('domain', 'example.com')
                orderers = orderer_org.get('orderers', ['orderer']),
                consensus_plugin = orderer_org.get('consensus_plugin', 'solo')

        elif hasattr(self.cluster,'consensus_plugin') and hasattr(self.cluster,'orderers'):
            orderer_org = {

            }
        # if isinstance(dict,orderer_org) and
            # attributes =

    # def generate_orderer_org_info(self):

    # def generate_orderer_org_info(self):

    # def generate_orderer_org_info(self):

    def handle_org_info(self):
        if not hasattr(self.cluster, 'orderer_rog') and hasattr(self.cluster, 'consensus_plugin'):
            pass

    def output_cluster_info_to_go(self):
        pass

    def generate_org_structure(self):
        pass


if __name__ == '__main__':
    class Cluster(object):

        def __init__(self):
            self.name = '测试'
            self.net_work = 'fabric-1.1'
            # self.cas = ['ca1', 'ca2']
            self.orderer_org = {
                'orderers': ['orderer'],
                'consensus_plugin': 'solo',
                'domain': 'ali.com'
            }
            self.peer_orgs = [
                {
                    'name': 'org1',
                    'ca': 'ca',
                    'orderer': 'orderer',
                    'peer': 4,
                    'domain': 'tencent.com'
                },
                {
                    'name': 'org2',
                    'ca': 'ca',
                    'orderer': 'orderer',
                    'peer': 4,
                    'domain': 'baidu.com'
                }
            ]
            self.channels = [
                {
                    'name': 'channel1',
                    'orderer': [
                        'orderer'
                    ],
                    'orgs': [
                        'org1', 'org2'
                    ]
                }
            ]


    cluster = Cluster()
    print(cluster.__dict__)
