#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi DCP2000 CLI Only Utility - Main File
:author: Ronan Delacroix
"""
import sys
import os
import cmd
import shlex
import toolbox
from . import commands as doremi_commands
from . import server as server


class CLI(cmd.Cmd, object):
    ### Generic
    prompt = 'DoremiAPICLI> '
    intro = '\n<< Welcome to Doremi API CLI >>\n'
    doc_leader = '\n<<Doremi API CLI Help Section>>\n'

    def __init__(self, address, port, debug=False):
        """
        Constructor
        """
        #hack : for windows 7 usage, need to set show-all-if-ambiguous to on for readline
        import readline
        import rlcompleter
        readline.parse_and_bind("set show-all-if-ambiguous on")
        reload(sys)  ## So as to enable setdefaultencoding
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind ^I rl_complete")
            readline.parse_and_bind("bind '\t' rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        #
        self.address = address
        self.port = port
        self.debug = debug
        self.client = None
        super(CLI, self).__init__(completekey='tab')

    def preloop(self):
        """
        At launch...
        """

        print("Connection...")
        try:
            self.client = server.DoremiServer(self.address, port=self.port, debug=self.debug)
        except:
            print("Connection to %s:%s failed." % (self.address, self.port))
            self.do_exit('')
            exit(1)
        print("Connected to Doremi DCP2000 server on %s:%s" % (self.address, self.port))

        super(CLI, self).preloop()

    def postloop(self):
        """
        End...
        """
        print('\nGoodbye!\n')
        super(CLI, self).postloop()

    ### Commands specifics

    def do_help(self, arg):
        """
        Dirty code : this function is copied from cmd.py...
        But I added some magic to have the doc of the API.
        """
        if arg:
            # XXX check arg syntax

            if arg in doremi_commands.NAMES:
                self.stdout.write("\n%s Help : \n" % str(arg))
                self.stdout.write("\tSummary :\n\t\tTODO (%s)\n\n" % (str(doremi_commands.NAMES[arg])))
                from inspect import getargspec
                self.stdout.write("\tParameters :\n\t\t%s\n\n" % (str(', '.join(getargspec(doremi_commands.NAMES[arg].handler).args))))
                return
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = [n.strip() for n in self.get_names()]
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]] = 1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif name[3:] in doremi_commands.NAMES.keys():
                        cmds_doc.append(cmd)
                    elif hasattr(self, name):
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  help.keys(),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

    def get_names(self):
        """
        Return all the function names of the current class + the API function names.
        """
        names = super(CLI, self).get_names()
        names.extend([str("do_" + c) for c in doremi_commands.NAMES.keys()])
        return ["%s " % name for name in names]

    def call_api(self, command, args=[]):
        """
        Call an API command
        """
        try:
            return self.client.command(command, *args)
        except doremi_commands.ParameterException as e:
            print("Wrong parameters : %s" % e)
        except Exception as e:
            print("ERROR : %s" % e)

        return

    def default(self, line):
        """
        When a command/do_function does not exists in that class, try to see if it exists in the API and if yes, calls it.
        """
        cmd, args, line = self.parseline(line)
        if cmd in doremi_commands.NAMES:

            args = shlex.split(args)

            result = self.call_api(cmd, args)
            if result:
                print("\nResults : \n")
                result = toolbox.text.dict_to_plaintext(result, indent=1)
                print(result)

            return

        return super(CLI, self).default(line)

    def completedefault(self, text, line, begidx, endidx):
        """Method called to complete an input line when no command-specific
        complete_*() method is available.

        By default, it returns an empty list.
        """
        from inspect import getargspec
        command = shlex.split(line)[0].replace('\x00', '').strip()
        listparams = []

        if command in doremi_commands.NAMES.keys():
            argspec = getargspec(doremi_commands.NAMES[command].handler)
            listparams = listparams+argspec.args

        arg_list = shlex.split(line)[1:]

        listparams = listparams[len(arg_list):]

        if len(listparams) > 0:
            print("\n\tMissing : " +' '.join(['<'+k+'>' for k in listparams]),)
            print("\n\tMissing : " +' '.join(['<'+k+'>' for k in listparams]),)

        return ['']

    ### Shell access
    def do_shell(self, s):
        """
        Allows to call shell commands
        """
        os.system(s)

    def help_shell(self):
        """
        Help on shell commands.
        """
        print("Execute shell commands")

    ### Exiting CLI
    def do_exit(self, s):
        """
        Exit
        """
        print("Exiting Doremi API CLI.")
        return True

    def help_exit(self):
        print("Exiting Doremi API CLI.")
        print("You can also use the Ctrl-D shortcut.")

    do_quit = do_exit
    help_quit = help_exit

    do_EOF = do_exit
    help_EOF = help_exit

