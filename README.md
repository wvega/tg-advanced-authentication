Example TurboGears 2 project for post ["Advanced Authentication in TurboGears 2"](http://wvega.com/266/advanced-authentication-in-turbogears-2-part-1).

Installation and Setup
======================

Install ``tg-advanced-authentication`` using the setup.py script::
------------------------------------------------------------------

    $ cd tg-advanced-authentication
    $ python setup.py install

Create the project database for any model classes defined::
-----------------------------------------------------------

    $ paster setup-app development.ini

Start the paste http server::
-----------------------------

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ paster serve --reload development.ini

Then you are ready to go.
