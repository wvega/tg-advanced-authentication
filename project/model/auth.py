# -*- coding: utf-8 -*-

"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

It's perfectly fine to re-use this definition in the frik application,
though.

"""

import os
import sys

try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\n'
             'If you are on python2.4 this library is not part of python. '
             'Please install it. Example: easy_install hashlib')

from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, synonym

from project.model import DeclarativeBase, metadata, DBSession

__all__ = ['User', 'Group', 'Permission']

#
# Association tables
#

# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
group_permission_table = Table('GroupPermissions', metadata,
    Column('group_id', Integer, ForeignKey('Groups.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Integer, ForeignKey('Permissions.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
user_group_table = Table('UserGroups', metadata,
    Column('user_id', Integer, ForeignKey('Users.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('Groups.id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

#
# *The auth* model itself
#

class Group(DeclarativeBase):
    """
    Group definition for :mod:`repoze.what`.

    Only the ``group_name`` column is required by :mod:`repoze.what`.

    """

    __tablename__ = 'Groups'

    # columns

    id = Column(Integer, autoincrement=True, primary_key=True)
    slug = Column(Unicode(16), unique=True, nullable=False)
    name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)

    # relations

    users = relation('User', secondary=user_group_table, backref='groups')

    # special methods

    def __repr__(self):
        return '<Group: name=%r>' % self.group_name

    def __unicode__(self):
        return self.group_name

# The 'info' argument we're passing to the email_address and password columns
# contain metadata that Rum (http://python-rum.org/) can use generate an
# admin interface for your models.
class User(DeclarativeBase):
    """
    User definition.

    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.

    """
    __tablename__ = 'Users'

    # columns

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255))
    _email = Column(Unicode(255), unique=True, info={'rum': {'field':'Email'}})
    _password = Column('password', Unicode(80), info={'rum': {'field':'Password'}})
    picture = Column(Unicode(255))

    fbid = Column(Integer, unique=True)
    twid = Column(Integer, unique=True)

    twitter_key = Column(Unicode(100), unique=True)
    twitter_secret = Column(Unicode(100), unique=True)

    created = Column(DateTime, default=datetime.now)

    # email and user_name properties
    def _get_email(self):
        return self._email

    def _set_email(self, email):
        self._email = email.lower()

    email = synonym('_email', descriptor=property(_get_email, _set_email))

    # password property
    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        # Make sure password is a str because we cannot hash unicode objects
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password + salt.hexdigest())
        password = salt.hexdigest() + hash.hexdigest()
        # Make sure the hashed password is a unicode object at the end of the
        # process because SQLAlchemy _wants_ unicode objects for Unicode cols
        if not isinstance(password, unicode):
            password = password.decode('utf-8')
        self._password = password

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password))

    # class methods

    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return DBSession.query(cls).filter(cls.email == email).first()

#    @classmethod
#    def by_user_name(cls, username):
#        """Return the user object whose user name is ``username``."""
#        return DBSession.query(cls).filter(cls.user_name == username).first()

    # non-column properties

    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    # other methods

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """
        hash = sha1()
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        hash.update(password + str(self.password[:40]))
        return self.password[40:] == hash.hexdigest()

    # special methods

    def __repr__(self):
        return '<User: name=%r, email=%r>' % (self.name, self.email)

    def __unicode__(self):
        return self.name

class Permission(DeclarativeBase):
    """
    Permission definition for :mod:`repoze.what`.

    Only the ``permission_name`` column is required by :mod:`repoze.what`.

    """

    __tablename__ = 'Permissions'

    # columns

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(63), unique=True, nullable=False)
    description = Column(Unicode(255))

    # relations

    groups = relation(Group, secondary=group_permission_table, backref='permissions')

    # special methods

    def __repr__(self):
        return '<Permission: name=%r>' % self.permission_name

    def __unicode__(self):
        return self.permission_name