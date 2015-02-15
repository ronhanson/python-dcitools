import os
from fabric.decorators import task
from fabric.api import local, run, cd, env, prefix, hide
from fabric.colors import cyan, red, green, yellow
import app
import git
import virtualenv


@task
def init():
    """
    Execute init tasks for all components (virtualenv, pip).
    """
    print(yellow("# Setting up environment...\n", True))
    virtualenv.init()
    virtualenv.update_requirements()
    print(green("\n# DONE.", True))
    print(green("Type ") + green("activate", True) + green(" to enable your virtual environment."))


@task
def update_requirements():
    """
    Update virtual env with requirements packages.
    """
    virtualenv.update_requirements()


@task
def update_dev_requirements():
    """
    Update virtual env with requirements packages.
    """
    virtualenv.update_dev_requirements()


@task
def dev():
    """
    Setting up Full Development mode.
    """
    print(yellow("# Setting up full development environment...\n", True))
    virtualenv.init()
    virtualenv.update_dev_requirements()
    print(green("\n# DONE.", True))
    print(green("Type ") + green("activate", True) + green(" to enable your dev virtual environment."))


@task
def clean():
    """
    Clean .pyc files
    """
    app.clean()


@task
def sync():
    """
    Git Sync
    """
    git.sync()

