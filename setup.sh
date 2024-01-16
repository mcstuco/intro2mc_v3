#!/bin/bash

# install python django and dependencies
sudo apt install python3-pip libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 -y
pip3 install -r ./requirements.txt

# install apache2 and configure wsgi
sudo apt install apache2 libapache2-mod-wsgi-py3
cat ./apache2_conf_addon.txt | sudo tee -a /etc/apache2/apache2.conf
# comment the next part inside apache2.conf out
##<Directory />
# Options FollowSymLinks
# AllowOverride None
# Require all denied
#</Directory>
sudo chgrp -R www-data ./
sudo chmod -R g+w ./

# WARNING: The script sqlformat is installed in '/home/mcstuco/.local/bin' which is not on PATH.
# WARNING: The script qr is installed in '/home/mcstuco/.local/bin' which is not on PATH.
# WARNING: The scripts f2py, f2py3 and f2py3.10 are installed in '/home/mcstuco/.local/bin' which is not on PATH.
# WARNING: The script normalizer is installed in '/home/mcstuco/.local/bin' which is not on PATH.
# WARNING: The script mcstatus is installed in '/home/mcstuco/.local/bin' which is not on PATH.
# WARNING: The script django-admin is installed in '/home/mcstuco/.local/bin' which is not on PATH.
# Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.

# setup django

python3 manage.py runserver
# I don't know what's the better way to create the database

python3 manage.py makemigrations intro2mc
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py collectstatic

# reload apache
sudo service apache2 restart

# configure website using superuser:
# https://www.mcstuco.net/admin-panel/semester
# adding "staff" status to instructors' accounts allows toggling admin
