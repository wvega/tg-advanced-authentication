# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in tg-advanced-authentication.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
 
"""

from tg.configuration import AppConfig

import project
from project import model
from project.lib import app_globals, helpers 

base_config = AppConfig()
base_config.renderers = []

base_config.package = project

#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'mako'
base_config.renderers.append('mako')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = project.model
base_config.DBSession = project.model.DBSession

