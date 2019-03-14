import sys
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from flask_login import UserMixin, AnonymousUserMixin
from modules.models import User as UserModel
from modules.models import LoginHistory, Profile
from common import log_handler, LOG_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)


class User(UserMixin):
    """
    User object that runs through the service
    """

    def __init__(self, username=None, password='123456', active=True, role=1,
                 is_admin=False, email=None, id=None, balance=0, apply_stat=0,
                 company='', department=None, mobile=None, reason=None):
        """
        Initialize a user object
        :param username: username of this user
        :param password: password of this user
        :param active: whether user is active
        :param is_admin: whether user is admin
        :param role: role of this user
        :param id: db id of this user
        :param balance: blue point of this user
        """
        self.username = username
        self.password = password
        self.active = active
        self.isAdmin = is_admin
        self.apply_stat = 0
        self.role = role
        self.id = id
        # self.profile = None
        self.dbUser = None
        # self.balance = balance
        self.apply_stat = apply_stat
        self.email = email
        self.company = company
        self.department = department
        self.mobile = mobile
        self.reason = reason
        self.password = password

    @staticmethod
    def set_password(password):
        return generate_password_hash(password)

    @staticmethod
    def check_password(hash_password, password):
        return check_password_hash(hash_password, password)

    def is_active(self):
        """
        Get whether user is active
        :return: True or False
        """
        return self.active

    def is_admin(self):
        """
        Get whether user is admin
        :return: True or False
        """
        return self.isAdmin

    @property
    def user_role(self):
        """
        Get user role
        :return: ADMIN/OPERATOR/COMMON_USER
        """
        return self.role

    def save(self):
        """
        Create new user
        :return: id of new user
        """
        hash_password = generate_password_hash(self.password)
        new_user = UserModel(username=self.username,
                             password=hash_password,
                             company=self.company,
                             department=self.department,
                             mobile=self.mobile,
                             active=self.active,
                             apply_stat=self.apply_stat,
                             email=self.email,
                             role=self.role,
                             isAdmin=self.isAdmin,
                             reason=self.reason
                             )
        new_user.save()
        self.id = str(new_user.id)
        self.dbUser = new_user
        return self.id

    def get_by_username(self, username):
        """
        Get user by username
        :param username: the name of user to query
        :return: User object
        """
        try:
            db_user = UserModel.objects.get(username=username)

            if db_user:
                self.username = db_user.username
                self.active = db_user.active
                self.password = db_user.password
                self.id = db_user.id
                self.isAdmin = db_user.isAdmin
                # self.balance = db_user.balance
                self.dbUser = db_user
                # self.role = db_user.role
                return self
            else:
                return None
        except Exception as exc:
            logger.error("get user exc %s", exc)
            return None

    def get_by_id(self, id):
        """
        Get user by user id
        :param id: id of user in db
        :return: User object
        """
        try:
            dbUser = UserModel.objects.get(id=id)
        except Exception:
            return None
        else:
            self.username = dbUser.username
            # self.password = dbUser.password
            self.mobile = dbUser.mobile
            self.company = dbUser.company
            self.department = dbUser.department
            self.isAdmin = dbUser.isAdmin
            self.active = dbUser.active
            self.apply_stat = dbUser.apply_stat

            self.id = dbUser.id
            # self.balance = dbUser.balance
            # self.profile = dbUser.profile
            self.dbUser = dbUser

            return self

    def get_by_mobile(self, mobile):
        """
        Get user by user's mobile
        :param mobile: mobile of user in db
        :return: user object
        """
        try:
            dbUser = UserModel.objects.get(mobile=mobile)
        except Exception as e:
            logger.error(e)
            return None
        self.username = dbUser.username
        self.password = dbUser.password
        self.active = dbUser.active
        self.isAdmin = dbUser.isAdmin
        # self.profile = dbUser.profile
        self.dbUser = dbUser
        self.id = dbUser.id

        return self

    def set_active(self, active):
        self.dbUser.update(set__active=active,
                           upsert=True)

    def update_password(self, password):
        try:
            self.dbUser.update(set__password=password,
                               upsert=True)
        except Exception as exc:
            logger.info("error {}".format(exc.message))

    def update_profile(self, name, email, bio, url, location):
        """
        Update user profile
        :param name: name to update
        :param email: email to update
        :param bio: bio to update
        :param url: url to update
        :param location: location to update
        """
        # if user has profile update else create new profile
        if self.profile:
            self.profile.update(set__name=name,
                                set__email=email,
                                set__bio=bio,
                                set__url=url,
                                set__location=location,
                                upsert=True)
        else:
            profile = Profile(name=name,
                              email=email,
                              bio=bio,
                              url=url,
                              location=location)
            profile.save()
            self.dbUser.profile = profile
            self.dbUser.save()

    @property
    def to_user_dict(self):
        resp_dict = {
            'id': str(self.dbUser.id),
            'username': self.dbUser.username,
            'mobile': self.dbUser.mobile,
            'company': self.dbUser.company,
            'department': self.dbUser.department,
            'active': self.dbUser.active,
            'apply_stat': self.dbUser.apply_stat,
            'isAdmin': self.dbUser.isAdmin,
            'role': self.dbUser.role
        }

        return resp_dict


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"

#
# if __name__ == '__main__':
#     user = User()
#     print(dir(user))
