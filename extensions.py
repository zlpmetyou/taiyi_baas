# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
from celery import Celery
import logging
import os

logger = logging.getLogger(__name__)
BROKER = os.environ.get("BROKER", "")
BACKEND = os.environ.get("BACKEND", "")

RABBITMQ_HOSTS = "localhost"

RABBITMQ_PORT = 5672

RABBITMQ_VHOST = '/'

RABBITMQ_USER = 'zlp'

RABBITMQ_PWD = 1

CELERY_IMPORTS = ('task',)

BROKER_URL = 'amqp://%s:%s@%s:%d/%s' % (RABBITMQ_USER, RABBITMQ_PWD, RABBITMQ_HOSTS, RABBITMQ_PORT, RABBITMQ_VHOST)

CELERY_TRACK_STARTED = True

CELERYD_CONCURRENCY = 4

CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_TASK_RESULT_EXPIRES = 60

CELERYD_HIJACK_ROOT_LOGGER = False

CELERY_DEFAULT_QUEUE = 'DEFAULT_QUEUE'


celery = Celery('cello-celery', broker=BROKER_URL, backend=BACKEND)
