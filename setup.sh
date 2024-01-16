#!/bin/bash

# install git, java, sqlite
sudo apt install git-lfs openjdk-17-jre-headless sqlite3 -y

# install python django and dependencies
sudo apt install python3-pip libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 -y
pip install -r ./requirements.txt

# install apache2 and configure wsgi
sudo apt install apache2 libapache2-mod-wsgi-py3 -y
cat ./apache2.conf | sudo tee /etc/apache2/apache2.conf > /dev/null

sudo chgrp -R www-data ../intro2mc_v3/
sudo chmod -R g+w ../intro2mc_v3/

# WARNING: The script sqlformat is installed in '/data/.local/bin' which is not on PATH.
# WARNING: The script qr is installed in '/data/.local/bin' which is not on PATH.
# WARNING: The scripts f2py, f2py3 and f2py3.10 are installed in '/data/.local/bin' which is not on PATH.
# WARNING: The script normalizer is installed in '/data/.local/bin' which is not on PATH.
# WARNING: The script mcstatus is installed in '/data/.local/bin' which is not on PATH.
# WARNING: The script django-admin is installed in '/data/.local/bin' which is not on PATH.
# Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.

# setup django

python3 manage.py runserver # should kill
# I don't know what's the better way to create the database

python3 manage.py makemigrations intro2mc
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py collectstatic # will prompt

# reload apache
sudo service apache2 restart

# configure website using superuser:
# https://www.mcstuco.net/admin-panel/semester
# adding "staff" status to instructors' accounts allows toggling admin

echo "Configuring IP Table... \n"
sudo iptables -L && \
sudo iptables-save > ~/iptables-rules && \
sudo iptables -P INPUT ACCEPT && \
sudo iptables -P OUTPUT ACCEPT && \
sudo iptables -P FORWARD ACCEPT && \
sudo iptables -F && \
sudo iptables-save | sudo tee /etc/iptables.conf && \
echo "My service will automatically do sudo iptables-restore < /etc/iptables.conf to load saved iptables.conf on server start."