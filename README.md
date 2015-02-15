Digital Cinema Server API Library
=================================

About
-----

This library attempts to provide a functional and simple python package to manipulate, through their API, different digital cinema servers, players, and theatre management system.

The only brand actually supported is Doremi (company now bought by Dolby).

Current supported machines are :
 - DCP2000
 - DCP-2K4
 - ShowVault
 - IMS1000

Coming next: 
 - Doremi TMS
 - AAM TMS
 - Unique TMS
 - GDC servers
 - Old Dolby servers
 - Sony ?
 - Qube (someday maybe, haha, I can't wait to code with their API again, it is a bloody joke)

Project url : https://github.com/ronhanson/python-dcitools


Usage
-----

***Lib Usage***

Library is going to be documented in the docs folder.
But it is not yet for now... so just look at the code as it is commented for that.

***Script Usage***

Scripts have been created in order to use DCP2000 apis directly from command lines.
This scripts is named doremi.py and its usage can be found by typing :

    bin/doremiapi --help

That should be fairly simple.

For example, to list the CPL on a server :

    bin/doremiapi execute 172.17.10.109 GetCPLList

To get information about a CPL :

    bin/doremiapi x 172.17.10.109 GetCPLInfo 851cc838-022e-43b7-9fee-18656bdfc995


Compatibility
-------------

This libraries are used most on Linux and OSX systems, but plenty of functions may work on windows.

This libraries are compatibles with Python 2.X and Python 3.X.

Mainly tested on 2.7 and 3.4.


Author & Licence
----------------

Copyright (c) 2007-2015 Ronan Delacroix

This program is released under MIT Licence. Feel free to use it or part of it anywhere you want.
 
