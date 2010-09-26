# coding: utf-8

"""Intended to work like a quick-started SQLAlchemy plugin"""

from repoze.what.middleware import AuthorizationMetadata
from repoze.what.plugins.pylonshq import booleanize_predicates
from repoze.what.plugins.sql import configure_sql_adapters
from repoze.who.plugins.sa import SQLAlchemyAuthenticatorPlugin
from repoze.who.plugins.sa import SQLAlchemyUserMDPlugin

from project.model import DBSession, User, Group, Permission

#
# authenticator plugin
#

authenticator = SQLAlchemyAuthenticatorPlugin(User, DBSession)
# users whoe log in using a regular form use their email address as username
authenticator.translations['user_name'] = 'email'

#
# metadata provider plugins
#

#
# From the documentation in repoze.what.plugins.sql.adapters package
#
# For developers to be able to use the names they want in their model, both the
# groups and permissions source adapters use a "translation table" for the
# field and table names involved:
#  * Group source adapter:
#    * "section_name" (default: "group_name"): The name of the table field that
#      contains the primary key in the groups table.
#    * "sections" (default: "groups"): The groups to which a given user belongs.
#    * "item_name" (default: "user_name"): The name of the table field that
#      contains the primary key in the users table.
#    * "items" (default: "users"): The users that belong to a given group.
#  * Permission source adapter:
#    * "section_name" (default: "permission_name"): The name of the table field
#      that contains the primary key in the permissions table.
#    * "sections" (default: "permissions"): The permissions granted to a given
#      group.
#    * "item_name" (default: "group_name"): The name of the table field that
#      contains the primary key in the groups table.
#    * "items" (default: "groups"): The groups that are granted a given
#      permission.
adapters = configure_sql_adapters(User, Group, Permission, DBSession,
                                  group_translations={'section_name': 'slug',
                                                      'item_name': 'email'},
                                  permission_translations={'section_name': 'name',
                                                           'item_name': 'slug'})

user = SQLAlchemyUserMDPlugin(User, DBSession)
# we get metadata based on user id, the only attribute an user is guranteed to
# have regardles the authentication method he/she uses (Form, Facebook, Twitter)
user.translations['user_name'] = 'email'

group = AuthorizationMetadata({'sqlauth': adapters['group']}, {'sqlauth': adapters['permission']})

# THIS IS CRITICALLY IMPORTANT!  Without this your site will
# consider every repoze.what predicate True!
booleanize_predicates()