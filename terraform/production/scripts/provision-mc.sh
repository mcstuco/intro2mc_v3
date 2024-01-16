# prevent interactive prompts
sudo sed -i "/#\$nrconf{restart} = 'i';/s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf

# install git, java, sqlite
sudo apt-get update && sudo apt-get upgrade -y

# install python3, pip, and virtualenv
sudo apt-get install git python3 python3-pip python3-virtualenv -y
echo 'alias python="python3 "' >> ~/.bashrc
pip install --no-cache-dir --upgrade pip

# install git-lfs, java, sqlite
sudo apt-get install git-lfs openjdk-17-jre-headless sqlite3 -y

# install python django and dependencies
sudo apt-get install libgirepository1.0-dev gcc libcairo2-dev pkg-config gir1.2-gtk-4.0 -y
# install apache2
sudo apt-get install apache2 libapache2-mod-wsgi-py3 -y

# at this point, you should be able to access apache server at port 80

# set StrictHostKeyChecking to no to avoid interactive prompt
touch ~/.ssh/config
echo "Host *" >> ~/.ssh/config
echo "  StrictHostKeyChecking no" >> ~/.ssh/config

# get the code
cd /data
sudo chown -R $USER:$USER /data
git -C intro2mc_v3 pull origin master || GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone git@github.com:mcstuco/intro2mc_v3.git intro2mc_v3
git -C mcstuco pull origin master || GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone git@hf.co:KokeCacao/mcstuco mcstuco

cd mcstuco
git checkout master
git lfs pull --include "*.jar"
cd ..

cd intro2mc_v3
virtualenv env
source env/bin/activate
env/bin/pip install django
env/bin/pip install -r ./requirements.txt

# configure wsgi
cat ./apache2.conf | sudo tee /etc/apache2/apache2.conf > /dev/null
sudo chgrp -R www-data ../intro2mc_v3/
sudo chmod -R g+w ../intro2mc_v3/

# Now there are some manual steps:
# (1) You should import secrets: DJANGO_SECRET, GOOGLE_OAUTH2_KEY, GOOGLE_OAUTH2_SECRET
# (2) execute `env/bin/python manage.py runserver 0.0.0.0:8080` and kill it to create database
# (3) execute `env/bin/python manage.py makemigrations intro2mc`
# (4) execute `env/bin/python manage.py migrate`
# (5) execute `env/bin/python manage.py createsuperuser` and follow the prompt
# (6) execute `env/bin/python manage.py collectstatic`
# (7) execute `env/bin/python manage.py` again
# (8) execute `sudo service apache2 restart`
# (9) execute `sudo chmod -R u+w /data/intro2mc_v3/db.sqlite3 && sudo chown -R www-data:www-data /data/intro2mc_v3/db.sqlite3` to allow apache to write to db.sqlite3
# (9) configure website using superuser: https://www.mcstuco.net/admin-panel/semester adding "staff" status to instructors' accounts allows toggling admin
# if anything wrong happened, check /var/log/apache2/error.log