
# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import datetime

import logging
from mongoengine import Document, StringField, \
    BooleanField, DateTimeField, IntField, ObjectIdField,\
    ReferenceField, DictField, ListField, CASCADE, PULL
from enum import Enum
from marshmallow import Schema, fields
from .user import User
from common import BLOCK_CHAIN_PROBATION_PERIOD


logger = logging.getLogger(__name__)

LOG_LEVEL = Enum("LOG_LEVEL", ("INFO", "DEBUG", "NOTICE", "WARNING", "ERROR", "CRITICAL"))

CLUSTER_STATE = Enum("CLUSTER_STATE", ("active", "released"))
CLUSTER_STATUS = Enum("CLUSTER_STATUS", ("running", "stopped"))


class Host(Document):
    id = StringField(default="", primary_key=True)
    name = StringField(default="")
    worker_api = StringField(default="")
    create_ts = DateTimeField(default=datetime.datetime.now)
    status = StringField(default="active")
    host_type = StringField(default="")
    log_level = StringField(default=LOG_LEVEL.INFO.name)
    log_type = StringField(default="")
    log_server = StringField(default="")
    autofill = BooleanField(default=False)
    schedulable = BooleanField(default=False)
    capacity = IntField(default=0)
    clusters = ListField(default=[])
    vcparam = DictField(default={})
    k8s_param = DictField(default={})
    port_used = ListField(IntField())
    # users = ListField(default=[])


class Cluster(Document):
    id = StringField(default="", primary_key=True)
    name = StringField(default="")
    network_type = StringField(default="")
    ports = ListField(default={})
    service_url = DictField(default={})
    containers = DictField(default={})
    health = StringField(default="")
    domain = StringField(default='')
    create_ts = DateTimeField(default=datetime.datetime.now)
    due_time = DateTimeField(default=datetime.datetime.now()+datetime.timedelta(days=BLOCK_CHAIN_PROBATION_PERIOD))
    status = StringField(default=CLUSTER_STATUS.running.name)
    host = ReferenceField(Host, reverse_delete_rule=CASCADE)
    env = DictField(default={})
    consensus_plugin = StringField(default="")
    user = ReferenceField(User, reverse_delete_rule=CASCADE)


class Org(Document):
    name = StringField()
    alias = StringField()
    domain = StringField(default='')
    org_type = StringField()
    users = ListField(ReferenceField(User, reverse_delete_rule=PULL))
    cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)


class Node(Document):
    name = StringField()
    alias = StringField()
    node_type = StringField()
    ip = StringField()
    ports = DictField()
    org = ReferenceField(Org, reverse_delete_rule=CASCADE)


class Channel(Document):
    name = StringField()
    alias = StringField()
    cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)
    orderers = ListField(ReferenceField(Node, reverse_delete_rule=PULL))
    orgs = ListField(ReferenceField(Org, reverse_delete_rule=PULL))


class Container(Document):
    id = StringField(default="", primary_key=True)
    name = StringField(default="")
    cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)


class ServicePort(Document):
    port = IntField(default=0)
    ip = StringField(default="")
    name = StringField(default="")
    cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)


class PeerOrg(Document):
    name = StringField()
    alias = StringField()
    domain = StringField(default='')
    # peers = ListField(default=[])
    ca = StringField(default='ca')
    channels = ListField(default=[])
    users = ListField(default=[])
    cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)


class Peer(Document):
    name = StringField()
    alias = StringField()
    # container = ReferenceField()
    org = ReferenceField(PeerOrg, reverse_delete_rule=CASCADE)
    # port = StringField()


class OrdererOrg(Document):
    name = StringField()
    domain = StringField(default='')
    ca = StringField(default='ca')
    cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)


class Orderer(Document):
    name = StringField()
    channels = ListField(default=[])
    org = ReferenceField(OrdererOrg, reverse_delete_rule=CASCADE)


class ClusterConfig(Document):
    name = StringField(default="")
    peer = IntField(default=2)
    orderer = IntField(default=1)
    ca = IntField(default=1)


class ClusterSchema(Schema):
    id = fields.Str()
    name = fields.String()
    duration = fields.Number()
    network_type = fields.String()
    mapped_ports = fields.Dict()
    service_url = fields.Dict()
    # containers = fields.Dict()
    size = fields.Integer()
    release_ts = fields.DateTime()
    health = fields.String()
    create_ts = fields.DateTime()
    apply_ts = fields.DateTime()
    worker_api = fields.String()
    status = fields.String()
    state = fields.String()
    host = fields.Method("get_host_name")
    host_id = fields.Method("get_host_id")
    user_id = fields.String()
    api_url = fields.String()
    consensus_plugin = fields.String()
    containers = fields.Method("get_containers")
    service_ports = fields.Method("get_service_ports")
    config = fields.Dict()

    def get_host_name(self, cluster):
        return cluster.host.name

    def get_host_id(self, cluster):
        return str(cluster.host.id)

    def format_create_ts(self, cluster):
        return cluster.create_ts.strftime("%a, %d %b %Y %H:%M:%S")

    def format_apply_ts(self, cluster):
        return cluster.apply_ts.strftime("%a, %d %b %Y %H:%M:%S")

    def get_containers(self, cluster):
        return [container.name for container in
                Container.objects(cluster=cluster)]

    def get_service_ports(self, cluster):
        return [service_port.port for service_port
                in ServicePort.objects(cluster=cluster).order_by('port')]


class HostSchema(Schema):
    id = fields.String()
    name = fields.String()
    worker_api = fields.String()
    create_ts = fields.Method("format_create_ts", dump_only=True)
    status = fields.String()
    host_type = fields.String()
    log_level = fields.String()
    log_type = fields.String()
    log_server = fields.String()
    autofill = fields.Method("format_autofill", dump_only=True)
    schedulable = fields.Method("format_schedulable", dump_only=True)
    clusters = fields.Method("get_clusters", dump_only=True)
    # users = fields.Method("get_users", dump_only=True)
    capacity = fields.Integer()

    @staticmethod
    def format_autofill(host):
        return "true" if host.autofill else "false"

    @staticmethod
    def format_create_ts(host):
        return host.create_ts.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_schedulable(host):
        return "true" if host.schedulable else "false"

    # @staticmethod
    # def get_users(host):
    #     from . import User
    #     users = User.objects(host=host)
    #
    #     return [str(user.id) for user in users]

    @staticmethod
    def get_clusters(host):
        clusters = Cluster.objects(host=host)

        return [str(cluster.id) for cluster in clusters]


