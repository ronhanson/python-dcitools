# Package Installation and Usage


### I. Python installation instructions for Linux 

1. First install Python (2.7 or 3.4), pip and python-setuptools. Depending on your system it is something like :

		sudo apt-get install python3.4 python3-setuptools python3-pip

2. You can install the python package "pip" with setuptools if you don't have a python-pip package :

		sudo easy_install pip
	
3. If you fancy it, you can add in your PYTHONPATH variable the current folder ".". Place that line in your ".profile" :

		export PYTHONPATH="$PYTHONPATH:."
		

### II. Package Installation

Install current packages and its dependencies :

    pip install my_project.tar.gz

You should now be able to launch the scripts installed with your package.


### III. Develop

Install Fabric globally :

    sudo pip install fabric

Create a virtual env, and setup the dev mode : 

    fab dev

### IV. Python Packaging / Egg Build

You can create a Python egg simply by doing :

    python setup.py sdist


### V. Debian Packaging / .Deb Build

If you want to create a .deb, first, check the debian.cfg file and add the dependencies you want.

Go to tools/build folder :

    cd tools/build

Build the package using vagrant (the .deb package will be generated with a jessie64 vagrant box):

    ./vagrant_build_deb.sh

Or if you are already on a Debian system:

    ./build_deb.sh


##### Bonus tip for PyCharm users

If you use PyCharm, you paste the following code:


    <?xml version="1.0" encoding="UTF-8"?>
    <toolSet name="Fabric">
      <tool name="Fab Dev" description="Fabric Initialize Development Mode" showInMainMenu="true" showInEditor="true" showInProject="true" showInSearchPopup="false" disabled="false" useConsole="true" showConsoleOnStdOut="true" showConsoleOnStdErr="true" synchronizeAfterRun="true">
        <exec>
          <option name="COMMAND" value="/usr/local/bin/fab" />
          <option name="PARAMETERS" value="dev" />
          <option name="WORKING_DIRECTORY" value="$ProjectFileDir$" />
        </exec>
      </tool>
    </toolSet>

Into your PyCharm config folder. That is to say :

 - For MacOSX : *~/Library/Preferences/PyCharm30/tools/Fabric.xml* 

 - For Linux : *~/.PyCharmXX/config/tools/Fabric.xml* 

That will add a Fabric external tools to pyCharm.
You will then be able to go to "Tools" / "Fabric" / "Fab Dev" to initialize your env, for any project you create with that template.
You can also add you fab lines.
