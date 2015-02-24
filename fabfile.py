from fabric.api import *
from boto.ec2 import connect_to_region
import os

env.port = "56565"
env.user = "gamealerts"
env.shell = "/bin/zsh -l --interactive -c"
env.password = os.environ.get("SUDO_PASS")


# Private method to get public DNS name for instance with given tag key and value pair
def _get_public_dns(region, key, value="*"):
    public_dns = []
    connection = _create_connection(region)
    reservations = connection.get_all_instances(filters={key: value})
    for reservation in reservations:
        for instance in reservation.instances:
            print "Instance", instance.public_dns_name
            public_dns.append(str(instance.public_dns_name))
    return public_dns


# Private method for getting AWS connection
def _create_connection(region):
    print "Connecting to ", region

    conn = connect_to_region(
        region_name=region,
        aws_access_key_id=os.environ.get("DJANGO_AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("DJANGO_AWS_SECRET_ACCESS_KEY")
    )

    print "Connection with AWS established"
    return conn


def production():

    env.hosts = _get_public_dns(os.environ.get("DJANGO_AWS_REGION"), "tag:role", "ga-app")


def local():
    env.hosts = ["gamealerts@localhost"]


def install_requirements():
    with cd("/var/www/gamealerts/django"), prefix("workon gamealerts"):
        sudo("pip install -r requirements.txt")


def pull_changes():
    with cd("/var/www/gamealerts/django"):
        sudo("git fetch --all")
        sudo("git reset --hard origin/master")


def database_setup():
    with cd("/var/www/gamealerts/django"), prefix("workon gamealerts"):
        sudo("python gamealerts.io/manage.py syncdb")
        sudo("python gamealerts.io/manage.py migrate")


def collect_static():

    with cd("/var/www/gamealerts/django"), prefix("workon gamealerts"):
        sudo("python gamealerts.io/manage.py collectstatic --noinput")


def set_permissions():
    sudo("touch nginx.nginx /var/www/gamealerts/logs/django.log")
    sudo("touch nginx.nginx /var/www/gamealerts/logs/celery.log")

    sudo("chown nginx.nginx /var/www/gamealerts/logs/django.log")
    sudo("chmod g+w /var/www/gamealerts/logs/django.log")

    sudo("chown nginx.nginx /var/www/gamealerts/logs/celery.log")
    sudo("chmod g+w /var/www/gamealerts/logs/celery.log")


def restart_services():
    sudo("/etc/init.d/nginx reload")
    sudo("touch nginx.nginx /var/www/gamealerts/config/uwsgi.ini")
    sudo("/usr/bin/supervisorctl restart gamealerts-celery")


def check_security():
    
    with cd("django"):
        run("python gamealerts.io/manage.py checksecure")


def pull_env():
    
    with cd("/var/www/gamealerts/gamealerts-private"):
        sudo("git fetch --all")
        sudo("git reset --hard origin/master")


def add_uwsgi_env_variables():

    sudo("cat /var/www/gamealerts/gamealerts-private/env/prod | sed 's/export/env =/' >> /var/www/gamealerts/config/uwsgi.ini")


def deploy():
    pull_env()
    pull_changes()
    install_requirements()
    database_setup()
    collect_static()
    add_uwsgi_env_variables()
    set_permissions()
    restart_services()