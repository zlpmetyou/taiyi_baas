import logging
import os
import shutil

from common import log_handler, LOG_LEVEL, CRYPTO_GEN_TOOL, CONFIG_TX_GEN_TOOL

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


class CertificateGenerator(object):

    def __init__(self, path):
        self.tool = CRYPTO_GEN_TOOL
        self.path = path

    def generate_certificate(self, file='crypto-config.yaml', target_dir=None):

        if target_dir:
            output = os.path.join(self.path, target_dir)
            result = os.system(self.tool + ' generate --config={} --output={}'.format(file, output))
        else:
            source_path = os.getcwd()
            os.chdir(self.path)
            # if os.path.exists('crypto-config'):
            #     shutil.rmtree('crypto-config')

            result = os.system(self.tool + ' generate --config=./{}'.format(file))
            os.chdir(source_path)

        if result == 0:
            logger.info('create crypto-config-dir with crypto-config.yaml success')
            return True
        else:
            logger.info('create crypto-config-dir with crypto-config.yaml failed')
            return False


class TxGenerator(object):

    def __init__(self, path, file='configtx.yaml'):
        self.tool = CONFIG_TX_GEN_TOOL
        self.file = file
        self.path = path
        self.target_dir = 'channel-artifacts'

    def generate_channel_tx(self, channel):
        logger.info('file:' + self.file)
        # make the output dir
        output = os.path.join(self.path, self.target_dir)

        if not os.path.exists(output):
            os.mkdir(output)

        source_path = os.getcwd()

        os.chdir(self.path)
        command = self.tool + ' -profile {} -outputCreateChannelTx ' .format(channel) + self.target_dir +\
                  '/{}.tx -channelID {}'.format(channel, channel)
        logging.info('command:'+ command)
        result = os.system(command)
        os.chdir(source_path)
        if result == 0:
            logger.info('create {}.tx with configtx.yaml success'.format(channel))
            return True
        else:
            logger.info('create {}_.tx with configtx.yaml failed'.format(channel))
            return False

    def generate_genesis_block(self):
        logger.info('file:' + self.file)
        # make the output dir
        output = os.path.join(self.path, self.target_dir)
        if not os.path.exists(output):
            os.mkdir(output)

        source_path = os.getcwd()

        os.chdir(self.path)
        profile_name = 'OrdererGenesis'
        command = self.tool + ' -profile ' + profile_name + ' --outputBlock ' + \
            self.target_dir + '/orderer.genesis.block'
        logger.info('command:' + command)
        result = os.system(command)
        os.chdir(source_path)

        if result == 0:
            logger.info('create genesis_block with configtx.yaml success')
            return True
        else:
            logger.info('create genesis_block with configtx.yaml failed')
            return False

    def generate_json(self, org):
        source_path = os.getcwd()

        os.chdir(self.path)

        org_msp_name = '{}MSP'.format(org.capitalize())
        result = os.system(self.tool +
                           ' -printOrg {} -profile {}/configtx.yaml > channel-artifacts/{}.json'
                           .format(org_msp_name, self.path, org))
        os.chdir(source_path)
        if result == 0:
            logger.info('create {}.json with configtx.yaml success'.format(org))
            return True
        else:
            logger.info('create {}.json with configtx.yaml failed'.format(org))
            return False


class FilesGenerator(object):

    def __init__(self, path):
        self.cert_generator = CertificateGenerator(path)
        self.tx_generator = TxGenerator(path)

    def generate_create_file(self, channel):
        self.cert_generator.generate_certificate()
        self.tx_generator.generate_channel_tx(channel)
        self.tx_generator.generate_genesis_block()

    def generate_new_org_cert(self, org):
        file_name = 'crypto-config-{}.yaml'.format(org)
        self.cert_generator.generate_certificate(file_name)

    def generate_new_org_json(self,org):
        self.tx_generator.generate_json(org)
