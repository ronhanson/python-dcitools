from fabric.decorators import task
from fabric.context_managers import settings
from fabric.colors import cyan, red
from fabric.api import local
from fabric.utils import abort


@task
def clean():
    """Clean pyc files from project folder"""
    print(cyan('Cleaning .pyc files...'))
    local('find . -name "*.pyc" -exec rm -rf {} \\;')

