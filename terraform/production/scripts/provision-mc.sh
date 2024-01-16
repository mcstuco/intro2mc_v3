
# install git
sudo apt install git-lfs -y

# install java
sudo apt install openjdk-17-jre-headless -y

# install sqlite
sudo apt install sqlite3 -y

# set StrictHostKeyChecking to no to avoid interactive prompt
mkdir ~/.ssh
touch ~/.ssh/config
echo "Host *" >> ~/.ssh/config
echo "  StrictHostKeyChecking no" >> ~/.ssh/config

# get the code
cd /data

git -C intro2mc_v3 pull origin master || GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone git@github.com:mcstuco/intro2mc_v3.git intro2mc_v3

git -C mcstuco pull origin master || GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone git@github.com:KokeCacao/mcstuco.git mcstuco

cd mcstuco
git lfs pull --include "*.jar"
cd ..
