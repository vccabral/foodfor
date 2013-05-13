pinax-project-social
====================

a starter project for social components based on pinax-project-account

Example usage
=============

    $ virtualenv mysite
    $ source mysite/bin/activate
    (mysite)$ pip install Django==1.4.3
    (mysite)$ django-admin.py startproject --template=https://github.com/pinax/pinax-project-social/zipball/master mysite
    (mysite)$ cd mysite
    (mysite)$ pip install -r requirements.txt
    (mysite)$ python manage.py syncdb
    (mysite)$ python manage.py runserver

Hit http://127.0.0.1:8000 to view the site!

What's included
===============

 * user profiles which are hooked up to the sign up process
