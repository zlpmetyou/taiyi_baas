# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import logging
import sys
import os

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from modules import cluster_handler
from common.request_fabric_api import get_token, send_cluster_config
from common import FABRIC_SEND_CLUSTER_CONFIG_PATH, FABRIC_TOKEN_API_PATH, USER_ACCOUNT, DELETE_BLOCK_CHAIN_API_PATH
from common import log_handler, LOG_LEVEL, make_tar_file
from extensions import celery
from exceptions import ReleaseClusterException, DeleteClusterException, SendClusterException

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


# @celery.task(name="release_cluster", bind=True, default_retry_delay=5, max_retries=3)
def release_cluster(cluster_id):
    if cluster_handler.release_cluster(cluster_id):
        logger.info("release cluster {} successfully".format(cluster_id))
        return True
    # else:
    #     self.retry(exc=ReleaseClusterException)


# @celery.task(name="delete_cluster", bind=True, default_retry_delay=5, max_retries=3)
def delete_cluster(cluster_id, status):
    if status == "active":
        result = cluster_handler.delete(id=cluster_id)
    else:
        result = cluster_handler.delete_released(id=cluster_id)

    if result:
        return True
    #
    # self.retry(exc=DeleteClusterException)


# @celery.task(name="send_cluster_info", bind=True, default_retry_delay=5, max_retries=3)
def send_cluster_info(config_path, cid, cluster_info, user_id):
    user = {'UserId': user_id, "Passwd": "123456"}
    token = get_token(FABRIC_TOKEN_API_PATH, user)
    # print(token)
    cluster_config_path = config_path + os.sep + cid
    file_list = [
        cluster_config_path + os.sep + 'crypto-config',
        cluster_config_path + os.sep+'channel-artifacts'
    ]
    file_path = make_tar_file(cluster_config_path+os.sep+'{}.tar.gz'.format(cluster_info['BlockchainName']), file_list)
    result = send_cluster_config(FABRIC_SEND_CLUSTER_CONFIG_PATH, cluster_info, token, file_path=file_path,
                                 user_id=user_id)
    logger.info('send cluster info,result:{}'.format(result))
    if int(result.get('Code')) == 0:
        logger.info('success send')
        os.remove(cluster_config_path+os.sep+'{}.tar.gz'.format(cluster_info['BlockchainName']))
        return True
    # else:
    #     self.retry(exc=SendClusterException)


# @celery.task(name="send_delete_cluster", bind=True, default_retry_delay=5, max_retries=3)
def send_delete_cluster(body, user_id, api=DELETE_BLOCK_CHAIN_API_PATH, token_api=FABRIC_TOKEN_API_PATH):
    user = {'UserId': user_id, "Passwd": "123456"}

    token = get_token(token_api, user)
    # print(token)
    headers = {
        'Private-Header': 'token={};userId={}'.format(token, user_id),
    }
    # print(user.get('UserId'))
    try:
        response = requests.post(api, json=body, headers=headers, verify=False)
    except Exception as e:
        logger.error(e)
        return False
    content = response.text
    obj_data = json.loads(content)
    logger.info('delete cluster,result:{}'.format(content))
    if int(obj_data.get('Code')) == 0:
        logger.info('success send')
        return obj_data
    # else:
    #     self.retry(exc=SendClusterException)


if __name__ == '__main__':
    a = send_delete_cluster(body={'BlockchainSign': '111'})
    print(a)