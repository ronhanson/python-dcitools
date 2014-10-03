import os
from fabric.decorators import task
from fabric.api import local, run, cd, env, prefix, hide
from fabric.colors import cyan, red, green, yellow
import app
import git
import virtualenv


@task
def init():
    """Execute init tasks for all components (virtualenv, pip)."""
    print(yellow("# Setting up development environment...\n", True))
    virtualenv.init()
    virtualenv.update()
    print(green("\n# DONE.", True))
    print(green("Type ") + green("activate", True) + green(" to enable your dev virtual environment."))


@task
def update():
    """Update virtual env with requirements packages."""
    virtualenv.update()




@task
def dev():
    """Setting up Development mode."""
    print(yellow("# Setting up development environment...\n", True))
    virtualenv.init()
    virtualenv.update()
    print(green("\n# DONE.", True))
    print(green("Type ") + green("activate", True) + green(" to enable your dev virtual environment."))


@task
def clean():
    """Clean .pyc files"""
    app.clean()

