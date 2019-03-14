import logging

from flask import Blueprint, request
from common import log_handler, LOG_LEVEL
from modules.models import Cluster as ClusterModel
from config_files.generate_config_files import GenerateChainBlockConfig
from common import BLOCKCHAIN_CONFIG_FILES_PATH
from tasks import send_cluster_info

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

bp_container_api = Blueprint('bp_container_api', __name__)


# 次功能需要基于gunicorn多进程,讲数据库更新为running，从而让创建进程根据数据库状态继续执行或者删除等操作
@bp_container_api.route('/container', methods=['GET', 'POST'])
def listen_container_message():
    hostname = request.args.get('id')
    logger.info('hostname:{}'.format(hostname))
    # cluster_id = hostname
    try:
        cluster = ClusterModel.objects.get(id=hostname)
        cluster.update(status='running')

    except Exception as e:
        logger.error(e)

    # config_path = BLOCKCHAIN_CONFIG_FILES_PATH
    # cluster_info = GenerateChainBlockConfig(cluster, config_file_path=config_path).generate_chaincode_config()
    # # 发送5次
    # pos = 0
    # while pos <= 5:
    #     result = send_cluster_info(config_path=config_path, cid=cluster_id, cluster_info=cluster_info, user_id=str(cluster.user.id))
    #     if result:
    #         break
    #     else:
    #         pos += 1
    # print(result)

    return 'ok'


