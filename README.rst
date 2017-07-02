Django-Blurmin is a powerful and flexible admin panel
platform. Back end part built using the `Django`_ CBV (Class Based Views),
And the front end built using excellent `Akveo Blur Admin`_
angular admin panel front end framework. At the moment the software is in alpha version.
python and bower packaging and also documentation will coming soon. Now you can just clone it and run from the source directory.
There is example project and app under the myapp and myproject folders, you can play with.

Requirements
------------

django >= 1.10 , nginx

How to run
----------

This section assumes your are running some debian like linux OS

- Install requirements if you have no installed them:

.. code:: sh

    $ pip install django
    $ apt-get install nginx

- Create your local_settings.py and put your database connection settings there. Then build django database:

.. code:: sh

    $ ./manage.py makemigrations
    $ ./manage.py migrate

- Open deploy/nginx-blurmin.conf and replace paths to your project directory
- Add blurmin host to your nginx

.. code:: sh

    $ sudo ln -s deploy/nginx-blurmin.conf /etc/nginx/sites-enabled/nginx-blurmin.conf
    $ sudo echo "127.0.0.1 blurmin" > /etc/hosts

- Point your browser to http://blurmin/dashboard

.. _`Django`: http://djangoproject.com/
.. _`Akveo Blur Admin`: https://akveo.github.io/blur-admin/

