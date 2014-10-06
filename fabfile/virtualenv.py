import os
from fabric.decorators import task
from fabric.context_managers import settings, hide
from fabric.colors import cyan, red, green, yellow
from fabric.utils import abort
from fabric.api import local, run, cd, env, prefix

@task
def init():
    """Execute init tasks for all components (virtualenv, pip)."""
    if not os.path.isdir('venv'):
        print(cyan('\nCreating the virtual env...'))

        local('pyvenv-3.4 venv')

        print(green('Virtual env created.'))

    print(green('Virtual Environment ready.'))


@task
def update():
    """Update virtual env with requirements packages."""
    with settings(warn_only=True):
        print(cyan('\nInstalling/Updating required packages...'))

        pip = local('venv/bin/pip install -U --allow-all-external --src libs -r requirements.txt', capture=True)
        if pip.failed:
            print(red(pip))
            abort("pip exited with return code %i" % pip.return_code)

        print(green('Packages requirements updated.'))
