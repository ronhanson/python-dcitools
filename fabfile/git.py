from fabric.api import local, run, cd, env, prefix
from fabric.colors import cyan, red, green
from fabric.decorators import task


@task
def push(remote='origin', branch='master'):
    """git push commit"""
    print(cyan("Pulling changes from repo ( %s / %s)..." % (remote, branch)))
    local("git push %s %s" % (remote, branch))


@task
def pull(remote='origin', branch='master'):
    """git pull commit"""
    print(cyan("Pulling changes from repo ( %s / %s)..." % (remote, branch)))
    local("git pull %s %s" % (remote, branch))


@task
def sync(remote='origin', branch='master'):
    """git pull and push commit""" 
    pull(branch, remote)
    push(branch, remote)
    print(cyan("Git Synced!"))
