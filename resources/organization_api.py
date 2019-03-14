from flask import Blueprint
from flask_restful import Api

from .organization import OrganizationView
from .users import OrgUser

bp_organization_api = Blueprint('bp_organization_api', __name__, url_prefix='/{}'.format('v0'))
organization_api = Api(bp_organization_api)
organization_api.add_resource(OrganizationView, '/org')
organization_api.add_resource(OrgUser, '/org/user')
