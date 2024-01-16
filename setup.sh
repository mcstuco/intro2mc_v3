#!/bin/bash

# install python django and dependencies
sudo apt install python3-pip -y
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 -y
sudo pip3 install -r /data/intro2mc_v3/requirements.txt

# install apache2 and configure wsgi
sudo apt install apache2 libapache2-mod-wsgi-py3
sudo cat /data/intro2mc_v3/apache2_conf_addon.txt >> /etc/apache2/apache2.conf
# comment the next part inside apache2.conf out
##<Directory />
# Options FollowSymLinks
# AllowOverride None
# Require all denied
#</Directory>
sudo chgrp -R www-data /data
sudo chmod -R g+w /data

# setup django
python3 manage.py runserver # I don't know what's the better way to create the database
python3 manage.py makemigrations intro2mc
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py collectstatic

# reload apache
sudo service apache2 restart

# configure website using superuser:
# https://www.mcstuco.net/admin-panel/semester
# adding "staff" status to instructors' accounts allows toggling admin
