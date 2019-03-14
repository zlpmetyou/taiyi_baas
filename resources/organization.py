import logging
import sys
import os

from flask_login import login_required, utils
from flask_restful import Resource, reqparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common import log_handler, LOG_LEVEL, make_ok_resp, make_fail_resp
from modules.models.host import Org as OrgModel
from modules.models import Cluster as ClusterModel
from modules import OrganizationHandler

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


org_create_parser = reqparse.RequestParser()
org_create_parser.add_argument('name', help='org name')
org_create_parser.add_argument('domain', help='org domain')
# org_create_parser.add_argument('peers', action='append', help='peers of org')
org_create_parser.add_argument('peers', help='peers of org')
# org_create_parser.add_argument('ca', help='org ca name')
org_create_parser.add_argument('cluster_id', help='cluster_id of org')


class OrganizationView(Resource):

    @login_required
    def post(self):
        user = utils._get_user()
        user = user.dbUser
        user_id = str(user.id)
        args = org_create_parser.parse_args()
        org_name = args.get('name')
        org_domain = args.get('domain')
        org_ca = args.get('ca', 'ca')
        org_peers = args.get('peers')
        org_cluster_id = args.get('cluster_id')

        if not all([org_name, org_domain, org_ca, org_peers, org_cluster_id]):
            return make_fail_resp(error='参数错误')

        cluster = ClusterModel.objects.get(id=org_cluster_id)
        if not cluster:
            return make_fail_resp(error='链不存在')

        orgs = OrgModel.objects(cluster=cluster, org_type='peer')
        if len(orgs) >= 5:
            return make_fail_resp(error='组织数量已达上限')
        for org in orgs:
            if org.name == org_name:
        # if OrgModel.objects(cluster=cluster, org_type='peer', name=org_name):
                return make_fail_resp(error='组织名重复')

        if OrganizationHandler().create(name=org_name, domain=org_domain,
                                        ca=org_ca, peers=org_peers, cluster=cluster, user=user_id):
            logger.debug("org creation successful")
            return make_ok_resp()
        else:
            logger.debug("org creation failed")
            return make_fail_resp(error="Failed to create org {}".
                                  format(org_name))
