import sys
import os
import datetime
from mongoengine import Document, StringField,\
    BooleanField, DateTimeField, IntField, \
    ReferenceField, ListField

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
# from .host import Host
ADMIN = 0
CLUSTER_USER = 1
ORG_ADMIN = 2
ORG_USER = 3

APPLYING = 0
APPLY_FAIL = -1
APPLY_SUCCESS = 1


class Profile(Document):
    """
    Profile model of User
    :member name: name of user
    :member email: email of user
    :member bio: bio of user
    :member organization: organization of user
    :member url: user's url
    :member location: user's location
    """
    name = StringField(default="")
    email = StringField(default="")
    bio = StringField(default="")
    organization = StringField(default="")
    url = StringField(default="")
    location = StringField(default="")
    company = StringField(required=True)
    department = StringField(default='')


class User(Document):
    """
    User model
    :member username: user's username
    :member password: user's password, save encrypted password
    :member active: whether user is active
    :member isAdmin: whether user is admin
    :member role: user's role
    :member timestamp: user's create time
    :member balance: user's balance
    :member profile: user's profile
    """
    username = StringField(required=True)
    password = StringField(default="")
    mobile = IntField(unique=True)
    email = StringField(default='')
    company = StringField(default='')
    department = StringField(default='')
    active = BooleanField(default=True)
    isAdmin = BooleanField(default=False)
    apply_stat = IntField(default=APPLYING)
    timestamp = DateTimeField(default=datetime.datetime.now)
    reason = StringField(default='')
    role = IntField(default=CLUSTER_USER)
    clusters = ListField(default=[])
    orgs = ListField(default=[])

    # role = IntField(default=COMMON_USER)
    # balance = IntField(default=0)
    # profile = ReferenceField(Profile)


class LoginHistory(Document):
    """
    User login history
    :member time: login time
    :member user: which user object
    """
    time = DateTimeField(default=datetime.datetime.now)
    user = ReferenceField(User)
