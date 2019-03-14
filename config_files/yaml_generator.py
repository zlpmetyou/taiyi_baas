import logging
import os
import yaml

from common import log_handler, LOG_LEVEL, BLOCKCHAIN_CONFIG_FILES_PATH

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


def generate_yaml_file(config, file_name, target_path):
    logger.info('create {} output into {}'.format(file_name, target_path))
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    target_file = os.path.join(target_path, file_name)
    with open(target_file, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    if os.path.exists(target_file):
        logger.info('create {} success'.format(file_name))
        return True
    else:
        logger.info('create {} failed'.format(file_name))
        return False


class YamlGenerator(object):

    def __init__(self, cluster_id, target_path=BLOCKCHAIN_CONFIG_FILES_PATH):
        self.cluster_id = cluster_id
        self.output_path = os.path.join(target_path, cluster_id)

    def generate_crypto_yaml(self, config):
        file_name = 'crypto-config.yaml'
        result = generate_yaml_file(config, file_name, self.output_path)
        return result

    def generate_tx_yaml(self, config):
        file_name = 'configtx.yaml'
        result = generate_yaml_file(config, file_name, self.output_path)
        return result

    def generate_new_org_yaml(self, org, config):
        file_name = 'crypto-config-{}.yaml'.format(org)
        result = generate_yaml_file(config, file_name, self.output_path)
        return file_name

    def generate_compose_file(self, config):
        file_name = '{}.yaml'.format(self.cluster_id)
        result = generate_yaml_file(config, file_name, self.output_path)
        return file_name

    def generate_add_org_compose_file(self, config, org):
        file_name = '{}-add-{}.yaml'.format(self.cluster_id, org)
        result = generate_yaml_file(config, file_name, self.output_path)
        return file_name


class ClusterYamlGenerator(object):
    def __init__(self, cluster):
        self.generator = YamlGenerator(cluster.id)

    def generate_create_yaml(self, crypto_config, tx_config):
        # 加个判断，跑出异常
        generate_crypto_config = self.generator.generate_crypto_yaml(crypto_config)
        generate_tx = self.generator.generate_tx_yaml(tx_config)

    def generate_add_org_yaml(self, crypto_config, org_name):
        self.generator.generate_new_org_yaml(org_name, crypto_config)

    def generate_compose_yaml(self, service_config):
        generate_service = self.generator.generate_compose_file(service_config)
        return generate_service

    def generate_new_org_compose_file(self, service_config, org_name):
        compose_file = self.generator.generate_add_org_compose_file(service_config, org_name)
        if compose_file:
            return compose_file
        else:
            return None

    def generate_tx_yaml(self, tx_config):
        self.generator.generate_tx_yaml(tx_config)
