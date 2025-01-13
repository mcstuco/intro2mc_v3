#!/bin/bash

# install git, java, sqlite
sudo apt install git-lfs openjdk-17-jre-headless sqlite3 -y

# install python django and dependencies
sudo apt install python3-pip libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 -y
sudo apt install libjpeg-dev zlib1g-dev -y # for pillow

# If you use ubuntu >22.04, then you should create venv
# Because: https://stackoverflow.com/questions/75602063/pip-install-r-requirements-txt-is-failing-this-environment-is-externally-mana
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install setuptools
pip3 install --upgrade pip # you may skip it if it generates warnings
pip3 install -r ./requirements.txt # or python3 -m pip install -r requirements.txt if you use venv

# install apache2 and configure wsgi
sudo apt install apache2 libapache2-mod-wsgi-py3 -y

# make sure your python version is correct in ./apache2.conf
# also your installation path is correct for all project (search and replace /intro2mc_v3)
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
sudo chgrp -R www-data /home/mcstuco/Documents/intro2mc_v3
sudo chmod -R g+w /home/mcstuco/Documents/intro2mc_v3

sudo chgrp www-data /home/mcstuco/Documents/
sudo chmod g+w /home/mcstuco/Documents/
sudo chgrp www-data /home/mcstuco/
sudo chmod g+w /home/mcstuco/
# you can't pass relative paths like ../intro2mc_v3/ as it doesn't work
# sudo -u www-data test -r /home/mcstuco/Documents/intro2mc_v3/db.sqlite3; echo "$?" # should return 0
# otherwise that means apache can't read the file

# I don't know what's the better way to create the database
python3 manage.py makemigrations intro2mc
python3 manage.py migrate
python3 manage.py createsuperuser # will prompt you to provide password
python3 manage.py collectstatic

# reload apache
sudo service apache2 restart

# configure website using superuser:
# https://www.mcstuco.net/admin
# AppConfig:
# - CurrSemester: f24
# - Syllabus: https://docs.google.com/document/d/15pjUb0WqTo_9UXciALYuUtajpPnz4tvRY8Z_3XCAGbI/edit?usp=sharing
# - ServerMapURL: http://server.mcstuco.net:8123
# - ServerAddress: server.mcstuco.net
# - Roster: hankec,hankec,hankec,hankec
# Assignments:
# - Term: f24
# - Name: hw1
# - Description: Build a house.
# Class sessions:
# - Date: just select one
# - Code: ABCD (must be 4 uppercase characters)
# - Term: f24
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

# make sure you set .env
# and then look at provision-mc.sh for the rest of the steps (maybe, or maybe not)