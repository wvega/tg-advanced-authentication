# coding: utf-8

"""Intended to work like a quick-started SQLAlchemy plugin"""

import transaction

from repoze.what.middleware import AuthorizationMetadata
from repoze.what.plugins.pylonshq import booleanize_predicates
from repoze.what.plugins.sql import configure_sql_adapters
from repoze.who.interfaces import IIdentifier, IMetadataProvider
from repoze.who.plugins.sa import SQLAlchemyAuthenticatorPlugin
from repoze.who.plugins.sa import SQLAlchemyUserMDPlugin
from sqlalchemy.exc import UnboundExecutionError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from webob import Request
from zope.interface import implements

from project.model import DBSession, User, Group, Permission

import facebook



class FacebookConnectPlugin(object):

    implements(IIdentifier, IMetadataProvider)

    def __init__(self, appid, secret, **kw):
        self.appid = appid
        self.secret = secret

    def identify(self, environ):
        request = Request(environ)

        params = facebook.get_user_from_cookie(request.cookies, self.appid, self.secret)
        if params is None:
            # user is not logged in to his/her facebook account or hasn't granted
            # access to this application
            return None

        fb = facebook.GraphAPI(params['access_token'])

        try:
            user = DBSession.query(User).filter(User.fbid==params['uid']).one()
        except (NoResultFound, MultipleResultsFound):
            try:
                profile = fb.get_object('me')
            except facebook.GraphAPIError:
                return None

            if 'id' not in profile:
                # we couldn't get any information from facebook. login failed.
                return None

            user = User(email=profile['email'], name=profile['name'], fbid=profile['id'])
            DBSession.add(user)
            transaction.commit()

        try:
            return {'repoze.who.userid': user.email, 'facebook': True}
        except UnboundExecutionError:
            return {'repoze.who.userid': profile['email'], 'facebook': True}

    def remember(self, environ, identify):
        # Facebook JavaScript SDK handles cookies creation and deletion
        pass

    def forget(self, environ, identity):
        # Facebook JavaScript SDK handles cookies creation and deletion
        pass

    def add_metadata(self, environ, identity):
        request = Request(environ)
        user = identity.get('user', None)

        params = facebook.get_user_from_cookie(request.cookies, self.appid, self.secret)

        if params is not None and user is not None:
            # facebook account is already linked to this user account
            if user.fbid == params['uid']:
                # give the application access to the OAuth token
                identity['facebook.token'] = params['access_token']

            # this user account is already linked to a different facebook account
            elif user.fbid is not None:
                # there is valid FacebookConnect session but the current user account is linked to a different Facebook account.
                pass # TODO: ask the user if he/she wants to switch accounts

            # this user account is not linked to a facebook account
            else:
                # there is valid FacebookConnect session but the current user account is not linked to it.
                pass # TODO: ask the user if he/she wants to link this account

            # TODO: what if the FacebookConnect session is linked to another user account?

            

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