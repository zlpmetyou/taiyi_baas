import os

import requests
import json
import logging
import tarfile

from requests_toolbelt import MultipartEncoder
from common import log_handler, LOG_LEVEL
from common.utils import FABRIC_TOKEN_API_PATH,ADD_USER_API

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


def convert_data(f):
    def wrapper(body):
        json_data = json.dumps(body)
        result = f(json_data)
        obj_data = json.loads(result)
        return obj_data
    return wrapper

#
# class GetToken(object):
#     def __init__(self, api):
#         self.api = api
#
#     @convert_data
#     def get_token(self, body):
#         response = requests.post(self.api, body)
#         return response
#
#
# class SendClusterConfig(object):
#     def __init__(self, api, token):
#         self.api = api
#         self.token = token
#
#     @convert_data
#     def send_cluster_config(self, body):
#         headers = {
#             'content-type': 'application/json',
#             'token': self.token,
#         }
#         response = requests.post(self.api, body=body, headers=headers)
#         return response


def get_token(api, user):
    try:
        response = requests.post(api, json=user, verify=False)
    except Exception as e:
        logger.error(e)
        return False
    content = response.text
    obj_data = json.loads(content)
    token = obj_data.get('Token')
    return token


def make_tar_file(output_filename, source_dirs):
    with tarfile.open(output_filename, "w:gz") as tar:
        for source_dir in source_dirs:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
    return tar.name


def send_cluster_config(api, body, token, file_path, user_id):
    json_data = json.dumps(body)
    data = MultipartEncoder(
        fields={
            'Body': json_data,
            'Files': (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')
        }
    )
    headers = {
        'Content-type': data.content_type,
        'Private-Header': 'token={};userId={}'.format(token, user_id),
    }

    try:
        response = requests.post(api, data=data, headers=headers, verify=False)
    except Exception as e:
        logger.error(e)
        return False
    content = response.text
    logger.info('content:' + content)
    obj_data = json.loads(content)
    return obj_data


def send_new_user_info(user_id, body, token_api=FABRIC_TOKEN_API_PATH, api=ADD_USER_API):
    user = {'UserId': user_id, "Passwd": "123456"}
    token = get_token(token_api, user)
    headers = {
        'Private-Header': 'token={};userId={}'.format(token, user_id),
    }
    try:
        response = requests.post(api, json=body, headers=headers, verify=False)
    except Exception as e:
        logger.error(e)
        return False
    content = response.text
    obj_data = json.loads(content)
    logger.info('add user,result:{}'.format(content))
    if int(obj_data.get('Code')) == 0:
        logger.info('success send')
        return obj_data
    else:
        return False


# class HandleRequest(object):
#
#     @classmethod
#     def get_token(cls):
#         pass
#     def __init__(self, url):
#         self.url = url
#
#     def get_token(self, api):
#         pass
#
#     def create_cluster(self):
#         pass
#
#     def delete_cluster(self):
#         pass
#
#     def add_user(self):
#         pass

# if __name__ == '__main__':
#     token = get_token('http://192.168.1.88:9001/baasServer/getToken',user={'UserId': '5bdab4b91d41c84f4c17301b', "Passwd": "123456"})
#     print(token)
# # if __name__ == '__main__':
#     body = {
#         "ChannelId": "mychannel",
#         "BlockchainSign": "zlp",
#         "BlockchainName": "zlp_fabric",
#         "Algorithm": "solo",
#         "CreateTime": "20181012144100",
#         "BlockChainCertPath": "XXX",
#         "Channels": [{
#             "ChannelId": "mychannel",
#             "ChannelConfigName": "mychannel.tx",
#             "Orgs": [{
#                 "OrgId": "org1",
#                 "Peers": [
#                     "peer0.org1.example.com",
#                     "peer1.org1.example.com"
#                 ]
#             }],
#             "Orderers": [
#                 "orderer.example.com"
#             ]
#         }],
#         "Orgs": [{
#                 "Name": "org1",
#                 "Type": "peer",
#                 "Domain": "example.com",
#                 "MspId": "Org1MSP",
#                 "Peers": [{
#                         "Name": "peer0.org1.example.com",
#                         "Url": "grpc://172.30.0.3:7051",
#                         "EventUrl": "grpc://172.30.0.3:7053"
#                     },
#                     {
#                         "Name": "peer1.org1.example.com",
#                         "Url": "grpc://172.30.0.8:7051",
#                         "EventUrl": "grpc://172.30.0.8:7053"
#                     }
#                 ],
#                 "Cas": [{
#                     "Name": "ca.org1.example.com",
#                     "Url": "http://172.30.0.6:7054",
#                     "EnrollId": "admin",
#                     "EnrollSecret": "adminpw",
#                     "ContainerName": "ca-org1"
#                 }]
#             },
#             {
#                 "Name": "ordererorg",
#                 "Type": "orderer",
#                 "Domain": "example.com",
#                 "MspId": "OrdererOrg",
#                 "Orderers": [{
#                     "Name": "orderer.example.com",
#                     "Url": "grpc://172.30.0.7:7050"
#                 }]
#             }
#         ]
#     }
#     token = get_token('http://192.168.1.88:9001/baasServer/getToken',{"UserId": "haifeng", "Passwd": "123456"})
#     result = send_cluster_config('http://192.168.1.88:9003/baasServer/blockchainManager/modifyBlockChainConfig',body=body,token=token)
#     print(token)
#     print(result)