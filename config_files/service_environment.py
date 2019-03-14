class Orderer:

    def __init__(self):
        self.ORDERER_GENERAL_LOGLEVEL = 'DEBUG',
        self.ORDERER_GENERAL_LISTENADDRESS = '0.0.0.0',
        self.ORDERER_GENERAL_GENESISMETHOD = 'file',
        self.ORDERER_GENERAL_GENESISFILE = '/var/hyperledger/orderer/orderer.genesis.block',
        self.ORDERER_GENERAL_LOCALMSPID = '{}MSP.format(str(org.id).capitalize())',
        self.ORDERER_GENERAL_LOCALMSPDIR = '/var/hyperledger/orderer/msp',
        self.ORDERER_GENERAL_TLS_ENABLED = 'false',
        self.ORDERER_GENERAL_TLS_PRIVATEKEY = '/var/hyperledger/orderer/tls/server.key',
        self.ORDERER_GENERAL_TLS_CERTIFICATE = '/var/hyperledger/orderer/tls/server.crt',
        self.ORDERER_GENERAL_TLS_ROOTCAS = ['/var/hyperledger/orderer/tls/ca.crt'],


