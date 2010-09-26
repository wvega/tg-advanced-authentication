# -*- coding: utf-8 -*-
"""Setup the tg-advanced-authentication application"""

import logging
from tg import config
from project import model

import transaction


def bootstrap(command, conf, vars):
    """Place any commands to setup project here"""

    # <websetup.bootstrap.before.auth>
    
    from sqlalchemy.exc import IntegrityError

    try:
        u = model.User()
        u.name = u'Example manager'
        u.email = u'manager@somedomain.com'
        u.password = u'managepass'

        model.DBSession.add(u)

        g = model.Group()
        g.slug = u'managers'
        g.name = u'Managers Group'

        g.users.append(u)

        model.DBSession.add(g)

        p = model.Permission()
        p.name = u'manage'
        p.description = u'This permission give an administrative right to the bearer'
        p.groups.append(g)

        model.DBSession.add(p)

        editor = model.User()
        editor.name = u'Example editor'
        editor.email = u'editor@somedomain.com'
        editor.password = u'editpass'

        model.DBSession.add(editor)
        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'

    # <websetup.bootstrap.after.auth>
