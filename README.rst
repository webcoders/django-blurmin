Django-Blurmin is a powerful and flexible admin panel
platform. Back end part built using the `Django`_ CBV (Class Based Views),
And the front end built using excellent `Akveo Blur Admin`_
angular admin panel front end framework. At the moment the software is in alpha version.
python and bower packaging and also documentation will coming soon. Now you can just clone it and run from the source directory.
There is example project and app under the myapp and myproject folders, you can play with.

Requirements
------------

django >= 1.10

How to run
----------

This section assumes your are running some debian like linux OS, your current directory is a project root

- Install requirements if you have no installed them:

.. code:: sh

    $ sudo pip install django

- Create your local_settings.py and put your database connection settings there. Then build django database:

.. code:: sh

    $ ./manage.py makemigrations notifications dashboard myapp
    $ ./manage.py migrate


We recommend to use nginx
-------------------------

- Add blurmin host to your nginx

.. code:: sh

    $ source deploy/nginx-conf.sh
    $ sudo ln -s `pwd`/deploy/nginx-blurmin.conf /etc/nginx/sites-enabled/nginx-blurmin.conf
    $ echo '127.0.0.1 blurmin' | sudo tee --append /etc/hosts
    $ sudo service nginx reload

- Now your site in under http://blurmin/dashboard

.. _`Django`: http://djangoproject.com/
.. _`Akveo Blur Admin`: https://akveo.github.io/blur-admin/

