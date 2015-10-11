import os

from fabric.api import local, env, run, cd, put, sudo, prefix
from fabric.contrib import django
from seattlestats.settings.secrets import *

django.settings_module('seattlestats.settings.local')
from django.conf import settings

env.local_base_dir = settings.BASE_DIR #CANDIDATE FOR REMOVAL
env.local_settings = "--settings=seattlestats.settings.local"
env.local_postgres_database = settings.DATABASES['default']['NAME']
env.local_postgres_user = settings.DATABASES['default']['USER']
env.local_postgres_password = LOCAL_DATABASE_PASSWORD
env.local_secrets_path = env.local_base_dir + '/settings/secrets.py'

env.hosts = ['ec2-52-88-130-134.us-west-2.compute.amazonaws.com']
env.user = 'ubuntu'
env.sudo_user = env.user
env.prod_postgres_database = settings.DATABASES['default']['NAME']
env.prod_postgres_user = settings.DATABASES['default']['USER']
env.prod_postgres_password = PROD_DATABASE_PASSWORD

env.github_url = 'https://github.com/lindsayrgwatt/citystats'
env.http_dir = '/home/ubuntu'
env.project_name = 'citystats'
env.project_dir = os.path.join(env.http_dir, env.project_name)
env.project_code_dir = os.path.join(env.project_dir, 'seattlestats')
env.virtualenv_dir = os.path.join(env.project_dir, 'venv')
env.deploy_dir = os.path.join(env.project_code_dir, 'deploy')
env.remote_secrets_path = env.http_dir + '/' + env.project_name + '/seattlestats/seattlestats/settings/'
env.prod_settings = "--settings=seattlestats.settings.prod"

### Local

def print_local_settings(): #CANDIDATE FOR REMOVAL
    local("echo %(local_base_dir)s" % env)
    local("echo %(local_postgres_user)s" % env)
    local("echo %(local_postgres_password)s" % env)
    local("echo %(local_secrets_path)s" % env)
    local("echo %(remote_secrets_path)s" % env)
    local("echo %(project_code_dir)s" % env)

def set_up_local_database():
    local("psql -c \"CREATE DATABASE %(local_postgres_database)s;\"" % env)
    local("psql -c \"CREATE USER %(local_postgres_user)s WITH PASSWORD '%(local_postgres_password)s';\"" % env)
    local("psql <<EOF\n\c %(local_postgres_database)s\nCREATE EXTENSION postgis;\nEOF" % env)
    local("psql <<EOF\n\c %(local_postgres_database)s\nCREATE EXTENSION postgis_topology;\nEOF" % env)
    local("psql -c \"GRANT ALL PRIVILEGES ON DATABASE %(local_postgres_database)s TO %(local_postgres_user)s;\"" % env)

def create_local_superuser():
    local("python manage.py createsuperuser %(local_settings)s" % env)

def update_requirements():
    local("pip freeze > requirements.txt")

def runserver():
    local("python manage.py runserver %(local_settings)s" % env)

### Remote

def update_server():
    run("sudo apt-get -y -q update")
    run("sudo apt-get -y -q upgrade")
    # All the options in the following command are to avoid getting stuck on a grub update screen
    # http://askubuntu.com/questions/146921/how-do-i-apt-get-y-dist-upgrade-without-a-grub-config-prompt
    # If you still get it, choose the package maintainer version:
    # http://serverfault.com/questions/662624/how-to-avoid-grub-errors-after-runing-apt-get-upgrade-ubunut
    run('sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')

def install_required_software():
    run("sudo apt-get -y -q install python-dev") # Needed to avoid GCC compilation error for pycrypto
    run("sudo apt-get -y -q install nginx")
    run("sudo apt-get -y -q install git")
    run("sudo apt-get -y -q install binutils libproj-dev gdal-bin") # Geospatial libraries
    run("sudo apt-get -y -q install postgresql postgresql-contrib python-psycopg2")
    run("sudo apt-get -y -q install postgis postgresql-9.3-postgis-2.1")
    run("sudo apt-get -y -q install build-essential libxml2-dev libgdal-dev libproj-dev libjson0-dev xsltproc docbook-xsl docbook-mathml") # PostGIS
    run("sudo apt-get -y -q install redis-server") # Will restart on reboot

def install_base_python_packages():
    run("sudo apt-get -y -q install python-pip")
    run("sudo pip install --upgrade pip")
    run("sudo pip install virtualenv")

def install_project_python_packages():
    with prefix('source %(virtualenv_dir)s/bin/activate' % env):
        with cd(env.project_code_dir):
            run("pip install -r requirements.txt")

def start_nginx():
    sudo("service nginx start")

def manually_configure_postgres():
    print "Now you need to do two things:"
    print "1. Give the postgres user in your database a password"
    print "2. Update the authentication method of postgres so that you can actually connect"
    print "Some details here: http://suite.opengeo.org/4.1/dataadmin/pgGettingStarted/firstconnect.html"
    print "\n"
    print "Part 1."
    print "1. ssh into your server: ssh %(user)s@%(hosts)s" % env
    print "2. open psql as the postgres user. No password is required as none exists yet: sudo -u postgres psql postgres"
    print "3. change the password: \password postgres"
    print "4. quit: \q"
    print "5. end session: exit"
    print "\n"
    print "Part 2."
    run("sudo find / -name \"pg_hba.conf\" -print")
    print "Now you need to do the following to change peer authentication to md5"
    print "1. SSH into your server as above"
    print "2. Change the file listed in print statement above e.g., sudo vi /etc/postgresql/9.3/main/pg_hba.conf"
    print "3. Change the lines:"
    print "local   all             postgres                                peer"
    print "local   all             all                                     peer"
    print "to:"
    print "local   all             postgres                                md5"
    print "local   all             all                                     md5"
    print "4. Save, end the SSH session and from your local machine run: fab restart_postgres"

def restart_postgres():
    run("sudo service postgresql restart")

def set_up_database():
    run("sudo psql -U postgres -c \"CREATE DATABASE %(prod_postgres_database)s;\"" % env)
    run("sudo psql -U postgres -c \"CREATE USER %(prod_postgres_user)s WITH PASSWORD '%(prod_postgres_password)s';\"" % env)
    run("sudo psql -U postgres <<EOF\n\c %(prod_postgres_database)s\nCREATE EXTENSION postgis;\nEOF" % env)
    run("sudo psql -U postgres <<EOF\n\c %(prod_postgres_database)s\nCREATE EXTENSION postgis_topology;\nEOF" % env)
    run("sudo psql -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE %(prod_postgres_database)s TO %(prod_postgres_user)s;\"" % env)

def upload_secrets():
    put(env.local_secrets_path, env.http_dir)
    run('sudo cp %(http_dir)s/secrets.py %(remote_secrets_path)s' % env)

def run_prod_migrations():
    with prefix('source %(virtualenv_dir)s/bin/activate' % env):
        with cd(env.project_code_dir):
            run("python manage.py migrate %(prod_settings)s" % env)

def install_gunicorn():
    with prefix('source %(virtualenv_dir)s/bin/activate' % env):
        run("pip install gunicorn")

def install_supervisor():
    with prefix('source %(virtualenv_dir)s/bin/activate' % env):
        run("pip install supervisor --pre")
        run("sudo cp -f %(deploy_dir)s/supervisorstart.conf /etc/init/" % env)

def reboot_remote_host():
    run("sudo reboot")

def configure_nginx():
    #run("sudo rm /etc/nginx/sites-enabled/default")
    #run("sudo rm /etc/nginx/sites-available/default")

    run("sudo cp -f %(deploy_dir)s/nginx.conf /etc/nginx/" % env)
    sudo("service nginx restart")

def first_deploy_prep_a():
    update_server()
    install_required_software()
    install_base_python_packages()
    start_nginx()
    manually_configure_postgres()

def first_deploy_prep_b():
    restart_postgres()

def clone_project():
    run("sudo git clone %(github_url)s" % env) # First install of code
    run("sudo chmod -R 777 %(project_dir)s" % env) # Set permissions

def remote_git_pull():
    with cd(env.project_code_dir):
        run("git stash")
        run("git pull")

def create_virtualenv():
    # Set up virtualenv and change write permissions
    run("sudo virtualenv %(virtualenv_dir)s" % env)
    run("sudo chmod -R 777 %(virtualenv_dir)s" % env)


def first_deploy():
    clone_project()

    upload_secrets()

    create_virtualenv()

    install_project_python_packages()

    set_up_database()

    run_prod_migrations()

    install_gunicorn()
    install_supervisor()
    
    reboot_remote_host() # You've installed superivsor to start on reboot. This is a way to check

    configure_nginx()

