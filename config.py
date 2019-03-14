
# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import os
import bcrypt


class Config(object):
    DEBUG = False
    SECRET_KEY = '?\xbf,\xb4\x8d\xa3"<\x9c\xb0@\x0f5\xab,w\xee\x8d$0\x13\x8b83'
    VERSION = 'v0'


class ProductionConfig(Config):
    DEBUG = False
    MONGODB_HOST = os.getenv('MONGODB_HOST', '120.27.22.25')
    MONGODB_DB = os.getenv('MONGODB_DB', 'dev')
    MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', '')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')
    CHAIN_CODE_HOST = os.getenv('CHAIN_CODE_HOST', '120.27.22.25')
    BLOCK_CHAIN_CONFIG_PATH = os.getenv('BLOCK_CHAIN_CONFIG_PATH', '/app/config_files')


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_HOST = os.getenv('MONGODB_HOST', '120.27.22.25')
    MONGODB_DB = os.getenv('MONGODB_DB', 'dev')
    MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', '')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')
    CHAIN_CODE_HOST = os.getenv('CHAIN_CODE_HOST', '120.27.22.25')
    BLOCK_CHAIN_CONFIG_PATH = os.getenv('BLOCK_CHAIN_CONFIG_PATH', '/app/config_files')

